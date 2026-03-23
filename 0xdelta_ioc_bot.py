"""
0xD3lta Research — IOC Feed Bot
================================
Monitora feeds de IOCs de fontes abertas e posta automaticamente
no canal #iocs-and-feeds do Discord.

Fontes:
  - Abuse.ch ThreatFox     → IOCs multi-família (IPs, URLs, hashes, domínios)
  - Abuse.ch URLhaus        → URLs maliciosas ativas
  - Abuse.ch MalwareBazaar  → Hashes de amostras recentes
  - OTX AlienVault          → Pulses com IOCs contextualizados
  - FeodoTracker            → C2 de botnets (Emotet, QBot, etc.)

Dependências:
    pip install requests python-dotenv

Variáveis de ambiente (.env):
    DISCORD_TOKEN       → Token do bot Discord
    IOC_CHANNEL_ID      → ID do canal #iocs-and-feeds
    OTX_API_KEY         → (opcional) API key do OTX AlienVault

Uso:
    python 0xdelta_ioc_bot.py
    python 0xdelta_ioc_bot.py --loop --interval 3600
"""

import requests
import hashlib
import json
import time
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────

TOKEN      = os.getenv("DISCORD_TOKEN", "")
CHANNEL_ID = os.getenv("IOC_CHANNEL_ID", "")
OTX_KEY    = os.getenv("OTX_API_KEY", "")
BASE       = "https://discord.com/api/v10"
SEEN_FILE  = Path("seen_iocs.json")

# Máximo de IOCs por fonte por ciclo (evitar flood no canal)
MAX_PER_SOURCE = 5

# ─────────────────────────────────────────────────────────────
#  TIPOS DE IOC E FORMATAÇÃO
# ─────────────────────────────────────────────────────────────

# Mapeamento de tipo para emoji
IOC_EMOJI = {
    "ip":      "🌐",
    "url":     "🔗",
    "domain":  "🏴",
    "hash":    "🧬",
    "sha256":  "🧬",
    "md5":     "🧬",
    "sha1":    "🧬",
    "email":   "📧",
    "btc":     "💰",
    "unknown": "📌",
}

# Cores dos embeds por severidade/tipo de fonte
COLORS = {
    "threatfox":   0xE53935,   # vermelho — IOCs ativos
    "urlhaus":     0xFF6D00,   # laranja — URLs maliciosas
    "bazaar":      0x8E24AA,   # roxo — malware samples
    "otx":         0x1E88E5,   # azul — intel contextualizada
    "feodo":       0xD81B60,   # rosa — C2 botnets
}

# ─────────────────────────────────────────────────────────────
#  CACHE
# ─────────────────────────────────────────────────────────────

def load_seen() -> set:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen: set) -> None:
    entries = list(seen)[-5000:]
    SEEN_FILE.write_text(json.dumps(entries, indent=2))


def make_id(*parts) -> str:
    raw = "::".join(str(p) for p in parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


# ─────────────────────────────────────────────────────────────
#  DISCORD HTTP
# ─────────────────────────────────────────────────────────────

def dheaders() -> dict:
    return {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type":  "application/json",
        "User-Agent":    "DiscordBot (0xdelta-iocbot, 1.0)",
    }


def post_embed(payload: dict) -> bool:
    url = f"{BASE}/channels/{CHANNEL_ID}/messages"
    for _ in range(4):
        r = requests.post(url, headers=dheaders(), json=payload, timeout=15)
        if r.status_code == 429:
            wait = r.json().get("retry_after", 2)
            print(f"  ⏳ Rate limit — aguardando {wait:.1f}s...")
            time.sleep(wait)
            continue
        if r.status_code in (200, 201):
            return True
        print(f"  ❌ HTTP {r.status_code}: {r.text[:200]}")
        return False
    return False


# ─────────────────────────────────────────────────────────────
#  FONTE 1 — ThreatFox (Abuse.ch)
#  API: https://threatfox-api.abuse.ch/api/v1/
#  Retorna IOCs recentes por tipo: ip:port, url, domain, md5, sha256
# ─────────────────────────────────────────────────────────────

def fetch_threatfox(seen: set) -> list[dict]:
    print("\n  📡 ThreatFox (Abuse.ch)")
    results = []
    try:
        r = requests.post(
            "https://threatfox-api.abuse.ch/api/v1/",
            json={"query": "get_iocs", "days": 1},
            timeout=20,
        )
        data = r.json()
        if data.get("query_status") != "ok":
            print(f"    ⚠️  Status: {data.get('query_status')}")
            return results

        iocs = data.get("data", [])[:MAX_PER_SOURCE * 3]

        for ioc in iocs:
            ioc_id = make_id("threatfox", ioc.get("id", ""), ioc.get("ioc", ""))
            if ioc_id in seen:
                continue

            ioc_value   = ioc.get("ioc", "")
            ioc_type    = ioc.get("ioc_type", "unknown").lower()
            malware     = ioc.get("malware", "Unknown")
            malware_alias = ioc.get("malware_alias", "")
            confidence  = ioc.get("confidence_level", 0)
            tags        = ioc.get("tags") or []
            reporter    = ioc.get("reporter", "anonymous")
            first_seen  = ioc.get("first_seen", "")

            emoji = IOC_EMOJI.get(ioc_type, "📌")
            conf_bar = "█" * (confidence // 20) + "░" * (5 - confidence // 20)

            embed = {
                "title":       f"{emoji} ThreatFox IOC — {malware}",
                "color":       COLORS["threatfox"],
                "description": f"```\n{ioc_value}\n```",
                "fields": [
                    {"name": "Type",       "value": f"`{ioc_type}`",         "inline": True},
                    {"name": "Family",     "value": f"`{malware}`",           "inline": True},
                    {"name": "Confidence", "value": f"`{conf_bar}` {confidence}%", "inline": True},
                ],
                "footer": {"text": f"ThreatFox • Reporter: {reporter}"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if malware_alias:
                embed["fields"].append({"name": "Aliases", "value": f"`{malware_alias}`", "inline": True})
            if tags:
                embed["fields"].append({"name": "Tags", "value": " ".join(f"`{t}`" for t in tags[:5]), "inline": True})
            if first_seen:
                embed["fields"].append({"name": "First seen", "value": f"`{first_seen}`", "inline": True})

            results.append({"id": ioc_id, "embed": embed})
            if len(results) >= MAX_PER_SOURCE:
                break

    except Exception as e:
        print(f"    ⚠️  Erro: {e}")

    print(f"    → {len(results)} novos IOCs")
    return results


# ─────────────────────────────────────────────────────────────
#  FONTE 2 — URLhaus (Abuse.ch)
#  API: https://urlhaus-api.abuse.ch/v1/urls/recent/
#  Retorna URLs maliciosas ativas com contexto de entrega
# ─────────────────────────────────────────────────────────────

def fetch_urlhaus(seen: set) -> list[dict]:
    print("\n  📡 URLhaus (Abuse.ch)")
    results = []
    try:
        r = requests.get(
            "https://urlhaus-api.abuse.ch/v1/urls/recent/limit/25/",
            timeout=20,
        )
        data = r.json()
        urls = data.get("urls", [])

        for entry in urls:
            url_id = make_id("urlhaus", entry.get("id", ""), entry.get("url", ""))
            if url_id in seen:
                continue

            # Só posta URLs ainda online ou recentemente removidas
            if entry.get("url_status") not in ("online", "unknown"):
                continue

            url_value  = entry.get("url", "")
            threat     = entry.get("threat", "unknown")
            tags       = entry.get("tags") or []
            reporter   = entry.get("reporter", "anonymous")
            date_added = entry.get("date_added", "")
            host       = entry.get("host", "")

            # Trunca URL longa pra caber no embed
            url_display = url_value if len(url_value) <= 80 else url_value[:77] + "..."

            embed = {
                "title":       f"🔗 URLhaus — {threat}",
                "color":       COLORS["urlhaus"],
                "description": f"```\n{url_display}\n```",
                "fields": [
                    {"name": "Host",     "value": f"`{host}`",       "inline": True},
                    {"name": "Threat",   "value": f"`{threat}`",     "inline": True},
                    {"name": "Status",   "value": "`🔴 ONLINE`",     "inline": True},
                    {"name": "Reporter", "value": f"`{reporter}`",   "inline": True},
                    {"name": "Added",    "value": f"`{date_added}`", "inline": True},
                ],
                "footer": {"text": "URLhaus • Abuse.ch"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if tags:
                embed["fields"].append({
                    "name": "Tags",
                    "value": " ".join(f"`{t}`" for t in tags[:6]),
                    "inline": False,
                })

            results.append({"id": url_id, "embed": embed})
            if len(results) >= MAX_PER_SOURCE:
                break

    except Exception as e:
        print(f"    ⚠️  Erro: {e}")

    print(f"    → {len(results)} novas URLs")
    return results


# ─────────────────────────────────────────────────────────────
#  FONTE 3 — MalwareBazaar (Abuse.ch)
#  API: https://mb-api.abuse.ch/api/v1/
#  Retorna hashes de amostras recentes com família e tags
# ─────────────────────────────────────────────────────────────

def fetch_bazaar(seen: set) -> list[dict]:
    print("\n  📡 MalwareBazaar (Abuse.ch)")
    results = []
    try:
        r = requests.post(
            "https://mb-api.abuse.ch/api/v1/",
            json={"query": "get_recent", "selector": "time"},
            timeout=20,
        )
        data = r.json()
        if data.get("query_status") != "ok":
            return results

        samples = data.get("data", [])[:MAX_PER_SOURCE * 3]

        for sample in samples:
            s_id = make_id("bazaar", sample.get("sha256_hash", ""))
            if s_id in seen:
                continue

            sha256   = sample.get("sha256_hash", "")
            md5      = sample.get("md5_hash", "")
            family   = sample.get("signature") or "Unknown"
            filetype = sample.get("file_type", "unknown")
            filesize = sample.get("file_size", 0)
            tags     = sample.get("tags") or []
            reporter = sample.get("reporter", "anonymous")
            origin   = sample.get("origin_country", "")
            delivery = sample.get("delivery_method", "")
            first_seen = sample.get("first_seen", "")

            # Tamanho legível
            if filesize > 1024 * 1024:
                size_str = f"{filesize / 1024 / 1024:.1f} MB"
            elif filesize > 1024:
                size_str = f"{filesize / 1024:.1f} KB"
            else:
                size_str = f"{filesize} B"

            embed = {
                "title":       f"🧬 MalwareBazaar — {family}",
                "color":       COLORS["bazaar"],
                "description": (
                    f"**SHA256**\n```\n{sha256}\n```\n"
                    f"**MD5** `{md5}`"
                ),
                "fields": [
                    {"name": "Family",   "value": f"`{family}`",   "inline": True},
                    {"name": "Type",     "value": f"`{filetype}`", "inline": True},
                    {"name": "Size",     "value": f"`{size_str}`", "inline": True},
                    {"name": "Reporter", "value": f"`{reporter}`", "inline": True},
                ],
                "footer": {"text": "MalwareBazaar • Abuse.ch"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if first_seen:
                embed["fields"].append({"name": "First seen", "value": f"`{first_seen}`", "inline": True})
            if origin:
                embed["fields"].append({"name": "Origin", "value": f"`{origin}`", "inline": True})
            if delivery:
                embed["fields"].append({"name": "Delivery", "value": f"`{delivery}`", "inline": True})
            if tags:
                embed["fields"].append({
                    "name": "Tags",
                    "value": " ".join(f"`{t}`" for t in tags[:6]),
                    "inline": False,
                })

            # Link direto pro sandbox
            embed["url"] = f"https://bazaar.abuse.ch/sample/{sha256}/"

            results.append({"id": s_id, "embed": embed})
            if len(results) >= MAX_PER_SOURCE:
                break

    except Exception as e:
        print(f"    ⚠️  Erro: {e}")

    print(f"    → {len(results)} novas amostras")
    return results


# ─────────────────────────────────────────────────────────────
#  FONTE 4 — FeodoTracker (Abuse.ch)
#  API: https://feodotracker.abuse.ch/downloads/ipblocklist.json
#  Retorna C2 ativos de botnets conhecidos (Emotet, QBot, Dridex...)
# ─────────────────────────────────────────────────────────────

def fetch_feodo(seen: set) -> list[dict]:
    print("\n  📡 FeodoTracker (C2 Botnets)")
    results = []
    try:
        r = requests.get(
            "https://feodotracker.abuse.ch/downloads/ipblocklist.json",
            timeout=20,
        )
        entries = r.json()

        # Ordena por data de primeiro avistamento desc
        entries = sorted(entries, key=lambda x: x.get("first_seen", ""), reverse=True)

        for entry in entries[:MAX_PER_SOURCE * 3]:
            e_id = make_id("feodo", entry.get("ip_address", ""), entry.get("port", ""))
            if e_id in seen:
                continue

            # Só posta C2s ainda online
            if entry.get("status") != "online":
                continue

            ip         = entry.get("ip_address", "")
            port       = entry.get("port", "")
            malware    = entry.get("malware", "Unknown")
            first_seen = entry.get("first_seen", "")
            last_seen  = entry.get("last_online", "")
            country    = entry.get("country", "")
            asn        = entry.get("as_number", "")
            as_name    = entry.get("as_name", "")

            embed = {
                "title":       f"🔴 C2 Online — {malware}",
                "color":       COLORS["feodo"],
                "description": f"**C2 Address**\n```\n{ip}:{port}\n```",
                "fields": [
                    {"name": "Malware",     "value": f"`{malware}`",   "inline": True},
                    {"name": "Status",      "value": "`🔴 ONLINE`",    "inline": True},
                    {"name": "Country",     "value": f"`{country}`",   "inline": True},
                    {"name": "ASN",         "value": f"`AS{asn}`",     "inline": True},
                    {"name": "Provider",    "value": f"`{as_name}`",   "inline": True},
                    {"name": "First seen",  "value": f"`{first_seen}`","inline": True},
                ],
                "footer": {"text": "FeodoTracker • Abuse.ch"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if last_seen:
                embed["fields"].append({"name": "Last seen", "value": f"`{last_seen}`", "inline": True})

            results.append({"id": e_id, "embed": embed})
            if len(results) >= MAX_PER_SOURCE:
                break

    except Exception as e:
        print(f"    ⚠️  Erro: {e}")

    print(f"    → {len(results)} novos C2s")
    return results


# ─────────────────────────────────────────────────────────────
#  FONTE 5 — OTX AlienVault (opcional, requer API key)
#  API: https://otx.alienvault.com/api/v1/pulses/subscribed
#  Retorna pulses dos últimos dias com IOCs contextualizados
# ─────────────────────────────────────────────────────────────

def fetch_otx(seen: set) -> list[dict]:
    if not OTX_KEY:
        print("\n  📡 OTX AlienVault — pulando (sem API key)")
        return []

    print("\n  📡 OTX AlienVault")
    results = []
    try:
        since = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        r = requests.get(
            "https://otx.alienvault.com/api/v1/pulses/subscribed",
            headers={"X-OTX-API-KEY": OTX_KEY},
            params={"modified_since": since, "limit": 10},
            timeout=20,
        )
        data = r.json()
        pulses = data.get("results", [])

        for pulse in pulses[:MAX_PER_SOURCE]:
            p_id = make_id("otx", pulse.get("id", ""))
            if p_id in seen:
                continue

            name        = pulse.get("name", "Unknown Pulse")[:100]
            description = (pulse.get("description") or "")[:200]
            tags        = pulse.get("tags") or []
            tlp         = pulse.get("tlp", "white").upper()
            ioc_count   = len(pulse.get("indicators", []))
            author      = pulse.get("author_name", "unknown")
            created     = pulse.get("created", "")
            pulse_url   = f"https://otx.alienvault.com/pulse/{pulse.get('id', '')}"

            # Amostra dos primeiros IOCs do pulse
            indicators = pulse.get("indicators", [])[:5]
            ioc_sample = "\n".join(
                f"{IOC_EMOJI.get(i.get('type','').lower(), '📌')} `{i.get('indicator','')[:60]}`"
                for i in indicators
            )

            embed = {
                "title":       f"🧠 OTX Pulse — {name}",
                "url":         pulse_url,
                "color":       COLORS["otx"],
                "description": description or "No description provided.",
                "fields": [
                    {"name": "IOC count", "value": f"`{ioc_count}`",  "inline": True},
                    {"name": "TLP",       "value": f"`TLP:{tlp}`",    "inline": True},
                    {"name": "Author",    "value": f"`{author}`",     "inline": True},
                ],
                "footer": {"text": f"OTX AlienVault • {created[:10]}"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if tags:
                embed["fields"].append({
                    "name": "Tags",
                    "value": " ".join(f"`{t}`" for t in tags[:8]),
                    "inline": False,
                })

            if ioc_sample:
                embed["fields"].append({
                    "name": f"Sample IOCs (showing {len(indicators)} of {ioc_count})",
                    "value": ioc_sample,
                    "inline": False,
                })

            results.append({"id": p_id, "embed": embed})

    except Exception as e:
        print(f"    ⚠️  Erro: {e}")

    print(f"    → {len(results)} novos pulses")
    return results


# ─────────────────────────────────────────────────────────────
#  SEPARADOR VISUAL ENTRE FONTES
# ─────────────────────────────────────────────────────────────

SEPARATORS = {
    "threatfox": "🔴 **ThreatFox IOCs** — Active indicators from Abuse.ch ThreatFox",
    "urlhaus":   "🔗 **URLhaus Feed** — Malicious URLs currently online",
    "bazaar":    "🧬 **MalwareBazaar** — Fresh malware samples",
    "feodo":     "🔴 **FeodoTracker** — Active botnet C2 servers",
    "otx":       "🧠 **OTX AlienVault** — Threat intelligence pulses",
}


def post_separator(source_key: str) -> None:
    label = SEPARATORS.get(source_key, source_key)
    payload = {
        "content": f"\n{'─' * 40}\n{label}\n{'─' * 40}",
    }
    url = f"{BASE}/channels/{CHANNEL_ID}/messages"
    requests.post(url, headers=dheaders(), json=payload, timeout=10)
    time.sleep(0.5)


# ─────────────────────────────────────────────────────────────
#  RUNNER PRINCIPAL
# ─────────────────────────────────────────────────────────────

def run_once(verbose: bool = True) -> int:
    if not TOKEN or not CHANNEL_ID:
        print("❌ Configure DISCORD_TOKEN e IOC_CHANNEL_ID no .env")
        sys.exit(1)

    seen = load_seen()
    total_new = 0

    if verbose:
        print(f"\n🔄 IOC Feed — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("─" * 60)

    sources = [
        ("threatfox", fetch_threatfox),
        ("urlhaus",   fetch_urlhaus),
        ("bazaar",    fetch_bazaar),
        ("feodo",     fetch_feodo),
        ("otx",       fetch_otx),
    ]

    for key, fetch_fn in sources:
        items = fetch_fn(seen)

        if items:
            post_separator(key)
            time.sleep(0.5)

            for item in items:
                payload = {"embeds": [item["embed"]]}
                success = post_embed(payload)
                if success:
                    seen.add(item["id"])
                    total_new += 1
                    time.sleep(1.2)  # pausa entre posts

        time.sleep(0.5)

    save_seen(seen)

    if verbose:
        print(f"\n✅ Ciclo concluído — {total_new} novos IOCs postados")

    return total_new


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="0xDelta IOC Feed Bot")
    parser.add_argument("--loop",     action="store_true",   help="Rodar em loop contínuo")
    parser.add_argument("--interval", type=int, default=3600, help="Intervalo em segundos (padrão: 3600 = 1h)")
    parser.add_argument("--quiet",    action="store_true",   help="Suprimir output verbose")
    args = parser.parse_args()

    if args.loop:
        print(f"🤖 IOC Bot iniciado — intervalo: {args.interval}s ({args.interval // 60} min)")
        while True:
            try:
                run_once(verbose=not args.quiet)
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\n👋 Bot encerrado.")
                break
            except Exception as e:
                print(f"⚠️  Erro inesperado: {e}")
                time.sleep(60)
    else:
        run_once(verbose=not args.quiet)


if __name__ == "__main__":
    main()

"""
0xD3lta Research — CVE Watcher + EPSS Bot
==========================================
Monitora CVEs novos e atualizados via NVD API e enriquece
cada entrada com o score EPSS (probabilidade de exploração
nos próximos 30 dias) da FIRST.org.

Lógica de priorização:
  CRITICAL  → CVSS >= 9.0  OU  EPSS >= 0.70  → posta com @here
  HIGH      → CVSS >= 7.0  OU  EPSS >= 0.40
  MEDIUM    → CVSS >= 4.0  OU  EPSS >= 0.10
  LOW       → resto

Fontes:
  - NVD API v2   https://services.nvd.nist.gov/rest/json/cves/2.0
  - EPSS API     https://api.first.org/data/v1/epss

Dependências:
    pip install requests python-dotenv

Variáveis de ambiente:
    DISCORD_TOKEN    → token do bot
    CVE_CHANNEL_ID   → ID do canal #detection-and-rules
    NVD_API_KEY      → (opcional) aumenta rate limit do NVD

Uso:
    python 0xdelta_cve_bot.py
    python 0xdelta_cve_bot.py --loop --interval 3600
    python 0xdelta_cve_bot.py --severity CRITICAL --hours 24
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
CHANNEL_ID = os.getenv("CVE_CHANNEL_ID", "")
NVD_KEY    = os.getenv("NVD_API_KEY", "")
BASE       = "https://discord.com/api/v10"
SEEN_FILE  = Path("seen_cves.json")

MAX_CVES_PER_RUN = 10   # máximo de CVEs postados por execução
LOOKBACK_HOURS   = 2    # janela de busca (últimas N horas)

# ─────────────────────────────────────────────────────────────
#  PRIORIDADE E CORES
# ─────────────────────────────────────────────────────────────

def get_priority(cvss: float, epss: float) -> str:
    if cvss >= 9.0 or epss >= 0.70:
        return "CRITICAL"
    if cvss >= 7.0 or epss >= 0.40:
        return "HIGH"
    if cvss >= 4.0 or epss >= 0.10:
        return "MEDIUM"
    return "LOW"


PRIORITY_CFG = {
    "CRITICAL": {"color": 0xE53935, "emoji": "🚨", "mention": "@here"},
    "HIGH":     {"color": 0xFB8C00, "emoji": "⚠️",  "mention": ""},
    "MEDIUM":   {"color": 0xFDD835, "emoji": "📌",  "mention": ""},
    "LOW":      {"color": 0x546E7A, "emoji": "ℹ️",  "mention": ""},
}

# Barra visual para EPSS (0.0 → 1.0)
def epss_bar(score: float) -> str:
    filled = round(score * 10)
    return "█" * filled + "░" * (10 - filled)

# Barra visual para CVSS (0.0 → 10.0)
def cvss_bar(score: float) -> str:
    filled = round(score / 2)
    return "█" * filled + "░" * (5 - filled)


# ─────────────────────────────────────────────────────────────
#  CACHE
# ─────────────────────────────────────────────────────────────

def load_seen() -> set:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen: set) -> None:
    entries = list(seen)[-3000:]
    SEEN_FILE.write_text(json.dumps(entries, indent=2))


def make_id(cve_id: str) -> str:
    return hashlib.sha256(cve_id.encode()).hexdigest()[:16]


# ─────────────────────────────────────────────────────────────
#  DISCORD HTTP
# ─────────────────────────────────────────────────────────────

def dheaders() -> dict:
    return {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type":  "application/json",
        "User-Agent":    "DiscordBot (0xdelta-cvebot, 1.0)",
    }


def post_message(payload: dict) -> bool:
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
#  NVD API v2 — busca CVEs recentes
# ─────────────────────────────────────────────────────────────

def fetch_nvd_cves(hours: int = LOOKBACK_HOURS) -> list[dict]:
    """
    Busca CVEs publicados ou modificados nas últimas N horas.
    Retorna lista de dicts com dados normalizados.
    """
    now    = datetime.now(timezone.utc)
    since  = now - timedelta(hours=hours)

    # NVD espera formato: 2024-01-01T00:00:00.000
    fmt    = "%Y-%m-%dT%H:%M:%S.000"
    params = {
        "pubStartDate": since.strftime(fmt),
        "pubEndDate":   now.strftime(fmt),
        "resultsPerPage": 50,
        "startIndex": 0,
    }

    headers = {"User-Agent": "0xDelta-CVEBot/1.0"}
    if NVD_KEY:
        headers["apiKey"] = NVD_KEY

    try:
        r = requests.get(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            params=params,
            headers=headers,
            timeout=30,
        )
        if r.status_code != 200:
            print(f"  ⚠️  NVD retornou {r.status_code}")
            return []

        data = r.json()
        raw  = data.get("vulnerabilities", [])
        print(f"  📥 NVD: {len(raw)} CVEs nos últimos {hours}h")
        return [parse_nvd_entry(v) for v in raw if v.get("cve")]

    except Exception as e:
        print(f"  ⚠️  Erro NVD: {e}")
        return []


def parse_nvd_entry(v: dict) -> dict:
    """Normaliza uma entrada bruta da NVD API."""
    cve   = v.get("cve", {})
    cve_id = cve.get("id", "CVE-UNKNOWN")

    # Descrição em inglês
    descs  = cve.get("descriptions", [])
    desc   = next((d["value"] for d in descs if d.get("lang") == "en"), "No description.")
    desc   = desc[:400] + "..." if len(desc) > 400 else desc

    # CVSS — tenta v3.1 → v3.0 → v2.0
    cvss_score  = 0.0
    cvss_vector = ""
    cvss_ver    = ""
    metrics     = cve.get("metrics", {})

    for ver_key, ver_label in [("cvssMetricV31", "3.1"), ("cvssMetricV30", "3.0"), ("cvssMetricV2", "2.0")]:
        entries = metrics.get(ver_key, [])
        if entries:
            data_m = entries[0].get("cvssData", {})
            cvss_score  = data_m.get("baseScore", 0.0)
            cvss_vector = data_m.get("vectorString", "")
            cvss_ver    = ver_label
            break

    # Severity label
    severity = "NONE"
    if cvss_score >= 9.0:   severity = "CRITICAL"
    elif cvss_score >= 7.0: severity = "HIGH"
    elif cvss_score >= 4.0: severity = "MEDIUM"
    elif cvss_score > 0:    severity = "LOW"

    # CPE — produtos afetados
    configs      = cve.get("configurations", [])
    affected     = []
    for cfg in configs:
        for node in cfg.get("nodes", []):
            for match in node.get("cpeMatch", []):
                cpe = match.get("criteria", "")
                parts = cpe.split(":")
                if len(parts) >= 5:
                    vendor  = parts[3]
                    product = parts[4]
                    version = parts[5] if len(parts) > 5 else "*"
                    label   = f"{vendor}/{product}"
                    if label not in affected:
                        affected.append(label)
                if len(affected) >= 6:
                    break

    # CWEs
    weaknesses = cve.get("weaknesses", [])
    cwes = []
    for w in weaknesses:
        for desc_w in w.get("description", []):
            val = desc_w.get("value", "")
            if val.startswith("CWE-") and val not in cwes:
                cwes.append(val)

    # Referências
    refs = cve.get("references", [])
    ref_urls = [r.get("url", "") for r in refs[:3] if r.get("url")]

    # Datas
    published = cve.get("published", "")[:10]
    modified  = cve.get("lastModified", "")[:10]

    return {
        "id":          cve_id,
        "description": desc,
        "cvss_score":  cvss_score,
        "cvss_vector": cvss_vector,
        "cvss_ver":    cvss_ver,
        "severity":    severity,
        "affected":    affected,
        "cwes":        cwes,
        "refs":        ref_urls,
        "published":   published,
        "modified":    modified,
        "epss_score":  0.0,        # preenchido depois
        "epss_pct":    0.0,
    }


# ─────────────────────────────────────────────────────────────
#  EPSS API — enriquece CVEs com probabilidade de exploração
# ─────────────────────────────────────────────────────────────

def enrich_epss(cves: list[dict]) -> list[dict]:
    """
    Consulta a API EPSS da FIRST.org em batch.
    Adiciona epss_score (0.0–1.0) e epss_pct (percentil) a cada CVE.
    """
    if not cves:
        return cves

    ids = [c["id"] for c in cves]
    # API aceita até 30 CVEs por request
    batch_size = 30

    epss_map: dict[str, tuple[float, float]] = {}

    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        try:
            r = requests.get(
                "https://api.first.org/data/v1/epss",
                params={"cve": ",".join(batch)},
                timeout=15,
            )
            data = r.json()
            for entry in data.get("data", []):
                cve_id = entry.get("cve", "")
                score  = float(entry.get("epss", 0.0))
                pct    = float(entry.get("percentile", 0.0))
                epss_map[cve_id] = (score, pct)
        except Exception as e:
            print(f"  ⚠️  Erro EPSS batch {i}: {e}")

        time.sleep(0.3)

    for cve in cves:
        score, pct = epss_map.get(cve["id"], (0.0, 0.0))
        cve["epss_score"] = score
        cve["epss_pct"]   = pct

    return cves


# ─────────────────────────────────────────────────────────────
#  BUILD DISCORD EMBED
# ─────────────────────────────────────────────────────────────

def build_embed(cve: dict) -> dict:
    priority = get_priority(cve["cvss_score"], cve["epss_score"])
    cfg      = PRIORITY_CFG[priority]

    cve_id   = cve["id"]
    nvd_url  = f"https://nvd.nist.gov/vuln/detail/{cve_id}"

    # Cabeçalho CVSS
    cvss_str = (
        f"`{cve['cvss_score']:.1f}` {cvss_bar(cve['cvss_score'])} "
        f"*(CVSSv{cve['cvss_ver']})*"
        if cve["cvss_score"] > 0
        else "`N/A`"
    )

    # Cabeçalho EPSS
    epss_pct_val = cve["epss_pct"] * 100
    epss_str = (
        f"`{cve['epss_score']:.4f}` {epss_bar(cve['epss_score'])} "
        f"*(top {100 - epss_pct_val:.1f}%)*"
        if cve["epss_score"] > 0
        else "`N/A`"
    )

    embed: dict = {
        "title":       f"{cfg['emoji']} {cve_id} — {cve['severity']}",
        "url":         nvd_url,
        "color":       cfg["color"],
        "description": cve["description"],
        "fields": [
            {
                "name":   "CVSS Score",
                "value":  cvss_str,
                "inline": False,
            },
            {
                "name":   "EPSS Score",
                "value":  epss_str,
                "inline": False,
            },
        ],
        "footer": {
            "text": f"NVD • Published: {cve['published']} • Modified: {cve['modified']}",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Vector string
    if cve["cvss_vector"]:
        embed["fields"].append({
            "name":   "Attack vector",
            "value":  f"`{cve['cvss_vector']}`",
            "inline": False,
        })

    # Produtos afetados
    if cve["affected"]:
        embed["fields"].append({
            "name":   "Affected products",
            "value":  " ".join(f"`{a}`" for a in cve["affected"][:6]),
            "inline": False,
        })

    # CWEs
    if cve["cwes"]:
        cwe_links = " ".join(
            f"[{c}](https://cwe.mitre.org/data/definitions/{c.replace('CWE-','')}.html)"
            for c in cve["cwes"][:4]
        )
        embed["fields"].append({
            "name":   "Weakness (CWE)",
            "value":  cwe_links,
            "inline": False,
        })

    # Referências
    if cve["refs"]:
        refs_str = "\n".join(f"• <{u}>" for u in cve["refs"][:3])
        embed["fields"].append({
            "name":   "References",
            "value":  refs_str,
            "inline": False,
        })

    return embed


def build_payload(cve: dict) -> dict:
    priority = get_priority(cve["cvss_score"], cve["epss_score"])
    cfg      = PRIORITY_CFG[priority]
    embed    = build_embed(cve)
    content  = cfg["mention"] if cfg["mention"] else ""
    return {"content": content, "embeds": [embed]}


# ─────────────────────────────────────────────────────────────
#  RUNNER PRINCIPAL
# ─────────────────────────────────────────────────────────────

def run_once(
    verbose:          bool  = True,
    min_severity:     str   = "LOW",
    min_epss:         float = 0.0,
    hours:            int   = LOOKBACK_HOURS,
) -> int:

    if not TOKEN or not CHANNEL_ID:
        print("❌  Configure DISCORD_TOKEN e CVE_CHANNEL_ID no .env")
        sys.exit(1)

    seen = load_seen()

    if verbose:
        print(f"\n🔄 CVE Watcher — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Janela: últimas {hours}h | Severidade mínima: {min_severity}")
        print("─" * 60)

    # 1. Busca CVEs novos no NVD
    cves = fetch_nvd_cves(hours=hours)

    # 2. Filtra já vistos
    cves = [c for c in cves if make_id(c["id"]) not in seen]

    if not cves:
        if verbose:
            print("  ✅ Nenhum CVE novo encontrado.")
        return 0

    # 3. Enriquece com EPSS
    if verbose:
        print(f"  🔬 Enriquecendo {len(cves)} CVEs com EPSS...")
    cves = enrich_epss(cves)

    # 4. Aplica filtros de severidade e EPSS mínimo
    severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
    min_order      = severity_order.get(min_severity, 0)

    cves = [
        c for c in cves
        if (
            severity_order.get(get_priority(c["cvss_score"], c["epss_score"]), 0) >= min_order
            or c["epss_score"] >= min_epss
        )
    ]

    # 5. Ordena: CRITICAL primeiro, depois por EPSS desc, depois por CVSS desc
    cves.sort(
        key=lambda c: (
            -severity_order.get(get_priority(c["cvss_score"], c["epss_score"]), 0),
            -c["epss_score"],
            -c["cvss_score"],
        )
    )

    # 6. Limita ao máximo por run
    cves = cves[:MAX_CVES_PER_RUN]

    if verbose:
        print(f"  📤 Postando {len(cves)} CVEs...")

    posted = 0
    for cve in cves:
        priority = get_priority(cve["cvss_score"], cve["epss_score"])
        if verbose:
            print(
                f"    {PRIORITY_CFG[priority]['emoji']} {cve['id']} "
                f"CVSS:{cve['cvss_score']:.1f} "
                f"EPSS:{cve['epss_score']:.4f} "
                f"[{priority}]"
            )

        payload = build_payload(cve)
        success = post_message(payload)
        if success:
            seen.add(make_id(cve["id"]))
            posted += 1
            time.sleep(1.5)

    save_seen(seen)

    if verbose:
        print(f"\n✅ Concluído — {posted} CVEs postados")

    return posted


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="0xDelta CVE Watcher + EPSS Bot")
    parser.add_argument("--loop",      action="store_true",    help="Rodar em loop contínuo")
    parser.add_argument("--interval",  type=int, default=3600, help="Intervalo em segundos (padrão: 3600)")
    parser.add_argument("--quiet",     action="store_true",    help="Suprimir output")
    parser.add_argument("--severity",  default="LOW",          help="Severidade mínima: LOW | MEDIUM | HIGH | CRITICAL")
    parser.add_argument("--min-epss",  type=float, default=0.0,help="EPSS mínimo para postar (0.0 – 1.0)")
    parser.add_argument("--hours",     type=int, default=LOOKBACK_HOURS, help="Janela de busca em horas")
    args = parser.parse_args()

    kwargs = {
        "verbose":      not args.quiet,
        "min_severity": args.severity.upper(),
        "min_epss":     args.min_epss,
        "hours":        args.hours,
    }

    if args.loop:
        print(f"🤖 CVE Bot iniciado — intervalo: {args.interval}s")
        while True:
            try:
                run_once(**kwargs)
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\n👋 Bot encerrado.")
                break
            except Exception as e:
                print(f"⚠️  Erro inesperado: {e}")
                time.sleep(60)
    else:
        run_once(**kwargs)


if __name__ == "__main__":
    main()

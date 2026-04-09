"""
0xD3lta Research — Ransomware Tracker Bot
==========================================
Monitora grupos de ransomware ativos e novas vítimas em tempo real.

Fontes:
  - ransomware.live API     → vítimas novas por grupo, em tempo real
  - ransomwatch GitHub      → dados agregados de leak sites
  - ID Ransomware (Emsisoft)→ (RSS) identificações recentes

Enriquecimento por vítima:
  - Classificação por setor (saúde, governo, financeiro, etc.)
  - Scoring de impacto por setor + tamanho estimado da org
  - Histórico de atividade do grupo no mesmo ciclo
  - Links para post no leak site quando disponível
  - Alerta @here para setores críticos (saúde, governo, infraestrutura)

Dependências:
    pip install requests python-dotenv

Variáveis de ambiente:
    DISCORD_TOKEN           → token do bot
    RANSOMWARE_CHANNEL_ID   → ID do canal #threat-intel

Uso:
    python 0xdelta_ransomware_bot.py
    python 0xdelta_ransomware_bot.py --loop --interval 3600
    python 0xdelta_ransomware_bot.py --hours 24 --min-impact MEDIUM
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
CHANNEL_ID = os.getenv("RANSOMWARE_CHANNEL_ID", "")
BASE       = "https://discord.com/api/v10"
SEEN_FILE  = Path("seen_ransomware.json")

MAX_PER_RUN   = 15    # máximo de vítimas postadas por ciclo
LOOKBACK_HOURS = 2    # janela de busca

# ─────────────────────────────────────────────────────────────
#  CLASSIFICAÇÃO DE GRUPOS
# ─────────────────────────────────────────────────────────────

# Grupos com histórico de alta sofisticação / impacto geopolítico
TIER1_GROUPS = {
    "lockbit", "lockbit3", "blackcat", "alphv", "clop", "cl0p",
    "blackbasta", "black-basta", "akira", "play", "royal",
    "bianlian", "bian-lian", "hive", "conti", "revil", "darkside",
    "ragnarlocker", "ragnar-locker", "cuba", "lorenz", "maze",
    "evilcorp", "evil-corp", "lazarus", "scattered-spider",
}

TIER2_GROUPS = {
    "rhysida", "hunters", "hunters-international", "medusa",
    "meow", "ransomhub", "ransomhouse", "monti", "nokoyawa",
    "8base", "darkvault", "donutleaks", "dunghill",
    "stormous", "snatch", "quilin", "everest",
}

def group_tier(name: str) -> int:
    key = name.lower().replace(" ", "-")
    if key in TIER1_GROUPS:  return 1
    if key in TIER2_GROUPS:  return 2
    return 3


# ─────────────────────────────────────────────────────────────
#  CLASSIFICAÇÃO DE SETORES
# ─────────────────────────────────────────────────────────────

# Setor → (label, emoji, impacto base, crítico?)
SECTOR_MAP = {
    # Críticos (disparam @here)
    "healthcare":        ("Healthcare",        "🏥", 90, True),
    "hospital":          ("Healthcare",        "🏥", 90, True),
    "health":            ("Healthcare",        "🏥", 90, True),
    "government":        ("Government",        "🏛️", 85, True),
    "military":          ("Government/Military","⚔️", 95, True),
    "defense":           ("Defense",           "⚔️", 95, True),
    "critical infrastructure":("Critical Infra","⚡", 95, True),
    "energy":            ("Energy/Utilities",  "⚡", 90, True),
    "utilities":         ("Energy/Utilities",  "⚡", 90, True),
    "water":             ("Water/Utilities",   "💧", 90, True),
    "nuclear":           ("Nuclear",           "☢️", 99, True),
    "aviation":          ("Aviation",          "✈️", 90, True),
    "transportation":    ("Transportation",    "🚢", 80, True),

    # Alto impacto
    "finance":           ("Finance",           "💰", 75, False),
    "banking":           ("Banking",           "🏦", 75, False),
    "insurance":         ("Insurance",         "💼", 70, False),
    "legal":             ("Legal",             "⚖️", 65, False),
    "pharmaceutical":    ("Pharma",            "💊", 70, False),
    "education":         ("Education",         "🎓", 60, False),
    "university":        ("Education",         "🎓", 60, False),

    # Médio impacto
    "manufacturing":     ("Manufacturing",     "🏭", 55, False),
    "technology":        ("Technology",        "💻", 60, False),
    "it":                ("Technology",        "💻", 60, False),
    "telecom":           ("Telecom",           "📡", 65, False),
    "retail":            ("Retail",            "🛒", 45, False),
    "construction":      ("Construction",      "🏗️", 40, False),
    "hospitality":       ("Hospitality",       "🏨", 40, False),
    "media":             ("Media",             "📺", 50, False),
    "ngo":               ("NGO/Nonprofit",     "🤝", 50, False),
}

DEFAULT_SECTOR = ("Unknown", "🏢", 40, False)


def classify_sector(sector: str, name: str = "") -> tuple[str, str, int, bool]:
    """Retorna (label, emoji, impacto_base, critico) para um setor."""
    combined = (sector + " " + name).lower()
    for key, val in SECTOR_MAP.items():
        if key in combined:
            return val
    return DEFAULT_SECTOR


# ─────────────────────────────────────────────────────────────
#  SCORE DE IMPACTO
# ─────────────────────────────────────────────────────────────

def impact_score(sector_impact: int, group_tier: int, country: str) -> int:
    """
    Score de impacto 0–100.
    Base: setor (0–60) + tier do grupo (0–30) + país (0–10)
    """
    score = int(sector_impact * 0.6)

    if group_tier == 1:   score += 30
    elif group_tier == 2: score += 20
    else:                 score += 10

    # Países de infraestrutura crítica global
    high_value_countries = {
        "us", "usa", "united states", "uk", "united kingdom",
        "de", "germany", "fr", "france", "ca", "canada",
        "au", "australia", "jp", "japan", "kr", "south korea",
    }
    if country.lower() in high_value_countries:
        score += 10

    return min(score, 100)


def impact_label(score: int) -> str:
    if score >= 80: return "CRITICAL"
    if score >= 60: return "HIGH"
    if score >= 40: return "MEDIUM"
    return "LOW"


def impact_bar(score: int) -> str:
    filled = round(score / 10)
    return "█" * filled + "░" * (10 - filled)


IMPACT_COLORS = {
    "CRITICAL": 0xB71C1C,
    "HIGH":     0xE53935,
    "MEDIUM":   0xFB8C00,
    "LOW":      0x546E7A,
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
        "User-Agent":    "DiscordBot (0xdelta-ransombot, 1.0)",
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
#  FONTE 1 — ransomware.live
#  API pública, sem key — vítimas recentes por grupo
# ─────────────────────────────────────────────────────────────

def fetch_ransomware_live(seen: set, hours: int) -> list[dict]:
    print("\n  📡 ransomware.live")
    results = []

    try:
        # Endpoint de vítimas recentes
        r = requests.get(
            "https://api.ransomware.live/recentvictims",
            headers={"User-Agent": "0xDelta-RansomBot/1.0"},
            timeout=20,
        )
        if r.status_code != 200:
            print(f"    ⚠️  HTTP {r.status_code}")
            return results

        victims = r.json()
        if not isinstance(victims, list):
            return results

        # Filtra pelo lookback
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        for v in victims:
            # Parse da data — ransomware.live usa formato variado
            date_str = v.get("published", v.get("discovered", ""))
            try:
                if "T" in date_str:
                    pub_date = datetime.fromisoformat(
                        date_str.replace("Z", "+00:00")
                    )
                else:
                    pub_date = datetime.strptime(
                        date_str[:10], "%Y-%m-%d"
                    ).replace(tzinfo=timezone.utc)
            except Exception:
                continue

            if pub_date < cutoff:
                continue

            group   = v.get("group_name", v.get("gang", "unknown"))
            victim  = v.get("victim", v.get("company", "Unknown"))
            country = v.get("country", "")
            sector  = v.get("activity", v.get("sector", ""))
            url     = v.get("url", v.get("post_url", ""))
            desc    = v.get("description", "")[:300]
            website = v.get("website", "")

            vid = make_id("rlive", group, victim, date_str[:10])
            if vid in seen:
                continue

            results.append({
                "id":        vid,
                "source":    "ransomware.live",
                "group":     group,
                "victim":    victim,
                "country":   country,
                "sector":    sector,
                "url":       url,
                "website":   website,
                "desc":      desc,
                "published": date_str[:10],
            })

    except Exception as e:
        print(f"    ⚠️  Erro: {e}")

    print(f"    → {len(results)} novas vítimas")
    return results


# ─────────────────────────────────────────────────────────────
#  FONTE 2 — ransomwatch (GitHub)
#  JSON público com posts de leak sites agregados
# ─────────────────────────────────────────────────────────────

def fetch_ransomwatch(seen: set, hours: int) -> list[dict]:
    print("\n  📡 ransomwatch")
    results = []

    try:
        r = requests.get(
            "https://raw.githubusercontent.com/joshhighet/ransomwatch/main/posts.json",
            headers={"User-Agent": "0xDelta-RansomBot/1.0"},
            timeout=20,
        )
        if r.status_code != 200:
            print(f"    ⚠️  HTTP {r.status_code}")
            return results

        posts = r.json()
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        for post in posts:
            date_str = post.get("discovered", "")
            try:
                pub_date = datetime.fromisoformat(
                    date_str.replace("Z", "+00:00")
                )
            except Exception:
                continue

            if pub_date < cutoff:
                continue

            group   = post.get("group_name", "unknown")
            victim  = post.get("post_title", "Unknown")
            url     = post.get("url", "")

            vid = make_id("rwatch", group, victim, date_str[:10])
            if vid in seen:
                continue

            results.append({
                "id":        vid,
                "source":    "ransomwatch",
                "group":     group,
                "victim":    victim,
                "country":   "",
                "sector":    "",
                "url":       url,
                "website":   "",
                "desc":      "",
                "published": date_str[:10],
            })

    except Exception as e:
        print(f"    ⚠️  Erro: {e}")

    # Deduplica por vítima+grupo (pode aparecer nas duas fontes)
    unique = {make_id(r["group"], r["victim"]): r for r in results}
    results = list(unique.values())

    print(f"    → {len(results)} novos posts")
    return results


# ─────────────────────────────────────────────────────────────
#  SUMÁRIO DE ATIVIDADE DO GRUPO (via ransomware.live)
# ─────────────────────────────────────────────────────────────

_group_cache: dict[str, dict] = {}

def get_group_stats(group_name: str) -> dict:
    """Busca estatísticas do grupo — com cache em memória."""
    key = group_name.lower()
    if key in _group_cache:
        return _group_cache[key]

    try:
        r = requests.get(
            f"https://api.ransomware.live/group/{group_name}",
            headers={"User-Agent": "0xDelta-RansomBot/1.0"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            stats = {
                "total_victims": data.get("total_victims", 0),
                "active_since":  data.get("first_seen", "")[:7],
                "description":   (data.get("description") or "")[:200],
                "locations":     data.get("locations", [])[:3],
            }
            _group_cache[key] = stats
            return stats
    except Exception:
        pass

    stats = {"total_victims": 0, "active_since": "", "description": "", "locations": []}
    _group_cache[key] = stats
    return stats


# ─────────────────────────────────────────────────────────────
#  BUILD EMBED
# ─────────────────────────────────────────────────────────────

def build_embed(victim: dict) -> dict:
    group   = victim["group"]
    name    = victim["victim"]
    country = victim["country"]
    sector  = victim["sector"]
    desc    = victim["desc"]
    url     = victim["url"]
    website = victim["website"]
    pub     = victim["published"]
    source  = victim["source"]

    # Classificação
    sec_label, sec_emoji, sec_impact, is_critical = classify_sector(sector, name)
    tier    = group_tier(group)
    score   = impact_score(sec_impact, tier, country)
    i_label = impact_label(score)
    color   = IMPACT_COLORS[i_label]

    # Tier badge
    tier_str = {1: "⭐ Tier 1 — Major threat actor", 2: "🔸 Tier 2", 3: "🔹 Tier 3"}.get(tier, "")

    # Stats do grupo
    stats = get_group_stats(group)

    embed: dict = {
        "title": f"🔒 New victim — {group.upper()}",
        "color": color,
        "description": (
            f"**{sec_emoji} {name}**"
            + (f"\n{desc}" if desc else "")
        ),
        "fields": [
            {
                "name":   "Impact score",
                "value":  f"`{score}/100` {impact_bar(score)} **{i_label}**",
                "inline": False,
            },
            {
                "name":   "Sector",
                "value":  f"`{sec_label}`",
                "inline": True,
            },
            {
                "name":   "Country",
                "value":  f"`{country}`" if country else "`Unknown`",
                "inline": True,
            },
            {
                "name":   "Published",
                "value":  f"`{pub}`",
                "inline": True,
            },
            {
                "name":   "Group",
                "value":  f"`{group}` — {tier_str}",
                "inline": False,
            },
        ],
        "footer": {
            "text": f"0xD3lta Research • {source}",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Stats do grupo se disponíveis
    if stats["total_victims"]:
        embed["fields"].append({
            "name":   "Group activity",
            "value": (
                f"`{stats['total_victims']}` total victims"
                + (f" • Since `{stats['active_since']}`" if stats["active_since"] else "")
            ),
            "inline": False,
        })

    # Descrição do grupo
    if stats["description"]:
        embed["fields"].append({
            "name":   "Group profile",
            "value":  stats["description"][:200],
            "inline": False,
        })

    # Links
    links = []
    if url:
        links.append(f"[Leak site post]({url})")
    if website:
        links.append(f"[Victim website]({website})")
    links.append(f"[ransomware.live](https://www.ransomware.live/group/{group})")

    embed["fields"].append({
        "name":   "Links",
        "value":  " • ".join(links),
        "inline": False,
    })

    return embed


def build_payload(victim: dict) -> dict:
    sector  = victim["sector"]
    name    = victim["victim"]
    _, _, sec_impact, is_critical = classify_sector(sector, name)
    tier    = group_tier(victim["group"])
    score   = impact_score(sec_impact, tier, victim["country"])
    i_label = impact_label(score)

    embed   = build_embed(victim)
    # @here para setor crítico OU score CRITICAL
    content = "@here" if (is_critical or i_label == "CRITICAL") else ""
    return {"content": content, "embeds": [embed]}


# ─────────────────────────────────────────────────────────────
#  SUMÁRIO DIÁRIO DE GRUPOS ATIVOS
# ─────────────────────────────────────────────────────────────

def post_daily_summary(victims: list[dict]) -> None:
    """
    Posta um embed de sumário com os grupos mais ativos no ciclo.
    Chamado apenas quando há 5+ vítimas novas no mesmo run.
    """
    if len(victims) < 5:
        return

    # Conta vítimas por grupo
    group_counts: dict[str, int] = {}
    for v in victims:
        g = v["group"]
        group_counts[g] = group_counts.get(g, 0) + 1

    top_groups = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)[:8]

    lines = "\n".join(
        f"`{g:<20}` → **{c}** victim{'s' if c > 1 else ''}"
        for g, c in top_groups
    )

    embed = {
        "title":       f"📊 Ransomware activity — last cycle ({len(victims)} new victims)",
        "color":       0xB71C1C,
        "description": lines,
        "footer":      {"text": "0xD3lta Research • ransomware.live + ransomwatch"},
        "timestamp":   datetime.now(timezone.utc).isoformat(),
    }

    post_message({"content": "", "embeds": [embed]})
    time.sleep(1)


# ─────────────────────────────────────────────────────────────
#  RUNNER PRINCIPAL
# ─────────────────────────────────────────────────────────────

def run_once(
    verbose:    bool = True,
    hours:      int  = LOOKBACK_HOURS,
    min_impact: str  = "LOW",
) -> int:

    if not TOKEN or not CHANNEL_ID:
        print("❌  Configure DISCORD_TOKEN e RANSOMWARE_CHANNEL_ID no .env")
        sys.exit(1)

    seen  = load_seen()
    total = 0

    if verbose:
        print(f"\n🔄 Ransomware Tracker — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Janela: últimas {hours}h | Impacto mínimo: {min_impact}")
        print("─" * 60)

    # Coleta de ambas as fontes
    victims = fetch_ransomware_live(seen, hours)
    victims += fetch_ransomware_live(seen, hours)   # dedup via seen
    rwatch  = fetch_ransomwatch(seen, hours)

    # Deduplica entre fontes por grupo+vítima
    seen_pairs: set[str] = set()
    all_victims = []
    for v in victims + rwatch:
        pair = make_id(v["group"], v["victim"])
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            all_victims.append(v)

    # Filtra por impacto mínimo
    impact_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    min_order    = impact_order.get(min_impact.upper(), 1)

    def victim_impact(v: dict) -> int:
        _, _, sec_impact, _ = classify_sector(v["sector"], v["victim"])
        score = impact_score(sec_impact, group_tier(v["group"]), v["country"])
        return impact_order.get(impact_label(score), 1)

    all_victims = [v for v in all_victims if victim_impact(v) >= min_order]

    # Ordena: críticos primeiro → tier do grupo → score de impacto
    all_victims.sort(
        key=lambda v: (
            -victim_impact(v),
            group_tier(v["group"]),
        )
    )

    # Limita por run
    all_victims = all_victims[:MAX_PER_RUN]

    if not all_victims:
        if verbose:
            print("\n  ✅ Nenhuma vítima nova encontrada.")
        return 0

    # Sumário se houver muitas vítimas
    if len(all_victims) >= 5:
        post_daily_summary(all_victims)
        time.sleep(1)

    # Separador
    url = f"{BASE}/channels/{CHANNEL_ID}/messages"
    requests.post(
        url,
        headers=dheaders(),
        json={"content": f"\n{'─'*40}\n🔒 **Ransomware Victims** — New disclosures\n{'─'*40}"},
        timeout=10,
    )
    time.sleep(0.5)

    # Posta cada vítima
    for v in all_victims:
        _, _, sec_impact, is_crit = classify_sector(v["sector"], v["victim"])
        score   = impact_score(sec_impact, group_tier(v["group"]), v["country"])
        i_label = impact_label(score)

        if verbose:
            print(
                f"    🔒 [{i_label:<8}] {v['group']:<20} → {v['victim'][:30]}"
                + (" 🚨" if is_crit else "")
            )

        payload = build_payload(v)
        success = post_message(payload)
        if success:
            seen.add(v["id"])
            total += 1
            time.sleep(1.5)

    save_seen(seen)

    if verbose:
        print(f"\n✅ Concluído — {total} vítimas postadas")

    return total


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="0xDelta Ransomware Tracker")
    parser.add_argument("--loop",       action="store_true",    help="Loop contínuo")
    parser.add_argument("--interval",   type=int, default=3600, help="Intervalo em segundos")
    parser.add_argument("--quiet",      action="store_true",    help="Suprimir output")
    parser.add_argument("--hours",      type=int, default=LOOKBACK_HOURS, help="Janela de busca em horas")
    parser.add_argument("--min-impact", default="LOW",          help="Impacto mínimo: LOW | MEDIUM | HIGH | CRITICAL")
    args = parser.parse_args()

    kwargs = {
        "verbose":    not args.quiet,
        "hours":      args.hours,
        "min_impact": args.min_impact.upper(),
    }

    if args.loop:
        print(f"🤖 Ransomware Tracker iniciado — intervalo: {args.interval}s")
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

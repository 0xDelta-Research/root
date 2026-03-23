"""
0xD3lta Research — News & Advisories Automation Bot
=====================================================
Monitora feeds RSS de fontes de cybersecurity e posta
automaticamente no canal #news-and-advisories do Discord.

Fontes cobertas:
  - CISA KEV (Known Exploited Vulnerabilities)
  - NVD CVEs (NIST)
  - Bleeping Computer
  - The Hacker News
  - Krebs on Security
  - Securelist (Kaspersky)
  - Google Project Zero
  - SANS Internet Storm Center
  - Recorded Future
  - Unit 42 (Palo Alto)

Dependências:
    pip install requests feedparser python-dotenv

Uso:
    echo "DISCORD_TOKEN=..." >> .env
    echo "NEWS_CHANNEL_ID=..." >> .env
    python 0xdelta_news_bot.py

    # Rodar em loop contínuo (a cada 30 min):
    python 0xdelta_news_bot.py --loop --interval 1800
"""

import requests
import feedparser
import hashlib
import json
import time
import os
import sys
import argparse
from datetime import datetime, timezone
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
CHANNEL_ID = os.getenv("NEWS_CHANNEL_ID", "")
BASE       = "https://discord.com/api/v10"
SEEN_FILE  = Path("seen_entries.json")   # cache de posts já enviados

# ─────────────────────────────────────────────────────────────
#  FEEDS DE FONTES
# ─────────────────────────────────────────────────────────────

FEEDS = [
    {
        "name":  "CISA KEV",
        "url":   "https://www.cisa.gov/feeds/hse.xml",
        "emoji": "🏛️",
        "tag":   "CISA",
        "color": 0x1565C0,   # azul escuro
        "priority": "HIGH",
    },
    {
        "name":  "NVD — New CVEs",
        "url":   "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml",
        "emoji": "🆕",
        "tag":   "NVD/CVE",
        "color": 0x37474F,
        "priority": "MEDIUM",
    },
    {
        "name":  "Bleeping Computer",
        "url":   "https://www.bleepingcomputer.com/feed/",
        "emoji": "📰",
        "tag":   "BleepingComputer",
        "color": 0x455A64,
        "priority": "MEDIUM",
    },
    {
        "name":  "The Hacker News",
        "url":   "https://feeds.feedburner.com/TheHackersNews",
        "emoji": "🗞️",
        "tag":   "THN",
        "color": 0x37474F,
        "priority": "MEDIUM",
    },
    {
        "name":  "Krebs on Security",
        "url":   "https://krebsonsecurity.com/feed/",
        "emoji": "🔍",
        "tag":   "KrebsOnSecurity",
        "color": 0x1B5E20,
        "priority": "HIGH",
    },
    {
        "name":  "Securelist (Kaspersky GReAT)",
        "url":   "https://securelist.com/feed/",
        "emoji": "🔬",
        "tag":   "Securelist",
        "color": 0x880E4F,
        "priority": "HIGH",
    },
    {
        "name":  "Google Project Zero",
        "url":   "https://googleprojectzero.blogspot.com/feeds/posts/default",
        "emoji": "🔴",
        "tag":   "ProjectZero",
        "color": 0xB71C1C,
        "priority": "HIGH",
    },
    {
        "name":  "SANS ISC",
        "url":   "https://isc.sans.edu/rssfeed_full.xml",
        "emoji": "📡",
        "tag":   "SANS-ISC",
        "color": 0x004D40,
        "priority": "MEDIUM",
    },
    {
        "name":  "Unit 42 (Palo Alto)",
        "url":   "https://unit42.paloaltonetworks.com/feed/",
        "emoji": "🦁",
        "tag":   "Unit42",
        "color": 0xE65100,
        "priority": "HIGH",
    },
    {
        "name":  "Red Canary Blog",
        "url":   "https://redcanary.com/blog/feed/",
        "emoji": "🐦",
        "tag":   "RedCanary",
        "color": 0xC62828,
        "priority": "MEDIUM",
    },
]

# Keywords que elevam a prioridade para CRITICAL (gera @here automático)
CRITICAL_KEYWORDS = [
    "zero-day", "0-day", "actively exploited", "emergency patch",
    "critical rce", "remote code execution", "ransomware campaign",
    "nation-state", "critical infrastructure", "mass exploitation",
    "supply chain attack", "widespread", "actively being exploited",
]

# ─────────────────────────────────────────────────────────────
#  CACHE DE POSTS JÁ ENVIADOS
# ─────────────────────────────────────────────────────────────

def load_seen() -> set:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen: set) -> None:
    # Mantém apenas as últimas 2000 entradas para não crescer indefinidamente
    entries = list(seen)[-2000:]
    SEEN_FILE.write_text(json.dumps(entries, indent=2))


def entry_id(entry: dict, feed_name: str) -> str:
    raw = f"{feed_name}::{entry.get('link', '')}::{entry.get('title', '')}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ─────────────────────────────────────────────────────────────
#  HELPERS HTTP
# ─────────────────────────────────────────────────────────────

def discord_headers() -> dict:
    return {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (0xdelta-newsbot, 1.0)",
    }


def post_message(payload: dict) -> bool:
    """Posta uma mensagem no canal configurado. Retorna True se bem-sucedido."""
    url = f"{BASE}/channels/{CHANNEL_ID}/messages"
    for attempt in range(4):
        r = requests.post(url, headers=discord_headers(), json=payload)
        if r.status_code == 429:
            wait = r.json().get("retry_after", 2)
            print(f"  ⏳ Rate limit — aguardando {wait:.1f}s...")
            time.sleep(wait)
            continue
        if r.status_code in (200, 201):
            return True
        print(f"  ❌ Erro HTTP {r.status_code}: {r.text[:200]}")
        return False
    return False


# ─────────────────────────────────────────────────────────────
#  ANÁLISE DE PRIORIDADE
# ─────────────────────────────────────────────────────────────

def assess_priority(title: str, summary: str, base_priority: str) -> str:
    combined = (title + " " + summary).lower()
    if any(kw in combined for kw in CRITICAL_KEYWORDS):
        return "CRITICAL"
    return base_priority


def priority_config(priority: str) -> dict:
    return {
        "CRITICAL": {"emoji": "🚨", "color": 0xE53935, "mention": "@here"},
        "HIGH":     {"emoji": "⚠️",  "color": 0xFB8C00, "mention": ""},
        "MEDIUM":   {"emoji": "📌",  "color": 0x546E7A, "mention": ""},
        "LOW":      {"emoji": "ℹ️",  "color": 0x37474F, "mention": ""},
    }.get(priority, {"emoji": "📌", "color": 0x546E7A, "mention": ""})


# ─────────────────────────────────────────────────────────────
#  BUILD DISCORD EMBED
# ─────────────────────────────────────────────────────────────

def build_embed(entry: dict, feed: dict, priority: str) -> dict:
    cfg     = priority_config(priority)
    title   = entry.get("title", "No title")[:256]
    link    = entry.get("link",  "")
    summary = entry.get("summary", "")

    # Limpa HTML tags do summary se existirem
    import re
    summary = re.sub(r"<[^>]+>", "", summary).strip()
    summary = summary[:300] + "..." if len(summary) > 300 else summary

    # Timestamp
    published = entry.get("published_parsed")
    if published:
        ts = int(datetime(*published[:6], tzinfo=timezone.utc).timestamp())
        ts_str = f"<t:{ts}:R>"
    else:
        ts_str = ""

    embed = {
        "title":       f"{feed['emoji']} {title}",
        "url":         link,
        "description": summary,
        "color":       cfg["color"],
        "fields": [
            {
                "name":   "Source",
                "value":  f"`{feed['tag']}`",
                "inline": True,
            },
            {
                "name":   "Priority",
                "value":  f"{cfg['emoji']} `{priority}`",
                "inline": True,
            },
        ],
        "footer": {
            "text": f"0xD3lta Research • {feed['name']}",
        },
    }

    if ts_str:
        embed["fields"].append({
            "name":   "Published",
            "value":  ts_str,
            "inline": True,
        })

    return embed


def build_payload(entry: dict, feed: dict, priority: str) -> dict:
    embed   = build_embed(entry, feed, priority)
    cfg     = priority_config(priority)
    content = cfg["mention"] if cfg["mention"] else ""
    return {
        "content": content,
        "embeds":  [embed],
    }


# ─────────────────────────────────────────────────────────────
#  FETCH & POST LOOP
# ─────────────────────────────────────────────────────────────

def process_feed(feed: dict, seen: set) -> list[str]:
    """Processa um feed RSS e retorna lista de IDs novos postados."""
    posted_ids = []
    try:
        parsed = feedparser.parse(
            feed["url"],
            request_headers={"User-Agent": "0xDelta-NewsBot/1.0"},
        )
    except Exception as e:
        print(f"  ⚠️  Erro ao parsear {feed['name']}: {e}")
        return posted_ids

    entries = parsed.entries[:10]   # máximo 10 por feed por ciclo

    for entry in reversed(entries):  # reversed = ordem cronológica
        eid = entry_id(entry, feed["name"])
        if eid in seen:
            continue

        title    = entry.get("title", "")
        summary  = entry.get("summary", "")
        priority = assess_priority(title, summary, feed["priority"])
        payload  = build_payload(entry, feed, priority)

        print(f"  📨 [{feed['tag']}] {title[:60]}...")
        success = post_message(payload)
        if success:
            posted_ids.append(eid)
            time.sleep(1.5)  # pausa entre posts para não inundar o canal

    return posted_ids


def run_once(verbose: bool = True) -> int:
    """Executa um ciclo completo de verificação de todos os feeds."""
    if not TOKEN or not CHANNEL_ID:
        print("❌ Configure DISCORD_TOKEN e NEWS_CHANNEL_ID no .env")
        sys.exit(1)

    seen = load_seen()
    total_new = 0

    if verbose:
        print(f"\n🔄 Verificando {len(FEEDS)} feeds — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("─" * 60)

    for feed in FEEDS:
        if verbose:
            print(f"\n📡 {feed['name']}")
        new_ids = process_feed(feed, seen)
        seen.update(new_ids)
        total_new += len(new_ids)
        time.sleep(0.5)

    save_seen(seen)

    if verbose:
        print(f"\n✅ Ciclo concluído — {total_new} novas entradas postadas")

    return total_new


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="0xD3lta News Bot")
    parser.add_argument("--loop",     action="store_true",  help="Rodar em loop contínuo")
    parser.add_argument("--interval", type=int, default=1800, help="Intervalo em segundos (padrão: 1800 = 30min)")
    parser.add_argument("--quiet",    action="store_true",  help="Suprimir output verbose")
    args = parser.parse_args()

    if args.loop:
        print(f"🤖 News Bot iniciado — intervalo: {args.interval}s ({args.interval//60} min)")
        print("   Pressione Ctrl+C para parar.\n")
        while True:
            try:
                run_once(verbose=not args.quiet)
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\n👋 Bot encerrado.")
                break
            except Exception as e:
                print(f"⚠️  Erro inesperado: {e}")
                time.sleep(60)  # aguarda 1 min antes de tentar de novo
    else:
        run_once(verbose=not args.quiet)


if __name__ == "__main__":
    main()

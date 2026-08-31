"""
0xD3lta Research — Report Announcement Bot
==========================================
Anuncia no Discord os relatórios publicados no site.

Roda no workflow "Announce New Report", disparado depois que o deploy
para o GitHub Pages termina com sucesso — então o link já está no ar
quando a mensagem é enviada.

Uso:
    python 0xdelta_announce_bot.py <caminho/do/index.md> [outro/index.md ...]

Ao contrário dos bots de feed, este falha ALTO: se o Discord recusar a
mensagem por token inválido, permissão ou canal inexistente, o processo
sai com código 1 e o Actions fica vermelho.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import requests

TOKEN = os.getenv("DISCORD_TOKEN", "")
CHANNEL_ID = os.getenv("RESEARCH_CHANNEL_ID", "")
BASE = "https://discord.com/api/v10"
SITE = "https://0xdelta.org"

CONTENT_ROOT = "src/content/blog"

TEAM_COLOR = {
    "Red Team": 0xEF4444,
    "Blue Team": 0x3B82F6,
    "Purple Team": 0xA683E0,
}

RISK_MARK = {
    "CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵", "INFO": "⚪",
}


def parse_frontmatter(path: Path) -> dict:
    """Lê o bloco YAML entre '---' do topo do arquivo. Sem dependência externa."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        raise ValueError(f"{path}: frontmatter não encontrado")

    data = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        km = re.match(r'^([A-Za-z_]+):\s*(.*)$', line)
        if not km:
            continue
        key, raw = km.group(1), km.group(2).strip()
        if raw.startswith("[") and raw.endswith("]"):
            data[key] = re.findall(r'"([^"]*)"', raw)
        else:
            data[key] = raw.strip('"').strip("'")
    return data


def slug_for(path: Path) -> str:
    """src/content/blog/<time>/<cat>/<post>/index.md -> '<time>/<cat>/<post>' minúsculo.

    O Astro gera a URL e a imagem OG a partir do caminho em minúsculas.
    """
    rel = path.as_posix().split(CONTENT_ROOT + "/", 1)[1]
    return rel.rsplit("/index.md", 1)[0].lower()


def build_embed(data: dict, slug: str) -> dict:
    url = f"{SITE}/blog/{slug}/"
    team = data.get("team", "Blue Team")
    risk = data.get("risk", "")

    fields = [
        {"name": "Operator", "value": f"`{data.get('author', '—')}`", "inline": True},
        {"name": "Division", "value": f"`{team}`", "inline": True},
    ]
    if risk:
        fields.append({
            "name": "Risk",
            "value": f"{RISK_MARK.get(risk, '')} `{risk}`",
            "inline": True,
        })

    collaborators = data.get("collaborators") or []
    if collaborators:
        fields.append({
            "name": "Collaborators",
            "value": " · ".join(f"`{c}`" for c in collaborators),
            "inline": False,
        })

    description = data.get("description", "")
    if len(description) > 300:
        description = description[:297] + "..."

    return {
        "title": data.get("title", "New report")[:256],
        "url": url,
        "description": description,
        "color": TEAM_COLOR.get(team, 0x3B82F6),
        "fields": fields,
        "image": {"url": f"{SITE}/og/{slug}.png"},
        "footer": {"text": f"0xDelta Research • {data.get('category', '')}"},
    }


def post(payload: dict) -> None:
    """Envia a mensagem. Levanta exceção em qualquer falha definitiva."""
    url = f"{BASE}/channels/{CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (0xdelta-announce, 1.0)",
    }

    for attempt in range(4):
        r = requests.post(url, headers=headers, json=payload, timeout=30)

        if r.status_code in (200, 201):
            return

        # 429 é temporário: respeita o retry_after e tenta de novo.
        if r.status_code == 429:
            wait = float(r.json().get("retry_after", 2))
            print(f"  rate limit — aguardando {wait:.1f}s")
            time.sleep(min(wait, 60))
            continue

        # 401/403/404 e afins são falhas de configuração: não adianta insistir.
        raise RuntimeError(
            f"Discord recusou a mensagem — HTTP {r.status_code}: {r.text[:300]}"
        )

    raise RuntimeError("Discord respondeu 429 em todas as tentativas")


def main() -> int:
    paths = [Path(p) for p in sys.argv[1:] if p.strip()]
    if not paths:
        print("Nenhum relatório novo para anunciar.")
        return 0

    if not TOKEN or not CHANNEL_ID:
        print("ERRO: DISCORD_TOKEN e RESEARCH_CHANNEL_ID precisam estar definidos.",
              file=sys.stderr)
        return 1

    for path in paths:
        data = parse_frontmatter(path)
        slug = slug_for(path)
        embed = build_embed(data, slug)

        print(f"Anunciando: {data.get('title')} ({slug})")
        post({"embeds": [embed]})
        time.sleep(1.5)

    print(f"{len(paths)} relatório(s) anunciado(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

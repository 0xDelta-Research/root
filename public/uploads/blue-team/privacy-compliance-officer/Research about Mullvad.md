\## Revisão — ajustes necessários antes do merge

Valeu pelo post! Mas do jeito que está ele \*\*não vai aparecer no site\*\* e \*\*quebra o build\*\*. Seguem os ajustes pra alinhar ao Protocolo 0xD3LTA:

\### 1. 📁 Local do arquivo (crítico)

- [ ] Mover de `public/uploads/...` para `src/content/blog/blue-team/privacy-compliance-officer/`
- `public/uploads/` é só para \*\*vídeos/assets\*\*. O Astro carrega posts \*\*apenas\*\* de `src/content/blog/`.

\### 2. 📄 Pasta + nome do arquivo

- [ ] Criar pasta com slug (minúsculo/hífen) e nomear o arquivo como \*\*`index.md`\*\*:

`src/content/blog/blue-team/privacy-compliance-officer/mullvad-vpn-ecosystem/index.md`

- Sem nomes com espaço (ex.: `SecOps Analysis - Mullvad....md`).

\### 3. 🧩 Frontmatter obrigatório (hoje está ausente → build falha)

- [ ] Adicionar no topo do arquivo:

\```yaml

\---

title: "Operational Security Analysis: Mass Surveillance Mitigation via Mullvad VPN"

description: "SecOps analysis of Mullvad's anonymity model — identity decoupling, RAM-only infrastructure, System Transparency (stboot), and zero-retention architecture."

risk: "INFO"

pubDate: 2026-06-15

author: "SPECIEUNKN0WN\_"

team: "Blue Team"

category: "Privacy Compliance Officer"

tags: ["Privacy", "OpSec", "VPN", "Mullvad", "Anti-Surveillance"]

\---

\```

- Obrigatórios: `title`, `description`, `pubDate`, `author`, `team`, `category`.
- `author`, `team`, `category` com \*\*casing exato\*\* (`category` = `"Privacy Compliance Officer"`).
- Sem comentários (`#`) no frontmatter.

\### 4. 🧹 Limpeza de formatação (colado do Google Docs)

- [ ] Remover a linha `Line Spacing: 1.15`
- [ ] Trocar títulos `# \*\*Texto\*\*` por `## Texto` / `### Texto` (sem negrito no heading)
- [ ] Remover escapes dos números: `## \*\*1\. Anatomy...` → `## 1. Anatomy...`
- [ ] Blocos de código com a linguagem especificada (` ```http `, ` ```bash `, etc.)

\### 5. 🖼️ Imagens (se houver)

- [ ] Dentro da própria pasta do post, referenciadas com `./imagem.png`
- [ ] EXIF removido; borrar qualquer dado sensível

\### 6. 🌿 Git / Branch

- [ ] Branch no padrão `intel/mullvad-vpn-ecosystem`
- [ ] Commit em inglês: `content: add mullvad vpn opsec analysis`

\### 7. ✅ Antes de subir — testar

- [ ] Rodar `npm run dev` \*\*e\*\* `npm run build` localmente
- [ ] Confirmar que o post aparece em `/blog` e \*\*abre com o conteúdo renderizado\*\* (não só o título)

\---

Fazendo esses ajustes (principalmente \*\*1, 2 e 3\*\*), o post entra certinho. 👍

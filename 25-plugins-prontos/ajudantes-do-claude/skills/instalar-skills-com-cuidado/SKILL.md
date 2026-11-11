---
name: instalar-skills-com-cuidado
description: Receitas para instalar skills e plugins no Claude Code (estantes de skills, Instagram Agent, plugin do Codex, web-quality, Superpowers, Matt Pocock e outras), mostrando antes qualquer comando que instale algo fora do Claude Code. Use quando o usuário pedir para instalar skills, plugins ou uma "estante".
---

# Instalar skills com cuidado

Responda em português.

## Regras
- Antes de instalar, confira se a skill já existe (na lista de skills disponíveis, nos plugins e no repositório de skills do usuário). Se já existe, avise e não instale de novo.
- Tudo que instala fora do Claude Code (npm, pip, brew, curl, programas) só roda depois de mostrar o comando e o usuário aprovar.
- Login (ChatGPT, Google etc.) é sempre o usuário quem faz.
- Ao terminar, avise o que ficou pronto e teste se o comando ou a skill aparece.
- Skills pagas nunca vão para repositório público.

## Estantes (instalar só a que o usuário escolher; pergunte o número se faltar)
1. **LIMITE (gastar menos)**: Caveman (github.com/JuliusBrussee/caveman), Claude-Mem (github.com/thedotmack/claude-mem), Headroom (github.com/headroomlabs-ai/headroom)
2. **PÁGINA (design que não parece feito por IA)**: Taste (github.com/Leonxlnx/taste-skill), Impeccable (github.com/pbakaus/impeccable), Hallmark (github.com/Nutlope/hallmark)
3. **TEXTO E VÍDEO**: Humanizer (github.com/blader/humanizer), HyperFrames (github.com/heygen-com/hyperframes), Marketing Skills (github.com/coreyhaines31/marketingskills)
4. **PROGRAMAR COMO SÊNIOR**: Superpowers (github.com/obra/superpowers), Matt Pocock Skills (github.com/mattpocock/skills), Karpathy Skills (github.com/multica-ai/andrej-karpathy-skills)
5. **PESQUISA**: Last 30 Days (github.com/mvanhorn/last30days-skill), Agent Reach (github.com/Panniantong/Agent-Reach), Graphify (github.com/Graphify-Labs/graphify)

## Receitas avulsas
- **5 skills do Clube**: hyperframes (heygen-com/hyperframes), find-skills (vercel-labs/skills), agent-browser (vercel-labs/agent-browser; pede `npm i -g agent-browser`), só a grilling (mattpocock/skills), design-taste-frontend (leonxlnx/taste-skill).
- **Programar**: prototype, diagnosing-bugs, code-review e tdd (mattpocock/skills) e a Superpowers (obra/superpowers; também está no catálogo oficial: `superpowers@claude-plugins-official`).
- **Velocidade de página**: core-web-vitals e performance (addyosmani/web-quality-skills) e web-perf (cloudflare/skills).
- **Instagram Agent**: as 13 skills ig-* de github.com/Jakeschincariol/instagram-agent-skill. Confirme que o `/ig-reel` funciona. Depois copie `templates/voice.md` para `~/.claude/instagram/voice.md` e faça as perguntas para preencher com o jeito de falar do usuário.
- **Plugin do Codex** (github.com/openai/codex-plugin-cc): `/plugin marketplace add openai/codex-plugin-cc`, depois `/plugin install codex@openai-codex`, depois `/reload-plugins` e `/codex:setup`. Se faltar o Codex, mostre o comando antes (`npm install -g @openai/codex`). No fim, confirme que o `/codex:review` aparece.

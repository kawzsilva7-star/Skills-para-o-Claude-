# Skills para o Claude

Backup de todas as skills do dono, **separadas por função** (pastas numeradas). Repositório **privado**.
Caminho de cada skill: `<pasta da função>/<skill>/SKILL.md`. A lista com o que cada uma faz está em `INDICE.md`; as regras de uso (só quando precisar, para gastar menos token) estão em `LEIA-ME.md`.

Instalar no PC (Windows): `powershell -ExecutionPolicy Bypass -File .\instalar.ps1` instala ffmpeg/Python/yt-dlp/streamlink, copia as skills essenciais para `~/.claude/skills` (`-Todas` para todas) e cria a pasta `~/cortes` com o passo a passo.

Regras:
- Toda skill nova entra na pasta da sua função. Se nenhuma servir, cria-se uma pasta nova numerada.
- Skill já existente não é copiada de novo; se vier uma versão diferente, vai para `22-versoes-alternativas/`.
- Nunca colocar chaves, senhas ou dados pessoais aqui.
- Este repositório é o destino de toda skill que o dono adicionar ao GitHub. Atualiza-se com `scripts/sincronizar_skills.ps1` do bot.

# Skills para o Claude

Backup de todas as skills do dono, **separadas por função** (pastas numeradas). Repositório **privado**.
Caminho de cada skill: `<pasta da função>/<skill>/SKILL.md`. A lista com o que cada uma faz está em `INDICE.md`; as regras de uso (só quando precisar, para gastar menos token) estão em `LEIA-ME.md`.

Regras:
- Toda skill nova entra na pasta da sua função. Se nenhuma servir, cria-se uma pasta nova numerada.
- Skill já existente não é copiada de novo; se vier uma versão diferente, vai para `22-versoes-alternativas/`.
- Para gastar menos token, monte o contexto só com as skills da tarefa usando `11-economia-de-tokens/contexto-enxuto/gerar_contexto.bat`; ao receber um `<regras_ativas>`, execute APENAS as skills listadas.
- Toda skill nova ou revisada segue as regras de `21-agentes-e-automacao/aperfeicoar-skills/SKILL.md` (direção de som e imagem, estilo coerente com o roteiro, script determinístico, verificação, teste A/B).
- Nunca colocar chaves, senhas ou dados pessoais aqui.
- Este repositório é o destino de toda skill que o dono adicionar ao GitHub. Atualiza-se com `scripts/sincronizar_skills.ps1` do bot.

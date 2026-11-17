---
name: contexto-enxuto
description: Regra para gastar menos token - montar um arquivo só com as skills que a tarefa precisa (gerar_contexto.bat) e executar apenas essas. Use quando o dono quiser juntar várias skills num contexto só ou mandar um arquivo de regras ativas ao Claude.
---

# Contexto enxuto

## Regra
1. Antes de uma tarefa, escolha só as skills que ela precisa (veja `INDICE.md`).
2. Rode `gerar_contexto.bat` (Windows, nesta pasta) e digite os nomes separados por espaço, ex.: `copywriting ffmpeg`.
3. O script cria `contexto_enxuto.txt` com o conteúdo das skills dentro de `<regras_ativas>`.
4. Mande esse arquivo ao Claude (ou aponte o MCP para ele).
5. Quando receber um `<regras_ativas>`: **execute APENAS as skills listadas**, ignore funções não mencionadas e combine-as se houver mais de uma.

## Como o script acha a skill
- Primeiro `skills\<nome>.txt` na pasta de onde foi rodado.
- Senão, a pasta `<nome>` com `SKILL.md` dentro deste repositório (a primeira encontrada; se o nome existir em duas pastas, vale a primeira).
- Nome não encontrado gera `[AVISO]` e é pulado.
- `contexto_enxuto.txt` fica fora do Git (`.gitignore`).

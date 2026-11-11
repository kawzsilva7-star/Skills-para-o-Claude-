---
name: economizar-limite
description: Ajuda a gastar menos limite no Claude Code - propõe regras de economia para o CLAUDE.md (mostrando antes de salvar), mede o tamanho do CLAUDE.md e diz o que cortar, e resume a conversa em poucas linhas para continuar numa conversa nova. Use quando o usuário quiser gastar menos limite, enxugar o CLAUDE.md ou pedir um resumo para trocar de conversa.
---

# Economizar limite

Responda em português, curto e direto.

## Regras para o CLAUDE.md
Acrescente estas regras no CLAUDE.md do usuário. **Mostre antes de salvar** e só salve com o OK dele:
1. Quando um assunto terminar, avise para abrir uma conversa nova (/clear), em vez de continuar na mesma.
2. Use o modelo mais leve que resolver. Para tarefa simples, lembre de trocar para o Sonnet ou o Haiku com /model. O Opus só quando a tarefa for difícil.
3. Leia só o trecho do arquivo que importa: procure antes e abra só as linhas certas, nunca o arquivo inteiro sem precisar.
4. Respostas curtas e diretas, sem repetir o que ele já disse.

No fim, diga o tamanho do CLAUDE.md hoje (linhas e caracteres) e o que dá para cortar dele.

## Resumo para continuar em outra conversa
Quando ele pedir: resuma o que importa da conversa (decisões, arquivos e próximo passo) em poucas linhas, para ele continuar numa conversa nova sem perder nada.

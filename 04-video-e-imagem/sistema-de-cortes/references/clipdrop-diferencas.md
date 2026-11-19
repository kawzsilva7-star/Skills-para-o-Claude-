# ClipDrop (versão em inglês) — o que muda em relação ao PDF BR

O prompt do ClipDrop é o mesmo sistema, traduzido, com estas diferenças (todas já estão no código):

1. **Detecta o idioma primeiro**: roda a detecção do Whisper num trecho do meio da live com fala, diz qual idioma achou e usa em tudo (`language="en"`, `"pt"`, `"es"`...). Na dúvida, pergunta. → `transcricao.detectar_lingua`, opção `--lingua`.
2. **Palavras de reação por idioma**: inglês (no way, bro, oh my god, what, let's go, bruh, lmao, lol, holy, dude, insane, crazy, run, help, I can't believe), português (as do PDF BR) e "equivalentes" para outro idioma. → `config.REACOES`.
3. **Palavras de ligação em inglês**: and, the, we, so, but. → `config.LIGACAO`.
4. **Títulos e descrições no idioma da live.**
5. **Só o layout sem câmera** (live inteira no meio, fundo desfocado). O layout com câmera veio do PDF BR.
6. Nomes em inglês: pasta `clips/`, `clip1-title.mp4`, `titles.txt`, `best-moments-youtube.mp4`, estilos HIGHLIGHT/BOX/KARAOKE/BEASTY/MINIMAL e OUTLINE/STRIPE/WHITE BOX. O código usa os nomes em português.

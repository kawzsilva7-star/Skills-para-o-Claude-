---
name: cortes-transcrever-live
description: "Assiste" a live inteira - extrai o áudio, detecta o idioma, transcreve com o tempo de cada palavra (faster-whisper) e mede o volume de cada segundo (ebur128), guardando tudo para não refazer. Use na etapa 2 do sistema-de-cortes, ou sempre que precisar transcrever um vídeo longo com o tempo das palavras.
---

# Transcrever a live e medir o volume

Comando pronto (na pasta da live, com o Python do .venv): `python cortes.py analisar "VIDEO"` (o script fica em `sistema-de-cortes/scripts/cortes.py`).
Para forçar o idioma: `--idioma pt` (ou en, es...).

## O que o comando faz (regras para seguir, mesmo sem o script)
1. **Áudio:** `ffmpeg -i VIDEO -vn -ac 1 -ar 16000 -c:a pcm_s16le analise/audio.wav`.
2. **Pedaços de 10 min como array numpy.** Leia o WAV em blocos de 600 s e passe cada bloco ao Whisper como `float32 / 32768`. **Nunca passe o arquivo de vídeo direto**: em algumas versões, essa leitura quebra.
3. **Idioma primeiro:** detecte em trechos de 30 s com fala no meio da live (50%, 35%, 65%...) e fique com o de maior confiança. Diga ao dono qual achou. Se a confiança for baixa (< 60%), pergunte e rode de novo com `--idioma`.
4. **Transcrição rápida:** `word_timestamps=True, vad_filter=True, condition_on_previous_text=False, beam_size=1`, com o idioma fixo.
5. **Progresso:** mostre o resultado a cada bloco e, depois do 1º, quanto tempo falta.
6. **Volume de cada segundo:** filtro `ebur128=framelog=info`, porque sem `framelog=info` ele não imprime nada. Ele gera uma medida a cada 0,1 s; use o maior valor M de cada segundo.
7. **Cache:** tudo vai para `cortes/<nome-da-live>/analise/` (`audio.wav`, `volume.json`, `transcricao.json`). Se já existir, não refaça. A transcrição é salva **a cada bloco**: se o computador desligar, a próxima rodada continua de onde parou.

## Tempo
1 hora de live leva de 5 a 25 minutos, conforme o computador.

## Cuidado
A transcrição também pega fala do jogo (personagens, trailer, cutscene). Isso é tratado na etapa seguinte, `cortes-achar-momentos`.

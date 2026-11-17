---
name: cortes-volume-14-lufs
description: Ajusta o volume de um vídeo para -14 LUFS com pico real de -1 dB ou menos (padrão de TikTok, Reels, Shorts e YouTube) - loudnorm em duas passadas e correção medida até acertar. Use ao exportar cortes, o vídeo longo ou qualquer vídeo/áudio para as redes.
---

# Volume em -14 LUFS e pico real -1 dB

No sistema de cortes, isto já roda dentro do `cortar` e do `longo` (função `normalizar` do `cortes.py`). O alvo é o mesmo para os cortes e para o vídeo longo.

## Passo a passo
1. **Medir:** `ffmpeg -i ARQ -vn -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -` e leia o JSON no fim da saída (`input_i`, `input_tp`, `input_lra`, `input_thresh`, `target_offset`).
2. **2ª passada:** `loudnorm=I=-14:TP=-1:LRA=11:measured_I=..:measured_TP=..:measured_LRA=..:measured_thresh=..:offset=..:linear=true,aresample=48000`. O vídeo vai com `-c:v copy` (não recodifica a imagem); o áudio sai AAC 192k, estéreo, 48 kHz. O loudnorm devolve 192 kHz, por isso o `aresample`.
3. **Medir de novo.** Só o loudnorm costuma parar em -16 a -18 LUFS em corte curto com pausas.
4. **Corrigir:** se estiver a mais de 0,5 LU de -14, aplique `volume=+XdB` (X = -14 menos o medido) seguido de `alimiter=limit=0.84:level=0` e meça de novo. Repita até ficar a 0,5 LU ou menos e com pico real (true peak) em -1 dB ou abaixo.
5. Se o volume estiver certo mas o **pico real** passar de -1 dB (a compressão AAC cria picos), aperte o limitador (0.79, 0.74...) mantendo o ganho no alvo. Só baixar o volume tira o arquivo do alvo (num teste, foi para -14,5 LUFS).
6. **Informe os dois números finais de cada arquivo** (LUFS e pico real).

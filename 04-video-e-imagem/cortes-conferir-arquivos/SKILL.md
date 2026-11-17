---
name: cortes-conferir-arquivos
description: Confere cada vídeo exportado antes de postar - duração, tamanho (1080x1920 nos cortes, 1920x1080 no longo), se tem som, volume em -14 LUFS e pico real até -1 dB, e tira um quadro de cada corte com legenda na tela para olhar. Use no fim do sistema-de-cortes ou para validar qualquer lote de vídeos para as redes.
---

# Conferir os arquivos no final

Comando: `python cortes.py checar "VIDEO"`. Ele confere todos os `.mp4` de `cortes/<live>/`.

## O que conferir em cada arquivo
1. **Duração** (os cortes de 20 a 60 s).
2. **Tamanho:** 1080x1920 nos cortes e 1920x1080 no `melhores-momentos-youtube.mp4`.
3. **Som:** existe faixa de áudio.
4. **Volume:** -14 LUFS ± 0,5 e pico real ≤ -1 dB. Fora disso, rode de novo o ajuste (`cortes-volume-14-lufs`).
5. **Legenda e título aparecem:** o script pega, no `.ass` do corte, uma legenda no meio do vídeo e tira um quadro nesse instante para `analise/quadros/`. **Abra cada quadro com a ferramenta de leitura de imagem e olhe**: título no topo, legenda inteira em 1 linha, sem cobrir o rosto nem a ação, e zoom e layout certos.
6. Se algo falhar, corrija e confira de novo **antes** de dizer que acabou.

## Relatório final ao dono
- Onde está tudo (`cortes/<live>/`), a lista de arquivos com duração, LUFS e pico de cada um, o `titulos.txt` para os posts e quanto tempo levou.
- Lembrete curto: crédito ao streamer em todo post, sem spoiler, sem cutscene e sem rádio (`cortes-postar-e-crescer`).

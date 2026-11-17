---
name: cortes-video-longo-youtube
description: Junta os momentos aprovados de uma live num vídeo 1920x1080 de melhores momentos para o YouTube, na ordem em que aconteceram, com fade de meio segundo e áudio em -14 LUFS, e orienta como torná-lo monetizável (história ou ranking com narração). Use na etapa bônus do sistema-de-cortes ou para montar compilações 16:9.
---

# Vídeo longo de melhores momentos (YouTube)

Comando: `python cortes.py longo "VIDEO"`. Gera `cortes/<live>/melhores-momentos-youtube.mp4`.

## Regras
- Use **os momentos aprovados**, na ordem em que aconteceram na live (não na ordem de nota).
- 1920x1080: cada trecho em `scale=...:force_original_aspect_ratio=decrease,pad=1920:1080` (sem esticar), com o mesmo fps da live, `setsar=1` e `yuv420p`.
- Fade de 0,5 s entre os trechos: `xfade=transition=fade:duration=0.5:offset=O` e `acrossfade=d=0.5`. O offset de cada junção é a duração acumulada até ali menos 0,5 s por junção já feita (o script calcula).
- Áudio a -14 LUFS e pico real até -1 dB (`cortes-volume-14-lufs`). Informe os dois números.
- H.264 + AAC estéreo 48 kHz, `+faststart`.

## Para ganhar dinheiro com ele (avise o dono)
- Compilação **colada** (só trechos um atrás do outro) **não é monetizada** no YouTube.
- Transforme em **história ou ranking** ("as 5 piores fugas da semana"), com a **narração do dono** entre os momentos, abertura e fechamento próprios.
- No vídeo longo, 55% da receita de anúncio fica com o canal.
- Crédito sempre: @ do streamer na tela e link do canal na descrição.

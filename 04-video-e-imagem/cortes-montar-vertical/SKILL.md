---
name: cortes-montar-vertical
description: Monta o corte vertical 1080x1920 de um trecho de live - acha a câmera do streamer e usa o layout câmera em cima e jogo embaixo, ou, sem câmera, a live inteira com fundo desfocado; coloca o zoom de impacto na reação e exporta em H.264/AAC. Use na etapa de cortar do sistema-de-cortes ou para transformar qualquer vídeo 16:9 em vertical para Reels, TikTok ou Shorts.
---

# Montar o corte vertical

Só corte o que o dono aprovou (`"aprovado": true` no `momentos.json`).

## 1. Tem câmera?
`python cortes.py quadros "VIDEO"` tira 3 quadros (20%, 50% e 80% da live) para `analise/quadros-live/`. **Abra e olhe cada um.**
- A câmera é um retângulo com o rosto do streamer, quase sempre num canto. Anote x, y, largura e altura **por dentro da moldura colorida**, sem pegar a moldura.
- Na dúvida, mostre o quadro ao dono e pergunte onde está a câmera.

## 2. Cortar
```
python cortes.py cortar "VIDEO" --legenda destaque --titulo contorno                      # sem câmera
python cortes.py cortar "VIDEO" --legenda destaque --titulo contorno --camera 1500,40,380,300   # com câmera
python cortes.py cortar "VIDEO" ... --jogo 600,100,812,797                               # recorte do jogo escolhido por você
```
`--legenda todos` faz o 1º corte em cada estilo de legenda, para o dono escolher (veja `cortes-legendas-ass`).

## Layout COM câmera (câmera em cima, jogo embaixo, sem barra preta e sem fundo desfocado)
- **Em cima, 1080x860:** a câmera recortada sem a moldura e levada à proporção 1080:860, cortando as laterais ou o topo/base e centralizando o rosto. **Nunca estique.** Amplie com `scale=1080:860:flags=lanczos` e passe `unsharp=5:5:0.6`, porque ela é pequena.
- **Embaixo, 1080x1060:** o jogo recortado no centro da ação, sem a câmera, sem a barra e sem a legenda do player, na mesma proporção 1080:1060 (ex.: 812x797). Se a ação estiver embaixo da câmera, **priorize a ação** (pode sobrar um pedaço da câmera no canto). Sem `--jogo`, o script usa o centro da tela na altura inteira; confira no quadro se serve.
- `vstack` (860 + 1060 = 1920). O título fica sobre a câmera (MarginV ~90) e quebra em 2 linhas acima de ~22 letras. A legenda fica na emenda câmera/jogo (MarginV ~1000, Alignment 2).
- **Zoom de impacto na câmera:** uma cópia da câmera ampliada ~115% e recortada de volta para 1080x860, por cima só no trecho do pico (`overlay` com `enable`).

## Layout SEM câmera
- A live inteira na largura da tela, centro em y ≈ 860. Atrás, o mesmo vídeo ampliado e bem desfocado (`gblur`), um pouco escurecido, preenchendo o resto.
- **Zoom de impacto:** o vídeo pula para ~125% por 2,5 s e volta. Faça com uma cópia ampliada, recortada para o mesmo quadro e centralizada, sobreposta com `overlay=...:enable='between(t,a,b)'`. **Não use zoompan**: ele treme.
- Se a live não for 16:9, o script avisa: confira se o título e a legenda não cobrem a cena.

## Para os dois layouts
- O zoom vai nas **palavras de reação** (o "caraca", o grito), não só no barulho mais alto do jogo. O script usa a 1ª palavra de reação perto do pico.
- Legenda e título queimados com o filtro `subtitles` (regras em `cortes-legendas-ass`). Rode o ffmpeg **de dentro da pasta da live**, com o `.ass` em caminho relativo e `fontsdir=fontes`, porque "C:" quebra o filtro.
- Exportação: `libx264 -crf 20 -preset medium`, `yuv420p`, AAC estéreo 48 kHz 192k, `-movflags +faststart`. O volume vai para -14 LUFS (`cortes-volume-14-lufs`).
- Nome: `cortes/<live>/corte1-titulo-sem-acento.mp4`, mais o `titulos.txt` com o título e a descrição de cada corte.
- Cada corte leva cerca de 1 minuto.

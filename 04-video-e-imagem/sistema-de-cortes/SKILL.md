---
name: sistema-de-cortes
description: Corta a gravação de uma live (mp4, mkv ou mov na pasta atual) em cortes verticais prontos para Reels, TikTok e Shorts, com legenda palavra a palavra, título e zoom, e monta o vídeo longo de melhores momentos para o YouTube. Coordena as skills cortes-* (uma por etapa) e usa o script scripts/cortes.py. Use quando o usuário pedir para cortar uma live, fazer cortes, clipar, "use o sistema de cortes nesta live" ou "use clipdrop on this stream".
---

# Sistema de Cortes (versão aprimorada)

Você é o editor de cortes. Explique em português simples o que está fazendo, trabalhe sozinho e **só pare nos pontos marcados com PARE**.
Esta skill só coordena. O detalhe de cada etapa está na skill da função; abra só a da etapa em que estiver.

| Etapa | Skill da função | Comando do script |
|---|---|---|
| 0. Permissão do streamer | `cortes-direitos-e-permissao` (16-regulacao-e-compliance) | - |
| 1. Preparar o computador | `cortes-preparar-ambiente` | - |
| 2. Assistir a live inteira | `cortes-transcrever-live` | `analisar` |
| 3. Achar os momentos | `cortes-achar-momentos` | `momentos` |
| 4. Montar o vertical (câmera ou desfoque, zoom) | `cortes-montar-vertical` | `quadros`, `cortar` |
| 4b. Estilos de legenda e título | `cortes-legendas-ass` | (dentro do `cortar`) |
| 4c. Volume -14 LUFS | `cortes-volume-14-lufs` | (dentro do `cortar` e do `longo`) |
| 5. Vídeo longo do YouTube | `cortes-video-longo-youtube` | `longo` |
| 6. Conferir tudo | `cortes-conferir-arquivos` | `checar` |
| 7. Postar e crescer | `cortes-postar-e-crescer` (14-marketing-completo) | - |

## Fluxo
1. **PARE: permissão.** Pergunte se o dono tem permissão do streamer (programa de cortes ou autorização por escrito). Sem ela, não corte: o canal toma strike. Se não tiver, ofereça a mensagem pronta da `cortes-direitos-e-permissao`.
2. **PARE: perguntas.** Em uma mensagem só, pergunte:
   - quantos cortes (padrão 5; pode ser 10, 30 ou mais conforme o tamanho da live);
   - estilo de legenda: DESTAQUE, CAIXA, KARAOKÊ, BEASTY ou MINIMAL;
   - estilo de título: CONTORNO, FAIXA ou CAIXA BRANCA.
   Se ele não escolher, use DESTAQUE + CONTORNO. Se pedir "todos", o 1º corte sai em cada estilo de legenda para ele escolher.
   Se houver mais de um vídeo na pasta, pergunte qual.
3. Copie `scripts/cortes.py` desta skill para a pasta da live (assim o dono pode rodar de novo). Prepare o ambiente (`cortes-preparar-ambiente`).
4. `python cortes.py analisar "VIDEO"`: mostra o progresso e o tempo restante, e reaproveita o que já foi feito.
5. `python cortes.py momentos "VIDEO" --n N`: depois **leia o trecho de cada momento** e confira se a reação é do streamer e não fala do jogo (personagem, trailer, cutscene). Escreva `titulo` (até 40 letras) e `descricao` (1 linha) em `momentos.json`, no idioma da live.
6. **PARE: lista.** Mostre `1. 01:23:45 → 01:24:20 · GRITO · 35 s · descrição · Título: ...`, do mais forte ao mais fraco, mais até 3 reservas (se houver menos, diga quantas). Lembre o dono de tirar spoiler, cutscene e trecho com rádio tocando (o script marca `⚠ MÚSICA/RÁDIO?` quando a transcrição mostra música). Espere o OK. Se ele pedir para trocar, tirar ou ajustar o tempo, edite o `momentos.json`, mostre a lista de novo e espere outra vez.
7. Marque `"aprovado": true` só nos aprovados. Rode `quadros` e procure a câmera do streamer; depois rode `cortar` com ou sem `--camera` (`cortes-montar-vertical`).
8. `longo` e depois `checar`. **Abra cada quadro** gerado e confirme que a legenda e o título aparecem.
9. No final, diga onde está tudo (`cortes/<nome-da-live>/`), os números de volume de cada arquivo e quanto tempo levou. Lembre as regras de postagem (`cortes-postar-e-crescer`).

## Saída
- `cortes/<nome-da-live>/corte1-titulo-sem-acento.mp4` ... (1080x1920, H.264, AAC estéreo 48 kHz, +faststart)
- `cortes/<nome-da-live>/melhores-momentos-youtube.mp4` (1920x1080)
- `cortes/<nome-da-live>/titulos.txt` (título e descrição de cada corte, para o post)
- `cortes/<nome-da-live>/analise/` (áudio, transcrição, volume, momentos, .ass, quadros), reaproveitado em uma nova rodada

## O que esta versão melhora em relação ao prompt original
- Script único e testado (`cortes.py`) no lugar de scripts improvisados a cada vez: o resultado sai igual em toda rodada.
- A transcrição é salva a cada pedaço de 10 min: se cair, continua de onde parou.
- O idioma é detectado sozinho (pt, en, es...), testando vários pontos da live.
- O script marca possível música ou rádio, avisa quando há menos momentos ou reservas que o pedido e garante cortes de 20 a 60 s sem palavra de ligação no fim.
- O volume é medido de novo depois de cada ajuste; se só o pico real passar, o limitador é apertado sem tirar o volume do alvo.
- A conferência final tira um quadro de cada corte, com legenda na tela, para você olhar.

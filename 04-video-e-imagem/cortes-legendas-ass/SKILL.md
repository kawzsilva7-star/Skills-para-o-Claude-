---
name: cortes-legendas-ass
description: Menu de estilos de legenda palavra por palavra (DESTAQUE, CAIXA, KARAOKÊ, BEASTY, MINIMAL) e de título (CONTORNO, FAIXA, CAIXA BRANCA) em arquivo .ass 1080x1920, queimado com o ffmpeg. Use para mostrar o menu ao dono e montar a legenda de cortes verticais, Reels ou Shorts a partir de palavras com tempo.
---

# Legendas e títulos em .ass

O `cortes.py cortar` gera tudo sozinho (`--legenda` e `--titulo`). Use estas regras para mostrar o menu, conferir o resultado ou montar uma legenda à mão.

## Base do arquivo
- `PlayResX: 1080`, `PlayResY: 1920`, `WrapStyle: 2`, `Fontname Arial` com `Bold -1`. Dois estilos: `Leg` (legenda, Alignment 2, embaixo no centro) e `Tit` (título, Alignment 8, no topo, fixo do começo ao fim).
- Use as palavras da transcrição **beam_size=5** feita para o momento (mais certas que a 1ª passada). Se aparecer fala de personagem do jogo ou do trailer, deixe na legenda **só a fala do streamer**.
- Cores no estilo são `&HAABBGGRR`: amarelo `&H0000E5FF`, verde `&H0055FF55`, branco `&H00FFFFFF`, preto `&H00000000`, vermelho `&H002A2AE6`. No texto, a tag usa `&HBBGGRR&` (amarelo = `{\c&H00E5FF&}`).
- **Uma legenda nunca passa de 1 linha.** Se o grupo não couber em ~900 px, use menos palavras. O grupo também quebra numa pausa (> 0,6 s) e no fim de frase.
- **Nunca** crie legenda com duração zero (ela faz o título sumir) e **nunca** deixe duas legendas na tela ao mesmo tempo.

## MENU DE LEGENDA (Fontsize, BorderStyle, Outline, Shadow, MarginV)
1. **DESTAQUE** (padrão): até 3 palavras em MAIÚSCULAS, branco com contorno preto, a palavra falada em amarelo (86, 1, 7, 3, 560).
2. **CAIXA:** igual ao DESTAQUE, dentro de uma caixa preta sólida (78, BorderStyle 3 com OutlineColour preto, Outline 16, 0, 560).
3. **KARAOKÊ:** até 4 palavras; a frase aparece branca e o amarelo "enche" palavra por palavra com `\kf` (duração em centésimos). PrimaryColour amarelo, SecondaryColour branco (80, 1, 7, 3, 560).
4. **BEASTY:** UMA palavra gigante por vez, sem pontuação, em MAIÚSCULAS, alternando amarelo, verde e branco, contorno grosso e "pop" `{\fscx130\fscy130\t(0,90,\fscx100\fscy100)}` (150, 1, 12, 6, 520).
5. **MINIMAL:** até 4 palavras em minúsculas, contorno fino e sombra semitransparentes (OutlineColour `&H50000000`, BackColour `&H70000000`); a palavra falada inteira e as outras apagadas com `{\alpha&H70&}` (68, 1, 4, 2, 580).

## MENU DE TÍTULO (estilo Tit, Alignment 8, MarginV 300)
1. **CONTORNO** (padrão): branco com contorno preto (74, BorderStyle 1, Outline 7).
2. **FAIXA:** texto branco numa faixa vermelha sólida (68, BorderStyle 3, OutlineColour vermelho, Outline 18).
3. **CAIXA BRANCA:** texto preto numa caixa branca (68, BorderStyle 3, PrimaryColour preto, OutlineColour branco, Outline 18).
Título longo quebra em 2 linhas com `\N`, no espaço mais perto do meio.

## Layout com câmera
A legenda vai para a emenda câmera/jogo (MarginV ~1000) e o título vai para o topo, sobre a câmera (MarginV ~90), quebrando acima de ~22 letras.

## Fonte
- Copie uma fonte em negrito para a subpasta `fontes`: Windows `C:/Windows/Fonts/arialbd.ttf`; Mac `/System/Library/Fonts/Supplemental/Arial Bold.ttf`. No Linux, o script usa a DejaVu Sans Bold se não houver Arial.
- Rode o ffmpeg de dentro da pasta de trabalho com `subtitles=filename='caminho/relativo.ass':fontsdir=fontes`. Use caminho relativo, porque "C:" quebra o filtro.

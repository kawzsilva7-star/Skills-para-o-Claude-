# Treino Anime — Design (rascunho 1)

> Rascunho. Será ajustado com a ideia do dono (áudio/texto).

## Ideia em 1 frase
O jogador treina para ganhar **Poder**, luta contra bonecos de treino para ganhar **Moedas** e compra itens (cabelo prata, bandana, roupas) na loja.

## Estilo visual: PIXEL ART
- Mundo feito de blocos simples, cores chapadas, poucas cores por área (paleta de 16 a 32 cores).
- Texturas pequenas (16x16 ou 32x32), sem suavização.
- Interface (botões, barras, loja) em pixel art, fonte pixelada.
- Personagem: mantém o cabelo prata e a bandana já feitos. Visual pixel vem de textura pequena e cores chapadas (decisão pendente: ver "Perguntas").

### Como fazer no Roblox (técnico)
- Imagens de interface: `ImageLabel.ResampleMode = Enum.ResamplerMode.Pixelated` (mantém os pixels nítidos).
- Texturas de Parts/MeshParts: arquivos PNG pequenos (16x16 / 32x32) com cores chapadas.
- Iluminação: `Lighting.GlobalShadows = false`, `Technology = Compatibility`, céu de cor sólida, sem brilho forte.
- Fonte: usar uma fonte pixelada do Roblox (ex.: `Enum.Font.Arcade`) ou imagem de texto.
- Arte 2D de ícones (itens, armas, moedas): desenhar em Aseprite, Piskel (grátis, no navegador) ou LibreSprite e exportar PNG.

## Ciclo do jogo
1. Entra no jogo → vê **Poder** e **Moedas** (Parte 1, pronta).
2. Treina (clicar/segurar) → ganha Poder.
3. Luta com boneco de treino → ganha Moedas; mais Poder = dano maior.
4. Loja → compra cabelo, bandana, roupas.
5. Dados salvos ao sair.

## Ganhar / perder
- Ganha: boneco derrotado dá Moedas.
- Perde: se a vida do jogador chega a 0, volta ao ponto inicial (sem perder Poder).

## Partes de código (uma por vez)
1. [pronta] Dados do jogador: `Parte1_Dados.lua`
2. Treino: botão que dá Poder
3. Bonecos de treino: vida, dano, recompensa
4. Loja: comprar itens com Moedas
5. Teste do cabelo em R6/R15/Rthro: `Vitrine_Roblox.lua`
6. Interface em pixel art

## Perguntas em aberto
- Pixel art só no cenário e na interface, ou o personagem também vira "pixelado"?
- Câmera: 3ª pessoa normal ou vista de cima/lateral?
- Nome final do jogo.
- Preço dos itens (decidir depois de ver as regras do Creator Hub).

## Regras combinadas
- Nada de nome/emblema de personagem de anime. Design original.
- Não trocar letras de nomes para escapar da moderação.

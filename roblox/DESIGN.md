# Presidentes do Brasil 3D — Design (rascunho 2)

> Rascunho. Será ajustado com a ideia completa do dono.

## Ideia em 1 frase
Aventura 3D em pixel art onde o jogador viaja pela história do Brasil, uma era por vez, e encontra cada presidente (NPC) que dá um desafio curto; vencer dá Moedas e libera a próxima era.

## Estilo visual: PIXEL ART 3D
- Mundo 3D de blocos (estilo voxel), cores chapadas, paleta de 16 a 32 cores por era.
- Texturas pequenas (16x16 ou 32x32), sem suavização.
- Cada presidente: boneco pixel art com traços simples e roupa da época (caricatura leve, respeitosa).
- Interface (botões, cartas, loja) em pixel art, fonte pixelada.

### Como fazer no Roblox (técnico)
- Imagens de interface: `ImageLabel.ResampleMode = Enum.ResamplerMode.Pixelated`.
- Texturas: PNG pequenos, cores chapadas.
- Iluminação: `Lighting.GlobalShadows = false`, céu de cor sólida.
- Fonte: `Enum.Font.Arcade` ou imagem de texto.
- Modelos: montar com Parts em blocos no Studio (ou voxel no MagicaVoxel/Blockbench e exportar FBX).
- Ícones 2D: Piskel (piskelapp.com), grátis.

## Ciclo do jogo
1. Entra → vê **Moedas** e **Era atual** (Parte 1, pronta, Poder pode virar "Pontos").
2. Anda pela era (Império/República Velha, Vargas, JK, ditadura, redemocratização...).
3. Fala com o presidente (NPC) → recebe um desafio curto (quiz de história, coletar itens, corrida).
4. Vence → ganha Moedas e abre o portal da próxima era.
5. Loja: cabelo, bandana, roupas da época.
6. Dados salvos ao sair.

## Ganhar / perder
- Ganha: completa o desafio da era.
- Perde: erra o desafio ou cai do mapa → volta ao início da era (sem perder Moedas).

## Partes de código (uma por vez)
1. [pronta] Dados do jogador: `Parte1_Dados.lua`
2. Eras: portais e lista de eras liberadas
3. NPC presidente: conversa e desafio (quiz)
4. Recompensas e progresso salvo
5. Loja
6. Teste do cabelo em R6/R15/Rthro: `Vitrine_Roblox.lua`
7. Interface em pixel art

## ATENÇÃO: regras do Roblox e cuidados
- Conferir nas Regras da Comunidade do Roblox se pode representar políticos reais. Presidentes que já morreram, em tom educativo e respeitoso, são bem mais seguros. Presidentes vivos e política atual são risco de moderação: evitar.
- Nada de propaganda, campanha, ofensa ou "fake news" sobre pessoas reais.
- Usar fatos de fontes confiáveis (livros didáticos, Planalto, Arquivo Nacional) nos quizzes.
- Nada de nome/emblema de personagem de anime. Não trocar letras de nomes para escapar da moderação.

## Perguntas em aberto
- Quais presidentes entram (todos ou só alguns marcantes)? Só falecidos?
- O objetivo é educativo (quiz) ou aventura/luta com chefes?
- Pixel art no personagem do jogador também?
- Nome do jogo.

---
name: video-pixel-art
description: Refaz ou cria um vídeo vertical no padrão do vídeo fixado "Descontos Brutais" (personagens blocados estilo pixel art, balões, cartões com prints, dedo, legendas com etiquetas amarelas), reaproveitando o projeto, os clipes e as vozes que já existem para gastar o mínimo de crédito do ElevenLabs. Use quando o usuário pedir vídeo pixel art, seguir o padrão do vídeo fixado, ajustar esse vídeo ou fazer outro igual com outro texto.
---

# Vídeo pixel art (seguir o padrão do vídeo fixado)

Responda em português simples.

## Onde está o padrão
Pasta `projetos/video-fixado-descontos-brutais/` deste repositório (branch `claude/hopeful-tesla-2gcr3r`, ou `main` depois de juntada).
- **Leia só dois arquivos:** `LEIA-ME.md` (estado, decisões, códigos do ElevenLabs, pendências) e `src/Video.tsx` (a montagem).
- **Não releia o roteiro** (`roteiro-video-fixado.md`) nem refaça a ideia do zero: o vídeo pronto é o padrão. Só use o roteiro se o dono pedir para mudar a história.
- Vídeos prontos: `video-pronto/video-fixado-v2.mp4` (atual) e `v1`.
- Materiais: `public/` (clipes `clipB/C/D.mp4`, imagem `k1.png`, vozes `dono-*.mp3` e `masc-*.mp3`, música, ambiente, efeitos, prints em `shots/`).

## O padrão
- Vertical 1080 x 1920, 30 quadros por segundo, cerca de 50 s. Estilo 3D blocado (cubos) no vídeo inteiro, cenário de parque à noite.
- Personagens: o dono blocado (jaqueta jeans, camiseta branca) e o mascote (cubo laranja, chapéu preto com raio, óculos pixelados, asinhas), que voa ao lado e um pouco acima da cabeça dele.
- Cores da marca: preto, amarelo-ouro `#f2b300` e branco. Laranja só no mascote e no logo.
- Legenda embaixo, texto branco grosso, no máximo 2 linhas; palavras-chave em etiquetas amarelas com texto preto (`*palavra*` em `LEGENDAS`).
- Balões amarelos (vermelhos para dúvida): entram com "pop", flutuam, saem estourando.
- Cartões (pins) com prints reais, borda amarela, leve inclinação; dedo blocado com círculo amarelo a cada toque.
- Som: voz do dono (a voz clonada dele), voz do mascote (outra voz), música baixa que desce mais quando alguém fala, ambiente de grilos, efeitos pop/plop/puf/clique. Volume final normalizado (loudnorm -15).
- Fim: tela preta com logo, nome, @, chamada para o link da bio e "Contém links de afiliado".

## Como gastar o mínimo de crédito (do mais barato ao mais caro)
1. **Remontar sem gerar nada (0 crédito do ElevenLabs):** trocar legendas, balões, prints, botões, tempos e a ordem das cenas em `Video.tsx`. A maior parte dos pedidos cabe aqui.
2. **Reusar falas e clipes que já existem:** cortar ou reordenar os `.mp3` com ffmpeg; repetir os clipes de fundo em loop (já é assim no clipe C). Cenas novas podem reusar `clipB/C/D` como fundo, com outros balões e cartões por cima.
3. **Voz nova só para texto novo.** Uma frase nova na voz do dono ou do mascote precisa ser gerada no ElevenLabs (não dá para formar frase nova só com os áudios guardados). É barato: uma fala curta custa cerca de 35 a 180 créditos.
4. **Animação nova só para cena nova.** É a parte cara. Se a cena for parada, use a imagem com zoom lento em vez de animar.
5. **Antes de qualquer geração:** peça uma estimativa (`estimate_only`), mostre o valor ao dono e espere o OK. Gere uma vez só; nunca repita para "tentar de novo".

Preços medidos em 12/11/2026 (confira de novo, podem mudar): clipe de 10 s com o melhor modelo (Seedance 2.5) custa 62.648 créditos em 1080p e 28.007 em 720p; modelo "fast" 14.664 e "mini" 9.162 (720p); imagem em 2K cerca de 518; música de 50 s cerca de 750; efeito curto menos de 5.

## Passos
1. Ler `LEIA-ME.md` e `src/Video.tsx` do projeto. Copiar a pasta para trabalhar (`npm install` dentro dela).
2. Perguntar só o que mudou: texto, cenas, prints, links, se aceita gastar crédito. Oferecer 2 ou 3 sugestões.
3. Mostrar um plano curto: o que será reaproveitado (0 crédito), o que precisa gerar e o custo estimado. Esperar o OK.
4. Montar, conferir quadros-chave e o volume, exportar e entregar o arquivo, dizendo onde ficou.
5. Guardar tudo no repositório e atualizar o `LEIA-ME.md` do projeto (estado, créditos gastos, pendências).

## Armadilhas já resolvidas
- ElevenLabs voz: usar idioma `pt` (com `pt-BR` a gravação falha e ainda mostra preço).
- Remotion na nuvem não baixa o navegador: usar `--browser-executable` com o `chrome-headless-shell` de `/opt/pw-browsers`.
- Baixar arquivos do ElevenLabs e prints exige o ambiente liberar `elevenlabsusercontent.com`, `cdn.beacons.ai` e `http2.mlstatic.com`.
- Prints: desfocar seguidores, inscritos, preços, telefone e e-mail.
- Promessas ("confiável", "sem fraude") só valem enquanto o bot postar de lojas grandes.
- Não citar saúde na fala; o nicho aparece só na página.

## Regras do dono (valem para esta skill)
- Responda em português simples, sem termo técnico: o dono não é programador.
- Se faltar algo (link, referência, arquivo, a ideia, o público ou o objetivo), pergunte antes de começar e ofereça 2 ou 3 sugestões.
- Não invente dado, número, fonte, preço ou resultado. Se não souber, diga que não sabe. Confira números e datas.
- Tarefa grande ou que mexe em arquivos: mostre um plano curto e espere o OK. Nunca apague, publique, envie ou gaste dinheiro sem o OK.
- Teste antes de entregar e mostre a prova.
- Instalação fora do Claude Code (npm, npx, pip, programas): mostre o comando antes. Senha e chave nunca no chat.
- Post de afiliado: diga que é publicidade e não invente preço, desconto nem avaliação.

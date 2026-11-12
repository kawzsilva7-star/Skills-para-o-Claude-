# Jogo de Eleição em Pixel Art 3D — Design (rascunho 3)

Fonte: 5 áudios do dono (12/11/2026) + 2 imagens de referência.
Nome provisório: **Eleição Pixel** (a decidir).

---

## 1. A ideia, como o dono falou

**Plano geral**
- Criar vários jogos no Roblox. Primeiro alguns de teste/farm (que viciam), depois o jogo principal.
- Divulgar com vídeos: "sou novo desenvolvedor, quero fazer jogos para Roblox, me deem uma força".
- Pedir para seguir o perfil e curtir. No perfil saem os códigos dos jogos e os lançamentos.
- Discord com: links dos jogos, links das skins, códigos, e às vezes sorteio de Robux.

**Jogo principal: eleição**
- Personagens: políticos (presidentes principais e outros nomes). Cada um com ataques próprios, baseados no jeito e nas falas dele.
- "Escolha seu partido": cada partido tem sua área no mapa.
- Luta entre partidos.
- Gadgets no lugar de espadas: armas diferentes e engraçadas (cajado etc.).
- Palanque com chat de voz para discutir ideias.
- Liberar personagens: jogando (todos liberáveis com o tempo) ou com Robux (atalho). Alguns bem difíceis.
- Skins para os personagens (principal fonte de renda).
- Ao derrotar um inimigo: animação/meme de derrota do personagem.
- Mapa com várias áreas do Brasil.
- Códigos que liberam personagens, válidos por 30 dias.
- Aba de sugestões: jogadores mandam ideias de personagens e poderes.
- Visual: pixel art 3D.

---

## 2. PROBLEMA: regras do Roblox sobre política

As Regras da Comunidade do Roblox proíbem, em resumo:
- políticos reais em função oficial (governantes atuais ou recentes);
- candidatos que concorrem ou concorreram há pouco, seus slogans e material de campanha;
- partidos políticos reais;
- disputas eleitorais reais específicas.

Ou seja: **presidentes reais + partidos reais + eleição = jogo removido e conta em risco.**
Pessoas reais apanhando e com "meme de morte" piora o risco.
Não consegui abrir a página oficial nesta sessão (site bloqueado); isto veio de busca. Conferir o texto atual antes de publicar.

Fontes:
- https://en.help.roblox.com/hc/en-us/articles/203313410-Roblox-Rules-of-Conduct
- https://ag.ny.gov/sites/default/files/social-media-policy-report/2025-q4-roblox-corporation-policy.pdf
- https://www.axios.com/roblox-romance-politics-standards-bc55bc7c-6d18-4a6d-8cf7-dcaede9ac9c6.html
- https://devforum.roblox.com/t/fictional-political-parties-allowed/3188788

### Saída recomendada: tudo fictício
Mesmo jogo, mesma graça, com **políticos e partidos inventados**:
- Personagens originais por "tipo" de político: o Coronel do Interior, a Prefeita Influencer, o Deputado das Promessas, o Candidato do Meme, o Doutor Burocrata...
- Partidos inventados e engraçados: Partido do Pastel, Partido da Soneca, Partido do Churrasco...
- País fictício com cara de Brasil (praia, sertão, floresta, cidade grande, capital).
- **Sem** nome, rosto, bordão ou slogan de político real. Não vale nome real com letra trocada (regra já combinada).

Isso também protege o dono fora do Roblox (uso de imagem de pessoa real em produto pago).

---

## 3. Estilo visual (referência: 2ª foto, a cidade)

Voxel/blocos com **textura em pixel art e sombras fortes**, luz de fim de tarde, janelas acesas, placas pixeladas. Não é o estilo liso e sem textura da 1ª foto.

### Como fazer no Roblox
- `Lighting.Technology = Future`, `GlobalShadows = true` (sombras reais).
- Hora do dia perto do pôr do sol (`ClockTime` ~17.5), `Atmosphere` + `ColorCorrection` com tom quente/roxo.
- Luzes (`PointLight`/`SurfaceLight`) nas janelas e letreiros.
- Texturas: desenhar em 16x16 ou 32x32 e **ampliar para 256x256 sem suavização** antes de enviar (senão o Roblox borra). Aplicar com objeto `Texture` (repete como azulejo).
- Poucas texturas repetidas: tijolo, calçada, asfalto, parede, telhado, grama.
- Interface: `ImageLabel.ResampleMode = Pixelated`, fonte pixelada.
- Ferramentas grátis: Piskel (texturas/ícones), MagicaVoxel ou Blockbench (modelos em bloco).

Personagens: a última imagem enviada (boneco de blocos, low-poly) fica como possível referência. **Confirmar com o dono.**

---

## 4. Como o jogo funciona (versão adaptada)

1. Entra → escolhe um partido (fictício) → nasce na base do partido.
2. Escolhe um personagem liberado. Cada um tem 2 ou 3 ataques próprios.
3. Luta em arenas pelas áreas do mapa. Derrotar inimigo dá **Votos** (pontos) e **Moedas**.
4. Votos sobem o nível e liberam personagens novos. Robux é atalho, nunca a única forma.
5. Loja: skins e gadgets.
6. Praça do Palanque: área sem luta para conversar.
7. Códigos promocionais com validade.
8. Derrota: animação engraçada (personagem cai, vira confete, "perdeu a eleição"). Sem sangue.

**Ganhar / perder:** rodada de alguns minutos; ganha o partido com mais Votos. Quem é derrotado volta para a base em poucos segundos.

---

## 5. Pontos do áudio que precisam de ajuste

| Ideia | Situação | O que fazer |
|---|---|---|
| Políticos e partidos reais | Proibido pelo Roblox | Personagens e partidos fictícios |
| Voz no palanque | Voz só para contas verificadas (idade); debate político é risco | Palanque como praça social, sem tema político real |
| Aba que abre arquivo/PDF/e-mail | Roblox não envia arquivo nem e-mail de dentro do jogo | Caixa de texto no jogo (salva para o dono ler) + canal de sugestões no Discord |
| Link do Discord | Só pelos "Links sociais" da página do jogo; regras de idade | Conferir no Creator Hub |
| Sorteio de Robux | Há regras do Roblox e lei brasileira de sorteios | Conferir antes de prometer |
| "Meme de morte" | Com pessoa real é risco; com fictício, ok | Animação leve, sem sangue |
| Personagem só com Robux | Dono já decidiu: todos liberáveis jogando | Mantido |

---

## 6. Partes de código (uma por vez)

1. [pronta] Dados do jogador e salvamento: `Parte1_Dados.lua` (trocar "Poder" por "Votos" na Parte 2)
2. Partidos: escolher time e nascer na base
3. Personagens: escolher e trocar; lista de liberados salva
4. Combate: ataque básico + 1 habilidade, vida, derrota e retorno
5. Recompensas: Votos, Moedas, nível, liberar personagens
6. Loja: skins e gadgets (Moedas e Robux)
7. Códigos com validade
8. Caixa de sugestões
9. Rodadas e placar de partidos
10. Interface em pixel art

Arte (em paralelo): texturas base, 1 área do mapa, 3 personagens, 3 gadgets.

Primeiro jogo de teste (farm): pode reutilizar as partes 1, 5 e 6.

---

## 7. Perguntas para o dono

1. Aceita trocar para políticos e partidos **fictícios**? (Sem isso o jogo não passa no Roblox.)
2. Nos áudios apareceram dois nomes que não entendi bem (soou como "Superchandão" e "Enes"). Quem são?
3. A última imagem (boneco de blocos) é a referência dos personagens?
4. Quantos partidos no começo? Sugestão: 3.
5. Nome do jogo.

---
name: cortes-achar-momentos
description: Acha os melhores momentos de uma live já transcrita (GRITO pelo volume + REAÇÃO pelas palavras), escolhe começo e fim em pausas da fala (20 a 60 s), escreve título e descrição e mostra a lista para aprovação antes de cortar. Use na etapa 3 do sistema-de-cortes ou para escolher trechos virais de qualquer gravação longa com fala.
---

# Achar os momentos e montar a lista

Comando: `python cortes.py momentos "VIDEO" --n 5` (precisa do `analisar` antes). Opções: `--minimo 1.5` (nota mínima de um momento bom) e `--sem-refino` (pula a 2ª transcrição; mais rápido e menos preciso).
O resultado vai para `cortes/<live>/momentos.json`.

## Como a nota é feita
- **GRITO:** compare o volume de cada segundo com a **mediana dos segundos COM FALA** nos 2 minutos em volta. Os segundos de silêncio ficam fora da mediana, senão a fala normal parece grito. Só conta se estiver **6 dB ou mais** acima. Barulho do jogo sem voz vale menos (o script dá peso 0,35).
- **REAÇÃO:** palavras de surpresa, pânico ou comemoração no idioma da live:
  - pt: caraca, mano, meu deus, não acredito, que isso, socorro, eita, nossa, mentira, kkkk, corre;
  - en: no way, bro, oh my god, what, let's go, bruh, lmao, lol, holy, dude, insane, crazy, run, help, I can't believe;
  - outros idiomas: as expressões equivalentes.
  Também contam a risada, a palavra repetida ("corre, corre"), a exclamação e a fala que acelera de repente.
- Some os dois numa nota por segundo e pegue os N melhores que **não se sobrepõem**, mais até 3 reservas. Se a live não tiver N bons, **diga quantos achou em vez de inventar** (o script avisa).

## Começo e fim do corte
- De **20 a 60 s**. Comece de 5 a 20 s antes do pico, no **começo de uma frase** que já faça parte do momento. Se a frase anterior for de outro assunto, comece mais perto do pico, no mínimo 3 s antes.
- Termine quando acabar a frase depois do pico. Corte sempre numa pausa, nunca no meio de uma palavra e nunca numa palavra de ligação (pt: e, o, a, que, mas, aí; en: and, the, we, so, but). O fim **nunca passa do começo da palavra seguinte**.
- A 1ª passada é rápida e as frases saem longas e sem pontuação. Para escolher os limites, **transcreva de novo uns 95 s em volta do pico com beam_size=5** e use essas frases. O script já faz isso, e essas palavras servem também para a legenda.

## O que você (Claude) faz depois do script
1. **Leia o trecho de cada momento.** Se a "reação" for fala de personagem, trailer ou cutscene, e não do streamer, descarte ou ajuste. Na dúvida, ouça o trecho ou compare com o volume da voz dele.
2. Ajuste `ini`/`fim` se o começo pegar outro assunto (editando o JSON).
3. Escreva `titulo` (até 40 letras, que dê vontade de assistir e **sem mentir**) e `descricao` (1 linha), no idioma da live.
4. **PARE e mostre a lista**, do mais forte (1) ao mais fraco:
   `1. 01:23:45 → 01:24:20 · GRITO · 35 s · descrição em uma linha · Título: ...`
   Depois as reservas (até 3; se houver menos, diga quantas). Destaque os `⚠ MÚSICA/RÁDIO?` e lembre: sem spoiler, sem cutscene e sem rádio tocando (geram derrubada ou reivindicação).
5. Espere o OK. Se o dono pedir para trocar, tirar ou ajustar, refaça a lista e espere de novo. Só então marque `"aprovado": true` nos escolhidos.

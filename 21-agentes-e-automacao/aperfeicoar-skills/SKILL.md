---
name: aperfeicoar-skills
description: Regras do dono para criar, revisar e aperfeiçoar skills (principalmente as de vídeo e automação) - direção explícita de som e imagem, coerência entre estilo e roteiro, scripts determinísticos com verificação, sincronia com a narração, assets livres de direitos, custo medido e teste A/B com a mesma entrada. Use sempre que for criar uma skill nova, melhorar uma existente ou adaptar uma skill de terceiros para o repositório.
---

# Regras para aperfeiçoar skills

Origem: lições do vídeo "Testei 5 Automações GRÁTIS que Fazem Vídeos para Canal Dark" (canal Dark Sem Filtro, 16/11/2026), que comparou 5 skills de vídeo (Huashu Art Motion, Huashu Motion, Lanchu, MoneyPrinterTurbo, Cerik; nomes de ouvido) em vários modelos, sempre com o mesmo roteiro.
Aplique as regras que servirem à skill em questão. Não force regra de vídeo em skill que não é de vídeo.

## 1. A skill dirige, não só pede
- O que mais pesa no resultado é a **camada de direção**. Um prompt genérico gera um vídeo genérico.
- Toda skill de vídeo diz explicitamente:
  - **áudio:** narração, trilha, **efeitos sonoros** (moeda caindo, papel rasgando, transição, carregamento) e **ducking** (a trilha abaixa sozinha quando há fala e volta depois);
  - **câmera e movimento:** zoom, plano (primeiro ou segundo plano) e transições;
  - **o que pode e o que não pode aparecer na tela.**
- Efeito sonoro e trilha são o que mais se esquece e o que mais dá imersão. Se a skill não fala de som, ela está incompleta.

## 2. Estilo combina com o roteiro
- Antes de gerar, confira se o estilo visual combina com a narrativa. Exemplo do vídeo: "dossiê de investigação" num roteiro de economia ficou ruim em todos os modelos. Não foi culpa do modelo nem da skill, foi falta de curadoria.
- Toda skill com mais de um estilo:
  - mostra o menu com **para que serve cada estilo** (ex.: arte/pintura → história, filosofia, mitologia; motion limpo → finanças, tecnologia, geopolítica; ritmo nas batidas → mini documentário, clipe, astronomia; investigação → mistério, casos não resolvidos);
  - recomenda um estilo para o roteiro e **pergunta antes de gerar**, em vez de escolher às cegas.

## 3. Determinístico vence improvisado
- Tudo o que é mecânico (cortar, medir volume, montar legenda, sincronizar, renderizar, conferir) vai num **script Python ou de linha de comando salvo junto da skill**, e não em código improvisado a cada rodada.
- Ganhos:
  - o resultado se repete;
  - a skill funciona até em modelo mais barato ou com esforço menor;
  - gasta menos tokens.
- O modelo fica com o que exige julgamento: escolher momentos, escrever títulos, fazer a curadoria de estilo.
- O lado ruim é o vídeo sair "mais quadrado". Deixe parâmetros para variar (estilo, ritmo, cores).

## 4. Verificação embutida (os "juízes")
- A skill confere o próprio resultado antes de dizer que acabou: código, áudio (volume, se tem som), integridade de imagens e vídeos, duração e tamanho.
- Inclua a **checagem visual**: tirar quadros e olhar se há texto sobreposto, legenda cortada, objeto na frente do assunto (ex.: poste na frente da cobra), imagem repetida ou elemento que a narração não menciona.
- Essa auditoria costuma levar o dobro do tempo das outras etapas. Faça por amostragem (quadros-chave), não quadro a quadro.

## 5. Sincronia é o mínimo
- A imagem tem que mostrar **o que a narração está dizendo, naquele momento**. Se um modelo erra isso, nenhum efeito bonito salva o vídeo.
- Use a transcrição com o tempo de cada palavra para posicionar imagens, textos e zoom.
- Em vídeo com música, detecte o **BPM e as batidas fortes** e corte ou troque de imagem nelas (ex.: relâmpago na batida da bateria).
- Evite repetir a mesma imagem ou o mesmo movimento várias vezes.

## 6. Assets sem risco de direitos
- Prefira o que é gerado por código (sem imagem nem vídeo de IA: custo zero e sem conteúdo reaproveitado) ou bancos de domínio público e gratuitos: Wikimedia Commons, NASA, Met Museum, Openverse, Mixkit, Pexels, Pixabay.
- Esses bancos têm mais imagem que vídeo (~70% imagem). Use zoom e movimento para a imagem parada não cansar.
- **Busca de asset em inglês: traduza o conceito, não a palavra.** A tradução literal traz imagem errada. Gere 2 ou 3 termos de busca por cena e confira o resultado antes de usar.
- Pexels e Pixabay pedem chave de API. A skill diz isso e pede a chave do jeito seguro, nunca no chat.

## 7. Idioma e clareza das instruções
- Skill de terceiros escrita em chinês (ou outro idioma pouco treinado) rende menos, principalmente em modelos menores. Ao trazer para o repositório, **reescreva as instruções em português ou inglês claros**.
- Para traduzir uma página no navegador: botão direito → "Traduzir para o português".

## 8. Custo, tempo e esforço
- Registre na skill quanto leva e quanto gasta. O tempo **não cresce em linha reta** com a duração do vídeo: instalação, checagem e auditoria são quase fixas.
- Teste com esforço menor antes de usar o máximo: se a qualidade agradar, sobram mais vídeos no limite (de 5 horas, da semana).
- Esforço máximo em alguns modelos pensa demais e demora horas. Se uma etapa passa muito do tempo esperado, pare e investigue em vez de esperar.
- Tendências observadas:
  - o Claude caprichou mais no design e nos efeitos sonoros, mas tende a exagerar (muita coisa ao mesmo tempo). Peça **contenção e minimalismo** quando o roteiro for sério;
  - o GPT foi mais rápido e econômico, mas esqueceu efeito sonoro. Peça o som explicitamente.

## 9. Teste A/B com a mesma entrada
- Para comparar versões, modelos ou estilos, use **o mesmo roteiro e o mesmo áudio** em todos. Só assim a diferença é da skill ou do modelo.
- Guarde o prompt usado, o modelo, o esforço, o tempo e o resultado (ex.: `testes/AAAA-MM-DD-nome.md`). Mude uma coisa por vez.

## 10. Saídas reaproveitáveis
- Quando fizer sentido, ofereça exportar só as animações com **fundo transparente**, para usar em outro editor.
- Renderização no navegador (Remotion, HyperFrames) gasta muita memória RAM e não usa a placa de vídeo. Em vídeo longo, renderize em partes e avise o dono.
- Legenda é escolha do canal: alguns acham que deixa "cara de IA". Pergunte em vez de sempre colocar (em cortes de live ela é o padrão).

## Checklist ao criar ou revisar uma skill
- [ ] Direção explícita de áudio (trilha, efeitos, ducking), câmera e o que não pode aparecer
- [ ] Menu de estilos com "para que serve" e pergunta antes de gerar
- [ ] Partes mecânicas em script salvo e testado
- [ ] Verificação no final (técnica e visual, por amostragem)
- [ ] Sincronia com a narração ou a batida
- [ ] Assets livres de direitos, com busca por conceito
- [ ] Instruções em português ou inglês claros
- [ ] Tempo e custo anotados, sugestão de esforço
- [ ] Testada com uma entrada fixa (A/B) antes de entrar no repositório

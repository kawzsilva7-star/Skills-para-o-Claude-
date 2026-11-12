# Notas do projeto: site Mega Motors (prévia)

Arquivo de memória para continuar o trabalho em outra conversa. Leia tudo antes de mexer.
Atualizado em 2026-11-12.

## Onde está tudo
- **Código do site (fonte):** este repositório privado `kawzsilva7-star/Skills-para-o-Claude-`, branch `claude/keen-keller-wkf1qe`, pasta `mega-motors-previa/`.
- **Site publicado:** repositório público `kawzsilva7-star/Megamotors`, branch `main`, arquivos na raiz.
  Link: https://kawzsilva7-star.github.io/Megamotors/
  GitHub Pages configurado pelo dono em Settings > Pages: Deploy from a branch, `main`, `/ (raiz)`.
- **Como atualizar o site:** editar em `mega-motors-previa/`, testar, commitar e subir na branch acima. Depois copiar os arquivos alterados (`index.html`, `dados.js`, `imagens/`, `videos/`) para a raiz do repositório Megamotors e dar push em `main`. O link se atualiza em 1 a 2 minutos (Ctrl+F5 se aparecer a versão antiga).
- Para mexer no Megamotors é preciso anexar o repositório com permissão de escrita (`add_repo` com `access: push`) e clonar em `/home/user/megamotors`.
- O GitHub Pages não pode ser ligado por ferramenta; é um clique do dono.

## Estrutura do site (HTML, CSS e JS simples, sem bibliotecas, mobile first)
- `index.html` (CSS e JS embutidos), `dados.js` (TODOS os textos, produtos, preços, serviços, perguntas, links), pasta `imagens/`, pasta `videos/`.
- Cada pasta tem um `LEIA-ME.txt` com os nomes de arquivo esperados. Foto que não existe vira um quadro tracejado "[FOTO]".
- Visual: fundo preto/cinza escuro, amarelo `#FFD400`, botões grandes.
- Seções (ordem): topo com fachada + WhatsApp + botão Horários (status aberto/fechado e "Agendar horário"), catálogo com filtro, test drive, assistência técnica (serviços precificados, cada um abre o WhatsApp), vídeos de manutenção ("Em breve"), seminovos e consignados, sobre nós (fotos da loja e da equipe), benefícios, avaliações de clientes (selo grande, caixa "Avalie no Google", carrossel de vídeos e fotos com item central em destaque e visualizador em tela grande), perguntas em chat sem IA, onde estamos (mapa), trabalhe conosco, rodapé com aviso "Prévia de demonstração", botão fixo do WhatsApp. A seção Parcerias foi removida a pedido do dono.

## Dados da loja
- Mega Motors - Mobilidade Elétrica. Frase: "A forma inteligente de se locomover".
- Endereço: Av. São José dos Campos, 2410 - Parque São Martinho, Campinas - SP, CEP 13040-565 (confirmado pelo Google).
- Horário: segunda a sexta 9h às 19h, sábado 9h às 17h (confirmado pelos stories da loja), domingo fechado.
- WhatsApp: 5519999499216 (`https://wa.me/5519999499216`). Instagram: @megamotors.eletrica.
- E-mail no site: o que aparece no perfil do WhatsApp da loja (está em `dados.js`).
- Link do Google Maps (Como chegar): https://maps.app.goo.gl/PyJKYSdRAHc4Tt3g7
- Link direto de avaliação do Google: https://search.google.com/local/writereview?placeid=ChIJ1Zq91evPyJQRTAlzcfRIwjw

## Decisões do dono
- Nada de inventar dados: o que não é real fica como marcador `[MODELO]`, `[POTÊNCIA]`, `[RESPOSTA]` etc.
- Produtos e preços são **de exemplo** (selo "Preço de exemplo"/"Exemplo"). Fotos das 7 scooters e 2 triciclos são reais (recortes do Instagram da loja). Bike, patinete, infantil e capacete ainda sem foto (cards de exemplo com quadro tracejado). O dono não consegue as fotos agora; vai pedir à loja. Foi oferecido esconder esses 4 cards até chegarem as fotos (ainda sem resposta).
- Serviços da assistência: preços de exemplo ("Serviços (exemplo)"), todos levam ao WhatsApp com mensagem pronta.
- Vídeos de manutenção: seção mostra "Em breve" (lista `videos: []` em `dados.js`).
- Perguntas do chat: horário, endereço, outras marcas, seminovos, test drive e pagamento têm resposta real. Autonomia, carga, garantia e habilitação/emplacamento estão como "PROVISÓRIA" (genéricas). Não usar a "Visão geral" do Google, que é gerada por IA e pode estar errada (falava em 30 meses de garantia, sem CNH e outro endereço).
- Estilo do carrossel de avaliações aprovado pelo dono: item central em destaque, vizinhos apagados, toque abre em tela grande como YouTube.
- Selo redondo (mulher loira + cachorro golden, feito no ChatGPT) está em `imagens/selo.png`, grande, no topo das avaliações. Dono aprovou. Confirmar que a pessoa retratada autorizou o uso como imagem da marca.

## Pendências
1. Fotos de bike, patinete, infantil e capacete (a loja vai mandar).
2. Preços e nomes reais das motos e dos serviços; confirmar os nomes `[MODELO]`.
3. Trocar as respostas "PROVISÓRIA" do chat pelas reais.
4. Texto do "Sobre nós" (história, tempo de mercado, diferenciais). Hoje há um parágrafo básico mais um marcador.
5. Vídeos de manutenção (hoje "Em breve").
6. Foto da equipe: só existem 3 recortes do vídeo "Ficha aprovada" (dois rapazes de boné e a mulher loira). O dono disse que o resto da equipe não tem foto.
7. Opcional: esconder os 4 cards sem foto; usar o selo também no "Sobre nós"; botão de avaliação também no topo (o dono pediu mais destaque e já foi feito dentro das avaliações).

## Cuidados
- Fotos e vídeos de clientes e de crianças vieram do Instagram da própria loja (enviados pelo dono). O repositório Megamotors é **público**: confirmar com a loja que há autorização. Um vídeo traz o @ de uma cliente na legenda.
- As 3 fotos de loja tiradas de contas de terceiros (Zynko, Leandro Melo) foram **substituídas** por quadros dos vídeos da própria loja.
- Não colocar chaves, senhas ou dados pessoais nos repositórios.

## Sobre vídeos com áudio (conversa mais recente)
- As skills de vídeo e áudio estão em `04-video-e-imagem/` (remotion, hyperframes, video-use, ffmpeg, text-to-speech, music, sound-effects, dubbing, etc.). As de áudio gerado usam ElevenLabs (pago, exige chave; não está configurada e não se sabe se o ambiente acessa o serviço).
- Neste ambiente existe `ffmpeg`. Não há voz sintética local instalada.
- Recomendação dada ao dono: **não precisa de ElevenLabs agora**. Ele grava uma voz no celular (15 a 30 s) e/ou manda uma música, e a montagem é feita com ffmpeg (fotos das motos, preço, selo, logo, botão do WhatsApp no final). Assunto do primeiro vídeo ainda não definido.
- Nunca pedir ao dono para colar chave na conversa; usar o formulário seguro de credencial.

## Como retomar numa conversa nova
Peça ao Claude: "Leia `NOTAS-MEGA-MOTORS.md` no repositório Skills-para-o-Claude- (branch `claude/keen-keller-wkf1qe`) e continue o site da Mega Motors."

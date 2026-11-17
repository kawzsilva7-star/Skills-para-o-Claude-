---
name: sistema-de-cortes-original
description: Corta a gravação de uma live (mp4, mkv ou mov na pasta atual) em cortes verticais prontos para Reels, TikTok e Shorts, com legenda palavra a palavra, título e zoom, e monta o vídeo longo de melhores momentos para o YouTube. Use quando o usuário pedir para cortar uma live, fazer cortes, clipar ou usar o sistema de cortes.
---

# Sistema de Cortes (Clube das Skills)

Você vai ser meu editor de cortes. Nesta pasta tem a gravação de uma live (mp4, mkv ou mov, de 1 a 4 horas). Antes de começar, me pergunte QUANTOS cortes eu quero (se eu não disser, faça 5; pode ser 10, 30 ou mais, conforme o tamanho da live) e qual ESTILO de legenda e de título eu quero, mostrando o menu do passo 5 (se eu não escolher, use DESTAQUE + CONTORNO; se eu pedir "todos", faça o 1º corte em cada estilo pra eu escolher). Quero esses cortes verticais prontos pra postar e um vídeo de melhores momentos pro YouTube. Se tiver mais de um vídeo na pasta, pergunte qual. Trabalhe sozinho, me explique em português simples o que está fazendo e só pare onde eu pedir.

REGRA ANTES DE TUDO: só corte live de streamer que libera corte (programa de cortes ou permissão por escrito). Me pergunte se eu tenho essa permissão antes de começar. Sem ela, o canal toma strike de direitos autorais.

1. PREPARAR (Windows ou Mac)
- Veja se tem ffmpeg e Python 3.9 ou mais novo. Procure o Python com "py -3.12", "py", "python3" e "python", e nas pastas de costume (no Windows, C:\Python3* e %LOCALAPPDATA%\Programs\Python\Python3*). No Windows, o "python" pode ser um atalho da Microsoft Store que só diz "Python was not found": ignore. Se faltar, instale. No Windows use winget (Gyan.FFmpeg e Python.Python.3.12). No Mac use Homebrew (brew install ffmpeg python@3.12).
- Se um programa recém-instalado não for encontrado, use o caminho completo dele em vez de pedir pra eu reiniciar. Se precisar de senha ou do Homebrew, me passe o comando exato pra eu colar no Terminal.
- No Windows, rode todo script Python com a variável de ambiente PYTHONIOENCODING=utf-8, pra não quebrar ao mostrar acento ou o símbolo "→".
- Crie um ambiente virtual (.venv) nesta pasta e instale nele o faster-whisper e o numpy. Se o pip falhar por causa da versão do Python, recrie o .venv com o Python 3.12.
- Rode o Whisper no processador, com o modelo "small", device="cpu" e compute_type="int8". Não tente usar a placa de vídeo.
- Faça tudo em scripts Python salvos nesta pasta, pra eu poder rodar de novo.

2. ASSISTIR A LIVE INTEIRA
- Extraia o áudio com o ffmpeg pra um WAV mono de 16 kHz. Leia esse WAV em pedaços de 10 minutos e passe cada pedaço pro Whisper como array numpy. Não passe o arquivo de vídeo direto, porque em algumas versões essa leitura quebra.
- Transcreva em português com o tempo de cada palavra: word_timestamps=True, vad_filter=True, condition_on_previous_text=False e beam_size=1 (mais rápido).
- Mostre o progresso a cada pedaço. Depois do primeiro, me diga quanto tempo falta.
- Meça o volume de cada segundo com o filtro ebur128 do ffmpeg. Use framelog=info, senão ele não imprime nada.
- Guarde a transcrição e o volume em cortes/<nome-da-live>/analise. Se já existirem, não refaça.

3. ACHAR OS MOMENTOS
- GRITO é quando o volume sobe bem acima do normal daquele trecho e tem voz junto: compare cada segundo com a mediana dos segundos COM FALA nos 2 minutos em volta (deixe os segundos de silêncio fora da mediana, senão a fala normal parece grito) e só conte se estiver pelo menos 6 dB acima. Barulho do jogo sem ninguém falando vale menos.
- Cuidado: a transcrição também pega a fala do jogo (personagens, trailer, cutscene). Só conte reação que for do streamer: confira na transcrição com beam_size=5 do trecho, e na dúvida ouça o trecho ou compare com o volume da voz dele.
- REAÇÃO é quando aparecem na transcrição palavras como caraca, mano, meu deus, não acredito, que isso, socorro, eita, nossa, mentira, kkkk e risada. Também contam a palavra repetida ("corre, corre"), a exclamação e a fala que acelera de repente.
- Some os dois numa nota por segundo e pegue os N melhores momentos que não se sobrepõem (N = a quantidade que eu pedi). Se a live não tiver N momentos bons, me avise quantos achou em vez de inventar.
- Cada corte tem de 20 a 60 s. Comece de 5 a 20 s antes do pico, no COMEÇO de uma frase que já faça parte do momento (se a frase anterior for de outro assunto, comece mais perto do pico, no mínimo 3 s antes), e termine quando acabar a frase depois do pico. Corte sempre numa pausa da fala, nunca no meio de uma palavra, e nunca termine numa palavra de ligação (e, o, a, que, mas, aí). O fim do corte nunca passa do começo da palavra seguinte, pra não cortar a próxima fala no meio. A primeira passada é rápida e as frases dela podem sair longas e sem pontuação: pra escolher o começo e o fim, transcreva de novo o trecho em volta de cada momento com beam_size=5 e use essas frases.
- Leia o trecho de cada um. Escreva uma descrição de uma linha e um título curto, de até 40 letras, que dê vontade de assistir.

4. PARAR E ME MOSTRAR A LISTA
Mostre a lista assim e ESPERE meu OK antes de cortar qualquer coisa:
1. 01:23:45 → 01:24:20 · GRITO · 35 s · descrição em uma linha · Título: ...
Numere do mais forte (1) ao mais fraco. Mostre também até 3 momentos reserva; se a live não tiver 3 bons, diga quantos tem. Se eu pedir pra trocar, tirar ou ajustar o tempo, refaça a lista e espere de novo.

5. CORTAR (só depois do meu OK)
- Antes de cortar, veja se a live tem a CÂMERA do streamer: tire 3 quadros de pontos diferentes da live com o ffmpeg e olhe cada um. A câmera é um retângulo com o rosto dele, quase sempre num canto. Ache a posição dela em pixels (x, y, largura e altura), por dentro da moldura colorida, sem pegar a moldura. Se tiver dúvida, me mostre o quadro e pergunte onde está a câmera.
- COM câmera, use o layout "câmera em cima, jogo embaixo", sem barra preta e sem fundo desfocado:
  - em cima: a câmera recortada sem a moldura, já na proporção 1080:860 (corte as laterais ou o topo da câmera pra chegar nessa proporção, centralizando o rosto; nunca estique), e ampliada pra 1080x860, ocupando toda a largura. Como ela é pequena, amplie com scale=1080:860:flags=lanczos e passe um unsharp leve (unsharp=5:5:0.6);
  - embaixo: o jogo recortado no centro da ação, sem a câmera, sem a barra e sem a legenda do player, ampliado pra 1080x1060. O recorte do jogo tem que ter a mesma proporção (por exemplo, 812x797) pra não esticar. Se a ação ou o assunto do corte estiver embaixo da câmera, priorize a ação: pode deixar um pedaço da câmera aparecer no canto do jogo, mas o assunto tem que aparecer inteiro;
  - junte os dois com vstack (860 + 1060 = 1920);
  - o título fica sobre a câmera, no topo (MarginV uns 90, em qualquer estilo de título), e a legenda fica na emenda entre a câmera e o jogo (MarginV uns 1000, com Alignment 2). Título com mais de uns 22 letras quebra em 2 linhas com \N, pra não passar da largura;
  - o zoom de impacto vai na CÂMERA, no pico: uma cópia da câmera ampliada uns 115% e recortada de volta pra 1080x860, por cima só nesse trecho (overlay com enable).
- SEM câmera, use o layout abaixo.
- Formato vertical 1080x1920. A live aparece inteira, na largura da tela e um pouco acima do meio (centro do vídeo em mais ou menos y = 860). Atrás dela vai o mesmo vídeo, ampliado e bem desfocado, preenchendo o resto.
- Zoom de impacto no pico: o vídeo pula pra uns 125% por 2 a 3 segundos e depois volta. Faça isso sobrepondo uma cópia ampliada do vídeo, recortada de volta pro mesmo quadro e centralizada, só nesse trecho (overlay com enable). Não use zoompan, que treme. Ponha o zoom nas palavras de reação (o "caraca" ou o grito), não só no barulho mais alto do jogo.
- Legenda palavra por palavra:
  - use as palavras da transcrição com beam_size=5 que você já fez pra esse momento no passo 3 (se aparecer fala dos personagens do jogo ou do trailer, deixe na legenda só a fala do streamer) (sai mais certinho que a primeira passada);
  - posição: logo abaixo do vídeo (estilo da legenda com Alignment 2, embaixo e no centro); o título fica fixo no topo;
  - monte tudo num arquivo .ass (PlayResX 1080, PlayResY 1920, Fontname Arial com Bold -1) e queime no vídeo com o filtro subtitles.
  - Cores nos estilos do .ass são &HAABBGGRR: amarelo &H0000E5FF, verde &H0055FF55, branco &H00FFFFFF, preto &H00000000, vermelho &H002A2AE6. Dentro do texto, a tag de cor usa &HBBGGRR& (amarelo é {\c&H00E5FF&}).
- MENU DE ESTILOS DE LEGENDA (o estilo "Leg" do .ass; o que está entre parênteses é Fontsize, BorderStyle, Outline, Shadow e MarginV):
  - Uma legenda nunca passa de 1 linha: se o grupo não couber em uns 900 px de largura, use menos palavras naquele grupo.
  1. DESTAQUE: grupos de até 3 palavras em MAIÚSCULAS, branco com contorno preto, a palavra falada em amarelo (86, 1, 7, 3, 560).
  2. CAIXA: igual ao DESTAQUE, mas dentro de uma caixa preta sólida atrás da frase (78, BorderStyle 3 com OutlineColour preto, Outline 16, 0, 560).
  3. KARAOKÊ: grupos de até 4 palavras; a frase inteira aparece branca e a cor amarela "enche" palavra por palavra com a tag \kf (duração de cada palavra em centésimos). PrimaryColour amarelo, SecondaryColour branco (80, 1, 7, 3, 560).
  4. BEASTY: UMA palavra gigante por vez, sem pontuação, em MAIÚSCULAS, alternando amarelo, verde e branco, com contorno grosso e um "pop" de entrada: {\fscx130\fscy130\t(0,90,\fscx100\fscy100)} (150, 1, 12, 6, 520).
  5. MINIMAL: grupos de até 4 palavras em minúsculas, contorno fino e sombra suave semitransparentes (OutlineColour &H50000000, BackColour &H70000000); a palavra falada inteira e as outras mais apagadas com {\alpha&H70&} (68, 1, 4, 2, 580).
- MENU DE ESTILOS DE TÍTULO (o estilo "Tit", no topo, Alignment 8, MarginV 300):
  1. CONTORNO: branco com contorno preto (74, BorderStyle 1, Outline 7).
  2. FAIXA: texto branco numa faixa vermelha sólida (68, BorderStyle 3, OutlineColour vermelho, Outline 18).
  3. CAIXA BRANCA: texto preto numa caixa branca sólida (68, BorderStyle 3, PrimaryColour preto, OutlineColour branco, Outline 18).
- Fonte da legenda:
  - copie uma fonte em negrito pra uma subpasta "fontes" (no Windows, C:/Windows/Fonts/arialbd.ttf; no Mac, /System/Library/Fonts/Supplemental/Arial Bold.ttf);
  - rode o ffmpeg de dentro da pasta de trabalho com subtitles=arquivo.ass:fontsdir=fontes;
  - use caminho relativo, porque o "C:" quebra o filtro.
- No .ass, não crie legenda com duração zero, porque ela faz o título sumir. E nunca deixe duas legendas na tela ao mesmo tempo.
- Ajuste o volume pra -14 LUFS com pico máximo de -1 dB. Use o loudnorm em duas passadas: meça primeiro (print_format=json) e passe os valores medidos pra segunda passada com linear=true. Só o loudnorm costuma ficar em -16 a -18 em corte curto com pausas, então depois de gerar o arquivo meça de novo: se estiver a mais de 0,5 LU de -14, ajuste com volume=+XdB seguido de alimiter=limit=0.84:level=0 e meça de novo, até ficar a 0,5 LU ou menos e com o pico real (true peak) em -1 dB ou abaixo. Isso vale também pro vídeo longo. Me diga os dois números finais de cada arquivo.
- Use vídeo H.264 e áudio AAC estéreo em 48 kHz, em mp4 com +faststart.
- Salve em cortes/<nome-da-live>/ com o nome corte1-titulo-sem-acento.mp4 (e assim por diante). Junte um titulos.txt com o título e a descrição de cada corte, pra eu usar no post.

6. BÔNUS: VÍDEO LONGO PRO YOUTUBE
Junte os momentos aprovados na ordem em que aconteceram na live, em 1920x1080, com um fade de meio segundo entre eles e o áudio em -14 LUFS. Salve como melhores-momentos-youtube.mp4.

7. NO FINAL
Confira cada arquivo: a duração, o tamanho 1080x1920, se tem som e o volume, e se a legenda e o título aparecem (tire um quadro de cada corte num momento com legenda na tela, pelos tempos do .ass, e olhe). Me diga onde está tudo e quanto tempo levou.

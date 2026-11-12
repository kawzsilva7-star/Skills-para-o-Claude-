# Vídeo fixado "Descontos Brutais": estado em 12/11/2026

Tudo o que é preciso para continuar o vídeo em outra sessão está nesta pasta.
O roteiro original do dono é `roteiro-video-fixado.md`.

## O que está pronto
- **Versão final (v3), 55,7 s, 1080 x 1920:**
  - `video-pronto/video-fixado-v3-instagram-tiktok.mp4` (termina com "Clica no link da bio").
  - `video-pronto/video-fixado-v3-telegram-facebook.mp4` (termina com "Clica no link aqui embaixo").
- Versões antigas: `video-fixado-v1.mp4` e `video-fixado-v2.mp4`.
- Página de produtos (`Descontos_Brutais.Br`, branch `main`): botão "💬 GRUPO DO WHATSAPP" publicado, logo abaixo do Telegram.
  Link usado: `https://chat.whatsapp.com/LOSj2Ykzd0L5ezYTVGN3pa`. A mudança está no gerador (`src/pagina/gerador.py`) e em `docs/index.html`.

## Como o vídeo é montado
- Montagem em Remotion: `src/Video.tsx` (tempos das cenas ficam no objeto `T`, legendas em `LEGENDAS`, com tempos medidos nas pausas das gravações). Duas composições: `VideoFixado` (Instagram/TikTok) e `VideoFixadoOutras` (Telegram/Facebook).
- Materiais em `public/`:
  - `clipB.mp4` (cena 3), `clipC.mp4` (cenas 4 a 6, em repetição), `clipD.mp4` (cena 7): animações de IA em 1080p.
  - `k1.png`: imagem do dono sozinho, usada nas cenas 1 e 2 com zoom lento (não há clipe animado para elas).
  - `shots/site-full.png`: captura real da página de produtos (gerada por `tools/shots.js`).
  - `shots/insta.png`: print real do Instagram enviado pelo dono, com números borrados.
  - `shots/beacons.png`: print do Beacons enviado pelo dono (cena 5, toque em "VER PRODUTOS").
  - `masc-2n.mp3`: fala dos nichos (cena 4). `masc-6o.mp3`: fala final da versão Telegram/Facebook.
  - Áudios: `dono-*.mp3` (voz clonada "Minha voz"), `masc-*.mp3` (voz "Matheus - Energetic and Dynamic"), `musica.mp3`, `ambiente.mp3`, efeitos.

### Exportar de novo
```bash
npm install
```
```bash
npx remotion render src/index.ts VideoFixado out/bruto.mp4 --codec=h264 --crf=17 --browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
```
```bash
ffmpeg -y -i out/bruto.mp4 -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -af "loudnorm=I=-15:TP=-1.5:LRA=11" -c:a aac -b:a 192k -movflags +faststart out/video-fixado.mp4
```
Para a versão Telegram/Facebook, troque `VideoFixado` por `VideoFixadoOutras`. Na nuvem, o Remotion não consegue baixar o navegador dele; por isso o `--browser-executable` acima (o caminho pode mudar de versão).

## ElevenLabs
- Projeto (flow) do vídeo: `gfZU8r3BEHK3urChxeCi` ("Vídeo fixado - Descontos Brutais"). Projeto antigo com os personagens: `EY82yvaPPikUkiwPu1H9`.
- Vozes: dono `Xe7E9Z5crYh1h7GiQLRm`; mascote `NQmLEqxcRTkWYIYZSYod`. Modelo `eleven_v4`, idioma `pt` (com `pt-BR` a gravação falha).
- Nós úteis no flow:
  - Clipe A (cenas 1 e 2), **preparado e ainda não gerado**: `SKGbZZuuUFNNXnOithun` (10 s, 1080p, 62.648 créditos; 720p custa 28.007).
  - Clipe B `AhNsI2kEnqxzlXXM91fP`, clipe C `ImMps0kfTfgGGTS1mrFS`, clipe D `YulZfGEUdQvtg58B1ah5`.
  - Imagens de base: dono sozinho `wqXxflqBzt8d2aEEuvGp`; dono + mascote `7nQ3vFikS5ms0wvOISl5`; os dois olhando para cima `YSU8sQRm3JPSJyyhItOx`.
- Gasto até aqui: cerca de 126,4 mil créditos (119 mil em 19 s de animação 1080p, o resto em vozes, música, efeitos e imagens). Em 12/11, depois da v3, restavam cerca de 2.250 créditos.
- Falas da v3: nichos `U1OldHXYVKbZC9cTy77b` (usada a 1ª gravação) e final Telegram/Facebook `uSLUcmKT11kH9GvDHoHg` (usada a 2ª).
- Para baixar arquivos gerados, o ambiente precisa liberar `elevenlabsusercontent.com` (o ambiente "Skills-para-o-Claude (videos)" já libera, junto com `cdn.beacons.ai` e `http2.mlstatic.com`).

## Decisões do dono
- Qualidade: máxima (1080p). WhatsApp: existe, manter na fala e no vídeo. TikTok `@achadosbiblicais`: está certo.
- Link da bio: **continua no Beacons** (decisão do dono em 12/11). O caminho real é: link da bio -> Beacons -> toque em "VER PRODUTOS" -> página de produtos (GitHub, com o botão do WhatsApp). O Beacons não precisa do WhatsApp.

## Pendências
1. **Única pendência:** animar as cenas 1 e 2 (clipe A, nó `SKGbZZuuUFNNXnOithun`, 10 s em 1080p, 62.648 créditos). O dono aprovou em 12/11, mas a conta tinha só 2.619 créditos e nada foi cobrado. Quando houver crédito: gerar, baixar para `public/clipA.mp4` (converter para H.264 como os outros), trocar `<DonoSozinho />` por esse clipe de 0 a 10,45 s (`playbackRate` perto de 0,96) e conferir a posição dos balões, porque a câmera se aproxima do rosto.

Feito na v3: fala dos nichos com etiquetas, versão Telegram/Facebook, passo do Beacons na cena 5 (o link da bio continua no Beacons) e cartão da loja simplificado (decisão do dono).

## Diferenças em relação ao roteiro
- 55,7 s em vez de 47 s (só as falas somam cerca de 49 s).
- Fala dos nichos: "Com descontos" em vez de "Tudo com desconto", para não prometer desconto em todos os produtos.
- Música: começa baixinha e recomeça na chegada do mascote (junto com o "puf"), para o fim da música coincidir com o fim do vídeo.
- O mascote aparece dentro da fumaça amarela, em vez de entrar voando.
- Cartão da loja é simplificado, com preço borrado; não usa a marca visual do Mercado Livre. Decisão do dono: manter assim.

## Skill do padrão
Para ajustar este vídeo ou fazer outro igual, use a skill `video-pixel-art` (pasta `04-video-e-imagem/video-pixel-art/`). Ela manda reaproveitar este projeto e gastar o mínimo de crédito do ElevenLabs.

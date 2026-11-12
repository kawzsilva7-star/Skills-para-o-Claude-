# Vídeo fixado "Descontos Brutais": estado em 12/11/2026

Tudo o que é preciso para continuar o vídeo em outra sessão está nesta pasta.
O roteiro original do dono é `roteiro-video-fixado.md`.

## O que está pronto
- `video-pronto/video-fixado-v2.mp4`: versão atual. Vertical 1080 x 1920, 53,6 s, com as 8 cenas, vozes, música, efeitos e legendas.
  (Se só existir `video-fixado-v1.mp4`, a v2 não terminou de exportar: rode a exportação abaixo.)
- Página de produtos (`Descontos_Brutais.Br`, branch `main`): botão "💬 GRUPO DO WHATSAPP" publicado, logo abaixo do Telegram.
  Link usado: `https://chat.whatsapp.com/LOSj2Ykzd0L5ezYTVGN3pa`. A mudança está no gerador (`src/pagina/gerador.py`) e em `docs/index.html`.

## Como o vídeo é montado
- Montagem em Remotion: `src/Video.tsx` (tempos das cenas ficam no objeto `T`, legendas em `LEGENDAS`).
- Materiais em `public/`:
  - `clipB.mp4` (cena 3), `clipC.mp4` (cenas 4 a 6, em repetição), `clipD.mp4` (cena 7): animações de IA em 1080p.
  - `k1.png`: imagem do dono sozinho, usada nas cenas 1 e 2 com zoom lento (não há clipe animado para elas).
  - `shots/site-full.png`: captura real da página de produtos (gerada por `tools/shots.js`).
  - `shots/insta.png`: print real do Instagram enviado pelo dono, com números borrados.
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
Na nuvem, o Remotion não consegue baixar o navegador dele; por isso o `--browser-executable` acima (o caminho pode mudar de versão).

## ElevenLabs
- Projeto (flow) do vídeo: `gfZU8r3BEHK3urChxeCi` ("Vídeo fixado - Descontos Brutais"). Projeto antigo com os personagens: `EY82yvaPPikUkiwPu1H9`.
- Vozes: dono `Xe7E9Z5crYh1h7GiQLRm`; mascote `NQmLEqxcRTkWYIYZSYod`. Modelo `eleven_v4`, idioma `pt` (com `pt-BR` a gravação falha).
- Nós úteis no flow:
  - Clipe A (cenas 1 e 2), **preparado e ainda não gerado**: `SKGbZZuuUFNNXnOithun` (10 s, 1080p, 62.648 créditos; 720p custa 28.007).
  - Clipe B `AhNsI2kEnqxzlXXM91fP`, clipe C `ImMps0kfTfgGGTS1mrFS`, clipe D `YulZfGEUdQvtg58B1ah5`.
  - Imagens de base: dono sozinho `wqXxflqBzt8d2aEEuvGp`; dono + mascote `7nQ3vFikS5ms0wvOISl5`; os dois olhando para cima `YSU8sQRm3JPSJyyhItOx`.
- Gasto até aqui: cerca de 126 mil créditos (119 mil em 19 s de animação 1080p, o resto em vozes, música, efeitos e imagens).
- Para baixar arquivos gerados, o ambiente precisa liberar `elevenlabsusercontent.com` (o ambiente "Skills-para-o-Claude (videos)" já libera, junto com `cdn.beacons.ai` e `http2.mlstatic.com`).

## Decisões do dono
- Qualidade: máxima (1080p). WhatsApp: existe, manter na fala e no vídeo. TikTok `@achadosbiblicais`: está certo.
- Link da bio: **continua no Beacons** (decisão do dono em 12/11). O caminho real é: link da bio -> Beacons -> toque em "VER PRODUTOS" -> página de produtos (GitHub, com o botão do WhatsApp). O Beacons não precisa do WhatsApp.

## Pendências (esperando o "pode fazer" do dono, cerca de 63 mil créditos)
1. Gerar o clipe A e trocar a imagem parada das cenas 1 e 2 (em `Video.tsx`, componente `DonoSozinho`).
2. Regravar a fala 2 do mascote com os nichos, sem citar saúde:
   "Lá tem de tudo: moda, beleza, academia, cozinha, pet e muito mais! Tudo com desconto, em lojas confiáveis, sem dor de cabeça de cair em fraude!"
   e fazer cada nicho aparecer como etiqueta amarela (cerca de 300 créditos).
3. Versão para Telegram e Facebook: fala final "Clica no link aqui embaixo." (cerca de 80 créditos).
4. ~~Trocar o cartão da loja pelo print real do Mercado Livre~~: o dono decidiu (12/11) manter o cartão simplificado (fatiador de legumes, um produto que está na página). Não pedir esse print.
5. **Cena 5 precisa de um passo a mais:** perfil do Instagram -> toque no link da bio -> cartão do Beacons (print `prints-do-dono/beacons-ver-produtos.png`, cortar a barra de cima do celular) -> toque em "VER PRODUTOS" -> página de produtos -> produto -> loja. Hoje o vídeo vai direto do perfil para a página. O print do Instagram que já está no vídeo (mostra o link do Beacons) está certo: não precisa de print novo. Cuidado com o tempo: a cena 5 dura 5,7 s (de 26,9 s a 32,6 s) e agora terá um cartão a mais.

## Diferenças em relação ao roteiro
- 53,6 s em vez de 47 s (só as falas somam 46,5 s).
- O mascote aparece dentro da fumaça amarela, em vez de entrar voando.
- Cartão da loja é simplificado, com preço borrado; não usa a marca visual do Mercado Livre. Decisão do dono: manter assim.

## Skill do padrão
Para ajustar este vídeo ou fazer outro igual, use a skill `video-pixel-art` (pasta `04-video-e-imagem/video-pixel-art/`). Ela manda reaproveitar este projeto e gastar o mínimo de crédito do ElevenLabs.

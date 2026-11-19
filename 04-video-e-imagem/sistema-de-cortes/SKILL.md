---
name: sistema-de-cortes
description: Corta live de streamer (gravação mp4/mkv/mov ou live acontecendo agora) em cortes verticais 1080x1920 com legenda palavra por palavra, título, zoom e crédito, e monta o vídeo longo para o YouTube. Use quando o usuário pedir para cortar uma live, fazer cortes, clipar, usar o sistema de cortes/ClipDrop ou gravar e cortar lives ao vivo.
---

# Sistema de Cortes (em código)

Responda em português simples. O trabalho pesado é feito pelo pacote Python `sistema_cortes/` (ao lado deste arquivo): **não reescreva scripts, rode os comandos**. Você (Claude) só entra onde está escrito **VOCÊ** — o resto é código, que gasta zero token.

Como rodar (de dentro da pasta da live), sendo `SKILL` a pasta desta skill:
- Windows: `"SKILL\cortes.cmd" <comando>` · Mac/Linux: `SKILL/cortes.sh <comando>` (o atalho acha o `.venv` sozinho).
- Mais de um vídeo na pasta: pergunte qual e passe `--video nome.mp4` antes do comando.
- `diagnostico` diz o que falta; se `venv_pronto` for false, rode `preparar` (uma vez só, vale para todas as lives).

## Mandaram um LINK (Twitch, Kick ou YouTube)
Pegue da mensagem: link, onde está a permissão, @ do streamer, quantos cortes e estilo (faltou permissão? pergunte; o resto tem padrão).
`link "URL" --permissao "onde está escrita" --arroba "@streamer" --quantos 5` (+ `--tudo` se pedirem a live inteira; `--inicio 0 --duracao 2h` para outro trecho).
- **Ao vivo agora:** ele grava e analisa até a live acabar (pode levar horas: rode em segundo plano e avise o dono para deixar o PC ligado). No fim, siga o passo 3 do modo ao vivo abaixo. Para usar o layout com câmera, depois do 1º bloco tire um quadro de `blocos/<canal>/` com o ffmpeg, ache a câmera e ponha `"camera": "x,y,w,h"` no `streamers.json` da pasta.
- **Já acabou (VOD):** ele baixa o trecho (padrão: 3 h pulando a meia hora inicial), registra a permissão e roda o `analisar` sozinho. Continue do passo 5 abaixo.

## Live já gravada (fluxo dos PDFs)
1. **Pergunte antes de tudo:** o dono tem permissão do streamer? Quantos cortes (padrão 5)? Qual estilo de legenda e de título (mostre o menu abaixo; sem escolha: `destaque` + `contorno`; "todos" = 1º corte em cada estilo)? Qual o @ do streamer para o crédito?
2. `diagnostico` → se faltar algo, mostre o comando de instalação que ele imprime. Se o `.venv` não estiver pronto, `preparar`.
3. `permissao --origem "onde está escrita"` — sem isso nenhum outro passo roda.
4. `analisar --quantos N` (idioma automático; `--lingua pt|en|es` para forçar; `--gpu` se tiver NVIDIA). Mostra o progresso e o tempo que falta.
5. **VOCÊ:** leia a `fala:` de cada momento na lista e escreva título (até 40 letras, dá vontade de assistir, sem mentir) e descrição de 1 linha:
   `ajustar --titulo 1="..." --descricao 1="..."` (repita por momento). Itens com ⚠ podem ser fala do jogo/cutscene: avise o dono.
6. `lista` → **PARE**. Mostre a lista e espere o OK. Pedidos de troca: `ajustar --tirar N`, `--reserva N` (promove a reserva RN), `--tempo N=01:23:40-01:24:20`. Depois de qualquer ajuste, mostre de novo e espere.
7. Com o OK: `aprovar`.
8. `quadros` → **VOCÊ:** abra as 3 imagens e ache a câmera do streamer (retângulo do rosto, POR DENTRO da moldura). Com câmera: `camera --area x,y,w,h` (se a ação ficar embaixo da câmera, passe `--jogo x,y,w,h` priorizando a ação). Sem câmera ou na dúvida depois de perguntar: `camera --sem-camera`.
9. `estilo --legenda destaque --titulo contorno --credito "@streamer"` e `cortar`. Com `--legenda todos` ele gera o 1º corte nos 5 estilos e **PARA** para o dono escolher.
10. `longo` (vídeo 16:9 de melhores momentos) e `verificar`. **VOCÊ:** abra cada quadro de `verificacao/` e confira se legenda e título aparecem. Diga onde está tudo, os números de LUFS/pico e quanto tempo levou.

Menu de legenda: `destaque` (3 palavras, maiúsculas, falada em amarelo) · `caixa` (destaque em caixa preta) · `karaoke` (4 palavras, amarelo "enche") · `beasty` (1 palavra gigante, cores alternadas, "pop") · `minimal` (4 palavras minúsculas, as outras apagadas).
Menu de título: `contorno` · `faixa` (faixa vermelha) · `caixa-branca`.

## Ficar de olho em até 3 streamers (modo ao vivo, "ligue o modo ao vivo")
Ninguém baixa nada: o PC grava a live em blocos de 20 min e analisa cada bloco novo.
1. Monte `streamers.json` (modelo em `streamers.exemplo.json`): máximo 3, todos com `permissao` preenchida.
2. Uma janela para cada: `ao-vivo gravar --nome X` (precisa do `streamlink`; `--lancamento` confere a cada 2 min), `ao-vivo chat --canal x` (só Twitch) e `ao-vivo analisar` (um para todos; `--gpu` se tiver NVIDIA).
3. Candidatos caem em `pendentes/*.json`. **VOCÊ** ajuda a pessoa a dar a nota (0 a 2 em gancho, virada, entende sozinho, relevância, vontade de rever): `avaliar --pendente arquivo.json --gancho 2 ...`. 9-10 posta, 7-8 fila, 5-6 reserva, <5 descarta; só fala vai para reserva.
4. Nota 7+: `ao-vivo cortar --pendente arquivo.json --titulo "..."` (crédito do streamer entra sozinho).

## Regras que não podem ser quebradas
O código já trava estas (ver `REGRAS.md`): sem permissão não analisa; sem `aprovar` não corta; o original nunca é alterado; título > 40 letras é recusado; legenda nunca 2 ao mesmo tempo nem com duração zero; volume -14 LUFS ±0,5 e pico real ≤ -1 dB. As regras para postar sem perder a conta estão em `references/regras-de-postagem.md`: leia só quando o dono perguntar sobre postar, monetizar ou pedir permissão.

Testar o código: `python -m pytest tests` (o teste de ponta a ponta usa ffmpeg de verdade e uma live sintética).

Instalar tudo no Windows (programas, skills e a pasta `cortes` com o COMO-USAR): `instalar.ps1` na raiz do repositório.

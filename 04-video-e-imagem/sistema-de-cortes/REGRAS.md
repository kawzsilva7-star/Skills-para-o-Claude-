# Regras: que função faz o quê, e onde o Claude entra

O texto das duas skills compradas (BR e ClipDrop) e o `LOGICA-DO-SISTEMA` viraram funções. Cada número mora em `sistema_cortes/config.py`; cada trava mora em `sistema_cortes/regras.py`.

## Regra de uso do repertório (economizar tokens)
O `LEIA-ME.md` do repositório pede: **só use skill quando a tarefa for de decisão, criação de código ou raciocínio**. Aqui isso fica assim:

| Passo | Quem faz | Gasta token? |
|---|---|---|
| Instalar, transcrever, medir volume, achar momentos, cortar, legendar, ajustar volume, vídeo longo, conferir números | **código** (`python -m sistema_cortes ...`) | Não |
| Escrever título e descrição de cada momento | **Claude** (lê a fala e decide) | Sim, pouco |
| Achar a câmera e o recorte do jogo nos quadros | **Claude** (olha 3 imagens) | Sim, 1 vez por live |
| Conferir se legenda e título aparecem | **Claude** (olha 1 quadro por corte) | Sim, pouco |
| Separar fala do streamer x fala do jogo (avisos ⚠) | **Claude + dono** | Só quando há aviso |
| Aprovar a lista e dar a nota de qualidade | **Dono** (Claude ajuda) | — |

Não abra os arquivos `.py` para "entender" antes de rodar: o `SKILL.md` já diz o comando.

## Mapa função → regra
| Módulo | Função principal | Regra (origem) |
|---|---|---|
| `regras.py` | `registrar_permissao`, `exigir_permissao` | Só streamer que libera corte; guarda onde está a permissão (PDFs) |
| `regras.py` | `exigir_aprovacao` | PARE: lista só vira corte depois do OK (PDFs, passo 4) |
| `regras.py` | `assinar_original`, `conferir_original`, `garantir_saida_segura` | Nunca alterar o original; saída só em `cortes/` (skill `editar-video-ffmpeg`) |
| `regras.py` | `varrer_segredos` | Nada de chave, senha, e-mail ou telefone no repositório (README) |
| `ambiente.py` | `diagnostico`, `achar_python`, `preparar_venv` | Python 3.9+, ffmpeg, winget/brew, caminho completo em vez de reiniciar, `.venv` (PDFs, passo 1) |
| `midia.py` | `extrair_wav`, `ler_wav_em_pedacos` | WAV mono 16 kHz em pedaços de 10 min como array numpy (PDFs, passo 2) |
| `transcricao.py` | `transcrever_live`, `detectar_lingua`, `retranscrever_trecho` | Whisper small/CPU/int8, beam 1 na live e beam 5 no trecho; idioma detectado no meio da live (ClipDrop); `--gpu` (LOGICA) |
| `volume.py` | `medir_volume` | ebur128 com `framelog=info`, volume por segundo, cache (PDFs) |
| `momentos.py` | `nota_grito` | +6 dB sobre a mediana dos segundos COM fala em 2 min; sem voz vale menos (PDFs) |
| `momentos.py` | `achar_reacoes`, `nota_reacao` | Palavras de reação pt/en/es, risada, palavra repetida, exclamação, fala acelerada (PDFs) |
| `momentos.py` | `nota_chat` | Pico do chat com 10 s de atraso compensado (LOGICA) |
| `momentos.py` | `escolher_picos`, `achar_momentos` | N melhores sem sobrepor, 45 s entre eles, + até 3 reservas; não inventa (PDFs, LOGICA) |
| `momentos.py` | `conferir_reacao_fina` | Reação que some no beam 5 = provável fala do jogo (PDFs) |
| `limites.py` | `definir_corte` | 20-60 s; começa 5-20 s antes no começo de frase (3 s se mudou de assunto); fim na frase do pico; nunca em palavra de ligação nem cortando a próxima (PDFs) |
| `legenda.py` | `gerar_ass`, `eventos_legenda`, `normalizar_eventos` | 5 estilos, 3 títulos, cores &HAABBGGRR, 1 linha ≤ 900 px, sem duração zero, sem 2 ao mesmo tempo (PDFs); palavrão censurado e crédito na tela (LOGICA) |
| `layout.py` | `filtro_com_camera`, `filtro_sem_camera`, `jogo_automatico` | Câmera 1080x860 + jogo 1080x1060 sem esticar; sem câmera: centro y=860 com fundo desfocado; zoom por overlay, nunca zoompan (PDFs) |
| `audio.py` | `medir_trecho`, `filtro_segunda_passada`, `garantir_volume` | loudnorm 2 passadas, depois volume+alimiter até -14 ±0,5 LU e pico real ≤ -1 dB (PDFs) |
| `render.py` | `renderizar_corte` | H.264 + AAC estéreo 48 kHz + faststart; ffmpeg rodando de dentro da pasta com caminho relativo e `fontsdir=fontes` (PDFs) |
| `longo.py` | `montar_video_longo` | Ordem da live, 1920x1080, fade 0,5 s, -14 LUFS (PDFs) |
| `verificacao.py` | `verificar` | Duração, 1080x1920, som, volume e quadro com legenda (PDFs, passo 7) |
| `avaliacao.py` | `decidir` | Nota 0-10 e destino; só fala vai para reserva (LOGICA) |
| `ao_vivo.py` | `gravar`, `ler_chat_twitch`, `loop_analisador`, `limpar` | Blocos de 20 min, máx. 3 streamers, 30 min/2 min offline, até 4 picos por bloco, corte 12-60 s, limpeza de disco (LOGICA) |

## Diferenças entre as fontes (e o que o código escolheu)
| Ponto | PDF BR | ClipDrop (EN) | LOGICA | No código |
|---|---|---|---|---|
| Idioma | só pt | detecta | en/pt | detecta (pt/en/es) ou `--lingua` |
| Layout com câmera | 860 + 1060 | não tem | 840 + 1080 | 860 + 1060 (`config.py`) |
| Corte mínimo / começo | 20 s / 5 s antes | igual | 12 s / 3 s antes | live gravada = PDF; ao vivo = LOGICA (`REGRAS_AO_VIVO`) |
| Whisper | CPU | CPU | GPU | CPU padrão, `--gpu` opcional |
| Crédito | só regra de postagem | igual | na tela | `estilo --credito` (na tela e no `titulos.txt`) |

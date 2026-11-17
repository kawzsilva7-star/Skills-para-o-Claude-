---
name: cortes-preparar-ambiente
description: Prepara o computador (Windows ou Mac) para cortar lives - instala e acha ffmpeg e Python 3.9+, cria o .venv com faster-whisper e numpy e deixa o Whisper no processador. Use na 1ª etapa do sistema-de-cortes, ou quando um script de vídeo/transcrição falhar com "programa não encontrado", "Python was not found" ou erro do pip.
---

# Preparar o ambiente para os cortes

Explique cada passo em português simples. O Claude pede permissão antes de cada comando: o dono só lê e aceita.

## 1. ffmpeg e ffprobe
- Teste `ffmpeg -version`. Se faltar:
  - Windows: `winget install Gyan.FFmpeg`
  - Mac: `brew install ffmpeg`. Sem Homebrew, passe ao dono o comando oficial de instalação do Homebrew para colar no Terminal (ele pede a senha do Mac).
- Instalou e "não encontrado"? **Não peça para reiniciar**: use o caminho completo. No Windows, procure em `%LOCALAPPDATA%\Microsoft\WinGet\Links\` e em `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin\`. O `cortes.py` já procura nesses lugares sozinho e também aceita as variáveis `CORTES_FFMPEG` e `CORTES_FFPROBE`.

## 2. Python 3.9 ou mais novo
- Procure nesta ordem: `py -3.12`, `py`, `python3`, `python`, e nas pastas `C:\Python3*` e `%LOCALAPPDATA%\Programs\Python\Python3*`.
- No Windows, o `python` pode ser um atalho da Microsoft Store que só diz "Python was not found": ignore e use o `py` ou o caminho completo.
- Se faltar: Windows `winget install Python.Python.3.12`; Mac `brew install python@3.12`.

## 3. Ambiente virtual
```
py -3.12 -m venv .venv          (Mac: python3.12 -m venv .venv)
.venv\Scripts\python -m pip install faster-whisper numpy      (Mac: .venv/bin/python -m pip ...)
```
- Se o pip falhar por causa da versão do Python (sem pacote pronto para ela), apague o `.venv` e recrie com o 3.12.
- Sempre rode os scripts com o Python do `.venv`.
- No Windows, rode com `PYTHONIOENCODING=utf-8` para acento e "→" não quebrarem. O `cortes.py` já faz isso sozinho, mas outros scripts precisam.

## 4. Whisper
- Sempre no processador: modelo `small`, `device="cpu"`, `compute_type="int8"`. Não tente usar a placa de vídeo.
- Na 1ª vez ele baixa o modelo (uns 500 MB contando tudo). Se o download falhar com erro de rede ou proxy, avise o dono: o modelo vem do huggingface.co.

## 5. Teste rápido
`.venv/.../python -c "import faster_whisper, numpy; print('ok')"` e `ffmpeg -version`. Só siga para a próxima etapa (`cortes-transcrever-live`) com os dois funcionando.

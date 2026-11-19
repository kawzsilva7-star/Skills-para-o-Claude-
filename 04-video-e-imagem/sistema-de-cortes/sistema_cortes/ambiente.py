"""Passo 1 (PREPARAR): acha ffmpeg e Python 3.9+, cria o .venv e instala faster-whisper e numpy.

Nunca pede para reiniciar: se o programa acabou de ser instalado e não está no PATH, usa o caminho completo.
Se precisar de senha ou Homebrew, devolve o comando exato para o dono colar no Terminal.
"""
from __future__ import annotations

import glob
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .midia import rodar

PACOTES = ["faster-whisper", "numpy"]


def _versao_python(cmd: List[str]) -> Optional[Tuple[int, int]]:
    r = rodar([*cmd, "-c", "import sys;print(sys.version_info[0], sys.version_info[1])"])
    if r.returncode != 0 or "was not found" in (r.stdout + r.stderr):  # atalho da Microsoft Store
        return None
    try:
        a, b = r.stdout.split()
        return int(a), int(b)
    except ValueError:
        return None


def candidatos_python() -> List[List[str]]:
    cands = [["py", "-3.12"], ["py"], ["python3"], ["python"]]
    if platform.system() == "Windows":
        locais = glob.glob(r"C:\Python3*\python.exe") + glob.glob(
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python3*\python.exe")
        )
        cands += [[p] for p in sorted(locais, reverse=True)]
    cands.append([sys.executable])
    return cands


def achar_python() -> Optional[List[str]]:
    for cmd in candidatos_python():
        if shutil.which(cmd[0]) or Path(cmd[0]).exists():
            v = _versao_python(cmd)
            if v and v >= (3, 9):
                return cmd
    return None


def achar_ffmpeg() -> Optional[str]:
    achado = shutil.which("ffmpeg")
    if achado:
        return achado
    if platform.system() == "Windows":  # winget instala aqui e o PATH só atualiza depois
        for p in glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\**\bin\ffmpeg.exe"), recursive=True):
            return p
    for p in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        if Path(p).exists():
            return p
    return None


def comandos_de_instalacao(sistema: Optional[str] = None) -> Dict[str, str]:
    sistema = sistema or platform.system()
    if sistema == "Windows":
        return {
            "ffmpeg": "winget install --id Gyan.FFmpeg -e",
            "python": "winget install --id Python.Python.3.12 -e",
        }
    if sistema == "Darwin":
        return {"ffmpeg": "brew install ffmpeg", "python": "brew install python@3.12"}
    return {"ffmpeg": "sudo apt-get install -y ffmpeg", "python": "sudo apt-get install -y python3 python3-venv"}


def diagnostico() -> Dict[str, object]:
    py = achar_python()
    ff = achar_ffmpeg()
    falta = comandos_de_instalacao()
    return {
        "sistema": platform.system(),
        "python": " ".join(py) if py else None,
        "ffmpeg": ff,
        "instalar": {k: v for k, v in falta.items() if (k == "python" and not py) or (k == "ffmpeg" and not ff)},
    }


def python_do_venv(pasta: Path) -> Path:
    return pasta / ".venv" / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")


def preparar_venv(pasta: Path, python: List[str]) -> Path:
    """Cria .venv e instala os pacotes. Se o pip falhar pela versão do Python, tenta com o 3.12."""
    venv_py = python_do_venv(pasta)
    if not venv_py.exists():
        r = rodar([*python, "-m", "venv", str(pasta / ".venv")])
        if r.returncode != 0:
            raise RuntimeError(f"Não consegui criar o .venv: {r.stderr[-400:]}")
    r = rodar([str(venv_py), "-m", "pip", "install", "-q", *PACOTES])
    if r.returncode != 0:
        if python[:2] != ["py", "-3.12"] and shutil.which("py"):
            shutil.rmtree(pasta / ".venv", ignore_errors=True)
            return preparar_venv(pasta, ["py", "-3.12"])
        raise RuntimeError(f"pip falhou: {r.stderr[-400:]}")
    return venv_py

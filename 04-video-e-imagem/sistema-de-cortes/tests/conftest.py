import shutil
import sys
from pathlib import Path
from typing import List, Optional

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sistema_cortes.modelos import Palavra  # noqa: E402

FILLER = "a gente vai entrar ali agora no carro pega a rua olha o mapa depois volta".split()


def roteiro(duracao: float, eventos: dict) -> List[Palavra]:
    """Fala sintética: frases de 6 palavras (0,4 s cada) com pausa de 0,8 s; `eventos` = {segundo: 'texto'}."""
    palavras: List[Palavra] = []
    t, k = 1.0, 0
    especiais = sorted(eventos.items())
    while t < duracao - 3:
        for _ in range(6):
            if especiais and t >= especiais[0][0]:
                for w in especiais.pop(0)[1].split():
                    palavras.append(Palavra(round(t, 2), round(t + 0.35, 2), w))
                    t += 0.4
            palavras.append(Palavra(round(t, 2), round(t + 0.35, 2), FILLER[k % len(FILLER)]))
            k += 1
            t += 0.4
        palavras[-1].texto += "."
        t += 0.8
    return palavras


class TranscritorFalso:
    def __init__(self, palavras: List[Palavra], lingua: str = "pt"):
        self.palavras = palavras
        self.lingua = lingua

    def transcrever(self, audio, lingua: Optional[str], beam: int, offset: float = 0.0):
        fim = offset + len(audio) / 16000
        return [
            Palavra(p.inicio - offset, p.fim - offset, p.texto, p.prob)
            for p in self.palavras
            if offset <= p.inicio and p.fim <= fim
        ]

    def detectar_lingua(self, audio):
        return self.lingua, 0.99


precisa_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg não instalado")

"""Transcrição com o faster-whisper, palavra por palavra.

O transcritor é trocável (interface `Transcritor`): nos testes usamos um falso,
na vida real o `TranscritorWhisper`. Assim o resto do sistema não depende do Whisper.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable, List, Optional, Protocol, Tuple

import numpy as np

from .config import MODELO_WHISPER, PEDACO_TRANSCRICAO_S
from .midia import ler_wav_em_pedacos, ler_wav_trecho
from .modelos import Palavra

TAXA = 16000


class Transcritor(Protocol):
    def transcrever(self, audio: np.ndarray, lingua: Optional[str], beam: int, offset: float = 0.0) -> List[Palavra]:
        """Tempos relativos ao começo de `audio`. `offset` = onde o trecho começa na live (só informativo)."""

    def detectar_lingua(self, audio: np.ndarray) -> Tuple[str, float]:
        """(código, probabilidade)."""


class TranscritorWhisper:
    """faster-whisper. Padrão dos PDFs: modelo small, CPU, int8. `gpu=True` para placa NVIDIA (modo ao vivo)."""

    def __init__(self, modelo: str = MODELO_WHISPER, gpu: bool = False):
        from faster_whisper import WhisperModel  # importa só quando for usar

        if gpu:
            self._m = WhisperModel(modelo, device="cuda", compute_type="float16")
        else:
            self._m = WhisperModel(modelo, device="cpu", compute_type="int8")

    def transcrever(self, audio: np.ndarray, lingua: Optional[str], beam: int, offset: float = 0.0) -> List[Palavra]:
        segmentos, _ = self._m.transcribe(
            audio,
            language=lingua,
            word_timestamps=True,
            vad_filter=True,
            condition_on_previous_text=False,
            beam_size=beam,
        )
        return [
            Palavra(float(w.start), float(w.end), w.word.strip(), float(w.probability))
            for s in segmentos
            for w in (s.words or [])
            if w.word.strip()
        ]

    def detectar_lingua(self, audio: np.ndarray) -> Tuple[str, float]:
        lingua, prob, _ = self._m.detect_language(audio)
        return lingua, float(prob)


# ------------------------------------------------------------------ cache em JSON
def salvar_palavras(palavras: List[Palavra], arquivo: Path, extra: Optional[dict] = None) -> None:
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    dados = {"palavras": [p.para_dict() for p in palavras], **(extra or {})}
    arquivo.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")


def carregar_palavras(arquivo: Path) -> Tuple[List[Palavra], dict]:
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    palavras = [Palavra(**p) for p in dados.pop("palavras")]
    return palavras, dados


# ------------------------------------------------------------------ passos
def detectar_lingua(wav: Path, duracao: float, transcritor: Transcritor) -> Tuple[str, float]:
    """Testa 3 trechos de 30 s do meio da live e fica com o mais confiante (o que tem fala de verdade)."""
    melhor = ("pt", 0.0)
    for frac in (0.5, 0.35, 0.65):
        ini = max(0.0, duracao * frac)
        _, audio = ler_wav_trecho(wav, ini, ini + 30)
        if audio.size < TAXA:
            continue
        lingua, prob = transcritor.detectar_lingua(audio)
        if prob > melhor[1]:
            melhor = (lingua, prob)
    return melhor


def transcrever_live(
    wav: Path,
    cache: Path,
    transcritor: Transcritor,
    lingua: Optional[str],
    duracao: float,
    avisar: Callable[[str], None] = print,
    pedaco_s: int = PEDACO_TRANSCRICAO_S,
) -> List[Palavra]:
    """Primeira passada (rápida, beam 1) na live inteira, de 10 em 10 minutos, com progresso e tempo restante."""
    if cache.exists():
        avisar("Transcrição já existe, não vou refazer.")
        return carregar_palavras(cache)[0]
    total = max(1, int(np.ceil(duracao / pedaco_s)))
    palavras: List[Palavra] = []
    comeco = time.monotonic()
    for i, (offset, audio) in enumerate(ler_wav_em_pedacos(wav, pedaco_s), 1):
        for p in transcritor.transcrever(audio, lingua, beam=1, offset=offset):
            palavras.append(Palavra(p.inicio + offset, p.fim + offset, p.texto, p.prob))
        gasto = time.monotonic() - comeco
        falta = gasto / i * (total - i)
        avisar(f"Pedaço {i}/{total} transcrito. Falta uns {falta / 60:.0f} min.")
    salvar_palavras(palavras, cache, {"lingua": lingua, "beam": 1})
    return palavras


def retranscrever_trecho(
    wav: Path, inicio: float, fim: float, transcritor: Transcritor, lingua: Optional[str], beam: int = 5
) -> List[Palavra]:
    """Segunda passada, só em volta do momento, com beam 5: frases e pontuação melhores para começo, fim e legenda."""
    real, audio = ler_wav_trecho(wav, inicio, fim)
    return [
        Palavra(p.inicio + real, p.fim + real, p.texto, p.prob)
        for p in transcritor.transcrever(audio, lingua, beam=beam, offset=real)
    ]

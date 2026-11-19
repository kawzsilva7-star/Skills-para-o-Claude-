"""Volume de cada segundo (filtro ebur128 do ffmpeg)."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from .midia import rodar_ffmpeg

SILENCIO_DB = -70.0
_LINHA = re.compile(r"t:\s*([\d.]+)\s+TARGET:.*?M:\s*(-?inf|-?[\d.]+)")


def interpretar_ebur128(log: str) -> np.ndarray:
    """Transforma o log do ebur128 (framelog=info) no volume máximo de cada segundo, em LUFS.

    O ffmpeg imprime uma linha a cada 0,1 s; ficamos com o maior "M" (momentâneo) de cada segundo.
    """
    tempos, valores = [], []
    for m in _LINHA.finditer(log):
        tempos.append(float(m.group(1)))
        v = m.group(2)
        valores.append(SILENCIO_DB if "inf" in v else max(SILENCIO_DB, float(v)))
    if not tempos:
        return np.zeros(0, dtype=np.float32)
    seg = np.floor(np.asarray(tempos) - 1e-6).astype(int).clip(min=0)
    saida = np.full(seg.max() + 1, SILENCIO_DB, dtype=np.float32)
    np.maximum.at(saida, seg, np.asarray(valores, dtype=np.float32))
    return saida


def medir_volume(audio: Path, cache: Path) -> np.ndarray:
    """Mede (ou lê do cache .npy) o volume por segundo. Use o WAV: é muito mais rápido que o vídeo."""
    if cache.exists():
        return np.load(cache)
    # framelog=info é obrigatório: sem ele o ebur128 não imprime as linhas por tempo.
    log = rodar_ffmpeg(["-v", "info", "-i", audio, "-vn", "-af", "ebur128=framelog=info", "-f", "null", "-"])
    vol = interpretar_ebur128(log)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache, vol)
    return vol

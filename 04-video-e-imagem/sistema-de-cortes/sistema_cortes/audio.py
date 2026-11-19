"""Volume final: -14 LUFS e pico real (true peak) até -1 dB.

loudnorm em duas passadas e, como em corte curto ele costuma parar em -16 a -18,
mede de novo e corrige com volume + alimiter até ficar dentro de 0,5 LU.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple

from .config import REGRAS, Regras
from .midia import rodar_ffmpeg


def interpretar_loudnorm(log: str) -> Dict[str, float]:
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", log, re.S)
    if not m:
        raise ValueError("loudnorm não devolveu o JSON de medição")
    return {k: float(v) for k, v in json.loads(m.group(0)).items() if k != "normalization_type"}


def interpretar_resumo_ebur128(log: str) -> Tuple[float, float]:
    """(LUFS integrado, true peak em dBFS) do resumo final do ebur128=peak=true."""
    resumo = log[log.rfind("Summary:"):] if "Summary:" in log else log
    i = re.search(r"I:\s*(-?[\d.]+|-inf)\s*LUFS", resumo)
    p = re.search(r"True peak:\s*\n?\s*Peak:\s*(-?[\d.]+|-inf)\s*dBFS", resumo)
    def num(x):
        return float("-inf") if x is None or "inf" in x.group(1) else float(x.group(1))
    return num(i), num(p)


def medir_trecho(video: Path, inicio: float, duracao: float, r: Regras = REGRAS) -> Dict[str, float]:
    """1ª passada do loudnorm, só no trecho do corte."""
    log = rodar_ffmpeg([
        "-v", "info", "-ss", f"{inicio:.3f}", "-t", f"{duracao:.3f}", "-i", video, "-vn",
        "-af", f"loudnorm=I={r.lufs_alvo}:TP={r.pico_verdadeiro_max_db}:LRA=11:print_format=json",
        "-f", "null", "-",
    ])
    return interpretar_loudnorm(log)


def filtro_segunda_passada(medido: Dict[str, float], r: Regras = REGRAS) -> str:
    return (
        f"loudnorm=I={r.lufs_alvo}:TP={r.pico_verdadeiro_max_db}:LRA=11:"
        f"measured_I={medido['input_i']}:measured_TP={medido['input_tp']}:"
        f"measured_LRA={medido['input_lra']}:measured_thresh={medido['input_thresh']}:"
        f"offset={medido['target_offset']}:linear=true:print_format=summary"
    )


def medir_arquivo(arquivo: Path) -> Tuple[float, float]:
    log = rodar_ffmpeg(["-v", "info", "-i", arquivo, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    return interpretar_resumo_ebur128(log)


def precisa_corrigir(lufs: float, pico: float, r: Regras = REGRAS) -> Optional[float]:
    """Ganho em dB a aplicar, ou None se já está bom."""
    if lufs == float("-inf"):
        return None  # sem som: não há o que corrigir (a conferência final acusa)
    if abs(lufs - r.lufs_alvo) <= r.lufs_tolerancia and pico <= r.pico_verdadeiro_max_db:
        return None
    return round(r.lufs_alvo - lufs, 2)


def garantir_volume(arquivo: Path, r: Regras = REGRAS) -> Tuple[float, float]:
    """Mede e corrige (só o áudio; o vídeo é copiado) até -14 ±0,5 LU e pico real ≤ -1 dB."""
    lufs, pico = medir_arquivo(arquivo)
    for _ in range(r.correcoes_max):
        ganho = precisa_corrigir(lufs, pico, r)
        if ganho is None:
            break
        tmp = arquivo.with_name(arquivo.stem + ".ajuste" + arquivo.suffix)
        rodar_ffmpeg([
            "-i", arquivo, "-map", "0", "-c:v", "copy",
            "-af", f"volume={ganho:+.2f}dB,alimiter=limit={r.limitador}:level=0",
            "-c:a", "aac", "-b:a", "192k", "-ar", str(r.audio_hz), "-ac", "2",
            "-movflags", "+faststart", tmp,
        ])
        shutil.move(str(tmp), str(arquivo))
        lufs, pico = medir_arquivo(arquivo)
    return lufs, pico

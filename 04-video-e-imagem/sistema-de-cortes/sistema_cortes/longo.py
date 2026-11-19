"""Vídeo longo para o YouTube: momentos aprovados em ordem da live, 1920x1080, fade de 0,5 s, -14 LUFS.

Lembrete dos PDFs: compilação colada não é monetizada. Use este arquivo como base e
grave a sua narração entre os momentos (história ou ranking).
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence, Tuple

from .audio import garantir_volume
from .config import ALTURA_LONGO, LARGURA_LONGO, REGRAS, Regras
from .midia import rodar_ffmpeg
from .modelos import Momento


def offsets_xfade(duracoes: Sequence[float], fade: float) -> List[float]:
    """Onde cada transição começa: soma das durações anteriores menos os fades já usados."""
    offsets, acumulado = [], 0.0
    for k in range(1, len(duracoes)):
        acumulado += duracoes[k - 1]
        offsets.append(round(acumulado - k * fade, 3))
    return offsets


def grafo_longo(momentos: Sequence[Momento], fade: float, fps: int = 30) -> Tuple[str, str, str, float]:
    """(filter_complex, rótulo do vídeo, rótulo do áudio, duração final)."""
    ms = sorted(momentos, key=lambda m: m.inicio)
    n = len(ms)
    if n == 0:
        raise ValueError("nenhum momento aprovado")
    partes = [f"[0:v]split={n}" + "".join(f"[sv{i}]" for i in range(n)) if n > 1 else "[0:v]null[sv0]",
              f"[0:a]asplit={n}" + "".join(f"[sa{i}]" for i in range(n)) if n > 1 else "[0:a]anull[sa0]"]
    for i, m in enumerate(ms):
        partes.append(
            f"[sv{i}]trim=start={m.inicio:.3f}:end={m.fim:.3f},setpts=PTS-STARTPTS,"
            f"scale={LARGURA_LONGO}:{ALTURA_LONGO}:force_original_aspect_ratio=decrease,"
            f"pad={LARGURA_LONGO}:{ALTURA_LONGO}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},format=yuv420p[v{i}]"
        )
        partes.append(f"[sa{i}]atrim=start={m.inicio:.3f}:end={m.fim:.3f},asetpts=PTS-STARTPTS,aresample=48000[a{i}]")
    duracoes = [m.duracao for m in ms]
    v, a = "v0", "a0"
    for k, off in enumerate(offsets_xfade(duracoes, fade), 1):
        partes.append(f"[{v}][v{k}]xfade=transition=fade:duration={fade}:offset={off}[xv{k}]")
        partes.append(f"[{a}][a{k}]acrossfade=d={fade}[xa{k}]")
        v, a = f"xv{k}", f"xa{k}"
    total = sum(duracoes) - fade * (n - 1)
    return ";".join(partes), v, a, total


def montar_video_longo(video: Path, momentos: Sequence[Momento], saida: Path, r: Regras = REGRAS) -> Tuple[Path, float, float]:
    grafo, v, a, _ = grafo_longo(momentos, r.fade_longo_s)
    # o loudnorm entra no próprio grafo (ffmpeg não aceita -af em saída de filter_complex)
    grafo += f";[{a}]loudnorm=I={r.lufs_alvo}:TP={r.pico_verdadeiro_max_db}:LRA=11,aresample={r.audio_hz}[aout]"
    rodar_ffmpeg([
        "-i", video, "-filter_complex", grafo, "-map", f"[{v}]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", r.preset, "-crf", str(r.crf), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", str(r.audio_hz), "-ac", "2", "-movflags", "+faststart", saida,
    ])
    lufs, pico = garantir_volume(saida, r)
    return saida, lufs, pico

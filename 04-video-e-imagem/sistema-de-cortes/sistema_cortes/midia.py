"""Tudo que conversa com o ffmpeg/ffprobe: rodar comandos, ler dados do vídeo, extrair áudio e quadros."""
from __future__ import annotations

import json
import os
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, List, Optional, Sequence, Tuple

if TYPE_CHECKING:  # só para as dicas de tipo
    import numpy as np

# numpy NÃO é importado aqui em cima: `diagnostico` e `preparar` rodam antes de o numpy existir.


class ErroFFmpeg(RuntimeError):
    pass


def rodar(cmd: Sequence[str], cwd: Optional[Path] = None, capturar: bool = True) -> subprocess.CompletedProcess:
    """Roda um programa sem shell. No Windows força UTF-8 (senão acento e '→' quebram)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run(
        list(map(str, cmd)),
        cwd=str(cwd) if cwd else None,
        env=env,
        stdout=subprocess.PIPE if capturar else None,
        stderr=subprocess.PIPE if capturar else None,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return r


def rodar_ffmpeg(args: Sequence[str], cwd: Optional[Path] = None) -> str:
    """ffmpeg com saída limpa. Devolve o stderr; levanta ErroFFmpeg com o fim do log se falhar."""
    r = rodar(["ffmpeg", "-hide_banner", "-nostats", "-y", *args], cwd=cwd)
    if r.returncode != 0:
        fim = "\n".join((r.stderr or "").strip().splitlines()[-12:])
        raise ErroFFmpeg(f"ffmpeg falhou (código {r.returncode}):\n{fim}")
    return r.stderr or ""


@dataclass(frozen=True)
class InfoMidia:
    duracao: float
    largura: int
    altura: int
    fps: float
    tem_audio: bool
    tem_video: bool = True


def _fps(txt: str) -> float:
    try:
        a, _, b = txt.partition("/")
        return float(a) / float(b or 1)
    except (ValueError, ZeroDivisionError):
        return 0.0


def sondar(arquivo: Path) -> InfoMidia:
    r = rodar(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", arquivo]
    )
    if r.returncode != 0:
        raise ErroFFmpeg(f"ffprobe não leu {arquivo.name}: {r.stderr.strip()[-300:]}")
    dados = json.loads(r.stdout)
    video = next((s for s in dados.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = any(s.get("codec_type") == "audio" for s in dados.get("streams", []))
    duracao = float(dados.get("format", {}).get("duration") or (video or {}).get("duration") or 0)
    return InfoMidia(
        duracao=duracao,
        largura=int((video or {}).get("width", 0)),
        altura=int((video or {}).get("height", 0)),
        fps=_fps((video or {}).get("avg_frame_rate", "0/1")),
        tem_audio=audio,
        tem_video=video is not None,
    )


def extrair_wav(video: Path, wav: Path) -> Path:
    """WAV mono 16 kHz (o formato que o Whisper e a medição de volume usam)."""
    if wav.exists():
        return wav
    wav.parent.mkdir(parents=True, exist_ok=True)
    rodar_ffmpeg(["-i", video, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav])
    return wav


def _para_float(bruto: bytes) -> "np.ndarray":
    import numpy as np

    return np.frombuffer(bruto, dtype="<i2").astype(np.float32) / 32768.0


def ler_wav_em_pedacos(wav: Path, segundos: int = 600) -> Iterator[Tuple[float, np.ndarray]]:
    """Gera (começo_em_segundos, amostras) de 10 em 10 minutos, como array numpy."""
    with wave.open(str(wav), "rb") as w:
        taxa = w.getframerate()
        por_pedaco = segundos * taxa
        pos = 0
        while True:
            bruto = w.readframes(por_pedaco)
            if not bruto:
                break
            yield pos / taxa, _para_float(bruto)
            pos += por_pedaco


def ler_wav_trecho(wav: Path, inicio: float, fim: float) -> Tuple[float, np.ndarray]:
    """Lê só [inicio, fim] do WAV. Devolve (começo_real, amostras)."""
    with wave.open(str(wav), "rb") as w:
        taxa = w.getframerate()
        total = w.getnframes()
        a = max(0, int(inicio * taxa))
        b = min(total, int(fim * taxa))
        w.setpos(a)
        return a / taxa, _para_float(w.readframes(max(0, b - a)))


def extrair_quadro(video: Path, tempo: float, destino: Path, cwd: Optional[Path] = None) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    rodar_ffmpeg(["-ss", f"{tempo:.3f}", "-i", video, "-frames:v", "1", "-q:v", "2", destino], cwd=cwd)
    return destino


def quadros_para_achar_camera(video: Path, duracao: float, pasta: Path) -> List[Path]:
    """3 quadros de pontos diferentes da live, para o Claude (ou o dono) olhar onde está a câmera."""
    pontos = [0.2, 0.5, 0.8]
    return [
        extrair_quadro(video, duracao * p, pasta / f"quadro{i + 1}.png")
        for i, p in enumerate(pontos)
    ]

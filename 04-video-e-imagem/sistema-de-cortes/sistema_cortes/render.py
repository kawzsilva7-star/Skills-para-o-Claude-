"""Gera cada corte: .ass + filtro + loudnorm 2 passadas + H.264/AAC 48 kHz + faststart."""
from __future__ import annotations

import platform
import re
import shutil
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from .audio import filtro_segunda_passada, garantir_volume, medir_trecho
from .config import REGRAS, Regras
from .layout import Retangulo, filtro_com_camera, filtro_sem_camera, janela_de_zoom
from .legenda import gerar_ass, palavras_relativas
from .midia import InfoMidia, rodar_ffmpeg
from .modelos import Momento, Palavra

# Fontes em negrito, na ordem de preferência. (caminho, nome da família para o .ass)
FONTES_NEGRITO: List[Tuple[str, str]] = [
    ("C:/Windows/Fonts/arialbd.ttf", "Arial"),
    ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "Arial"),
    ("/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf", "Arial"),
    ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "Liberation Sans"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVu Sans"),
]


def slug(texto: str, limite: int = 50) -> str:
    """'Ele NÃO sabia!' -> 'ele-nao-sabia' (nome de arquivo sem acento)."""
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:limite].rstrip("-") or "corte"


def preparar_fonte(pasta_trabalho: Path) -> str:
    """Copia uma fonte em negrito para `fontes/` e devolve o nome da família para o .ass."""
    destino = pasta_trabalho / "fontes"
    destino.mkdir(parents=True, exist_ok=True)
    for caminho, familia in FONTES_NEGRITO:
        p = Path(caminho)
        if p.exists():
            alvo = destino / p.name
            if not alvo.exists():
                shutil.copy2(p, alvo)
            return familia
    raise FileNotFoundError(
        f"Não achei fonte em negrito ({platform.system()}). Copie uma .ttf em negrito para {destino}."
    )


@dataclass
class OpcoesCorte:
    estilo_legenda: str = "destaque"
    estilo_titulo: str = "contorno"
    camera: Optional[Retangulo] = None
    jogo: Optional[Retangulo] = None
    credito: Optional[str] = None


def nome_do_corte(n: int, titulo: str, sufixo: str = "") -> str:
    meio = f"-{sufixo}" if sufixo else ""
    return f"corte{n}{meio}-{slug(titulo)}.mp4"


def renderizar_corte(
    video: Path,
    info: InfoMidia,
    momento: Momento,
    palavras: Sequence[Palavra],
    pasta_trabalho: Path,
    nome_arquivo: str,
    opcoes: OpcoesCorte,
    r: Regras = REGRAS,
) -> Tuple[Path, float, float]:
    """Gera o corte e devolve (arquivo, LUFS final, true peak final).

    Roda o ffmpeg DE DENTRO da pasta de trabalho com caminhos relativos (o 'C:' quebra o filtro subtitles).
    """
    pasta_trabalho.mkdir(parents=True, exist_ok=True)
    fonte = preparar_fonte(pasta_trabalho)
    dur = momento.duracao
    rel = palavras_relativas(palavras, momento.inicio, momento.fim)
    texto_ass, _ = gerar_ass(
        rel, dur, momento.titulo, opcoes.estilo_legenda, opcoes.estilo_titulo,
        com_camera=opcoes.camera is not None, credito=opcoes.credito, fonte=fonte, r=r,
    )
    nome_ass = Path(nome_arquivo).with_suffix(".ass").name
    (pasta_trabalho / nome_ass).write_text(texto_ass, encoding="utf-8")

    zoom = janela_de_zoom(momento.zoom_em - momento.inicio, dur, r)
    if opcoes.camera is not None:
        jogo = opcoes.jogo
        if jogo is None:
            from .layout import jogo_automatico
            jogo = jogo_automatico(info.largura, info.altura, opcoes.camera)
        filtro = filtro_com_camera(opcoes.camera, jogo, nome_ass, "fontes", zoom, r)
    else:
        filtro = filtro_sem_camera(info.largura, info.altura, nome_ass, "fontes", zoom, r)

    medido = medir_trecho(video, momento.inicio, dur, r)
    rodar_ffmpeg([
        "-ss", f"{momento.inicio:.3f}", "-t", f"{dur:.3f}", "-i", str(video.resolve()),
        "-filter_complex", filtro, "-map", "[vout]", "-map", "0:a:0",
        "-af", filtro_segunda_passada(medido, r) + f",aresample={r.audio_hz}",
        "-c:v", "libx264", "-preset", r.preset, "-crf", str(r.crf), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", str(r.audio_hz), "-ac", "2",
        "-movflags", "+faststart", nome_arquivo,
    ], cwd=pasta_trabalho)
    saida = pasta_trabalho / nome_arquivo
    lufs, pico = garantir_volume(saida, r)
    return saida, lufs, pico

"""Montagem do vídeo vertical 1080x1920 (filter_complex do ffmpeg).

Dois layouts:
- COM câmera: câmera em cima (1080x860) + jogo embaixo (1080x1060), sem barra preta.
- SEM câmera: a live inteira na largura, centro em y≈860, com o mesmo vídeo desfocado atrás.
Zoom de impacto: cópia ampliada sobreposta só no trecho do pico (overlay com enable). Nunca zoompan (treme).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .config import (
    ALTURA, CAMERA_ALTURA, CENTRO_Y_SEM_CAMERA, JOGO_ALTURA, LARGURA, REGRAS, Regras,
)


@dataclass(frozen=True)
class Retangulo:
    x: int
    y: int
    w: int
    h: int

    @property
    def direita(self) -> int:
        return self.x + self.w

    @property
    def baixo(self) -> int:
        return self.y + self.h

    def intersecta(self, o: "Retangulo") -> bool:
        return self.x < o.direita and o.x < self.direita and self.y < o.baixo and o.y < self.baixo

    def cabe_em(self, w: int, h: int) -> bool:
        return self.x >= 0 and self.y >= 0 and self.direita <= w and self.baixo <= h and self.w > 0 and self.h > 0

    @classmethod
    def de_texto(cls, texto: str) -> "Retangulo":
        """'x,y,w,h' -> Retangulo."""
        x, y, w, h = (int(float(v)) for v in texto.replace(" ", "").split(","))
        return cls(x, y, w, h)

    def texto(self) -> str:
        return f"{self.x},{self.y},{self.w},{self.h}"


def _par(n: float) -> int:
    return max(2, int(round(n / 2)) * 2)


def recorte_na_proporcao(area: Retangulo, prop_w: int, prop_h: int, centro: Optional[Tuple[float, float]] = None) -> Retangulo:
    """Maior recorte com a proporção pedida dentro de `area`, centrado em `centro` (nunca estica)."""
    if area.w / area.h > prop_w / prop_h:
        h = area.h
        w = round(h * prop_w / prop_h)
    else:
        w = area.w
        h = round(w * prop_h / prop_w)
    cx, cy = centro if centro else (area.x + area.w / 2, area.y + area.h / 2)
    x = int(min(max(cx - w / 2, area.x), area.direita - w))
    y = int(min(max(cy - h / 2, area.y), area.baixo - h))
    return Retangulo(x, y, w, h)


def jogo_automatico(quadro_w: int, quadro_h: int, camera: Optional[Retangulo], margem: float = 0.03) -> Retangulo:
    """Recorte do jogo (proporção 1080:1060) o maior possível SEM pegar a câmera.

    Tira `margem` das bordas (barra e legenda do player). Se a ação estiver embaixo da câmera,
    quem olha o quadro deve passar o recorte à mão (`--jogo x,y,w,h`): a ação vem antes da câmera.
    """
    mx, my = int(quadro_w * margem), int(quadro_h * margem)
    area = Retangulo(mx, my, quadro_w - 2 * mx, quadro_h - 2 * my)
    base = recorte_na_proporcao(area, LARGURA, JOGO_ALTURA)
    if camera is None:
        return base
    # a câmera é passada POR DENTRO da moldura: a folga evita pegar a moldura colorida no jogo
    folga = max(8, int(0.08 * max(camera.w, camera.h)))
    camera = Retangulo(camera.x - folga, camera.y - folga, camera.w + 2 * folga, camera.h + 2 * folga)
    for escala in [1 - i * 0.02 for i in range(0, 30)]:
        w, h = int(base.w * escala), int(base.h * escala)
        cy, cx = area.y + area.h / 2, area.x + area.w / 2
        candidatos = [
            (cx - w / 2, cy - h / 2),  # centro
            (camera.direita, cy - h / 2),  # à direita da câmera
            (camera.x - w, cy - h / 2),  # à esquerda
            (cx - w / 2, camera.baixo),  # abaixo
            (cx - w / 2, camera.y - h),  # acima
        ]
        for x, y in candidatos:
            x = int(min(max(x, area.x), area.direita - w))
            y = int(min(max(y, area.y), area.baixo - h))
            r = Retangulo(x, y, w, h)
            if r.cabe_em(quadro_w, quadro_h) and not r.intersecta(camera):
                return r
    return base


def camera_sem_esticar(camera: Retangulo) -> Retangulo:
    """Recorta laterais ou topo da câmera para chegar em 1080:860, mantendo o rosto (centro)."""
    return recorte_na_proporcao(camera, LARGURA, CAMERA_ALTURA)


def _zoom(entrada: str, saida: str, w: int, h: int, fator: float, janela: Optional[Tuple[float, float]], tag: str) -> str:
    """Cópia ampliada, recortada de volta para w x h (centralizada), por cima só no trecho do pico."""
    if not janela:
        return f"[{entrada}]null[{saida}]"
    a, b = janela
    zw, zh = _par(w * fator), _par(h * fator)
    return (
        f"[{entrada}]split=2[{tag}1][{tag}2];"
        f"[{tag}2]scale={zw}:{zh}:flags=lanczos,crop={w}:{h}[{tag}z];"
        f"[{tag}1][{tag}z]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[{saida}]"
    )


def janela_de_zoom(zoom_em_relativo: float, duracao: float, r: Regras = REGRAS) -> Optional[Tuple[float, float]]:
    if zoom_em_relativo < 0 or zoom_em_relativo >= duracao:
        return None
    a = max(0.0, zoom_em_relativo - 0.15)
    return a, min(duracao, a + r.zoom_duracao_s)


def filtro_com_camera(
    camera: Retangulo, jogo: Retangulo, ass: str, fontsdir: str, zoom: Optional[Tuple[float, float]], r: Regras = REGRAS
) -> str:
    cam = camera_sem_esticar(camera)
    jogo = recorte_na_proporcao(jogo, LARGURA, JOGO_ALTURA)
    return ";".join([
        "[0:v]split=2[fonte_cam][fonte_jogo]",
        f"[fonte_cam]crop={cam.w}:{cam.h}:{cam.x}:{cam.y},scale={LARGURA}:{CAMERA_ALTURA}:flags=lanczos,"
        f"unsharp=5:5:0.6,setsar=1[cam0]",
        _zoom("cam0", "cam", LARGURA, CAMERA_ALTURA, r.zoom_camera, zoom, "zc"),
        f"[fonte_jogo]crop={jogo.w}:{jogo.h}:{jogo.x}:{jogo.y},scale={LARGURA}:{JOGO_ALTURA}:flags=lanczos,setsar=1[jogo]",
        "[cam][jogo]vstack=inputs=2[emp]",
        f"[emp]subtitles={ass}:fontsdir={fontsdir},format=yuv420p[vout]",
    ])


def filtro_sem_camera(
    quadro_w: int, quadro_h: int, ass: str, fontsdir: str, zoom: Optional[Tuple[float, float]], r: Regras = REGRAS
) -> str:
    fg_h = _par(LARGURA * quadro_h / quadro_w)
    y = int(CENTRO_Y_SEM_CAMERA - fg_h / 2)
    return ";".join([
        "[0:v]split=2[fundo0][frente0]",
        # fundo: reduz, desfoca e amplia de volta (mais rápido que desfocar em 1080x1920)
        f"[fundo0]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=8:3,"
        f"scale={LARGURA}:{ALTURA},setsar=1[fundo]",
        f"[frente0]scale={LARGURA}:{fg_h}:flags=lanczos,setsar=1[frente1]",
        _zoom("frente1", "frente", LARGURA, fg_h, r.zoom_sem_camera, zoom, "zf"),
        f"[fundo][frente]overlay=0:{y}[emp]",
        f"[emp]subtitles={ass}:fontsdir={fontsdir},format=yuv420p[vout]",
    ])

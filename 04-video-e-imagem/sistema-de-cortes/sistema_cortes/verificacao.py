"""Conferência final de cada arquivo (duração, tamanho, som, volume, legenda e título aparecendo)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .audio import medir_arquivo
from .config import ALTURA, LARGURA, REGRAS, Regras
from .legenda import tempo_com_legenda
from .midia import extrair_quadro, sondar


@dataclass
class Relatorio:
    arquivo: str
    duracao: float
    largura: int
    altura: int
    tem_audio: bool
    lufs: float
    pico: float
    quadro: Optional[str] = None
    problemas: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problemas

    def linha(self) -> str:
        status = "OK" if self.ok else "PROBLEMA: " + "; ".join(self.problemas)
        return (
            f"{self.arquivo}: {self.duracao:.1f} s · {self.largura}x{self.altura} · "
            f"{self.lufs:.1f} LUFS · pico {self.pico:.1f} dB · {status}"
        )


def verificar(
    arquivo: Path,
    vertical: bool = True,
    ass: Optional[Path] = None,
    pasta_quadros: Optional[Path] = None,
    r: Regras = REGRAS,
) -> Relatorio:
    info = sondar(arquivo)
    lufs, pico = medir_arquivo(arquivo) if info.tem_audio else (float("-inf"), float("-inf"))
    rel = Relatorio(arquivo.name, info.duracao, info.largura, info.altura, info.tem_audio, lufs, pico)
    esperado = (LARGURA, ALTURA) if vertical else (1920, 1080)
    if (info.largura, info.altura) != esperado:
        rel.problemas.append(f"tamanho {info.largura}x{info.altura}, esperado {esperado[0]}x{esperado[1]}")
    if not info.tem_audio:
        rel.problemas.append("sem som")
    elif abs(lufs - r.lufs_alvo) > r.lufs_tolerancia:
        rel.problemas.append(f"volume {lufs:.1f} LUFS (alvo {r.lufs_alvo})")
    if info.tem_audio and pico > r.pico_verdadeiro_max_db + 0.05:
        rel.problemas.append(f"pico real {pico:.1f} dB (máx {r.pico_verdadeiro_max_db})")
    if vertical and not (r.corte_min_s - 1 <= info.duracao <= r.corte_max_s + 1):
        rel.problemas.append(f"duração {info.duracao:.1f} s fora de {r.corte_min_s:.0f}-{r.corte_max_s:.0f} s")
    if ass and ass.exists() and pasta_quadros:
        t = tempo_com_legenda(ass.read_text(encoding="utf-8"))
        if t is None:
            rel.problemas.append("o .ass não tem nenhuma legenda")
        else:
            q = extrair_quadro(arquivo, t, pasta_quadros / (arquivo.stem + ".png"))
            rel.quadro = str(q)  # o Claude abre a imagem e confere se legenda e título aparecem
    return rel

"""Tipos de dados usados por todo o sistema (sem lógica pesada aqui)."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List


@dataclass
class Palavra:
    inicio: float
    fim: float
    texto: str
    prob: float = 1.0

    def para_dict(self) -> dict:
        return asdict(self)


@dataclass
class Frase:
    palavras: List[Palavra]

    @property
    def inicio(self) -> float:
        return self.palavras[0].inicio

    @property
    def fim(self) -> float:
        return self.palavras[-1].fim

    @property
    def texto(self) -> str:
        return " ".join(p.texto for p in self.palavras)


@dataclass
class Momento:
    """Um momento escolhido da live. Tempos em segundos desde o começo da gravação."""

    pico: float
    tipo: str  # GRITO, REAÇÃO ou GRITO+REAÇÃO
    nota: float
    inicio: float = 0.0
    fim: float = 0.0
    zoom_em: float = 0.0  # segundo exato do zoom de impacto (palavra de reação ou pico)
    titulo: str = ""
    descricao: str = ""
    trecho: str = ""  # texto falado no corte (para quem for conferir/escrever o título)
    avisos: List[str] = field(default_factory=list)

    @property
    def duracao(self) -> float:
        return self.fim - self.inicio

    def para_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def de_dict(cls, d: dict) -> "Momento":
        return cls(**d)


def formatar_tempo(segundos: float) -> str:
    """83.4 -> '00:01:23' (HH:MM:SS, arredondando para baixo)."""
    s = max(0, int(segundos))
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def ler_tempo(texto: str) -> float:
    """Aceita '5025', '1:23:45', '23:45' ou '01:23:45.5'."""
    partes = texto.strip().split(":")
    if not 1 <= len(partes) <= 3:
        raise ValueError(f"tempo inválido: {texto!r}")
    total = 0.0
    for p in partes:
        total = total * 60 + float(p)
    return total

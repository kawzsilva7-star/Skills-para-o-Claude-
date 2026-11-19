"""Pastas e estado de uma live: cortes/<nome-da-live>/estado.json guarda tudo entre um passo e outro."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config import EXTENSOES_VIDEO
from .modelos import Momento


def videos_na_pasta(pasta: Path) -> List[Path]:
    return sorted(p for p in pasta.iterdir() if p.is_file() and p.suffix.lower() in EXTENSOES_VIDEO)


@dataclass
class Projeto:
    pasta: Path  # onde o dono abriu o Claude Code (tem a gravação)
    video: Path

    @property
    def nome(self) -> str:
        from .render import slug

        return slug(self.video.stem, 60)

    @property
    def saida(self) -> Path:
        return self.pasta / "cortes" / self.nome

    @property
    def analise(self) -> Path:
        return self.saida / "analise"

    @property
    def arquivo_estado(self) -> Path:
        return self.saida / "estado.json"

    def carregar(self) -> dict:
        if self.arquivo_estado.exists():
            return json.loads(self.arquivo_estado.read_text(encoding="utf-8"))
        return {"video": self.video.name, "aprovado": False, "momentos": [], "reservas": []}

    def salvar(self, estado: dict) -> None:
        self.saida.mkdir(parents=True, exist_ok=True)
        self.arquivo_estado.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")


def abrir(pasta: Path, video: Optional[str] = None) -> Projeto:
    """Acha a gravação. Mais de um vídeo e nenhum escolhido? Pergunta (erro com a lista)."""
    if video:
        v = (pasta / video) if not Path(video).is_absolute() else Path(video)
        if not v.exists():
            raise FileNotFoundError(f"Não achei {video}")
        return Projeto(pasta, v)
    achados = videos_na_pasta(pasta)
    if not achados:
        raise FileNotFoundError("Nenhum vídeo (mp4, mkv ou mov) nesta pasta.")
    if len(achados) > 1:
        nomes = ", ".join(p.name for p in achados)
        raise ValueError(f"Tem mais de um vídeo na pasta: {nomes}. Pergunte ao dono qual e use --video.")
    return Projeto(pasta, achados[0])


def momentos(estado: dict, chave: str = "momentos") -> List[Momento]:
    return [Momento.de_dict(d) for d in estado.get(chave, [])]


def guardar_momentos(estado: dict, lista: List[Momento], chave: str = "momentos") -> None:
    estado[chave] = [m.para_dict() for m in lista]

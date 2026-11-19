"""Nota de qualidade do candidato (LOGICA-DO-SISTEMA, seção 4). Quem dá a nota é a pessoa (com ajuda da IA);
o código só faz a conta e aplica a decisão, sempre igual.

5 itens, de 0 a 2 cada: gancho, virada, entende sozinho, relevância, vontade de rever.
9-10 posta agora · 7-8 fila · 5-6 reserva · abaixo de 5 descarta.
"Só fala, sem nada acontecendo na tela" vai para a reserva, mesmo com nota alta.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

ITENS = ("gancho", "virada", "entende_sozinho", "relevancia", "vontade_de_rever")
PERGUNTAS = {
    "gancho": "Prende nos primeiros 2 segundos?",
    "virada": "Tem um momento de surpresa ou explosão?",
    "entende_sozinho": "Quem não viu a live entende?",
    "relevancia": "É assunto do momento?",
    "vontade_de_rever": "Dá vontade de ver de novo ou mandar para alguém?",
}


@dataclass(frozen=True)
class Decisao:
    nota: int
    destino: str  # postar_agora | fila | reserva | descartar
    motivo: str


def decidir(notas: Dict[str, int], so_fala: bool = False) -> Decisao:
    faltando = [i for i in ITENS if i not in notas]
    if faltando:
        raise ValueError(f"faltam notas: {', '.join(faltando)}")
    for item in ITENS:
        if notas[item] not in (0, 1, 2):
            raise ValueError(f"{item}: nota deve ser 0, 1 ou 2")
    total = sum(notas[i] for i in ITENS)
    if total >= 9:
        destino, motivo = "postar_agora", "nota 9-10"
    elif total >= 7:
        destino, motivo = "fila", "nota 7-8"
    elif total >= 5:
        destino, motivo = "reserva", "nota 5-6"
    else:
        destino, motivo = "descartar", "nota abaixo de 5: poucos cortes bons valem mais que muitos ruins"
    if so_fala and destino in ("postar_agora", "fila"):
        destino, motivo = "reserva", "só fala, nada acontecendo na tela"
    return Decisao(total, destino, motivo)

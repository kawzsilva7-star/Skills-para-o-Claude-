"""Onde o corte começa e termina.

Regras (PDFs):
- começa 5 a 20 s antes do pico, no COMEÇO de uma frase que já faz parte do momento;
- se a frase anterior é de outro assunto, começa mais perto do pico (mínimo 3 s antes);
- termina quando acaba a frase depois do pico; sempre numa pausa, nunca no meio de palavra;
- nunca termina em palavra de ligação (e, o, a, que, mas, aí);
- o fim nunca passa do começo da palavra seguinte;
- 20 a 60 s (no modo ao vivo, 12 a 60 s).
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

from .config import LIGACAO, REGRAS, Regras
from .modelos import Frase, Momento, Palavra
from .momentos import normalizar

_FIM_DE_FRASE = (".", "?", "!", "…")


def montar_frases(palavras: Sequence[Palavra], r: Regras = REGRAS, max_palavras: int = 30) -> List[Frase]:
    """Separa as palavras em frases por pausa ou pontuação final."""
    frases: List[Frase] = []
    atual: List[Palavra] = []
    for i, p in enumerate(palavras):
        if atual and (p.inicio - atual[-1].fim >= r.pausa_entre_frases_s or len(atual) >= max_palavras):
            frases.append(Frase(atual))
            atual = []
        atual.append(p)
        if p.texto.rstrip().endswith(_FIM_DE_FRASE):
            frases.append(Frase(atual))
            atual = []
    if atual:
        frases.append(Frase(atual))
    return frases


def _indice_da_frase(frases: Sequence[Frase], t: float) -> int:
    for i, f in enumerate(frases):
        if f.inicio <= t <= f.fim + 0.3:
            return i
    depois = [i for i, f in enumerate(frases) if f.inicio > t]
    return depois[0] if depois else len(frases) - 1


def _sem_ligacao_no_fim(frase: Frase, lingua: str) -> Palavra:
    """Última palavra que não é de ligação (tira até 3 do fim)."""
    ligacao = LIGACAO.get(lingua, LIGACAO["pt"])
    palavras = frase.palavras
    k = len(palavras) - 1
    while k > 0 and len(palavras) - 1 - k < 3 and normalizar(palavras[k].texto) in ligacao:
        k -= 1
    return palavras[k]


def _entrada(palavra: Palavra, todas: Sequence[Palavra], r: Regras) -> float:
    """Começa um pouco antes da palavra, sem invadir a palavra anterior (corta na pausa)."""
    anteriores = [p for p in todas if p.fim <= palavra.inicio + 1e-6 and p is not palavra]
    limite = anteriores[-1].fim + 0.02 if anteriores else 0.0
    return max(limite, palavra.inicio - r.folga_inicio_s, 0.0)


def _saida(palavra: Palavra, todas: Sequence[Palavra], r: Regras) -> float:
    """Sai um pouco depois da palavra, mas nunca passa do começo da palavra seguinte."""
    seguintes = [p for p in todas if p.inicio >= palavra.fim - 1e-6 and p is not palavra]
    limite = seguintes[0].inicio - 0.02 if seguintes else float("inf")
    return min(palavra.fim + r.folga_fim_s, limite)


def definir_corte(
    pico: float,
    palavras: Sequence[Palavra],
    duracao_live: float,
    lingua: str = "pt",
    r: Regras = REGRAS,
) -> Tuple[float, float, List[str]]:
    """Devolve (inicio, fim, avisos) para um pico."""
    avisos: List[str] = []
    palavras = sorted(palavras, key=lambda p: p.inicio)
    frases = montar_frases(palavras, r)
    if not frases:
        ini = max(0.0, pico - r.antes_pico_min_s - 3)
        return ini, min(duracao_live, ini + r.corte_min_s), ["trecho sem fala: corte feito só pelo tempo"]

    k = _indice_da_frase(frases, pico)

    # ---- começo: sobe pelas frases do mesmo assunto, até 20 s antes do pico
    primeira = k
    while (
        primeira > 0
        and frases[primeira].inicio - frases[primeira - 1].fim < r.quebra_de_assunto_s
        and frases[primeira - 1].inicio >= pico - r.antes_pico_max_s
    ):
        primeira -= 1
    candidatas = [i for i in range(primeira, k + 1) if frases[i].inicio <= pico - r.antes_pico_min_s]
    if candidatas:
        palavra_ini = frases[candidatas[0]].palavras[0]
    else:
        # frase anterior é de outro assunto: começa perto do pico, mas no mínimo 3 s antes, numa palavra inteira
        antes = [p for p in palavras if p.inicio <= pico - r.antes_pico_absoluto_s]
        if antes and antes[-1].inicio >= pico - r.antes_pico_max_s:
            palavra_ini = antes[-1]
            if palavra_ini not in [f.palavras[0] for f in frases]:
                avisos.append("começo no meio de uma frase (a anterior era outro assunto)")
        else:
            palavra_ini = frases[primeira].palavras[0]
            if palavra_ini.inicio > pico - r.antes_pico_absoluto_s:
                avisos.append("começa menos de 3 s antes do pico")
    inicio = _entrada(palavra_ini, palavras, r)

    # ---- fim: acaba a frase do pico (se o pico está no finzinho, leva a frase seguinte junto)
    j = k
    if frases[j].fim - pico < 1.0 and j + 1 < len(frases) and frases[j + 1].inicio - frases[j].fim < r.quebra_de_assunto_s:
        j += 1
    fim = _saida(_sem_ligacao_no_fim(frases[j], lingua), palavras, r)

    # ---- duração mínima: leva frases seguintes, depois anteriores
    while fim - inicio < r.corte_min_s and j + 1 < len(frases) and frases[j + 1].fim - inicio <= r.corte_max_s:
        j += 1
        fim = _saida(_sem_ligacao_no_fim(frases[j], lingua), palavras, r)
    i0 = frases.index(next(f for f in frases if palavra_ini in f.palavras))
    while fim - inicio < r.corte_min_s and i0 > 0 and fim - frases[i0 - 1].inicio <= r.corte_max_s:
        i0 -= 1
        inicio = _entrada(frases[i0].palavras[0], palavras, r)
    if fim - inicio < r.corte_min_s:
        avisos.append(f"só deu {fim - inicio:.0f} s (mínimo {r.corte_min_s:.0f})")

    # ---- duração máxima: entra mais tarde (sem passar de 5 s antes do pico), depois corta o fim numa frase
    if fim - inicio > r.corte_max_s:
        for f in frases:
            if f.inicio > inicio and fim - f.inicio <= r.corte_max_s and f.inicio <= pico - r.antes_pico_absoluto_s:
                inicio = _entrada(f.palavras[0], palavras, r)
                break
    if fim - inicio > r.corte_max_s:
        cabem = [f for f in frases if f.fim <= inicio + r.corte_max_s and f.fim >= pico]
        if cabem:
            fim = _saida(_sem_ligacao_no_fim(cabem[-1], lingua), palavras, r)
        else:
            fim = inicio + r.corte_max_s
            avisos.append("fim cortado no limite de 60 s (frase muito longa)")

    return max(0.0, inicio), min(duracao_live, fim), avisos


def aplicar_limites(m: Momento, palavras: Sequence[Palavra], duracao_live: float, lingua: str, r: Regras = REGRAS) -> Momento:
    m.inicio, m.fim, avisos = definir_corte(m.pico, palavras, duracao_live, lingua, r)
    m.inicio, m.fim = round(m.inicio, 2), round(m.fim, 2)
    m.avisos.extend(avisos)
    m.trecho = " ".join(p.texto for p in palavras if m.inicio <= p.inicio < m.fim)
    if not (m.inicio <= m.zoom_em <= m.fim):
        m.zoom_em = m.pico
    return m

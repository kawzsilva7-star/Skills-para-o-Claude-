"""Monta o arquivo .ass: legenda palavra por palavra, título fixo no topo e crédito do streamer.

Garantias (testadas):
- nenhuma legenda com duração zero (faz o título sumir);
- nunca duas legendas ao mesmo tempo;
- uma legenda nunca passa de 1 linha (~900 px).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from .config import (
    ALTURA, AMARELO, BRANCO, CREDITO_FONTSIZE, CREDITO_MARGIN_V, ESTILOS_LEGENDA, ESTILOS_TITULO,
    LARGURA, LEGENDA_MARGIN_V_COM_CAMERA, PRETO, REGRAS, TITULO_MARGIN_V_COM_CAMERA,
    TITULO_MARGIN_V_SEM_CAMERA, VERDE, EstiloLegenda, EstiloTitulo, Regras, cor_tag,
)
from .modelos import Palavra
from .momentos import normalizar

PALAVROES = frozenset(
    "porra caralho merda foda fodase puta viado buceta cu fuck fucking shit bitch motherfucker".split()
)
_POP = r"{\fscx130\fscy130\t(0,90,\fscx100\fscy100)}"


@dataclass
class Evento:
    inicio_cs: int
    fim_cs: int
    estilo: str
    texto: str
    camada: int = 0


# ------------------------------------------------------------------- utilidades
def tempo_ass(cs: int) -> str:
    cs = max(0, cs)
    return f"{cs // 360000}:{(cs // 6000) % 60:02d}:{(cs // 100) % 60:02d}.{cs % 100:02d}"


def escapar(texto: str) -> str:
    return texto.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def censurar(texto: str) -> str:
    """'porra' -> 'p***'. Mantém pontuação."""
    nucleo = normalizar(texto)
    if nucleo in PALAVROES and nucleo:
        m = re.search(r"\w", texto)
        if m:
            i = m.start()
            return texto[: i + 1] + "*" * max(2, len(nucleo) - 1) + re.sub(r"[\w]", "", texto[i + 1:])
    return texto


def largura_px(texto: str, fontsize: int, maiusculas: bool) -> float:
    """Estimativa da largura em Arial Bold (sem medir a fonte de verdade)."""
    fator = 0.68 if maiusculas else 0.56
    return len(texto) * fontsize * fator


def quebrar_titulo(titulo: str, limite: int) -> str:
    """Título com mais de `limite` letras vira 2 linhas, cortando no espaço mais perto do meio."""
    titulo = " ".join(titulo.split())
    if len(titulo) <= limite or " " not in titulo:
        return titulo
    meio = len(titulo) / 2
    espacos = [i for i, c in enumerate(titulo) if c == " "]
    i = min(espacos, key=lambda x: abs(x - meio))
    return titulo[:i] + r"\N" + titulo[i + 1:]


def _texto_palavra(p: Palavra, estilo: EstiloLegenda, sem_pontuacao: bool = False) -> str:
    t = censurar(p.texto.strip())
    if sem_pontuacao:
        t = re.sub(r"[^\w*]", "", t)
    t = t.upper() if estilo.maiusculas else (t.lower() if estilo.modo == "minimal" else t)
    return escapar(t)


def agrupar(palavras: Sequence[Palavra], estilo: EstiloLegenda, largura_max: int, pausa_s: float = 0.7) -> List[List[Palavra]]:
    """Grupos de até N palavras que cabem em 1 linha; quebra também em pausa ou fim de frase."""
    grupos: List[List[Palavra]] = []
    atual: List[Palavra] = []
    for p in palavras:
        candidato = atual + [p]
        texto = " ".join(_texto_palavra(x, estilo) for x in candidato)
        quebra = bool(atual) and (
            len(candidato) > estilo.max_palavras
            or largura_px(texto, estilo.fontsize, estilo.maiusculas) > largura_max
            or p.inicio - atual[-1].fim > pausa_s
            or atual[-1].texto.rstrip().endswith((".", "?", "!"))
        )
        if quebra:
            grupos.append(atual)
            atual = [p]
        else:
            atual = candidato
    if atual:
        grupos.append(atual)
    return grupos


def _cs(t: float) -> int:
    return int(round(t * 100))


def normalizar_eventos(eventos: List[Evento], duracao_cs: int, minimo_cs: int) -> List[Evento]:
    """Ordena, tira sobreposição, garante duração mínima e corta no fim do vídeo."""
    saida: List[Evento] = []
    fim_anterior = 0
    for e in sorted(eventos, key=lambda x: x.inicio_cs):
        ini = max(e.inicio_cs, fim_anterior)
        fim = max(e.fim_cs, ini + minimo_cs)
        fim = min(fim, duracao_cs)
        if fim - ini < minimo_cs:
            continue
        saida.append(Evento(ini, fim, e.estilo, e.texto, e.camada))
        fim_anterior = fim
    # um evento termina onde o próximo começa (nunca dois ao mesmo tempo)
    for a, b in zip(saida, saida[1:]):
        a.fim_cs = min(a.fim_cs, b.inicio_cs)
    return [e for e in saida if e.fim_cs - e.inicio_cs >= minimo_cs]


# ------------------------------------------------------------------- eventos por estilo
def eventos_legenda(palavras: Sequence[Palavra], estilo: EstiloLegenda, r: Regras = REGRAS) -> List[Evento]:
    """Palavras com tempo relativo ao começo do corte."""
    if not palavras:
        return []
    amarelo, volta = cor_tag(AMARELO), r"{\r}"
    eventos: List[Evento] = []
    if estilo.modo == "beasty":
        cores = [AMARELO, VERDE, BRANCO]
        for i, p in enumerate(palavras):
            fim = palavras[i + 1].inicio if i + 1 < len(palavras) and palavras[i + 1].inicio - p.fim < 0.4 else p.fim
            texto = _texto_palavra(p, estilo, sem_pontuacao=True)
            if not texto:
                continue
            fs = ""
            w = largura_px(texto, estilo.fontsize, True)
            if w > r.legenda_largura_max_px:
                fs = r"{\fs%d}" % int(estilo.fontsize * r.legenda_largura_max_px / w)
            eventos.append(Evento(_cs(p.inicio), _cs(fim), "Leg", f"{fs}{{\\c{cor_tag(cores[i % 3])}}}{_POP}{texto}"))
        return eventos

    for grupo in agrupar(palavras, estilo, r.legenda_largura_max_px):
        textos = [_texto_palavra(p, estilo) for p in grupo]
        if estilo.modo == "karaoke":
            ini = _cs(grupo[0].inicio)
            partes, cursor = [], ini
            for j, p in enumerate(grupo):
                prox = _cs(grupo[j + 1].inicio) if j + 1 < len(grupo) else _cs(p.fim)
                dur = max(1, prox - cursor)
                partes.append(f"{{\\kf{dur}}}{textos[j]}")
                cursor += dur
            eventos.append(Evento(ini, cursor, "Leg", " ".join(partes)))
            continue
        for j, p in enumerate(grupo):
            fim = grupo[j + 1].inicio if j + 1 < len(grupo) else p.fim
            if estilo.modo == "minimal":
                partes = [
                    t if k == j else r"{\alpha&H70&}" + t + r"{\alpha&H00&}" for k, t in enumerate(textos)
                ]
            else:  # destaque e caixa: palavra falada em amarelo
                partes = [f"{{\\c{amarelo}}}{t}{volta}" if k == j else t for k, t in enumerate(textos)]
            eventos.append(Evento(_cs(p.inicio), _cs(fim), "Leg", " ".join(partes)))
    return eventos


# ------------------------------------------------------------------- arquivo
_FORMATO_ESTILO = (
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
    "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
    "Alignment, MarginL, MarginR, MarginV, Encoding"
)


def _linha_estilo(nome, fonte, size, prim, sec, out, back, bs, outline, shadow, alin, mv) -> str:
    return (
        f"Style: {nome},{fonte},{size},{prim},{sec},{out},{back},-1,0,0,0,100,100,0,0,"
        f"{bs},{outline},{shadow},{alin},40,40,{mv},1"
    )


def gerar_ass(
    palavras_relativas: Sequence[Palavra],
    duracao: float,
    titulo: str,
    estilo_legenda: str = "destaque",
    estilo_titulo: str = "contorno",
    com_camera: bool = False,
    credito: Optional[str] = None,
    fonte: str = "Arial",
    r: Regras = REGRAS,
) -> Tuple[str, List[Evento]]:
    """Devolve (texto do .ass, eventos de legenda). `palavras_relativas`: tempos a partir do começo do corte."""
    el = ESTILOS_LEGENDA[estilo_legenda]
    et: EstiloTitulo = ESTILOS_TITULO[estilo_titulo]
    mv_leg = LEGENDA_MARGIN_V_COM_CAMERA if com_camera else el.margin_v
    mv_tit = TITULO_MARGIN_V_COM_CAMERA if com_camera else TITULO_MARGIN_V_SEM_CAMERA
    dur_cs = _cs(duracao)

    legendas = normalizar_eventos(eventos_legenda(palavras_relativas, el, r), dur_cs, r.ass_duracao_minima_cs)
    linhas = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {LARGURA}",
        f"PlayResY: {ALTURA}",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        _FORMATO_ESTILO,
        _linha_estilo("Leg", fonte, el.fontsize, el.primary, el.secondary, el.outline_cor, el.back_cor,
                      el.border_style, el.outline, el.shadow, 2, mv_leg),
        _linha_estilo("Tit", fonte, et.fontsize, et.primary, et.primary, et.outline_cor, PRETO,
                      et.border_style, et.outline, 0, 8, mv_tit),
        _linha_estilo("Cred", fonte, CREDITO_FONTSIZE, BRANCO, BRANCO, PRETO, PRETO, 1, 4, 0, 2, CREDITO_MARGIN_V),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    fixos = []
    if titulo:
        fixos.append(Evento(0, dur_cs, "Tit", quebrar_titulo(escapar(titulo), r.titulo_quebra_letras), 1))
    if credito:
        fixos.append(Evento(0, dur_cs, "Cred", escapar(credito), 1))
    for e in fixos + legendas:
        linhas.append(
            f"Dialogue: {e.camada},{tempo_ass(e.inicio_cs)},{tempo_ass(e.fim_cs)},{e.estilo},,0,0,0,,{e.texto}"
        )
    return "\n".join(linhas) + "\n", legendas


def palavras_relativas(palavras: Sequence[Palavra], inicio: float, fim: float) -> List[Palavra]:
    """Só as palavras dentro do corte, com o tempo contado a partir do começo do corte."""
    return [
        Palavra(max(0.0, p.inicio - inicio), min(fim, p.fim) - inicio, p.texto, p.prob)
        for p in palavras
        if p.inicio >= inicio - 0.05 and p.fim <= fim + 0.3 and p.inicio < fim
    ]


def tempo_com_legenda(texto_ass: str) -> Optional[float]:
    """Meio da primeira legenda (estilo Leg) — para tirar o quadro de conferência."""
    m = re.search(r"Dialogue: \d+,(\d+):(\d+):(\d+)\.(\d+),(\d+):(\d+):(\d+)\.(\d+),Leg,", texto_ass)
    if not m:
        return None
    v = [int(x) for x in m.groups()]
    a = v[0] * 3600 + v[1] * 60 + v[2] + v[3] / 100
    b = v[4] * 3600 + v[5] * 60 + v[6] + v[7] / 100
    return (a + b) / 2

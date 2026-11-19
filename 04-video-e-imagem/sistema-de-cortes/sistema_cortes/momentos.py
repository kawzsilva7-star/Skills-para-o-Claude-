"""Achar os momentos: nota de GRITO + REAÇÃO (+ CHAT, no modo ao vivo) por segundo, e os N melhores picos."""
from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .config import REACOES, REGRAS, ROTULOS_TIPO, Regras
from .modelos import Momento, Palavra

_RISADA = re.compile(r"^(k{3,}|(ha){2,}h?|(ah){2,}|(he){2,}|(ja){2,}|lol|lmao|rs{2,}|hu(e|a){2,}.*)$")


def normalizar(texto: str) -> str:
    """'Não!' -> 'nao'. Sem acento, minúsculas, sem pontuação."""
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^\w\s]", "", t).strip()


def mascara_fala(palavras: Sequence[Palavra], n: int) -> np.ndarray:
    """True nos segundos em que alguém está falando."""
    fala = np.zeros(n, dtype=bool)
    for p in palavras:
        a, b = int(p.inicio), int(np.ceil(p.fim))
        fala[max(0, a): min(n, max(b, a + 1))] = True
    return fala


# ------------------------------------------------------------------- GRITO
def nota_grito(volume: np.ndarray, fala: np.ndarray, r: Regras = REGRAS) -> np.ndarray:
    """Compara cada segundo com a mediana dos segundos COM FALA nos 2 minutos em volta.

    Silêncio fica fora da mediana (senão a fala normal parece grito). Só conta a partir de
    `grito_db_acima` dB acima; segundo sem voz (barulho do jogo) vale `peso_sem_fala`.
    """
    n = len(volume)
    nota = np.zeros(n, dtype=np.float32)
    meio = r.janela_mediana_s // 2
    for s in range(n):
        a, b = max(0, s - meio), min(n, s + meio + 1)
        janela = volume[a:b][fala[a:b]]
        if janela.size < 5:
            continue
        acima = float(volume[s] - np.median(janela))
        if acima < r.grito_db_acima:
            continue
        valor = min(acima / r.grito_db_acima, r.grito_teto)
        nota[s] = valor if fala[s] else valor * r.peso_sem_fala
    return nota


# ------------------------------------------------------------------- REAÇÃO
def _frases_de_reacao(lingua: str) -> List[Tuple[str, ...]]:
    lista = REACOES.get(lingua) or tuple(x for v in REACOES.values() for x in v)
    return sorted({tuple(normalizar(f).split()) for f in lista}, key=len, reverse=True)


def achar_reacoes(palavras: Sequence[Palavra], lingua: str) -> List[Tuple[float, float, str]]:
    """Lista (tempo, peso, motivo) de cada sinal de reação na transcrição."""
    norm = [normalizar(p.texto) for p in palavras]
    frases = _frases_de_reacao(lingua)
    sinais: List[Tuple[float, float, str]] = []
    i = 0
    while i < len(palavras):
        achou = False
        for f in frases:
            if tuple(norm[i: i + len(f)]) == f:
                sinais.append((palavras[i].inicio, 1.0, " ".join(f)))
                if palavras[i + len(f) - 1].texto.rstrip().endswith("!"):
                    sinais.append((palavras[i].inicio, 0.5, "exclamação"))
                i += len(f)
                achou = True
                break
        if achou:
            continue
        w = norm[i]
        if w and _RISADA.match(w):
            sinais.append((palavras[i].inicio, 1.0, "risada"))
        elif w and i > 0 and w == norm[i - 1] and palavras[i].inicio - palavras[i - 1].fim < 1.5:
            sinais.append((palavras[i].inicio, 0.8, f"repetiu '{w}'"))
        if palavras[i].texto.rstrip().endswith("!"):
            sinais.append((palavras[i].inicio, 0.5, "exclamação"))
        i += 1
    sinais.extend(_fala_acelerada(palavras))
    return sinais


def _fala_acelerada(palavras: Sequence[Palavra]) -> List[Tuple[float, float, str]]:
    """Fala que acelera de repente: palavras/s numa janela de 5 s bem acima do normal do minuto."""
    if len(palavras) < 30:
        return []
    fim = int(palavras[-1].fim) + 1
    contagem = np.zeros(fim)
    for p in palavras:
        contagem[int(p.inicio)] += 1
    taxa = np.convolve(contagem, np.ones(5) / 5, mode="same")
    sinais = []
    for s in range(0, fim, 5):
        a, b = max(0, s - 60), min(fim, s + 60)
        base = np.median(taxa[a:b][taxa[a:b] > 0]) if np.any(taxa[a:b] > 0) else 0
        if base > 0 and taxa[s] >= 3 and taxa[s] >= 1.6 * base:
            sinais.append((float(s), 0.5, "fala acelerada"))
    return sinais


def nota_reacao(palavras: Sequence[Palavra], n: int, lingua: str) -> np.ndarray:
    nota = np.zeros(n, dtype=np.float32)
    for t, peso, _ in achar_reacoes(palavras, lingua):
        if 0 <= int(t) < n:
            nota[int(t)] += peso
    return nota


# ------------------------------------------------------------------- CHAT (ao vivo)
def nota_chat(msgs_por_segundo: Optional[np.ndarray], n: int, atraso_s: int = 10) -> np.ndarray:
    """Pico de mensagens no chat. O chat reage ~10 s depois: puxamos a curva 10 s para trás."""
    nota = np.zeros(n, dtype=np.float32)
    if msgs_por_segundo is None or len(msgs_por_segundo) == 0:
        return nota
    m = np.asarray(msgs_por_segundo, dtype=np.float32)
    base = float(np.median(m)) + 1.0
    rel = np.clip(m / base - 2.0, 0, 3)  # só conta acima de 3x o normal
    rel = rel[atraso_s:]
    k = min(n, len(rel))
    nota[:k] = rel[:k]
    return nota


# ------------------------------------------------------------------- escolher
def suavizar(nota: np.ndarray, janela: int) -> np.ndarray:
    """Soma numa janela: vários sinais juntos valem mais que um isolado."""
    if janela <= 1 or nota.size == 0:
        return nota.astype(np.float32)
    return np.convolve(nota, np.ones(janela, dtype=np.float32), mode="same")


def escolher_picos(nota: np.ndarray, quantos: int, distancia_s: float, minimo: float) -> List[int]:
    """Os `quantos` maiores picos que não se sobrepõem. Não inventa: para quando a nota cai abaixo de `minimo`."""
    resto = nota.astype(np.float64).copy()
    picos: List[int] = []
    raio = int(distancia_s)
    while len(picos) < quantos and resto.size:
        s = int(np.argmax(resto))
        if resto[s] < minimo:
            break
        picos.append(s)
        resto[max(0, s - raio): s + raio + 1] = -np.inf
    return picos


def achar_momentos(
    palavras: Sequence[Palavra],
    volume: np.ndarray,
    quantos: int,
    lingua: str = "pt",
    chat: Optional[np.ndarray] = None,
    r: Regras = REGRAS,
) -> Tuple[List[Momento], List[Momento]]:
    """Devolve (principais, reservas). Principais ordenados do mais forte ao mais fraco."""
    n = len(volume)
    fala = mascara_fala(palavras, n)
    g = nota_grito(volume, fala, r)
    re_ = nota_reacao(palavras, n, lingua)
    c = nota_chat(chat, n)
    total = suavizar(g + re_ + c, r.suavizar_s)
    picos = escolher_picos(total, quantos + r.reservas, r.distancia_minima_s, r.nota_minima)
    rotulos = ROTULOS_TIPO.get(lingua, ROTULOS_TIPO["pt"])
    reacoes = achar_reacoes(palavras, lingua)
    momentos = []
    for s in picos:
        a, b = max(0, s - 4), min(n, s + 5)
        tem_g, tem_r = g[a:b].sum() > 0, (re_[a:b].sum() + c[a:b].sum()) > 0
        tipo = rotulos["ambos"] if tem_g and tem_r else rotulos["grito"] if tem_g else rotulos["reacao"]
        momentos.append(
            Momento(
                pico=float(s), tipo=tipo, nota=round(float(total[s]), 2),
                zoom_em=_onde_dar_zoom(s, reacoes, g),
                avisos=_avisos(s, g, re_),
            )
        )
    return momentos[:quantos], momentos[quantos:]


def _onde_dar_zoom(pico: int, reacoes: List[Tuple[float, float, str]], grito: np.ndarray) -> float:
    """Zoom na palavra de reação (o 'caraca') mais perto do pico; se não tiver, no segundo de grito mais forte."""
    perto = [t for t, peso, _ in reacoes if abs(t - pico) <= 4 and peso >= 1.0]
    if perto:
        return float(min(perto, key=lambda t: abs(t - pico)))
    a, b = max(0, pico - 4), min(len(grito), pico + 5)
    if b > a and grito[a:b].max() > 0:
        return float(a + int(np.argmax(grito[a:b])))
    return float(pico)


def _avisos(s: int, g: np.ndarray, re_: np.ndarray) -> List[str]:
    a, b = max(0, s - 4), min(len(g), s + 5)
    if g[a:b].sum() == 0 and 0 < re_[a:b].sum() <= 1.0:
        return ["só 1 palavra de reação e nenhum grito: pode ser fala do jogo, confira"]
    return []


def conferir_reacao_fina(m: Momento, palavras_finas: Sequence[Palavra], lingua: str) -> Momento:
    """Depois da transcrição fina (beam 5): se a reação sumiu, provavelmente era fala do jogo/trailer."""
    perto = [x for x in achar_reacoes(palavras_finas, lingua) if abs(x[0] - m.pico) <= 6]
    if not perto and "GRITO" not in m.tipo.upper() and "SCREAM" not in m.tipo.upper():
        m.avisos.append("a reação some na transcrição fina: provável fala de personagem/cutscene")
    return m


def resumo_sinais(palavras: Sequence[Palavra], lingua: str) -> Dict[str, int]:
    """Para mostrar ao dono por que o momento foi escolhido."""
    cont: Dict[str, int] = {}
    for _, _, motivo in achar_reacoes(palavras, lingua):
        cont[motivo] = cont.get(motivo, 0) + 1
    return cont

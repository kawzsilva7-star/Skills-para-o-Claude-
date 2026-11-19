"""Modo AO VIVO (LOGICA-DO-SISTEMA): grava a live em blocos, lê o chat e analisa cada bloco novo.

Ninguém precisa "baixar a live": o gravador (streamlink) salva blocos de 20 min enquanto a live acontece,
o analisador acha os candidatos e põe numa fila `pendentes/`. Uma pessoa aprova e o corte é gerado.

Regras:
- só streamers com permissão (campo `permissao` no streamers.json; sem ele, não grava);
- no máximo 3 gravando ao mesmo tempo;
- offline: confere a cada 30 min (dia de lançamento: 2 min);
- até 4 picos por bloco, 45 s entre eles, corte de 12 a 60 s, começo 3 a 20 s antes do pico;
- limpeza: bloco sem candidato é apagado; bloco com candidato vive no máx. 6 h.
"""
from __future__ import annotations

import json
import socket
import time
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

import numpy as np

from .config import REGRAS, Regras
from .limites import aplicar_limites
from .midia import extrair_wav, rodar, sondar
from .momentos import achar_momentos
from .transcricao import Transcritor, retranscrever_trecho
from .volume import medir_volume

MAX_GRAVANDO = 3
BLOCO_S = 20 * 60
CHECAR_OFFLINE_S = 30 * 60
CHECAR_OFFLINE_LANCAMENTO_S = 2 * 60
PICOS_POR_BLOCO = 4
VIDA_BLOCO_COM_CANDIDATO_S = 6 * 3600

# Regras do modo ao vivo: as mesmas dos PDFs, com corte mínimo de 12 s e começo a partir de 3 s antes.
REGRAS_AO_VIVO = replace(REGRAS, corte_min_s=12.0, antes_pico_min_s=3.0, reservas=0)


@dataclass
class Streamer:
    nome: str
    link: str  # twitch.tv/..., youtube.com/@.../live, kick.com/...
    arroba: str  # para o crédito
    idioma: str = "pt"
    camera: Optional[str] = None  # "x,y,w,h" no quadro da live, ou None
    permissao: str = ""  # onde está escrita (obrigatório)

    @property
    def canal_twitch(self) -> Optional[str]:
        if "twitch.tv/" in self.link:
            return self.link.rstrip("/").split("twitch.tv/")[-1].split("/")[0].lower()
        return None


def carregar_streamers(arquivo: Path) -> List[Streamer]:
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    lista = [Streamer(**d) for d in dados]
    sem = [s.nome for s in lista if len(s.permissao.strip()) < 5]
    if sem:
        raise ValueError(f"Sem permissão registrada, não gravo: {', '.join(sem)}")
    if len(lista) > MAX_GRAVANDO:
        raise ValueError(f"No máximo {MAX_GRAVANDO} streamers ao mesmo tempo (tem {len(lista)}).")
    return lista


# ------------------------------------------------------------------- gravador
def comando_streamlink(link: str) -> List[str]:
    """Grava sem reencodar (qualidade original). O ffmpeg depois divide em blocos de 20 min."""
    return ["streamlink", "--twitch-disable-ads", "--retry-streams", "30", "--retry-max", "3",
            "--retry-open", "5", "-O", link, "best"]


def comando_blocos(pasta: Path, nome: str) -> List[str]:
    """Lê o stream do streamlink pela entrada padrão e salva blocos de 20 min com data e hora no nome."""
    return [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", "pipe:0", "-c", "copy", "-map", "0",
        "-f", "segment", "-segment_time", str(BLOCO_S), "-reset_timestamps", "1", "-strftime", "1",
        str(pasta / f"{nome}_%Y-%m-%d_%H-%M-%S.mkv"),
    ]


def esta_ao_vivo(link: str) -> bool:
    r = rodar(["streamlink", "--json", link])
    return r.returncode == 0 and '"streams"' in (r.stdout or "")


def gravar_sessao(streamer: Streamer, pasta: Path, avisar: Callable[[str], None] = print) -> None:
    """Grava enquanto a live durar (streamlink -> ffmpeg em blocos). Volta quando o stream termina."""
    import subprocess

    pasta.mkdir(parents=True, exist_ok=True)
    avisar(f"{streamer.nome} está ao vivo: gravando em blocos de 20 min em {pasta}.")
    sl = subprocess.Popen(comando_streamlink(streamer.link), stdout=subprocess.PIPE)
    ff = subprocess.Popen(comando_blocos(pasta, streamer.nome), stdin=sl.stdout)
    sl.stdout.close()  # type: ignore[union-attr]
    ff.wait()
    sl.wait()


def gravar_ate_acabar(streamer: Streamer, pasta: Path, avisar: Callable[[str], None] = print,
                      tentativas_reconectar: int = 3, espera_s: int = 60) -> None:
    """Modo link: grava a live e, se cair, tenta reconectar algumas vezes. Termina quando ela acaba de vez."""
    while True:
        gravar_sessao(streamer, pasta, avisar)
        for _ in range(tentativas_reconectar):
            time.sleep(espera_s)
            if esta_ao_vivo(streamer.link):
                avisar(f"{streamer.nome}: a live voltou, reconectando.")
                break
        else:
            avisar(f"{streamer.nome}: a live acabou.")
            return


def gravar(streamer: Streamer, pasta: Path, lancamento: bool = False, avisar: Callable[[str], None] = print) -> None:
    """Loop do gravador de UM streamer (fica de olho para sempre). Reconecta sozinho se a live cair."""
    espera = CHECAR_OFFLINE_LANCAMENTO_S if lancamento else CHECAR_OFFLINE_S
    while True:
        if not esta_ao_vivo(streamer.link):
            time.sleep(espera)
            continue
        gravar_sessao(streamer, pasta, avisar)
        avisar(f"{streamer.nome}: gravação parou (live caiu ou acabou). Conferindo de novo.")
        time.sleep(10)


# ------------------------------------------------------------------- chat da Twitch
def ler_chat_twitch(canal: str, saida_csv: Path, parar: Callable[[], bool] = lambda: False) -> None:
    """Lê o chat de forma anônima (usuário justinfan) e grava 'segundo_unix,mensagens' por segundo."""
    s = socket.create_connection(("irc.chat.twitch.tv", 6667), timeout=30)
    s.sendall(b"NICK justinfan%d\r\n" % (int(time.time()) % 100000))
    s.sendall(f"JOIN #{canal}\r\n".encode())
    contagem: Dict[int, int] = {}
    buf = b""
    saida_csv.parent.mkdir(parents=True, exist_ok=True)
    with saida_csv.open("a", encoding="utf-8") as f:
        while not parar():
            try:
                buf += s.recv(4096)
            except socket.timeout:
                continue
            *linhas, buf = buf.split(b"\r\n")
            agora = int(time.time())
            for linha in linhas:
                if linha.startswith(b"PING"):
                    s.sendall(b"PONG :tmi.twitch.tv\r\n")
                elif b" PRIVMSG " in linha:
                    contagem[agora] = contagem.get(agora, 0) + 1
            for seg in [k for k in contagem if k < agora]:
                f.write(f"{seg},{contagem.pop(seg)}\n")
            f.flush()


def chat_do_bloco(csv: Path, inicio_unix: float, duracao: float) -> Optional[np.ndarray]:
    if not csv.exists():
        return None
    n = int(duracao) + 1
    serie = np.zeros(n, dtype=np.float32)
    for linha in csv.read_text(encoding="utf-8").splitlines():
        seg, _, qtd = linha.partition(",")
        i = int(seg) - int(inicio_unix)
        if 0 <= i < n:
            serie[i] += float(qtd)
    return serie


# ------------------------------------------------------------------- analisador
@dataclass
class Candidato:
    streamer: str
    arroba: str
    bloco: str
    inicio: float
    fim: float
    pico: float
    zoom_em: float
    tipo: str
    nota: float
    texto: str
    idioma: str
    avisos: List[str] = field(default_factory=list)
    criado_em: str = ""


def inicio_do_bloco(arquivo: Path) -> Optional[float]:
    """Lê data/hora do nome 'nome_AAAA-MM-DD_HH-MM-SS.mkv'."""
    try:
        carimbo = "_".join(arquivo.stem.split("_")[-2:])
        return datetime.strptime(carimbo, "%Y-%m-%d_%H-%M-%S").timestamp()
    except ValueError:
        return None


def analisar_bloco(
    bloco: Path, streamer: Streamer, transcritor: Transcritor, pasta_pendentes: Path,
    chat_csv: Optional[Path] = None, r: Regras = REGRAS_AO_VIVO,
) -> List[Candidato]:
    """Analisa um bloco de 20 min e salva até 4 candidatos em `pendentes/` (um .json cada)."""
    trabalho = bloco.with_suffix("")
    wav = extrair_wav(bloco, trabalho / "audio.wav")
    info = sondar(bloco)
    from .transcricao import detectar_lingua, transcrever_live

    if not streamer.idioma:  # "auto": descobre no 1º bloco e mantém
        streamer.idioma = detectar_lingua(wav, info.duracao, transcritor)[0]

    palavras = transcrever_live(wav, trabalho / "transcricao.json", transcritor, streamer.idioma, info.duracao,
                                avisar=lambda *_: None)
    volume = medir_volume(wav, trabalho / "volume.npy")
    chat = None
    t0 = inicio_do_bloco(bloco)
    if chat_csv and t0:
        chat = chat_do_bloco(chat_csv, t0, info.duracao)
    momentos, _ = achar_momentos(palavras, volume, PICOS_POR_BLOCO, streamer.idioma, chat, r)
    candidatos = []
    pasta_pendentes.mkdir(parents=True, exist_ok=True)
    for m in momentos:
        finas = retranscrever_trecho(wav, max(0, m.pico - 30), m.pico + 45, transcritor, streamer.idioma)
        aplicar_limites(m, finas, info.duracao, streamer.idioma, r)
        c = Candidato(streamer.nome, streamer.arroba, bloco.name, m.inicio, m.fim, m.pico, m.zoom_em, m.tipo,
                      m.nota, m.trecho, streamer.idioma, m.avisos, datetime.now().isoformat(timespec="seconds"))
        destino = pasta_pendentes / f"{bloco.stem}_{int(m.pico):05d}.json"
        destino.write_text(json.dumps({**asdict(c), "palavras": [p.para_dict() for p in finas]}, ensure_ascii=False),
                           encoding="utf-8")
        candidatos.append(c)
    return candidatos


def limpar(pasta_blocos: Path, pasta_pendentes: Path, agora: Optional[float] = None) -> List[Path]:
    """Apaga blocos já analisados sem candidato e blocos com candidato com mais de 6 h. Devolve o que apagou."""
    agora = agora or time.time()
    usados = {json.loads(p.read_text(encoding="utf-8"))["bloco"] for p in pasta_pendentes.glob("*.json")}
    apagados = []
    for bloco in pasta_blocos.glob("*.mkv"):
        analisado = (bloco.with_suffix("") / "transcricao.json").exists()
        velho = agora - bloco.stat().st_mtime > VIDA_BLOCO_COM_CANDIDATO_S
        if analisado and (bloco.name not in usados or velho):
            bloco.unlink()
            apagados.append(bloco)
    return apagados


def blocos_prontos(pasta: Path, ja_vistos: Iterable[str], parado_ha_s: float = 60) -> List[Path]:
    """Blocos fechados (sem mudar de tamanho há 1 min) e ainda não analisados."""
    vistos = set(ja_vistos)
    agora = time.time()
    return sorted(
        b for b in pasta.glob("*.mkv")
        if b.name not in vistos and agora - b.stat().st_mtime > parado_ha_s
    )


def analisar_novos(
    streamers: List[Streamer], pasta_raiz: Path, transcritor: Transcritor, vistos: Dict[str, set],
    avisar: Callable[[str], None] = print, parado_ha_s: float = 60,
) -> int:
    """Uma passada: analisa os blocos fechados que ainda não viu. Devolve quantos candidatos achou."""
    pendentes = pasta_raiz / "pendentes"
    total = 0
    for s in streamers:
        pasta = pasta_raiz / "blocos" / s.nome
        if not pasta.exists():
            continue
        for bloco in blocos_prontos(pasta, vistos.setdefault(s.nome, set()), parado_ha_s):
            chat = pasta_raiz / "chat" / f"{s.canal_twitch}.csv" if s.canal_twitch else None
            cands = analisar_bloco(bloco, s, transcritor, pendentes, chat)
            vistos[s.nome].add(bloco.name)
            total += len(cands)
            avisar(f"{s.nome} · {bloco.name}: {len(cands)} candidato(s).")
        limpar(pasta, pendentes)
    return total


def loop_analisador(
    streamers: List[Streamer], pasta_raiz: Path, transcritor: Transcritor,
    a_cada_s: int = 30, avisar: Callable[[str], None] = print,
    continuar: Callable[[], bool] = lambda: True,
) -> int:
    """Um analisador para todos: a cada 30 s procura blocos novos. Quando `continuar()` vira False,
    analisa o que sobrou (inclusive o último bloco) e termina."""
    vistos: Dict[str, set] = {}
    total = 0
    while continuar():
        total += analisar_novos(streamers, pasta_raiz, transcritor, vistos, avisar)
        time.sleep(a_cada_s)
    return total + analisar_novos(streamers, pasta_raiz, transcritor, vistos, avisar, parado_ha_s=0)


# ------------------------------------------------------------------- acompanhar PERFIS (sempre)
BATIMENTO = ".acompanhando"


def _gravar_sem_parar(s: Streamer, pasta: Path, lancamento: bool, avisar: Callable[[str], None]) -> None:
    while True:  # um erro (internet caiu, programa travou) não pode matar o gravador
        try:
            gravar(s, pasta, lancamento, avisar)
        except Exception as e:  # noqa: BLE001
            avisar(f"{s.nome}: gravador reiniciando depois de erro ({e}).")
            time.sleep(60)


def _chat_sem_parar(canal: str, csv: Path, avisar: Callable[[str], None]) -> None:
    while True:
        try:
            ler_chat_twitch(canal, csv)
        except OSError as e:
            avisar(f"chat de {canal}: reconectando ({e}).")
        time.sleep(30)


def esta_acompanhando(raiz: Path, idade_max_s: float = 120) -> bool:
    """Já existe uma janela acompanhando os perfis desta pasta? (batimento renovado a cada 30 s)"""
    arq = raiz / BATIMENTO
    try:
        return time.time() - float(arq.read_text()) < idade_max_s
    except (OSError, ValueError):
        return False


def acompanhar_perfis(
    raiz: Path, transcritor: Transcritor, lancamento: bool = False,
    avisar: Callable[[str], None] = print, a_cada_s: int = 30, voltas: Optional[int] = None,
) -> None:
    """Uma janela só: fica de olho em todos os perfis do streamers.json, grava toda live deles e analisa.

    Relê o streamers.json a cada volta: perfil novo entra sozinho, sem fechar nada.
    """
    import threading

    arq = raiz / "streamers.json"
    rodando: Dict[str, threading.Thread] = {}
    vistos: Dict[str, set] = {}
    volta = 0
    while voltas is None or volta < voltas:
        streamers = carregar_streamers(arq)
        for s in streamers:
            if s.nome in rodando and rodando[s.nome].is_alive():
                continue
            avisar(f"De olho em {s.nome} ({s.link}).")
            t = threading.Thread(target=_gravar_sem_parar, args=(s, raiz / "blocos" / s.nome, lancamento, avisar), daemon=True)
            t.start()
            rodando[s.nome] = t
            if s.canal_twitch:
                threading.Thread(target=_chat_sem_parar, args=(s.canal_twitch, raiz / "chat" / f"{s.canal_twitch}.csv", avisar),
                                 daemon=True).start()
        analisar_novos(streamers, raiz, transcritor, vistos, avisar)
        (raiz / BATIMENTO).write_text(str(time.time()))
        volta += 1
        time.sleep(a_cada_s)

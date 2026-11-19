"""Cortar a partir de um LINK (Twitch, Kick ou YouTube), sem baixar nada à mão.

- Live acontecendo agora: grava em blocos de 20 min (streamlink) e analisa cada bloco enquanto a live roda;
  termina sozinho quando a live acaba. Candidatos em `pendentes/`.
- Live que já acabou (VOD): baixa só o trecho que importa (yt-dlp) e segue o fluxo normal.
  Padrão do LOGICA-DO-SISTEMA: 3 horas, pulando a meia hora inicial. No YouTube baixa o vídeo inteiro
  em 8 partes paralelas e corta aqui (o YouTube limita quem baixa só um trecho).
- Guarda um registro (`baixados.json`) para não baixar o mesmo trecho duas vezes.
"""
from __future__ import annotations

import json
import re
import shutil
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from .midia import rodar, rodar_ffmpeg
from .modelos import formatar_tempo

INICIO_PADRAO_S = 30 * 60
DURACAO_PADRAO_S = 3 * 3600
FORMATO = "bv*[height<=1080]+ba/b[height<=1080]/b"


class ErroLink(RuntimeError):
    pass


# ------------------------------------------------------------------- ler o link
def plataforma(url: str) -> str:
    host = urlparse(url if "://" in url else "https://" + url).netloc.lower()
    for nome, dominio in (("twitch", "twitch.tv"), ("kick", "kick.com"), ("youtube", "youtube.com"), ("youtube", "youtu.be")):
        if host == dominio or host.endswith("." + dominio):
            return nome
    raise ErroLink(f"Link não reconhecido: {url}. Aceito Twitch, Kick e YouTube.")


def nome_do_canal(url: str) -> str:
    """'https://www.twitch.tv/Fulano/videos/123' -> 'fulano'; YouTube '@Fulano' -> 'fulano'."""
    u = urlparse(url if "://" in url else "https://" + url)
    partes = [p for p in u.path.split("/") if p]
    if plataforma(url) == "youtube":
        arroba = next((p[1:] for p in partes if p.startswith("@")), None)
        if arroba:
            return arroba.lower()
        video = parse_qs(u.query).get("v", [None])[0] or (partes[-1] if partes else None)
        return f"youtube-{video}" if video else "youtube"
    if not partes or partes[0] == "videos":
        return plataforma(url)
    return partes[0].lower()


def ler_duracao(texto: str) -> float:
    """'30m', '3h', '1h30m', '90s', '1:30:00' ou '5400' -> segundos."""
    t = texto.strip().lower()
    if ":" in t or re.fullmatch(r"[\d.]+", t):
        from .modelos import ler_tempo

        return ler_tempo(t)
    partes = re.findall(r"([\d.]+)\s*([hms])", t)
    if not partes or "".join(n + u for n, u in partes) != t.replace(" ", ""):
        raise ValueError(f"duração inválida: {texto!r} (use 30m, 3h, 1h30m ou 1:30:00)")
    return sum(float(n) * {"h": 3600, "m": 60, "s": 1}[u] for n, u in partes)


def trecho(inicio_s: float, duracao_s: float, total_s: Optional[float]) -> Optional[tuple]:
    """(inicio, fim) do pedaço a baixar, ou None para baixar tudo.

    Se a live é mais curta que o começo pulado + 10 min, começa do zero.
    """
    if total_s is not None and total_s <= inicio_s + 600:
        inicio_s = 0.0
    fim = inicio_s + duracao_s
    if total_s is not None:
        fim = min(fim, total_s)
        if inicio_s <= 0 and fim >= total_s:
            return None
    return (inicio_s, fim)


def secao_yt_dlp(t: tuple) -> str:
    return f"*{formatar_tempo(t[0])}-{formatar_tempo(t[1])}"


# ------------------------------------------------------------------- comandos
def comando_info(url: str) -> List[str]:
    return ["yt-dlp", "-J", "--no-playlist", "--no-warnings", url]


def comando_baixar(url: str, destino: Path, secao: Optional[str]) -> List[str]:
    cmd = ["yt-dlp", "--no-playlist", "-N", "8", "-f", FORMATO, "--merge-output-format", "mp4",
           "-o", str(destino), "--no-part"]
    if secao:
        cmd += ["--download-sections", secao]
    return cmd + [url]


def informacoes(url: str) -> dict:
    r = rodar(comando_info(url))
    if r.returncode != 0:
        raise ErroLink(f"yt-dlp não conseguiu ler o link: {(r.stderr or '').strip()[-400:]}")
    return json.loads(r.stdout)


def esta_ao_vivo(url: str, info: Optional[dict] = None) -> bool:
    if info is not None:
        return info.get("live_status") == "is_live" or bool(info.get("is_live"))
    if shutil.which("streamlink"):
        from .ao_vivo import esta_ao_vivo as pelo_streamlink

        return pelo_streamlink(url)
    return False


# ------------------------------------------------------------------- registro
def _registro(pasta: Path) -> Dict[str, str]:
    arq = pasta / "baixados.json"
    return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}


def _guardar_registro(pasta: Path, chave: str, arquivo: Path) -> None:
    reg = _registro(pasta)
    reg[chave] = arquivo.name
    (pasta / "baixados.json").write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")


# ------------------------------------------------------------------- VOD
def baixar_vod(
    url: str, pasta: Path, inicio_s: float = INICIO_PADRAO_S, duracao_s: float = DURACAO_PADRAO_S,
    tudo: bool = False, info: Optional[dict] = None, avisar: Callable[[str], None] = print,
) -> Path:
    """Baixa o trecho da live gravada para `pasta` e devolve o arquivo .mp4."""
    from .render import slug

    info = info if info is not None else informacoes(url)
    if esta_ao_vivo(url, info):
        raise ErroLink("Esse link está ao vivo agora: use o modo ao vivo (o comando `link` faz isso sozinho).")
    total = info.get("duration")
    t = None if tudo else trecho(inicio_s, duracao_s, float(total) if total else None)
    titulo = info.get("title") or info.get("id") or "live"
    destino = pasta / f"{slug(nome_do_canal(url) + '-' + str(titulo), 60)}.mp4"
    chave = f"{info.get('webpage_url') or url}|{t}"
    feito = _registro(pasta).get(chave)
    if feito and (pasta / feito).exists():
        avisar(f"Esse trecho já foi baixado: {feito}. Não vou baixar de novo.")
        return pasta / feito

    pasta.mkdir(parents=True, exist_ok=True)
    faixa = "a live inteira" if t is None else f"de {formatar_tempo(t[0])} até {formatar_tempo(t[1])}"
    avisar(f"Baixando {faixa} de '{titulo}'... (pode demorar; deixe o PC ligado)")
    if t is not None and plataforma(url) == "youtube":
        inteiro = pasta / ".baixando" / "inteiro.mp4"
        inteiro.parent.mkdir(exist_ok=True)
        _baixar(comando_baixar(url, inteiro, None))
        rodar_ffmpeg(["-ss", f"{t[0]:.3f}", "-to", f"{t[1]:.3f}", "-i", inteiro, "-c", "copy",
                      "-movflags", "+faststart", destino])
        shutil.rmtree(inteiro.parent, ignore_errors=True)
    else:
        _baixar(comando_baixar(url, destino, secao_yt_dlp(t) if t else None))
    if not destino.exists():
        raise ErroLink("O download terminou mas o arquivo não apareceu. Rode de novo.")
    _guardar_registro(pasta, chave, destino)
    avisar(f"Pronto: {destino.name}")
    return destino


def _baixar(cmd: List[str]) -> None:
    r = rodar(cmd, capturar=False)  # mostra o progresso do yt-dlp na tela
    if r.returncode != 0:
        raise ErroLink("O download falhou (link privado, apagado ou só para inscritos?).")


# ------------------------------------------------------------------- AO VIVO
def acompanhar_live(
    url: str, pasta: Path, arroba: str, permissao: str, idioma: str, transcritor,
    camera: Optional[str] = None, avisar: Callable[[str], None] = print,
) -> int:
    """Grava e analisa a live até ela acabar. Devolve quantos candidatos foram para `pendentes/`."""
    from dataclasses import asdict

    from .ao_vivo import Streamer, gravar_ate_acabar, ler_chat_twitch, loop_analisador

    if not shutil.which("streamlink"):
        raise ErroLink("Para live ao vivo falta o streamlink. Windows: winget install --id Streamlink.Streamlink -e")
    s = Streamer(nome=nome_do_canal(url), link=url, arroba=arroba or "@" + nome_do_canal(url),
                 idioma="" if idioma == "auto" else idioma, camera=camera, permissao=permissao)
    _salvar_streamer(pasta / "streamers.json", s, asdict)

    gravando = threading.Thread(target=gravar_ate_acabar, args=(s, pasta / "blocos" / s.nome, avisar), daemon=True)
    gravando.start()
    if s.canal_twitch:
        def chat():
            try:
                ler_chat_twitch(s.canal_twitch, pasta / "chat" / f"{s.canal_twitch}.csv", lambda: not gravando.is_alive())
            except OSError as e:  # sem chat não para nada: só perde essa nota
                avisar(f"Chat da Twitch indisponível ({e}); sigo só com voz e volume.")
        threading.Thread(target=chat, daemon=True).start()
    avisar("Analisando cada bloco de 20 min assim que fecha. Deixe o PC ligado até a live acabar.")
    return loop_analisador([s], pasta, transcritor, avisar=avisar, continuar=gravando.is_alive)


def _salvar_streamer(arquivo: Path, s, asdict) -> None:
    """Põe (ou atualiza) o streamer no streamers.json da pasta, para o `ao-vivo cortar` achar depois."""
    lista = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else []
    lista = [x for x in lista if x.get("nome") != s.nome] + [asdict(s)]
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(lista, ensure_ascii=False, indent=2), encoding="utf-8")

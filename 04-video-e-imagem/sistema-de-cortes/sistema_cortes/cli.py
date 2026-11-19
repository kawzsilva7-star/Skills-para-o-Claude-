"""Linha de comando. Cada passo da skill é um comando; o estado fica em cortes/<live>/estado.json.

Fluxo da live gravada (PDFs):
  diagnostico -> preparar -> permissao -> analisar -> (Claude escreve títulos com `ajustar`) -> lista
  -> PARE (dono aprova) -> aprovar -> quadros -> camera -> estilo -> cortar -> longo -> verificar

Fluxo ao vivo (LOGICA-DO-SISTEMA):
  ao-vivo gravar / ao-vivo chat / ao-vivo analisar -> avaliar (nota 0-10) -> ao-vivo cortar
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

from . import projeto as prj
from .config import ESTILOS_LEGENDA, ESTILOS_TITULO, REGRAS
from .layout import Retangulo
from .modelos import Momento, Palavra, formatar_tempo, ler_tempo
from .regras import (
    Assinatura, RegraViolada, assinar_original, conferir_original, exigir_aprovacao,
    exigir_permissao, garantir_saida_segura, registrar_permissao,
)


def _p(msg: str) -> None:
    print(msg, flush=True)


# ------------------------------------------------------------------ apoio
def _transcritor(gpu: bool = False, modelo: str = "small"):
    from .transcricao import TranscritorWhisper

    return TranscritorWhisper(modelo, gpu=gpu)


def _arquivo_palavras(pr: prj.Projeto, m: Momento) -> Path:
    return pr.analise / f"momento_{int(m.pico):06d}.json"


def _palavras_do_corte(pr: prj.Projeto, m: Momento, estado: dict) -> List[Palavra]:
    """Palavras finas (beam 5) do corte. Se o tempo foi ajustado para fora do que já foi transcrito, transcreve de novo."""
    from .transcricao import carregar_palavras, retranscrever_trecho, salvar_palavras

    arq = _arquivo_palavras(pr, m)
    if arq.exists():
        palavras, extra = carregar_palavras(arq)
        if extra.get("de", 1e9) <= m.inicio and extra.get("ate", -1) >= m.fim:
            return palavras
    de, ate = max(0.0, m.inicio - 2), m.fim + 2
    palavras = retranscrever_trecho(pr.analise / "audio.wav", de, ate, _transcritor(), estado.get("lingua"))
    salvar_palavras(palavras, arq, {"de": de, "ate": ate})
    return palavras


def mostrar_lista(estado: dict) -> None:
    ms, rs = prj.momentos(estado), prj.momentos(estado, "reservas")
    if not ms:
        _p("Nenhum momento ainda. Rode `analisar`.")
        return
    _p(f"Momentos ({len(ms)}), do mais forte ao mais fraco:")
    for i, m in enumerate(ms, 1):
        _p(f"{i}. {formatar_tempo(m.inicio)} → {formatar_tempo(m.fim)} · {m.tipo} · {m.duracao:.0f} s · "
           f"{m.descricao or '(sem descrição)'} · Título: {m.titulo or '(sem título)'}")
        _p(f"     fala: {m.trecho[:300]}")
        for a in m.avisos:
            _p(f"     ⚠ {a}")
    if rs:
        _p(f"Reservas ({len(rs)}):")
        for i, m in enumerate(rs, 1):
            _p(f"R{i}. {formatar_tempo(m.inicio)} → {formatar_tempo(m.fim)} · {m.tipo} · {m.duracao:.0f} s · fala: {m.trecho[:160]}")
    else:
        _p("Reservas: nenhuma (a live não tem mais momentos bons).")
    _p("PARE: mostre esta lista ao dono e espere o OK. Tirar spoiler, cutscene e trecho com rádio tocando.")


# ------------------------------------------------------------------ comandos: live gravada
def cmd_diagnostico(a) -> int:
    from .ambiente import diagnostico

    d = diagnostico()
    _p(json.dumps(d, ensure_ascii=False, indent=2))
    return 0 if not d["instalar"] else 1


def cmd_preparar(a) -> int:
    from .ambiente import achar_python, preparar_venv

    py = achar_python()
    if not py:
        _p("Python 3.9+ não encontrado. Rode `diagnostico` para ver o comando de instalação.")
        return 1
    pasta_skill = Path(__file__).resolve().parents[1]  # um .venv só, dentro da skill (serve para todas as lives)
    _p(f"Usando {' '.join(py)}. Criando .venv e instalando faster-whisper e numpy (uma vez só)...")
    _p(f"Pronto: {preparar_venv(pasta_skill, py)}")
    return 0


def cmd_permissao(a) -> int:
    pr = prj.abrir(Path(a.pasta), a.video)
    estado = registrar_permissao(pr.carregar(), a.origem)
    pr.salvar(estado)
    _p(f"Permissão registrada: {a.origem}")
    return 0


def cmd_analisar(a) -> int:
    from .limites import aplicar_limites
    from .midia import extrair_wav, sondar
    from .momentos import achar_momentos, conferir_reacao_fina
    from .transcricao import detectar_lingua, retranscrever_trecho, salvar_palavras, transcrever_live
    from .volume import medir_volume

    import numpy as np

    comeco = time.monotonic()
    pr = prj.abrir(Path(a.pasta), a.video)
    estado = pr.carregar()
    exigir_permissao(estado)
    assin = assinar_original(pr.video)
    estado["assinatura_original"] = asdict(assin)
    info = sondar(pr.video)
    if not info.tem_audio:
        raise RegraViolada("O vídeo não tem áudio: não dá para achar gritos nem reações.")
    _p(f"Live: {pr.video.name} · {formatar_tempo(info.duracao)} · {info.largura}x{info.altura}")

    _p("Extraindo o áudio (WAV mono 16 kHz)...")
    wav = extrair_wav(pr.video, pr.analise / "audio.wav")
    tr = _transcritor(a.gpu, a.modelo)
    lingua = None if a.lingua == "auto" else a.lingua
    if lingua is None:
        lingua, prob = detectar_lingua(wav, info.duracao, tr)
        _p(f"Idioma da live: {lingua} ({prob:.0%} de certeza). Se estiver errado, rode de novo com --lingua.")
    estado["lingua"] = lingua

    _p("Assistindo a live inteira (transcrição rápida)...")
    palavras = transcrever_live(wav, pr.analise / "transcricao.json", tr, lingua, info.duracao, avisar=_p)
    _p("Medindo o volume de cada segundo...")
    volume = medir_volume(wav, pr.analise / "volume.npy")
    n = int(info.duracao) + 1
    if len(volume) < n:
        volume = np.pad(volume, (0, n - len(volume)), constant_values=-70.0)

    principais, reservas = achar_momentos(palavras, volume, a.quantos, lingua)
    _p("Transcrevendo de novo, com mais precisão, em volta de cada momento...")
    for m in principais + reservas:
        de, ate = max(0.0, m.pico - 30), min(info.duracao, m.pico + 45)
        finas = retranscrever_trecho(wav, de, ate, tr, lingua, beam=5)
        salvar_palavras(finas, _arquivo_palavras(pr, m), {"de": de, "ate": ate})
        conferir_reacao_fina(m, finas, lingua)
        aplicar_limites(m, finas, info.duracao, lingua)
    if len(principais) < a.quantos:
        _p(f"Atenção: pedi {a.quantos}, mas a live só tem {len(principais)} momentos bons. Não vou inventar.")
    prj.guardar_momentos(estado, principais)
    prj.guardar_momentos(estado, reservas, "reservas")
    estado["aprovado"] = False
    estado["quantos"] = a.quantos
    pr.salvar(estado)
    conferir_original(pr.video, assin)
    _p(f"Análise em {(time.monotonic() - comeco) / 60:.1f} min.")
    _p("Agora o Claude lê a fala de cada momento e escreve título (até 40 letras) e descrição com `ajustar`.")
    mostrar_lista(estado)
    return 0


def cmd_lista(a) -> int:
    mostrar_lista(prj.abrir(Path(a.pasta), a.video).carregar())
    return 0


def _indice(texto: str, total: int) -> int:
    i = int(texto) - 1
    if not 0 <= i < total:
        raise ValueError(f"número {texto} não existe na lista (1 a {total})")
    return i


def cmd_ajustar(a) -> int:
    pr = prj.abrir(Path(a.pasta), a.video)
    estado = pr.carregar()
    ms, rs = prj.momentos(estado), prj.momentos(estado, "reservas")
    for item in a.titulo or []:
        k, _, txt = item.partition("=")
        txt = txt.strip()
        if len(txt) > REGRAS.titulo_max_letras:
            raise ValueError(f"Título {k} tem {len(txt)} letras (máx {REGRAS.titulo_max_letras}): {txt}")
        ms[_indice(k, len(ms))].titulo = txt
    for item in a.descricao or []:
        k, _, txt = item.partition("=")
        ms[_indice(k, len(ms))].descricao = txt.strip()
    for item in a.tempo or []:
        k, _, faixa = item.partition("=")
        ini, _, fim = faixa.partition("-")
        m = ms[_indice(k, len(ms))]
        m.inicio, m.fim = ler_tempo(ini), ler_tempo(fim)
        if not REGRAS.corte_min_s <= m.duracao <= REGRAS.corte_max_s:
            _p(f"Atenção: corte {k} ficou com {m.duracao:.0f} s (regra: 20 a 60 s).")
    for k in a.reserva or []:
        r = rs.pop(_indice(k, len(rs)))
        ms.append(r)
    for k in sorted({_indice(x, len(ms)) for x in (a.tirar or [])}, reverse=True):
        ms.pop(k)
    prj.guardar_momentos(estado, ms)
    prj.guardar_momentos(estado, rs, "reservas")
    estado["aprovado"] = False  # mudou a lista: precisa de OK de novo
    pr.salvar(estado)
    mostrar_lista(estado)
    return 0


def cmd_aprovar(a) -> int:
    pr = prj.abrir(Path(a.pasta), a.video)
    estado = pr.carregar()
    exigir_permissao(estado)
    ms = prj.momentos(estado)
    sem_titulo = [str(i) for i, m in enumerate(ms, 1) if not m.titulo]
    if not ms:
        raise RegraViolada("Lista vazia.")
    if sem_titulo:
        raise RegraViolada(f"Faltam títulos nos momentos {', '.join(sem_titulo)} (use `ajustar --titulo N=...`).")
    estado["aprovado"] = True
    pr.salvar(estado)
    _p(f"Aprovados {len(ms)} momentos. Próximo: `quadros` e `camera`.")
    return 0


def cmd_quadros(a) -> int:
    from .midia import quadros_para_achar_camera, sondar

    pr = prj.abrir(Path(a.pasta), a.video)
    q = quadros_para_achar_camera(pr.video, sondar(pr.video).duracao, pr.analise / "quadros")
    _p("Olhe os quadros e ache a câmera (x, y, largura, altura) POR DENTRO da moldura:")
    for x in q:
        _p(f"  {x}")
    return 0


def cmd_camera(a) -> int:
    pr = prj.abrir(Path(a.pasta), a.video)
    estado = pr.carregar()
    if a.sem_camera:
        estado["camera"], estado["jogo"] = None, None
        _p("Layout sem câmera: live inteira no meio com fundo desfocado.")
    else:
        from .layout import jogo_automatico
        from .midia import sondar

        cam = Retangulo.de_texto(a.area)
        info = sondar(pr.video)
        if not cam.cabe_em(info.largura, info.altura):
            raise ValueError(f"Câmera {cam.texto()} fora do quadro {info.largura}x{info.altura}")
        jogo = Retangulo.de_texto(a.jogo) if a.jogo else jogo_automatico(info.largura, info.altura, cam)
        estado["camera"], estado["jogo"] = cam.texto(), jogo.texto()
        _p(f"Câmera: {cam.texto()} · recorte do jogo: {jogo.texto()} (troque com --jogo se a ação ficar de fora)")
    pr.salvar(estado)
    return 0


def cmd_estilo(a) -> int:
    pr = prj.abrir(Path(a.pasta), a.video)
    estado = pr.carregar()
    if a.legenda:
        estado["estilo_legenda"] = a.legenda
    if a.titulo:
        estado["estilo_titulo"] = a.titulo
    if a.credito is not None:
        estado["credito"] = a.credito.strip() or None
    pr.salvar(estado)
    _p(f"Legenda: {estado.get('estilo_legenda', 'destaque')} · título: {estado.get('estilo_titulo', 'contorno')} · "
       f"crédito: {estado.get('credito') or '(nenhum — a regra pede o @ do streamer na tela ou na legenda)'}")
    return 0


def cmd_cortar(a) -> int:
    from .midia import sondar
    from .render import OpcoesCorte, nome_do_corte, renderizar_corte

    comeco = time.monotonic()
    pr = prj.abrir(Path(a.pasta), a.video)
    estado = pr.carregar()
    exigir_permissao(estado)
    exigir_aprovacao(estado)
    if "camera" not in estado:
        raise RegraViolada("Antes de cortar: rode `quadros`, olhe e depois `camera --area x,y,w,h` ou `camera --sem-camera`.")
    assin = Assinatura(**estado["assinatura_original"]) if "assinatura_original" in estado else assinar_original(pr.video)
    info = sondar(pr.video)
    ms = prj.momentos(estado)
    cam = Retangulo.de_texto(estado["camera"]) if estado.get("camera") else None
    jogo = Retangulo.de_texto(estado["jogo"]) if estado.get("jogo") else None
    estilo_leg = estado.get("estilo_legenda", "destaque")
    estilo_tit = estado.get("estilo_titulo", "contorno")
    trabalhos = []
    if estilo_leg == "todos":
        for nome in ESTILOS_LEGENDA:
            trabalhos.append((1, ms[0], nome, nome))
        _p("Estilo 'todos': gerando o 1º corte em cada estilo para o dono escolher.")
    else:
        trabalhos = [(i, m, estilo_leg, "") for i, m in enumerate(ms, 1)]

    resultados = []
    for n, m, est, sufixo in trabalhos:
        t0 = time.monotonic()
        palavras = _palavras_do_corte(pr, m, estado)
        nome = nome_do_corte(n, m.titulo, sufixo)
        garantir_saida_segura(pr.saida / nome, pr.video)
        _p(f"Cortando {nome} ({m.duracao:.0f} s)...")
        saida, lufs, pico = renderizar_corte(
            pr.video, info, m, palavras, pr.saida, nome,
            OpcoesCorte(est, estilo_tit, cam, jogo, estado.get("credito")),
        )
        resultados.append((saida, lufs, pico))
        _p(f"  pronto em {time.monotonic() - t0:.0f} s · {lufs:.1f} LUFS · pico real {pico:.1f} dB")

    if estilo_leg != "todos":
        linhas = []
        for i, m in enumerate(ms, 1):
            linhas += [f"Corte {i}: {m.titulo}", m.descricao, ""]
            if estado.get("credito"):
                linhas.insert(-1, f"Créditos: {estado['credito']}")
        (pr.saida / "titulos.txt").write_text("\n".join(linhas), encoding="utf-8")
    conferir_original(pr.video, assin)
    _p(f"Tudo em {pr.saida} · {(time.monotonic() - comeco) / 60:.1f} min. O original não foi alterado.")
    if estilo_leg == "todos":
        _p("PARE: o dono escolhe o estilo; depois `estilo --legenda <nome>` e `cortar` de novo.")
    return 0


def cmd_longo(a) -> int:
    from .longo import montar_video_longo

    pr = prj.abrir(Path(a.pasta), a.video)
    estado = pr.carregar()
    exigir_permissao(estado)
    exigir_aprovacao(estado)
    saida = pr.saida / "melhores-momentos-youtube.mp4"
    garantir_saida_segura(saida, pr.video)
    _p("Montando o vídeo longo 16:9 (momentos na ordem da live, fade de 0,5 s)...")
    _, lufs, pico = montar_video_longo(pr.video, prj.momentos(estado), saida)
    _p(f"{saida} · {lufs:.1f} LUFS · pico real {pico:.1f} dB")
    _p("Lembrete: compilação colada não é monetizada. Grave sua narração entre os momentos.")
    return 0


def cmd_verificar(a) -> int:
    from .verificacao import verificar

    pr = prj.abrir(Path(a.pasta), a.video)
    ruins = 0
    for arq in sorted(pr.saida.glob("*.mp4")):
        vertical = arq.name.startswith("corte")
        rel = verificar(arq, vertical, arq.with_suffix(".ass"), pr.saida / "verificacao")
        _p(rel.linha())
        if rel.quadro:
            _p(f"   olhe o quadro: {rel.quadro}")
        ruins += not rel.ok
    return 1 if ruins else 0


# ------------------------------------------------------------------ link
def cmd_link(a) -> int:
    """Link da Twitch/Kick/YouTube: ao vivo grava e analisa; VOD baixa o trecho e analisa."""
    from . import link as lk

    pasta = Path(a.pasta)
    registrar_permissao({}, a.permissao)  # valida antes de baixar qualquer coisa
    lk.plataforma(a.url)
    info = None
    if shutil.which("yt-dlp"):
        try:
            info = lk.informacoes(a.url)
        except lk.ErroLink:
            info = None  # canal offline ou link de canal: o streamlink decide abaixo
    ao_vivo = lk.esta_ao_vivo(a.url, info) if info is not None else lk.esta_ao_vivo(a.url)
    if ao_vivo:
        _p(f"{a.url} está AO VIVO. Vou gravar e analisar até a live acabar.")
        n = lk.acompanhar_live(a.url, pasta, a.arroba or "", a.permissao, a.lingua,
                               _transcritor(a.gpu, a.modelo), a.camera, avisar=_p, info=info)
        _p(f"A live acabou. {n} candidato(s) em {pasta / 'pendentes'}.")
        _p("PARE: dê a nota de cada um com `avaliar --pendente ...` e corte os de nota 7+ com `ao-vivo cortar`.")
        _p("Para completar o começo que a gravação não pegou: mande o link do VOD NESTA MESMA PASTA.")
        return 0
    if info is None:
        if not shutil.which("yt-dlp"):
            raise RegraViolada("Para baixar live gravada falta o yt-dlp. Windows: winget install --id yt-dlp.yt-dlp -e")
        raise RegraViolada("Esse canal não está ao vivo e o link não é de um vídeo. Mande o link do VOD.")
    inicio, duracao, tudo = lk.ler_duracao(a.inicio), lk.ler_duracao(a.duracao), a.tudo
    live = lk.ler_live(pasta)
    if live and not a.tudo:
        fim = lk.fim_do_comeco(live, info)
        if fim is None:
            _p("A gravação ao vivo pegou a live desde o começo: não falta nada para completar.")
            return 0
        _p(f"Esta pasta já acompanhou a live ao vivo. Vou baixar só o começo que faltou "
           f"(00:00:00 até {formatar_tempo(fim)}) e achar os momentos dele.")
        inicio, duracao, tudo = 0.0, fim, False
    arquivo = lk.baixar_vod(a.url, pasta, inicio, duracao, tudo, info, avisar=_p)
    pr = prj.abrir(pasta, arquivo.name)
    estado = registrar_permissao(pr.carregar(), a.permissao)
    estado["link"] = a.url
    if a.arroba:
        estado["credito"] = a.arroba
    pr.salvar(estado)
    return cmd_analisar(argparse.Namespace(pasta=a.pasta, video=arquivo.name, quantos=a.quantos,
                                           lingua=a.lingua, modelo=a.modelo, gpu=a.gpu))


# ------------------------------------------------------------------ nota de qualidade
def cmd_avaliar(a) -> int:
    from .avaliacao import ITENS, decidir

    notas = {i: getattr(a, i) for i in ITENS}
    d = decidir(notas, a.so_fala)
    _p(f"Nota {d.nota}/10 → {d.destino} ({d.motivo})")
    if a.pendente:
        arq = Path(a.pendente)
        dados = json.loads(arq.read_text(encoding="utf-8"))
        dados["avaliacao"] = {"notas": notas, "nota": d.nota, "destino": d.destino, "motivo": d.motivo}
        arq.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return 0


# ------------------------------------------------------------------ ao vivo
def cmd_ao_vivo(a) -> int:
    from . import ao_vivo as av

    raiz = Path(a.pasta)
    if a.acao == "chat":
        av.ler_chat_twitch(a.canal.lower(), raiz / "chat" / f"{a.canal.lower()}.csv")
        return 0
    streamers = av.carregar_streamers(Path(a.streamers))
    if a.acao == "gravar":
        s = next((x for x in streamers if x.nome == a.nome), None)
        if not s:
            raise ValueError(f"{a.nome} não está no {a.streamers}")
        av.gravar(s, raiz / "blocos" / s.nome, a.lancamento)
    elif a.acao == "analisar":
        av.loop_analisador(streamers, raiz, _transcritor(a.gpu, a.modelo))
    elif a.acao == "cortar":
        return _cortar_pendente(a, streamers, raiz)
    return 0


def _cortar_pendente(a, streamers, raiz: Path) -> int:
    from .midia import sondar
    from .render import OpcoesCorte, nome_do_corte, renderizar_corte

    arq = Path(a.pendente)
    dados = json.loads(arq.read_text(encoding="utf-8"))
    destino = dados.get("avaliacao", {}).get("destino")
    if destino not in ("postar_agora", "fila"):
        raise RegraViolada("PARE: candidato sem nota 7+ (rode `avaliar --pendente ...` com a nota de uma pessoa).")
    if not a.titulo or len(a.titulo) > REGRAS.titulo_max_letras:
        raise ValueError("Passe --titulo com até 40 letras.")
    s = next(x for x in streamers if x.nome == dados["streamer"])
    bloco = raiz / "blocos" / s.nome / dados["bloco"]
    m = Momento(dados["pico"], dados["tipo"], dados["nota"], dados["inicio"], dados["fim"], dados["zoom_em"], a.titulo)
    palavras = [Palavra(**p) for p in dados["palavras"]]
    cam = Retangulo.de_texto(s.camera) if s.camera else None
    saida_pasta = raiz / "cortes" / s.nome
    nome = nome_do_corte(int(time.time()), a.titulo)
    saida, lufs, pico = renderizar_corte(
        bloco, sondar(bloco), m, palavras, saida_pasta, nome,
        OpcoesCorte(a.estilo, a.estilo_titulo, cam, None, f"{s.arroba}"),
    )
    _p(f"{saida} · {lufs:.1f} LUFS · pico {pico:.1f} dB · crédito {s.arroba}")
    return 0


# ------------------------------------------------------------------ parser
def criar_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sistema_cortes", description="Sistema de cortes de lives (Clube das Skills, em código).")
    p.add_argument("--pasta", default=".", help="pasta da live (padrão: a atual)")
    p.add_argument("--video", help="nome do vídeo, se houver mais de um")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("diagnostico").set_defaults(f=cmd_diagnostico)
    sub.add_parser("preparar").set_defaults(f=cmd_preparar)
    s = sub.add_parser("permissao")
    s.add_argument("--origem", required=True, help="onde a permissão está escrita")
    s.set_defaults(f=cmd_permissao)
    s = sub.add_parser("analisar")
    s.add_argument("--quantos", type=int, default=5)
    s.add_argument("--lingua", default="auto", help="auto, pt, en, es...")
    s.add_argument("--modelo", default="small")
    s.add_argument("--gpu", action="store_true", help="placa NVIDIA (padrão: processador)")
    s.set_defaults(f=cmd_analisar)
    sub.add_parser("lista").set_defaults(f=cmd_lista)
    s = sub.add_parser("ajustar")
    s.add_argument("--titulo", action="append", metavar="N=TEXTO")
    s.add_argument("--descricao", action="append", metavar="N=TEXTO")
    s.add_argument("--tempo", action="append", metavar="N=INI-FIM")
    s.add_argument("--tirar", action="append", metavar="N")
    s.add_argument("--reserva", action="append", metavar="N", help="promove a reserva RN para a lista")
    s.set_defaults(f=cmd_ajustar)
    sub.add_parser("aprovar").set_defaults(f=cmd_aprovar)
    sub.add_parser("quadros").set_defaults(f=cmd_quadros)
    s = sub.add_parser("camera")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--area", metavar="x,y,w,h")
    g.add_argument("--sem-camera", action="store_true")
    s.add_argument("--jogo", metavar="x,y,w,h")
    s.set_defaults(f=cmd_camera)
    s = sub.add_parser("estilo")
    s.add_argument("--legenda", choices=[*ESTILOS_LEGENDA, "todos"])
    s.add_argument("--titulo", choices=list(ESTILOS_TITULO))
    s.add_argument("--credito", help='ex.: "@streamer na Twitch"')
    s.set_defaults(f=cmd_estilo)
    sub.add_parser("cortar").set_defaults(f=cmd_cortar)
    sub.add_parser("longo").set_defaults(f=cmd_longo)
    sub.add_parser("verificar").set_defaults(f=cmd_verificar)

    s = sub.add_parser("link", help="link da Twitch/Kick/YouTube (ao vivo ou VOD)")
    s.add_argument("url")
    s.add_argument("--permissao", required=True, help="onde a permissão do streamer está escrita")
    s.add_argument("--arroba", help="@ do streamer para o crédito")
    s.add_argument("--quantos", type=int, default=5)
    s.add_argument("--lingua", default="auto")
    s.add_argument("--modelo", default="small")
    s.add_argument("--gpu", action="store_true")
    s.add_argument("--inicio", default="30m", help="quanto pular do começo do VOD (padrão 30m)")
    s.add_argument("--duracao", default="3h", help="quanto baixar do VOD (padrão 3h)")
    s.add_argument("--tudo", action="store_true", help="baixa o VOD inteiro")
    s.add_argument("--camera", metavar="x,y,w,h", help="posição da câmera na live (modo ao vivo)")
    s.set_defaults(f=cmd_link)

    s = sub.add_parser("avaliar", help="nota 0-2 em 5 itens (quem dá a nota é a pessoa)")
    for item in ("gancho", "virada", "entende_sozinho", "relevancia", "vontade_de_rever"):
        s.add_argument(f"--{item.replace('_', '-')}", dest=item, type=int, required=True, choices=[0, 1, 2])
    s.add_argument("--so-fala", action="store_true")
    s.add_argument("--pendente", help="arquivo .json da fila pendentes/")
    s.set_defaults(f=cmd_avaliar)

    s = sub.add_parser("ao-vivo")
    s.add_argument("acao", choices=["gravar", "chat", "analisar", "cortar"])
    s.add_argument("--streamers", default="streamers.json")
    s.add_argument("--nome")
    s.add_argument("--canal")
    s.add_argument("--lancamento", action="store_true", help="confere a cada 2 min em vez de 30")
    s.add_argument("--gpu", action="store_true")
    s.add_argument("--modelo", default="small")
    s.add_argument("--pendente")
    s.add_argument("--titulo")
    s.add_argument("--estilo", default="destaque", choices=list(ESTILOS_LEGENDA))
    s.add_argument("--estilo-titulo", default="contorno", choices=list(ESTILOS_TITULO))
    s.set_defaults(f=cmd_ao_vivo)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows: acento e "→" não quebram
    a = criar_parser().parse_args(argv)
    try:
        return a.f(a)
    except (RegraViolada, ValueError, FileNotFoundError, RuntimeError) as e:
        _p(f"PARE: {e}")
        return 2

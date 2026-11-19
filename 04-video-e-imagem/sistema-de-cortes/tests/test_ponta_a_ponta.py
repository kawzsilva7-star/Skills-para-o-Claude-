"""Roda o fluxo inteiro (analisar → aprovar → cortar → longo → verificar) numa live sintética.

O Whisper é trocado por um transcritor falso (sem baixar modelo); o ffmpeg é de verdade.
"""
import json
import subprocess
from pathlib import Path

import pytest
from conftest import TranscritorFalso, precisa_ffmpeg, roteiro

from sistema_cortes import cli
from sistema_cortes.midia import sondar

DURACAO = 150
EVENTOS = {60: "caraca mano meu deus", 112: "socorro socorro nao acredito"}


def criar_live(destino: Path) -> Path:
    """640x360, 'câmera' no canto inferior direito, voz baixa com 2 gritos (60 s e 112 s)."""
    audio = (
        "aevalsrc='0.03*sin(2*PI*220*t)*(1+5*between(t,60,62.5)+4*between(t,112,114))"
        f"|0.03*sin(2*PI*220*t)*(1+5*between(t,60,62.5)+4*between(t,112,114))':s=48000:d={DURACAO}"
    )
    video = (
        f"testsrc2=size=640x360:rate=30:duration={DURACAO}[jogo];"
        f"color=c=orange:size=150x120:rate=30:duration={DURACAO}[moldura];"
        f"smptebars=size=140x110:rate=30:duration={DURACAO}[rosto];"
        "[moldura][rosto]overlay=5:5[cam];[jogo][cam]overlay=480:230[v]"
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-filter_complex", video, "-f", "lavfi", "-i", audio,
         "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest",
         str(destino)],
        check=True,
    )
    return destino


@precisa_ffmpeg
def test_fluxo_completo(tmp_path, monkeypatch):
    live = criar_live(tmp_path / "live-teste.mp4")
    falso = TranscritorFalso(roteiro(DURACAO, EVENTOS))
    monkeypatch.setattr(cli, "_transcritor", lambda *a, **k: falso)
    rodar = lambda *args: cli.main(["--pasta", str(tmp_path), *args])

    # sem permissão, nada acontece
    assert rodar("analisar", "--quantos", "2") == 2
    assert rodar("permissao", "--origem", "teste automatizado, live sintética") == 0
    assert rodar("analisar", "--quantos", "2") == 0

    estado_arq = tmp_path / "cortes" / "live-teste" / "estado.json"
    estado = json.loads(estado_arq.read_text(encoding="utf-8"))
    ms = estado["momentos"]
    assert len(ms) == 2 and estado["lingua"] == "pt"
    picos = sorted(m["pico"] for m in ms)
    assert abs(picos[0] - 61) <= 5 and abs(picos[1] - 113) <= 5
    for m in ms:
        assert 20 <= m["fim"] - m["inicio"] <= 60
        assert m["pico"] - 20.5 <= m["inicio"] <= m["pico"] - 3

    # PARE: sem título não aprova; sem aprovar não corta
    assert rodar("aprovar") == 2
    assert rodar("cortar") == 2
    assert rodar("ajustar", "--titulo", "1=Ele não esperava por essa", "--titulo",
                 "2=O grito que acordou o prédio inteiro", "--descricao", "1=Susto no meio da fuga") == 0
    assert rodar("ajustar", "--titulo", "1=" + "x" * 41) == 2  # título > 40 letras
    assert rodar("aprovar") == 0
    assert rodar("cortar") == 2  # falta decidir a câmera
    assert rodar("camera", "--area", "485,235,140,110") == 0
    assert rodar("estilo", "--legenda", "destaque", "--titulo", "faixa", "--credito", "@streamer_teste") == 0
    assert rodar("cortar") == 0
    assert rodar("longo") == 0
    assert rodar("verificar") == 0

    saida = tmp_path / "cortes" / "live-teste"
    cortes = sorted(saida.glob("corte*.mp4"))
    assert [c.name for c in cortes] == ["corte1-ele-nao-esperava-por-essa.mp4", "corte2-o-grito-que-acordou-o-predio-inteiro.mp4"]
    for c in cortes:
        info = sondar(c)
        assert (info.largura, info.altura) == (1080, 1920) and info.tem_audio
    assert (saida / "titulos.txt").read_text(encoding="utf-8").count("@streamer_teste") == 2
    assert sondar(saida / "melhores-momentos-youtube.mp4").largura == 1920
    assert len(list((saida / "verificacao").glob("*.png"))) == 2  # o longo não tem .ass

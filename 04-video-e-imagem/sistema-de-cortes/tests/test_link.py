"""Comando link: entender o link, escolher o trecho do VOD e não baixar duas vezes (download simulado)."""
import pytest

from sistema_cortes import cli
from sistema_cortes import link as lk


@pytest.mark.parametrize("url,plat,canal", [
    ("https://www.twitch.tv/Fulano", "twitch", "fulano"),
    ("twitch.tv/fulano/videos/123", "twitch", "fulano"),
    ("https://www.twitch.tv/videos/2299", "twitch", "twitch"),
    ("https://kick.com/Ciclano", "kick", "ciclano"),
    ("https://www.youtube.com/@Beltrano/live", "youtube", "beltrano"),
    ("https://www.youtube.com/watch?v=abc123", "youtube", "youtube-abc123"),
    ("https://youtu.be/abc123", "youtube", "youtube-abc123"),
])
def test_entende_o_link(url, plat, canal):
    assert lk.plataforma(url) == plat and lk.nome_do_canal(url) == canal


def test_link_estranho_recusado():
    with pytest.raises(lk.ErroLink):
        lk.plataforma("https://exemplo.com/live")


def test_duracoes():
    assert lk.ler_duracao("30m") == 1800 and lk.ler_duracao("3h") == 10800
    assert lk.ler_duracao("1h30m") == 5400 and lk.ler_duracao("1:30:00") == 5400
    with pytest.raises(ValueError):
        lk.ler_duracao("3 horas")


def test_trecho_do_vod():
    assert lk.trecho(1800, 10800, 5 * 3600) == (1800, 12600)  # pula 30 min, pega 3 h
    assert lk.trecho(1800, 10800, 2 * 3600) == (1800, 7200)  # live menor que 3h30
    assert lk.trecho(1800, 10800, 1500) is None  # live curta: baixa inteira
    assert lk.secao_yt_dlp((1800, 12600)) == "*00:30:00-03:30:00"
    cmd = lk.comando_baixar("u", lk.Path("x.mp4"), "*00:30:00-03:30:00")
    assert cmd[cmd.index("--download-sections") + 1] == "*00:30:00-03:30:00" and "-N" in cmd


def test_baixa_uma_vez_so(tmp_path, monkeypatch):
    chamadas = []

    def falso(cmd):
        chamadas.append(cmd)
        lk.Path(cmd[cmd.index("-o") + 1]).write_bytes(b"video")

    monkeypatch.setattr(lk, "_baixar", falso)
    info = {"title": "GTA 6 dia 1!", "duration": 6 * 3600, "live_status": "was_live",
            "webpage_url": "https://www.twitch.tv/videos/1"}
    url = "https://www.twitch.tv/videos/1"
    a = lk.baixar_vod(url, tmp_path, info=info, avisar=lambda *_: None)
    b = lk.baixar_vod(url, tmp_path, info=info, avisar=lambda *_: None)
    assert a == b and a.name == "twitch-gta-6-dia-1.mp4" and len(chamadas) == 1
    assert "--download-sections" in chamadas[0]


def test_youtube_baixa_inteiro_e_corta_aqui(tmp_path, monkeypatch):
    feitos = []
    monkeypatch.setattr(lk, "_baixar", lambda cmd: (feitos.append(cmd), lk.Path(cmd[cmd.index("-o") + 1]).write_bytes(b"v")))
    monkeypatch.setattr(lk, "rodar_ffmpeg", lambda args, cwd=None: lk.Path(args[-1]).write_bytes(b"v"))
    info = {"title": "Live", "duration": 5 * 3600, "live_status": "was_live"}
    saida = lk.baixar_vod("https://www.youtube.com/watch?v=xyz", tmp_path, info=info, avisar=lambda *_: None)
    assert saida.exists() and "--download-sections" not in feitos[0]
    assert not (tmp_path / ".baixando").exists()


def test_link_ao_vivo_recusa_vod(tmp_path):
    with pytest.raises(lk.ErroLink):
        lk.baixar_vod("https://www.twitch.tv/fulano", tmp_path, info={"live_status": "is_live"})


def test_link_sem_permissao_nem_comeca(tmp_path):
    assert cli.main(["--pasta", str(tmp_path), "link", "https://www.twitch.tv/videos/1", "--permissao", " "]) == 2
    assert list(tmp_path.iterdir()) == []


def test_completar_o_comeco():
    # gravação começou 40 min depois do início da live
    live = {"gravacao_inicio": 1_000_000 + 2400, "live_inicio": 1_000_000}
    assert lk.fim_do_comeco(live, {"duration": 4 * 3600}) == 2400 + lk.FOLGA_COMECO_S
    # a hora do VOD (timestamp da Twitch) vale mais que a guardada
    assert lk.fim_do_comeco(live, {"timestamp": 1_000_000 + 600, "duration": 4 * 3600}) == 1800 + 60
    # sem hora nenhuma: total - tempo gravado
    live2 = {"gravacao_inicio": 5000, "gravacao_fim": 5000 + 3 * 3600}
    assert lk.fim_do_comeco(live2, {"duration": 4 * 3600}) == 3600 + 60
    # gravou desde o começo: nada a completar
    assert lk.fim_do_comeco({"gravacao_inicio": 1010, "live_inicio": 1000}, {"duration": 999}) is None
    with pytest.raises(lk.ErroLink):
        lk.fim_do_comeco({"gravacao_inicio": 5000}, {})


def test_vod_na_mesma_pasta_baixa_so_o_comeco(tmp_path, monkeypatch):
    (tmp_path / "live.json").write_text('{"gravacao_inicio": 1002400, "live_inicio": 1000000}')
    info = {"title": "Live", "duration": 4 * 3600, "live_status": "was_live", "timestamp": 1000000}
    chamadas = []
    monkeypatch.setattr(lk, "informacoes", lambda url: info)
    monkeypatch.setattr(lk, "_baixar", lambda cmd: (chamadas.append(cmd), lk.Path(cmd[cmd.index("-o") + 1]).write_bytes(b"v")))
    monkeypatch.setattr(cli.shutil, "which", lambda x: "/bin/" + x)
    monkeypatch.setattr(cli, "cmd_analisar", lambda a: 0)
    assert cli.main(["--pasta", str(tmp_path), "link", "https://www.twitch.tv/videos/9", "--permissao", "programa de cortes"]) == 0
    secao = chamadas[0][chamadas[0].index("--download-sections") + 1]
    assert secao == "*00:00:00-00:41:00"

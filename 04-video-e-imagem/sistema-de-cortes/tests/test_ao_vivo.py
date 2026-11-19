"""Modo ao vivo: regras do streamers.json, nomes dos blocos, chat e limpeza (sem rede)."""
import json
import os
import time

import pytest

from sistema_cortes import ao_vivo as av


def _salvar(tmp_path, lista):
    arq = tmp_path / "streamers.json"
    arq.write_text(json.dumps(lista), encoding="utf-8")
    return arq


def test_streamer_sem_permissao_nao_grava(tmp_path):
    base = {"nome": "a", "link": "https://www.twitch.tv/Fulano", "arroba": "@a"}
    with pytest.raises(ValueError, match="permissão"):
        av.carregar_streamers(_salvar(tmp_path, [base]))
    ok = av.carregar_streamers(_salvar(tmp_path, [{**base, "permissao": "programa de cortes"}]))
    assert ok[0].canal_twitch == "fulano"
    with pytest.raises(ValueError, match="3"):
        av.carregar_streamers(_salvar(tmp_path, [{**base, "permissao": "ok ok ok", "nome": str(i)} for i in range(4)]))


def test_bloco_de_20_min_com_data_no_nome(tmp_path):
    cmd = av.comando_blocos(tmp_path, "fulano")
    assert cmd[cmd.index("-segment_time") + 1] == "1200" and "-c" in cmd and "copy" in cmd
    t = av.inicio_do_bloco(tmp_path / "fulano_2026-11-19_20-15-00.mkv")
    assert time.localtime(t)[:5] == (2026, 11, 19, 20, 15)
    assert av.inicio_do_bloco(tmp_path / "sem-data.mkv") is None


def test_chat_do_bloco(tmp_path):
    csv = tmp_path / "chat.csv"
    csv.write_text("1000,3\n1005,40\n2000,1\n", encoding="utf-8")
    serie = av.chat_do_bloco(csv, 1000, 10)
    assert serie[0] == 3 and serie[5] == 40 and serie.sum() == 43


def test_limpeza_de_disco(tmp_path):
    blocos, pend = tmp_path / "blocos", tmp_path / "pendentes"
    blocos.mkdir(); pend.mkdir()
    for nome in ("sem_cand.mkv", "com_cand.mkv", "velho.mkv", "nao_analisado.mkv"):
        (blocos / nome).write_bytes(b"x")
        if nome != "nao_analisado.mkv":
            (blocos / nome.replace(".mkv", "")).mkdir()
            (blocos / nome.replace(".mkv", "") / "transcricao.json").write_text("{}")
    for nome in ("com_cand.mkv", "velho.mkv"):
        (pend / f"{nome}.json").write_text(json.dumps({"bloco": nome}))
    antigo = time.time() - 7 * 3600
    os.utime(blocos / "velho.mkv", (antigo, antigo))
    apagados = {p.name for p in av.limpar(blocos, pend)}
    assert apagados == {"sem_cand.mkv", "velho.mkv"}

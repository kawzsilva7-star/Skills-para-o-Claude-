"""Testes das funções puras (rápidos, sem ffmpeg)."""
import re
from pathlib import Path

import numpy as np
import pytest
from conftest import roteiro

from sistema_cortes import avaliacao, legenda, limites, momentos
from sistema_cortes.audio import interpretar_loudnorm, interpretar_resumo_ebur128, precisa_corrigir
from sistema_cortes.config import ESTILOS_LEGENDA, LIGACAO, REGRAS
from sistema_cortes.layout import (
    Retangulo, filtro_com_camera, filtro_sem_camera, jogo_automatico, recorte_na_proporcao,
)
from sistema_cortes.longo import grafo_longo, offsets_xfade
from sistema_cortes.modelos import Momento, Palavra, formatar_tempo, ler_tempo
from sistema_cortes.regras import (
    AprovacaoPendente, PermissaoNegada, exigir_aprovacao, exigir_permissao, registrar_permissao,
    varrer_segredos,
)
from sistema_cortes.render import nome_do_corte, slug
from sistema_cortes.volume import interpretar_ebur128

PASTA_SKILL = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------- tempo e nomes
def test_tempo_ida_e_volta():
    assert formatar_tempo(5025) == "01:23:45"
    assert ler_tempo("01:23:45") == 5025
    assert ler_tempo("23:45") == 1425
    assert ler_tempo("90.5") == 90.5


def test_nome_do_corte_sem_acento():
    assert slug("Ele NÃO sabia que a polícia!") == "ele-nao-sabia-que-a-policia"
    assert nome_do_corte(1, "Caraca, mano!") == "corte1-caraca-mano.mp4"


# ---------------------------------------------------------------- volume e áudio
def test_ebur128_pega_o_maior_de_cada_segundo():
    log = "\n".join(
        f"[Parsed_ebur128_0 @ 0x1] t: {t:.5f}    TARGET:-23 LUFS    M: {m} S: -20.0     I: -20 LUFS"
        for t, m in [(0.1, "-inf"), (0.5, "-30.0"), (1.2, "-25.0"), (1.9, "-12.5"), (2.3, "-40.0")]
    )
    vol = interpretar_ebur128(log)
    assert vol.tolist() == [-30.0, -12.5, -40.0]


def test_resumo_e_loudnorm():
    log = "Summary:\n\n  Integrated loudness:\n    I:         -14.2 LUFS\n  True peak:\n    Peak:      -1.3 dBFS\n"
    assert interpretar_resumo_ebur128(log) == (-14.2, -1.3)
    j = '{\n "input_i" : "-21.81", "input_tp" : "-17.69", "input_lra" : "0.10", "input_thresh" : "-31.81",' \
        ' "output_i" : "-14.01", "normalization_type" : "dynamic", "target_offset" : "0.01"\n}'
    assert interpretar_loudnorm("lixo antes " + j)["input_i"] == -21.81


def test_quando_corrigir_volume():
    assert precisa_corrigir(-14.3, -1.5) is None
    assert precisa_corrigir(-17.0, -3.0) == 3.0
    assert precisa_corrigir(-14.0, -0.5) == 0.0  # pico alto: passa no limitador
    assert precisa_corrigir(float("-inf"), float("-inf")) is None


# ---------------------------------------------------------------- momentos
def test_grito_so_conta_6db_acima_da_fala_e_ignora_silencio():
    vol = np.full(300, -30.0, dtype=np.float32)
    fala = np.ones(300, dtype=bool)
    vol[100:160] = -70.0  # silêncio longo não pode baixar a mediana
    fala[100:160] = False
    vol[200] = -20.0  # +10 dB: grito
    vol[250] = -26.0  # +4 dB: fala animada, não é grito
    g = momentos.nota_grito(vol, fala)
    assert g[200] > 0 and g[250] == 0 and g[50] == 0
    assert np.count_nonzero(g) == 1


def test_grito_sem_voz_vale_menos():
    vol = np.full(300, -30.0, dtype=np.float32)
    fala = np.ones(300, dtype=bool)
    vol[100] = vol[200] = -18.0
    fala[200] = False
    g = momentos.nota_grito(vol, fala)
    assert g[200] == pytest.approx(g[100] * REGRAS.peso_sem_fala)


def test_reacoes_pt_e_en():
    ps = [Palavra(i, i + 0.3, w) for i, w in enumerate(
        ["Caraca", "mano", "corre", "corre", "kkkkkk", "não", "acredito!", "normal"])]
    motivos = [m for _, _, m in momentos.achar_reacoes(ps, "pt")]
    assert "caraca" in motivos and "mano" in motivos and "nao acredito" in motivos
    assert "risada" in motivos and "repetiu 'corre'" in motivos and "exclamação" in motivos
    en = [Palavra(i, i + 0.3, w) for i, w in enumerate(["No", "way", "bro", "LMAO"])]
    assert {m for _, _, m in momentos.achar_reacoes(en, "en")} >= {"no way", "bro", "risada"}


def test_picos_nao_se_sobrepoem_e_nao_inventa():
    nota = np.zeros(1000)
    nota[[100, 120, 500, 900]] = [5, 4, 3, 0.5]
    assert momentos.escolher_picos(nota, 10, 45, 1.0) == [100, 500]


def test_chat_compensa_atraso():
    chat = np.ones(100)
    chat[60] = 50  # o chat explode 10 s depois do momento (50)
    assert int(np.argmax(momentos.nota_chat(chat, 100, atraso_s=10))) == 50


def test_achar_momentos_ponta_a_ponta_sem_ffmpeg():
    pal = roteiro(400, {100: "caraca mano meu deus", 300: "socorro socorro"})
    vol = np.full(400, -30.0, dtype=np.float32)
    vol[101] = -15.0
    principais, reservas = momentos.achar_momentos(pal, vol, quantos=2, lingua="pt")
    assert len(principais) == 2
    assert abs(principais[0].pico - 101) <= 4 and "GRITO" in principais[0].tipo
    assert abs(principais[1].pico - 300) <= 5
    assert abs(principais[0].zoom_em - 100) <= 2  # zoom na palavra de reação


# ---------------------------------------------------------------- limites do corte
def test_corte_comeca_em_frase_e_respeita_tempos():
    pal = roteiro(400, {100: "caraca mano"})
    ini, fim, _ = limites.definir_corte(100.0, pal, 400)
    assert 100 - 20 - 0.3 <= ini <= 100 - 5
    assert REGRAS.corte_min_s <= fim - ini <= REGRAS.corte_max_s
    comecos = {p.inicio for f in limites.montar_frases(pal) for p in f.palavras[:1]}
    assert any(abs(ini + REGRAS.folga_inicio_s - c) < 0.25 for c in comecos)  # entrou no começo de uma frase
    seguinte = [p for p in pal if p.inicio >= fim]
    assert not seguinte or fim <= seguinte[0].inicio  # não corta a próxima palavra


def test_corte_nunca_termina_em_ligacao():
    pal = [Palavra(i * 0.4, i * 0.4 + 0.35, w) for i, w in enumerate(("olha isso aqui mano que " * 20).split())]
    for p in pal[4::5]:  # termina cada frase em "que"
        p.texto = "que"
    _, fim, _ = limites.definir_corte(20.0, pal, 60)
    ultima = [p for p in pal if p.fim <= fim][-1]
    assert momentos.normalizar(ultima.texto) not in LIGACAO["pt"]


def test_assunto_diferente_comeca_mais_perto():
    pal = [Palavra(70 + i * 0.4, 70 + i * 0.4 + 0.3, "falando") for i in range(10)]  # outro assunto
    pal += [Palavra(98 + i * 0.4, 98 + i * 0.4 + 0.3, w) for i, w in enumerate("vai vai caraca mano olha".split())]
    ini, _, avisos = limites.definir_corte(100.0, pal, 400)
    assert 100 - 5 < ini <= 100 - 0.5 or avisos


# ---------------------------------------------------------------- legenda .ass
def _eventos_leg(ass: str):
    linhas = [l for l in ass.splitlines() if l.startswith("Dialogue:") and ",Leg," in l]
    out = []
    for l in linhas:
        a, b = re.findall(r"(\d+):(\d\d):(\d\d)\.(\d\d)", l)[:2]
        conv = lambda x: int(x[0]) * 3600 + int(x[1]) * 60 + int(x[2]) + int(x[3]) / 100
        out.append((conv(a), conv(b), l))
    return out


@pytest.mark.parametrize("estilo", list(ESTILOS_LEGENDA))
def test_legenda_sem_sobreposicao_sem_duracao_zero(estilo):
    pal = roteiro(40, {10: "caraca mano porra"})
    ass, _ = legenda.gerar_ass(pal, 40.0, "Ele não sabia que a polícia estava atrás", estilo)
    evs = _eventos_leg(ass)
    assert evs
    for (a1, b1, _), (a2, _, _) in zip(evs, evs[1:]):
        assert b1 <= a2 + 1e-9
    assert all(b > a for a, b, _ in evs)
    assert "p**" in ass.lower() or estilo == "beasty" and "P**" in ass  # palavrão censurado
    assert r"\N" in ass  # título longo quebra em 2 linhas
    assert "Dialogue: 1,0:00:00.00,0:00:40.00,Tit" in ass


def test_legenda_cabe_numa_linha():
    pal = [Palavra(i, i + 0.5, "INCONSTITUCIONALISSIMAMENTE") for i in range(6)]
    for estilo in ("destaque", "karaoke", "minimal"):
        grupos = legenda.agrupar(pal, ESTILOS_LEGENDA[estilo], 900)
        assert all(len(g) == 1 for g in grupos)


def test_karaoke_soma_bate():
    pal = [Palavra(1.0, 1.3, "a"), Palavra(1.4, 1.8, "b"), Palavra(2.0, 2.5, "c")]
    ev = legenda.eventos_legenda(pal, ESTILOS_LEGENDA["karaoke"])
    assert len(ev) == 1
    soma = sum(int(x) for x in re.findall(r"\\kf(\d+)", ev[0].texto))
    assert soma == ev[0].fim_cs - ev[0].inicio_cs


def test_titulo_com_camera_vai_no_topo():
    ass, _ = legenda.gerar_ass([], 30, "Titulo", com_camera=True, credito="@streamer")
    assert ",8,40,40,90,1" in ass  # Tit: Alignment 8, MarginV 90
    assert ",2,40,40,1000,1" in ass  # Leg na emenda câmera/jogo
    assert "Cred,,0,0,0,,@streamer" in ass


# ---------------------------------------------------------------- layout
def test_recorte_nunca_estica():
    r = recorte_na_proporcao(Retangulo(1500, 700, 400, 360), 1080, 860)
    assert abs(r.w / r.h - 1080 / 860) < 0.01 and r.w <= 400 and r.h <= 360


def test_jogo_nao_pega_camera():
    cam = Retangulo(1500, 700, 400, 360)
    jogo = jogo_automatico(1920, 1080, cam)
    assert not jogo.intersecta(cam) and jogo.cabe_em(1920, 1080)
    assert abs(jogo.w / jogo.h - 1080 / 1060) < 0.01
    assert jogo.w > 900  # ainda grande


def test_filtros_tem_as_pecas_certas():
    f = filtro_com_camera(Retangulo(0, 0, 400, 300), Retangulo(500, 0, 1000, 980), "c.ass", "fontes", (2.0, 4.5))
    assert "vstack=inputs=2" in f and "unsharp=5:5:0.6" in f and "between(t,2.00,4.50)" in f
    assert "zoompan" not in f
    g = filtro_sem_camera(1920, 1080, "c.ass", "fontes", None)
    assert "boxblur" in g and "overlay=0:556" in g  # centro em y=860 (608 de altura)


# ---------------------------------------------------------------- vídeo longo
def test_offsets_do_fade():
    assert offsets_xfade([30, 20, 25], 0.5) == [29.5, 49.0]
    grafo, v, a, total = grafo_longo([Momento(0, "G", 1, 100, 130), Momento(0, "G", 1, 10, 30)], 0.5)
    assert grafo.index("trim=start=10.000") < grafo.index("trim=start=100.000")  # ordem da live
    assert total == pytest.approx(49.5) and v == "xv1"


# ---------------------------------------------------------------- avaliação
def test_nota_de_qualidade():
    tudo2 = dict.fromkeys(avaliacao.ITENS, 2)
    assert avaliacao.decidir(tudo2).destino == "postar_agora"
    assert avaliacao.decidir(tudo2, so_fala=True).destino == "reserva"
    assert avaliacao.decidir({**tudo2, "gancho": 1, "virada": 0}).destino == "fila"
    assert avaliacao.decidir(dict.fromkeys(avaliacao.ITENS, 1)).destino == "reserva"
    assert avaliacao.decidir(dict.fromkeys(avaliacao.ITENS, 0)).destino == "descartar"
    with pytest.raises(ValueError):
        avaliacao.decidir({"gancho": 3})


# ---------------------------------------------------------------- regras
def test_permissao_e_aprovacao_obrigatorias():
    with pytest.raises(PermissaoNegada):
        exigir_permissao({})
    with pytest.raises(PermissaoNegada):
        registrar_permissao({}, "  ")
    e = registrar_permissao({}, "programa de cortes da Whop, print salvo")
    exigir_permissao(e)
    with pytest.raises(AprovacaoPendente):
        exigir_aprovacao(e)


def test_skill_sem_segredos_nem_dados_pessoais():
    achados = varrer_segredos(PASTA_SKILL, permitidos={"cadastro@clubedasskills.com.br"})
    assert achados == []

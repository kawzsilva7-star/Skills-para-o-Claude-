#!/usr/bin/env python3
"""Sistema de Cortes - cortes verticais de live com legenda palavra por palavra.

Uso (rode na pasta da live, onde está o vídeo):
  python cortes.py analisar  VIDEO                  # áudio, idioma, transcrição, volume (com cache)
  python cortes.py momentos  VIDEO --n 5            # acha os momentos e grava momentos.json
  python cortes.py quadros   VIDEO                  # tira 3 quadros da live para achar a câmera
  python cortes.py cortar    VIDEO --legenda destaque --titulo contorno [--camera X,Y,L,A] [--jogo X,Y,L,A]
  python cortes.py longo     VIDEO                  # vídeo 16:9 com os aprovados, para o YouTube
  python cortes.py checar    VIDEO                  # confere tamanho, som, volume e tira 1 quadro de cada

Tudo fica em cortes/<nome-da-live>/ (análise em cortes/<nome>/analise/).
Requisitos: ffmpeg/ffprobe; para analisar/momentos: faster-whisper e numpy (.venv).
"""
import argparse, json, math, os, re, shutil, statistics, subprocess, sys, time, unicodedata, wave
from pathlib import Path

for _s in (sys.stdout, sys.stderr):  # Windows: evita erro ao imprimir acento ou "→"
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------- utilidades

def achar_programa(nome):
    env = os.environ.get("CORTES_" + nome.upper())
    if env and Path(env).exists():
        return env
    p = shutil.which(nome)
    if p:
        return p
    cands = []
    if os.name == "nt":
        la = os.environ.get("LOCALAPPDATA", "")
        cands += [Path(la) / "Microsoft/WinGet/Links" / f"{nome}.exe"]
        cands += list((Path(la) / "Microsoft/WinGet/Packages").glob(f"Gyan.FFmpeg*/*/bin/{nome}.exe"))
        cands += [Path(f"C:/ffmpeg/bin/{nome}.exe")]
    else:
        cands += [Path(f"/opt/homebrew/bin/{nome}"), Path(f"/usr/local/bin/{nome}")]
    for c in cands:
        if c.exists():
            return str(c)
    sys.exit(f"[ERRO] {nome} não encontrado. Instale (Windows: winget install Gyan.FFmpeg; Mac: brew install ffmpeg) "
             f"ou defina CORTES_{nome.upper()} com o caminho completo.")

FFMPEG, FFPROBE = None, None

def ff(args):
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-y"] + args,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stderr[-3000:])
        sys.exit("[ERRO] ffmpeg falhou.")
    return r.stderr

def sonda(arquivo):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(arquivo)],
                       stdout=subprocess.PIPE, text=True, encoding="utf-8")
    return json.loads(r.stdout or "{}")

def video_info(arquivo):
    return next(s for s in sonda(arquivo)["streams"] if s["codec_type"] == "video")

def slug(txt, maxi=40):
    t = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    if len(t) > maxi:
        t = t[:maxi + 1].rsplit("-", 1)[0] if "-" in t[:maxi + 1] else t[:maxi]
    return t.strip("-") or "corte"

def sem_acento(t):
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()

def hms(s):
    s = max(0, int(round(s)))
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"

def pastas(video):
    out = Path("cortes") / slug(Path(video).stem, 60)
    an = out / "analise"
    an.mkdir(parents=True, exist_ok=True)
    return out, an

def ler_json(p, padrao=None):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else padrao

def gravar_json(p, dados):
    Path(p).write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")

def par(n):
    return max(2, int(n) // 2 * 2)

# ---------------------------------------------------------------- whisper

_MODELO = None

def modelo(nome="small"):
    global _MODELO
    if _MODELO is None:
        from faster_whisper import WhisperModel
        print(f"Carregando o Whisper '{nome}' no processador (a 1ª vez baixa o modelo)...")
        _MODELO = WhisperModel(nome, device="cpu", compute_type="int8")
    return _MODELO

def ler_wav(caminho, ini, dur):
    import numpy as np
    with wave.open(str(caminho), "rb") as w:
        sr = w.getframerate()
        w.setpos(min(int(ini * sr), w.getnframes()))
        dados = w.readframes(int(dur * sr))
    return np.frombuffer(dados, dtype=np.int16).astype("float32") / 32768.0

def duracao_wav(caminho):
    with wave.open(str(caminho), "rb") as w:
        return w.getnframes() / w.getframerate()

def transcrever(audio, offset, idioma, beam, nome_modelo):
    segs, _ = modelo(nome_modelo).transcribe(
        audio, language=idioma, word_timestamps=True, vad_filter=True,
        condition_on_previous_text=False, beam_size=beam)
    saida = []
    for s in segs:
        pal = [{"ini": round(w.start + offset, 2), "fim": round(w.end + offset, 2), "p": w.word.strip()}
               for w in (s.words or []) if w.word.strip()]
        if pal:
            saida.append({"ini": round(s.start + offset, 2), "fim": round(s.end + offset, 2),
                          "texto": s.text.strip(), "palavras": pal})
    return saida

# ---------------------------------------------------------------- 1. analisar

def ler_volume(log, total):
    por_seg = {}
    for m in re.finditer(r"t:\s*([\d.]+)\s+TARGET:.*?M:\s*(-?[\d.]+|-inf)", log):
        t, v = float(m.group(1)), m.group(2)
        v = -120.0 if v == "-inf" else float(v)
        por_seg[int(t)] = max(por_seg.get(int(t), -120.0), v)
    return [round(por_seg.get(i, -120.0), 1) for i in range(int(math.ceil(total)))]

def cmd_analisar(a):
    out, an = pastas(a.video)
    wav = an / "audio.wav"
    if not wav.exists():
        print("Extraindo o áudio (16 kHz mono)...")
        ff(["-i", a.video, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)])
    total = duracao_wav(wav)
    print(f"Duração: {hms(total)}")

    vol_p = an / "volume.json"
    if not vol_p.exists():
        print("Medindo o volume de cada segundo (ebur128)...")
        log = ff(["-v", "info", "-nostats", "-i", str(wav), "-af", "ebur128=framelog=info", "-f", "null", "-"])
        gravar_json(vol_p, ler_volume(log, total))
    else:
        print("Volume já medido (reaproveitado).")

    tr_p = an / "transcricao.json"
    tr = ler_json(tr_p, {"idioma": a.idioma, "blocos_feitos": 0, "segmentos": []})
    if not tr.get("idioma"):
        print("Detectando o idioma em trechos com fala no meio da live...")
        melhor = (None, 0.0)
        for frac in (0.5, 0.35, 0.65, 0.2, 0.8):
            pedaco = ler_wav(wav, max(0, total * frac - 15), 30)
            _, info = modelo(a.modelo).transcribe(pedaco, vad_filter=True, beam_size=1)
            if info.language_probability > melhor[1]:
                melhor = (info.language, info.language_probability)
            if info.language_probability >= 0.8:
                break
        tr["idioma"] = melhor[0]
        print(f"Idioma detectado: {melhor[0]} (confiança {melhor[1]:.0%})"
              + ("  ← BAIXA: confirme com o dono e rode de novo com --idioma xx" if melhor[1] < 0.6 else ""))
        gravar_json(tr_p, tr)

    bloco = 600
    nblocos = int(math.ceil(total / bloco))
    if tr["blocos_feitos"] >= nblocos:
        print("Transcrição já feita (reaproveitada).")
    t0, feitos = time.time(), 0
    for i in range(tr["blocos_feitos"], nblocos):
        tr["segmentos"] += transcrever(ler_wav(wav, i * bloco, bloco), i * bloco, tr["idioma"], 1, a.modelo)
        tr["blocos_feitos"] = i + 1
        gravar_json(tr_p, tr)  # salva a cada bloco: se cair, continua de onde parou
        feitos += 1
        resta = (time.time() - t0) / feitos * (nblocos - i - 1)
        print(f"Pedaço {i + 1}/{nblocos} pronto. Faltam ~{resta / 60:.0f} min.")
    print(f"Transcrição: {sum(len(s['palavras']) for s in tr['segmentos'])} palavras, idioma {tr['idioma']}.")

# ---------------------------------------------------------------- 2. momentos

REACOES = {
    "pt": ["caraca", "mano", "meu deus", "nao acredito", "que isso", "socorro", "eita", "nossa", "mentira",
           "kkkk", "corre", "puts", "caramba", "ai meu deus", "uau", "pqp", "vai vai"],
    "en": ["no way", "bro", "oh my god", "omg", "what", "let's go", "lets go", "bruh", "lmao", "lol", "holy",
           "dude", "insane", "crazy", "run", "help", "i can't believe", "i cant believe", "wtf", "oh no"],
    "es": ["no puede ser", "wey", "guey", "dios mio", "vamos", "corre", "ayuda", "no mames", "jajaja",
           "madre mia", "increible", "hostia", "loco"],
}
CONECTORES = {
    "pt": {"e", "o", "a", "os", "as", "que", "mas", "ai", "entao", "eu", "de", "da", "do", "pra", "para", "com",
           "um", "uma", "porque", "no", "na"},
    "en": {"and", "the", "we", "so", "but", "or", "a", "an", "to", "of", "i", "because", "then", "with"},
    "es": {"y", "el", "la", "los", "las", "que", "pero", "entonces", "de", "del", "con", "un", "una", "porque"},
}
RISO = re.compile(r"^(?:(?:h[aeu]){2,}h?|k{3,}|(?:ja){2,}|(?:rs){2,}|lol|lmao)$")
MUSICA = re.compile(r"♪|\[(?:music|música|musica)\]", re.I)

def limpa(p):
    return re.sub(r"[^\w']+", "", sem_acento(p))

def pontuar(palavras, vol, idioma):
    n = len(vol)
    fala = [0] * n
    for w in palavras:
        for s in range(int(w["ini"]), min(n, int(w["fim"]) + 1)):
            fala[s] = 1
    # GRITO: compara com a mediana dos segundos COM fala em ±60 s (silêncio fica de fora)
    grito = [0.0] * n
    for s in range(n):
        viz = [vol[j] for j in range(max(0, s - 60), min(n, s + 61)) if fala[j] and vol[j] > -70]
        if len(viz) < 10:
            continue
        dif = vol[s] - statistics.median(viz)
        if dif >= 6:
            peso = 1.0 if any(fala[j] for j in range(max(0, s - 1), min(n, s + 2))) else 0.35  # barulho sem voz vale menos
            grito[s] = ((dif - 6) / 3 + 1) * peso
    # REAÇÃO: palavras-chave, riso, palavra repetida, exclamação, fala acelerada
    reac = [0.0] * n
    termos = [[limpa(x) for x in t.split()] for t in REACOES.get(idioma, []) + REACOES["en"]]
    limpas = [limpa(w["p"]) for w in palavras]
    pal_reacao = set()
    for i, w in enumerate(palavras):
        s = int(w["ini"])
        if s >= n:
            continue
        if any(limpas[i:i + len(t)] == t for t in termos):
            reac[s] += 1.0
            pal_reacao.add(i)
        if RISO.match(limpas[i]):
            reac[s] += 1.0
            pal_reacao.add(i)
        if i and len(limpas[i]) > 1 and limpas[i] == limpas[i - 1] and w["ini"] - palavras[i - 1]["fim"] < 1.5:
            reac[s] += 0.7
            pal_reacao.add(i)
        if w["p"].endswith("!"):
            reac[s] += 0.3
    ritmo = [0] * n
    for w in palavras:
        if int(w["ini"]) < n:
            ritmo[int(w["ini"])] += 1
    for s in range(n):
        janela = sum(ritmo[max(0, s - 1):s + 2]) / 3
        viz = [ritmo[j] for j in range(max(0, s - 60), min(n, s + 61)) if fala[j]]
        if len(viz) >= 10 and janela >= 1.7 * max(1, statistics.median(viz)):
            reac[s] += 0.5
    total = [grito[s] + reac[s] for s in range(n)]
    suave = [sum(total[max(0, s - 2):s + 3]) for s in range(n)]
    return grito, reac, total, suave, pal_reacao

def limites(pico, segs, idioma, minimo=20, maximo=60):
    """Começo no início de uma frase 5-20 s antes do pico; fim numa pausa depois da frase do pico;
    nunca termina em palavra de ligação e nunca passa do começo da palavra seguinte."""
    segs = [s for s in segs if s["palavras"]]
    if not segs:
        return max(0, pico - 10), pico + 15
    cand = [s["ini"] for s in segs if pico - 20 <= s["ini"] <= pico - 5]
    if cand:
        ini = min(cand, key=lambda x: abs(x - (pico - 10)))
    else:
        antes = [s["ini"] for s in segs if s["ini"] <= pico - 3]
        ini = max(antes) if antes else max(0, pico - 5)
    idx = next((i for i, s in enumerate(segs) if s["fim"] >= pico), len(segs) - 1)
    k = min(idx + 1, len(segs) - 1)
    fim = segs[k]["fim"]
    while fim - ini < minimo and k + 1 < len(segs):
        k += 1
        fim = segs[k]["fim"]
    pal = [w for s in segs for w in s["palavras"] if ini - 0.05 <= w["ini"] and w["fim"] <= fim + 0.05]
    if pal and pal[-1]["fim"] - pal[0]["ini"] > maximo:
        dentro = [w for w in pal if w["fim"] <= pal[0]["ini"] + maximo]
        corte = len(dentro) - 1
        for j in range(len(dentro) - 1, 0, -1):  # termina numa pausa (>= 0,25 s) depois do pico
            prox = pal[j + 1]["ini"] if j + 1 < len(pal) else dentro[j]["fim"] + 1
            if prox - dentro[j]["fim"] >= 0.25 and dentro[j]["fim"] > pico + 2:
                corte = j
                break
        pal = pal[:corte + 1]
    conect = CONECTORES.get(idioma, set()) | CONECTORES["en"]
    while len(pal) > 3 and limpa(pal[-1]["p"]) in conect:
        pal.pop()
    if not pal:
        return ini, fim
    todas = [w for s in segs for w in s["palavras"]]
    antes = [w["fim"] for w in todas if w["fim"] <= pal[0]["ini"]]
    depois = [w["ini"] for w in todas if w["ini"] >= pal[-1]["fim"]]
    ini = max(pal[0]["ini"] - 0.15, max(antes) if antes else 0)
    fim = min(pal[-1]["fim"] + 0.35, min(depois) if depois else pal[-1]["fim"] + 0.35)
    if fim - ini < minimo:  # pouca fala em volta: completa até 20 s sem cair no meio de uma palavra
        ini = max(0.0, min(ini, pico - 10))
        fim = max(fim, ini + minimo)
        for w in todas:
            if w["ini"] < ini < w["fim"]:
                ini = w["ini"]
            if w["ini"] < fim < w["fim"]:
                fim = w["ini"]
    return round(ini, 2), round(fim, 2)

def cmd_momentos(a):
    out, an = pastas(a.video)
    tr, vol = ler_json(an / "transcricao.json"), ler_json(an / "volume.json")
    if not tr or not vol:
        sys.exit("[ERRO] Rode antes: python cortes.py analisar VIDEO")
    idioma = tr["idioma"]
    palavras = [w for s in tr["segmentos"] for w in s["palavras"]]
    grito, reac, total, suave, pal_reacao = pontuar(palavras, vol, idioma)
    picos = []
    for s in sorted(range(len(suave)), key=lambda s: -suave[s]):
        if suave[s] < a.minimo or len(picos) >= a.n + 3:
            break
        if all(abs(s - p) >= 45 for p in picos):
            picos.append(s)
    wav = an / "audio.wav"
    momentos = []
    for pico in picos:
        jan = range(max(0, pico - 3), min(len(total), pico + 4))
        pico_fino = max(jan, key=lambda s: total[s])
        segs = None
        if not a.sem_refino:
            ini_j = max(0, pico_fino - 40)
            segs = transcrever(ler_wav(wav, ini_j, 95), ini_j, idioma, 5, a.modelo)  # 2ª passada, beam 5
        if not segs:
            segs = [s for s in tr["segmentos"] if pico_fino - 40 <= s["ini"] <= pico_fino + 55]
        ini, fim = limites(pico_fino, segs, idioma)
        if any(not (fim <= m["ini"] or ini >= m["fim"]) for m in momentos):
            continue  # sobrepõe um momento mais forte
        pal = [w for s in segs for w in s["palavras"] if w["ini"] >= ini - 0.01 and w["fim"] <= fim + 0.01]
        reac_t = [palavras[i]["ini"] for i in pal_reacao if pico_fino - 3 <= palavras[i]["ini"] <= pico_fino + 3]
        texto = " ".join(w["p"] for w in pal)
        momentos.append({
            "id": 0, "ini": ini, "fim": fim, "pico": pico_fino,
            "zoom": round(min(reac_t), 2) if reac_t else float(pico_fino),
            "tipo": "GRITO" if sum(grito[s] for s in jan) >= sum(reac[s] for s in jan) else "REAÇÃO",
            "nota": round(suave[pico], 2), "texto": texto, "palavras": pal,
            "alerta_musica": bool(MUSICA.search(texto)),
            "titulo": "", "descricao": "", "aprovado": False, "reserva": False,
        })
    momentos.sort(key=lambda m: -m["nota"])
    for i, m in enumerate(momentos, 1):
        m["id"], m["reserva"] = i, i > a.n
    gravar_json(out / "momentos.json", {"idioma": idioma, "video": a.video, "momentos": momentos})
    principais = sum(1 for m in momentos if not m["reserva"])
    if principais < a.n:
        print(f"[AVISO] Pediu {a.n}, mas a live só tem {principais} momentos bons (nota >= {a.minimo}).")
    if len(momentos) - principais < 3:
        print(f"[AVISO] Só há {len(momentos) - principais} momento(s) reserva (o ideal são 3).")
    for m in momentos:
        flag = " ⚠ MÚSICA/RÁDIO?" if m["alerta_musica"] else ""
        rot = "RESERVA " if m["reserva"] else ""
        print(f"{rot}{m['id']}. {hms(m['ini'])} → {hms(m['fim'])} · {m['tipo']} · {m['fim'] - m['ini']:.0f} s · nota {m['nota']}{flag}")
        print(f"   \"{m['texto'][:220]}\"")
    print(f"\nGravado em {out / 'momentos.json'}. Escreva titulo/descricao, mostre a lista e ESPERE o OK.")

# ---------------------------------------------------------------- 3. quadros (achar a câmera)

def cmd_quadros(a):
    out, an = pastas(a.video)
    pasta = an / "quadros-live"
    pasta.mkdir(exist_ok=True)
    dur = float(sonda(a.video)["format"]["duration"])
    v = video_info(a.video)
    for i, frac in enumerate((0.2, 0.5, 0.8), 1):
        png = pasta / f"quadro{i}.png"
        ff(["-ss", f"{dur * frac:.1f}", "-i", a.video, "-frames:v", "1", str(png)])
        print(png)
    print(f"Tamanho da live: {v['width']}x{v['height']}. Olhe os quadros e ache a câmera (x, y, largura, altura), "
          "por dentro da moldura. Na dúvida, mostre o quadro ao dono e pergunte.")

# ---------------------------------------------------------------- 4. legendas (.ass)

AMARELO, VERDE, BRANCO, PRETO, VERMELHO = "&H0000E5FF", "&H0055FF55", "&H00FFFFFF", "&H00000000", "&H002A2AE6"
TAG = lambda c: "{\\c&H" + c[4:] + "&}"  # &H00BBGGRR -> {\c&HBBGGRR&}

# (Fontsize, Primary, Secondary, Outline, Back, BorderStyle, Outline, Shadow, MarginV, máx. palavras)
LEGENDAS = {
    "destaque": (86, BRANCO, BRANCO, PRETO, PRETO, 1, 7, 3, 560, 3),
    "caixa":    (78, BRANCO, BRANCO, PRETO, PRETO, 3, 16, 0, 560, 3),
    "karaoke":  (80, AMARELO, BRANCO, PRETO, PRETO, 1, 7, 3, 560, 4),
    "beasty":   (150, BRANCO, BRANCO, PRETO, PRETO, 1, 12, 6, 520, 1),
    "minimal":  (68, BRANCO, BRANCO, "&H50000000", "&H70000000", 1, 4, 2, 580, 4),
}
TITULOS = {  # (Fontsize, Primary, Outline, BorderStyle, Outline)
    "contorno":     (74, BRANCO, PRETO, 1, 7),
    "faixa":        (68, BRANCO, VERMELHO, 3, 18),
    "caixa-branca": (68, PRETO, BRANCO, 3, 18),
}
APELIDOS = {"highlight": "destaque", "box": "caixa", "karaoke": "karaoke", "karaokê": "karaoke",
            "outline": "contorno", "stripe": "faixa", "whitebox": "caixa-branca", "white-box": "caixa-branca"}

def t_ass(t):
    cs = int(round(max(0.0, t) * 100))
    return f"{cs // 360000}:{cs % 360000 // 6000:02d}:{cs % 6000 // 100:02d}.{cs % 100:02d}"

def texto_ass(p):
    return p.replace("\\", "").replace("{", "(").replace("}", ")")

def largura(txt, fs):
    return len(txt) * fs * 0.6

def agrupar(pal, maxi, fs, caixa_alta):
    grupos, atual = [], []
    for w in pal:
        cand = atual + [w]
        txt = " ".join(x["p"] for x in cand)
        txt = txt.upper() if caixa_alta else txt
        pausa = atual and w["ini"] - atual[-1]["fim"] > 0.6
        fim_frase = atual and re.search(r"[.!?…]$", atual[-1]["p"])
        if atual and (len(cand) > maxi or largura(txt, fs) > 900 or pausa or fim_frase):
            grupos.append(atual)
            atual = [w]
        else:
            atual = cand
    if atual:
        grupos.append(atual)
    return grupos

def quebrar_titulo(t, limite):
    if len(t) <= limite:
        return t
    pals = t.split()
    k = min(range(1, len(pals)), key=lambda k: abs(len(" ".join(pals[:k])) - len(" ".join(pals[k:]))), default=1)
    return " ".join(pals[:k]) + "\\N" + " ".join(pals[k:])

def gerar_ass(pal, dur, titulo, legenda, estilo_titulo, fonte="Arial", camera=False):
    fs, pri, sec, out, back, bs, ol, sh, mv, maxi = LEGENDAS[legenda]
    tfs, tpri, tout, tbs, tol = TITULOS[estilo_titulo]
    mv_tit = 300
    limite_tit = 24
    if camera:  # título sobre a câmera, legenda na emenda câmera/jogo
        mv, mv_tit, limite_tit = 1000, 90, 22
    linhas = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2",
        "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Leg,{fonte},{fs},{pri},{sec},{out},{back},-1,0,0,0,100,100,0,0,{bs},{ol},{sh},2,40,40,{mv},1",
        f"Style: Tit,{fonte},{tfs},{tpri},{tpri},{tout},{tout},-1,0,0,0,100,100,0,0,{tbs},{tol},0,8,60,60,{mv_tit},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 1,{t_ass(0)},{t_ass(dur)},Tit,,0,0,0,,{quebrar_titulo(texto_ass(titulo), limite_tit)}",
    ]
    pal = [dict(w, p=texto_ass(w["p"])) for w in pal if 0 <= w["ini"] < dur]
    if legenda == "beasty":
        pal = [dict(w, p=re.sub(r"[^\w'À-ÿ]", "", w["p"])) for w in pal]
        pal = [w for w in pal if w["p"]]
    grupos = agrupar(pal, maxi, fs, legenda != "minimal")
    eventos = []
    cores = [AMARELO, VERDE, BRANCO]
    cont = 0
    for gi, g in enumerate(grupos):
        prox_ini = grupos[gi + 1][0]["ini"] if gi + 1 < len(grupos) else dur
        fim_grupo = min(max(g[-1]["fim"], g[-1]["ini"] + 0.3), prox_ini, dur)
        if legenda == "karaoke":
            partes = []
            for j, w in enumerate(g):
                fim_w = g[j + 1]["ini"] if j + 1 < len(g) else fim_grupo
                partes.append(f"{{\\kf{max(1, int(round((fim_w - w['ini']) * 100)))}}}{w['p'].upper()}")
            eventos.append((g[0]["ini"], fim_grupo, " ".join(partes)))
            continue
        for j, w in enumerate(g):
            fim_w = g[j + 1]["ini"] if j + 1 < len(g) else fim_grupo
            if legenda == "beasty":
                txt = TAG(cores[cont % 3]) + "{\\fscx130\\fscy130\\t(0,90,\\fscx100\\fscy100)}" + w["p"].upper()
                cont += 1
            elif legenda == "minimal":
                txt = " ".join(("{\\alpha&H00&}" if k == j else "{\\alpha&H70&}") + x["p"].lower() for k, x in enumerate(g))
            else:
                txt = " ".join((TAG(AMARELO) + x["p"].upper() + TAG(BRANCO)) if k == j else x["p"].upper()
                               for k, x in enumerate(g))
            eventos.append((w["ini"], fim_w, txt))
    # nunca duas legendas ao mesmo tempo, nunca duração zero (faz o título sumir)
    limpos = []
    for ini, fim, txt in eventos:
        if limpos and ini < limpos[-1][1]:
            limpos[-1] = (limpos[-1][0], ini, limpos[-1][2])
        if limpos and limpos[-1][1] - limpos[-1][0] < 0.05:
            limpos.pop()
        limpos.append((ini, max(fim, ini + 0.05), txt))
    for ini, fim, txt in limpos:
        fim = min(fim, dur)
        if fim - ini >= 0.05:
            linhas.append(f"Dialogue: 0,{t_ass(ini)},{t_ass(fim)},Leg,,0,0,0,,{txt}")
    return "\n".join(linhas) + "\n"

# ---------------------------------------------------------------- 5. volume -14 LUFS

def medir(arquivo):
    log = ff(["-i", str(arquivo), "-vn", "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"])
    return json.loads(log[log.rfind("{"):log.rfind("}") + 1])

def normalizar(arquivo, alvo=-14.0):
    """loudnorm em 2 passadas (linear) e correção com volume+alimiter até ±0,5 LU e pico real <= -1 dB."""
    arquivo = Path(arquivo)
    tmp = arquivo.with_suffix(".tmp.mp4")
    aud = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]
    m = medir(arquivo)
    filtro = (f"loudnorm=I={alvo}:TP=-1:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
              "linear=true,aresample=48000")
    ff(["-i", str(arquivo), "-c:v", "copy", "-af", filtro] + aud + [str(tmp)])
    tmp.replace(arquivo)
    limite = 0.84
    for _ in range(6):
        m = medir(arquivo)
        i, tp = float(m["input_i"]), float(m["input_tp"])
        if abs(i - alvo) <= 0.5 and tp <= -1.0:
            break
        if tp > -1.0:  # pico real passou: aperta o limitador e mantém o volume no alvo
            limite = max(0.6, limite - 0.05)
        ff(["-i", str(arquivo), "-c:v", "copy", "-af", f"volume={alvo - i:.2f}dB,alimiter=limit={limite:.2f}:level=0"]
           + aud + [str(tmp)])
        tmp.replace(arquivo)
    else:
        m = medir(arquivo)
        print(f"[AVISO] {arquivo.name}: não chegou no alvo depois de 6 ajustes.")
    return float(m["input_i"]), float(m["input_tp"])

# ---------------------------------------------------------------- 6. cortar

def preparar_fonte():
    Path("fontes").mkdir(exist_ok=True)
    opcoes = [("C:/Windows/Fonts/arialbd.ttf", "Arial"), ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "Arial"),
              ("/Library/Fonts/Arial Bold.ttf", "Arial"), ("/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf", "Arial"),
              ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVu Sans")]
    for caminho, nome in opcoes:
        if Path(caminho).exists():
            destino = Path("fontes") / Path(caminho).name
            if not destino.exists():
                shutil.copy(caminho, destino)
            return nome
    print("[AVISO] Nenhuma fonte em negrito encontrada; o ffmpeg vai usar a padrão.")
    return "Arial"

def caixa(txt):
    v = [int(float(x)) for x in txt.replace(" ", "").split(",")]
    if len(v) != 4:
        sys.exit("[ERRO] Use X,Y,LARGURA,ALTURA (ex.: 1500,40,380,300)")
    return v

def na_proporcao(x, y, w, h, alvo, limite_w, limite_h):
    """Corta laterais ou topo/base (centralizado) até a proporção alvo, sem esticar."""
    if w / h > alvo:
        nw = h * alvo
        x, w = x + (w - nw) / 2, nw
    else:
        nh = w / alvo
        y, h = y + (h - nh) / 2, nh
    w, h = par(min(w, limite_w)), par(min(h, limite_h))
    x, y = par(max(0, min(x, limite_w - w))), par(max(0, min(y, limite_h - h)))
    return x, y, w, h

def filtro_camera(cam, jogo, W, H, z0, z1, ass_rel):
    cx, cy, cw, ch = na_proporcao(*cam, 1080 / 860, W, H)
    if jogo:
        gx, gy, gw, gh = na_proporcao(*jogo, 1080 / 1060, W, H)
    else:  # centro da tela, altura inteira
        gx, gy, gw, gh = na_proporcao(0, 0, W, H, 1080 / 1060, W, H)
    return (
        "[0:v]split=3[a][b][c];"
        f"[a]crop={cw}:{ch}:{cx}:{cy},scale=1080:860:flags=lanczos,unsharp=5:5:0.6[cam];"
        f"[c]crop={cw}:{ch}:{cx}:{cy},scale=1242:990:flags=lanczos,crop=1080:860,unsharp=5:5:0.6[camz];"
        f"[cam][camz]overlay=0:0:enable='between(t,{z0:.2f},{z1:.2f})'[camf];"
        f"[b]crop={gw}:{gh}:{gx}:{gy},scale=1080:1060:flags=lanczos[jogo];"
        "[camf][jogo]vstack[v2];"
        f"[v2]subtitles=filename='{ass_rel}':fontsdir=fontes,format=yuv420p[v]")

def filtro_desfoque(W, H, z0, z1, ass_rel):
    alt = par(1080 * H / W)
    y = max(0, 860 - alt // 2)
    return (
        "[0:v]split=3[a][b][c];"
        "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.08[bg];"
        f"[b]scale=1080:{alt}[fg];"
        f"[c]scale=1350:-2,crop=1080:{alt}[z];"
        f"[bg][fg]overlay=0:{y}[v1];"
        f"[v1][z]overlay=0:{y}:enable='between(t,{z0:.2f},{z1:.2f})'[v2];"
        f"[v2]subtitles=filename='{ass_rel}':fontsdir=fontes,format=yuv420p[v]"), alt

def cmd_cortar(a):
    out, an = pastas(a.video)
    dados = ler_json(out / "momentos.json")
    if not dados:
        sys.exit("[ERRO] Rode antes: python cortes.py momentos VIDEO")
    aprovados = [m for m in dados["momentos"] if m.get("aprovado")]
    if not aprovados:
        sys.exit('[ERRO] Nenhum momento com "aprovado": true em momentos.json. Mostre a lista e espere o OK do dono.')
    legenda = APELIDOS.get(a.legenda, a.legenda)
    titulo_est = APELIDOS.get(a.titulo, a.titulo)
    if legenda not in LEGENDAS and legenda != "todos":
        sys.exit(f"[ERRO] Legenda: {', '.join(LEGENDAS)} ou todos")
    if titulo_est not in TITULOS:
        sys.exit(f"[ERRO] Título: {', '.join(TITULOS)}")
    fonte = preparar_fonte()
    v = video_info(a.video)
    W, H = int(v["width"]), int(v["height"])
    cam = caixa(a.camera) if a.camera else None
    jogo = caixa(a.jogo) if a.jogo else None
    print("Layout:", "câmera em cima, jogo embaixo" if cam else "live inteira com fundo desfocado")
    (an / "ass").mkdir(exist_ok=True)
    titulos_txt = []
    for n, m in enumerate(aprovados, 1):
        lista = list(LEGENDAS) if (legenda == "todos" and n == 1) else ["destaque" if legenda == "todos" else legenda]
        dur = m["fim"] - m["ini"]
        pal = [{"ini": w["ini"] - m["ini"], "fim": w["fim"] - m["ini"], "p": w["p"]} for w in m["palavras"]]
        z0 = max(0.0, m["zoom"] - m["ini"] - 0.2)
        z1 = min(dur, z0 + 2.5)
        titulo = m.get("titulo") or f"Corte {n}"
        for est in lista:
            nome = f"corte{n}-{slug(titulo)}" + (f"-{est}" if len(lista) > 1 else "")
            ass = an / "ass" / f"{nome}.ass"
            ass.write_text(gerar_ass(pal, dur, titulo, est, titulo_est, fonte, camera=bool(cam)), encoding="utf-8")
            ass_rel = ass.as_posix()  # caminho relativo: "C:" quebra o filtro subtitles
            if cam:
                filtro = filtro_camera(cam, jogo, W, H, z0, z1, ass_rel)
            else:
                filtro, alt = filtro_desfoque(W, H, z0, z1, ass_rel)
                if alt > 700:
                    print(f"[AVISO] A live não é 16:9 (altura {alt} px no vertical): confira se título/legenda cobrem a cena.")
            mp4 = out / f"{nome}.mp4"
            print(f"Cortando {mp4.name} ({dur:.0f} s, legenda {est}, título {titulo_est})...")
            ff(["-ss", f"{m['ini']:.2f}", "-to", f"{m['fim']:.2f}", "-i", a.video, "-filter_complex", filtro,
                "-map", "[v]", "-map", "0:a:0?", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(mp4)])
            i, tp = normalizar(mp4)
            print(f"   volume {i:.1f} LUFS · pico real {tp:.1f} dB")
        titulos_txt.append(f"corte{n}: {titulo}\n{m.get('descricao', '')}\n")
    (out / "titulos.txt").write_text("\n".join(titulos_txt), encoding="utf-8")
    print(f"Pronto. Cortes e titulos.txt em {out}")

# ---------------------------------------------------------------- 7. longo (YouTube)

def cmd_longo(a):
    out, an = pastas(a.video)
    dados = ler_json(out / "momentos.json") or {"momentos": []}
    aprovados = sorted([m for m in dados["momentos"] if m.get("aprovado")], key=lambda m: m["ini"])
    if not aprovados:
        sys.exit("[ERRO] Nenhum momento aprovado.")
    num, den = (video_info(a.video).get("avg_frame_rate") or "30/1").split("/")
    fps = round(float(num) / float(den or 1)) or 30
    ent, filtro, d = [], [], 0.5
    for i, m in enumerate(aprovados):
        ent += ["-ss", f"{m['ini']:.2f}", "-to", f"{m['fim']:.2f}", "-i", a.video]
        filtro.append(f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1,"
                      f"fps={fps},format=yuv420p[v{i}];[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
    va, aa = "v0", "a0"
    acum = aprovados[0]["fim"] - aprovados[0]["ini"]
    for i in range(1, len(aprovados)):
        filtro.append(f"[{va}][v{i}]xfade=transition=fade:duration={d}:offset={acum - d:.2f}[vx{i}]")
        filtro.append(f"[{aa}][a{i}]acrossfade=d={d}[ax{i}]")
        va, aa = f"vx{i}", f"ax{i}"
        acum += (aprovados[i]["fim"] - aprovados[i]["ini"]) - d
    mp4 = out / "melhores-momentos-youtube.mp4"
    print(f"Montando o vídeo longo ({len(aprovados)} momentos, ~{acum / 60:.1f} min)...")
    ff(ent + ["-filter_complex", ";".join(filtro), "-map", f"[{va}]", "-map", f"[{aa}]", "-c:v", "libx264",
              "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
              "-movflags", "+faststart", str(mp4)])
    i, tp = normalizar(mp4)
    print(f"Pronto: {mp4} · volume {i:.1f} LUFS · pico real {tp:.1f} dB")

# ---------------------------------------------------------------- 8. checar

def cmd_checar(a):
    out, an = pastas(a.video)
    (an / "quadros").mkdir(exist_ok=True)
    problemas = 0
    for mp4 in sorted(out.glob("*.mp4")):
        info = sonda(mp4)
        vs = [s for s in info["streams"] if s["codec_type"] == "video"]
        aus = [s for s in info["streams"] if s["codec_type"] == "audio"]
        w, h = int(vs[0]["width"]), int(vs[0]["height"])
        dur = float(info["format"]["duration"])
        esperado = (1920, 1080) if mp4.name.startswith("melhores-momentos") else (1080, 1920)
        avisos = []
        if (w, h) != esperado:
            avisos.append(f"tamanho {w}x{h} (esperado {esperado[0]}x{esperado[1]})")
        i = tp = float("nan")
        if not aus:
            avisos.append("SEM SOM")
        else:
            m = medir(mp4)
            i, tp = float(m["input_i"]), float(m["input_tp"])
            if abs(i + 14) > 0.5 or tp > -1.0:
                avisos.append("volume fora do alvo")
        quadro = ""
        ass = an / "ass" / (mp4.stem + ".ass")
        if ass.exists():
            leg = [l for l in ass.read_text(encoding="utf-8").splitlines() if l.startswith("Dialogue: 0,")]
            if leg:
                p = leg[len(leg) // 2].split(",")
                seg = lambda s: sum(float(x) * k for x, k in zip(s.split(":"), (3600, 60, 1)))
                png = an / "quadros" / (mp4.stem + ".png")
                ff(["-ss", f"{(seg(p[1]) + seg(p[2])) / 2:.2f}", "-i", str(mp4), "-frames:v", "1", str(png)])
                quadro = f" · quadro: {png}"
            else:
                avisos.append("sem legenda no .ass")
        problemas += bool(avisos)
        estado = "OK" if not avisos else "PROBLEMA: " + "; ".join(avisos)
        print(f"{mp4.name}: {dur:.1f} s · {w}x{h} · {i:.1f} LUFS · pico {tp:.1f} dB · {estado}{quadro}")
    print("Abra os quadros e confira se a legenda e o título aparecem." if not problemas
          else f"{problemas} arquivo(s) com problema.")

# ---------------------------------------------------------------- main

def main():
    global FFMPEG, FFPROBE
    ap = argparse.ArgumentParser(description="Sistema de Cortes: cortes verticais de live")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nome in ("analisar", "momentos", "quadros", "cortar", "longo", "checar"):
        p = sub.add_parser(nome)
        p.add_argument("video")
        p.add_argument("--modelo", default="small")
        if nome == "analisar":
            p.add_argument("--idioma", default=None, help="força o idioma (pt, en, es...)")
        if nome == "momentos":
            p.add_argument("--n", type=int, default=5)
            p.add_argument("--minimo", type=float, default=1.5, help="nota mínima de um momento bom")
            p.add_argument("--sem-refino", action="store_true", help="não retranscreve com beam 5")
        if nome == "cortar":
            p.add_argument("--legenda", default="destaque", help="destaque, caixa, karaoke, beasty, minimal ou todos")
            p.add_argument("--titulo", default="contorno", help="contorno, faixa ou caixa-branca")
            p.add_argument("--camera", help="X,Y,LARGURA,ALTURA da câmera (por dentro da moldura)")
            p.add_argument("--jogo", help="X,Y,LARGURA,ALTURA do recorte do jogo (opcional)")
    a = ap.parse_args()
    FFMPEG, FFPROBE = achar_programa("ffmpeg"), achar_programa("ffprobe")
    t0 = time.time()
    {"analisar": cmd_analisar, "momentos": cmd_momentos, "quadros": cmd_quadros, "cortar": cmd_cortar,
     "longo": cmd_longo, "checar": cmd_checar}[a.cmd](a)
    print(f"Tempo: {(time.time() - t0) / 60:.1f} min")

if __name__ == "__main__":
    main()

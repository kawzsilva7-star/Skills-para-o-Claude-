"""Todas as regras e números do sistema num lugar só.

Mudou uma regra? Mude aqui. Nenhum outro arquivo tem número "solto".
Os valores vêm dos dois PDFs do Clube das Skills (versão BR e ClipDrop em inglês).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Tuple

# ---------------------------------------------------------------- formato final
LARGURA = 1080
ALTURA = 1920
CAMERA_ALTURA = 860  # câmera em cima
JOGO_ALTURA = 1060  # jogo embaixo (860 + 1060 = 1920)
CENTRO_Y_SEM_CAMERA = 860  # centro da live inteira quando não há câmera
LARGURA_LONGO, ALTURA_LONGO = 1920, 1080

# ---------------------------------------------------------------- cores do .ass
# Estilos usam &HAABBGGRR; dentro do texto a tag usa &HBBGGRR&.
AMARELO = "&H0000E5FF"
VERDE = "&H0055FF55"
BRANCO = "&H00FFFFFF"
PRETO = "&H00000000"
VERMELHO = "&H002A2AE6"


def cor_tag(cor_estilo: str) -> str:
    """'&H0000E5FF' -> '&H00E5FF&' (formato da tag \\c dentro do texto)."""
    return "&H" + cor_estilo[4:] + "&"


@dataclass(frozen=True)
class Regras:
    # --- tamanho e começo/fim do corte
    corte_min_s: float = 20.0
    corte_max_s: float = 60.0
    antes_pico_min_s: float = 5.0
    antes_pico_max_s: float = 20.0
    antes_pico_absoluto_s: float = 3.0  # se a frase anterior é de outro assunto
    pausa_entre_frases_s: float = 0.45
    quebra_de_assunto_s: float = 2.5
    folga_inicio_s: float = 0.2  # entra um pouco antes da primeira palavra
    folga_fim_s: float = 0.25  # sai um pouco depois da última palavra
    # --- achar os momentos
    grito_db_acima: float = 6.0
    janela_mediana_s: int = 120
    peso_sem_fala: float = 0.3  # barulho do jogo sem ninguém falando vale menos
    grito_teto: float = 3.0
    suavizar_s: int = 7
    distancia_minima_s: float = 45.0
    nota_minima: float = 1.0
    reservas: int = 3
    # --- zoom
    zoom_camera: float = 1.15
    zoom_sem_camera: float = 1.25
    zoom_duracao_s: float = 2.5
    # --- legenda e título
    legenda_largura_max_px: int = 900
    titulo_max_letras: int = 40
    titulo_quebra_letras: int = 22
    ass_duracao_minima_cs: int = 5
    # --- áudio
    lufs_alvo: float = -14.0
    lufs_tolerancia: float = 0.5
    pico_verdadeiro_max_db: float = -1.0
    limitador: float = 0.84
    correcoes_max: int = 3
    # --- vídeo longo
    fade_longo_s: float = 0.5
    # --- codificação
    crf: int = 20
    preset: str = "medium"
    audio_hz: int = 48000


REGRAS = Regras()

# ---------------------------------------------------------------- estilos de legenda


@dataclass(frozen=True)
class EstiloLegenda:
    nome: str
    modo: str  # destaque | caixa | karaoke | beasty | minimal
    fontsize: int
    border_style: int
    outline: int
    shadow: int
    margin_v: int
    max_palavras: int
    maiusculas: bool
    primary: str = BRANCO
    secondary: str = BRANCO
    outline_cor: str = PRETO
    back_cor: str = PRETO


ESTILOS_LEGENDA: Dict[str, EstiloLegenda] = {
    "destaque": EstiloLegenda("destaque", "destaque", 86, 1, 7, 3, 560, 3, True),
    "caixa": EstiloLegenda("caixa", "caixa", 78, 3, 16, 0, 560, 3, True),
    "karaoke": EstiloLegenda(
        "karaoke", "karaoke", 80, 1, 7, 3, 560, 4, False, primary=AMARELO, secondary=BRANCO
    ),
    "beasty": EstiloLegenda("beasty", "beasty", 150, 1, 12, 6, 520, 1, True),
    "minimal": EstiloLegenda(
        "minimal", "minimal", 68, 1, 4, 2, 580, 4, False,
        outline_cor="&H50000000", back_cor="&H70000000",
    ),
}
ESTILO_LEGENDA_PADRAO = "destaque"
# Karaokê: o PDF fala de "caixa" só para o estilo caixa. Mantemos a grafia dos menus.
# Legenda com câmera em cima fica na emenda entre câmera e jogo.
LEGENDA_MARGIN_V_COM_CAMERA = 1000


@dataclass(frozen=True)
class EstiloTitulo:
    nome: str
    fontsize: int
    border_style: int
    outline: int
    primary: str
    outline_cor: str


ESTILOS_TITULO: Dict[str, EstiloTitulo] = {
    "contorno": EstiloTitulo("contorno", 74, 1, 7, BRANCO, PRETO),
    "faixa": EstiloTitulo("faixa", 68, 3, 18, BRANCO, VERMELHO),
    "caixa-branca": EstiloTitulo("caixa-branca", 68, 3, 18, PRETO, BRANCO),
}
ESTILO_TITULO_PADRAO = "contorno"
TITULO_MARGIN_V_SEM_CAMERA = 300
TITULO_MARGIN_V_COM_CAMERA = 90

# Crédito do streamer na tela (regra dos PDFs: "crédito sempre").
CREDITO_FONTSIZE = 44
CREDITO_MARGIN_V = 110

# ---------------------------------------------------------------- palavras
# Reações por idioma. Comparação é feita sem acento e em minúsculas.
REACOES: Dict[str, Tuple[str, ...]] = {
    "pt": (
        "caraca", "mano", "meu deus", "nao acredito", "que isso", "socorro", "eita",
        "nossa", "mentira", "caramba", "pqp", "porra", "gente", "olha isso", "ai meu deus",
    ),
    "en": (
        "no way", "bro", "oh my god", "omg", "what", "lets go", "bruh", "holy", "dude",
        "insane", "crazy", "help", "i cant believe", "oh no", "wtf", "yo",
    ),
    "es": (
        "no puede ser", "dios mio", "que", "mentira", "socorro", "vamos", "increible",
        "locura", "ayuda", "no lo creo", "hostia", "joder",
    ),
}
# Palavras de ligação: o corte nunca termina nelas.
LIGACAO: Dict[str, FrozenSet[str]] = {
    "pt": frozenset(
        "e o a os as um uma que mas ai pra para de do da em no na com se porque entao ou".split()
    ),
    "en": frozenset(
        "and the a an we so but or to of in on with because then if that as at for".split()
    ),
    "es": frozenset("y el la los las un una que pero asi para de del en con si porque o".split()),
}
LINGUAS_SUPORTADAS = tuple(REACOES)
ROTULOS_TIPO = {
    "pt": {"grito": "GRITO", "reacao": "REAÇÃO", "ambos": "GRITO+REAÇÃO"},
    "en": {"grito": "SCREAM", "reacao": "REACTION", "ambos": "SCREAM+REACTION"},
    "es": {"grito": "GRITO", "reacao": "REACCIÓN", "ambos": "GRITO+REACCIÓN"},
}

# ---------------------------------------------------------------- arquivos
EXTENSOES_VIDEO: Tuple[str, ...] = (".mp4", ".mkv", ".mov")
MODELO_WHISPER = "small"
PEDACO_TRANSCRICAO_S = 600

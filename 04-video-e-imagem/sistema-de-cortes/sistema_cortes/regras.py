"""Regras do repertório que o código FAZ CUMPRIR (não dependem de lembrar).

1. Permissão do streamer antes de tudo (regra dos PDFs).
2. PARE: nada é cortado antes do OK explícito do dono (comando `aprovar`).
3. Nunca alterar nem apagar o vídeo original (regra da skill editar-video-ffmpeg).
4. Nunca guardar chaves, senhas ou dados pessoais (regra do README do repositório).
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Tuple


class RegraViolada(RuntimeError):
    """Erro com mensagem em português simples, pronta para mostrar ao dono."""


class PermissaoNegada(RegraViolada):
    pass


class AprovacaoPendente(RegraViolada):
    pass


class OriginalAlterado(RegraViolada):
    pass


# --------------------------------------------------------------- 1. permissão
def registrar_permissao(estado: dict, origem: str) -> dict:
    """Guarda de onde vem a permissão (programa de cortes, print de conversa, link).

    `origem` não pode ser vazia: é com ela que o dono contesta uma denúncia.
    """
    origem = (origem or "").strip()
    if len(origem) < 5:
        raise PermissaoNegada(
            "Sem permissão do streamer não corto. Diga onde ela está escrita "
            "(programa de cortes, print da conversa, regras do canal)."
        )
    estado["permissao"] = {
        "origem": origem,
        "registrada_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    return estado


def exigir_permissao(estado: dict) -> None:
    if not estado.get("permissao"):
        raise PermissaoNegada(
            "Falta a permissão do streamer. Rode: permissao --origem \"onde está escrita\"."
        )


# --------------------------------------------------------------- 2. PARE / OK
def exigir_aprovacao(estado: dict) -> None:
    if not estado.get("aprovado"):
        raise AprovacaoPendente(
            "PARE: a lista de momentos ainda não foi aprovada. Mostre a lista ao dono, "
            "espere o OK e só então rode `aprovar`."
        )


# --------------------------------------------------------------- 3. original intacto
@dataclass(frozen=True)
class Assinatura:
    tamanho: int
    hash_pontas: str  # conteúdo, não data: copiar/mover o arquivo não conta como alterar


def _hash_pontas(caminho: Path, bloco: int = 1 << 20) -> str:
    h = hashlib.sha256()
    tamanho = caminho.stat().st_size
    with caminho.open("rb") as f:
        h.update(f.read(bloco))
        if tamanho > 2 * bloco:
            f.seek(-bloco, 2)
            h.update(f.read(bloco))
    return h.hexdigest()


def assinar_original(video: Path) -> Assinatura:
    st = video.stat()
    return Assinatura(st.st_size, _hash_pontas(video))


def conferir_original(video: Path, antes: Assinatura) -> None:
    if assinar_original(video) != antes:
        raise OriginalAlterado(f"O vídeo original foi modificado: {video.name}. Pare e avise o dono.")


def garantir_saida_segura(saida: Path, video: Path) -> None:
    """A saída nunca pode ser o próprio original nem ficar do lado dele sem a pasta `cortes/`."""
    if saida.resolve() == video.resolve():
        raise OriginalAlterado("A saída é o próprio vídeo original.")
    if "cortes" not in {p.name for p in saida.resolve().parents}:
        raise RegraViolada(f"Saída fora da pasta 'cortes/': {saida}")


# --------------------------------------------------------------- 4. segredos
_PADROES_SEGREDO: List[Tuple[str, "re.Pattern[str]"]] = [
    ("chave sk-", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("token GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("chave AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("chave privada", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("e-mail", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")),
    ("telefone", re.compile(r"\(?\+?55\)?[\s-]?\(?\d{2}\)?[\s-]?9?\d{4}[\s-]?\d{4}")),
]
_EXTENSOES_TEXTO = {".py", ".md", ".txt", ".json", ".toml", ".cfg", ".yml", ".yaml", ".ass"}


def varrer_segredos(pasta: Path, permitidos: Iterable[str] = ()) -> List[Tuple[str, int, str]]:
    """Procura chaves, e-mails e telefones. Devolve (arquivo, linha, tipo). Vazio = limpo."""
    liberados = set(permitidos)
    achados: List[Tuple[str, int, str]] = []
    for arq in sorted(pasta.rglob("*")):
        if not arq.is_file() or arq.suffix.lower() not in _EXTENSOES_TEXTO:
            continue
        if any(parte.startswith(".") or parte == "__pycache__" for parte in arq.parts):
            continue
        for n, linha in enumerate(arq.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for tipo, padrao in _PADROES_SEGREDO:
                for achado in padrao.finditer(linha):
                    if achado.group(0) not in liberados:
                        achados.append((str(arq.relative_to(pasta)), n, tipo))
    return achados

"""Leitura e validação do arquivo halloween_vendas.csv (biblioteca padrão)."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Cabeçalho esperado conforme o dataset do mini-projeto.
EXPECTED_COLUMNS: tuple[str, ...] = (
    "pedido_id",
    "data_venda",
    "produto",
    "categoria",
    "canal_venda",
    "cidade",
    "quantidade",
    "preco_unitario",
    "custo_unitario",
    "desconto_pct",
    "status_pedido",
    "publico",
    "tamanho",
    "data_entrega",
)

DEFAULT_CSV_NAME = "halloween_vendas.csv"
SEM_CATEGORIA = "sem categoria"

CANAIS_OFICIAIS: dict[str, str] = {
    "mercado": "Mercado",
    "loja física": "Loja física",
    "loja fisica": "Loja física",
    "web": "Web",
}

_CATEGORIA_CARACTERES_INVALIDOS = re.compile(r"[^a-z ]")
_ESPACOS_MULTIPLOS = re.compile(r"\s+")


@dataclass(frozen=True)
class CsvValidationResult:
    """Resultado da validação estrutural do CSV antes da análise."""

    path: Path
    file_exists: bool
    readable_utf8: bool
    has_header: bool
    columns_match: bool
    missing_columns: tuple[str, ...]
    extra_columns: tuple[str, ...]
    row_count: int
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.file_exists and self.readable_utf8 and self.has_header and self.columns_match

    def summary(self) -> dict[str, Any]:
        return {
            "arquivo": str(self.path),
            "valido": self.ok,
            "linhas_de_dados": self.row_count,
            "colunas_esperadas": len(EXPECTED_COLUMNS),
            "colunas_ausentes": list(self.missing_columns),
            "colunas_extras": list(self.extra_columns),
            "erros": list(self.errors),
        }


def project_root() -> Path:
    """Diretório raiz do exercício (onde ficam o CSV e o notebook)."""
    return Path(__file__).resolve().parent


def default_csv_path() -> Path:
    return project_root() / DEFAULT_CSV_NAME


def validate_csv_file(csv_path: Path | str | None = None) -> CsvValidationResult:
    """
    Valida existência, encoding UTF-8, cabeçalho e colunas obrigatórias.
    Conta linhas de dados (exclui o cabeçalho) sem alterar o arquivo.
    """
    path = Path(csv_path) if csv_path is not None else default_csv_path()
    errors: list[str] = []

    if not path.is_file():
        errors.append(f"Arquivo não encontrado: {path}")
        return CsvValidationResult(
            path=path,
            file_exists=False,
            readable_utf8=False,
            has_header=False,
            columns_match=False,
            missing_columns=tuple(EXPECTED_COLUMNS),
            extra_columns=(),
            row_count=0,
            errors=tuple(errors),
        )

    header: list[str] | None = None
    readable_utf8 = False
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            header_row = next(reader, None)
            if header_row is not None:
                header = [cell.strip() for cell in header_row]
            readable_utf8 = True
    except UnicodeDecodeError as exc:
        errors.append(f"Não foi possível ler o arquivo como UTF-8: {exc}")
    except OSError as exc:
        errors.append(f"Erro ao abrir o arquivo: {exc}")

    if not readable_utf8:
        return CsvValidationResult(
            path=path,
            file_exists=True,
            readable_utf8=False,
            has_header=False,
            columns_match=False,
            missing_columns=tuple(EXPECTED_COLUMNS),
            extra_columns=(),
            row_count=0,
            errors=tuple(errors),
        )

    has_header = header is not None and len(header) > 0
    if not has_header:
        errors.append("Arquivo vazio ou sem linha de cabeçalho.")

    missing = tuple(col for col in EXPECTED_COLUMNS if col not in (header or []))
    extra = tuple(col for col in (header or []) if col not in EXPECTED_COLUMNS)
    columns_match = has_header and not missing and header == list(EXPECTED_COLUMNS)

    if missing:
        errors.append(f"Colunas obrigatórias ausentes: {', '.join(missing)}")
    if extra:
        errors.append(f"Colunas não previstas no enunciado: {', '.join(extra)}")
    if has_header and header != list(EXPECTED_COLUMNS) and not missing and not extra:
        errors.append("Ordem das colunas difere do cabeçalho esperado.")

    row_count = 0
    if has_header and not missing:
        try:
            with path.open(encoding="utf-8", newline="") as handle:
                row_count = sum(1 for _ in csv.DictReader(handle))
        except csv.Error as exc:
            errors.append(f"Erro ao interpretar linhas CSV: {exc}")

    return CsvValidationResult(
        path=path,
        file_exists=True,
        readable_utf8=True,
        has_header=has_header,
        columns_match=columns_match,
        missing_columns=missing,
        extra_columns=extra,
        row_count=row_count,
        errors=tuple(errors),
    )


def read_sales_csv(csv_path: Path | str | None = None) -> list[dict[str, str]]:
    """
    Lê o CSV com csv.DictReader; todos os campos permanecem como texto.
    Levanta ValueError se a validação estrutural falhar.
    """
    path = Path(csv_path) if csv_path is not None else default_csv_path()
    validation = validate_csv_file(path)
    if not validation.ok:
        detail = "; ".join(validation.errors) or "validação falhou"
        raise ValueError(f"CSV inválido ({path}): {detail}")

    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(frozen=True)
class StringTransformStats:
    """Contagens da padronização de `categoria` e `canal_venda`."""

    categorias_vazias_preenchidas: int
    categorias_nao_vazias_alteradas: int
    canais_alterados: int

    def summary(self) -> dict[str, int]:
        return {
            "categorias_vazias_preenchidas": self.categorias_vazias_preenchidas,
            "categorias_nao_vazias_alteradas": self.categorias_nao_vazias_alteradas,
            "canais_alterados": self.canais_alterados,
        }


def normalize_categoria(raw: str) -> str:
    """
    Aplica .strip(), .lower() e re.sub() para remover pontuação indevida,
    preservando letras (sem acento) e espaços. Vazio após limpeza -> sem categoria.
    """
    if not raw.strip():
        return SEM_CATEGORIA

    texto = raw.strip().lower()
    texto = _CATEGORIA_CARACTERES_INVALIDOS.sub("", texto)
    texto = _ESPACOS_MULTIPLOS.sub(" ", texto).strip()
    return texto or SEM_CATEGORIA


def normalize_canal_venda(raw: str) -> str:
    """Padroniza grafias conhecidas para Mercado, Loja física e Web."""
    chave = _ESPACOS_MULTIPLOS.sub(" ", raw.strip().lower())
    return CANAIS_OFICIAIS.get(chave, raw.strip())


def transform_string_fields(
    registros: list[dict[str, str]],
) -> tuple[list[dict[str, str]], StringTransformStats]:
    """
    Retorna cópias dos registros com categoria e canal padronizados,
    sem modificar o CSV original.
    """
    saida: list[dict[str, str]] = []
    vazias_preenchidas = 0
    nao_vazias_alteradas = 0
    canais_alterados = 0

    for registro in registros:
        novo = dict(registro)
        categoria_original = registro["categoria"]
        canal_original = registro["canal_venda"]

        categoria_nova = normalize_categoria(categoria_original)
        canal_novo = normalize_canal_venda(canal_original)

        if not categoria_original.strip():
            vazias_preenchidas += 1
        elif categoria_nova != categoria_original:
            nao_vazias_alteradas += 1

        if canal_novo != canal_original:
            canais_alterados += 1

        novo["categoria"] = categoria_nova
        novo["canal_venda"] = canal_novo
        saida.append(novo)

    stats = StringTransformStats(
        categorias_vazias_preenchidas=vazias_preenchidas,
        categorias_nao_vazias_alteradas=nao_vazias_alteradas,
        canais_alterados=canais_alterados,
    )
    return saida, stats

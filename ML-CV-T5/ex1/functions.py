"""Leitura e validação do arquivo halloween_vendas.csv (biblioteca padrão)."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import datetime
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
DATA_VENDA_FORMAT = "%Y-%m-%d %H:%M:%S"
STATUS_CANCELADO = "Cancelado"

CANAIS_OFICIAIS: dict[str, str] = {
    "mercado": "Mercado",
    "loja física": "Loja física",
    "loja fisica": "Loja física",
    "web": "Web",
}
CANAIS_RECONHECIDOS: frozenset[str] = frozenset(CANAIS_OFICIAIS.values())

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


@dataclass(frozen=True)
class NumericValidationStats:
    """Contagens de problemas em quantidade e preco_unitario."""

    problemas_quantidade: int
    problemas_preco_unitario: int
    pedidos_com_problema: int

    def summary(self) -> dict[str, int]:
        return {
            "problemas_quantidade": self.problemas_quantidade,
            "problemas_preco_unitario": self.problemas_preco_unitario,
            "pedidos_com_problema": self.pedidos_com_problema,
        }


def _motivo_quantidade_invalida(raw: str) -> str | None:
    """
    Regra: quantidade deve ser inteiro estrito maior que zero.
    Não corrigimos o valor — apenas classificamos o problema.
    """
    texto = raw.strip()
    if not texto:
        return "quantidade_vazia"
    try:
        valor = int(texto)
    except ValueError:
        return "quantidade_nao_inteira"
    if valor <= 0:
        return "quantidade_menor_ou_igual_a_zero"
    return None


def _motivo_preco_invalido(raw: str) -> str | None:
    """
    Regra: preco_unitario deve estar preenchido e ser numérico >= 0.
    """
    texto = raw.strip()
    if not texto:
        return "preco_unitario_ausente"
    try:
        valor = float(texto)
    except ValueError:
        return "preco_unitario_nao_numerico"
    if valor < 0:
        return "preco_unitario_negativo"
    return None


def validate_numeric_fields(
    registros: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], NumericValidationStats]:
    """
    Separa registros com problemas numéricos dos demais, sem alterar valores.
    O processamento considera todos os registros mesmo quando há erros.
    """
    validos: list[dict[str, str]] = []
    com_problema: list[dict[str, str]] = []
    problemas_quantidade = 0
    problemas_preco = 0
    pedidos_afetados: set[str] = set()

    for registro in registros:
        motivos: list[str] = []
        motivo_q = _motivo_quantidade_invalida(registro["quantidade"])
        if motivo_q is not None:
            motivos.append(motivo_q)
            problemas_quantidade += 1
        motivo_p = _motivo_preco_invalido(registro["preco_unitario"])
        if motivo_p is not None:
            motivos.append(motivo_p)
            problemas_preco += 1

        if motivos:
            pedidos_afetados.add(registro["pedido_id"])
            marcado = dict(registro)
            marcado["_problemas"] = motivos
            com_problema.append(marcado)
        else:
            validos.append(dict(registro))

    stats = NumericValidationStats(
        problemas_quantidade=problemas_quantidade,
        problemas_preco_unitario=problemas_preco,
        pedidos_com_problema=len(pedidos_afetados),
    )
    return validos, com_problema, stats


@dataclass(frozen=True)
class DataVendaInfo:
    """Resultado do parse de data_venda; preserva o texto original."""

    original: str
    valido: bool
    data_br: str | None
    ano: int | None
    mes: int | None
    dia: int | None
    hora: str | None


@dataclass(frozen=True)
class EntregaSemDataStats:
    sem_entrega_cancelados: int
    sem_entrega_outros_status: int
    hipotese_todos_cancelados: bool
    exemplos_outros_status: tuple[dict[str, str], ...]

    def summary(self) -> dict[str, Any]:
        return {
            "sem_entrega_cancelados": self.sem_entrega_cancelados,
            "sem_entrega_outros_status": self.sem_entrega_outros_status,
            "hipotese_todos_cancelados": self.hipotese_todos_cancelados,
            "exemplos_outros_status": len(self.exemplos_outros_status),
        }


@dataclass(frozen=True)
class ContagemCanal:
    por_canal: dict[str, int]
    excluidos: int

    def summary(self) -> dict[str, Any]:
        return {"por_canal": self.por_canal, "excluidos": self.excluidos}


@dataclass(frozen=True)
class ContagemAnoMes:
    por_ano_mes: dict[str, int]
    excluidos: int

    def summary(self) -> dict[str, Any]:
        return {"por_ano_mes": self.por_ano_mes, "excluidos": self.excluidos}


@dataclass(frozen=True)
class RelatorioStatus:
    total_linhas: int
    categorias_padronizadas: int
    problemas_numericos: NumericValidationStats
    datas_invalidas: int
    total_cancelados: int
    entrega: EntregaSemDataStats
    canais: ContagemCanal
    periodos: ContagemAnoMes

    def summary(self) -> dict[str, Any]:
        return {
            "total_linhas": self.total_linhas,
            "categorias_padronizadas": self.categorias_padronizadas,
            "problemas_numericos": self.problemas_numericos.summary(),
            "datas_invalidas": self.datas_invalidas,
            "total_cancelados": self.total_cancelados,
            "entrega": self.entrega.summary(),
            "canais": self.canais.summary(),
            "periodos": self.periodos.summary(),
        }


def parse_data_venda(raw: str) -> DataVendaInfo:
    """Converte data_venda com strptime e gera apresentação brasileira (dd/mm/aaaa)."""
    original = raw
    texto = raw.strip()
    if not texto:
        return DataVendaInfo(original, False, None, None, None, None, None)
    try:
        momento = datetime.strptime(texto, DATA_VENDA_FORMAT)
    except ValueError:
        return DataVendaInfo(original, False, None, None, None, None, None)
    return DataVendaInfo(
        original=original,
        valido=True,
        data_br=momento.strftime("%d/%m/%Y"),
        ano=momento.year,
        mes=momento.month,
        dia=momento.day,
        hora=momento.strftime("%H:%M:%S"),
    )


def _data_entrega_vazia(raw: str) -> bool:
    return not raw.strip()


def analyze_entrega_sem_data(
    registros: list[dict[str, str]],
    max_exemplos: int = 3,
) -> EntregaSemDataStats:
    """
    Verifica se pedidos sem data_entrega são sempre Cancelado.
    Não altera status nem inventa datas.
    """
    sem_entrega_cancelados = 0
    sem_entrega_outros_status = 0
    exemplos: list[dict[str, str]] = []

    for registro in registros:
        if not _data_entrega_vazia(registro["data_entrega"]):
            continue
        if registro["status_pedido"] == STATUS_CANCELADO:
            sem_entrega_cancelados += 1
        else:
            sem_entrega_outros_status += 1
            if len(exemplos) < max_exemplos:
                exemplos.append(dict(registro))

    hipotese = sem_entrega_outros_status == 0
    return EntregaSemDataStats(
        sem_entrega_cancelados=sem_entrega_cancelados,
        sem_entrega_outros_status=sem_entrega_outros_status,
        hipotese_todos_cancelados=hipotese,
        exemplos_outros_status=tuple(exemplos),
    )


def contar_pedidos_por_canal(registros: list[dict[str, str]]) -> ContagemCanal:
    """Conta pedidos por canal reconhecido; inclui todos os status."""
    contagem: dict[str, int] = {canal: 0 for canal in sorted(CANAIS_RECONHECIDOS)}
    excluidos = 0
    for registro in registros:
        canal = registro["canal_venda"]
        if canal in CANAIS_RECONHECIDOS:
            contagem[canal] += 1
        else:
            excluidos += 1
    return ContagemCanal(por_canal=contagem, excluidos=excluidos)


def contar_pedidos_por_ano_mes(registros: list[dict[str, str]]) -> ContagemAnoMes:
    """Agrupa por ano-mês usando apenas data_venda válida."""
    contagem: dict[str, int] = {}
    excluidos = 0
    for registro in registros:
        info = parse_data_venda(registro["data_venda"])
        if not info.valido or info.ano is None or info.mes is None:
            excluidos += 1
            continue
        chave = f"{info.ano}-{info.mes:02d}"
        contagem[chave] = contagem.get(chave, 0) + 1
    return ContagemAnoMes(
        por_ano_mes=dict(sorted(contagem.items())),
        excluidos=excluidos,
    )


def contar_datas_invalidas(registros: list[dict[str, str]]) -> int:
    return sum(1 for registro in registros if not parse_data_venda(registro["data_venda"]).valido)


def gerar_relatorio_status(
    registros_limpos: list[dict[str, str]],
    stats_strings: StringTransformStats,
    stats_numericos: NumericValidationStats,
) -> RelatorioStatus:
    """Relatório consolidado da exploração (Sprint 4)."""
    return RelatorioStatus(
        total_linhas=len(registros_limpos),
        categorias_padronizadas=len(registros_limpos),
        problemas_numericos=stats_numericos,
        datas_invalidas=contar_datas_invalidas(registros_limpos),
        total_cancelados=sum(
            1 for registro in registros_limpos if registro["status_pedido"] == STATUS_CANCELADO
        ),
        entrega=analyze_entrega_sem_data(registros_limpos),
        canais=contar_pedidos_por_canal(registros_limpos),
        periodos=contar_pedidos_por_ano_mes(registros_limpos),
    )

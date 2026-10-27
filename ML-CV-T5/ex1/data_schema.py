"""Dataclasses e definição de colunas do dataset de vendas."""

from __future__ import annotations

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

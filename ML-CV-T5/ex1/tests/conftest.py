"""Fixtures pytest reutilizadas em ``tests/test_functions.py``."""

from __future__ import annotations

import csv
from collections.abc import Callable
from pathlib import Path

import pytest

import functions as fn

LinhaFactory = Callable[..., dict[str, str]]


@pytest.fixture
def linha() -> LinhaFactory:
    """Monta um registro de venda com valores padrão sobrescritos por campo."""

    def _montar(**campos: str) -> dict[str, str]:
        base = {coluna: "" for coluna in fn.EXPECTED_COLUMNS}
        base.update(
            {
                "pedido_id": "1",
                "data_venda": "2025-10-12 14:35:00",
                "produto": "Produto teste",
                "categoria": "Fantasia",
                "canal_venda": "Web",
                "cidade": "Curitiba",
                "quantidade": "2",
                "preco_unitario": "10.5",
                "custo_unitario": "5",
                "desconto_pct": "0",
                "status_pedido": "Concluído",
                "publico": "Adulto",
                "tamanho": "M",
                "data_entrega": "2025-10-15 10:00:00",
            }
        )
        base.update(campos)
        return base

    return _montar


@pytest.fixture
def csv_halloween() -> Path:
    """Caminho do CSV real; pula o teste se o arquivo não existir."""
    caminho = fn.default_csv_path()
    if not caminho.is_file():
        pytest.skip("halloween_vendas.csv ausente")
    return caminho


@pytest.fixture
def registros_halloween(csv_halloween: Path) -> list[dict[str, str]]:
    """Lista de pedidos lida do ``halloween_vendas.csv`` via ``read_sales_csv``."""
    return fn.read_sales_csv(csv_halloween)


@pytest.fixture
def pipeline_halloween(
    registros_halloween: list[dict[str, str]],
) -> tuple[list[dict[str, str]], fn.StringTransformStats, fn.NumericValidationStats]:
    """Tupla ``(registros_limpos, stats_strings, stats_numericos)`` após Sprints 2–3."""
    limpos, stats_strings = fn.transform_string_fields(registros_halloween)
    _, _, stats_numericos = fn.validate_numeric_fields(limpos)
    return limpos, stats_strings, stats_numericos


@pytest.fixture
def csv_valido_tmp(tmp_path: Path) -> Path:
    """CSV temporário com cabeçalho completo e uma linha de dados."""
    caminho = tmp_path / "valido.csv"
    with caminho.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(fn.EXPECTED_COLUMNS)
        writer.writerow([f"v{i}" for i in range(len(fn.EXPECTED_COLUMNS))])
    return caminho

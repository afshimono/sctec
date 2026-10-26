"""Testes pytest do módulo functions."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

import functions as fn

Linha = Callable[..., dict[str, str]]


def test_project_root_contem_functions() -> None:
    assert (fn.project_root() / "functions.py").is_file()


def test_default_csv_path() -> None:
    assert fn.default_csv_path().name == fn.DEFAULT_CSV_NAME


def test_validate_csv_arquivo_inexistente() -> None:
    resultado = fn.validate_csv_file(Path("/caminho/inexistente.csv"))
    assert not resultado.ok
    assert not resultado.file_exists


def test_validate_csv_valido_em_temporario(csv_valido_tmp: Path) -> None:
    resultado = fn.validate_csv_file(csv_valido_tmp)
    assert resultado.ok
    assert resultado.row_count == 1


def test_validate_csv_cabecalho_incompleto(tmp_path: Path) -> None:
    caminho = tmp_path / "ruim.csv"
    caminho.write_text("pedido_id,data_venda\n1,2025-01-01\n", encoding="utf-8")
    resultado = fn.validate_csv_file(caminho)
    assert not resultado.ok
    assert resultado.missing_columns


def test_read_sales_csv_levanta_erro_se_invalido() -> None:
    with pytest.raises(ValueError):
        fn.read_sales_csv(Path("/nao/existe.csv"))


def test_read_sales_csv_halloween(registros_halloween: list[dict[str, str]]) -> None:
    assert len(registros_halloween) == 1500


def test_normalize_categoria_vazia() -> None:
    assert fn.normalize_categoria("   ") == fn.SEM_CATEGORIA


def test_normalize_categoria_pontuacao() -> None:
    assert fn.normalize_categoria("  FANTASIA!!!  ") == "fantasia"


def test_normalize_canal_oficial() -> None:
    assert fn.normalize_canal_venda(" web ") == "Web"


def test_normalize_canal_desconhecido() -> None:
    assert fn.normalize_canal_venda("  Loja X  ") == "Loja X"


def test_transform_string_fields(linha: Linha) -> None:
    registros = [linha(categoria="", canal_venda=" mercado ")]
    saida, stats = fn.transform_string_fields(registros)
    assert saida[0]["categoria"] == fn.SEM_CATEGORIA
    assert saida[0]["canal_venda"] == "Mercado"
    assert stats.categorias_vazias_preenchidas == 1
    assert stats.canais_alterados == 1


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("", "quantidade_vazia"),
        ("-1", "quantidade_menor_ou_igual_a_zero"),
        ("1.5", "quantidade_nao_inteira"),
        ("3", None),
    ],
)
def test_motivo_quantidade_invalida(valor: str, esperado: str | None) -> None:
    assert fn._motivo_quantidade_invalida(valor) == esperado


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("", "preco_unitario_ausente"),
        ("-2", "preco_unitario_negativo"),
        ("0", None),
    ],
)
def test_motivo_preco_invalido(valor: str, esperado: str | None) -> None:
    assert fn._motivo_preco_invalido(valor) == esperado


def test_validate_numeric_fields_separa_validos_e_invalidos(linha: Linha) -> None:
    registros = [
        linha(pedido_id="1", quantidade="2", preco_unitario="10"),
        linha(pedido_id="2", quantidade="-1", preco_unitario=""),
    ]
    validos, com_problema, stats = fn.validate_numeric_fields(registros)
    assert len(validos) == 1
    assert len(com_problema) == 1
    assert stats.problemas_quantidade == 1
    assert stats.problemas_preco_unitario == 1
    assert stats.pedidos_com_problema == 1
    assert "quantidade_menor_ou_igual_a_zero" in com_problema[0]["_problemas"]


def test_parse_data_venda_valida() -> None:
    info = fn.parse_data_venda("2025-10-12 14:35:00")
    assert info.valido
    assert info.data_br == "12/10/2025"
    assert info.ano == 2025
    assert info.mes == 10
    assert info.hora == "14:35:00"


def test_parse_data_venda_invalida() -> None:
    assert not fn.parse_data_venda("data-ruim").valido


def test_data_entrega_vazia() -> None:
    assert fn._data_entrega_vazia("  ")
    assert not fn._data_entrega_vazia("2025-01-01")


def test_analyze_entrega_sem_data(linha: Linha) -> None:
    registros = [
        linha(pedido_id="1", data_entrega="", status_pedido=fn.STATUS_CANCELADO),
        linha(pedido_id="2", data_entrega="", status_pedido="Concluído"),
    ]
    stats = fn.analyze_entrega_sem_data(registros)
    assert not stats.hipotese_todos_cancelados
    assert stats.sem_entrega_cancelados == 1
    assert stats.sem_entrega_outros_status == 1
    assert len(stats.exemplos_outros_status) == 1


def test_contar_pedidos_por_canal(linha: Linha) -> None:
    registros = [linha(canal_venda="Web"), linha(pedido_id="2", canal_venda="Desconhecido")]
    contagem = fn.contar_pedidos_por_canal(registros)
    assert contagem.por_canal["Web"] == 1
    assert contagem.excluidos == 1


def test_contar_pedidos_por_ano_mes(linha: Linha) -> None:
    registros = [
        linha(data_venda="2025-10-12 14:35:00"),
        linha(pedido_id="2", data_venda="invalida"),
    ]
    contagem = fn.contar_pedidos_por_ano_mes(registros)
    assert contagem.por_ano_mes["2025-10"] == 1
    assert contagem.excluidos == 1


def test_contar_datas_invalidas(linha: Linha) -> None:
    registros = [linha(data_venda=""), linha(pedido_id="2", data_venda="2024-01-01 00:00:00")]
    assert fn.contar_datas_invalidas(registros) == 1


def test_gerar_relatorio_status(linha: Linha) -> None:
    transformados, stats_strings = fn.transform_string_fields([linha()])
    _, _, stats_numericos = fn.validate_numeric_fields(transformados)
    relatorio = fn.gerar_relatorio_status(transformados, stats_strings, stats_numericos)
    assert relatorio.total_linhas == 1
    assert relatorio.datas_invalidas == 0
    assert "total_linhas" in relatorio.summary()


def test_csv_validation_result_summary() -> None:
    resultado = fn.CsvValidationResult(
        path=Path("x.csv"),
        file_exists=True,
        readable_utf8=True,
        has_header=True,
        columns_match=True,
        missing_columns=(),
        extra_columns=(),
        row_count=10,
        errors=(),
    )
    assert resultado.summary()["valido"]


def test_string_transform_stats_summary() -> None:
    assert fn.StringTransformStats(1, 2, 3).summary()["canais_alterados"] == 3


def test_pipeline_halloween_completo(pipeline_halloween) -> None:
    limpos, stats_strings, stats_numericos = pipeline_halloween
    relatorio = fn.gerar_relatorio_status(limpos, stats_strings, stats_numericos)
    assert relatorio.total_linhas == 1500
    assert stats_numericos.pedidos_com_problema == 19
    assert not relatorio.entrega.hipotese_todos_cancelados

"""Testes unitários do módulo functions."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import functions as fn


def _linha(**campos: str) -> dict[str, str]:
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


class TestPaths(unittest.TestCase):
    def test_project_root_contem_functions(self) -> None:
        self.assertTrue((fn.project_root() / "functions.py").is_file())

    def test_default_csv_path(self) -> None:
        self.assertEqual(fn.default_csv_path().name, fn.DEFAULT_CSV_NAME)


class TestValidateCsvFile(unittest.TestCase):
    def test_arquivo_inexistente(self) -> None:
        resultado = fn.validate_csv_file(Path("/caminho/inexistente.csv"))
        self.assertFalse(resultado.ok)
        self.assertFalse(resultado.file_exists)

    def test_csv_valido_em_temporario(self) -> None:
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "teste.csv"
            with caminho.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(fn.EXPECTED_COLUMNS)
                writer.writerow([f"v{i}" for i in range(len(fn.EXPECTED_COLUMNS))])

            resultado = fn.validate_csv_file(caminho)
            self.assertTrue(resultado.ok)
            self.assertEqual(resultado.row_count, 1)

    def test_cabecalho_incompleto(self) -> None:
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "ruim.csv"
            caminho.write_text("pedido_id,data_venda\n1,2025-01-01\n", encoding="utf-8")
            resultado = fn.validate_csv_file(caminho)
            self.assertFalse(resultado.ok)
            self.assertTrue(resultado.missing_columns)


class TestReadSalesCsv(unittest.TestCase):
    def test_levanta_erro_se_invalido(self) -> None:
        with self.assertRaises(ValueError):
            fn.read_sales_csv(Path("/nao/existe.csv"))

    def test_le_halloween_se_presente(self) -> None:
        if not fn.default_csv_path().is_file():
            self.skipTest("halloween_vendas.csv ausente")
        registros = fn.read_sales_csv()
        self.assertEqual(len(registros), 1500)


class TestStrings(unittest.TestCase):
    def test_normalize_categoria_vazia(self) -> None:
        self.assertEqual(fn.normalize_categoria("   "), fn.SEM_CATEGORIA)

    def test_normalize_categoria_pontuacao(self) -> None:
        self.assertEqual(fn.normalize_categoria("  FANTASIA!!!  "), "fantasia")

    def test_normalize_canal_oficial(self) -> None:
        self.assertEqual(fn.normalize_canal_venda(" web "), "Web")

    def test_normalize_canal_desconhecido(self) -> None:
        self.assertEqual(fn.normalize_canal_venda("  Loja X  "), "Loja X")

    def test_transform_string_fields(self) -> None:
        registros = [_linha(categoria="", canal_venda=" mercado ")]
        saida, stats = fn.transform_string_fields(registros)
        self.assertEqual(saida[0]["categoria"], fn.SEM_CATEGORIA)
        self.assertEqual(saida[0]["canal_venda"], "Mercado")
        self.assertEqual(stats.categorias_vazias_preenchidas, 1)
        self.assertEqual(stats.canais_alterados, 1)


class TestNumericHelpers(unittest.TestCase):
    def test_motivo_quantidade(self) -> None:
        self.assertEqual(fn._motivo_quantidade_invalida(""), "quantidade_vazia")
        self.assertEqual(fn._motivo_quantidade_invalida("-1"), "quantidade_menor_ou_igual_a_zero")
        self.assertEqual(fn._motivo_quantidade_invalida("1.5"), "quantidade_nao_inteira")
        self.assertIsNone(fn._motivo_quantidade_invalida("3"))

    def test_motivo_preco(self) -> None:
        self.assertEqual(fn._motivo_preco_invalido(""), "preco_unitario_ausente")
        self.assertEqual(fn._motivo_preco_invalido("-2"), "preco_unitario_negativo")
        self.assertIsNone(fn._motivo_preco_invalido("0"))


class TestValidateNumericFields(unittest.TestCase):
    def test_separa_validos_e_invalidos(self) -> None:
        registros = [
            _linha(pedido_id="1", quantidade="2", preco_unitario="10"),
            _linha(pedido_id="2", quantidade="-1", preco_unitario=""),
        ]
        validos, com_problema, stats = fn.validate_numeric_fields(registros)
        self.assertEqual(len(validos), 1)
        self.assertEqual(len(com_problema), 1)
        self.assertEqual(stats.problemas_quantidade, 1)
        self.assertEqual(stats.problemas_preco_unitario, 1)
        self.assertEqual(stats.pedidos_com_problema, 1)
        self.assertIn("quantidade_menor_ou_igual_a_zero", com_problema[0]["_problemas"])


class TestDatasEEntrega(unittest.TestCase):
    def test_parse_data_venda_valida(self) -> None:
        info = fn.parse_data_venda("2025-10-12 14:35:00")
        self.assertTrue(info.valido)
        self.assertEqual(info.data_br, "12/10/2025")
        self.assertEqual(info.ano, 2025)
        self.assertEqual(info.mes, 10)
        self.assertEqual(info.hora, "14:35:00")

    def test_parse_data_venda_invalida(self) -> None:
        info = fn.parse_data_venda("data-ruim")
        self.assertFalse(info.valido)

    def test_data_entrega_vazia(self) -> None:
        self.assertTrue(fn._data_entrega_vazia("  "))
        self.assertFalse(fn._data_entrega_vazia("2025-01-01"))

    def test_analyze_entrega_sem_data(self) -> None:
        registros = [
            _linha(pedido_id="1", data_entrega="", status_pedido=fn.STATUS_CANCELADO),
            _linha(pedido_id="2", data_entrega="", status_pedido="Concluído"),
        ]
        stats = fn.analyze_entrega_sem_data(registros)
        self.assertFalse(stats.hipotese_todos_cancelados)
        self.assertEqual(stats.sem_entrega_cancelados, 1)
        self.assertEqual(stats.sem_entrega_outros_status, 1)
        self.assertEqual(len(stats.exemplos_outros_status), 1)


class TestContagens(unittest.TestCase):
    def test_contar_por_canal(self) -> None:
        registros = [_linha(canal_venda="Web"), _linha(pedido_id="2", canal_venda="Desconhecido")]
        contagem = fn.contar_pedidos_por_canal(registros)
        self.assertEqual(contagem.por_canal["Web"], 1)
        self.assertEqual(contagem.excluidos, 1)

    def test_contar_por_ano_mes(self) -> None:
        registros = [
            _linha(data_venda="2025-10-12 14:35:00"),
            _linha(pedido_id="2", data_venda="invalida"),
        ]
        contagem = fn.contar_pedidos_por_ano_mes(registros)
        self.assertEqual(contagem.por_ano_mes["2025-10"], 1)
        self.assertEqual(contagem.excluidos, 1)

    def test_contar_datas_invalidas(self) -> None:
        registros = [_linha(data_venda=""), _linha(pedido_id="2", data_venda="2024-01-01 00:00:00")]
        self.assertEqual(fn.contar_datas_invalidas(registros), 1)


class TestRelatorio(unittest.TestCase):
    def test_gerar_relatorio_status(self) -> None:
        registros = [_linha()]
        transformados, stats_strings = fn.transform_string_fields(registros)
        _, _, stats_numericos = fn.validate_numeric_fields(transformados)
        relatorio = fn.gerar_relatorio_status(transformados, stats_strings, stats_numericos)
        self.assertEqual(relatorio.total_linhas, 1)
        self.assertEqual(relatorio.datas_invalidas, 0)
        self.assertIn("total_linhas", relatorio.summary())


class TestDataclassesSummary(unittest.TestCase):
    def test_csv_validation_summary(self) -> None:
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
        self.assertTrue(resultado.summary()["valido"])

    def test_string_stats_summary(self) -> None:
        stats = fn.StringTransformStats(1, 2, 3)
        self.assertEqual(stats.summary()["canais_alterados"], 3)


class TestIntegracaoHalloween(unittest.TestCase):
    def test_pipeline_completo(self) -> None:
        if not fn.default_csv_path().is_file():
            self.skipTest("halloween_vendas.csv ausente")
        registros = fn.read_sales_csv()
        limpos, stats_strings = fn.transform_string_fields(registros)
        _, _, stats_numericos = fn.validate_numeric_fields(limpos)
        relatorio = fn.gerar_relatorio_status(limpos, stats_strings, stats_numericos)
        self.assertEqual(relatorio.total_linhas, 1500)
        self.assertEqual(stats_numericos.pedidos_com_problema, 19)
        self.assertFalse(relatorio.entrega.hipotese_todos_cancelados)


if __name__ == "__main__":
    unittest.main()

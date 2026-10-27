# Mini-projeto — Festa em Cena (Módulo 1)

## O problema

A **Festa em Cena** é uma rede fictícia de fantasias e acessórios de Halloween. A gestão precisa entender como os pedidos variam por **canal** (Mercado, Loja física, Web) e por **período**, mas o arquivo exportado chega com ruídos típicos de sistemas reais: categorias escritas de formas diferentes, canais com espaços extras, quantidades inválidas, preços ausentes e algumas datas inconsistentes.

Antes de qualquer análise mais avançada (ou uso em modelos de Machine Learning), é necessário **organizar e auditar** esses registros. Este projeto faz essa etapa com **Python nativo** (`csv`, `re`, `datetime`), sem Pandas, preservando o arquivo original no disco. O fluxo completo está em [`analise.ipynb`](analise.ipynb); a lógica reutilizável está em [`functions.py`](functions.py) e os tipos de retorno em [`data_schema.py`](data_schema.py).

Cada **linha** do CSV representa um pedido de um único produto; a coluna `quantidade` indica **unidades** daquele item, não o total de pedidos distintos na base.

| Coluna | Significado |
|--------|-------------|
| `pedido_id` | Identificador do pedido |
| `data_venda` | Data e hora do registro (horário local de São Paulo, sem fuso no arquivo) |
| `canal_venda` | Mercado, Loja física ou Web |
| `status_pedido` | Situação do pedido (ex.: Concluído, Cancelado) |

Enunciado completo: [`INSTRUCTIONS.md`](INSTRUCTIONS.md).

## Arquivo de dados

| Item | Valor |
|------|--------|
| **Nome** | `halloween_vendas.csv` |
| **Local** | Mesma pasta deste projeto: `ML-CV-T5/ex1/` (junto com `functions.py` e `analise.ipynb`) |
| **Caminho relativo ao repositório** | `ML-CV-T5/ex1/halloween_vendas.csv` |
| **Volume** | 1.500 linhas de pedidos (agosto–novembro de 2024 e 2025) |

O programa **não altera** o CSV no disco. Toda limpeza e validação ocorrem em memória após a leitura com `csv.DictReader` e `encoding="utf-8"`.

Se o arquivo estiver ausente, baixe-o conforme o link no enunciado e coloque-o na pasta `ex1` antes de executar o notebook ou os testes de integração.

## Padronização e tratamento de dados

### Textos (`categoria` e `canal_venda`)

- **`categoria`:** `.strip()`, `.lower()` e `re.sub()` para remover pontuação indevida (mantendo letras e espaços). Se o campo vier vazio ou ficar vazio após a limpeza, usamos a string fixa **`sem categoria`** (equivalente a preencher categoria ausente sem inventar um produto).
- **`canal_venda`:** grafias reconhecidas (`mercado`, ` web `, ` loja física `, etc.) são normalizadas para **Mercado**, **Loja física** e **Web**. Canais não reconhecidos permanecem com `strip`, sem chute de valor.

Contagens separadas registram quantas categorias vazias foram preenchidas e quantas categorias não vazias mudaram de texto.

### Valores numéricos (`quantidade` e `preco_unitario`)

Não **corrigimos** valores errados; apenas **classificamos** e separamos registros com problema:

- **`quantidade`:** deve ser inteiro **maior que zero**.
- **`preco_unitario`:** deve estar preenchido e ser numérico **≥ 0**.

Registros com falha ganham a lista `_problemas` em memória. Contamos problemas por campo e **pedidos distintos** (`pedido_id`) afetados, sem somar o mesmo pedido duas vezes quando os dois campos falham.

### Datas e regras de negócio

- **`data_venda`:** convertida com `datetime.strptime` no formato `YYYY-MM-DD HH:MM:SS`; exibição opcional em `dd/mm/aaaa`. Datas inválidas ou vazias são contadas e **excluídas** de agrupamentos por ano-mês (não substituímos pela data de hoje).
- **`data_entrega`:** campos vazios **não** recebem data inventada. Investigamos se todo pedido sem entrega está **Cancelado** e reportamos contraexemplos.

O relatório final (`gerar_relatorio_status`) consolida totais, cancelados, canais e períodos.

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/) instalado
- Python 3.11+ (versão em [`.python-version`](.python-version))

## Como instalar e executar

### 1. Ambiente

Na raiz do exercício dentro do repositório:

```bash
cd ML-CV-T5/ex1
uv sync
```

Isso cria `.venv` e instala dependências de desenvolvimento (Jupyter e pytest).

### 2. Análise interativa (recomendado)

Com `halloween_vendas.csv` na pasta `ex1`:

```bash
uv run jupyter notebook analise.ipynb
```

Ou com JupyterLab:

```bash
uv run jupyter lab analise.ipynb
```

Execute as células **em ordem**: validação do arquivo → leitura → strings → numéricos → datas e relatório.

### 3. Uso via módulo Python

Exemplo rápido no terminal (a partir de `ML-CV-T5/ex1`):

```bash
uv run python -c "from functions import validate_csv_file; print(validate_csv_file().summary())"
```

### 4. Testes automatizados

```bash
uv run pytest
```

Saída detalhada:

```bash
uv run pytest -v
```

Os testes estão em [`tests/test_functions.py`](tests/test_functions.py), com fixtures em [`tests/conftest.py`](tests/conftest.py).

## Resultados (base fictícia)

Reproduza os números no notebook. Destaques típicos:

- **Entrega sem data:** a hipótese “sem `data_entrega` ⇒ Cancelado” é **falsa** na base (há pedidos Concluído sem data de entrega).
- **Canal:** **Web** costuma liderar o volume de linhas registradas após padronização.
- **Período:** **outubro** (2024 e 2025) concentra picos de `data_venda` válida, alinhado ao Halloween.

*Limitação:* as contagens são de **pedidos registrados** no CSV (linhas), não receita nem vendas concluídas no mundo real.

## Estrutura do projeto

Pasta de trabalho: `ML-CV-T5/ex1/`.

| Arquivo / pasta | Função |
|-----------------|--------|
| `halloween_vendas.csv` | Base de dados de entrada (1.500 pedidos; **não** é alterado pelo código) |
| `data_schema.py` | Esquema do CSV (`EXPECTED_COLUMNS`) e dataclasses de validação, transformação e relatório (`CsvValidationResult`, `StringTransformStats`, `NumericValidationStats`, `DataVendaInfo`, `EntregaSemDataStats`, `ContagemCanal`, `ContagemAnoMes`, `RelatorioStatus`) |
| `functions.py` | Funções de leitura (`csv.DictReader`), padronização, validação numérica, datas e `gerar_relatorio_status` |
| `analise.ipynb` | Notebook com o fluxo completo e interpretação dos resultados |
| `INSTRUCTIONS.md` | Enunciado acadêmico do mini-projeto |
| `pyproject.toml` / `uv.lock` | Dependências e ambiente gerenciados com [uv](https://docs.astral.sh/uv/) |
| `tests/` | Testes automatizados (`test_functions.py`, `conftest.py`) executados com pytest |

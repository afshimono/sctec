# Mini-projeto — Festa em Cena (Módulo 1)

Análise exploratória do arquivo `halloween_vendas.csv` com **Python nativo** (`csv`, `re`, `datetime`), conforme o enunciado em [`INSTRUCTIONS.md`](INSTRUCTIONS.md).

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/) instalado
- Python 3.11+ (o projeto fixa a versão em `.python-version`)

## Instalação

Na pasta `ML-CV-T5/ex1`:

```bash
cd ML-CV-T5/ex1
uv sync
```

Isso cria o ambiente virtual em `.venv` e instala o Jupyter (grupo de desenvolvimento) para executar o notebook.

Coloque o arquivo `halloween_vendas.csv` na mesma pasta do projeto (já incluído neste repositório).

## Como executar

### Notebook

```bash
uv run jupyter notebook analise.ipynb
```

Ou, com JupyterLab:

```bash
uv run jupyter lab analise.ipynb
```

Execute as células em ordem. O notebook valida o arquivo, lê os registros com `csv.DictReader` e aplica as transformações documentadas no código.

### Módulo Python

As funções reutilizáveis ficam em `functions.py`. Exemplo no terminal:

```bash
uv run python -c "from functions import validate_csv_file; print(validate_csv_file().summary())"
```

## Estrutura

| Arquivo | Função |
|---------|--------|
| `functions.py` | Leitura do CSV, validação e transformações |
| `analise.ipynb` | Exploração e relatórios |
| `halloween_vendas.csv` | Base de dados (1.500 pedidos) |
| `INSTRUCTIONS.md` | Enunciado completo do mini-projeto |

### Regras de validação numérica

- **quantidade:** texto não vazio, conversível para `int` e **maior que zero**. Valores ausentes, não inteiros ou ≤ 0 são marcados; o valor original é mantido.
- **preco_unitario:** texto não vazio, conversível para `float` e **≥ 0**. Ausente, não numérico ou negativo são marcados; não preenchemos preço faltante.

Contagens reportam problemas **por campo** e **pedidos distintos** com qualquer problema (`pedido_id`), sem somar campos do mesmo pedido como pedidos separados.

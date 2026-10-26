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

### Notebook (Sprint 1 — ingestão)

```bash
uv run jupyter notebook analise.ipynb
```

Ou, com JupyterLab:

```bash
uv run jupyter lab analise.ipynb
```

Execute as células em ordem. A primeira etapa valida o arquivo e lê os registros com `csv.DictReader`.

### Módulo Python

As funções reutilizáveis ficam em `functions.py`. Exemplo no terminal:

```bash
uv run python -c "from functions import validate_csv_file; print(validate_csv_file().summary())"
```

## Estrutura

| Arquivo | Função |
|---------|--------|
| `functions.py` | Leitura do CSV e validação estrutural |
| `analise.ipynb` | Exploração e relatórios por sprint |
| `halloween_vendas.csv` | Base de dados (1.500 pedidos) |
| `INSTRUCTIONS.md` | Enunciado completo do mini-projeto |

## Sprint 1 — entrega parcial

- Leitura do CSV com `csv.DictReader` e `encoding="utf-8"`
- Validação de existência do arquivo, cabeçalho e colunas
- Contagem de linhas e exibição de três registros de exemplo

## Sprint 2 — entrega parcial

- Funções `normalize_categoria`, `normalize_canal_venda` e `transform_string_fields`
- Contagem separada de categorias vazias preenchidas e categorias não vazias alteradas
- Exemplos antes/depois no notebook `analise.ipynb`

Branch `sprint-2-transformacao` (worktree Herdr em `worktrees/sprint-2-transformacao`).

# Mini-projeto — Festa em Cena (Módulo 1)

A **Festa em Cena** é uma rede fictícia de fantasias e acessórios de Halloween. Este projeto lê `halloween_vendas.csv`, trata inconsistências e gera um relatório exploratório com **Python nativo** (`csv`, `re`, `datetime`), conforme [`INSTRUCTIONS.md`](INSTRUCTIONS.md).

Cada **linha** do CSV é um pedido de um único produto (a coluna `quantidade` indica unidades, não pedidos distintos).

| Coluna | Significado |
|--------|-------------|
| `pedido_id` | Identificador do pedido |
| `data_venda` | Data e hora do registro (horário local, sem fuso) |
| `canal_venda` | Mercado, Loja física ou Web |
| `status_pedido` | Situação do pedido (ex.: Concluído, Cancelado) |

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/) instalado
- Python 3.11+ (`.python-version`)

## Instalação e execução

```bash
cd ML-CV-T5/ex1
uv sync
uv run jupyter notebook analise.ipynb
```

O arquivo `halloween_vendas.csv` deve ficar nesta pasta.

## Regras adotadas

### Textos

- `categoria`: `.strip()`, `.lower()`, `re.sub()` para remover pontuação; vazio → `sem categoria`.
- `canal_venda`: padronização para Mercado, Loja física e Web quando a grafia é reconhecida.

### Valores numéricos

- `quantidade`: inteiro **maior que zero**; problemas são marcados, sem correção.
- `preco_unitario`: preenchido e **≥ 0**; ausências não são inventadas.

### Datas

- `data_venda`: parse com `datetime.strptime(..., "%Y-%m-%d %H:%M:%S")`; exibição brasileira `dd/mm/aaaa`; inválidas são contadas e excluídas das séries por ano-mês.
- `data_entrega`: vazia não é preenchida; investigamos a relação com `status_pedido` sem alterar o CSV.

## Resultados (base fictícia)

Execute o notebook para reproduzir os números. Resumo típico:

- **Entrega sem data:** a hipótese “só cancelados” é **falsa** — há pedidos **Concluído** sem `data_entrega` (contraexemplos no notebook).
- **Descoberta por canal:** o canal **Web** concentra o maior volume de pedidos registrados na base tratada (todos os status), à frente de Loja física e Mercado. *Limitação:* contagem de linhas do CSV, não receita nem vendas efetivadas.
- **Descoberta por período:** os meses de **outubro** (2024 e 2025) lideram os registros com `data_venda` válida, coerente com a sazonalidade de Halloween. *Limitação:* quatro datas inválidas ficam fora do agrupamento ano-mês.

## Estrutura

| Arquivo | Função |
|---------|--------|
| `functions.py` | Leitura, validação, transformações e relatório |
| `analise.ipynb` | Fluxo completo e interpretação |
| `halloween_vendas.csv` | 1.500 pedidos fictícios |
| `INSTRUCTIONS.md` | Enunciado |

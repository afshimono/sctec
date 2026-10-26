# Machine Learning e Visão Computacional — Turma 04

**Mini-Projeto Avaliativo — Módulo 1 — Semana 07**

---

## Sumário

1. [Contextualização](#1-contextualização)
2. [Desafio](#2-desafio)
3. [Resultados esperados (entrega)](#3-resultados-esperados-entrega)
4. [Requisitos das tarefas](#4-requisitos-das-tarefas)
5. [Gravação de vídeo](#5-gravação-de-vídeo)
6. [Critérios de avaliação](#6-critérios-de-avaliação)

---

## 1. Contextualização

A **Festa em Cena** é uma rede fictícia que vende fantasias e acessórios para o Halloween pelos canais **Mercado**, **Loja física** e **Web**.

- **Mercado** — vendas para consumidores finais nos caixas de supermercados parceiros
- **Loja física** — lojas próprias
- **Web** — pedidos feitos pelo site

A empresa precisa organizar seus registros e entender como os pedidos variam por canal e período.

Antes de interpretar os dados ou utilizá-los em Machine Learning, é necessário verificar informações ausentes, textos inconsistentes e datas inválidas. A qualidade dos dados influencia os resultados das análises e dos modelos. Entretanto, limpeza não garante, sozinha, evitar overfitting ou underfitting: representatividade, escolha do modelo e avaliação também importam.

Nesta atividade, você aplicará lógica de programação para ler, organizar e explorar um único CSV. A base contém **1.500 pedidos distintos** de agosto a novembro de 2024 e de 2025. Cada linha representa um pedido de um único produto, que pode conter várias unidades. Os dados são fictícios e incluem problemas intencionais para aprendizagem.

**Base de dados (`.csv`):** `halloween_vendas.csv`, disponível em:

[https://github.com/Machine-Learning-Visao-Computacional-T5/python_exercises/blob/main/data_analysis/arquivo_mini_projeto/halloween_vendas.csv](https://github.com/Machine-Learning-Visao-Computacional-T5/python_exercises/blob/main/data_analysis/arquivo_mini_projeto/halloween_vendas.csv)

Os horários são locais de São Paulo, sem fuso explícito. O Halloween é considerado em **31 de outubro** de cada ano.

---

## 2. Desafio

A equipe da Festa em Cena identificou categorias vazias, pontuações indevidas, diferenças na escrita dos canais, quantidades inválidas, preços ausentes e algumas datas inválidas. A gestão quer um relatório simples antes de comparar os períodos de venda.

Sua missão como **Analista de Dados Júnior** é desenvolver um programa em Python, usando apenas a biblioteca padrão, como `csv`, `re` e `datetime`. Utilize variáveis, listas, dicionários, condicionais, laços e funções. **Não utilize Pandas** ou outras bibliotecas externas para processar os dados.

As tarefas técnicas específicas a serem cumpridas são:

### Validação e tratamento de dados ausentes

Leia `halloween_vendas.csv` com usando `pd.read_csv()`, da biblioteca Pandas, e armazene os dados em um DataFrame. Preencha categoria vazia com a string `"sem categoria"`. Verifique `quantidade` (inteiro maior que zero) e `preco_unitario` (preenchido e não negativo). Marque ou separe registros com problemas, sem inventar valores. Justifique sua regra nos comentários e no README. Conte os problemas por campo e o total de pedidos afetados, sem somar ocorrências que podem se sobrepor.

### Padronização de strings e regex

Utilize `.strip()` e `.lower()` na coluna `categoria` e aplique obrigatoriamente `re.sub()` para retirar pontuações indevidas, preservando letras e espaços significativos. As categorias preenchidas deste CSV usam letras sem acentos. Se o resultado ficar vazio, use `"sem categoria"`. Padronize `canal_venda` para **Mercado**, **Loja física** e **Web**. Conte categorias vazias preenchidas e categorias não vazias alteradas separadamente.

### Lógica de regra de negócio (filtros e validação)

Com condicionais, investigue se todos os registros com `data_entrega` vazia têm `status_pedido` igual a **Cancelado**. Conte separadamente pedidos sem entrega e cancelados e pedidos sem entrega com outros status. Mostre até três exemplos do segundo grupo. Se houver um contraexemplo, a hipótese é falsa na base. Não altere o status nem invente datas de entrega.

### Formatação temporal (datetime)

Converta `data_venda` com `datetime.strptime()`, do formato `"2025-10-12 14:35:00"`. Preserve o texto original, extraia ano, mês, dia e hora e crie uma apresentação brasileira com `strftime()`, como `"12/10/2025"`. Conte e marque ou separe datas inválidas ou vazias, permitindo continuar o processamento. Não substitua pela data de hoje.

### Relatório de status manual e exploração

Exiba total de linhas lidas, categorias preenchidas e padronizadas, problemas numéricos, datas inválidas e total de cancelados, além dos dois grupos sem data de entrega. Conte pedidos por canal usando registros com canal reconhecido; por ano-mês, use registros com `data_venda` válida. Nessas duas contagens, inclua todos os status e informe exclusões. **Não agrupe apenas por mês**, pois isso mistura anos. Produza **duas descobertas**: uma por canal e outra por período, com números, interpretação e limitação. Essas contagens representam pedidos registrados, não receita ou vendas concluídas.

---

## 3. Resultados esperados (entrega)

Você deverá organizar e submeter o projeto contendo os seguintes entregáveis:

### Script Python (`main.py`, `funcoes.py` ou `.ipynb`)

O código deve ser modular, dividido em funções com parâmetros e retornos adequados, e comentado para explicar as decisões. Demonstre a aplicação prática de:

- **Manipulação nativa de CSV** com `csv.DictReader` e `with open()`, preservando o arquivo original. Os campos são lidos como texto e precisam de conversão quando usados como números ou datas.
- **Variáveis, listas e dicionários** para armazenar registros e construir contadores. Utilize vírgula como separador e `encoding="utf-8"` na leitura.
- **Condicionais e laços de repetição** para examinar os registros. Um laço `for` é suficiente; `while` não é obrigatório.
- **Funções** definidas com `def`, **Expressões Regulares** (`re`) e **datetime**. A solução pode ser um script `.py` ou notebook `.ipynb`, sempre com Python nativo. Gráficos, margem, treinamento de modelos e união de arquivos não são exigidos.

### Arquivo `README.md` (documentação)

Um arquivo de texto explicativo escrito em Markdown no repositório contendo:

- **Descrição do projeto:** Explique o problema da Festa em Cena, o objetivo do programa, o significado de uma linha e de quatro colunas à sua escolha. Documente as regras adotadas para textos, valores e datas. Custos e descontos estão no CSV, mas seu uso é opcional.
- **Guia de execução e resultados:** Explique como abrir e executar o projeto, onde colocar o CSV e quais arquivos são necessários. Apresente os resultados, a conclusão sobre entrega sem data e duas descobertas com evidência numérica, interpretação e limitação. Não confunda unidades com pedidos ou a base fictícia com o mercado real.

**Regra de submissão:** Crie um repositório público no GitHub com os arquivos do código, `README.md` e `halloween_vendas.csv`. Registre o desenvolvimento com commits de mensagens compreensíveis. Envie o link no AVA, na tarefa **"Módulo 1 - Mini-Projeto Avaliativo"**, até o prazo publicado pela coordenação. A organização dos commits fica a critério do estudante. Consulte no AVA se a realização será individual ou em grupo.

---

## 4. Requisitos das tarefas

Para apoiar a sua organização e o gerenciamento de tempo, recomenda-se dividir a execução do projeto nas seguintes etapas (Sprints):

| Sprint | Foco | Entrega parcial |
|--------|------|-----------------|
| **Sprint 1** (Configuração e ingestão) | Crie o repositório, organize a pasta e leia o CSV com `csv.DictReader`. Confira o total de linhas e mostre três registros. | Leitura funcionando e significado dos dados explicado. |
| **Sprint 2** (Transformação de strings) | Crie funções para limpar categorias com `.strip()`, `.lower()` e `re.sub()`, preencher vazios e padronizar canais. | Exemplos de antes e depois e contagens de correções. |
| **Sprint 3** (Nulos e validação) | Verifique quantidade e preço, marque ou separe problemas e documente a regra. | Contagens por campo e por pedido, com processamento que continua após erros. |
| **Sprint 4** (Regras de negócio e datas) | Converta timestamps, extraia suas partes, investigue entrega sem data e conte pedidos por canal e ano-mês. | Hipótese respondida e duas descobertas sustentadas por números. |

---

## 5. Gravação de vídeo

Além do desenvolvimento deste sistema você deverá gravar um **vídeo**, com tempo máximo de **7 minutos**, abordando os seguintes questionamentos:

1. Qual o objetivo dessa análise? E demonstração de funcionamento.
2. O que deve ser realizado para executar a análise? Quais pontos são importantes.
3. Como você organizou as tarefas antes de começar a desenvolver?
4. Quais as branches você criou e quais os objetivos para cada uma?
5. Você acha que faltou algo no seu código que você poderia melhorar?

---

## 6. Critérios de avaliação

A tabela abaixo apresenta os critérios que serão avaliados durante a correção do projeto. O mesmo possui variação de nota de **0** (zero) a **10** (dez) como nota mínima e máxima, e possui **peso de 25%** sobre a avaliação do módulo. Neste item devem ser listadas tarefas em formato de Sprint para que os estudantes possam realizar durante o período de execução do Mini-projeto Avaliativo, seguindo as orientações e critérios disponibilizados neste arquivo.

Serão desconsiderados e atribuída a nota **0** (zero) os projetos que apresentarem plágio de soluções encontradas na internet ou de outros colegas. Lembre-se: você está livre para utilizar outras soluções como base, mas **não é permitida a cópia**.

### Documentação do projeto

| Nº | Critério de avaliação | 0 | 2,00 |
|----|------------------------|---|------|
| 1 | **Versionamento e documentação** | Não entregou o repositório no GitHub contendo os arquivos organizados e um `README.md` explicativo com a reflexão teórica obrigatória sobre ML e qualidade de dados. | Entregou o repositório no GitHub contendo os arquivos organizados e um `README.md` explicativo com a reflexão teórica obrigatória sobre ML e qualidade de dados. |
| 2 | **Vídeo** | Não fez vídeo | Entregou o vídeo explicando os itens solicitados no item 5. |

### Desenvolvimento do projeto

| Nº | Critério de avaliação | 0 | 0,5 | 1,0 | 2 |
|----|------------------------|---|-----|-----|---|
| 2 | **Manipulação de arquivos CSV** | Não realizou a leitura e extração dos arquivos de dados usando `pd.read_csv()`, da biblioteca Pandas. | Realizou a leitura e extração dos arquivos de dados de forma parcialmente dados usando `pd.read_csv()`. | Realizou a leitura e extração dos arquivos de dados de forma estruturada e nativa dados usando `pd.read_csv()`. | — |
| 3 | **Tratamento de nulos e condicionais** | Não implementou a lógica (`if`/`else`) para preencher categorias vazias com "Sem Categoria" e não tratou os nulos das dimensões físicas, justificando a escolha. | Implementou parcialmente a lógica (`if`/`else`) para preencher categorias vazias com "Sem Categoria" e tratou parcialmente os nulos das dimensões físicas, justificando a escolha. | Implementou a lógica (`if`/`else`) para preencher categorias vazias com "Sem Categoria" e tratou corretamente os nulos das dimensões físicas, justificando a escolha. | — |
| 4 | **Regras de negócio e datas** | Não validou a regra dos pedidos cancelados separando os registros, e não converteu com sucesso a string de data de aprovação utilizando o módulo `datetime`. | Validou parcialmente a regra dos pedidos cancelados separando os registros, e converteu parcialmente a string de data de aprovação utilizando o módulo `datetime`. | Validou a regra dos pedidos cancelados separando os registros, e converteu com sucesso a string de data de aprovação utilizando o módulo `datetime`. | — |
| 5 | **Limpeza de strings** | Não aplicou corretamente os métodos de string e o módulo `re` (Regex) na padronização das categorias. | Aplicou parcialmente os métodos de string e o módulo `re` (Regex) na padronização das categorias. | Aplicou corretamente os métodos de string e o módulo `re` (Regex) na padronização das categorias. | — |
| 6 | **Report.md** | O código não possui o `report.md` | Possui `report.md`, mas não atende aos requisitos. | — | O `Report.md` atende aos requisitos. |

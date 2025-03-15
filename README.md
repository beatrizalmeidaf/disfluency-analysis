# Análise e Processamento de Transcrições com Disfluências

Esse repositório contém dois scripts Python para análise e processamento de transcrições com disfluências em arquivos CSV:

- **`analisar-expressoes.py`**: Conta a frequência de expressões de fala espontânea em uma coluna de um arquivo CSV.
- **`add-expressoes.py`**: Modifica transcrições adicionando tags de expressões espontâneas e calcula a taxa de erro de caracteres (CER).

## Requisitos

Antes de executar os scripts, instale as dependências necessárias:

```sh
pip install pandas tqdm torchmetrics num2words jiwer
```

## Uso dos Scripts

### `analisar-expressoes.py`

Esse script analisa a ocorrência de expressões de fala espontânea dentro de uma coluna específica de um arquivo CSV.

#### Uso:

```sh
python analisar-expressoes.py caminho/do/arquivo.csv nome_da_coluna
```

#### Exemplo:

```sh
python analisar-expressoes.py transcricoes.csv transcription-w2v
```

#### O que ele faz:
- Lê um arquivo CSV e uma coluna específica.
- Conta a ocorrência de expressões como "tá", "né", "ué", etc.
- Exibe a contagem e a porcentagem de cada expressão em relação ao total de palavras.

### `add-expressoes.py`

Esse script processa um arquivo CSV contendo transcrições e adiciona expressões espontâneas ao texto de referência para melhor comparação. Também calcula a taxa de erro de caracteres (CER) antes e depois da modificação.

#### Uso:

```sh
python add-expressoes.py input.csv output.csv coluna_referencia coluna_analisada
```

#### Exemplo:

```sh
python add-expressoes.py transcricoes.csv resultado.csv transcription-whisper transcription-w2v
```

#### O que ele faz:
- Lê um arquivo CSV e as colunas de transcrição de referência e analisada.
- Normaliza os textos para melhor análise.
- Adiciona tags de expressões espontâneas no texto de referência.
- Calcula a taxa de erro de caracteres (CER) antes e depois da modificação.
- Salva os resultados em um novo arquivo CSV.


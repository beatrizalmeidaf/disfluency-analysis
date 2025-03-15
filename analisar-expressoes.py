import pandas as pd
import re
import argparse

# Lista de expressões de fala espontânea
expressoes = ["tá", "né", "ué", "tipo", "poxa", "pô", 
              "daí", "aí", "hein", "aham", "ixi",  
              "puxa", "ô", "caraca", "opa", "beleza", 
              "vixe", "eita", "ó", "eh"]

# Configuração dos argumentos de linha de comando
parser = argparse.ArgumentParser(description="Análise de expressões em um CSV")
parser.add_argument("csv_file", type=str, help="Caminho do arquivo CSV")
parser.add_argument("column_name", type=str, help="Nome da coluna para análise")
args = parser.parse_args()

# Carregar CSV
df = pd.read_csv(args.csv_file, delimiter='|')

# Verificar se a coluna existe no DataFrame
if args.column_name not in df.columns:
    raise ValueError(f"A coluna '{args.column_name}' não foi encontrada no arquivo CSV.")

# Função para verificar se a linha contém uma expressão como palavra isolada
def contem_expressao(texto, expressao):
    if isinstance(texto, str):  
        padrao = r'\b' + re.escape(expressao) + r'\b'  
        return re.search(padrao, texto) is not None
    return False

# Função para contar o número total de palavras
def contar_palavras(texto):
    if isinstance(texto, str):
        return len(texto.split())
    return 0

# Contagem total de palavras na coluna especificada
total_palavras = df[args.column_name].apply(contar_palavras).sum()
print(f"Total de palavras na coluna '{args.column_name}': {total_palavras}")

# Dicionário para armazenar a contagem de cada expressão e suas porcentagens
contagem_expressoes = {}

# Inicializa as contagens e calcula as porcentagens
for expressao in expressoes:
    contagem = df[args.column_name].apply(lambda x: contem_expressao(x, expressao)).sum()
    porcentagem = (contagem / total_palavras) * 100 if total_palavras > 0 else 0
    contagem_expressoes[expressao] = (contagem, porcentagem)

# Exibe a contagem e a porcentagem final de todas as expressões
print("\nResumo da contagem de expressões:")
for expressao, (contagem, porcentagem) in contagem_expressoes.items():
    print(f"'{expressao}': {contagem} ocorrência(s) ({porcentagem:.4f}%)")

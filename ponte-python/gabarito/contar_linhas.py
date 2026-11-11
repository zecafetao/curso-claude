"""Informa quantas linhas e colunas tem um arquivo CSV separado por ponto e vírgula.

Solução de referência do módulo P.1. Tente escrever a sua versão antes de ler.

Uso:
    python contar_linhas.py arquivo.csv
"""

import csv
import sys

caminho = sys.argv[1]

with open(caminho, encoding="utf-8", newline="") as arquivo:
    leitor = csv.reader(arquivo, delimiter=";")
    cabecalho = next(leitor)
    quantidade_de_linhas = 0
    for linha in leitor:
        quantidade_de_linhas = quantidade_de_linhas + 1

print(f"Arquivo: {caminho}")
print(f"Colunas: {len(cabecalho)}")
print(f"Linhas de dados: {quantidade_de_linhas}")
print("Nomes das colunas:")
for nome in cabecalho:
    print(f"  - {nome}")

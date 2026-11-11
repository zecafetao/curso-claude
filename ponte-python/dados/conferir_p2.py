"""Confere as funções do módulo P.2 contra os casos de casos_p2.csv.

Copie este arquivo e o casos_p2.csv para a pasta em que está o seu validacao.py e rode:
    python conferir_p2.py
"""

import csv

import validacao

with open("casos_p2.csv", encoding="utf-8", newline="") as arquivo:
    casos = list(csv.DictReader(arquivo, delimiter=";"))

acertos = 0
for caso in casos:
    funcao = getattr(validacao, caso["funcao"])
    obtido = funcao(caso["entrada"])
    if obtido is None:
        obtido = ""
    obtido = str(obtido)
    if obtido == caso["esperado"]:
        acertos = acertos + 1
    else:
        print(f"ERRO em {caso['funcao']}({caso['entrada']!r}): esperado {caso['esperado']!r}, obtido {obtido!r}")

print(f"{acertos} de {len(casos)} casos corretos")

"""Consulta cidade e UF dos CEPs de uma base em uma API pública.

Solução de referência do módulo P.4. Tente escrever a sua versão antes de ler.

Uso:
    python consultar_cep.py base_bruta.csv ceps.csv
"""

import sys
import time

import pandas as pd
import requests

import validacao as v

URL = "https://brasilapi.com.br/api/cep/v1/{cep}"
PAUSA_ENTRE_CONSULTAS = 0.5  # segundos; evita sobrecarregar um serviço gratuito


def consultar_cep(cep):
    """Devolve um dicionário com cep, cidade, uf e a situação da consulta."""
    resultado = {"cep": cep, "cidade": "", "uf": "", "situacao": ""}
    try:
        resposta = requests.get(URL.format(cep=cep), timeout=10)
    except requests.exceptions.RequestException as erro:
        resultado["situacao"] = f"falha de conexão ({type(erro).__name__})"
        return resultado

    if resposta.status_code == 404:
        resultado["situacao"] = "não encontrado"
        return resultado
    if resposta.status_code != 200:
        resultado["situacao"] = f"erro {resposta.status_code}"
        return resultado

    dados = resposta.json()
    resultado["cidade"] = dados["city"]
    resultado["uf"] = dados["state"]
    resultado["situacao"] = "encontrado"
    return resultado


def ceps_distintos(caminho_base):
    """Lê a base bruta e devolve a lista ordenada de CEPs válidos, sem repetição."""
    base = pd.read_csv(caminho_base, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    ceps = set(base["CEP"].map(v.padronizar_cep))
    ceps.discard("")
    return sorted(ceps)


def consultar_todos(ceps):
    """Consulta cada CEP uma única vez, com pausa entre as consultas."""
    resultados = []
    for posicao, cep in enumerate(ceps, start=1):
        resultado = consultar_cep(cep)
        print(f"{posicao}/{len(ceps)} {cep}: {resultado['situacao']}")
        resultados.append(resultado)
        time.sleep(PAUSA_ENTRE_CONSULTAS)
    return pd.DataFrame(resultados)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python consultar_cep.py base_bruta.csv ceps.csv")
        sys.exit(1)
    tabela = consultar_todos(ceps_distintos(sys.argv[1]))
    tabela.to_csv(sys.argv[2], sep=";", index=False, encoding="utf-8")
    print(tabela["situacao"].value_counts().to_string())

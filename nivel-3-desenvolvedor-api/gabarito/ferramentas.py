"""Funções que servem de ferramentas ao assistente do módulo 3.4.

Regra de desenho: as ferramentas devolvem contagens e resumos, nunca linhas com dados de pessoas.
O que uma ferramenta devolve é enviado à API.

Solução de referência do módulo 3.4. Executado e testado.
"""

import csv
import os
import re
from pathlib import Path

import validacao as v

# Pasta em que estão os dados. As ferramentas só leem arquivos de dentro dela.
PASTA_DADOS = Path(os.environ.get("PASTA_DADOS_N3", "dados_n3"))

COLUNAS_DO_LAYOUT = ["email", "telefone", "area", "origem", "consentimento", "data_consentimento"]
COLUNAS_PERMITIDAS = ["area", "uf", "origem", "consentimento", "cidade", "empresa"]
AREAS = ["Compras", "Produção", "Marketing", "Comercial", "Diretoria", "Outros"]
ORIGENS = ["Credenciamento", "Expositor", "Site", "Evento", "Compra de base"]
FORMATO_TELEFONE = re.compile(r"^\+55\d{10,11}$")


def ler_csv(nome_arquivo):
    """Lê um CSV da pasta de dados. Aceita só o nome do arquivo, sem caminho."""
    if Path(nome_arquivo).name != nome_arquivo or not nome_arquivo.endswith(".csv"):
        raise ValueError("Informe só o nome de um arquivo .csv da pasta de dados, sem caminho.")
    caminho = PASTA_DADOS / nome_arquivo
    if not caminho.exists():
        raise ValueError(f"O arquivo {nome_arquivo} não existe na pasta de dados.")
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo, delimiter=";"))


def resumir_base(coluna):
    """Conta os contatos da base tratada por valor de uma coluna."""
    if coluna not in COLUNAS_PERMITIDAS:
        return {"erro": f"Coluna não permitida. Use uma destas: {', '.join(COLUNAS_PERMITIDAS)}."}
    base = ler_csv("base_contatos_tratada.csv")
    contagem = {}
    for linha in base:
        valor = linha[coluna] or "(vazio)"
        contagem[valor] = contagem.get(valor, 0) + 1
    ordenada = dict(sorted(contagem.items(), key=lambda item: -item[1])[:20])
    return {"coluna": coluna, "total_de_contatos": len(base), "valores_distintos": len(contagem), "contagem": ordenada}


def contar_contatos(area="", uf="", consentimento="", origem=""):
    """Conta os contatos da base tratada que cumprem todos os filtros informados."""
    filtros = {"area": area, "uf": uf.upper(), "consentimento": consentimento.upper(), "origem": origem}
    filtros = {coluna: valor for coluna, valor in filtros.items() if valor != ""}
    base = ler_csv("base_contatos_tratada.csv")
    quantidade = 0
    for linha in base:
        if all(linha[coluna] == valor for coluna, valor in filtros.items()):
            quantidade += 1
    return {"filtros": filtros, "quantidade": quantidade, "total_de_contatos": len(base)}


def validar_arquivo(nome_arquivo):
    """Confere um arquivo de importação contra o layout do CRM e conta os problemas por tipo."""
    try:
        linhas = ler_csv(nome_arquivo)
    except ValueError as erro:
        return {"erro": str(erro)}
    if not linhas or any(coluna not in linhas[0] for coluna in COLUNAS_DO_LAYOUT):
        return {"erro": f"O arquivo {nome_arquivo} não tem as colunas do layout de importação."}

    problemas = {
        "e-mail inválido": 0,
        "e-mail repetido": 0,
        "telefone fora do formato": 0,
        "área fora da lista": 0,
        "origem fora da lista": 0,
        "consentimento S sem data": 0,
    }
    vistos, com_problema = set(), 0
    for linha in linhas:
        achados = []
        if not v.email_valido(linha["email"]):
            achados.append("e-mail inválido")
        elif linha["email"] in vistos:
            achados.append("e-mail repetido")
        vistos.add(linha["email"])
        if linha["telefone"] != "" and not FORMATO_TELEFONE.match(linha["telefone"]):
            achados.append("telefone fora do formato")
        if linha["area"] not in AREAS:
            achados.append("área fora da lista")
        if linha["origem"] not in ORIGENS:
            achados.append("origem fora da lista")
        if linha["consentimento"] == "S" and linha["data_consentimento"] == "":
            achados.append("consentimento S sem data")
        for achado in achados:
            problemas[achado] += 1
        if achados:
            com_problema += 1
    return {"arquivo": nome_arquivo, "linhas": len(linhas), "linhas_com_problema": com_problema, "problemas": problemas}

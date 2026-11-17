"""Monta o banco SQLite da campanha a partir das exportações em CSV.

Solução de referência do módulo 4.3. Executado e testado.

Uso:
    python montar_banco.py dados_n4 dados_n4/campanha.db

O banco é recriado do zero a cada execução. Os arquivos CSV não são alterados.
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd

import relatorio_mensal as rm

DISPAROS_WHATSAPP = [
    # disparo, data, tema. Dados fictícios da campanha de WhatsApp da Expo Modelo 2026.
    ("D1", "2026-10-13", "Convite para credenciamento"),
    ("D2", "2026-10-17", "Programação e rodada de negócios"),
    ("D3", "2026-10-19", "Lembrete na véspera da feira"),
]


def ler_csv(caminho, separador=";"):
    """Lê um CSV com tudo como texto."""
    return pd.read_csv(caminho, sep=separador, dtype=str, keep_default_na=False, encoding="utf-8")


def tabela_disparos_email(pasta):
    """Junta as exportações de e-mail dos meses em uma tabela, com mês e público."""
    partes = []
    for arquivo in sorted(Path(pasta).glob("desempenho_email_*.csv")):
        base = rm.ler_desempenho(arquivo)
        base["mes"] = base["data_envio"].dt.strftime("%Y-%m")
        base["data_envio"] = base["data_envio"].dt.strftime("%Y-%m-%d")
        partes.append(base)
    tabela = pd.concat(partes, ignore_index=True)
    colunas = ["disparo", "mes", "data_envio", "hora_envio", "publico", "enviadas", "entregues",
               "aberturas_unicas", "cliques_unicos", "descadastros"]
    return tabela[colunas]


def montar(pasta, caminho_banco):
    """Cria o banco com as tabelas da campanha. Devolve a quantidade de linhas por tabela."""
    pasta, caminho_banco = Path(pasta), Path(caminho_banco)
    caminho_banco.unlink(missing_ok=True)
    tabelas = {
        "disparos_email": tabela_disparos_email(pasta),
        "disparos_whatsapp": pd.DataFrame(DISPAROS_WHATSAPP, columns=["disparo", "data_envio", "tema"]),
        "whatsapp_tentativas": ler_csv(pasta / "feira_whatsapp_tentativas.csv"),
        "credenciados": ler_csv(pasta / "feira_credenciados.csv"),
        "visitantes": ler_csv(pasta / "feira_visitantes.csv"),
        "inscritos_evento": ler_csv(pasta / "feira_inscritos_evento.csv"),
    }
    tabelas["whatsapp_tentativas"]["tentativa"] = pd.to_numeric(tabelas["whatsapp_tentativas"]["tentativa"])
    with sqlite3.connect(caminho_banco) as conexao:
        for nome, tabela in tabelas.items():
            tabela.to_sql(nome, conexao, index=False)
    return {nome: len(tabela) for nome, tabela in tabelas.items()}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python montar_banco.py pasta_dos_csv caminho_do_banco.db")
        sys.exit(1)
    for nome, linhas in montar(sys.argv[1], sys.argv[2]).items():
        print(f"{nome}: {linhas} linhas")

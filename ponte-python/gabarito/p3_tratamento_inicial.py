"""Primeiro tratamento da base com pandas: limpar, filtrar, remover duplicados e exportar.

Solução de referência do módulo P.3. Tente escrever a sua versão antes de ler.

Uso:
    python p3_tratamento_inicial.py base_bruta.csv descadastrados.xlsx saida.csv
"""

import sys

import pandas as pd

import validacao as v

base = pd.read_csv(sys.argv[1], sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
descadastrados = pd.read_excel(sys.argv[2], dtype=str)
print(f"Linhas lidas: {len(base)}")

base = base.rename(
    columns={
        "Nome Completo": "nome_completo",
        "E-mail": "email",
        "Telefone": "telefone",
        "Empresa": "empresa",
        "UF": "uf",
        "Origem": "origem",
    }
)

# Limpeza de texto com os métodos de texto do pandas
base["email"] = base["email"].str.strip().str.lower()
base["nome_completo"] = base["nome_completo"].str.strip().str.replace(r"\s+", " ", regex=True).str.title()
base["empresa"] = base["empresa"].str.strip()
base["uf"] = base["uf"].str.strip().str.upper()
base["origem"] = base["origem"].str.strip()

# Funções do módulo P.2 aplicadas a cada valor da coluna
telefones = base["telefone"].map(v.padronizar_telefone)
base["telefone"] = telefones.fillna("")

# 1. E-mails inválidos
email_ok = base["email"].map(v.email_valido)
print(f"E-mails inválidos: {(~email_ok).sum()}")
base = base[email_ok]

# 2. Descadastrados
descadastrados["email"] = descadastrados["email"].str.strip().str.lower()
marcada = base.merge(descadastrados[["email"]], on="email", how="left", indicator=True)
print(f"Descadastrados: {(marcada['_merge'] == 'both').sum()}")
base = marcada[marcada["_merge"] == "left_only"].drop(columns="_merge")

# 3. Duplicados
antes = len(base)
base = base.drop_duplicates(subset="email", keep="first")
print(f"Duplicados: {antes - len(base)}")

colunas = ["email", "nome_completo", "telefone", "empresa", "uf", "origem"]
base[colunas].to_csv(sys.argv[3], sep=";", index=False, encoding="utf-8")
print(f"Linhas gravadas: {len(base)}")
print(f"Com telefone: {(base['telefone'] != '').sum()}")

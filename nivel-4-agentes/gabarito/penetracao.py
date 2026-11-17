"""Calcula a penetração da feira no universo de empresas parecidas, por setor, em uma região.

Solução de referência do módulo 4.2. A conta é feita por código, e não pelo agente: o agente encontra os
tamanhos do universo, com fonte; este script junta com a base de expositores e calcula.

Uso:
    python penetracao.py dados_n4/empresas_expositoras.csv dados_n4/universo_sul_exemplo.csv Sul

O arquivo do universo tem as colunas setor;empresas_universo;fonte. Setor sem número ou sem fonte fica como
lacuna: a penetração não é calculada.
"""

import sys

import pandas as pd

import perfil_expositores as pe


def penetracao(arq_expositores, arq_universo, regiao):
    base = pe.ler_empresas(arq_expositores)
    expositores = base[base["regiao"] == regiao].groupby("setor").size().rename("expositores")
    universo = pd.read_csv(arq_universo, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    universo = universo.set_index("setor")
    tabela = universo.join(expositores, how="outer")
    tabela["expositores"] = tabela["expositores"].fillna(0).astype(int)
    com_fonte = (tabela["empresas_universo"].fillna("") != "") & (tabela["fonte"].fillna("") != "")
    tabela["empresas_universo"] = pd.to_numeric(tabela["empresas_universo"].where(com_fonte)).astype("Int64")
    tabela["penetracao_pct"] = (100 * tabela["expositores"] / tabela["empresas_universo"]).round(2)
    tabela["situacao"] = com_fonte.map({True: "calculado", False: "lacuna: universo sem número ou sem fonte"})
    return tabela[["expositores", "empresas_universo", "penetracao_pct", "situacao", "fonte"]]


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python penetracao.py empresas_expositoras.csv universo.csv Região")
        sys.exit(1)
    resultado = penetracao(*sys.argv[1:])
    print(resultado.drop(columns="fonte").to_string())

"""Monta as tabelas do perfil de empresas expositoras.

Solução de referência do módulo P.6 (parte B). Tente escrever a sua versão antes de ler.

Uso:
    python perfil_expositores.py empresas_expositoras.csv
"""

import sys

import pandas as pd

REGIOES = {
    "SP": "Sudeste", "RJ": "Sudeste", "MG": "Sudeste", "ES": "Sudeste",
    "PR": "Sul", "SC": "Sul", "RS": "Sul",
    "BA": "Nordeste", "PE": "Nordeste", "CE": "Nordeste",
    "GO": "Centro-Oeste", "DF": "Centro-Oeste",
}
LIMITES = [0, 4_800_000, 30_000_000, 300_000_000, float("inf")]
FAIXAS = ["Até R$ 4,8 mi", "R$ 4,8 mi a R$ 30 mi", "R$ 30 mi a R$ 300 mi", "Acima de R$ 300 mi"]


def ler_empresas(caminho):
    """Lê a base e converte faturamento, funcionários e data de abertura."""
    base = pd.read_csv(caminho, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    sem_milhar = base["faturamento_estimado"].str.replace(".", "", regex=False)
    base["faturamento"] = pd.to_numeric(sem_milhar.str.replace(",", ".", regex=False))
    base["funcionarios"] = pd.to_numeric(base["funcionarios"])
    base["data_abertura"] = pd.to_datetime(base["data_abertura"], format="%d/%m/%Y")
    base["regiao"] = base["uf"].map(REGIOES)
    base["faixa_faturamento"] = pd.cut(base["faturamento"], bins=LIMITES, labels=FAIXAS)
    return base


def participacao(base, coluna):
    """Contagem e participação percentual de cada valor da coluna."""
    tabela = base[coluna].value_counts(sort=False).rename("empresas").to_frame()
    tabela["participacao"] = (100 * tabela["empresas"] / len(base)).round(1)
    return tabela.sort_values("empresas", ascending=False)


if __name__ == "__main__":
    base = ler_empresas(sys.argv[1])
    print(f"Empresas: {len(base)}")

    for coluna in ["porte", "setor", "regiao", "faixa_faturamento"]:
        print(f"\n{coluna.upper()}")
        print(participacao(base, coluna).to_string())

    medio_grande = base["porte"].isin(["Média", "Grande"]).sum()
    acima_30 = (base["faturamento"] > 30_000_000).sum()
    em_sp = (base["uf"] == "SP").sum()
    antes_2000 = (base["data_abertura"].dt.year < 2000).sum()

    print(f"\nMédio e grande porte: {medio_grande} ({100 * medio_grande / len(base):.1f}%)")
    print(f"Faturamento estimado acima de R$ 30 milhões: {acima_30} ({100 * acima_30 / len(base):.1f}%)")
    print(f"São Paulo: {em_sp} ({100 * em_sp / len(base):.1f}%)")
    print(f"Abertas antes de 2000: {antes_2000}")
    print(f"Faturamento total: R$ {base['faturamento'].sum() / 1e9:.2f} bilhões")
    print(f"Funcionários (mediana): {int(base['funcionarios'].median())}")
    print("\nFaturamento médio por porte, em R$ milhões:")
    print((base.groupby("porte")["faturamento"].mean() / 1e6).round(1).to_string())

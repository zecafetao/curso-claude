"""Calcula os indicadores do relatório mensal de e-mail a partir da exportação por disparo.

Solução de referência do módulo P.6 (parte A). Tente escrever a sua versão antes de ler.

Uso:
    python relatorio_mensal.py desempenho_email_outubro.csv
    python relatorio_mensal.py desempenho_email_outubro.csv desempenho_email_setembro.csv
"""

import sys

import pandas as pd

CONTAGENS = ["enviadas", "entregues", "aberturas_unicas", "cliques_unicos", "descadastros"]
NOMES_PUBLICO = {
    "Prospeccao": "Prospecção",
    "Credenciamento": "Credenciamento",
    "PreCredenciado": "Pré-credenciado",
    "Reativacao": "Reativação",
    "Expositor": "Expositor",
}
DIAS = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
MINIMO_DE_ENVIOS = 10       # abaixo disso, o disparo é resposta automática ou teste
LIMITE_DE_CLIQUE = 15.0     # acima disso, a taxa de clique é sinalizada como possível clique automático


def ler_desempenho(caminho):
    """Lê a exportação e converte contagens em número e a data em data."""
    base = pd.read_csv(caminho, dtype=str, keep_default_na=False, encoding="utf-8")
    for coluna in CONTAGENS:
        base[coluna] = pd.to_numeric(base[coluna])
    base["data_envio"] = pd.to_datetime(base["data_envio"], format="%Y-%m-%d")
    base["hora"] = pd.to_numeric(base["hora_envio"].str[:2], errors="coerce")
    base["dia_semana"] = base["data_envio"].dt.dayofweek.map(DIAS)
    base["publico"] = base["disparo"].str.split("_").str[3].map(NOMES_PUBLICO).fillna("Outros")
    return base


def acrescentar_taxas(tabela):
    """Calcula as três taxas a partir das contagens, em percentual com uma casa decimal."""
    tabela = tabela.copy()
    tabela["taxa_entrega"] = (100 * tabela["entregues"] / tabela["enviadas"]).round(1)
    tabela["taxa_abertura"] = (100 * tabela["aberturas_unicas"] / tabela["entregues"]).round(1)
    tabela["taxa_clique"] = (100 * tabela["cliques_unicos"] / tabela["entregues"]).round(1)
    return tabela


def separar_excluidos(base):
    """Devolve (considerados, excluídos) pela regra do mínimo de envios."""
    excluidos = base[base["enviadas"] < MINIMO_DE_ENVIOS]
    considerados = base[base["enviadas"] >= MINIMO_DE_ENVIOS]
    return considerados, excluidos


def indicadores_gerais(considerados):
    """Uma linha com os totais e as taxas do período."""
    totais = considerados[CONTAGENS].sum().to_frame().T
    totais.insert(0, "disparos", len(considerados))
    return acrescentar_taxas(totais)


def por_grupo(considerados, coluna):
    """Totais e taxas por grupo. A taxa do grupo é soma dividida por soma, não média de taxas."""
    tabela = considerados.groupby(coluna, as_index=False).agg(
        disparos=("disparo", "count"),
        enviadas=("enviadas", "sum"),
        entregues=("entregues", "sum"),
        aberturas_unicas=("aberturas_unicas", "sum"),
        cliques_unicos=("cliques_unicos", "sum"),
        descadastros=("descadastros", "sum"),
    )
    return acrescentar_taxas(tabela).sort_values("enviadas", ascending=False).reset_index(drop=True)


def com_total(tabela, coluna):
    """Acrescenta a linha de total a uma tabela por grupo."""
    total = tabela[["disparos"] + CONTAGENS].sum().to_frame().T
    total.insert(0, coluna, "Total")
    return pd.concat([tabela, acrescentar_taxas(total)], ignore_index=True)


def anomalias(considerados):
    """Disparos com taxa de clique acima do limite. Eles continuam nos totais."""
    tabela = acrescentar_taxas(considerados)
    return tabela[tabela["taxa_clique"] > LIMITE_DE_CLIQUE]


def comparar(atual, anterior):
    """Compara os indicadores gerais de dois períodos. Diferenças de taxa em pontos percentuais."""
    linhas = pd.concat([indicadores_gerais(anterior), indicadores_gerais(atual)], ignore_index=True)
    linhas.insert(0, "periodo", ["anterior", "atual"])
    diferenca = {"periodo": "diferença"}
    for coluna in ["taxa_entrega", "taxa_abertura", "taxa_clique"]:
        diferenca[coluna] = round(linhas.loc[1, coluna] - linhas.loc[0, coluna], 1)
    diferenca["enviadas"] = round(100 * (linhas.loc[1, "enviadas"] / linhas.loc[0, "enviadas"] - 1), 1)
    return linhas, diferenca


def numero(valor):
    """Formata um inteiro com ponto de milhar: 50812 -> 50.812."""
    return f"{int(valor):,}".replace(",", ".")


def percentual(valor):
    """Formata uma taxa com vírgula decimal: 52.6 -> 52,6%."""
    return f"{valor:.1f}%".replace(".", ",")


def sinal(valor):
    """Formata uma diferença com sinal e vírgula decimal: 6.9 -> +6,9."""
    return f"{valor:+.1f}".replace(".", ",")


def formatar(tabela):
    """Devolve uma cópia da tabela com contagens e taxas no formato do relatório."""
    tabela = tabela.copy()
    for coluna in tabela.columns:
        if coluna.startswith("taxa_"):
            tabela[coluna] = tabela[coluna].map(percentual)
        elif coluna in CONTAGENS or coluna == "disparos":
            tabela[coluna] = tabela[coluna].map(numero)
    return tabela


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Uso: python relatorio_mensal.py mes_atual.csv [mes_anterior.csv]")
        sys.exit(1)

    considerados, excluidos = separar_excluidos(ler_desempenho(sys.argv[1]))

    print("INDICADORES GERAIS")
    print(formatar(indicadores_gerais(considerados)).to_string(index=False))

    print("\nDISPAROS EXCLUÍDOS")
    print(excluidos[["disparo", "enviadas"]].to_string(index=False))

    print("\nPOR PÚBLICO")
    print(formatar(com_total(por_grupo(considerados, "publico"), "publico")).to_string(index=False))

    print("\nPOSSÍVEL CLIQUE AUTOMÁTICO")
    print(formatar(anomalias(considerados))[["disparo", "entregues", "cliques_unicos", "taxa_clique"]].to_string(index=False))

    print("\nPOR DIA DA SEMANA")
    print(formatar(por_grupo(considerados, "dia_semana")).to_string(index=False))

    if len(sys.argv) == 3:
        anterior, _ = separar_excluidos(ler_desempenho(sys.argv[2]))
        linhas, diferenca = comparar(considerados, anterior)
        print("\nCOMPARAÇÃO COM O MÊS ANTERIOR")
        print(formatar(linhas).to_string(index=False))
        print(
            f"Enviadas: {sinal(diferenca['enviadas'])}%"
            f" | entrega: {sinal(diferenca['taxa_entrega'])} p.p."
            f" | abertura: {sinal(diferenca['taxa_abertura'])} p.p."
            f" | clique: {sinal(diferenca['taxa_clique'])} p.p."
        )

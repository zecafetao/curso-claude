"""Gera os gráficos do relatório mensal de e-mail, sempre no mesmo padrão.

Solução de referência do módulo P.8. Tente escrever a sua versão antes de ler.

Uso:
    python graficos_relatorio.py mes_atual.csv mes_anterior.csv pasta_de_saida

Cada gráfico é gravado em PNG, com a tabela dos valores desenhados em um CSV de mesmo nome.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")                     # grava imagens sem abrir janela
import matplotlib.pyplot as plt
import pandas as pd

import relatorio_mensal as rm

# Padrão visual da Agência Modelo (fictício).
AMBAR = "#F59E0B"          # a série que o leitor deve ver primeiro
CINZA = "#8A8A8A"          # a série de comparação
GRAFITE = "#1F1F1F"        # texto
CINZA_TEXTO = "#555555"    # texto de apoio: eixos e legenda
CINZA_CLARO = "#E5E5E5"    # linhas de apoio

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]


# ---------- Padrão ----------

def nova_figura():
    """Cria a figura no formato dos slides, 16:9."""
    return plt.subplots(figsize=(8, 4.5))


def aplicar_padrao(ax, titulo, legenda_no_topo=False):
    """Aplica o padrão visual a um gráfico: título, cores de texto e linhas discretas."""
    distancia = 34 if legenda_no_topo else 14      # com legenda no topo, o título sobe para dar lugar a ela
    ax.set_title(titulo, loc="left", fontsize=14, fontweight="bold", color=GRAFITE, pad=distancia)
    for lado in ["top", "right", "left"]:
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(CINZA_CLARO)
    ax.tick_params(colors=CINZA_TEXTO, length=0, labelsize=10)
    ax.set_axisbelow(True)                 # as linhas de apoio ficam atrás das barras


def salvar(fig, caminho):
    """Grava a figura em PNG e libera a memória."""
    fig.tight_layout()
    fig.savefig(caminho, dpi=200, facecolor="white")
    plt.close(fig)


def nome_do_periodo(base):
    """Devolve o mês e o ano dos dados, como 'outubro de 2026'."""
    data = base["data_envio"].max()
    return f"{MESES[data.month - 1]} de {data.year}"


def eixo_percentual(valor, posicao):
    """Texto de um valor do eixo: 40 vira 40%."""
    return f"{valor:.0f}%"


def eixo_milhar(valor, posicao):
    """Texto de um valor do eixo: 50000 vira 50.000."""
    return rm.numero(valor)


# ---------- Tabelas: os valores que cada gráfico desenha ----------

def tabela_clique_por_publico(considerados):
    """Taxa de clique por público, da maior para a menor."""
    tabela = rm.por_grupo(considerados, "publico")[["publico", "entregues", "cliques_unicos", "taxa_clique"]]
    return tabela.sort_values("taxa_clique", ascending=False).reset_index(drop=True)


def tabela_abertura_comparada(atual, anterior):
    """Taxa de abertura por público nos dois meses, na ordem do volume do mês atual."""
    do_atual = rm.por_grupo(atual, "publico")[["publico", "taxa_abertura"]]
    do_anterior = rm.por_grupo(anterior, "publico")[["publico", "taxa_abertura"]]
    tabela = do_atual.merge(do_anterior, on="publico", how="left", suffixes=("_atual", "_anterior"))
    tabela["diferenca_pp"] = (tabela["taxa_abertura_atual"] - tabela["taxa_abertura_anterior"]).round(1)
    return tabela


def tabela_envios_acumulados(considerados):
    """E-mails enviados acumulados por dia do mês, do dia 1 ao 31."""
    por_dia = considerados.groupby(considerados["data_envio"].dt.day)["enviadas"].sum()
    acumulado = por_dia.reindex(range(1, 32), fill_value=0).cumsum()
    return pd.DataFrame({"dia": acumulado.index, "enviadas_acumuladas": acumulado.values})


# ---------- Gráficos ----------

def desenhar_clique_por_publico(tabela, periodo):
    """Barras horizontais ordenadas, uma cor, com o valor na ponta de cada barra."""
    fig, ax = nova_figura()
    tabela = tabela.iloc[::-1]             # o matplotlib desenha de baixo para cima
    barras = ax.barh(tabela["publico"], tabela["taxa_clique"], height=0.3, color=AMBAR)
    ax.bar_label(barras, labels=[rm.percentual(valor) for valor in tabela["taxa_clique"]],
                 padding=6, fontsize=11, color=GRAFITE)
    aplicar_padrao(ax, f"Taxa de clique por público — {periodo}")
    ax.spines["bottom"].set_visible(False)
    ax.xaxis.set_visible(False)            # todos os valores estão nos rótulos
    ax.tick_params(axis="y", labelsize=11, colors=GRAFITE)
    ax.set_xlim(0, tabela["taxa_clique"].max() * 1.15)
    return fig


def desenhar_abertura_comparada(tabela, periodo_atual, periodo_anterior):
    """Duas barras por público: o mês atual em destaque e o anterior em cinza."""
    fig, ax = nova_figura()
    tabela = tabela.iloc[::-1].reset_index(drop=True)
    posicoes = range(len(tabela))
    ax.barh([p - 0.17 for p in posicoes], tabela["taxa_abertura_anterior"], height=0.3,
            color=CINZA, label=periodo_anterior)
    barras = ax.barh([p + 0.17 for p in posicoes], tabela["taxa_abertura_atual"], height=0.3,
                     color=AMBAR, label=periodo_atual)
    ax.bar_label(barras, labels=[rm.percentual(valor) for valor in tabela["taxa_abertura_atual"]],
                 padding=6, fontsize=11, color=GRAFITE)
    aplicar_padrao(ax, "Taxa de abertura por público", legenda_no_topo=True)
    ax.set_yticks(list(posicoes), tabela["publico"])
    ax.tick_params(axis="y", labelsize=11, colors=GRAFITE)
    ax.xaxis.set_major_formatter(eixo_percentual)
    ax.grid(axis="x", color=CINZA_CLARO, linewidth=0.8)
    ax.set_xlim(0, 100)
    # A legenda segue a ordem das barras: a de cima primeiro.
    marcas, nomes = ax.get_legend_handles_labels()
    ax.legend(marcas[::-1], nomes[::-1], frameon=False, loc="lower left", bbox_to_anchor=(0, 1),
              borderaxespad=0, ncols=2, fontsize=10, labelcolor=CINZA_TEXTO)   # entre o título e as barras
    return fig


def desenhar_envios_acumulados(acumulado_atual, acumulado_anterior, periodo_atual, periodo_anterior):
    """Duas linhas em degraus, com o nome e o total no fim de cada uma."""
    fig, ax = nova_figura()
    series = [(acumulado_anterior, periodo_anterior, CINZA), (acumulado_atual, periodo_atual, AMBAR)]
    for tabela, periodo, cor in series:
        ax.step(tabela["dia"], tabela["enviadas_acumuladas"], where="post", color=cor, linewidth=2, label=periodo)
        total = tabela["enviadas_acumuladas"].iloc[-1]
        ax.plot(31, total, marker="o", markersize=7, color=cor, markeredgecolor="white", markeredgewidth=1.5)
        ax.annotate(f"{periodo.split(' de ')[0].capitalize()}: {rm.numero(total)}", (31, total),
                    xytext=(10, 0), textcoords="offset points", va="center", fontsize=11, color=GRAFITE)
    aplicar_padrao(ax, "E-mails enviados, acumulado no mês")
    ax.set_xlabel("Dia do mês", fontsize=10, color=CINZA_TEXTO)
    ax.set_xticks([1, 5, 10, 15, 20, 25, 31])
    ax.set_xlim(1, 39)                     # espaço à direita para os rótulos
    ax.set_ylim(0, None)
    ax.yaxis.set_major_formatter(eixo_milhar)
    ax.grid(axis="y", color=CINZA_CLARO, linewidth=0.8)
    ax.legend(frameon=False, loc="upper left", fontsize=10, labelcolor=CINZA_TEXTO)
    return fig


# ---------- Tudo junto ----------

def gerar_graficos(caminho_atual, caminho_anterior, pasta_saida):
    """Gera os três gráficos e as tabelas. Devolve a lista dos arquivos PNG gravados."""
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    atual, _ = rm.separar_excluidos(rm.ler_desempenho(caminho_atual))
    anterior, _ = rm.separar_excluidos(rm.ler_desempenho(caminho_anterior))
    periodo_atual, periodo_anterior = nome_do_periodo(atual), nome_do_periodo(anterior)

    clique = tabela_clique_por_publico(atual)
    abertura = tabela_abertura_comparada(atual, anterior)
    acumulado_atual = tabela_envios_acumulados(atual)
    acumulado_anterior = tabela_envios_acumulados(anterior)
    acumulado = acumulado_atual.merge(acumulado_anterior, on="dia", suffixes=("_atual", "_anterior"))

    trabalhos = [
        ("clique_por_publico", clique, desenhar_clique_por_publico(clique, periodo_atual)),
        ("abertura_por_publico", abertura, desenhar_abertura_comparada(abertura, periodo_atual, periodo_anterior)),
        ("envios_acumulados", acumulado,
         desenhar_envios_acumulados(acumulado_atual, acumulado_anterior, periodo_atual, periodo_anterior)),
    ]
    gravados = []
    for nome, tabela, figura in trabalhos:
        tabela.to_csv(pasta_saida / f"{nome}.csv", sep=";", index=False, encoding="utf-8")
        salvar(figura, pasta_saida / f"{nome}.png")
        gravados.append(pasta_saida / f"{nome}.png")
    return gravados


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python graficos_relatorio.py mes_atual.csv mes_anterior.csv pasta_de_saida")
        sys.exit(1)
    for arquivo in gerar_graficos(sys.argv[1], sys.argv[2], sys.argv[3]):
        print(f"Gravado: {arquivo}")

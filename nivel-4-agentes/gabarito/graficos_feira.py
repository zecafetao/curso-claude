"""Gráficos do report pós-feira, no mesmo padrão visual dos gráficos do módulo P.8.

Usado pelo projeto do Nível 4. Executado e testado.
"""

from pathlib import Path

import pandas as pd

import graficos_relatorio as gr
import indicadores as ind
import relatorio_mensal as rm


def desenhar_funil(funil):
    """Barras horizontais do funil em pessoas, com o valor e a taxa na ponta."""
    etapas = pd.DataFrame([
        ("Credenciados", funil["credenciados"], ""),
        ("Visitantes", funil["visitantes"], f" ({rm.percentual(funil['taxa_visitacao'])} dos credenciados)"),
        ("Participantes do evento", funil["participantes_evento"],
         f" ({rm.percentual(funil['taxa_participacao_sobre_visitantes'])} dos visitantes)"),
    ], columns=["etapa", "pessoas", "complemento"]).iloc[::-1]
    fig, ax = gr.nova_figura()
    barras = ax.barh(etapas["etapa"], etapas["pessoas"], height=0.3, color=gr.AMBAR)
    ax.bar_label(barras, labels=[rm.numero(p) + c for p, c in zip(etapas["pessoas"], etapas["complemento"])],
                 padding=6, fontsize=11, color=gr.GRAFITE)
    gr.aplicar_padrao(ax, "Funil da feira, em pessoas")
    ax.spines["bottom"].set_visible(False)
    ax.xaxis.set_visible(False)
    ax.tick_params(axis="y", labelsize=11, colors=gr.GRAFITE)
    ax.set_xlim(0, etapas["pessoas"].max() * 1.6)
    return fig


def desenhar_entrega_whatsapp(entrega):
    """Barras da taxa de entrega por disparo de WhatsApp, com o valor na ponta."""
    tabela = pd.DataFrame(entrega["disparos"]).iloc[::-1]
    rotulos = [f"{linha.disparo} · {linha.tema}" for linha in tabela.itertuples()]
    fig, ax = gr.nova_figura()
    barras = ax.barh(rotulos, tabela["taxa_entrega"], height=0.3, color=gr.AMBAR)
    ax.bar_label(barras, labels=[rm.percentual(valor) for valor in tabela["taxa_entrega"]],
                 padding=6, fontsize=11, color=gr.GRAFITE)
    gr.aplicar_padrao(ax, "Entrega dos disparos de WhatsApp, em contatos")
    ax.spines["bottom"].set_visible(False)
    ax.xaxis.set_visible(False)
    ax.tick_params(axis="y", labelsize=11, colors=gr.GRAFITE)
    ax.set_xlim(0, 115)
    return fig


def gerar_graficos_feira(pasta_saida):
    """Gera os dois gráficos do report pós-feira e as tabelas. Devolve os caminhos das imagens."""
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    funil, entrega = ind.funil_feira(), ind.entrega_whatsapp()
    trabalhos = [
        ("funil_feira", pd.DataFrame([{k: v for k, v in funil.items() if not isinstance(v, dict)}]),
         desenhar_funil(funil)),
        ("entrega_whatsapp", pd.DataFrame(entrega["disparos"]), desenhar_entrega_whatsapp(entrega)),
    ]
    gravados = []
    for nome, tabela, figura in trabalhos:
        tabela.to_csv(pasta_saida / f"{nome}.csv", sep=";", index=False, encoding="utf-8")
        gr.salvar(figura, pasta_saida / f"{nome}.png")
        gravados.append(pasta_saida / f"{nome}.png")
    return gravados

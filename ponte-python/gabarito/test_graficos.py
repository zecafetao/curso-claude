"""Testes dos gráficos do relatório mensal. Exemplo de solução do exercício do módulo P.8.

Rode na pasta dos seus scripts, com a pasta dados ao lado:
    python -m pytest test_graficos.py
"""

import matplotlib.pyplot as plt

import graficos_relatorio as gr
import relatorio_mensal as rm

ATUAL = "dados/desempenho_email_outubro.csv"
ANTERIOR = "dados/desempenho_email_setembro.csv"


def considerados(caminho):
    base, _ = rm.separar_excluidos(rm.ler_desempenho(caminho))
    return base


def test_tabela_de_clique_vem_ordenada_da_maior_para_a_menor():
    tabela = gr.tabela_clique_por_publico(considerados(ATUAL))
    assert list(tabela["publico"]) == ["Expositor", "Pré-credenciado", "Credenciamento", "Prospecção", "Reativação"]
    assert list(tabela["taxa_clique"]) == [6.8, 3.7, 3.6, 1.6, 1.0]


def test_rotulos_desenhados_sao_os_valores_da_tabela():
    tabela = gr.tabela_clique_por_publico(considerados(ATUAL))
    figura = gr.desenhar_clique_por_publico(tabela, "outubro de 2026")
    rotulos = [texto.get_text() for texto in figura.axes[0].texts]
    plt.close(figura)
    # O matplotlib desenha de baixo para cima: o primeiro rótulo é o da barra de baixo.
    assert rotulos == ["1,0%", "1,6%", "3,6%", "3,7%", "6,8%"]


def test_tabela_de_abertura_compara_os_dois_meses():
    tabela = gr.tabela_abertura_comparada(considerados(ATUAL), considerados(ANTERIOR))
    linha = tabela[tabela["publico"] == "Prospecção"].iloc[0]
    assert (linha["taxa_abertura_atual"], linha["taxa_abertura_anterior"], linha["diferenca_pp"]) == (54.7, 46.2, 8.5)
    assert len(tabela) == 5


def test_acumulado_fecha_com_o_total_do_mes():
    atual = gr.tabela_envios_acumulados(considerados(ATUAL))
    anterior = gr.tabela_envios_acumulados(considerados(ANTERIOR))
    assert atual["enviadas_acumuladas"].iloc[-1] == 50812
    assert anterior["enviadas_acumuladas"].iloc[-1] == 64307
    assert atual.loc[atual["dia"] == 15, "enviadas_acumuladas"].iloc[0] == 50812
    assert anterior.loc[anterior["dia"] == 15, "enviadas_acumuladas"].iloc[0] == 35134


def test_acumulado_nunca_diminui():
    tabela = gr.tabela_envios_acumulados(considerados(ATUAL))
    assert tabela["enviadas_acumuladas"].is_monotonic_increasing


def test_gerar_graficos_grava_imagens_e_tabelas(tmp_path):
    gravados = gr.gerar_graficos(ATUAL, ANTERIOR, tmp_path)
    assert len(gravados) == 3
    for imagem in gravados:
        assert imagem.stat().st_size > 10_000
        assert imagem.with_suffix(".csv").exists()

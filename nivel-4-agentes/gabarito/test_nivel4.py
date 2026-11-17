"""Testes das partes do Nível 4 que não chamam a API. Não gastam créditos.

Rode na pasta dos seus scripts, com a pasta dados_n4 ao lado e o banco montado:
    python montar_banco.py dados_n4 dados_n4/campanha.db
    python -m pytest test_nivel4.py -q
"""

import asyncio
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

import acervo
import agente_mercado
import apresentacao as ap
import avaliar_busca
import busca_semantica as bs
import fontes_feira as ff
import indicadores as ind
import verificar_numeros as vn

PASTA_HOOKS = Path(__file__).parent / "claude-code" / ".claude" / "hooks"


# ---------- indicadores (4.3 e projeto) ----------

def test_indicadores_de_outubro_conferem_com_a_ponte():
    geral = ind.indicadores_email("2026-10")
    assert (geral["disparos"], geral["enviadas"], geral["entregues"]) == (14, 50812, 50116)
    assert (geral["taxa_entrega"], geral["taxa_abertura"], geral["taxa_clique"]) == (98.6, 52.6, 2.4)
    assert [d["enviadas"] for d in geral["disparos_excluidos"]] == [6]


def test_comparacao_de_meses():
    diferencas = ind.comparar_meses("2026-10", "2026-09")["diferencas_pp"]
    assert diferencas == {"taxa_entrega": 0.7, "taxa_abertura": 6.9, "taxa_clique": 0.6, "variacao_enviadas_pct": -21.0}


def test_mes_invalido_gera_erro_e_nao_zero():
    assert "erro" in ind.indicadores_email("outubro")
    assert "erro" in ind.indicadores_email("2026-08")


def test_funil_e_whatsapp_conferem_com_a_ponte():
    funil = ind.funil_feira()
    assert (funil["credenciados"], funil["visitantes"], funil["participantes_evento"]) == (560, 218, 44)
    entrega = {d["disparo"]: (d["contatos"], d["receberam"]) for d in ind.entrega_whatsapp()["disparos"]}
    assert entrega == {"D1": (456, 435), "D2": (456, 441), "D3": (456, 429)}


def test_banco_aberto_so_para_leitura():
    with ind.conectar() as conexao, pytest.raises(Exception):
        conexao.execute("DELETE FROM disparos_email")


# ---------- servidor MCP (4.3) ----------

def test_servidor_mcp_responde_por_um_cliente_real():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def conversar():
        parametros = StdioServerParameters(command=sys.executable, args=["servidor_campanha.py"])
        async with stdio_client(parametros) as (leitura, escrita):
            async with ClientSession(leitura, escrita) as sessao:
                await sessao.initialize()
                nomes = [t.name for t in (await sessao.list_tools()).tools]
                resultado = await sessao.call_tool("indicadores_email", {"mes": "2026-10"})
                return nomes, json.loads(resultado.content[0].text)

    nomes, geral = asyncio.run(conversar())
    assert {"indicadores_email", "funil_feira", "entrega_whatsapp"} <= set(nomes)
    assert geral["enviadas"] == 50812


# ---------- verificador de números (4.7 e projeto) ----------

def test_verificador_aceita_numeros_das_ferramentas_e_recusa_os_outros():
    referencias = [ind.indicadores_email("2026-10"), ind.comparar_meses("2026-10", "2026-09")]
    texto = "Abertura de 52,6%, alta de 6,9 pontos, 50.812 envios e queda de 21,0%. Previsão de 55,0% e 1.234 cliques."
    resultado = vn.verificar(texto, referencias)
    assert [i["numero"] for i in resultado["verificados"]] == ["52,6", "6,9", "50.812", "21,0"]
    assert [i["numero"] for i in resultado["sem_fonte"]] == ["55,0", "1.234"]


def test_verificador_ignora_datas_anos_e_enumeracoes():
    texto = "A feira de 20 a 22 de outubro de 2026; no dia 15; em 2026-10; três achados, 3 públicos."
    assert vn.numeros_do_texto(texto) == []


# ---------- apresentação e conferidor (projeto) ----------

TITULOS = {
    "indicadores": "Outubro entregou 98,6% e abriu 52,6% das mensagens",
    "comparacao": "A abertura subiu 6,9 pontos percentuais sobre setembro",
    "publico": "Credenciamento lidera o clique entre os públicos grandes",
    "grafico_clique": "Expositor tem o maior clique, sobre 162 entregues",
    "grafico_abertura": "Prospecção puxou a alta da abertura",
}
ACHADOS = [
    {"titulo": "Abertura em alta", "fato": "A abertura passou de 45,7% para 52,6%.", "proximo_passo": "Manter a frequência."},
    {"titulo": "Reativação baixa", "fato": "A reativação abriu 12,6%.", "proximo_passo": "Testar outro assunto."},
    {"titulo": "Clique atípico", "fato": "Um reenvio teve clique de 20,1%.", "proximo_passo": "Confirmar no CRM."},
]


def montar(tmp_path, achados):
    import graficos_relatorio as gr
    imagens = gr.gerar_graficos("dados_n4/desempenho_email_outubro.csv", "dados_n4/desempenho_email_setembro.csv",
                                tmp_path / "graficos")
    return ap.relatorio_mensal("2026-10", "2026-09", achados, TITULOS, {"clique": imagens[0], "abertura": imagens[1]},
                               tmp_path / "relatorio.pptx")


def test_apresentacao_recusa_numero_sem_fonte(tmp_path):
    inventado = [dict(ACHADOS[0], fato="A abertura deve chegar a 55,0%.")] + ACHADOS[1:]
    resultado = montar(tmp_path, inventado)
    assert resultado["erro"] and resultado["sem_fonte"][0]["numero"] == "55,0"
    assert not (tmp_path / "relatorio.pptx").exists()


def test_apresentacao_aprovada_no_conferidor(tmp_path):
    resultado = montar(tmp_path, ACHADOS)
    assert "erro" not in resultado
    sys.path.insert(0, "dados_n4")
    import conferir_projeto_n4
    assert conferir_projeto_n4.conferir("mensal", tmp_path / "relatorio.pptx") == []
    with open(tmp_path / "conferencia.csv", encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo, delimiter=";"))
    assert len(linhas) >= 30 and {"slide", "elemento", "valor", "origem"} == set(linhas[0])


# ---------- estudo de mercado (4.2) ----------

def test_perfil_dos_expositores_tem_so_contagens():
    perfil = json.loads(agente_mercado.perfil_expositores.call({}))
    assert perfil["empresas"] == 120
    assert perfil["setor"]["Indústria de embalagens plásticas"] == {"empresas": 42, "participacao": 35.0}


def test_entrega_do_estudo_confere_fontes():
    secoes = [{"titulo": t, "texto": f"Texto [{i}]"} for i, t in enumerate(["A", "B", "C"], start=1)]
    secoes.append({"titulo": "D", "texto": "Sem citação."})
    problemas = agente_mercado.conferir_estudo(secoes, [{"titulo": "Um", "url": "https://um.example"}])
    assert any("sem fonte" in p for p in problemas)
    fontes = [{"titulo": n, "url": f"https://{n}.example"} for n in ("a", "b", "c")]
    assert agente_mercado.conferir_estudo(secoes, fontes) == []


# ---------- fontes grandes (4.6) ----------

def test_fontes_grandes_nao_cabem_no_contexto_mas_as_ferramentas_resumem():
    descricao = ff.descrever_fontes()
    total = sum(descricao[f]["caracteres"] for f in ff.FONTES)
    assert total > 5_000_000
    funil = ff.funil()
    assert (funil["cadastros_duplicados"], funil["credenciados"], funil["visitantes"]) == (884, 22300, 9320)
    assert len(json.dumps(funil)) < 500


# ---------- busca no acervo (4.8) ----------

def perguntas():
    with open("dados_n4/perguntas_acervo.csv", encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo, delimiter=";"))


def test_busca_por_palavras_no_acervo():
    busca = acervo.BuscaBM25(acervo.dividir_em_trechos("dados_n4/acervo"))
    assert len(busca.trechos) == 38
    acertos, totais, _ = avaliar_busca.avaliar(busca, perguntas(), k=3)
    assert (acertos["direta"], totais["direta"], acertos["parafraseada"], totais["parafraseada"]) == (16, 16, 4, 8)


def test_fusao_de_listas():
    a = [{"arquivo": "x", "secao": "1"}, {"arquivo": "y", "secao": "1"}]
    b = [{"arquivo": "y", "secao": "1"}, {"arquivo": "z", "secao": "1"}]
    assert [t["arquivo"] for t in bs.fundir([a, b], k=3)] == ["y", "x", "z"]


# ---------- hooks do Claude Code (4.4) ----------

@pytest.mark.parametrize("entrada, codigo", [
    ({"tool_name": "Read", "tool_input": {"file_path": "/repo/dados_reais/base.csv"}}, 2),
    ({"tool_name": "Bash", "tool_input": {"command": "cat .env"}}, 2),
    ({"tool_name": "Read", "tool_input": {"file_path": "/repo/validacao.py"}}, 0),
])
def test_hook_protege_dados_reais(entrada, codigo):
    processo = subprocess.run([sys.executable, str(PASTA_HOOKS / "proteger_dados.py")],
                              input=json.dumps(entrada), capture_output=True, text=True)
    assert processo.returncode == codigo

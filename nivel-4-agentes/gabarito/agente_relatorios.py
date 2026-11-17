"""Agente de relatórios: das exportações do CRM ao rascunho do relatório, com lista de conferência.

Solução de referência do projeto do Nível 4. As chamadas à API não foram executadas com uma chave real.
O servidor MCP, as ferramentas locais, o verificador e a montagem da apresentação foram executados
e testados.

Uso:
    python agente_relatorios.py mensal 2026-10 2026-09
    python agente_relatorios.py pos_feira

O que sai do computador: as instruções (com a Skill do relatório), o pedido e os resultados das
ferramentas, que são só contagens e taxas. Nenhum nome, e-mail ou telefone é enviado à API.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import anthropic
from anthropic import beta_async_tool
from anthropic.lib.tools.mcp import async_mcp_tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import apresentacao as ap
import claude_util as cu
import graficos_feira as gf
import graficos_relatorio as gr

PASTA_DADOS = Path(os.environ.get("PASTA_DADOS_N4", "dados_n4"))
PASTA_SAIDA = Path(os.environ.get("PASTA_SAIDA_N4", "saida_relatorios"))
SKILLS = {"mensal": PASTA_DADOS / "relatorio-mensal-email", "pos_feira": PASTA_DADOS / "report-pos-feira"}
TITULOS_ESPERADOS = {
    "mensal": ["indicadores", "comparacao", "publico", "grafico_clique", "grafico_abertura"],
    "pos_feira": ["funil", "grafico_funil", "whatsapp", "whatsapp_visitacao", "email"],
}

REGRAS = """Você prepara o rascunho de um relatório para uma equipe de CRM e marketing. Uma pessoa revisa o
rascunho antes de ele seguir para o cliente.

Como trabalhar:
- Os números vêm das ferramentas do servidor de campanha. Consulte as que o relatório pede antes de escrever.
- As tabelas e os números de destaque são montados por código. Você escreve os títulos-achado dos slides
  e três achados, cada um com titulo, fato e proximo_passo.
- Todo número que você escrever precisa existir no resultado de uma ferramenta, no mesmo valor. Não calcule
  diferenças, somas ou médias por conta própria: se precisar de um número que nenhuma ferramenta dá, escreva
  o achado sem ele.
- Antes de montar o relatório, passe todos os seus textos pela ferramenta verificar_textos. Se ela apontar
  números sem fonte, corrija o texto e verifique de novo.
- Separe fato de hipótese. Uma explicação para uma diferença é apresentada como hipótese.
- Termine chamando montar_relatorio. Na resposta final, diga em poucas linhas o que entrou no relatório,
  as ressalvas e os pontos que a pessoa revisora deve conferir.

As chaves de titulos para este relatório são: {chaves}.

A Skill do relatório está abaixo. Siga o método dela; a estrutura de slides é a que montar_relatorio produz.

<skill>
{skill}
</skill>"""


def instrucoes(tipo):
    """Junta as regras do agente e os arquivos da Skill do relatório."""
    pasta = SKILLS[tipo]
    partes = [(pasta / "SKILL.md").read_text(encoding="utf-8")]
    for referencia in sorted((pasta / "references").glob("*.md")) if (pasta / "references").exists() else []:
        partes.append(f"<referencia arquivo='{referencia.name}'>\n{referencia.read_text(encoding='utf-8')}\n</referencia>")
    return REGRAS.format(chaves=", ".join(TITULOS_ESPERADOS[tipo]), skill="\n\n".join(partes))


def ferramentas_locais(tipo, mes, mes_anterior):
    """As ferramentas que rodam neste processo, ligadas ao relatório pedido."""

    @beta_async_tool
    async def verificar_textos(textos: list[str]) -> str:
        """Confere se cada número dos textos existe nos resultados das ferramentas de campanha.

        Use antes de montar_relatorio, com todos os títulos e achados que você escreveu.

        Args:
            textos: Os textos a conferir, um por item.
        """
        sem_fonte = ap.conferir_textos(textos, ap.referencias(tipo, mes, mes_anterior))
        if not sem_fonte:
            return json.dumps({"aprovado": True}, ensure_ascii=False)
        return json.dumps({"aprovado": False, "sem_fonte": sem_fonte}, ensure_ascii=False)

    @beta_async_tool
    async def montar_relatorio(titulos: dict[str, str], achados: list[dict[str, str]]) -> str:
        """Gera os gráficos e monta a apresentação no padrão visual, com a lista de conferência.

        Recusa a montagem se algum texto tiver número sem fonte.

        Args:
            titulos: Título-achado de cada slide de dados, pelas chaves indicadas nas instruções.
            achados: Exatamente três achados, cada um com as chaves titulo, fato e proximo_passo.
        """
        faltando = [chave for chave in TITULOS_ESPERADOS[tipo] if not titulos.get(chave)]
        if faltando:
            return json.dumps({"erro": f"Faltam títulos para: {', '.join(faltando)}."}, ensure_ascii=False)
        if len(achados) != 3 or any(set(a) != {"titulo", "fato", "proximo_passo"} for a in achados):
            return json.dumps({"erro": "Envie três achados com titulo, fato e proximo_passo."}, ensure_ascii=False)
        pasta = PASTA_SAIDA / (f"mensal_{mes}" if tipo == "mensal" else "pos_feira")
        if tipo == "mensal":
            imagens = gr.gerar_graficos(PASTA_DADOS / f"desempenho_email_{nome_arquivo(mes)}.csv",
                                        PASTA_DADOS / f"desempenho_email_{nome_arquivo(mes_anterior)}.csv",
                                        pasta / "graficos")
            resultado = ap.relatorio_mensal(mes, mes_anterior, achados, titulos,
                                            {"clique": imagens[0], "abertura": imagens[1]},
                                            pasta / f"relatorio_email_{mes}.pptx")
        else:
            imagens = gf.gerar_graficos_feira(pasta / "graficos")
            resultado = ap.report_pos_feira(achados, titulos, {"funil": imagens[0]}, pasta / "report_pos_feira.pptx")
        return json.dumps(resultado, ensure_ascii=False)

    return [verificar_textos, montar_relatorio]


def nome_arquivo(mes):
    """'2026-10' vira 'outubro', como nos nomes das exportações."""
    return ap.MESES[int(mes.split("-")[1]) - 1]


def pedido(tipo, mes, mes_anterior):
    if tipo == "mensal":
        return (f"Prepare o rascunho do relatório mensal de e-mail de {ap.nome_do_mes(mes)}, "
                f"com a comparação com {ap.nome_do_mes(mes_anterior)}.")
    return "Prepare o rascunho do report pós-feira da Expo Modelo 2026."


async def executar(cliente, tipo, mes="", mes_anterior="", mostrar=print):
    """Roda o agente e devolve (texto final, total de uso, ferramentas chamadas)."""
    parametros = StdioServerParameters(
        command=sys.executable, args=["servidor_campanha.py"],
        env={**os.environ, "BANCO_CAMPANHA": str(PASTA_DADOS / "campanha.db")},
    )
    async with stdio_client(parametros) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()
            do_servidor = (await sessao.list_tools()).tools
            ferramentas = [async_mcp_tool(t, sessao) for t in do_servidor] + ferramentas_locais(tipo, mes, mes_anterior)

            executor = cliente.beta.messages.tool_runner(
                model=cu.MODELO,
                max_tokens=16000,
                system=instrucoes(tipo),
                tools=ferramentas,
                messages=[{"role": "user", "content": pedido(tipo, mes, mes_anterior)}],
                output_config={"effort": "medium"},
                betas=[cu.BETA_FALLBACK],
                fallbacks="default",
                max_iterations=15,
                thread=False,
            )
            total, chamadas, ultima = cu.novo_total(), [], None
            async for mensagem in executor:
                cu.somar_uso(total, mensagem.usage)
                ultima = mensagem
                for bloco in mensagem.content:
                    if bloco.type == "tool_use":
                        chamadas.append(bloco.name)
                        mostrar(f"  [ferramenta] {bloco.name}")
    if ultima is None or ultima.stop_reason == "refusal":
        return None, total, chamadas
    return cu.texto_da_resposta(ultima), total, chamadas


def principal(argumentos):
    if not argumentos or argumentos[0] not in ("mensal", "pos_feira") or (argumentos[0] == "mensal" and len(argumentos) != 3):
        print("Uso: python agente_relatorios.py mensal 2026-10 2026-09 | python agente_relatorios.py pos_feira")
        sys.exit(1)
    tipo = argumentos[0]
    mes, mes_anterior = (argumentos[1], argumentos[2]) if tipo == "mensal" else ("", "")
    cliente = anthropic.AsyncAnthropic()
    try:
        texto, total, chamadas = asyncio.run(executar(cliente, tipo, mes, mes_anterior))
    except anthropic.AuthenticationError:
        print("Chave de API inválida ou ausente. Confira a variável ANTHROPIC_API_KEY.")
        sys.exit(1)
    print(texto if texto is not None else "O pedido foi recusado.")
    print(f"Ferramentas chamadas: {len(chamadas)} | {cu.resumo_do_total(total)}")


if __name__ == "__main__":
    principal(sys.argv[1:])

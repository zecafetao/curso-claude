"""Assistente de perguntas sobre a campanha, usando o servidor MCP como fonte das ferramentas.

Solução de referência do módulo 4.3. As chamadas à API não foram executadas com uma chave real.
O servidor MCP e a ligação com ele foram executados e testados.

Uso:
    python agente_mcp.py "Como foi a taxa de abertura de outubro comparada com setembro?"

O mesmo servidor serve ao Claude Desktop, ao Claude Code e a este script: as ferramentas são escritas
uma vez e usadas em qualquer cliente MCP.
"""

import asyncio
import os
import sys

import anthropic
from anthropic.lib.tools.mcp import async_mcp_tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import claude_util as cu

SISTEMA = (
    "Você responde perguntas da equipe de CRM sobre a campanha da Expo Modelo 2026. Use as ferramentas do "
    "servidor de campanha para todo número. Respostas curtas, com os números que as ferramentas devolveram."
)
SERVIDOR = StdioServerParameters(
    command=sys.executable,
    args=["servidor_campanha.py"],
    env={**os.environ, "BANCO_CAMPANHA": os.environ.get("BANCO_CAMPANHA", "dados_n4/campanha.db")},
)


async def perguntar(cliente, pergunta):
    async with stdio_client(SERVIDOR) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()
            ferramentas = [async_mcp_tool(t, sessao) for t in (await sessao.list_tools()).tools]
            executor = cliente.beta.messages.tool_runner(
                model=cu.MODELO, max_tokens=16000, system=SISTEMA, tools=ferramentas,
                messages=[{"role": "user", "content": pergunta}], output_config={"effort": "low"},
                max_iterations=8, thread=False, **cu.opcoes_de_fallback(),
            )
            total, ultima = cu.novo_total(), None
            async for mensagem in executor:
                cu.somar_uso(total, mensagem.usage)
                ultima = mensagem
                for bloco in mensagem.content:
                    if bloco.type == "tool_use":
                        print(f"  [mcp] {bloco.name} {bloco.input}")
    texto = None if ultima is None or ultima.stop_reason == "refusal" else cu.texto_da_resposta(ultima)
    return texto, total


if __name__ == "__main__":
    texto, total = asyncio.run(perguntar(anthropic.AsyncAnthropic(), sys.argv[1]))
    print(texto if texto is not None else "O pedido foi recusado.")
    print(cu.resumo_do_total(total))

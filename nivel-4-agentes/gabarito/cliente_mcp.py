"""Testa o servidor MCP sem o Claude: lista as ferramentas e chama algumas.

Material do módulo 4.3. Executado e testado. Não gasta créditos.

Uso:
    python cliente_mcp.py
"""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PARAMETROS = StdioServerParameters(
    command=sys.executable,                       # o mesmo Python que roda este script
    args=["servidor_campanha.py"],
    env={**os.environ, "BANCO_CAMPANHA": os.environ.get("BANCO_CAMPANHA", "dados_n4/campanha.db")},
)


async def principal():
    async with stdio_client(PARAMETROS) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()

            ferramentas = await sessao.list_tools()
            print(f"{len(ferramentas.tools)} ferramentas:")
            for ferramenta in ferramentas.tools:
                parametros = list(ferramenta.input_schema.get("properties", {}))
                print(f"  {ferramenta.name}({', '.join(parametros)})")

            for nome, argumentos in [
                ("indicadores_email", {"mes": "2026-10"}),
                ("comparar_meses", {"mes_atual": "2026-10", "mes_anterior": "2026-09"}),
                ("indicadores_email", {"mes": "outubro"}),
            ]:
                resultado = await sessao.call_tool(nome, argumentos)
                texto = resultado.content[0].text
                print(f"\n{nome} {argumentos}:\n  {texto[:300]}")

            recurso = await sessao.read_resource("campanha://dicionario")
            print(f"\nRecurso campanha://dicionario:\n  {recurso.contents[0].text[:150]}...")


if __name__ == "__main__":
    asyncio.run(principal())

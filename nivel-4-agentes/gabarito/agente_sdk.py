"""O agente de estudo de mercado do módulo 4.2, refeito com o Claude Agent SDK.

Solução de referência do módulo 4.5. Executado uma vez no ambiente em que o curso foi escrito
(novembro de 2026, pacote claude-agent-sdk 0.2): a execução terminou com sucesso e custo informado de
US$ 0,36. A busca na web funcionou, a leitura das páginas foi bloqueada pela rede daquele ambiente, e o
agente registrou as lacunas em vez de usar números não lidos. O arquivo gerado está em
dados/exemplos/estudo_agent_sdk_execucao_real.md.

Instalação: pip install claude-agent-sdk   (o pacote traz o Claude Code; a chave vem de ANTHROPIC_API_KEY)

Uso:
    python agente_sdk.py "indústria de embalagens" "região Sul"

Diferença para o 4.2: o laço, a busca na web, a leitura de páginas e a gravação de arquivos vêm prontos
do Claude Code. Você escreve as instruções, a ferramenta própria e as permissões.
"""

import asyncio
import sys
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

import agente_mercado

PASTA_SAIDA = Path("saida_sdk").resolve()


@tool("perfil_expositores", "Perfil dos expositores atuais da feira por setor, porte, região e faturamento.", {})
async def perfil_expositores(argumentos):
    """Reaproveita a função do módulo 4.2. A ferramenta roda neste processo, no seu computador."""
    return {"content": [{"type": "text", "text": agente_mercado.perfil_expositores.call({})}]}


SERVIDOR_DE_DADOS = create_sdk_mcp_server(name="dados_feira", version="1.0.0", tools=[perfil_expositores])

INSTRUCOES = agente_mercado.SISTEMA.replace(
    "Termine chamando entregar_estudo.",
    "Termine gravando o estudo em Markdown no arquivo estudo.md da pasta de trabalho, com as quatro seções "
    "e uma seção Fontes numerada no fim.",
)


def opcoes():
    PASTA_SAIDA.mkdir(exist_ok=True)
    return ClaudeAgentOptions(
        model="claude-opus-5-5",
        system_prompt=INSTRUCOES,
        cwd=str(PASTA_SAIDA),                                   # o agente trabalha só nesta pasta
        tools=["WebSearch", "WebFetch", "Read", "Write"],      # ferramentas embutidas disponíveis
        mcp_servers={"dados": SERVIDOR_DE_DADOS},
        allowed_tools=["WebSearch", "WebFetch", "Read", "Write", "mcp__dados__perfil_expositores"],
        permission_mode="dontAsk",           # o que não está em allowed_tools é negado, sem perguntar
        setting_sources=[],                  # não carrega configurações do seu computador
        max_turns=30,
        max_budget_usd=2.0,                  # para quando o custo da execução passar de 2 dólares
        effort="medium",
    )


async def estudar(setor, regiao):
    custo, arquivo = None, PASTA_SAIDA / "estudo.md"
    async for mensagem in query(prompt=f"Setor: {setor}. Região: {regiao}.", options=opcoes()):
        if isinstance(mensagem, AssistantMessage):
            for bloco in mensagem.content:
                if isinstance(bloco, ToolUseBlock):
                    print(f"  [ferramenta] {bloco.name}")
                elif isinstance(bloco, TextBlock):
                    print(f"  {bloco.text[:120]}")
        elif isinstance(mensagem, ResultMessage):
            custo = mensagem.total_cost_usd
            print(f"Resultado: {mensagem.subtype}")
    return arquivo if arquivo.exists() else None, custo


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Uso: python agente_sdk.py "setor" "região"')
        sys.exit(1)
    arquivo, custo = asyncio.run(estudar(sys.argv[1], sys.argv[2]))
    print(f"Arquivo: {arquivo or 'não gravado'} | custo informado pelo SDK: US$ {custo}")

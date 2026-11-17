"""Servidor MCP com os indicadores da campanha da Expo Modelo 2026.

Solução de referência do módulo 4.3. Executado e testado com um cliente MCP real (cliente_mcp.py).

Como usar:
    - No Claude Code:  claude mcp add campanha -e BANCO_CAMPANHA=/caminho/campanha.db -- python /caminho/servidor_campanha.py
    - No Claude Desktop: bloco "mcpServers" do claude_desktop_config.json (ver o módulo 4.3)
    - Em um script:    cliente_mcp.py ou agente_mcp.py

O servidor só lê o banco e só devolve contagens e taxas. Nenhuma ferramenta devolve nome, e-mail ou telefone.
"""

from mcp.server.mcpserver import MCPServer

import indicadores as ind

servidor = MCPServer(
    "campanha-expo-modelo",
    instructions=(
        "Indicadores da campanha de marketing da Expo Modelo 2026: e-mail por mês e por público, "
        "WhatsApp por disparo e o funil da feira em pessoas. Os meses usam o formato AAAA-MM."
    ),
)


@servidor.tool()
def indicadores_email(mes: str) -> dict:
    """Totais e taxas de e-mail de um mês: disparos, enviadas, entregues, aberturas, cliques e as três taxas.

    Use para os indicadores gerais do relatório mensal. Disparos com menos de 10 envios ficam fora
    dos totais e aparecem em disparos_excluidos.

    Args:
        mes: Mês no formato AAAA-MM, como 2026-10.
    """
    return ind.indicadores_email(mes)


@servidor.tool()
def indicadores_por_publico(mes: str) -> dict:
    """Totais e taxas de e-mail por público em um mês, do maior volume de envio para o menor.

    Args:
        mes: Mês no formato AAAA-MM, como 2026-10.
    """
    return ind.indicadores_por_publico(mes)


@servidor.tool()
def anomalias_de_clique(mes: str) -> dict:
    """Disparos do mês com taxa de clique acima de 15%, sinal de possível clique automático.

    Args:
        mes: Mês no formato AAAA-MM, como 2026-10.
    """
    return ind.anomalias_de_clique(mes)


@servidor.tool()
def comparar_meses(mes_atual: str, mes_anterior: str) -> dict:
    """Compara os indicadores gerais de e-mail de dois meses. Diferenças de taxa em pontos percentuais.

    Args:
        mes_atual: Mês analisado, no formato AAAA-MM.
        mes_anterior: Mês de comparação, no formato AAAA-MM.
    """
    return ind.comparar_meses(mes_atual, mes_anterior)


@servidor.tool()
def entrega_whatsapp() -> dict:
    """Entrega de cada disparo de WhatsApp da feira, contada em contatos e não em tentativas."""
    return ind.entrega_whatsapp()


@servidor.tool()
def funil_feira() -> dict:
    """Funil da feira em pessoas: credenciados, visitantes, participantes do evento e dias de presença."""
    return ind.funil_feira()


@servidor.tool()
def whatsapp_e_visitacao() -> dict:
    """Taxa de visitação de quem recebeu e de quem não recebeu mensagens de WhatsApp.

    A comparação não mede o efeito do WhatsApp, porque os grupos não foram sorteados.
    """
    return ind.whatsapp_e_visitacao()


@servidor.resource("campanha://dicionario")
def dicionario() -> str:
    """Definições dos indicadores usados pelas ferramentas."""
    return (
        "Taxa de entrega = entregues / enviadas. Taxa de abertura = aberturas únicas / entregues. "
        "Taxa de clique = cliques únicos / entregues. Disparos com menos de 10 envios ficam fora dos totais. "
        "WhatsApp: um contato recebeu o disparo se ao menos uma tentativa foi entregue. "
        "Funil: pessoas, depois de resolver a identidade por e-mail, telefone e nome."
    )


if __name__ == "__main__":
    servidor.run()          # transporte stdio: o cliente inicia o processo e conversa pela entrada e saída padrão

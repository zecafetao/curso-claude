"""Assistente que responde perguntas sobre a base usando ferramentas.

Solução de referência do módulo 3.4. As chamadas à API não foram executadas com uma chave real.
As ferramentas em si (ferramentas.py) foram executadas e testadas.

Uso:
    python assistente.py "Quantos contatos de Compras em SP têm consentimento?"
"""

import json
import sys

from anthropic import beta_tool

import claude_util as cu
import ferramentas

SISTEMA = (
    "Você apoia uma equipe de CRM. Para qualquer número sobre a base de contatos ou sobre um arquivo "
    "de importação, use as ferramentas: não estime. Use a busca na web só para informações externas, "
    "como dados de mercado. Você não altera nem apaga arquivos; se pedirem isso, explique que não tem "
    "essa ferramenta. Respostas curtas, com os números que as ferramentas devolveram."
)


@beta_tool
def resumir_base(coluna: str) -> str:
    """Conta os contatos da base tratada por valor de uma coluna.

    Use quando a pergunta pedir a distribuição dos contatos, como "quantos por área" ou
    "quais UFs têm mais contatos".

    Args:
        coluna: Uma destas colunas: area, uf, origem, consentimento, cidade, empresa.
    """
    return json.dumps(ferramentas.resumir_base(coluna), ensure_ascii=False)


@beta_tool
def contar_contatos(area: str = "", uf: str = "", consentimento: str = "", origem: str = "") -> str:
    """Conta os contatos da base tratada que cumprem todos os filtros informados.

    Use quando a pergunta combinar condições, como "contatos de Compras em SP com consentimento".

    Args:
        area: Compras, Produção, Marketing, Comercial, Diretoria ou Outros. Vazio para todas.
        uf: Sigla do estado, como SP. Vazio para todos.
        consentimento: S ou N. Vazio para os dois.
        origem: Credenciamento, Expositor, Site, Evento ou Compra de base. Vazio para todas.
    """
    return json.dumps(ferramentas.contar_contatos(area, uf, consentimento, origem), ensure_ascii=False)


@beta_tool
def validar_arquivo(nome_arquivo: str) -> str:
    """Confere um arquivo CSV de importação contra o layout do CRM e conta os problemas por tipo.

    Use quando perguntarem se um arquivo está pronto para importar.

    Args:
        nome_arquivo: Só o nome do arquivo .csv na pasta de dados, sem caminho. Exemplo: arquivo_com_erros.csv.
    """
    return json.dumps(ferramentas.validar_arquivo(nome_arquivo), ensure_ascii=False)


FERRAMENTAS = [
    resumir_base,
    contar_contatos,
    validar_arquivo,
    {"type": "web_search_20260209", "name": "web_search"},   # ferramenta de servidor: roda na Anthropic
]


def perguntar(cliente, pergunta, mostrar_passos=True):
    """Roda o laço de ferramentas até a resposta final e devolve (texto, total de uso)."""
    executor = cliente.beta.messages.tool_runner(
        model=cu.MODELO,
        max_tokens=16000,
        system=SISTEMA,
        tools=FERRAMENTAS,
        messages=[{"role": "user", "content": pergunta}],
        output_config={"effort": "medium"},
        betas=[cu.BETA_FALLBACK],
        fallbacks="default",
        max_iterations=8,          # limite de voltas do laço, para a conta não crescer sem controle
        thread=False,              # cada requisição leva a conversa inteira, como no laço manual
    )
    total = cu.novo_total()
    ultima = None
    for mensagem in executor:      # cada volta é uma resposta do modelo
        cu.somar_uso(total, mensagem.usage)
        ultima = mensagem
        if mostrar_passos:
            for bloco in mensagem.content:
                if bloco.type in ("tool_use", "server_tool_use"):
                    print(f"  [ferramenta] {bloco.name} {json.dumps(bloco.input, ensure_ascii=False)}")
    if ultima is None or ultima.stop_reason == "refusal":
        return None, total
    return cu.texto_da_resposta(ultima), total


if __name__ == "__main__":
    cliente = cu.criar_cliente()
    texto, total = perguntar(cliente, sys.argv[1])
    print(texto if texto is not None else "O pedido foi recusado.")
    print(cu.resumo_do_total(total))

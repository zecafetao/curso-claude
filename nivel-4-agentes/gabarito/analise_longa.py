"""Análise de uma feira grande com memória entre sessões e limpeza de resultados antigos de ferramenta.

Solução de referência do módulo 4.6. As chamadas à API não foram executadas com uma chave real.
As ferramentas (fontes_feira.py) e a memória local foram executadas e testadas.

Uso:
    python analise_longa.py "O cliente Expo Modelo Sul prefere números absolutos antes de percentuais."
    python analise_longa.py "Prepare a análise de visitação e WhatsApp da Expo Modelo Sul."

Cada execução é uma sessão nova: nada da conversa anterior é reenviado. O que passa de uma sessão
para outra é só o que o agente gravou na pasta de memória.
"""

import json
import sys

from anthropic import beta_tool
from anthropic.tools.memory import BetaLocalFilesystemMemoryTool

import claude_util as cu
import fontes_feira as ff

PASTA_MEMORIA = "memoria_agente"
BETA_CONTEXTO = "context-management-2025-06-27"

SISTEMA = """Você analisa os dados de feiras para uma equipe de CRM e marketing.

Memória:
- No início de cada tarefa, consulte o diretório /memories. Ele guarda as preferências de cada cliente
  e o padrão de relatório da equipe, gravados em sessões anteriores.
- Quando a pessoa informar uma preferência de um cliente ou uma regra do relatório, grave em
  /memories/clientes/<nome-do-cliente>.md ou em /memories/padrao_relatorio.md.
- Não grave na memória dados de pessoas (nomes, e-mails, telefones) nem números de uma análise:
  números mudam a cada edição e vêm sempre das ferramentas.

Dados:
- As fontes são grandes demais para ler inteiras. Use as ferramentas, que devolvem resumos.
- Todo número da resposta vem de uma ferramenta.

Responda em português do Brasil, com frases curtas."""


@beta_tool
def descrever_fontes() -> str:
    """Linhas, colunas e tamanho de cada fonte da Expo Modelo Sul 2026. Use para conhecer os dados."""
    return json.dumps(ff.descrever_fontes(), ensure_ascii=False)


@beta_tool
def funil() -> str:
    """Credenciados, visitantes e taxa de visitação, em pessoas, depois de resolver duplicidades."""
    return json.dumps(ff.funil(), ensure_ascii=False)


@beta_tool
def presenca_por_dia() -> str:
    """Visitantes distintos por dia de feira e quantos dias cada visitante foi."""
    return json.dumps(ff.presenca_por_dia(), ensure_ascii=False)


@beta_tool
def credenciados_por_uf() -> str:
    """Credenciados por UF, em pessoas."""
    return json.dumps(ff.credenciados_por_uf(), ensure_ascii=False)


@beta_tool
def entrega_whatsapp() -> str:
    """Entrega de cada disparo de WhatsApp, contada em contatos."""
    return json.dumps(ff.entrega_whatsapp(), ensure_ascii=False)


def sessao(cliente, pedido, mostrar=print):
    """Roda uma sessão do agente. Devolve (texto final, total de uso, edições de contexto aplicadas)."""
    memoria = BetaLocalFilesystemMemoryTool(base_path=PASTA_MEMORIA)
    executor = cliente.beta.messages.tool_runner(
        model=cu.MODELO,
        max_tokens=16000,
        system=SISTEMA,
        tools=[descrever_fontes, funil, presenca_por_dia, credenciados_por_uf, entrega_whatsapp, memoria],
        messages=[{"role": "user", "content": pedido}],
        output_config={"effort": "medium"},
        betas=[cu.BETA_FALLBACK, BETA_CONTEXTO],
        fallbacks="default",
        context_management={"edits": [{
            "type": "clear_tool_uses_20250919",
            "trigger": {"type": "input_tokens", "value": 30000},   # começa a limpar acima de 30 mil tokens
            "keep": {"type": "tool_uses", "value": 3},             # mantém os 3 resultados mais recentes
            "exclude_tools": ["memory"],                           # nunca limpa as consultas à memória
        }]},
        max_iterations=12,
        thread=False,
    )
    total, edicoes, ultima = cu.novo_total(), [], None
    for mensagem in executor:
        cu.somar_uso(total, mensagem.usage)
        ultima = mensagem
        gestao = getattr(mensagem, "context_management", None)
        if gestao and gestao.applied_edits:
            edicoes += [edicao.model_dump() for edicao in gestao.applied_edits]
        for bloco in mensagem.content:
            if bloco.type == "tool_use":
                mostrar(f"  [ferramenta] {bloco.name} {json.dumps(bloco.input, ensure_ascii=False)[:80]}")
    texto = None if ultima is None or ultima.stop_reason == "refusal" else cu.texto_da_resposta(ultima)
    return texto, total, edicoes


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Uso: python analise_longa.py "pedido"')
        sys.exit(1)
    texto, total, edicoes = sessao(cu.criar_cliente(), sys.argv[1])
    print(texto if texto is not None else "O pedido foi recusado.")
    print(cu.resumo_do_total(total))
    if edicoes:
        print(f"Edições de contexto aplicadas: {edicoes}")

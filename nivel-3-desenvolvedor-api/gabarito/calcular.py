"""Conta exata com a ferramenta de execução de código, que roda na Anthropic.

Solução de referência do módulo 3.4. As chamadas à API não foram executadas com uma chave real.
Só o resumo por origem é enviado: nenhuma linha da base sai do computador.

Uso:
    python calcular.py
"""

import json

import claude_util as cu
import ferramentas

EXECUCAO_DE_CODIGO = {"type": "code_execution_20260120", "name": "code_execution"}


def percentuais_por_origem(cliente):
    """Pede ao Claude que calcule, por código, o percentual de cada origem. Devolve a resposta."""
    resumo = ferramentas.resumir_base("origem")
    pedido = (
        "Com os dados em <dados>, calcule o percentual de cada origem sobre o total, com uma casa decimal. "
        "Faça a conta por código.\n\n<dados>\n" + json.dumps(resumo, ensure_ascii=False) + "\n</dados>"
    )
    return cu.chamar(cliente, [{"role": "user", "content": pedido}], tools=[EXECUCAO_DE_CODIGO], esforco="low")


if __name__ == "__main__":
    resposta = percentuais_por_origem(cu.criar_cliente())
    print("Blocos da resposta:", [bloco.type for bloco in resposta.content])
    if resposta.stop_reason == "pause_turn":
        print("A resposta foi pausada antes do fim. Rode de novo.")
    print(cu.texto_da_resposta(resposta))
    print(f"Custo: US$ {cu.custo_em_dolares(resposta.usage):.4f}")

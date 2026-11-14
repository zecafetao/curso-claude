"""O laço de ferramentas escrito à mão, para entender o que o executor do SDK faz por você.

Exemplo didático do módulo 3.4. As chamadas à API não foram executadas com uma chave real.

Uso:
    python laco_manual.py "Quantos contatos há por área?"
"""

import json
import sys

import claude_util as cu
import ferramentas

# A mesma ferramenta do assistente, descrita em JSON Schema, como a API recebe.
DEFINICOES = [
    {
        "name": "resumir_base",
        "description": (
            "Conta os contatos da base tratada por valor de uma coluna. Use quando a pergunta pedir "
            "a distribuição dos contatos, como 'quantos por área'."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "coluna": {
                    "type": "string",
                    "enum": ferramentas.COLUNAS_PERMITIDAS,
                    "description": "A coluna a resumir.",
                }
            },
            "required": ["coluna"],
            "additionalProperties": False,
        },
    }
]

FUNCOES = {"resumir_base": ferramentas.resumir_base}


def executar(nome, entrada):
    """Roda a função pedida pelo modelo e devolve (texto do resultado, houve erro)."""
    if nome not in FUNCOES:
        return f"Ferramenta desconhecida: {nome}", True
    try:
        return json.dumps(FUNCOES[nome](**entrada), ensure_ascii=False), False
    except Exception as erro:      # o modelo recebe o erro e pode corrigir o pedido
        return f"Erro ao executar {nome}: {erro}", True


def responder(cliente, pergunta, max_voltas=8):
    mensagens = [{"role": "user", "content": pergunta}]
    for volta in range(max_voltas):
        resposta = cu.chamar(cliente, mensagens, tools=DEFINICOES)
        print(f"volta {volta + 1}: stop_reason = {resposta.stop_reason}")

        if resposta.stop_reason != "tool_use":
            return cu.texto_da_resposta(resposta)     # fim: resposta final, recusa ou corte

        # 1. A resposta do modelo, com os pedidos de ferramenta, entra inteira no histórico.
        mensagens.append({"role": "assistant", "content": resposta.content})

        # 2. Cada pedido é executado; todos os resultados voltam em uma única mensagem.
        resultados = []
        for bloco in resposta.content:
            if bloco.type == "tool_use":
                texto, houve_erro = executar(bloco.name, bloco.input)
                print(f"  executou {bloco.name}({bloco.input})")
                resultados.append(
                    {"type": "tool_result", "tool_use_id": bloco.id, "content": texto, "is_error": houve_erro}
                )
        mensagens.append({"role": "user", "content": resultados})
    return "O limite de voltas foi atingido sem resposta final."


if __name__ == "__main__":
    print(responder(cu.criar_cliente(), sys.argv[1]))

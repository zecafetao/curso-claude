"""Chat de terminal com streaming e histórico, com o layout do CRM nas instruções de sistema.

Solução de referência do módulo 3.1. As chamadas à API não foram executadas com uma chave real.

Uso:
    python chat_terminal.py dados_n3/layout_importacao_crm.md
"""

import sys
from pathlib import Path

import anthropic

import claude_util as cu


def montar_sistema(caminho_layout):
    """Monta as instruções de sistema com o layout de importação dentro de uma tag."""
    layout = Path(caminho_layout).read_text(encoding="utf-8")
    return (
        "Você apoia analistas de CRM que preparam bases de contatos para importação. "
        "Responda com base no layout em <layout>. Se a pergunta não puder ser respondida "
        "com o layout, diga qual informação falta. Respostas curtas, em português do Brasil.\n\n"
        f"<layout>\n{layout}\n</layout>"
    )


def responder(cliente, sistema, historico):
    """Envia o histórico, mostra a resposta conforme ela chega e devolve a mensagem final."""
    with cliente.beta.messages.stream(
        model=cu.MODELO,
        max_tokens=64000,
        system=sistema,
        messages=historico,
        output_config={"effort": "low"},
        betas=[cu.BETA_FALLBACK],
        fallbacks="default",
    ) as fluxo:
        for trecho in fluxo.text_stream:
            print(trecho, end="", flush=True)
        print()
        return fluxo.get_final_message()


def conversar(caminho_layout):
    cliente = cu.criar_cliente()
    sistema = montar_sistema(caminho_layout)
    historico = []
    total = cu.novo_total()
    print("Pergunte sobre o layout de importação. Digite 'sair' para encerrar.")

    while True:
        pergunta = input("\nVocê: ").strip()
        if pergunta == "" or pergunta.lower() == "sair":
            break
        historico.append({"role": "user", "content": pergunta})
        print("Claude: ", end="", flush=True)
        try:
            resposta = responder(cliente, sistema, historico)
        except anthropic.AuthenticationError:
            print("\nChave de API inválida ou ausente. Confira a variável ANTHROPIC_API_KEY.")
            break
        except anthropic.APIConnectionError:
            print("\nSem conexão com a API. Tente de novo.")
            historico.pop()
            continue

        cu.somar_uso(total, resposta.usage)
        if resposta.stop_reason == "refusal":
            print("[O pedido foi recusado pelos filtros de segurança. Reformule a pergunta.]")
            historico.pop()
            continue
        if resposta.stop_reason == "max_tokens":
            print("[A resposta foi cortada pelo limite de tokens.]")
        # O conteúdo volta inteiro para o histórico, e não só o texto.
        historico.append({"role": "assistant", "content": resposta.content})

    print(f"\n{cu.resumo_do_total(total)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python chat_terminal.py caminho/do/layout_importacao_crm.md")
        sys.exit(1)
    conversar(sys.argv[1])

"""Funções de apoio usadas nos scripts do Nível 3.

Situação dos testes: as funções que chamam a API (criar_cliente e chamar) foram escritas a
partir da documentação oficial e conferidas contra o SDK instalado, mas não foram executadas
com uma chave real. As demais foram executadas e têm testes em test_nivel3.py.
"""

import anthropic

MODELO = "claude-opus-5-5"
BETA_FALLBACK = "server-side-fallback-2026-07-01"
MODELOS_SEM_FALLBACK = {"claude-haiku-5-5"}

# Dólares por milhão de tokens. Referência: novembro de 2026. Confira a página oficial de preços.
# O preço do Haiku 5.5 vale para requisições com até 100 mil tokens de entrada.
PRECOS = {
    "claude-opus-5-5": {"entrada": 4.00, "saida": 20.00, "leitura_cache": 0.20},
    "claude-sonnet-5-5": {"entrada": 2.00, "saida": 10.00, "leitura_cache": 0.10},
    "claude-haiku-5-5": {"entrada": 0.10, "saida": 0.50, "leitura_cache": 0.01},
}
FATOR_ESCRITA_5MIN = 1.25    # gravar no cache com validade de 5 minutos custa 25% a mais que a entrada
FATOR_ESCRITA_1H = 2.0       # gravar no cache com validade de 1 hora custa o dobro da entrada
DESCONTO_LOTE = 0.5          # o processamento em lote custa a metade


def criar_cliente():
    """Cria o cliente da API. A chave é lida da variável de ambiente ANTHROPIC_API_KEY."""
    return anthropic.Anthropic()


def chamar(cliente, mensagens, sistema=None, modelo=MODELO, max_tokens=16000, esforco="medium",
           formato=None, **extras):
    """Faz uma chamada à API com os padrões do curso e devolve a resposta.

    - esforco: "low", "medium", "high", "xhigh" ou "max".
    - formato: um formato de saída estruturada (módulo 3.3), ou None.
    - Nos modelos que aceitam, liga o plano B automático para pedidos recusados (módulo 3.6).
    """
    configuracao = {"effort": esforco}
    if formato is not None:
        configuracao["format"] = formato
    parametros = dict(model=modelo, max_tokens=max_tokens, messages=mensagens,
                      output_config=configuracao, **extras)
    if sistema is not None:
        parametros["system"] = sistema
    if modelo in MODELOS_SEM_FALLBACK:
        return cliente.messages.create(**parametros)
    return cliente.beta.messages.create(betas=[BETA_FALLBACK], fallbacks="default", **parametros)


def texto_da_resposta(resposta):
    """Devolve o texto da resposta, ou None se o pedido foi recusado."""
    if resposta.stop_reason == "refusal":
        return None
    return "".join(bloco.text for bloco in resposta.content if bloco.type == "text")


def custo_em_dolares(uso, modelo=MODELO, lote=False):
    """Calcula o custo de uma chamada a partir do campo usage da resposta."""
    preco = PRECOS[modelo]
    escrita_total = uso.cache_creation_input_tokens or 0
    detalhe = getattr(uso, "cache_creation", None)      # divisão da escrita por validade, quando vem
    escrita_1h = (detalhe.ephemeral_1h_input_tokens or 0) if detalhe is not None else 0
    escrita_5min = escrita_total - escrita_1h
    leitura_cache = uso.cache_read_input_tokens or 0
    custo = (
        uso.input_tokens * preco["entrada"]
        + escrita_5min * preco["entrada"] * FATOR_ESCRITA_5MIN
        + escrita_1h * preco["entrada"] * FATOR_ESCRITA_1H
        + leitura_cache * preco["leitura_cache"]
        + uso.output_tokens * preco["saida"]
    ) / 1_000_000
    return custo * DESCONTO_LOTE if lote else custo


def novo_total():
    """Cria o acumulador de tokens e custo de uma execução."""
    return {"chamadas": 0, "entrada": 0, "escrita_cache": 0, "leitura_cache": 0, "saida": 0, "custo": 0.0}


def somar_uso(total, uso, modelo=MODELO, lote=False):
    """Acrescenta o uso de uma chamada ao acumulador."""
    total["chamadas"] += 1
    total["entrada"] += uso.input_tokens
    total["escrita_cache"] += uso.cache_creation_input_tokens or 0
    total["leitura_cache"] += uso.cache_read_input_tokens or 0
    total["saida"] += uso.output_tokens
    total["custo"] += custo_em_dolares(uso, modelo, lote)
    return total


def resumo_do_total(total):
    """Texto de uma linha com o consumo acumulado."""
    return (
        f"{total['chamadas']} chamadas | entrada {total['entrada']} | escrita de cache {total['escrita_cache']} | "
        f"leitura de cache {total['leitura_cache']} | saída {total['saida']} | custo US$ {total['custo']:.4f}"
    )

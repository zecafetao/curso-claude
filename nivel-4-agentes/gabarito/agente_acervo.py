"""Agente que responde perguntas sobre o acervo de relatórios e estudos, com a fonte de cada afirmação.

Solução de referência do módulo 4.8. As chamadas à API não foram executadas com uma chave real.
A busca (acervo.py) foi executada e avaliada.

Uso:
    python agente_acervo.py "Qual foi a visitação da edição 2025 e o que mudou em relação a 2024?"
"""

import json
import re
import sys

from anthropic import beta_tool

import acervo
import claude_util as cu

PASTA_ACERVO = "dados_n4/acervo"
BUSCA = acervo.BuscaBM25(acervo.dividir_em_trechos(PASTA_ACERVO))
DEVOLVIDAS = set()      # fontes que a busca devolveu na pergunta atual
CITACAO = re.compile(r"\[([^\[\]]+ › [^\[\]]+)\]")

SISTEMA = """Você responde perguntas da equipe de CRM com base no acervo de relatórios e estudos anteriores.

- Use a ferramenta buscar_acervo antes de responder. Se a primeira busca não trouxer o trecho certo,
  busque de novo com outras palavras: sinônimos, o nome do indicador, o ano.
- Responda só com o que os trechos trazem. Depois de cada afirmação, indique a fonte entre colchetes,
  no formato [arquivo › seção].
- Se o acervo não tiver a resposta, diga isso. Não complete com conhecimento geral.
- Respostas curtas, em português do Brasil."""


@beta_tool
def buscar_acervo(consulta: str) -> str:
    """Busca no acervo os três trechos mais relevantes, com o arquivo e a seção de cada um.

    A busca é por palavras: use os termos que provavelmente aparecem no documento.

    Args:
        consulta: As palavras a buscar, como "visitação 2025" ou "teste de assunto setor".
    """
    resultados = BUSCA.buscar(consulta, k=3)
    DEVOLVIDAS.update(f"{r['arquivo']} › {r['secao']}" for r in resultados)
    if not resultados:
        return "Nenhum trecho encontrado. Tente outras palavras."
    return json.dumps([
        {"fonte": f"{r['arquivo']} › {r['secao']}", "documento": r["titulo"], "texto": r["texto"]}
        for r in resultados
    ], ensure_ascii=False)


def conferir_citacoes(texto, devolvidas):
    """Conta as citações [arquivo › seção] da resposta e lista as que a busca não devolveu."""
    citadas = CITACAO.findall(texto or "")
    return {"citacoes": len(citadas), "fora_da_busca": sorted({c for c in citadas if c not in devolvidas})}


def perguntar(cliente, pergunta):
    """Devolve (texto, total de uso, consultas feitas, conferência das citações)."""
    DEVOLVIDAS.clear()
    executor = cliente.beta.messages.tool_runner(
        model=cu.MODELO, max_tokens=16000, system=SISTEMA, tools=[buscar_acervo],
        messages=[{"role": "user", "content": pergunta}], output_config={"effort": "low"},
        max_iterations=6, thread=False, **cu.opcoes_de_fallback(),
    )
    total, ultima, buscas = cu.novo_total(), None, []
    for mensagem in executor:
        cu.somar_uso(total, mensagem.usage)
        ultima = mensagem
        buscas += [b.input["consulta"] for b in mensagem.content if b.type == "tool_use"]
    texto = None if ultima is None or ultima.stop_reason == "refusal" else cu.texto_da_resposta(ultima)
    return texto, total, buscas, conferir_citacoes(texto, DEVOLVIDAS)


if __name__ == "__main__":
    texto, total, buscas, citacoes = perguntar(cu.criar_cliente(), sys.argv[1])
    print(f"Buscas feitas: {buscas}")
    print(texto if texto is not None else "O pedido foi recusado.")
    print(f"Citações: {citacoes['citacoes']} | fora do que a busca devolveu: {citacoes['fora_da_busca'] or 'nenhuma'}")
    print(cu.resumo_do_total(total))

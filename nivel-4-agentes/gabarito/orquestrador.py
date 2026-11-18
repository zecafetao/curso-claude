"""Orquestrador com dois subagentes, comparado com um agente único, no relatório mensal de e-mail.

Solução de referência do módulo 4.7. As chamadas à API não foram executadas com uma chave real.
As ferramentas de dados e a avaliação (verificar_numeros) foram executadas e testadas.

Uso:
    python orquestrador.py 2026-10 2026-09        # uma execução de cada arranjo
    python orquestrador.py 2026-10 2026-09 5      # cinco de cada, com as médias

Os dois arranjos recebem o mesmo pedido e as mesmas ferramentas de dados:
- agente único: um laço que consulta os dados e escreve os três achados;
- orquestrador: um agente que delega a redação a um subagente redator e a conferência a um
  subagente revisor, cada um com o próprio contexto.
A avaliação é a mesma para os dois: quantos números dos achados não existem nos dados (por código)
e quanto custou.
"""

import json
import sys
import time
from statistics import mean

from anthropic import beta_tool

import apresentacao as ap
import claude_util as cu
import indicadores as ind
import verificar_numeros as vn

MODELO_REDATOR = cu.MODELO
MODELO_REVISOR = cu.MODELO        # troque por "claude-haiku-5-5" para comparar custo e qualidade


# ---------- ferramentas de dados, as mesmas para todos ----------

@beta_tool
def indicadores_email(mes: str) -> str:
    """Totais e taxas de e-mail de um mês.

    Args:
        mes: Mês no formato AAAA-MM.
    """
    return json.dumps(ind.indicadores_email(mes), ensure_ascii=False)


@beta_tool
def indicadores_por_publico(mes: str) -> str:
    """Totais e taxas de e-mail por público em um mês.

    Args:
        mes: Mês no formato AAAA-MM.
    """
    return json.dumps(ind.indicadores_por_publico(mes), ensure_ascii=False)


@beta_tool
def comparar_meses(mes_atual: str, mes_anterior: str) -> str:
    """Compara os indicadores gerais de dois meses, com diferenças em pontos percentuais.

    Args:
        mes_atual: Mês analisado, AAAA-MM.
        mes_anterior: Mês de comparação, AAAA-MM.
    """
    return json.dumps(ind.comparar_meses(mes_atual, mes_anterior), ensure_ascii=False)


FERRAMENTAS_DE_DADOS = [indicadores_email, indicadores_por_publico, comparar_meses]


def rodar(cliente, modelo, sistema, pedido, ferramentas, total, max_iteracoes=10):
    """Roda um laço de ferramentas, soma o uso em 'total' e devolve o texto final."""
    executor = cliente.beta.messages.tool_runner(
        model=modelo, max_tokens=16000, system=sistema, tools=ferramentas,
        messages=[{"role": "user", "content": pedido}], output_config={"effort": "medium"},
        max_iterations=max_iteracoes, thread=False, **cu.opcoes_de_fallback(modelo),
    )
    ultima = None
    for mensagem in executor:
        cu.somar_uso(total, mensagem.usage, modelo)
        ultima = mensagem
    return None if ultima is None else cu.texto_da_resposta(ultima)


def extrair_achados(texto):
    """Lê os achados de um texto que contém uma lista JSON. Devolve [] se não houver."""
    if not texto:
        return []
    inicio, fim = texto.find("["), texto.rfind("]")
    try:
        achados = json.loads(texto[inicio:fim + 1])
    except (json.JSONDecodeError, ValueError):
        return []
    return [a for a in achados if isinstance(a, dict) and {"titulo", "fato", "proximo_passo"} <= set(a)]


FORMATO_ACHADOS = (
    "Responda só com uma lista JSON de três objetos, cada um com as chaves titulo, fato e proximo_passo. "
    "Todo número do texto vem de uma ferramenta, no mesmo valor."
)


# ---------- arranjo 1: agente único ----------

def agente_unico(cliente, mes, mes_anterior):
    total = cu.novo_total()
    sistema = f"Você escreve os achados do relatório mensal de e-mail de uma feira. {FORMATO_ACHADOS}"
    pedido = f"Escreva três achados do mês {mes}, comparando com {mes_anterior}."
    texto = rodar(cliente, MODELO_REDATOR, sistema, pedido, FERRAMENTAS_DE_DADOS, total)
    return extrair_achados(texto), total


# ---------- arranjo 2: orquestrador com dois subagentes ----------

def orquestrador(cliente, mes, mes_anterior):
    total = cu.novo_total()

    @beta_tool
    def redigir_achados(orientacao: str) -> str:
        """Pede ao subagente redator três achados do mês, escritos a partir das ferramentas de dados.

        Args:
            orientacao: O que os achados devem cobrir e o que evitar, em uma ou duas frases.
        """
        sistema = f"Você é o redator dos achados do relatório mensal de e-mail de uma feira. {FORMATO_ACHADOS}"
        pedido = f"Mês {mes}, comparação com {mes_anterior}. Orientação: {orientacao}"
        return rodar(cliente, MODELO_REDATOR, sistema, pedido, FERRAMENTAS_DE_DADOS, total) or "[]"

    @beta_tool
    def revisar_achados(achados_json: str) -> str:
        """Pede ao subagente revisor que confira cada número dos achados contra as ferramentas de dados.

        Args:
            achados_json: A lista JSON de achados devolvida pelo redator.
        """
        sistema = (
            "Você revisa números. Para cada número dos achados, consulte a ferramenta que o produz e confira "
            "o valor. Responda com uma lista JSON de problemas, cada um com numero, trecho e motivo. "
            "Lista vazia se tudo conferir."
        )
        return rodar(cliente, MODELO_REVISOR, sistema, achados_json, FERRAMENTAS_DE_DADOS, total) or "[]"

    sistema = (
        "Você coordena a produção dos achados do relatório mensal de e-mail. Peça os achados ao redator, "
        "envie-os ao revisor e, se o revisor apontar problemas, peça ao redator a correção. "
        f"No fim, {FORMATO_ACHADOS[0].lower()}{FORMATO_ACHADOS[1:]}"
    )
    pedido = f"Produza três achados do mês {mes}, comparando com {mes_anterior}."
    texto = rodar(cliente, MODELO_REDATOR, sistema, pedido, [redigir_achados, revisar_achados], total)
    return extrair_achados(texto), total


# ---------- avaliação, igual para os dois ----------

def avaliar(achados, mes, mes_anterior):
    """Conta os números verificados e sem fonte nos achados, por código."""
    referencias = ap.referencias("mensal", mes, mes_anterior)
    verificados, sem_fonte = 0, []
    for achado in achados:
        resultado = vn.verificar(" ".join(achado.values()), referencias)
        verificados += len(resultado["verificados"])
        sem_fonte += [item["numero"] for item in resultado["sem_fonte"]]
    return {"achados": len(achados), "numeros_verificados": verificados, "numeros_sem_fonte": sem_fonte}


ARRANJOS = {"agente_unico": agente_unico, "orquestrador": orquestrador}


def comparar(cliente, mes, mes_anterior, repeticoes=1, mostrar=print):
    """Roda cada arranjo 'repeticoes' vezes e resume qualidade, custo e tempo de cada um.

    Uma execução só não basta para comparar: o resultado de um agente varia de uma execução para outra.
    """
    resumo = {}
    for nome, arranjo in ARRANJOS.items():
        execucoes = []
        for _ in range(repeticoes):
            inicio = time.perf_counter()
            achados, total = arranjo(cliente, mes, mes_anterior)
            avaliacao = avaliar(achados, mes, mes_anterior)
            execucoes.append(dict(avaliacao, custo=total["custo"], chamadas=total["chamadas"],
                                  segundos=time.perf_counter() - inicio))
            mostrar(f"{nome}: {avaliacao['achados']} achados, sem fonte {avaliacao['numeros_sem_fonte']}, "
                    f"{total['chamadas']} chamadas, US$ {total['custo']:.4f}")
            for achado in achados:
                mostrar(f"  - {achado['titulo']}: {achado['fato']}")
        resumo[nome] = {
            "execucoes": repeticoes,
            "com_tres_achados": sum(e["achados"] == 3 for e in execucoes),
            "numeros_verificados": sum(e["numeros_verificados"] for e in execucoes),
            "numeros_sem_fonte": sum(len(e["numeros_sem_fonte"]) for e in execucoes),
            "chamadas_por_execucao": round(mean(e["chamadas"] for e in execucoes), 1),
            "custo_medio_usd": round(mean(e["custo"] for e in execucoes), 4),
            "segundos_por_execucao": round(mean(e["segundos"] for e in execucoes), 1),
        }
    return resumo


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print("Uso: python orquestrador.py 2026-10 2026-09 [repeticoes]")
        sys.exit(1)
    repeticoes = int(sys.argv[3]) if len(sys.argv) == 4 else 1
    resumo = comparar(cu.criar_cliente(), sys.argv[1], sys.argv[2], repeticoes)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))

"""Processa uma lista de itens com retomada: nenhum item se perde e nenhum é pago duas vezes.

Solução de referência do módulo 3.6. Este arquivo não chama a API: ele recebe a função que
processa um item. Executado e testado com falhas simuladas (falhas_simuladas.py e test_nivel3.py).

Como funciona:
- Cada item concluído vira uma linha no arquivo de progresso, gravada na hora.
- Ao começar, a função lê o arquivo de progresso e pula o que já foi concluído.
- Erros temporários são tentados de novo, com espera crescente.
- Um teto de custo e um limite de falhas seguidas interrompem a execução antes que ela saia do controle.
"""

import json
import time
from pathlib import Path

import anthropic

# Erros que costumam passar sozinhos: limite de requisições (429), falha do servidor (500 em
# diante, o que inclui sobrecarga, 529) e falha de conexão ou tempo esgotado.
ERROS_TEMPORARIOS = (anthropic.RateLimitError, anthropic.InternalServerError, anthropic.APIConnectionError)

# Erros que não adianta insistir nem seguir para o próximo item: chave inválida ou sem permissão.
ERROS_QUE_PARAM_TUDO = (anthropic.AuthenticationError, anthropic.PermissionDeniedError)

SITUACOES_FINAIS = ("ok", "recusado")     # itens nessas situações não são processados de novo


def ler_progresso(caminho):
    """Lê o arquivo de progresso. Devolve (último registro de cada item, custo já gasto)."""
    registros, gasto = {}, 0.0
    caminho = Path(caminho)
    if not caminho.exists():
        return registros, gasto
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        try:
            registro = json.loads(linha)
        except json.JSONDecodeError:
            continue                      # linha cortada por uma interrupção: é ignorada
        registros[registro["id"]] = registro
        gasto += registro.get("custo", 0.0)
    return registros, gasto


def gravar_registro(caminho, registro):
    """Acrescenta um registro ao arquivo de progresso, uma linha de JSON por item."""
    with open(caminho, "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def espera_para(erro, tentativa, espera_inicial):
    """Segundos de espera antes da próxima tentativa: dobra a cada vez e respeita o retry-after."""
    espera = espera_inicial * 2 ** (tentativa - 1)
    resposta = getattr(erro, "response", None)
    if resposta is not None:
        indicado = resposta.headers.get("retry-after", "")
        if indicado.isdigit():
            espera = max(espera, float(indicado))
    return espera


def tentar(processar, dados, temporarios, max_tentativas, espera_inicial, dormir, avisar):
    """Chama processar(dados), repetindo em caso de erro temporário. Devolve o registro do item."""
    for tentativa in range(1, max_tentativas + 1):
        try:
            return processar(dados)
        except ERROS_QUE_PARAM_TUDO:
            raise
        except temporarios as erro:
            if tentativa == max_tentativas:
                return {"situacao": "erro", "temporario": True, "detalhe": f"{type(erro).__name__}: {erro}"}
            espera = espera_para(erro, tentativa, espera_inicial)
            avisar(f"  erro temporário ({type(erro).__name__}); nova tentativa em {espera:.0f} s")
            dormir(espera)
        except Exception as erro:          # erro do pedido ou do tratamento da resposta: não se repete
            return {"situacao": "erro", "temporario": False, "detalhe": f"{type(erro).__name__}: {erro}"}


def processar_com_retomada(itens, processar, caminho_progresso, teto_de_custo=None, max_tentativas=4,
                           espera_inicial=2.0, max_falhas_seguidas=3, temporarios=ERROS_TEMPORARIOS,
                           dormir=time.sleep, avisar=print):
    """Processa os itens que ainda não foram concluídos e devolve o resumo da execução.

    itens: lista de pares (id, dados).
    processar: função que recebe os dados de um item e devolve um dicionário com "situacao"
        ("ok", "recusado" ou "erro") e, quando houver, "resultado", "custo" e "detalhe".
    teto_de_custo: em dólares, somando as execuções anteriores. None para não limitar.
    """
    registros, gasto = ler_progresso(caminho_progresso)
    falhas_seguidas = 0
    parada = None

    for identificador, dados in itens:
        anterior = registros.get(identificador)
        if anterior is not None and anterior["situacao"] in SITUACOES_FINAIS:
            continue                                         # já concluído em uma execução anterior
        if teto_de_custo is not None and gasto + 1e-9 >= teto_de_custo:   # folga para o arredondamento
            parada = "teto de custo"
            break
        if falhas_seguidas >= max_falhas_seguidas:
            parada = "falhas seguidas"
            break
        try:
            registro = tentar(processar, dados, temporarios, max_tentativas, espera_inicial, dormir, avisar)
        except KeyboardInterrupt:
            parada = "interrompido"
            break
        registro = {"id": identificador, **registro}
        gravar_registro(caminho_progresso, registro)         # gravado antes de seguir para o próximo
        registros[identificador] = registro
        gasto += registro.get("custo", 0.0)
        if registro["situacao"] == "erro":      # vários erros seguidos indicam um problema geral, não do item
            falhas_seguidas += 1
        else:
            falhas_seguidas = 0
        avisar(f"{identificador}: {registro['situacao']}")

    return resumir(itens, registros, gasto, parada)


def resumir(itens, registros, gasto, parada=None):
    """Conta os itens por situação. A soma das situações é sempre o total de itens."""
    resumo = {"total": len(itens), "ok": 0, "recusado": 0, "erro": 0, "pendente": 0, "custo": gasto, "parada": parada}
    for identificador, _ in itens:
        registro = registros.get(identificador)
        resumo[registro["situacao"] if registro else "pendente"] += 1
    return resumo


def texto_do_resumo(resumo):
    texto = (
        f"Total {resumo['total']} | ok {resumo['ok']} | recusado {resumo['recusado']} | erro {resumo['erro']} | "
        f"pendente {resumo['pendente']} | custo US$ {resumo['custo']:.4f}"
    )
    if resumo["parada"]:
        texto += f" | parada: {resumo['parada']}"
    return texto

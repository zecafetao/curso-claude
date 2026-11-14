"""A extração do módulo 3.3 com retomada, repetição em erros temporários e teto de custo.

Solução de referência do módulo 3.6. As chamadas à API não foram executadas com uma chave real.
A retomada em si (retomada.py) foi executada e testada.

Uso:
    python extrair_com_retomada.py dados_n3/contatos_texto_livre.csv extraidos.csv

Se a execução for interrompida, rode o mesmo comando de novo: ela continua de onde parou.
Para recomeçar do zero, apague o arquivo progresso_extracao.jsonl.
"""

import csv
import sys
from pathlib import Path

import anthropic

import claude_util as cu
import retomada
from extrair_contatos import CAMPOS, extrair

ARQ_PROGRESSO = Path("progresso_extracao.jsonl")
TETO_DE_CUSTO = 1.00        # em dólares, somando todas as execuções


def processar_com(cliente):
    """Devolve a função que processa um texto, no formato que a retomada espera."""
    def processar(texto):
        contato, resposta = extrair(cliente, texto)
        custo = cu.custo_em_dolares(resposta.usage)
        if resposta.stop_reason == "refusal":
            return {"situacao": "recusado", "custo": custo}
        if contato is None:
            return {"situacao": "erro", "custo": custo, "detalhe": f"resposta incompleta ({resposta.stop_reason})"}
        return {"situacao": "ok", "resultado": contato, "custo": custo}
    return processar


def gravar_saida(caminho, itens, registros):
    """Grava uma linha por item de entrada, concluído ou não. Nenhum item fica fora do arquivo."""
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["id", "situacao"] + CAMPOS, delimiter=";")
        escritor.writeheader()
        for identificador, _ in itens:
            registro = registros.get(identificador, {"situacao": "pendente"})
            escritor.writerow({"id": identificador, "situacao": registro["situacao"], **(registro.get("resultado") or {})})


if __name__ == "__main__":
    entrada, saida = sys.argv[1], sys.argv[2]
    with open(entrada, encoding="utf-8", newline="") as arquivo:
        itens = [(linha["id"], linha["texto"]) for linha in csv.DictReader(arquivo, delimiter=";")]

    cliente = cu.criar_cliente()
    try:
        resumo = retomada.processar_com_retomada(
            itens, processar_com(cliente), ARQ_PROGRESSO, teto_de_custo=TETO_DE_CUSTO
        )
    except anthropic.AuthenticationError:
        print("Chave de API inválida ou ausente. Confira a variável ANTHROPIC_API_KEY.")
        sys.exit(1)
    except anthropic.PermissionDeniedError as erro:
        print(f"A chave não tem permissão para este pedido: {erro}")
        sys.exit(1)

    registros, _ = retomada.ler_progresso(ARQ_PROGRESSO)
    gravar_saida(saida, itens, registros)
    print(retomada.texto_do_resumo(resumo))
    if resumo["pendente"] or resumo["erro"]:
        print("Há itens pendentes ou com erro. Rode o comando de novo para tentar esses itens.")

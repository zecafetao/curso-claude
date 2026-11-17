"""Mede quantas perguntas de teste têm o trecho certo entre os k primeiros resultados da busca.

Solução de referência do módulo 4.8. Executado e testado.

Uso:
    python avaliar_busca.py dados_n4/acervo dados_n4/perguntas_acervo.csv 3
"""

import csv
import sys

import acervo


def avaliar(busca, perguntas, k=3):
    """Devolve (acertos por tipo, total por tipo, lista de falhas)."""
    acertos, totais, falhas = {}, {}, []
    for item in perguntas:
        resultados = busca.buscar(item["pergunta"], k)
        achou = any(r["arquivo"] == item["arquivo"] and r["secao"] == item["secao"] for r in resultados)
        tipo = item["tipo"]
        totais[tipo] = totais.get(tipo, 0) + 1
        acertos[tipo] = acertos.get(tipo, 0) + achou
        if not achou:
            primeiro = f"{resultados[0]['arquivo']} › {resultados[0]['secao']}" if resultados else "nenhum resultado"
            falhas.append((item["pergunta"], f"{item['arquivo']} › {item['secao']}", primeiro))
    return acertos, totais, falhas


if __name__ == "__main__":
    pasta, caminho_perguntas = sys.argv[1], sys.argv[2]
    k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    with open(caminho_perguntas, encoding="utf-8", newline="") as arquivo:
        perguntas = list(csv.DictReader(arquivo, delimiter=";"))
    busca = acervo.BuscaBM25(acervo.dividir_em_trechos(pasta))
    print(f"Trechos no acervo: {len(busca.trechos)}")
    acertos, totais, falhas = avaliar(busca, perguntas, k)
    for tipo in totais:
        print(f"  {tipo}: {acertos[tipo]} de {totais[tipo]} com o trecho certo entre os {k} primeiros")
    print(f"  total: {sum(acertos.values())} de {sum(totais.values())}")
    for pergunta, esperado, primeiro in falhas:
        print(f"  FALHOU: {pergunta}\n    esperado: {esperado} | primeiro resultado: {primeiro}")

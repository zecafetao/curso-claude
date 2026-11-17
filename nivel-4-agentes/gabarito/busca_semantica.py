"""Busca por significado (embeddings da Voyage AI) e busca híbrida, que junta palavras e significado.

Solução de referência do módulo 4.8. As chamadas à Voyage AI não foram executadas: o ambiente em que o
curso foi escrito não tinha a chave nem acesso à documentação da Voyage. O código segue o exemplo da
página de embeddings da documentação da Anthropic (novembro de 2026). A fusão das listas e o cálculo
de similaridade foram executados e testados com vetores de mentira.

Instalação e chave:
    pip install -U voyageai          (versão 0.3.7 ou mais nova)
    variável de ambiente VOYAGE_API_KEY, com uma chave criada no MongoDB Atlas, em AI Model APIs

Uso:
    python busca_semantica.py dados_n4/acervo dados_n4/perguntas_acervo.csv 3
"""

import csv
import sys

import numpy as np

import acervo

MODELO_EMBEDDING = "voyage-4"
TAMANHO_DO_LOTE = 64          # textos por chamada; valor conservador


def vetorizar_com_voyage(textos, tipo):
    """Devolve uma matriz com um vetor por texto. tipo: "document" para os trechos, "query" para a pergunta."""
    import voyageai                     # importado aqui para o restante do arquivo funcionar sem o pacote

    cliente = voyageai.Client()         # lê a chave de VOYAGE_API_KEY
    vetores = []
    for inicio in range(0, len(textos), TAMANHO_DO_LOTE):
        lote = textos[inicio:inicio + TAMANHO_DO_LOTE]
        vetores += cliente.embed(lote, model=MODELO_EMBEDDING, input_type=tipo).embeddings
    return np.array(vetores)


class BuscaSemantica:
    """Ordena os trechos pela semelhança de significado com a pergunta."""

    def __init__(self, trechos, vetorizar=vetorizar_com_voyage):
        self.trechos, self.vetorizar = trechos, vetorizar
        textos = [f"{t['titulo']} — {t['secao']}: {t['texto']}" for t in trechos]
        self.vetores = self.vetorizar(textos, "document")      # uma chamada por lote, feita uma vez

    def buscar(self, consulta, k=3):
        pergunta = self.vetorizar([consulta], "query")[0]
        # Os vetores da Voyage têm comprimento 1: o produto escalar é a similaridade de cosseno.
        semelhancas = self.vetores @ pergunta
        ordem = np.argsort(-semelhancas)[:k]
        return [dict(self.trechos[i], pontos=round(float(semelhancas[i]), 3)) for i in ordem]


def fundir(listas, k=3, constante=60):
    """Fusão por posição recíproca: cada lista dá 1/(constante + posição) a cada trecho que traz."""
    pontos, trechos = {}, {}
    for lista in listas:
        for posicao, trecho in enumerate(lista, start=1):
            chave = (trecho["arquivo"], trecho["secao"])
            pontos[chave] = pontos.get(chave, 0) + 1 / (constante + posicao)
            trechos[chave] = trecho
    melhores = sorted(pontos, key=pontos.get, reverse=True)[:k]
    return [dict(trechos[chave], pontos=round(pontos[chave], 4)) for chave in melhores]


class BuscaHibrida:
    """Junta a busca por palavras e a busca por significado. Cada uma acha o que a outra perde."""

    def __init__(self, trechos, vetorizar=vetorizar_com_voyage):
        self.trechos = trechos
        self.palavras = acervo.BuscaBM25(trechos)
        self.significado = BuscaSemantica(trechos, vetorizar)

    def buscar(self, consulta, k=3, candidatos=10):
        return fundir([self.palavras.buscar(consulta, candidatos), self.significado.buscar(consulta, candidatos)], k)


if __name__ == "__main__":
    import avaliar_busca

    pasta, caminho_perguntas = sys.argv[1], sys.argv[2]
    k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    with open(caminho_perguntas, encoding="utf-8", newline="") as arquivo:
        perguntas = list(csv.DictReader(arquivo, delimiter=";"))
    trechos = acervo.dividir_em_trechos(pasta)
    for nome, busca in (("Palavras (BM25)", acervo.BuscaBM25(trechos)),
                        ("Significado (Voyage)", BuscaSemantica(trechos)),
                        ("Híbrida", BuscaHibrida(trechos))):
        acertos, totais, _ = avaliar_busca.avaliar(busca, perguntas, k)
        detalhe = " | ".join(f"{tipo} {acertos[tipo]}/{totais[tipo]}" for tipo in totais)
        print(f"{nome}: {sum(acertos.values())} de {sum(totais.values())} ({detalhe})")

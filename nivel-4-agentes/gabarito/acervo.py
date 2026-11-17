"""Busca por palavras (BM25) em um acervo de documentos em Markdown, dividido em trechos por seção.

Solução de referência do módulo 4.8. Executado e testado. Não chama nenhuma API.

Uso:
    python acervo.py dados_n4/acervo "Qual foi a visitação da edição 2025?"
"""

import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

PALAVRAS_VAZIAS = set("""
a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sobre e ou que qual quais
quanto quantos quantas como foi foram ser é são teve tem ter se ao aos à às pelo pela pelos pelas mais
menos já não sim isso este esta esse essa entre até também muito qual cada seu sua seus suas
""".split())


def normalizar(texto):
    """Minúsculas e sem acentos."""
    decomposto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(letra for letra in decomposto if not unicodedata.combining(letra))


def palavras(texto):
    """Divide o texto em palavras normalizadas, sem as palavras vazias."""
    return [p for p in re.findall(r"[a-z0-9]+", normalizar(texto)) if p not in PALAVRAS_VAZIAS]


def dividir_em_trechos(pasta):
    """Um trecho por seção (##) de cada documento, com o título do documento junto."""
    trechos = []
    for caminho in sorted(Path(pasta).glob("*.md")):
        titulo, secao, linhas = "", None, []
        for linha in caminho.read_text(encoding="utf-8").splitlines() + ["## FIM"]:
            if linha.startswith("# "):
                titulo = linha[2:].strip()
            elif linha.startswith("## "):
                if secao is not None and "".join(linhas).strip():
                    trechos.append({"arquivo": caminho.name, "titulo": titulo, "secao": secao,
                                     "texto": " ".join(l.strip() for l in linhas if l.strip())})
                secao, linhas = linha[3:].strip(), []
            elif secao is not None:
                linhas.append(linha)
    return trechos


class BuscaBM25:
    """Ordena os trechos pela fórmula BM25: palavras raras no acervo e frequentes no trecho pesam mais."""

    def __init__(self, trechos, k1=1.5, b=0.75):
        self.trechos, self.k1, self.b = trechos, k1, b
        # O título do documento e da seção entram no texto indexado: eles carregam o assunto do trecho.
        self.documentos = [palavras(f"{t['titulo']} {t['secao']} {t['texto']}") for t in trechos]
        self.media = sum(len(d) for d in self.documentos) / len(self.documentos)
        frequencia_no_acervo = Counter(p for d in self.documentos for p in set(d))
        total = len(self.documentos)
        self.idf = {p: math.log(1 + (total - n + 0.5) / (n + 0.5)) for p, n in frequencia_no_acervo.items()}

    def pontuar(self, consulta, documento):
        contagem = Counter(documento)
        pontos = 0.0
        for palavra in palavras(consulta):
            if palavra not in contagem:
                continue
            f = contagem[palavra]
            pontos += self.idf[palavra] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * len(documento) / self.media))
        return pontos

    def buscar(self, consulta, k=3):
        """Os k trechos mais relevantes, com a pontuação. Trechos sem nenhuma palavra em comum ficam de fora."""
        pontuados = [(self.pontuar(consulta, d), i) for i, d in enumerate(self.documentos)]
        melhores = sorted((p for p in pontuados if p[0] > 0), reverse=True)[:k]
        return [dict(self.trechos[i], pontos=round(p, 2)) for p, i in melhores]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Uso: python acervo.py pasta_do_acervo "pergunta"')
        sys.exit(1)
    busca = BuscaBM25(dividir_em_trechos(sys.argv[1]))
    for resultado in busca.buscar(sys.argv[2]):
        print(f"[{resultado['pontos']}] {resultado['arquivo']} › {resultado['secao']}\n    {resultado['texto'][:160]}")

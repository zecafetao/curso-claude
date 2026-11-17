"""Confere se cada número de um texto existe nos resultados das ferramentas.

Usado no módulo 4.7 (subagente revisor) e no projeto (ferramenta verificar_leituras). Executado e testado.

A regra: um número escrito pelo modelo só pode entrar no relatório se for igual a um valor calculado
por código. A comparação ignora o sinal (uma "queda de 21,0%" corresponde a -21,0) e usa uma casa
decimal para valores não inteiros. Anos (1900 a 2100) e inteiros de 0 a 10 não são conferidos: são
datas e enumerações, como "três achados" escrito com algarismo.
"""

import json
import re

NUMERO = re.compile(r"(?<![\w.,])[-+−]?\d{1,3}(?:\.\d{3})+(?:,\d+)?(?![\w])|(?<![\w.,])[-+−]?\d+(?:,\d+)?(?![\w])")
MESES = "janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro"
DATA = re.compile(
    r"\d{4}-\d{2}(?:-\d{2})?"                                   # 2026-10 ou 2026-10-20
    r"|\d{1,2}/\d{1,2}(?:/\d{2,4})?"                            # 20/10 ou 20/10/2026
    rf"|\d{{1,2}}(?:º)?(?:\s*(?:a|e|,)\s*\d{{1,2}})*\s+de\s+(?:{MESES})"  # 20 a 22 de outubro
    r"|\bdias?\s+\d{1,2}(?:\s*(?:a|e|,)\s*\d{1,2})*",                   # dia 15, dias 20 a 22
    re.IGNORECASE,
)


def para_numero(texto):
    """Converte '50.812', '52,6' ou '-21,0' em número."""
    limpo = texto.replace("−", "-").replace(".", "").replace(",", ".")
    return float(limpo)


def numeros_do_texto(texto):
    """Devolve os números de um texto em português, com o trecho de origem, sem datas."""
    sem_datas = DATA.sub(" ", texto)
    encontrados = []
    for achado in NUMERO.finditer(sem_datas):
        valor = para_numero(achado.group())
        if valor.is_integer() and (1900 <= abs(valor) <= 2100 or abs(valor) <= 10):
            continue
        inicio, fim = max(0, achado.start() - 30), min(len(sem_datas), achado.end() + 30)
        encontrados.append({"numero": achado.group(), "valor": valor, "trecho": sem_datas[inicio:fim].strip()})
    return encontrados


def valores_de(objeto):
    """Junta todos os números de um resultado de ferramenta (dicionários, listas ou texto em JSON)."""
    if isinstance(objeto, str):
        try:
            return valores_de(json.loads(objeto))
        except json.JSONDecodeError:
            return {para_numero(item["numero"]) for item in numeros_do_texto(objeto)}
    if isinstance(objeto, bool) or objeto is None:
        return set()
    if isinstance(objeto, (int, float)):
        return {float(objeto)}
    if isinstance(objeto, dict):
        valores = set()
        for chave, valor in objeto.items():
            if re.fullmatch(r"-?\d+(?:\.\d+)?", str(chave)):
                valores.add(float(chave))
            valores |= valores_de(valor)
        return valores
    if isinstance(objeto, (list, tuple, set)):
        valores = set()
        for item in objeto:
            valores |= valores_de(item)
        return valores
    return set()


def mesma_quantidade(a, b):
    """Iguais em módulo, com tolerância de arredondamento de uma casa decimal."""
    return abs(abs(a) - abs(b)) < 0.051


def verificar(texto, referencias):
    """Devolve {"verificados": [...], "sem_fonte": [...]} para os números do texto.

    referencias: resultados das ferramentas (dicionários, listas ou texto JSON).
    """
    valores = set()
    for referencia in referencias:
        valores |= valores_de(referencia)
    verificados, sem_fonte = [], []
    for item in numeros_do_texto(texto):
        if any(mesma_quantidade(item["valor"], valor) for valor in valores):
            verificados.append(item)
        else:
            sem_fonte.append(item)
    return {"verificados": verificados, "sem_fonte": sem_fonte}

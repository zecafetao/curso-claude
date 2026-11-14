"""Compara os contatos extraídos com o gabarito, campo a campo, depois de padronizar os dois lados.

Solução de referência do módulo 3.3. Executado e testado.

Uso:
    python avaliar_extracao.py extraidos.csv dados_n3/contatos_texto_livre_gabarito.csv
"""

import csv
import sys
import unicodedata

import validacao as v

CAMPOS = ["nome", "sobrenome", "email", "telefone", "empresa", "cargo"]


def chave_texto(texto):
    """Texto em minúsculas, sem acentos e sem espaços repetidos, para comparação."""
    decomposto = unicodedata.normalize("NFKD", str(texto))
    sem_acento = "".join(letra for letra in decomposto if not unicodedata.combining(letra))
    return " ".join(sem_acento.lower().split())


def padronizar(campo, valor):
    """Leva o valor de um campo à forma em que ele é comparado."""
    if campo == "email":
        return v.padronizar_email(valor)
    if campo == "telefone":
        return v.padronizar_telefone(valor) or ""
    if campo == "empresa":
        return chave_texto(v.padronizar_empresa(valor))
    return chave_texto(valor)


def ler(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return {linha["id"]: linha for linha in csv.DictReader(arquivo, delimiter=";")}


def avaliar(extraidos, gabarito):
    """Devolve (acertos por campo, lista de erros, quantidade de registros sem resultado)."""
    acertos = {campo: 0 for campo in CAMPOS}
    erros, sem_resultado = [], 0
    for ident, esperado in gabarito.items():
        obtido = extraidos.get(ident)
        if obtido is None or obtido.get("situacao", "ok") != "ok":
            sem_resultado += 1
            continue
        for campo in CAMPOS:
            if padronizar(campo, obtido.get(campo) or "") == padronizar(campo, esperado[campo]):
                acertos[campo] += 1
            else:
                erros.append((ident, campo, esperado[campo], obtido.get(campo) or ""))
    return acertos, erros, sem_resultado


if __name__ == "__main__":
    extraidos, gabarito = ler(sys.argv[1]), ler(sys.argv[2])
    acertos, erros, sem_resultado = avaliar(extraidos, gabarito)
    total = len(gabarito)
    print(f"Registros: {total} | sem resultado: {sem_resultado}")
    for campo in CAMPOS:
        print(f"  {campo}: {acertos[campo]} de {total}")
    completos = total - sem_resultado - len({ident for ident, _, _, _ in erros})
    print(f"Registros com todos os campos corretos: {completos} de {total}")
    for ident, campo, esperado, obtido in erros[:20]:
        print(f"  ERRO {ident} {campo}: esperado {esperado!r}, obtido {obtido!r}")

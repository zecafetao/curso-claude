"""Confere a saída do projeto da etapa Ponte contra a saída esperada.

Rode a partir da pasta em que este arquivo está, informando a pasta gerada pelo seu script:
    python conferir_projeto.py caminho/da/sua/pasta_de_saida
"""

import csv
import sys
from pathlib import Path

ESPERADA = Path(__file__).parent / "saida_esperada"
ARQUIVOS = {
    "importar.csv": None,                    # todas as colunas
    "rejeitados.csv": ["linha", "motivo"],
    "avisos.csv": ["linha", "aviso"],
}


def ler(caminho, colunas):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")
        cabecalho = leitor.fieldnames
        usar = colunas or cabecalho
        linhas = [tuple(linha.get(coluna, "<coluna ausente>") for coluna in usar) for linha in leitor]
    return cabecalho, sorted(linhas)


pasta = Path(sys.argv[1])
tudo_certo = True
for nome, colunas in ARQUIVOS.items():
    if not (pasta / nome).exists():
        print(f"{nome}: arquivo não encontrado em {pasta}")
        tudo_certo = False
        continue
    cabecalho_esperado, esperado = ler(ESPERADA / nome, colunas)
    cabecalho_obtido, obtido = ler(pasta / nome, colunas)
    if colunas is None and cabecalho_obtido != cabecalho_esperado:
        print(f"{nome}: colunas diferentes do layout.")
        print(f"  esperado: {cabecalho_esperado}")
        print(f"  obtido:   {cabecalho_obtido}")
        tudo_certo = False
        continue
    faltando = [linha for linha in esperado if linha not in obtido]
    sobrando = [linha for linha in obtido if linha not in esperado]
    if not faltando and not sobrando:
        print(f"{nome}: correto ({len(obtido)} linhas)")
        continue
    tudo_certo = False
    print(f"{nome}: {len(obtido)} linhas, esperadas {len(esperado)}")
    for linha in faltando[:5]:
        print(f"  falta ou está diferente: {linha}")
    for linha in sobrando[:5]:
        print(f"  não deveria estar assim: {linha}")

print("Projeto aprovado no conferidor." if tudo_certo else "Ainda há diferenças.")

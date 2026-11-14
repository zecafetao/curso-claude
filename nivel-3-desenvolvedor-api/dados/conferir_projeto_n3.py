"""Confere a saída do projeto do Nível 3 contra a saída esperada.

Rode informando a pasta gerada pelo seu script:
    python dados_n3/conferir_projeto_n3.py saida_projeto

O que é conferido:
- importar.csv: todas as colunas, menos area, precisam ser iguais à saída esperada.
- area: é medida a taxa de acerto por contato. O mínimo para aprovação é 90%.
- rejeitados.csv e avisos.csv: iguais à saída esperada.
- decisoes_cargos.csv e custo.txt: precisam existir.
"""

import csv
import sys
from pathlib import Path

ESPERADA = Path(__file__).parent / "saida_esperada_projeto"
AREAS = ["Compras", "Produção", "Marketing", "Comercial", "Diretoria", "Outros"]
MINIMO_DE_ACERTO = 0.90


def ler(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")
        return leitor.fieldnames, list(leitor)


def comparar(nome, colunas, pasta):
    """Compara as colunas indicadas de um arquivo com a saída esperada. Devolve True se forem iguais."""
    _, esperado = ler(ESPERADA / nome)
    _, obtido = ler(pasta / nome)
    esperado = sorted(tuple(linha.get(coluna, "") for coluna in colunas) for linha in esperado)
    obtido = sorted(tuple(linha.get(coluna, "<coluna ausente>") for coluna in colunas) for linha in obtido)
    faltando = [linha for linha in esperado if linha not in obtido]
    sobrando = [linha for linha in obtido if linha not in esperado]
    if not faltando and not sobrando:
        print(f"{nome}: correto ({len(obtido)} linhas)")
        return True
    print(f"{nome}: {len(obtido)} linhas, esperadas {len(esperado)}")
    for linha in faltando[:5]:
        print(f"  falta ou está diferente: {linha}")
    for linha in sobrando[:5]:
        print(f"  não deveria estar assim: {linha}")
    return False


pasta = Path(sys.argv[1])
tudo_certo = True

for nome in ["importar.csv", "rejeitados.csv", "avisos.csv", "decisoes_cargos.csv", "custo.txt"]:
    if not (pasta / nome).exists():
        print(f"{nome}: arquivo não encontrado em {pasta}")
        tudo_certo = False
if not tudo_certo:
    print("Ainda há diferenças.")
    sys.exit(1)

cabecalho_esperado, esperado = ler(ESPERADA / "importar.csv")
cabecalho_obtido, obtido = ler(pasta / "importar.csv")
if cabecalho_obtido != cabecalho_esperado:
    print("importar.csv: colunas diferentes do layout.")
    print(f"  esperado: {cabecalho_esperado}")
    print(f"  obtido:   {cabecalho_obtido}")
    tudo_certo = False
else:
    sem_area = [coluna for coluna in cabecalho_esperado if coluna != "area"]
    tudo_certo = comparar("importar.csv", sem_area, pasta) and tudo_certo

    area_certa = {linha["email"]: linha["area"] for linha in esperado}
    fora_da_lista = sorted({linha["area"] for linha in obtido if linha["area"] not in AREAS})
    if fora_da_lista:
        print(f"area: valores fora da lista do layout: {fora_da_lista}")
        tudo_certo = False
    acertos, erros = 0, {}
    for linha in obtido:
        certa = area_certa.get(linha["email"])
        if linha["area"] == certa:
            acertos += 1
        else:
            chave = (linha["cargo"], linha["area"], certa)
            erros[chave] = erros.get(chave, 0) + 1
    taxa = acertos / max(len(obtido), 1)
    print(f"area: {acertos} de {len(obtido)} contatos com a área correta ({taxa:.1%}). Mínimo: {MINIMO_DE_ACERTO:.0%}")
    for (cargo, veio, certa), vezes in sorted(erros.items(), key=lambda item: -item[1]):
        print(f"  {vezes}x {cargo}: veio {veio}, esperado {certa}")
    if taxa < MINIMO_DE_ACERTO:
        tudo_certo = False

tudo_certo = comparar("rejeitados.csv", ["linha", "motivo"], pasta) and tudo_certo
tudo_certo = comparar("avisos.csv", ["linha", "aviso"], pasta) and tudo_certo

_, decisoes = ler(pasta / "decisoes_cargos.csv")
print(f"decisoes_cargos.csv: {len(decisoes)} cargos")
if "Custo total" not in (pasta / "custo.txt").read_text(encoding="utf-8"):
    print("custo.txt: não encontrei a linha 'Custo total'.")
    tudo_certo = False

print("Projeto aprovado no conferidor." if tudo_certo else "Ainda há diferenças.")

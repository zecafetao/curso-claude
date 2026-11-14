"""Trata uma base bruta de contatos e gera o arquivo no layout de importação do CRM.

Solução de referência do projeto da etapa Ponte. Tente escrever a sua versão antes de ler.

Uso:
    python tratar_base.py base_bruta.csv descadastrados.xlsx pasta_de_saida
    python tratar_base.py base_bruta.csv descadastrados.xlsx pasta_de_saida ceps.csv

O quarto argumento é opcional (desafio do projeto): a tabela de CEPs do módulo P.4,
usada para preencher cidade e UF com os nomes oficiais.
"""

import sys
from pathlib import Path

import pandas as pd

import validacao as v

RENOMEAR = {
    "Nome Completo": "nome_completo",
    "E-mail": "email_bruto",
    "Telefone": "telefone_bruto",
    "Empresa": "empresa_bruta",
    "CNPJ": "cnpj_bruto",
    "Cargo": "cargo_bruto",
    "CEP": "cep_bruto",
    "Cidade": "cidade_bruta",
    "UF": "uf_bruta",
    "Origem": "origem_bruta",
    "Aceita comunicação": "aceita",
    "Data aceite": "data_aceite",
}

LAYOUT = [
    "email", "nome", "sobrenome", "telefone", "empresa", "cnpj", "cargo", "area",
    "cidade", "uf", "origem", "consentimento", "data_consentimento",
]


def ler_base(caminho):
    """Lê a base bruta mantendo tudo como texto, para não perder zeros à esquerda."""
    base = pd.read_csv(caminho, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    faltando = [coluna for coluna in RENOMEAR if coluna not in base.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes na base: {faltando}")
    base = base.rename(columns=RENOMEAR)
    base["linha"] = base.index + 2  # a linha 1 do arquivo é o cabeçalho
    return base


def ler_descadastrados(caminho):
    """Lê a lista de descadastrados e devolve o conjunto de e-mails padronizados."""
    tabela = pd.read_excel(caminho, dtype=str)
    return set(tabela["email"].map(v.padronizar_email))


def padronizar(base):
    """Cria as colunas do layout a partir das colunas brutas."""
    base = base.copy()
    base["email"] = base["email_bruto"].map(v.padronizar_email)

    nomes = [v.separar_nome(texto) for texto in base["nome_completo"]]
    base["nome"] = [par[0] for par in nomes]
    base["sobrenome"] = [par[1] for par in nomes]

    telefones = [v.padronizar_telefone(texto) for texto in base["telefone_bruto"]]
    base["telefone"] = [telefone or "" for telefone in telefones]
    base["aviso_telefone"] = (base["telefone_bruto"].str.strip() != "") & (base["telefone"] == "")

    base["empresa"] = base["empresa_bruta"].map(v.padronizar_empresa)
    base["cnpj"] = base["cnpj_bruto"].map(v.padronizar_cnpj)
    base["aviso_cnpj"] = (base["cnpj_bruto"].str.strip() != "") & (base["cnpj"] == "")

    base["cargo"] = base["cargo_bruto"].map(v.limpar_texto)
    base["area"] = base["cargo"].map(v.area_do_cargo)
    base["cep"] = base["cep_bruto"].map(v.padronizar_cep)
    base["cidade"] = base["cidade_bruta"].map(v.capitalizar_nome)
    base["uf"] = base["uf_bruta"].map(v.padronizar_uf)

    origens = [v.padronizar_origem(texto) for texto in base["origem_bruta"]]
    base["origem"] = [origem or "" for origem in origens]

    consentimentos = [
        v.padronizar_consentimento(aceita, data)
        for aceita, data in zip(base["aceita"], base["data_aceite"])
    ]
    base["consentimento"] = [item[0] for item in consentimentos]
    base["data_consentimento"] = [item[1] for item in consentimentos]
    base["aviso_consentimento"] = [item[2] for item in consentimentos]
    return base


def aplicar_ceps(base, caminho_ceps):
    """Troca cidade e UF pelos nomes oficiais quando o CEP da linha foi encontrado."""
    ceps = pd.read_csv(caminho_ceps, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    ceps = ceps[ceps["situacao"] == "encontrado"]
    cidade_por_cep = dict(zip(ceps["cep"], ceps["cidade"]))
    uf_por_cep = dict(zip(ceps["cep"], ceps["uf"]))

    base = base.copy()
    encontrado = base["cep"].isin(cidade_por_cep)
    base.loc[encontrado, "cidade"] = base.loc[encontrado, "cep"].map(cidade_por_cep)
    base.loc[encontrado, "uf"] = base.loc[encontrado, "cep"].map(uf_por_cep)
    return base


def classificar(base, descadastrados):
    """Preenche a coluna 'motivo' das linhas rejeitadas. A ordem das regras é a do enunciado."""
    base = base.copy()
    base["motivo"] = ""

    email_ok = base["email"].map(v.email_valido)
    base.loc[~email_ok, "motivo"] = "e-mail inválido"

    sem_motivo = base["motivo"] == ""
    base.loc[sem_motivo & (base["nome"] == ""), "motivo"] = "nome ausente"

    sem_motivo = base["motivo"] == ""
    base.loc[sem_motivo & (base["origem"] == ""), "motivo"] = "origem não reconhecida"

    sem_motivo = base["motivo"] == ""
    base.loc[sem_motivo & base["email"].isin(descadastrados), "motivo"] = "descadastrado"

    # Duplicados só entre as linhas que continuam válidas; fica a primeira ocorrência.
    validas = base[base["motivo"] == ""]
    repetidas = validas[validas.duplicated(subset="email", keep="first")].index
    base.loc[repetidas, "motivo"] = "e-mail repetido"
    return base


def montar_avisos(importar):
    """Lista os campos corrigidos de forma conservadora nas linhas que serão importadas."""
    tipos = {
        "aviso_telefone": "telefone descartado",
        "aviso_cnpj": "cnpj descartado",
        "aviso_consentimento": "consentimento rebaixado",
    }
    partes = []
    for coluna, texto in tipos.items():
        parte = importar.loc[importar[coluna], ["linha", "email"]].copy()
        parte["aviso"] = texto
        partes.append(parte)
    return pd.concat(partes).sort_values(["linha", "aviso"])


def tratar(caminho_base, caminho_descadastrados, pasta_saida, caminho_ceps=None):
    """Executa o tratamento completo e grava os arquivos de saída. Devolve o resumo."""
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    base = ler_base(caminho_base)
    descadastrados = ler_descadastrados(caminho_descadastrados)
    base = padronizar(base)
    if caminho_ceps is not None:
        base = aplicar_ceps(base, caminho_ceps)
    base = classificar(base, descadastrados)

    importar = base[base["motivo"] == ""]
    rejeitados = base[base["motivo"] != ""]
    avisos = montar_avisos(importar)

    importar[LAYOUT].to_csv(pasta_saida / "importar.csv", sep=";", index=False, encoding="utf-8")
    rejeitados[["linha", "email_bruto", "motivo"]].to_csv(
        pasta_saida / "rejeitados.csv", sep=";", index=False, encoding="utf-8"
    )
    avisos.to_csv(pasta_saida / "avisos.csv", sep=";", index=False, encoding="utf-8")

    linhas = [
        f"Linhas lidas: {len(base)}",
        f"Linhas para importar: {len(importar)}",
        f"Linhas rejeitadas: {len(rejeitados)}",
    ]
    for motivo, quantidade in rejeitados["motivo"].value_counts().sort_index().items():
        linhas.append(f"  {motivo}: {quantidade}")
    linhas.append(f"Avisos: {len(avisos)}")
    for aviso, quantidade in avisos["aviso"].value_counts().sort_index().items():
        linhas.append(f"  {aviso}: {quantidade}")
    resumo = "\n".join(linhas)
    (pasta_saida / "resumo.txt").write_text(resumo + "\n", encoding="utf-8")
    return resumo


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        print("Uso: python tratar_base.py base_bruta.csv descadastrados.xlsx pasta_de_saida [ceps.csv]")
        sys.exit(1)
    print(tratar(*sys.argv[1:]))

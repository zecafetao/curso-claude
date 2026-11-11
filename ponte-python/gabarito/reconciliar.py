"""Reconcilia as bases de uma feira que não têm chave comum e monta o funil em pessoas.

Solução de referência do módulo P.7. Tente escrever a sua versão antes de ler.

Uso:
    python reconciliar.py pasta_dos_dados
"""

import sys
import unicodedata
from pathlib import Path

import pandas as pd

import validacao as v


def chave_nome(texto):
    """Nome em minúsculas, sem acentos e sem espaços repetidos, para comparação."""
    decomposto = unicodedata.normalize("NFKD", str(texto))
    sem_acento = "".join(letra for letra in decomposto if not unicodedata.combining(letra))
    return " ".join(sem_acento.lower().split())


def ler_fonte(caminho, fonte):
    """Lê uma base e cria as três chaves de comparação: e-mail, telefone e nome."""
    base = pd.read_csv(caminho, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    base["fonte"] = fonte
    base["email"] = base["email"].map(v.padronizar_email)
    base["telefone"] = [v.padronizar_telefone(texto) or "" for texto in base["telefone"]]
    base["nome_chave"] = base["nome"].map(chave_nome)
    return base


def identificar_pessoas(registros, colunas=("telefone", "nome_chave")):
    """Cria a coluna 'pessoa'.

    A identidade parte do e-mail. Registros com os mesmos valores nas colunas de identidade
    são tratados como a mesma pessoa, mesmo com e-mails diferentes, e recebem o e-mail do
    primeiro registro do grupo. O padrão é telefone e nome juntos: telefone sozinho junta
    colegas que dividem o ramal, e nome sozinho junta homônimos.
    """
    colunas = list(colunas)
    registros = registros.copy()
    registros["pessoa"] = registros["email"]
    completos = (registros[colunas] != "").all(axis=1)
    chave = registros[colunas].agg("|".join, axis=1)
    primeiro_email = registros[completos].groupby(chave[completos])["email"].transform("first")
    registros.loc[completos, "pessoa"] = primeiro_email
    return registros


def pessoas_da_fonte(registros, fonte):
    """Conjunto das pessoas que aparecem em uma fonte."""
    return set(registros.loc[registros["fonte"] == fonte, "pessoa"])


def entrega_whatsapp(caminho):
    """Lê as tentativas e devolve (tentativas, resumo por disparo, telefones que receberam)."""
    tentativas = pd.read_csv(caminho, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    tentativas["telefone"] = [v.padronizar_telefone(texto) or "" for texto in tentativas["telefone"]]
    tentativas["entregue"] = tentativas["status"] == "entregue"
    tentativas["erro"] = tentativas["status"] == "erro"

    # Um contato recebeu o disparo se pelo menos uma tentativa foi entregue.
    por_contato = tentativas.groupby(["disparo", "telefone"], as_index=False).agg(
        recebeu=("entregue", "max"), tentativas_com_erro=("erro", "sum")
    )
    resumo = por_contato.groupby("disparo", as_index=False).agg(
        contatos=("telefone", "count"),
        receberam=("recebeu", "sum"),
        tentativas_com_erro=("tentativas_com_erro", "sum"),
    )
    resumo["nao_receberam"] = resumo["contatos"] - resumo["receberam"]
    resumo["entrega"] = (100 * resumo["receberam"] / resumo["contatos"]).round(1)

    recebeu_algum = tentativas.groupby("telefone")["entregue"].max()
    return tentativas, resumo, set(recebeu_algum[recebeu_algum].index)


def taxa(parte, total):
    return f"{100 * parte / total:.1f}%".replace(".", ",")


if __name__ == "__main__":
    pasta = Path(sys.argv[1])
    fontes = {
        "credenciados": "feira_credenciados.csv",
        "visitantes": "feira_visitantes.csv",
        "inscritos": "feira_inscritos_evento.csv",
    }
    registros = pd.concat(
        [ler_fonte(pasta / arquivo, fonte) for fonte, arquivo in fontes.items()], ignore_index=True
    )

    print("1. LINHAS E E-MAILS POR FONTE")
    soma_emails = 0
    for fonte in fontes:
        parte = registros[registros["fonte"] == fonte]
        soma_emails += parte["email"].nunique()
        print(f"  {fonte}: {len(parte)} linhas, {parte['email'].nunique()} e-mails distintos")
    print(f"  Soma dos e-mails distintos das três fontes: {soma_emails}")

    registros = identificar_pessoas(registros)
    por_email = registros["email"].nunique()
    pessoas = registros["pessoa"].nunique()
    print("\n2. UNIÃO")
    print(f"  União por e-mail: {por_email}")
    print(f"  Pessoas, depois de resolver a identidade por telefone e nome: {pessoas}")
    print(f"  Duplicidades ocultas (mesma pessoa, e-mails diferentes): {por_email - pessoas}")

    so_telefone = identificar_pessoas(registros, ["telefone"])["pessoa"].nunique()
    so_nome = identificar_pessoas(registros, ["nome_chave"])["pessoa"].nunique()
    print(f"  Se a identidade fosse só o telefone: {so_telefone} (junta colegas que dividem o ramal)")
    print(f"  Se a identidade fosse só o nome: {so_nome} (junta homônimos)")

    cred = pessoas_da_fonte(registros, "credenciados")
    vis = pessoas_da_fonte(registros, "visitantes")
    insc = pessoas_da_fonte(registros, "inscritos")
    print("\n3. SOBREPOSIÇÕES, EM PESSOAS")
    print(f"  Na base de credenciados: {len(cred)} | na de visitantes: {len(vis)} | na de inscritos: {len(insc)}")
    print(f"  Credenciados e visitantes: {len(cred & vis)}")
    print(f"  Credenciados e inscritos: {len(cred & insc)}")
    print(f"  Visitantes e inscritos: {len(vis & insc)}")
    print(f"  Nas três: {len(cred & vis & insc)}")
    print(f"  Visitantes fora da base de credenciados: {len(vis - cred)}")

    com_check_in = set(
        registros.loc[(registros["fonte"] == "inscritos") & (registros["check_in"] == "S"), "pessoa"]
    )
    todos = cred | vis | insc
    visitaram = vis | com_check_in
    print("\n4. FUNIL, EM PESSOAS")
    print(f"  Credenciados (união das três bases): {len(todos)}")
    print(f"  Visitantes (leitura de credencial ou check-in no evento): {len(visitaram)} ({taxa(len(visitaram), len(todos))} dos credenciados)")
    print(f"  Participantes do evento (check-in): {len(com_check_in)} ({taxa(len(com_check_in), len(visitaram))} dos visitantes)")
    sem_resolver = registros.loc[registros["fonte"] == "visitantes", "email"].nunique()
    base_email = registros.loc[registros["fonte"] == "credenciados", "email"].nunique()
    cruzados = len(
        set(registros.loc[registros["fonte"] == "credenciados", "email"])
        & set(registros.loc[registros["fonte"] == "visitantes", "email"])
    )
    print(f"  Conta ingênua, só por e-mail: {cruzados} de {base_email} credenciados visitaram ({taxa(cruzados, base_email)}); {sem_resolver} e-mails na base de visitantes")

    dias = registros[registros["fonte"] == "visitantes"].groupby("pessoa")["dia"].nunique()
    print("\n5. DIAS DE PRESENÇA (base de visitantes)")
    print(f"  Leituras: {len(registros[registros['fonte'] == 'visitantes'])} | pessoas: {len(dias)} | dias por pessoa: {dias.mean():.2f}".replace(".", ","))
    for quantidade, pessoas_no_grupo in dias.value_counts().sort_index().items():
        print(f"  {quantidade} dia(s): {pessoas_no_grupo}")

    tentativas, resumo, receberam = entrega_whatsapp(pasta / "feira_whatsapp_tentativas.csv")
    print("\n6. WHATSAPP")
    print(resumo.to_string(index=False))
    contatos = tentativas["telefone"].nunique()
    erros = int(tentativas["erro"].sum())
    print(f"  Contatos distintos: {contatos} | receberam ao menos uma mensagem: {len(receberam)} | nunca receberam: {contatos - len(receberam)}")
    print(f"  Tentativas: {len(tentativas)} | com erro: {erros}")

    registros["recebeu"] = registros["telefone"].isin(receberam)
    por_pessoa = registros.groupby("pessoa", as_index=False)["recebeu"].max()
    por_pessoa["visitou"] = por_pessoa["pessoa"].isin(visitaram)
    print("\n7. WHATSAPP E VISITAÇÃO, EM PESSOAS")
    for recebeu, grupo in por_pessoa.groupby("recebeu"):
        rotulo = "Recebeu ao menos uma mensagem" if recebeu else "Não recebeu"
        print(f"  {rotulo}: {len(grupo)} pessoas, {int(grupo['visitou'].sum())} visitaram ({taxa(grupo['visitou'].sum(), len(grupo))})")

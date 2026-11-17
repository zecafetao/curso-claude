"""Ferramentas sobre as fontes grandes da Expo Modelo Sul 2026 (fictícia), do módulo 4.6.

Executado e testado. As fontes juntas têm cerca de 5,8 milhões de caracteres: não cabem na janela de
contexto. As funções leem os arquivos no computador e devolvem só resumos.
"""

import os
from pathlib import Path

import pandas as pd

import reconciliar as rc
import validacao as v

PASTA = Path(os.environ.get("PASTA_FEIRA_GRANDE", "dados_n4/feira_grande"))
FONTES = {
    "credenciados": "credenciados.csv.gz",
    "visitantes": "visitantes.csv.gz",
    "whatsapp_tentativas": "whatsapp_tentativas.csv.gz",
}
_cache = {}


def ler(fonte):
    """Lê uma fonte compactada, com tudo como texto. Guarda em memória para as próximas chamadas."""
    if fonte not in FONTES:
        raise ValueError(f"Fonte desconhecida: {fonte}. Use uma destas: {', '.join(FONTES)}.")
    if fonte not in _cache:
        _cache[fonte] = pd.read_csv(PASTA / FONTES[fonte], sep=";", dtype=str, keep_default_na=False,
                                    encoding="utf-8", compression="gzip")
    return _cache[fonte]


def descrever_fontes():
    """Linhas, colunas e tamanho em caracteres de cada fonte. Não devolve nenhum registro."""
    resumo = {}
    for fonte in FONTES:
        base = ler(fonte)
        caracteres = int(base.to_csv(sep=";", index=False).__len__())
        resumo[fonte] = {"linhas": len(base), "colunas": list(base.columns), "caracteres": caracteres}
    resumo["observacao"] = "Os registros ficam no computador; as ferramentas devolvem só contagens."
    return resumo


def _registros():
    partes = []
    for fonte in ("credenciados", "visitantes"):
        base = ler(fonte).copy()
        base["fonte"] = fonte
        base["email"] = base["email"].map(v.padronizar_email)
        base["telefone"] = [v.padronizar_telefone(texto) or "" for texto in base["telefone"]]
        base["nome_chave"] = base["nome"].map(rc.chave_nome)
        partes.append(base)
    return rc.identificar_pessoas(pd.concat(partes, ignore_index=True))


def funil():
    """Credenciados e visitantes em pessoas, depois de resolver a identidade."""
    registros = _registros()
    credenciados = rc.pessoas_da_fonte(registros, "credenciados")
    visitantes = rc.pessoas_da_fonte(registros, "visitantes")
    todos = credenciados | visitantes
    return {
        "linhas_de_credenciamento": int((registros["fonte"] == "credenciados").sum()),
        "cadastros_duplicados": int((registros["fonte"] == "credenciados").sum()) - len(credenciados),
        "credenciados": len(todos),
        "visitantes": len(visitantes),
        "taxa_visitacao": round(100 * len(visitantes) / len(todos), 1),
        "visitantes_credenciados_na_hora": len(visitantes - credenciados),
    }


def presenca_por_dia():
    """Leituras e visitantes distintos por dia, e quantos dias cada visitante foi."""
    registros = _registros()
    visitas = registros[registros["fonte"] == "visitantes"]
    por_dia = visitas.groupby("dia")["pessoa"].nunique()
    dias = visitas.groupby("pessoa")["dia"].nunique().value_counts().sort_index()
    return {
        "visitantes_por_dia": {dia: int(n) for dia, n in por_dia.items()},
        "visitantes_por_dias_de_presenca": {str(k): int(n) for k, n in dias.items()},
    }


def credenciados_por_uf():
    """Credenciados por UF, em pessoas, do maior para o menor."""
    registros = _registros()
    credenciados = registros[registros["fonte"] == "credenciados"].drop_duplicates("pessoa")
    contagem = credenciados["uf"].value_counts()
    return {"credenciados_por_uf": {uf: int(n) for uf, n in contagem.items()}}


def entrega_whatsapp():
    """Entrega por disparo de WhatsApp, em contatos."""
    tentativas = ler("whatsapp_tentativas")
    entregue = tentativas.assign(entregue=tentativas["status"] == "entregue")
    por_contato = entregue.groupby(["disparo", "telefone"])["entregue"].max().reset_index()
    resumo = por_contato.groupby("disparo")["entregue"].agg(["count", "sum"])
    return {
        "tentativas": len(tentativas),
        "disparos": [
            {"disparo": d, "contatos": int(linha["count"]), "receberam": int(linha["sum"]),
             "taxa_entrega": round(100 * linha["sum"] / linha["count"], 1)}
            for d, linha in resumo.iterrows()
        ],
    }

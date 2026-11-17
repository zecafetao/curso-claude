"""Indicadores da campanha calculados a partir do banco SQLite.

Usado pelo servidor MCP (módulo 4.3), pelos agentes dos módulos 4.5 a 4.7 e pelo projeto.
Executado e testado.

Regras de desenho, as mesmas do módulo 3.4:
- toda função devolve contagens e taxas, nunca linhas com dados de pessoas;
- valores fora do esperado geram um erro claro, e não um zero;
- as consultas usam parâmetros (?), nunca texto montado com os valores recebidos.
"""

import os
import re
import sqlite3
from pathlib import Path

import pandas as pd

import reconciliar as rc
import validacao as v

CAMINHO_BANCO = Path(os.environ.get("BANCO_CAMPANHA", "dados_n4/campanha.db"))
MINIMO_DE_ENVIOS = 10       # abaixo disso, o disparo é resposta automática ou teste (método do relatório)
LIMITE_DE_CLIQUE = 15.0     # acima disso, possível clique automático
FORMATO_MES = re.compile(r"^\d{4}-\d{2}$")


def conectar():
    """Abre o banco só para leitura. As ferramentas não alteram dados."""
    if not CAMINHO_BANCO.exists():
        raise FileNotFoundError(f"Banco não encontrado: {CAMINHO_BANCO}. Rode o montar_banco.py.")
    return sqlite3.connect(f"file:{CAMINHO_BANCO}?mode=ro", uri=True)


def consultar(sql, parametros=()):
    """Roda uma consulta e devolve um DataFrame."""
    with conectar() as conexao:
        return pd.read_sql_query(sql, conexao, params=parametros)


def taxa(parte, total):
    """Percentual com uma casa decimal. Devolve None quando o total é zero."""
    return round(100 * parte / total, 1) if total else None


def meses_disponiveis():
    """Os meses que têm disparos de e-mail no banco."""
    return list(consultar("SELECT DISTINCT mes FROM disparos_email ORDER BY mes")["mes"])


def conferir_mes(mes):
    """Devolve uma mensagem de erro se o mês for inválido ou não estiver no banco, ou None."""
    if not FORMATO_MES.match(str(mes)):
        return f"Mês inválido: {mes}. Use o formato AAAA-MM, como 2026-10."
    disponiveis = meses_disponiveis()
    if mes not in disponiveis:
        return f"Não há disparos de e-mail em {mes}. Meses disponíveis: {', '.join(disponiveis)}."
    return None


def indicadores_email(mes):
    """Totais e taxas de e-mail de um mês, sem os disparos abaixo do mínimo de envios."""
    erro = conferir_mes(mes)
    if erro:
        return {"erro": erro}
    totais = consultar(
        """
        SELECT COUNT(*) AS disparos, SUM(enviadas) AS enviadas, SUM(entregues) AS entregues,
               SUM(aberturas_unicas) AS aberturas_unicas, SUM(cliques_unicos) AS cliques_unicos,
               SUM(descadastros) AS descadastros
        FROM disparos_email
        WHERE mes = ? AND enviadas >= ?
        """,
        (mes, MINIMO_DE_ENVIOS),
    ).iloc[0]
    excluidos = consultar(
        "SELECT disparo, enviadas FROM disparos_email WHERE mes = ? AND enviadas < ? ORDER BY disparo",
        (mes, MINIMO_DE_ENVIOS),
    )
    resultado = {chave: int(valor) for chave, valor in totais.items()}
    resultado.update({
        "mes": mes,
        "taxa_entrega": taxa(resultado["entregues"], resultado["enviadas"]),
        "taxa_abertura": taxa(resultado["aberturas_unicas"], resultado["entregues"]),
        "taxa_clique": taxa(resultado["cliques_unicos"], resultado["entregues"]),
        "disparos_excluidos": [
            {"disparo": linha.disparo, "enviadas": int(linha.enviadas)} for linha in excluidos.itertuples()
        ],
    })
    return resultado


def indicadores_por_publico(mes):
    """Totais e taxas por público em um mês, do maior volume para o menor."""
    erro = conferir_mes(mes)
    if erro:
        return {"erro": erro}
    tabela = consultar(
        """
        SELECT publico, COUNT(*) AS disparos, SUM(enviadas) AS enviadas, SUM(entregues) AS entregues,
               SUM(aberturas_unicas) AS aberturas_unicas, SUM(cliques_unicos) AS cliques_unicos
        FROM disparos_email
        WHERE mes = ? AND enviadas >= ?
        GROUP BY publico
        ORDER BY enviadas DESC
        """,
        (mes, MINIMO_DE_ENVIOS),
    )
    linhas = []
    for linha in tabela.itertuples():
        linhas.append({
            "publico": linha.publico,
            "disparos": int(linha.disparos),
            "enviadas": int(linha.enviadas),
            "entregues": int(linha.entregues),
            "taxa_entrega": taxa(linha.entregues, linha.enviadas),
            "taxa_abertura": taxa(linha.aberturas_unicas, linha.entregues),
            "taxa_clique": taxa(linha.cliques_unicos, linha.entregues),
        })
    return {"mes": mes, "publicos": linhas}


def anomalias_de_clique(mes):
    """Disparos do mês com taxa de clique acima do limite. Eles continuam nos totais."""
    erro = conferir_mes(mes)
    if erro:
        return {"erro": erro}
    tabela = consultar(
        """
        SELECT disparo, entregues, cliques_unicos,
               ROUND(100.0 * cliques_unicos / entregues, 1) AS taxa_clique
        FROM disparos_email
        WHERE mes = ? AND enviadas >= ? AND 100.0 * cliques_unicos / entregues > ?
        ORDER BY taxa_clique DESC
        """,
        (mes, MINIMO_DE_ENVIOS, LIMITE_DE_CLIQUE),
    )
    return {"mes": mes, "limite": LIMITE_DE_CLIQUE, "disparos": tabela.to_dict(orient="records")}


def comparar_meses(mes_atual, mes_anterior):
    """Compara os indicadores gerais de dois meses. Diferenças de taxa em pontos percentuais."""
    atual, anterior = indicadores_email(mes_atual), indicadores_email(mes_anterior)
    for resultado in (atual, anterior):
        if "erro" in resultado:
            return resultado
    diferencas = {
        chave: round(atual[chave] - anterior[chave], 1)
        for chave in ("taxa_entrega", "taxa_abertura", "taxa_clique")
    }
    diferencas["variacao_enviadas_pct"] = round(100 * (atual["enviadas"] / anterior["enviadas"] - 1), 1)
    return {
        "mes_atual": mes_atual,
        "mes_anterior": mes_anterior,
        "atual": {chave: atual[chave] for chave in ("enviadas", "taxa_entrega", "taxa_abertura", "taxa_clique")},
        "anterior": {chave: anterior[chave] for chave in ("enviadas", "taxa_entrega", "taxa_abertura", "taxa_clique")},
        "diferencas_pp": diferencas,
    }


def entrega_whatsapp():
    """Entrega dos disparos de WhatsApp, por disparo, contada em contatos e não em tentativas."""
    tabela = consultar(
        """
        SELECT t.disparo, d.data_envio, d.tema,
               COUNT(DISTINCT t.telefone) AS contatos,
               COUNT(DISTINCT CASE WHEN t.status = 'entregue' THEN t.telefone END) AS receberam,
               SUM(CASE WHEN t.status = 'erro' THEN 1 ELSE 0 END) AS tentativas_com_erro
        FROM whatsapp_tentativas AS t
        JOIN disparos_whatsapp AS d ON d.disparo = t.disparo
        GROUP BY t.disparo, d.data_envio, d.tema
        ORDER BY t.disparo
        """
    )
    disparos = []
    for linha in tabela.itertuples():
        disparos.append({
            "disparo": linha.disparo,
            "data_envio": linha.data_envio,
            "tema": linha.tema,
            "contatos": int(linha.contatos),
            "receberam": int(linha.receberam),
            "nao_receberam": int(linha.contatos - linha.receberam),
            "taxa_entrega": taxa(linha.receberam, linha.contatos),
            "tentativas_com_erro": int(linha.tentativas_com_erro),
        })
    return {"disparos": disparos}


def _registros_da_feira():
    """Junta as três bases da feira e resolve a identidade das pessoas (método do módulo P.7)."""
    with conectar() as conexao:
        bases = {
            "credenciados": pd.read_sql_query("SELECT * FROM credenciados", conexao),
            "visitantes": pd.read_sql_query("SELECT * FROM visitantes", conexao),
            "inscritos": pd.read_sql_query("SELECT * FROM inscritos_evento", conexao),
        }
    partes = []
    for fonte, base in bases.items():
        base = base.fillna("").astype(str)
        base["fonte"] = fonte
        base["email"] = base["email"].map(v.padronizar_email)
        base["telefone"] = [v.padronizar_telefone(texto) or "" for texto in base["telefone"]]
        base["nome_chave"] = base["nome"].map(rc.chave_nome)
        partes.append(base)
    return rc.identificar_pessoas(pd.concat(partes, ignore_index=True))


def funil_feira():
    """Funil da feira em pessoas: credenciados, visitantes e participantes do evento."""
    registros = _registros_da_feira()
    credenciados = rc.pessoas_da_fonte(registros, "credenciados")
    visitantes = rc.pessoas_da_fonte(registros, "visitantes")
    inscritos = rc.pessoas_da_fonte(registros, "inscritos")
    com_check_in = set(
        registros.loc[(registros["fonte"] == "inscritos") & (registros["check_in"] == "S"), "pessoa"]
    )
    todos = credenciados | visitantes | inscritos
    visitaram = visitantes | com_check_in
    dias = registros[registros["fonte"] == "visitantes"].groupby("pessoa")["dia"].nunique()
    return {
        "credenciados": len(todos),
        "visitantes": len(visitaram),
        "taxa_visitacao": taxa(len(visitaram), len(todos)),
        "participantes_evento": len(com_check_in),
        "taxa_participacao_sobre_visitantes": taxa(len(com_check_in), len(visitaram)),
        "visitantes_fora_da_base_de_credenciados": len(visitantes - credenciados),
        "dias_por_visitante": round(float(dias.mean()), 2),
        "visitantes_por_dias_de_presenca": {str(chave): int(valor) for chave, valor in dias.value_counts().sort_index().items()},
    }


def whatsapp_e_visitacao():
    """Taxa de visitação de quem recebeu e de quem não recebeu ao menos uma mensagem de WhatsApp."""
    registros = _registros_da_feira()
    tentativas = consultar("SELECT telefone, status FROM whatsapp_tentativas")
    tentativas["telefone"] = [v.padronizar_telefone(texto) or "" for texto in tentativas["telefone"]]
    receberam = set(tentativas.loc[tentativas["status"] == "entregue", "telefone"])
    com_check_in = set(
        registros.loc[(registros["fonte"] == "inscritos") & (registros["check_in"] == "S"), "pessoa"]
    )
    visitaram = rc.pessoas_da_fonte(registros, "visitantes") | com_check_in
    registros["recebeu"] = registros["telefone"].isin(receberam)
    por_pessoa = registros.groupby("pessoa", as_index=False)["recebeu"].max()
    por_pessoa["visitou"] = por_pessoa["pessoa"].isin(visitaram)
    grupos = {}
    for recebeu, grupo in por_pessoa.groupby("recebeu"):
        chave = "recebeu" if recebeu else "nao_recebeu"
        grupos[chave] = {
            "pessoas": int(len(grupo)),
            "visitaram": int(grupo["visitou"].sum()),
            "taxa_visitacao": taxa(int(grupo["visitou"].sum()), len(grupo)),
        }
    grupos["observacao"] = (
        "Comparação entre grupos que não foram sorteados: a diferença não mede o efeito do WhatsApp."
    )
    return grupos

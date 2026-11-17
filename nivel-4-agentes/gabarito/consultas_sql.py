"""Gabarito das oito consultas SQL do exercício do módulo 4.3.

Executado e testado. Tente escrever as suas antes de ler.

Uso:
    python consultas_sql.py dados_n4/campanha.db
"""

import sqlite3
import sys

import pandas as pd

CONSULTAS = {
    "1. Disparos de setembro com 10 envios ou mais": """
        SELECT COUNT(*) AS disparos
        FROM disparos_email
        WHERE mes = '2026-09' AND enviadas >= 10
    """,
    "2. Envios de outubro por público, do maior para o menor": """
        SELECT publico, SUM(enviadas) AS enviadas
        FROM disparos_email
        WHERE mes = '2026-10' AND enviadas >= 10
        GROUP BY publico
        ORDER BY enviadas DESC
    """,
    "3. Taxa de descadastro por mês, com duas casas": """
        SELECT mes, ROUND(100.0 * SUM(descadastros) / SUM(entregues), 2) AS taxa_descadastro
        FROM disparos_email
        WHERE enviadas >= 10
        GROUP BY mes
        ORDER BY mes
    """,
    "4. Público com maior clique em outubro, entre os de 1.000 entregues ou mais": """
        SELECT publico, SUM(entregues) AS entregues,
               ROUND(100.0 * SUM(cliques_unicos) / SUM(entregues), 1) AS taxa_clique
        FROM disparos_email
        WHERE mes = '2026-10' AND enviadas >= 10
        GROUP BY publico
        HAVING SUM(entregues) >= 1000
        ORDER BY taxa_clique DESC
        LIMIT 1
    """,
    "5. Tentativas de WhatsApp com erro, por disparo e tema": """
        SELECT d.disparo, d.tema, SUM(CASE WHEN t.status = 'erro' THEN 1 ELSE 0 END) AS tentativas_com_erro
        FROM whatsapp_tentativas AS t
        JOIN disparos_whatsapp AS d ON d.disparo = t.disparo
        GROUP BY d.disparo, d.tema
        ORDER BY d.disparo
    """,
    "6. Contatos que receberam o disparo D2": """
        SELECT COUNT(DISTINCT telefone) AS receberam
        FROM whatsapp_tentativas
        WHERE disparo = 'D2' AND status = 'entregue'
    """,
    "7. Os três disparos de e-mail com maior taxa de clique nos dois meses": """
        SELECT disparo, ROUND(100.0 * cliques_unicos / entregues, 1) AS taxa_clique
        FROM disparos_email
        WHERE enviadas >= 10
        ORDER BY taxa_clique DESC
        LIMIT 3
    """,
    "8. Registros de visitação por dia da feira": """
        SELECT dia, COUNT(*) AS registros
        FROM visitantes
        GROUP BY dia
        ORDER BY dia
    """,
}


def rodar(caminho_banco):
    """Roda as oito consultas e devolve um dicionário título -> DataFrame."""
    with sqlite3.connect(f"file:{caminho_banco}?mode=ro", uri=True) as conexao:
        return {titulo: pd.read_sql_query(sql, conexao) for titulo, sql in CONSULTAS.items()}


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "dados_n4/campanha.db"
    for titulo, tabela in rodar(caminho).items():
        print(f"\n{titulo}\n{tabela.to_string(index=False)}")

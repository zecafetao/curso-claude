"""Trata uma base bruta e usa o Claude para classificar a área de cada cargo.

Solução de referência do projeto do Nível 3. As chamadas à API não foram executadas com uma
chave real. O restante (tratamento, retomada, arquivos de saída e custo) foi executado e testado.

Divisão de trabalho:
- O código do projeto da Ponte (tratar_base.py) padroniza os campos e rejeita as linhas inválidas.
- O Claude classifica só os cargos distintos das linhas aprovadas. Nenhum nome, e-mail ou
  telefone é enviado à API: saem do computador apenas os textos dos cargos.

Uso:
    python tratar_base_claude.py base_bruta.csv descadastrados.xlsx pasta_de_saida

A base pode ser .csv ou .xlsx. Se a execução for interrompida, rode o mesmo comando de novo.
"""

import json
import sys
from pathlib import Path

import anthropic
import pandas as pd

import claude_util as cu
import retomada
import tratar_base as tb
import validacao as v

MODELO = cu.MODELO
TETO_DE_CUSTO = 2.00          # em dólares, por pasta de saída
ARQ_DEFINICAO = Path("dados_n3/definicao_areas.md")
AREAS = ["Compras", "Produção", "Marketing", "Comercial", "Diretoria", "Outros"]

FORMATO_AREA = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {"area": {"type": "string", "enum": AREAS}},
        "required": ["area"],
        "additionalProperties": False,
    },
}

INSTRUCOES = """Você classifica cargos de contatos de um CRM em áreas, seguindo a definição em <definicao>.
Cada mensagem traz um cargo, como o contato informou. Devolva a área.

<definicao>
{definicao}
</definicao>

Os exemplos abaixo ilustram a aplicação das regras. Os casos reais variam.

<exemplos>
Diretor de Suprimentos -> Diretoria (o nível de direção vem antes da função)
Head de Trade Marketing -> Marketing (heads ficam na área em que atuam)
Químico - Representante Técnico-Comercial -> Comercial (vale a função, não a formação)
Plant Manager -> Produção (cargo em inglês: gerente de fábrica)
Analista Contábil -> Outros
Consultor -> Outros (o cargo não permite identificar a função)
</exemplos>"""


def ler_base(caminho):
    """Lê a base bruta em CSV ou Excel, com tudo como texto, no formato que o tratamento espera."""
    if str(caminho).lower().endswith(".xlsx"):
        base = pd.read_excel(caminho, dtype=str, keep_default_na=False)
        faltando = [coluna for coluna in tb.RENOMEAR if coluna not in base.columns]
        if faltando:
            raise ValueError(f"Colunas ausentes na base: {faltando}")
        base = base.rename(columns=tb.RENOMEAR)
        base["linha"] = base.index + 2
        return base
    return tb.ler_base(caminho)


def montar_sistema():
    """Instruções de sistema com a definição das áreas e a marca de cache no fim."""
    definicao = ARQ_DEFINICAO.read_text(encoding="utf-8").strip()
    return [{"type": "text", "text": INSTRUCOES.format(definicao=definicao), "cache_control": {"type": "ephemeral"}}]


def processar_com(cliente, sistema):
    """Devolve a função que classifica um cargo, no formato que a retomada espera."""
    def processar(cargo):
        resposta = cu.chamar(
            cliente, [{"role": "user", "content": f"Cargo: {cargo}"}], sistema=sistema, modelo=MODELO,
            max_tokens=4000, esforco="low", formato=FORMATO_AREA,
        )
        registro = {"custo": cu.custo_em_dolares(resposta.usage, MODELO), "uso": {
            "entrada": resposta.usage.input_tokens,
            "escrita_cache": resposta.usage.cache_creation_input_tokens or 0,
            "leitura_cache": resposta.usage.cache_read_input_tokens or 0,
            "saida": resposta.usage.output_tokens,
        }}
        if resposta.stop_reason == "refusal":
            return {"situacao": "recusado", **registro}
        if resposta.stop_reason != "end_turn":
            return {"situacao": "erro", "detalhe": f"resposta incompleta ({resposta.stop_reason})", **registro}
        area = json.loads(cu.texto_da_resposta(resposta))["area"]
        return {"situacao": "ok", "resultado": {"area": area}, **registro}
    return processar


def montar_decisoes(importar, registros):
    """Uma linha por cargo distinto: área pela regra, área pelo Claude e a área que vale."""
    contagem = importar["cargo"].value_counts()
    linhas = []
    for cargo in sorted(contagem.index):
        area_regra = v.area_do_cargo(cargo)
        registro = registros.get(cargo, {})
        if cargo == "":
            area_claude, area_final, fonte = "", "Outros", "cargo vazio"
        elif registro.get("situacao") == "ok":
            area_claude = registro["resultado"]["area"]
            area_final, fonte = area_claude, "Claude"
        else:                                         # sem resposta utilizável: vale a regra de palavras-chave
            area_claude, area_final = "", area_regra
            fonte = f"regra ({registro.get('situacao', 'pendente')})"
        linhas.append({"cargo": cargo, "contatos": int(contagem[cargo]), "area_regra": area_regra,
                       "area_claude": area_claude, "area_final": area_final, "fonte": fonte})
    return pd.DataFrame(linhas)


def texto_do_custo(registros, linhas_importadas):
    """Soma o consumo registrado no arquivo de progresso, de todas as execuções."""
    soma = {"entrada": 0, "escrita_cache": 0, "leitura_cache": 0, "saida": 0}
    chamadas, custo = 0, 0.0
    for registro in registros.values():
        if "uso" in registro:
            chamadas += 1
            custo += registro.get("custo", 0.0)
            for chave in soma:
                soma[chave] += registro["uso"][chave]
    return "\n".join([
        f"Modelo: {MODELO}",
        f"Cargos classificados pelo Claude: {chamadas}",
        f"Tokens de entrada: {soma['entrada']}",
        f"Tokens gravados no cache: {soma['escrita_cache']}",
        f"Tokens lidos do cache: {soma['leitura_cache']}",
        f"Tokens de saída: {soma['saida']}",
        f"Custo total: US$ {custo:.4f}",
        f"Custo por contato importado: US$ {custo / max(linhas_importadas, 1):.6f}",
        f"Custo por mil contatos importados: US$ {custo / max(linhas_importadas, 1) * 1000:.4f}",
    ])


def tratar(caminho_base, caminho_descadastrados, pasta_saida, cliente):
    """Executa o tratamento completo e grava os arquivos de saída. Devolve o resumo."""
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    # 1. Tratamento determinístico: o mesmo do projeto da Ponte.
    base = tb.padronizar(ler_base(caminho_base))
    base = tb.classificar(base, tb.ler_descadastrados(caminho_descadastrados))
    importar = base[base["motivo"] == ""].copy()
    rejeitados = base[base["motivo"] != ""]
    avisos = tb.montar_avisos(importar)

    # 2. O Claude classifica os cargos distintos das linhas aprovadas, com retomada.
    cargos = sorted(cargo for cargo in importar["cargo"].unique() if cargo != "")
    arq_progresso = pasta_saida / "progresso_cargos.jsonl"
    resumo_claude = retomada.processar_com_retomada(
        [(cargo, cargo) for cargo in cargos], processar_com(cliente, montar_sistema()), arq_progresso,
        teto_de_custo=TETO_DE_CUSTO,
    )
    registros, _ = retomada.ler_progresso(arq_progresso)

    # 3. A área de cada linha passa a ser a decisão registrada para o cargo dela.
    decisoes = montar_decisoes(importar, registros)
    importar["area"] = importar["cargo"].map(dict(zip(decisoes["cargo"], decisoes["area_final"])))
    revisar = decisoes[(decisoes["area_regra"] != decisoes["area_final"]) | (decisoes["fonte"] != "Claude")]
    revisar = revisar.sort_values("contatos", ascending=False)

    # 4. Arquivos de saída.
    opcoes = dict(sep=";", index=False, encoding="utf-8")
    importar[tb.LAYOUT].to_csv(pasta_saida / "importar.csv", **opcoes)
    rejeitados[["linha", "email_bruto", "motivo"]].to_csv(pasta_saida / "rejeitados.csv", **opcoes)
    avisos.to_csv(pasta_saida / "avisos.csv", **opcoes)
    decisoes.to_csv(pasta_saida / "decisoes_cargos.csv", **opcoes)
    revisar.to_csv(pasta_saida / "revisar_areas.csv", **opcoes)
    (pasta_saida / "custo.txt").write_text(texto_do_custo(registros, len(importar)) + "\n", encoding="utf-8")

    linhas = [
        f"Linhas lidas: {len(base)}",
        f"Linhas para importar: {len(importar)}",
        f"Linhas rejeitadas: {len(rejeitados)}",
    ]
    for motivo, quantidade in rejeitados["motivo"].value_counts().sort_index().items():
        linhas.append(f"  {motivo}: {quantidade}")
    linhas.append(f"Avisos: {len(avisos)}")
    linhas.append(f"Cargos distintos: {len(cargos)}")
    linhas.append(f"Classificação pelo Claude: {retomada.texto_do_resumo(resumo_claude)}")
    linhas.append(f"Cargos em que a área mudou em relação à regra ou ficou sem resposta: {len(revisar)}")
    resumo = "\n".join(linhas)
    (pasta_saida / "resumo.txt").write_text(resumo + "\n", encoding="utf-8")
    return resumo


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python tratar_base_claude.py base_bruta.csv descadastrados.xlsx pasta_de_saida")
        sys.exit(1)
    try:
        print(tratar(sys.argv[1], sys.argv[2], sys.argv[3], cu.criar_cliente()))
    except anthropic.AuthenticationError:
        print("Chave de API inválida ou ausente. Confira a variável ANTHROPIC_API_KEY.")
        sys.exit(1)

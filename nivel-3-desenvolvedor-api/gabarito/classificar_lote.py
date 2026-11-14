"""Classifica mil contatos em segmentos pelo menor custo: pares distintos, cache e lote.

Solução de referência do módulo 3.5. As chamadas à API não foram executadas com uma chave real.
As funções que não chamam a API (pares distintos, projeção de custo, montagem da saída e medição
de acerto) foram executadas e têm testes em test_nivel3.py.

Uso:
    python classificar_lote.py contar        # conta os tokens de uma requisição, sem gerar resposta
    python classificar_lote.py amostra 20    # classifica 20 pares, um a um; mede acerto, tokens e custo
    python classificar_lote.py criar         # envia o lote com todos os pares distintos
    python classificar_lote.py situacao      # mostra o andamento do lote
    python classificar_lote.py coletar       # baixa os resultados, mede o acerto e calcula o custo
"""

import csv
import json
import sys
from pathlib import Path

from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

import claude_util as cu

MODELO = cu.MODELO          # troque aqui para comparar modelos, por exemplo "claude-haiku-5-5"
ESFORCO = "low"
MAX_TOKENS = 4000

PASTA = Path("dados_n3")
ARQ_CONTATOS = PASTA / "contatos_1000.csv"
ARQ_GABARITO = PASTA / "contatos_1000_gabarito.csv"
ARQ_REGRAS = PASTA / "regras_segmentos.md"
ARQ_LOTE = Path("lote_id.txt")              # identificador do lote enviado
ARQ_PARES = Path("lote_pares.csv")          # o que foi enviado em cada requisição do lote
ARQ_SAIDA = Path("contatos_1000_classificados.csv")

SEGMENTOS = ["Compras", "Tecnico", "Marketing", "Diretoria", "ForaDoPerfil"]
FORMATO = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "segmento": {"type": "string", "enum": SEGMENTOS},
            "regra": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6]},
        },
        "required": ["segmento", "regra"],
        "additionalProperties": False,
    },
}

INSTRUCOES = """Você classifica contatos de uma base de visitação de feira em segmentos, seguindo as regras em <regras>.
Cada mensagem traz o cargo e o setor de um contato. Devolva o segmento e o número da regra aplicada.
Os cargos podem vir abreviados ou em inglês: classifique pelo significado do cargo.

<regras>
{regras}
</regras>

Os exemplos abaixo ilustram a ordem de precedência das regras. Os casos reais variam.

<exemplos>
Cargo: Diretora de Marketing | Setor: Bebidas -> Diretoria, regra 2 (a regra 2 vem antes da 5)
Cargo: Purchasing Manager | Setor: Cosméticos -> Compras, regra 3
Cargo: Gerente de Suprimentos | Setor: Transportes -> ForaDoPerfil, regra 1 (o setor decide antes do cargo)
Cargo: Eng. de Processos | Setor: Pet -> Tecnico, regra 4
Cargo: Trade Marketing Specialist | Setor: Higiene e limpeza -> Marketing, regra 5
Cargo: Auxiliar de Contabilidade | Setor: Alimentos -> ForaDoPerfil, regra 6
</exemplos>"""


# ---------- Funções que não chamam a API ----------

def ler_csv(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo, delimiter=";"))


def gravar_csv(caminho, colunas, linhas):
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas, delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas)


def pares_distintos(contatos):
    """Devolve a lista ordenada dos pares (cargo, setor) que aparecem na base, sem repetição."""
    return sorted({(contato["cargo"], contato["setor"]) for contato in contatos})


def montar_sistema(validade=None):
    """Monta as instruções de sistema, com a marca de cache no fim da parte que não muda.

    validade: None para o padrão de 5 minutos, ou "1h" para uma hora (indicado em lotes).
    """
    regras = ARQ_REGRAS.read_text(encoding="utf-8").strip()
    marca = {"type": "ephemeral"}
    if validade is not None:
        marca["ttl"] = validade
    return [{"type": "text", "text": INSTRUCOES.format(regras=regras), "cache_control": marca}]


def mensagem_do_par(cargo, setor):
    """A parte que muda a cada requisição: só o cargo e o setor."""
    return [{"role": "user", "content": f"Cargo: {cargo}\nSetor: {setor}"}]


def interpretar(resposta):
    """Devolve {"segmento": ..., "regra": ...} ou None se a resposta não puder ser usada."""
    if resposta.stop_reason != "end_turn":           # recusa, corte por limite de tokens etc.
        return None
    texto = "".join(bloco.text for bloco in resposta.content if bloco.type == "text")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError:
        return None
    if dados.get("segmento") not in SEGMENTOS:
        return None
    return {"segmento": dados["segmento"], "regra": dados.get("regra")}


def projetar(prefixo, sufixo, saida, linhas, pares, modelo=MODELO):
    """Projeta o custo, em dólares, de cinco formas de processar a base.

    Tokens por requisição: prefixo (a parte fixa: instruções e regras), sufixo (a parte que
    muda: cargo e setor) e saida (tudo o que o modelo gera, raciocínio incluído).
    """
    preco = cu.PRECOS[modelo]
    milhao = 1_000_000
    por_resposta = (sufixo * preco["entrada"] + saida * preco["saida"]) / milhao
    prefixo_cheio = prefixo * preco["entrada"] / milhao
    prefixo_lido = prefixo * preco["leitura_cache"] / milhao

    uma_por_linha = linhas * (prefixo_cheio + por_resposta)
    so_pares = pares * (prefixo_cheio + por_resposta)
    com_cache = prefixo_cheio * cu.FATOR_ESCRITA_5MIN + (pares - 1) * prefixo_lido + pares * por_resposta
    lote_sem_cache = so_pares * cu.DESCONTO_LOTE
    lote_com_cache = cu.DESCONTO_LOTE * (
        prefixo_cheio * cu.FATOR_ESCRITA_1H + (pares - 1) * prefixo_lido + pares * por_resposta
    )
    return [
        ("Uma chamada por linha, sem cache", uma_por_linha),
        ("Uma chamada por par distinto, sem cache", so_pares),
        ("Pares distintos, com cache", com_cache),
        ("Pares distintos, em lote, se nenhuma leitura de cache acontecer", lote_sem_cache),
        ("Pares distintos, em lote, se todas as leituras de cache acontecerem", lote_com_cache),
    ]


def mostrar_projecao(prefixo, sufixo, saida, linhas, pares, modelo=MODELO):
    print(f"Projeção para {linhas} linhas e {pares} pares distintos ({modelo}):")
    for descricao, custo in projetar(prefixo, sufixo, saida, linhas, pares, modelo):
        print(f"  {descricao}: US$ {custo:.4f} (US$ {custo / linhas * 1000:.4f} por mil contatos)")


def montar_saida(contatos, resultado_por_par):
    """Leva a classificação de cada par para todas as linhas que têm aquele par."""
    linhas = []
    for contato in contatos:
        resultado = resultado_por_par.get((contato["cargo"], contato["setor"]))
        linhas.append({
            "id": contato["id"],
            "cargo": contato["cargo"],
            "setor": contato["setor"],
            "segmento": resultado["segmento"] if resultado else "",
            "regra": resultado["regra"] if resultado else "",
            "situacao": "ok" if resultado else "sem resultado",
        })
    return linhas


def medir_acerto(linhas, gabarito):
    """Compara com o gabarito. Devolve (acertos, total, lista de erros)."""
    certo = {item["id"]: item["segmento"] for item in gabarito}
    acertos, erros = 0, []
    for linha in linhas:
        if linha["segmento"] == certo[linha["id"]]:
            acertos += 1
        else:
            erros.append((linha["cargo"], linha["setor"], linha["segmento"] or "(sem resultado)", certo[linha["id"]]))
    return acertos, len(linhas), erros


def mostrar_acerto(linhas, gabarito):
    acertos, total, erros = medir_acerto(linhas, gabarito)
    print(f"Acerto: {acertos} de {total} ({acertos / total:.1%})")
    contagem = {}
    for erro in erros:
        contagem[erro] = contagem.get(erro, 0) + 1
    for (cargo, setor, obtido, esperado), vezes in sorted(contagem.items(), key=lambda item: -item[1]):
        print(f"  {vezes}x {cargo} | {setor}: veio {obtido}, esperado {esperado}")


# ---------- Funções que chamam a API ----------

def classificar_par(cliente, sistema, cargo, setor):
    """Classifica um par em uma chamada comum. Devolve (resultado ou None, resposta)."""
    resposta = cu.chamar(
        cliente, mensagem_do_par(cargo, setor), sistema=sistema, modelo=MODELO,
        max_tokens=MAX_TOKENS, esforco=ESFORCO, formato=FORMATO,
    )
    return interpretar(resposta), resposta


def contar(cliente):
    """Conta os tokens de entrada de uma requisição. A contagem não gera resposta."""
    contatos = ler_csv(ARQ_CONTATOS)
    pares = pares_distintos(contatos)
    mensagem = mensagem_do_par(*pares[0])
    com_sistema = cliente.messages.count_tokens(model=MODELO, system=montar_sistema(), messages=mensagem)
    sem_sistema = cliente.messages.count_tokens(model=MODELO, messages=mensagem)
    prefixo = com_sistema.input_tokens - sem_sistema.input_tokens
    print(f"Linhas: {len(contatos)} | pares distintos: {len(pares)}")
    print(f"Tokens da parte fixa (instruções e regras): {prefixo}")
    print(f"Tokens da parte que muda (cargo e setor): {sem_sistema.input_tokens}")
    if prefixo < 512:
        print("Atenção: a parte fixa tem menos de 512 tokens e não entra no cache.")


def amostra(cliente, quantidade):
    """Classifica alguns pares, um a um, para medir acerto, tokens e custo antes do lote."""
    contatos = ler_csv(ARQ_CONTATOS)
    pares = pares_distintos(contatos)
    passo = max(1, len(pares) // quantidade)
    escolhidos = pares[::passo][:quantidade]
    sistema = montar_sistema()
    total = cu.novo_total()
    resultado_por_par = {}
    for cargo, setor in escolhidos:
        resultado, resposta = classificar_par(cliente, sistema, cargo, setor)
        cu.somar_uso(total, resposta.usage, MODELO)
        resultado_por_par[(cargo, setor)] = resultado
    print(cu.resumo_do_total(total))

    da_amostra = [contato for contato in contatos if (contato["cargo"], contato["setor"]) in resultado_por_par]
    mostrar_acerto(montar_saida(da_amostra, resultado_por_par), ler_csv(ARQ_GABARITO))

    chamadas = total["chamadas"]
    prefixo = (total["escrita_cache"] + total["leitura_cache"]) // chamadas
    if prefixo == 0:
        print("O cache não foi usado: confira se a parte fixa tem ao menos 512 tokens.")
        return
    mostrar_projecao(prefixo, total["entrada"] // chamadas, total["saida"] // chamadas, len(contatos), len(pares))


def criar(cliente):
    """Envia um lote com uma requisição por par distinto e guarda o identificador."""
    pares = pares_distintos(ler_csv(ARQ_CONTATOS))
    sistema = montar_sistema(validade="1h")
    enviados, requisicoes = [], []
    for numero, (cargo, setor) in enumerate(pares, start=1):
        identificador = f"par-{numero:04d}"
        enviados.append({"custom_id": identificador, "cargo": cargo, "setor": setor})
        requisicoes.append(Request(
            custom_id=identificador,
            params=MessageCreateParamsNonStreaming(
                model=MODELO,
                max_tokens=MAX_TOKENS,
                system=sistema,
                messages=mensagem_do_par(cargo, setor),
                output_config={"effort": ESFORCO, "format": FORMATO},
            ),
        ))
    lote = cliente.messages.batches.create(requests=requisicoes)
    ARQ_LOTE.write_text(lote.id, encoding="utf-8")
    gravar_csv(ARQ_PARES, ["custom_id", "cargo", "setor"], enviados)
    print(f"Lote {lote.id} criado com {len(requisicoes)} requisições. Situação: {lote.processing_status}")


def situacao(cliente):
    """Mostra o andamento do lote."""
    lote = cliente.messages.batches.retrieve(ARQ_LOTE.read_text(encoding="utf-8").strip())
    contagem = lote.request_counts
    print(f"Lote {lote.id}: {lote.processing_status}")
    print(f"  em processamento {contagem.processing} | concluídas {contagem.succeeded} | "
          f"com erro {contagem.errored} | canceladas {contagem.canceled} | expiradas {contagem.expired}")
    return lote


def coletar(cliente):
    """Baixa os resultados do lote, repesca o que faltou, grava a saída e mede acerto e custo."""
    lote = situacao(cliente)
    if lote.processing_status != "ended":
        print("O lote ainda não terminou. Rode este comando de novo mais tarde.")
        return
    par_por_id = {item["custom_id"]: (item["cargo"], item["setor"]) for item in ler_csv(ARQ_PARES)}

    total = cu.novo_total()
    resultado_por_par = {}
    for item in cliente.messages.batches.results(lote.id):       # a ordem não é garantida: use o custom_id
        if item.result.type == "succeeded":
            mensagem = item.result.message
            cu.somar_uso(total, mensagem.usage, MODELO, lote=True)
            resultado_por_par[par_por_id[item.custom_id]] = interpretar(mensagem)
    print(f"Lote: {cu.resumo_do_total(total)}")

    # Repescagem: o que veio com erro, expirou ou não pôde ser lido é refeito em chamadas comuns.
    faltando = [par for par in par_por_id.values() if resultado_por_par.get(par) is None]
    if faltando:
        sistema = montar_sistema()
        repescagem = cu.novo_total()
        for cargo, setor in faltando:
            resultado, resposta = classificar_par(cliente, sistema, cargo, setor)
            cu.somar_uso(repescagem, resposta.usage, MODELO)
            resultado_por_par[(cargo, setor)] = resultado
        print(f"Repescagem de {len(faltando)} pares: {cu.resumo_do_total(repescagem)}")
        total["custo"] += repescagem["custo"]

    contatos = ler_csv(ARQ_CONTATOS)
    linhas = montar_saida(contatos, resultado_por_par)
    gravar_csv(ARQ_SAIDA, ["id", "cargo", "setor", "segmento", "regra", "situacao"], linhas)
    sem_resultado = sum(1 for linha in linhas if linha["situacao"] != "ok")
    print(f"Arquivo gravado: {ARQ_SAIDA} ({len(linhas)} linhas, {sem_resultado} sem resultado)")
    mostrar_acerto(linhas, ler_csv(ARQ_GABARITO))
    print(f"Custo total: US$ {total['custo']:.4f} | por mil contatos: US$ {total['custo'] / len(contatos) * 1000:.4f}")


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else ""
    if comando not in ("contar", "amostra", "criar", "situacao", "coletar"):
        print("Uso: python classificar_lote.py contar | amostra 20 | criar | situacao | coletar")
        sys.exit(1)
    cliente = cu.criar_cliente()
    if comando == "contar":
        contar(cliente)
    elif comando == "amostra":
        amostra(cliente, int(sys.argv[2]) if len(sys.argv) > 2 else 20)
    elif comando == "criar":
        criar(cliente)
    elif comando == "situacao":
        situacao(cliente)
    else:
        coletar(cliente)

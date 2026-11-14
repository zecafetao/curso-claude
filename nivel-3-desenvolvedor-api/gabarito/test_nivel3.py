"""Testes das partes do Nível 3 que não chamam a API. Não gastam créditos.

Rode na pasta dos seus scripts, com a pasta dados_n3 ao lado:
    pytest test_nivel3.py
"""

import json
from types import SimpleNamespace

import pytest

import avaliar_extracao
import classificar_lote
import claude_util as cu
import ferramentas
import retomada


def uso(entrada=0, saida=0, escrita=0, leitura=0, escrita_1h=None):
    """Monta um objeto com os mesmos campos do usage de uma resposta."""
    detalhe = None
    if escrita_1h is not None:
        detalhe = SimpleNamespace(ephemeral_1h_input_tokens=escrita_1h, ephemeral_5m_input_tokens=escrita - escrita_1h)
    return SimpleNamespace(input_tokens=entrada, output_tokens=saida, cache_creation_input_tokens=escrita,
                           cache_read_input_tokens=leitura, cache_creation=detalhe)


def resposta(texto, stop_reason="end_turn"):
    """Monta um objeto com os campos de uma resposta que os scripts leem."""
    return SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=texto)])


# ---------- claude_util ----------

def test_custo_de_entrada_e_saida():
    # 1 milhão de tokens de entrada e 1 milhão de saída no Opus 5.5: 4 + 20 dólares
    assert cu.custo_em_dolares(uso(entrada=1_000_000, saida=1_000_000)) == pytest.approx(24.0)


def test_custo_com_cache():
    # escrita de 5 minutos: 1,25 x 4 = 5 dólares por milhão; leitura: 0,20 por milhão
    assert cu.custo_em_dolares(uso(escrita=1_000_000)) == pytest.approx(5.0)
    assert cu.custo_em_dolares(uso(leitura=1_000_000)) == pytest.approx(0.20)


def test_custo_com_cache_de_uma_hora():
    # escrita de 1 hora: 2 x 4 = 8 dólares por milhão
    assert cu.custo_em_dolares(uso(escrita=1_000_000, escrita_1h=1_000_000)) == pytest.approx(8.0)


def test_custo_em_lote_e_a_metade():
    comum = cu.custo_em_dolares(uso(entrada=1000, saida=500))
    assert cu.custo_em_dolares(uso(entrada=1000, saida=500), lote=True) == pytest.approx(comum / 2)


def test_custo_por_modelo():
    assert cu.custo_em_dolares(uso(entrada=1_000_000), "claude-haiku-5-5") == pytest.approx(0.10)
    assert cu.custo_em_dolares(uso(saida=1_000_000), "claude-sonnet-5-5") == pytest.approx(10.0)


def test_total_acumula():
    total = cu.novo_total()
    cu.somar_uso(total, uso(entrada=100, saida=50))
    cu.somar_uso(total, uso(entrada=10, saida=5, leitura=700))
    assert total["chamadas"] == 2 and total["entrada"] == 110 and total["leitura_cache"] == 700


def test_texto_da_resposta():
    assert cu.texto_da_resposta(resposta("olá")) == "olá"
    assert cu.texto_da_resposta(resposta("", stop_reason="refusal")) is None


# ---------- ferramentas (módulo 3.4) ----------

def test_resumir_base_por_area():
    resultado = ferramentas.resumir_base("area")
    assert resultado["total_de_contatos"] == 87
    assert resultado["contagem"]["Compras"] == 18


def test_resumir_base_recusa_coluna_com_dado_pessoal():
    assert "erro" in ferramentas.resumir_base("email")


def test_contar_contatos_combina_filtros():
    assert ferramentas.contar_contatos(area="Compras", uf="sp", consentimento="s")["quantidade"] == 2
    assert ferramentas.contar_contatos()["quantidade"] == 87


def test_contar_contatos_avisa_valor_fora_da_lista():
    assert "erro" in ferramentas.contar_contatos(area="Vendas")      # sem o aviso, viria zero
    assert "erro" in ferramentas.contar_contatos(consentimento="sim")


def test_validar_arquivo_com_erros():
    resultado = ferramentas.validar_arquivo("arquivo_com_erros.csv")
    assert resultado["linhas"] == 87 and resultado["linhas_com_problema"] == 10
    assert resultado["problemas"] == {
        "e-mail inválido": 2, "e-mail repetido": 2, "telefone fora do formato": 2,
        "área fora da lista": 2, "origem fora da lista": 1, "consentimento S sem data": 2,
    }


def test_validar_arquivo_sem_erros():
    assert ferramentas.validar_arquivo("base_contatos_tratada.csv")["linhas_com_problema"] == 0


def test_validar_arquivo_nao_sai_da_pasta():
    assert "erro" in ferramentas.validar_arquivo("../segredos.csv")
    assert "erro" in ferramentas.validar_arquivo("nao_existe.csv")
    assert "erro" in ferramentas.validar_arquivo("contatos_1000.csv")      # existe, mas não é do layout


# ---------- avaliar_extracao (módulo 3.3) ----------

def test_avaliar_padroniza_antes_de_comparar():
    gabarito = {"C01": {"id": "C01", "nome": "Ana", "sobrenome": "Almeida", "email": "ana@alfa.example",
                        "telefone": "+5511999900001", "empresa": "Alimentos Alfa", "cargo": "Compradora"}}
    extraido = {"C01": {"id": "C01", "situacao": "ok", "nome": "ANA", "sobrenome": "almeida",
                        "email": "Ana@Alfa.example", "telefone": "(11) 99990-0001",
                        "empresa": "Alimentos Alfa Ltda", "cargo": "compradora"}}
    acertos, erros, sem_resultado = avaliar_extracao.avaliar(extraido, gabarito)
    assert erros == [] and sem_resultado == 0 and all(valor == 1 for valor in acertos.values())


def test_avaliar_conta_registro_sem_resultado():
    gabarito = {"C01": {"id": "C01", "nome": "Ana", "sobrenome": "", "email": "", "telefone": "", "empresa": "", "cargo": ""}}
    _, _, sem_resultado = avaliar_extracao.avaliar({"C01": {"id": "C01", "situacao": "refusal"}}, gabarito)
    assert sem_resultado == 1


# ---------- classificar_lote (módulo 3.5) ----------

def test_pares_distintos():
    contatos = classificar_lote.ler_csv(classificar_lote.ARQ_CONTATOS)
    assert len(contatos) == 1000
    assert len(classificar_lote.pares_distintos(contatos)) == 338


def test_interpretar():
    assert classificar_lote.interpretar(resposta('{"segmento": "Compras", "regra": 3}')) == {"segmento": "Compras", "regra": 3}
    assert classificar_lote.interpretar(resposta('{"segmento": "Compr', stop_reason="max_tokens")) is None
    assert classificar_lote.interpretar(resposta("", stop_reason="refusal")) is None
    assert classificar_lote.interpretar(resposta('{"segmento": "Vendas", "regra": 3}')) is None


def test_saida_tem_uma_linha_por_contato():
    contatos = [{"id": "K1", "cargo": "Buyer", "setor": "Pet"}, {"id": "K2", "cargo": "Buyer", "setor": "Pet"},
                {"id": "K3", "cargo": "CEO", "setor": "Banco"}]
    linhas = classificar_lote.montar_saida(contatos, {("Buyer", "Pet"): {"segmento": "Compras", "regra": 3}})
    assert [linha["situacao"] for linha in linhas] == ["ok", "ok", "sem resultado"]
    gabarito = [{"id": "K1", "segmento": "Compras"}, {"id": "K2", "segmento": "Compras"}, {"id": "K3", "segmento": "ForaDoPerfil"}]
    acertos, total, erros = classificar_lote.medir_acerto(linhas, gabarito)
    assert (acertos, total) == (2, 3) and erros[0][2] == "(sem resultado)"


def test_projecao_ordena_as_alternativas():
    custos = [custo for _, custo in classificar_lote.projetar(900, 30, 80, linhas=1000, pares=338, modelo="claude-opus-5-5")]
    uma_por_linha, so_pares, com_cache, lote_sem_cache, lote_com_cache = custos
    assert uma_por_linha > so_pares > com_cache > lote_com_cache
    assert lote_sem_cache == pytest.approx(so_pares / 2)
    # conta feita à mão: 1.000 x (900 x 4 + 30 x 4 + 80 x 20) / 1.000.000 = 5,32 dólares
    assert uma_por_linha == pytest.approx(5.32)


# ---------- retomada (módulo 3.6) ----------

class Temporario(Exception):
    pass


def rodar(itens, processar, caminho, **opcoes):
    return retomada.processar_com_retomada(
        itens, processar, caminho, temporarios=(Temporario,), dormir=lambda segundos: None,
        avisar=lambda texto: None, **opcoes,
    )


def test_retomada_nao_refaz_o_que_terminou(tmp_path):
    caminho = tmp_path / "progresso.jsonl"
    itens = [(f"I{numero}", numero) for numero in range(5)]
    chamados = []

    def processar(numero):
        chamados.append(numero)
        if numero == 3 and len(chamados) <= 4:
            raise KeyboardInterrupt                   # interrupção no quarto item, na primeira execução
        return {"situacao": "ok", "resultado": {"dobro": numero * 2}, "custo": 0.01}

    primeiro = rodar(itens, processar, caminho)
    assert primeiro["ok"] == 3 and primeiro["pendente"] == 2 and primeiro["parada"] == "interrompido"
    segundo = rodar(itens, processar, caminho)
    assert segundo["ok"] == 5 and segundo["pendente"] == 0
    assert chamados == [0, 1, 2, 3, 3, 4]             # os três primeiros não foram pagos duas vezes
    assert segundo["custo"] == pytest.approx(0.05)


def test_erro_temporario_e_tentado_de_novo(tmp_path):
    tentativas = []

    def processar(dados):
        tentativas.append(dados)
        if len(tentativas) < 3:
            raise Temporario("429")
        return {"situacao": "ok", "custo": 0.0}

    resumo = rodar([("A", "a")], processar, tmp_path / "p.jsonl")
    assert resumo["ok"] == 1 and len(tentativas) == 3


def test_erro_do_pedido_nao_e_repetido_e_nao_para_a_fila(tmp_path):
    def processar(dados):
        if dados == "ruim":
            raise ValueError("pedido inválido")
        return {"situacao": "ok", "custo": 0.0}

    resumo = rodar([("A", "ruim"), ("B", "bom")], processar, tmp_path / "p.jsonl")
    assert resumo["erro"] == 1 and resumo["ok"] == 1


def test_teto_de_custo_interrompe(tmp_path):
    itens = [(f"I{numero}", numero) for numero in range(10)]
    resumo = rodar(itens, lambda dados: {"situacao": "ok", "custo": 0.10}, tmp_path / "p.jsonl", teto_de_custo=0.30)
    assert resumo["ok"] == 3 and resumo["pendente"] == 7 and resumo["parada"] == "teto de custo"


def test_falhas_seguidas_interrompem(tmp_path):
    def processar(dados):
        raise Temporario("529")

    itens = [(f"I{numero}", numero) for numero in range(10)]
    resumo = rodar(itens, processar, tmp_path / "p.jsonl", max_tentativas=2, max_falhas_seguidas=3)
    assert resumo["erro"] == 3 and resumo["pendente"] == 7 and resumo["parada"] == "falhas seguidas"


def test_nenhum_item_se_perde(tmp_path):
    def processar(dados):
        if dados % 4 == 0:
            return {"situacao": "recusado", "custo": 0.0}
        if dados % 5 == 0:
            raise ValueError("erro")
        return {"situacao": "ok", "custo": 0.0}

    itens = [(f"I{numero}", numero) for numero in range(1, 21)]
    resumo = rodar(itens, processar, tmp_path / "p.jsonl")
    assert resumo["ok"] + resumo["recusado"] + resumo["erro"] + resumo["pendente"] == resumo["total"] == 20


def test_linha_cortada_no_progresso_e_ignorada(tmp_path):
    caminho = tmp_path / "p.jsonl"
    caminho.write_text(json.dumps({"id": "A", "situacao": "ok", "custo": 0.02}) + '\n{"id": "B", "situa', encoding="utf-8")
    registros, gasto = retomada.ler_progresso(caminho)
    assert list(registros) == ["A"] and gasto == pytest.approx(0.02)

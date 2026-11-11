"""Testes automatizados das funções de validacao.py.

Exemplo de referência do módulo P.5. Rode com:
    python -m pytest
"""

import pytest

import validacao as v


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        (" Ana.Souza@Alfa.Example ", "ana.souza@alfa.example"),
        ("JOAO@BETA.EXAMPLE", "joao@beta.example"),
    ],
)
def test_padronizar_email(entrada, esperado):
    assert v.padronizar_email(entrada) == esperado


@pytest.mark.parametrize(
    "email, esperado",
    [
        ("ana.souza@alfa.example", True),
        ("maria+feira@gama.example", True),
        ("ana.souza.alfa.example", False),   # sem arroba
        ("ana souza@alfa.example", False),   # espaço no meio
        ("joao@alfa", False),                # domínio sem ponto
        ("joao@@alfa.example", False),       # dois arrobas
        ("pedro@alfa.example,", False),      # vírgula no fim
        ("", False),
    ],
)
def test_email_valido(email, esperado):
    assert v.email_valido(email) == esperado


@pytest.mark.parametrize(
    "entrada",
    ["(11) 99990-0001", "11999900001", "+55 11 99990-0001", "5511999900001", "011999900001"],
)
def test_telefone_celular_em_varios_formatos(entrada):
    assert v.padronizar_telefone(entrada) == "+5511999900001"


def test_telefone_fixo():
    assert v.padronizar_telefone("(21) 3333-0002") == "+552133330002"


def test_telefone_celular_antigo_ganha_o_nono_digito():
    assert v.padronizar_telefone("(31) 9999-0003") == "+5531999990003"


@pytest.mark.parametrize("entrada", ["9999-0004", "123", "", "(10) 99990-0005", "(11) 89990-0006"])
def test_telefone_que_nao_da_para_padronizar(entrada):
    assert v.padronizar_telefone(entrada) is None


def test_separar_nome_com_particula():
    assert v.separar_nome("  MARIA  aparecida DA silva ") == ("Maria", "Aparecida da Silva")


def test_separar_nome_vazio():
    assert v.separar_nome("   ") == ("", "")


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("Alimentos Alfa LTDA", "Alimentos Alfa"),
        ("Bebidas Beta S.A.", "Bebidas Beta"),
        ("Laboratório Delta - EIRELI", "Laboratório Delta"),
        ("Cosméticos Gama Ltda. ME", "Cosméticos Gama"),
        ("Pet Zeta", "Pet Zeta"),
    ],
)
def test_padronizar_empresa(entrada, esperado):
    assert v.padronizar_empresa(entrada) == esperado


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("04.321.005/0001-00", "04321005000100"),
        ("4321005000100", "04321005000100"),   # zero à esquerda perdido
        ("123456", ""),
        ("", ""),
    ],
)
def test_padronizar_cnpj(entrada, esperado):
    assert v.padronizar_cnpj(entrada) == esperado


@pytest.mark.parametrize(
    "cargo, esperado",
    [
        ("Gerente de Compras", "Compras"),
        ("Diretora de Marketing", "Diretoria"),   # diretoria tem precedência
        ("Gerente de Produto", "Marketing"),
        ("Gerente de Produção", "Produção"),
        ("Brand Manager", "Outros"),              # limite das palavras-chave
    ],
)
def test_area_do_cargo(cargo, esperado):
    assert v.area_do_cargo(cargo) == esperado


@pytest.mark.parametrize(
    "entrada, esperado",
    [("credenciamento", "Credenciamento"), ("EVENTO 2025", "Evento"), ("Indicação", None), ("", None)],
)
def test_padronizar_origem(entrada, esperado):
    assert v.padronizar_origem(entrada) == esperado


@pytest.mark.parametrize(
    "aceita, data, esperado",
    [
        ("Sim", "15/03/2025", ("S", "2025-03-15", False)),
        ("s", "2025-03-15", ("S", "2025-03-15", False)),
        ("Sim", "", ("N", "", True)),             # aceite sem data: rebaixado
        ("sim", "31/02/2025", ("N", "", True)),   # data que não existe
        ("Não", "", ("N", "", False)),
        ("", "", ("N", "", False)),
    ],
)
def test_padronizar_consentimento(aceita, data, esperado):
    assert v.padronizar_consentimento(aceita, data) == esperado

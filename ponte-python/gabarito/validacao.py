"""Funções de validação e padronização de campos de contato.

Solução de referência do módulo P.2. Tente escrever a sua versão antes de ler.
"""

import re
from datetime import datetime

UFS = {
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
    "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
}

PARTICULAS = {"de", "da", "do", "dos", "das", "e"}

SUFIXOS_EMPRESA = ["ltda", "s.a", "s/a", "sa", "me", "eireli", "epp"]

ORIGENS = ["Credenciamento", "Expositor", "Site", "Evento", "Compra de base"]

# A ordem importa: a primeira área cujas palavras aparecem no cargo é a escolhida.
AREAS = [
    ("Diretoria", ["diretor", "sócio", "socio", "proprietári", "proprietari", "presidente", "ceo"]),
    ("Compras", ["compra", "suprimentos", "procurement", "supply"]),
    ("Produção", ["produção", "producao", "industrial", "qualidade", "engenh", "p&d", "desenvolvimento"]),
    ("Marketing", ["marketing", "marca", "produto", "trade", "comunicação", "comunicacao"]),
    ("Comercial", ["vendas", "comercial", "representante", "key account"]),
]


def limpar_texto(texto):
    """Remove espaços das pontas e reduz espaços repetidos a um só."""
    return " ".join(str(texto).split())


def padronizar_email(texto):
    """Devolve o e-mail em minúsculas e sem espaços nas pontas."""
    return str(texto).strip().lower()


def email_valido(email):
    """Diz se o e-mail tem formato aceitável para importação."""
    if email == "" or " " in email or email.count("@") != 1:
        return False
    for caractere in email:
        permitido = caractere.isascii() and (caractere.isalnum() or caractere in "._-+@")
        if not permitido:
            return False
    usuario, dominio = email.split("@")
    if usuario == "" or "." not in dominio:
        return False
    if dominio.startswith(".") or dominio.endswith("."):
        return False
    return True


def padronizar_telefone(texto):
    """Devolve o telefone no formato +55DDDNÚMERO ou None se não der para padronizar."""
    digitos = re.sub(r"\D", "", str(texto))
    if digitos.startswith("0"):
        digitos = digitos.lstrip("0")
    if len(digitos) in (12, 13) and digitos.startswith("55"):
        digitos = digitos[2:]
    if len(digitos) not in (10, 11):
        return None
    ddd = digitos[:2]
    numero = digitos[2:]
    if "0" in ddd:
        return None
    if len(numero) == 8 and numero[0] in "6789":
        numero = "9" + numero  # celular antigo, sem o nono dígito
    if len(numero) == 9 and numero[0] != "9":
        return None
    if len(numero) == 8 and numero[0] not in "2345":
        return None
    return "+55" + ddd + numero


def capitalizar_nome(texto):
    """Coloca iniciais maiúsculas, mantendo partículas como 'de' e 'da' em minúsculas."""
    palavras = limpar_texto(texto).lower().split(" ")
    resultado = []
    for posicao, palavra in enumerate(palavras):
        if palavra in PARTICULAS and posicao > 0:
            resultado.append(palavra)
        else:
            resultado.append(palavra.capitalize())
    return " ".join(resultado)


def separar_nome(nome_completo):
    """Divide o nome completo em (nome, sobrenome)."""
    nome_limpo = capitalizar_nome(nome_completo)
    if nome_limpo == "":
        return "", ""
    partes = nome_limpo.split(" ", 1)
    nome = partes[0]
    sobrenome = partes[1] if len(partes) > 1 else ""
    return nome, sobrenome


def padronizar_empresa(texto):
    """Remove sufixos societários como LTDA, S.A. e ME do fim do nome."""
    empresa = limpar_texto(texto)
    while True:
        palavras = empresa.split(" ")
        ultima = palavras[-1].lower().strip(".,") if palavras else ""
        if len(palavras) > 1 and ultima in SUFIXOS_EMPRESA:
            empresa = " ".join(palavras[:-1]).rstrip(" ,-")
        else:
            return empresa


def padronizar_cnpj(texto):
    """Devolve o CNPJ com 14 dígitos ou '' se a quantidade de dígitos não fizer sentido."""
    digitos = re.sub(r"\D", "", str(texto))
    if 12 <= len(digitos) <= 14:
        return digitos.zfill(14)
    return ""


def padronizar_cep(texto):
    """Devolve o CEP com 8 dígitos ou '' se a quantidade de dígitos não fizer sentido."""
    digitos = re.sub(r"\D", "", str(texto))
    if 7 <= len(digitos) <= 8:
        return digitos.zfill(8)
    return ""


def padronizar_uf(texto):
    """Devolve a sigla em maiúsculas ou '' se não for uma UF."""
    uf = limpar_texto(texto).upper()
    return uf if uf in UFS else ""


def area_do_cargo(cargo):
    """Classifica o cargo em uma das áreas do layout do CRM."""
    cargo_minusculo = str(cargo).lower()
    for area, palavras in AREAS:
        for palavra in palavras:
            if palavra in cargo_minusculo:
                return area
    return "Outros"


def padronizar_origem(texto):
    """Devolve a origem conforme a lista do layout ou None se não for reconhecida."""
    origem = limpar_texto(texto).lower()
    for opcao in ORIGENS:
        if origem.startswith(opcao.lower()):
            return opcao
    return None


def padronizar_data(texto):
    """Converte DD/MM/AAAA ou AAAA-MM-DD em AAAA-MM-DD. Devolve '' se a data não existir."""
    valor = limpar_texto(texto)
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(valor, formato).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def padronizar_consentimento(aceita, data):
    """Devolve (consentimento, data, rebaixado).

    O consentimento só é 'S' quando há aceite e uma data válida. Aceite sem data
    válida vira 'N', porque não há registro que comprove o consentimento.
    """
    aceitou = limpar_texto(aceita).lower() in ("s", "sim")
    data_padronizada = padronizar_data(data)
    if aceitou and data_padronizada != "":
        return "S", data_padronizada, False
    if aceitou:
        return "N", "", True
    return "N", "", False

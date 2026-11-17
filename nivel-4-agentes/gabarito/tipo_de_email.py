"""Classifica o e-mail de um contato como corporativo ou pessoal.

Solução de referência da funcionalidade do exercício do módulo 4.4. No seu repositório, a função vai para o
validacao.py, com os testes no test_validacao.py. Executado e testado.

Uso na segmentação: contatos com e-mail pessoal costumam ser visitantes ou profissionais autônomos; contatos
com e-mail corporativo permitem agrupar por empresa (domínio).
"""

import validacao as v

# Domínios de e-mail gratuito mais comuns no Brasil. A lista é uma decisão de negócio: revise com a equipe.
DOMINIOS_PESSOAIS = {
    "gmail.com", "hotmail.com", "hotmail.com.br", "outlook.com", "outlook.com.br", "live.com",
    "yahoo.com", "yahoo.com.br", "icloud.com", "uol.com.br", "bol.com.br", "terra.com.br",
    "ig.com.br", "globo.com", "msn.com",
}


def tipo_de_email(texto):
    """Devolve "pessoal", "corporativo" ou "" para e-mail vazio ou inválido.

    O e-mail é padronizado antes (minúsculas, sem espaços nas pontas), como na importação.
    """
    email = v.padronizar_email(texto)
    if not v.email_valido(email):
        return ""
    dominio = email.split("@")[1]
    return "pessoal" if dominio in DOMINIOS_PESSOAIS else "corporativo"

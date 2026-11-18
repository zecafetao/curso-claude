"""Confere por código os itens da lista de 15 do módulo 2.7 que não dependem de leitura humana.

Material do bônus do Nível 4 (agente de campanha). Executado e testado contra o e-mail de referência do
Nível 2. Os itens 12 a 15 (tom, fatos do briefing, celular e versão de texto) continuam com você.

Uso:
    python verificar_email.py email.html "Fazer meu credenciamento gratuito"
"""

import re
import sys

TAG_A = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.IGNORECASE | re.DOTALL)
TAG_TD = re.compile(r"<td\b([^>]*)>((?:(?!<td\b).)*?)</td>", re.IGNORECASE | re.DOTALL)


def estilo(atributos, propriedade):
    achado = re.search(rf"{propriedade}\s*:\s*([^;\"']+)", atributos, re.IGNORECASE)
    return achado.group(1).strip() if achado else None


def luminancia(cor_hex):
    cor_hex = cor_hex.lstrip("#")
    if len(cor_hex) == 3:
        cor_hex = "".join(c * 2 for c in cor_hex)
    canais = [int(cor_hex[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lineares = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    return 0.2126 * lineares[0] + 0.7152 * lineares[1] + 0.0722 * lineares[2]


def contraste(cor_a, cor_b):
    """Razão de contraste da WCAG entre duas cores em hexadecimal."""
    claro, escuro = sorted((luminancia(cor_a), luminancia(cor_b)), reverse=True)
    return (claro + 0.05) / (escuro + 0.05)


def verificar_email(html, texto_botao):
    """Devolve uma lista de (item, aprovado, detalhe)."""
    resultado = []
    titulo = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    assunto = titulo.group(1).strip() if titulo else ""
    resultado.append((1, 0 < len(assunto) <= 60, f"assunto com {len(assunto)} caracteres"))

    oculto = re.search(r"<div[^>]*display\s*:\s*none[^>]*>(.*?)</div>", html, re.IGNORECASE | re.DOTALL)
    pre = re.sub(r"\s+", " ", re.sub(r"<[^>]+>|&[a-z#0-9]+;", " ", oculto.group(1))).strip() if oculto else ""
    resultado.append((2, 0 < len(pre) <= 90 and pre != assunto, f"pré-cabeçalho com {len(pre)} caracteres"))

    botoes = [(atr, re.sub(r"<[^>]+>", "", txt).strip()) for atr, txt in TAG_A.findall(html)
              if "inline-block" in atr.replace(" ", "")]
    resultado.append((3, len(botoes) == 1, f"{len(botoes)} botão(ões) de ação"))
    resultado.append((4, len(botoes) == 1 and botoes[0][1] == texto_botao,
                      f"texto do botão: {botoes[0][1]!r}" if botoes else "sem botão"))
    resultado.append((5, "<table" in html.lower(), "layout em tabelas"))
    proibidas = [t for t in ("<style", "<script", "<form") if t in html.lower()]
    resultado.append((6, not proibidas, f"blocos proibidos: {proibidas or 'nenhum'}"))
    resultado.append((7, re.search(r"max-width\s*:\s*600px", html, re.IGNORECASE) is not None, "largura máxima de 600 px"))
    fontes = re.findall(r"font-family\s*:\s*([^;\"']+)", html, re.IGNORECASE)
    sem_arial = [f for f in fontes if "arial" not in f.lower()]
    resultado.append((8, bool(fontes) and not sem_arial, f"{len(fontes)} declarações de fonte, {len(sem_arial)} sem Arial"))

    celula = next((atr for atr, conteudo in TAG_TD.findall(html) if texto_botao in conteudo), None)
    fundo = estilo(celula, "background-color") if celula else None
    resultado.append((9, fundo is not None, f"cor de fundo na célula do botão: {fundo}"))
    cor_texto = estilo(botoes[0][0], "color") if botoes else None
    if fundo and cor_texto and fundo.startswith("#") and cor_texto.startswith("#"):
        razao = contraste(fundo, cor_texto)
        resultado.append((10, razao >= 4.5, f"contraste do botão {razao:.1f} para 1"))
    else:
        resultado.append((10, False, "não foi possível calcular o contraste"))
    descadastro = any("descadastr" in (atr + txt).lower() for atr, txt in TAG_A.findall(html))
    resultado.append((11, descadastro, "link de descadastro (remetente, motivo e endereço: confira lendo)"))
    return resultado


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Uso: python verificar_email.py email.html "texto do botão"')
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as arquivo:
        itens = verificar_email(arquivo.read(), sys.argv[2])
    for item, aprovado, detalhe in itens:
        print(f"  {'OK   ' if aprovado else 'FALHA'} item {item:2d}: {detalhe}")
    print("Itens 12 a 15: confira lendo (tom, fatos do briefing, celular, versão de texto).")
    sys.exit(0 if all(aprovado for _, aprovado, _ in itens) else 1)

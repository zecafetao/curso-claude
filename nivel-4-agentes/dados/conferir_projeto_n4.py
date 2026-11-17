"""Confere o rascunho gerado pelo agente de relatórios do projeto do Nível 4.

Uso:
    python dados_n4/conferir_projeto_n4.py mensal saida_relatorios/mensal_2026-10/relatorio_email_2026-10.pptx
    python dados_n4/conferir_projeto_n4.py pos_feira saida_relatorios/pos_feira/report_pos_feira.pptx

O que é conferido:
- a apresentação tem os 8 slides da estrutura e o rodapé em todos os slides de conteúdo;
- os números principais do gabarito aparecem na apresentação;
- todo número escrito em qualquer slide existe no gabarito do relatório (datas, anos e inteiros
  de 0 a 10 não são conferidos);
- o slide de leitura tem três achados, cada um com um próximo passo;
- a lista de conferência (conferencia.csv) existe, ao lado da apresentação, com as colunas esperadas.
"""

import csv
import re
import sys
from pathlib import Path

from pptx import Presentation

# Valores calculados pela solução de referência a partir dos dados do curso (referência: novembro de 2026).
PERMITIDOS = {
    "mensal": [0.6, 0.7, 1.0, 1.6, 1.8, 2.4, 3.6, 3.7, 6.8, 6.9, 12.6, 13, 14, 15, 20.1, 21.0, 40.6, 45.7,
               52.6, 54.7, 59.1, 61, 64.8, 69, 95.9, 97, 97.7, 97.9, 98.6, 98.8, 99.1, 100.0, 162, 304, 1112,
               1218, 2780, 2900, 4248, 4350, 16701, 16860, 26225, 26385, 26540, 28798, 50116, 50812, 62952, 64307],
    "pos_feira": [1.8, 2.4, 13, 14, 15, 20, 20.2, 21, 27, 36.8, 38.9, 44, 45.7, 47.7, 52, 52.6, 63, 69, 76, 91,
                  94.1, 95.4, 96.7, 97, 97.9, 98.6, 101, 109, 126, 166, 218, 429, 435, 441, 451, 456, 560, 1112,
                  1218, 26385, 28798, 50116, 50812, 62952, 64307],
}
OBRIGATORIOS = {
    "mensal": ["50.812", "98,6%", "52,6%", "2,4%", "64.307", "45,7%", "+6,9 p.p.", "-21,0%", "54,7%", "59,1%",
               "40,6%", "12,6%", "64,8%", "20,1%"],
    "pos_feira": ["560", "218", "38,9%", "44", "95,4%", "96,7%", "94,1%", "36,8%", "47,7%", "50.812", "64.307"],
}
MESES = "janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro"
DATA = re.compile(
    r"\d{4}-\d{2}(?:-\d{2})?|\d{1,2}/\d{1,2}(?:/\d{2,4})?"
    rf"|\d{{1,2}}(?:º)?(?:\s*(?:a|e|,)\s*\d{{1,2}})*\s+de\s+(?:{MESES})|\bdias?\s+\d{{1,2}}(?:\s*(?:a|e|,)\s*\d{{1,2}})*",
    re.IGNORECASE,
)
NUMERO = re.compile(r"(?<![\w.,])[-+−]?\d{1,3}(?:\.\d{3})+(?:,\d+)?(?![\w])|(?<![\w.,])[-+−]?\d+(?:,\d+)?(?![\w])")


def numeros(texto):
    for achado in NUMERO.finditer(DATA.sub(" ", texto)):
        valor = float(achado.group().replace("−", "-").replace(".", "").replace(",", "."))
        if valor.is_integer() and (1900 <= abs(valor) <= 2100 or abs(valor) <= 10):
            continue
        yield achado.group(), abs(valor)


def textos_dos_slides(caminho):
    slides = []
    for slide in Presentation(caminho).slides:
        partes = []
        for forma in slide.shapes:
            if forma.has_text_frame:
                partes.append(forma.text_frame.text)
            if forma.has_table:
                partes += [celula.text for linha in forma.table.rows for celula in linha.cells]
        slides.append(partes)
    return slides


def conferir(tipo, caminho):
    problemas = []
    slides = textos_dos_slides(caminho)
    if len(slides) != 8:
        problemas.append(f"A apresentação tem {len(slides)} slides; a estrutura pede 8.")
    for numero, partes in enumerate(slides[1:], start=2):
        if not any(parte.startswith("Agência Modelo ·") for parte in partes):
            problemas.append(f"Slide {numero} sem o rodapé do padrão visual.")

    tudo = "\n".join("\n".join(partes) for partes in slides)
    for esperado in OBRIGATORIOS[tipo]:
        if esperado not in tudo:
            problemas.append(f"Número do gabarito ausente: {esperado}")

    permitidos = PERMITIDOS[tipo]
    for numero, partes in enumerate(slides, start=1):
        for parte in partes:
            for escrito, valor in numeros(parte):
                if not any(abs(valor - p) < 0.051 for p in permitidos):
                    problemas.append(f"Slide {numero}: o número {escrito} não está no gabarito ({parte[:60]!r})")

    leitura = next((partes for partes in slides if partes and partes[0].startswith("Leitura")), None)
    if leitura is None:
        problemas.append("Não encontrei o slide de leitura.")
    elif sum(parte.count("Próximo passo") for parte in leitura) != 3:
        problemas.append("O slide de leitura precisa de três achados, cada um com um próximo passo.")

    conferencia = Path(caminho).with_name("conferencia.csv")
    if not conferencia.exists():
        problemas.append("conferencia.csv não encontrado ao lado da apresentação.")
    else:
        with open(conferencia, encoding="utf-8", newline="") as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=";")
            linhas = list(leitor)
        if leitor.fieldnames != ["slide", "elemento", "valor", "origem"]:
            problemas.append(f"conferencia.csv com colunas {leitor.fieldnames}; esperadas slide, elemento, valor, origem.")
        elif len(linhas) < 30:
            problemas.append(f"conferencia.csv tem só {len(linhas)} linhas.")
    return problemas


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in PERMITIDOS:
        print("Uso: python conferir_projeto_n4.py mensal|pos_feira caminho/da/apresentacao.pptx")
        sys.exit(1)
    encontrados = conferir(sys.argv[1], sys.argv[2])
    for problema in encontrados:
        print(f"  {problema}")
    print("Projeto aprovado no conferidor." if not encontrados else f"Ainda há diferenças: {len(encontrados)}.")

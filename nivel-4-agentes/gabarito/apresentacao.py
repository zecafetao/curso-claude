"""Monta a apresentação do relatório no padrão visual da Agência Modelo (fictício).

Usado pelo projeto do Nível 4. Executado e testado.

Divisão de trabalho:
- todos os números das tabelas e dos destaques vêm do módulo indicadores, por código;
- o modelo escreve só os títulos-achado e as leituras, e cada número que ele escreve passa
  pelo verificar_numeros antes de entrar no arquivo;
- cada número colocado na apresentação é registrado na lista de conferência, com a origem.
"""

import csv
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm, Pt

import indicadores as ind
import relatorio_mensal as rm
import verificar_numeros as vn

AZUL_MARINHO = RGBColor(0x14, 0x21, 0x3D)
BRANCO = RGBColor(0xFF, 0xFF, 0xFF)
AMBAR = RGBColor(0xF5, 0x9E, 0x0B)
GRAFITE = RGBColor(0x1F, 0x1F, 0x1F)
CINZA_CLARO = RGBColor(0xE5, 0xE5, 0xE5)
FONTE = "Arial"
LARGURA, ALTURA = Cm(33.867), Cm(19.05)          # 16:9
MARGEM = Cm(1.3)
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]


def nome_do_mes(mes):
    """'2026-10' vira 'outubro de 2026'."""
    ano, numero = mes.split("-")
    return f"{MESES[int(numero) - 1]} de {ano}"


class Relatorio:
    """Uma apresentação em construção, com a lista de conferência dos números colocados."""

    def __init__(self, rodape):
        self.apresentacao = Presentation()
        self.apresentacao.slide_width, self.apresentacao.slide_height = LARGURA, ALTURA
        self.rodape = rodape
        self.conferencia = []

    # ---------- registro ----------

    def registrar(self, slide, elemento, valor, origem):
        self.conferencia.append({"slide": slide, "elemento": elemento, "valor": valor, "origem": origem})

    # ---------- blocos de texto ----------

    def _texto(self, slide, esquerda, topo, largura, altura, texto, tamanho, negrito=False, cor=GRAFITE,
               alinhamento=PP_ALIGN.LEFT):
        caixa = slide.shapes.add_textbox(esquerda, topo, largura, altura)
        quadro = caixa.text_frame
        quadro.word_wrap = True
        paragrafo = quadro.paragraphs[0]
        paragrafo.alignment = alinhamento
        trecho = paragrafo.add_run()
        trecho.text = texto
        trecho.font.name, trecho.font.size, trecho.font.bold = FONTE, Pt(tamanho), negrito
        trecho.font.color.rgb = cor
        return caixa

    def _novo_slide(self, titulo=None, fundo=None):
        slide = self.apresentacao.slides.add_slide(self.apresentacao.slide_layouts[6])   # layout em branco
        if fundo is not None:
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = fundo
        numero = len(self.apresentacao.slides)
        if titulo is not None:
            self._texto(slide, MARGEM, MARGEM, LARGURA - 2 * MARGEM, Cm(2.6), titulo, 28, negrito=True)
            rodape = f"{self.rodape} · {numero}"
            self._texto(slide, MARGEM, ALTURA - MARGEM - Cm(0.6), LARGURA - 2 * MARGEM, Cm(0.6), rodape, 9)
        return slide, numero

    # ---------- tipos de slide ----------

    def capa(self, linhas):
        slide, _ = self._novo_slide(fundo=AZUL_MARINHO)
        topo = Cm(6)
        for indice, linha in enumerate(linhas):
            tamanho = 40 if indice == 0 else 20
            self._texto(slide, MARGEM, topo, LARGURA - 2 * MARGEM, Cm(2.2), linha, tamanho,
                        negrito=indice == 0, cor=BRANCO)
            topo += Cm(2.4 if indice == 0 else 1.4)

    def destaques(self, titulo, itens, nota=""):
        """Números principais em âmbar. itens: (rótulo, valor formatado, origem)."""
        slide, numero = self._novo_slide(titulo)
        largura = (LARGURA - 2 * MARGEM) / len(itens)
        for posicao, (rotulo, valor, origem) in enumerate(itens):
            esquerda = MARGEM + largura * posicao
            self._texto(slide, esquerda, Cm(6), largura, Cm(2.2), valor, 44, negrito=True, cor=AMBAR)
            self._texto(slide, esquerda, Cm(8.4), largura - Cm(0.5), Cm(2), rotulo, 14)
            self.registrar(numero, rotulo, valor, origem)
        if nota:
            self._texto(slide, MARGEM, Cm(14.5), LARGURA - 2 * MARGEM, Cm(1.8), nota, 9)

    def tabela(self, titulo, cabecalho, linhas, origem, numericas, nota="", total=False):
        """Tabela com cabeçalho azul-marinho. As colunas em 'numericas' ficam alinhadas à direita."""
        slide, numero = self._novo_slide(titulo)
        linhas = linhas[:10]                                          # no máximo 10 linhas por slide
        forma = slide.shapes.add_table(len(linhas) + 1, len(cabecalho), MARGEM, Cm(4.2),
                                       LARGURA - 2 * MARGEM, Cm(0.9) * (len(linhas) + 1))
        grade = forma.table
        for coluna, texto in enumerate(cabecalho):
            celula = grade.cell(0, coluna)
            celula.fill.solid()
            celula.fill.fore_color.rgb = AZUL_MARINHO
            self._celula(celula, texto, BRANCO, negrito=True, direita=coluna in numericas)
        for indice, linha in enumerate(linhas, start=1):
            ultima = total and indice == len(linhas)
            for coluna, texto in enumerate(linha):
                celula = grade.cell(indice, coluna)
                celula.fill.solid()
                celula.fill.fore_color.rgb = BRANCO
                self._celula(celula, str(texto), GRAFITE, negrito=ultima, direita=coluna in numericas)
                if coluna in numericas:
                    self.registrar(numero, f"{linha[0]} · {cabecalho[coluna]}", str(texto), origem)
        if nota:                                                      # posição fixa: linhas que quebram não a cobrem
            self._texto(slide, MARGEM, Cm(14.5), LARGURA - 2 * MARGEM, Cm(1.8), nota, 9)

    def _celula(self, celula, texto, cor, negrito=False, direita=False):
        quadro = celula.text_frame
        quadro.paragraphs[0].alignment = PP_ALIGN.RIGHT if direita else PP_ALIGN.LEFT
        trecho = quadro.paragraphs[0].add_run()
        trecho.text = texto
        trecho.font.name, trecho.font.size, trecho.font.bold = FONTE, Pt(11), negrito
        trecho.font.color.rgb = cor

    def imagem(self, titulo, caminho, origem, nota=""):
        slide, numero = self._novo_slide(titulo)
        altura = ALTURA - Cm(4.2) - MARGEM - Cm(1.6)
        slide.shapes.add_picture(str(caminho), MARGEM, Cm(4.0), height=altura)
        self.registrar(numero, f"gráfico {Path(caminho).name}", "valores na tabela de mesmo nome", origem)
        if nota:
            self._texto(slide, MARGEM, ALTURA - MARGEM - Cm(1.6), LARGURA - 2 * MARGEM, Cm(0.9), nota, 9)

    def leituras(self, titulo, achados, referencias):
        """Os achados escritos pelo modelo. Cada número deles foi conferido antes de chegar aqui."""
        slide, numero = self._novo_slide(titulo)
        topo = Cm(4.2)
        for achado in achados:
            self._texto(slide, MARGEM, topo, LARGURA - 2 * MARGEM, Cm(1), achado["titulo"], 14, negrito=True)
            texto = f"{achado['fato']} Próximo passo: {achado['proximo_passo']}"
            self._texto(slide, MARGEM, topo + Cm(1), LARGURA - 2 * MARGEM, Cm(2.2), texto, 14)
            for item in vn.verificar(" ".join(achado.values()), referencias)["verificados"]:
                self.registrar(numero, f"leitura: {achado['titulo']}", item["numero"], "texto do modelo, conferido")
            topo += Cm(3.6)

    def notas(self, titulo, linhas):
        slide, _ = self._novo_slide(titulo)
        self._texto(slide, MARGEM, Cm(4.2), LARGURA - 2 * MARGEM, Cm(10), "\n".join(linhas), 14)

    # ---------- gravação ----------

    def gravar(self, caminho_pptx):
        caminho_pptx = Path(caminho_pptx)
        caminho_pptx.parent.mkdir(parents=True, exist_ok=True)
        self.apresentacao.save(caminho_pptx)
        caminho_conferencia = caminho_pptx.with_name("conferencia.csv")
        with open(caminho_conferencia, "w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=["slide", "elemento", "valor", "origem"], delimiter=";")
            escritor.writeheader()
            escritor.writerows(self.conferencia)
        return caminho_pptx, caminho_conferencia


# ---------- os dois relatórios ----------

def referencias(tipo, mes=None, mes_anterior=None):
    """Os resultados de ferramenta contra os quais o texto do modelo é conferido."""
    if tipo == "mensal":
        return [ind.indicadores_email(mes), ind.indicadores_email(mes_anterior), ind.indicadores_por_publico(mes),
                ind.comparar_meses(mes, mes_anterior), ind.anomalias_de_clique(mes)]
    return [ind.funil_feira(), ind.entrega_whatsapp(), ind.whatsapp_e_visitacao(),
            ind.indicadores_email("2026-09"), ind.indicadores_email("2026-10")]


def conferir_textos(textos, refs):
    """Devolve os números sem fonte nos textos do modelo. Lista vazia significa aprovado."""
    sem_fonte = []
    for texto in textos:
        sem_fonte += vn.verificar(texto, refs)["sem_fonte"]
    return sem_fonte


def relatorio_mensal(mes, mes_anterior, achados, titulos, graficos, caminho_pptx):
    """Monta o relatório mensal de e-mail. titulos: textos-achado de cada slide de dados."""
    refs = referencias("mensal", mes, mes_anterior)
    sem_fonte = conferir_textos(list(titulos.values()) + [" ".join(a.values()) for a in achados], refs)
    if sem_fonte:
        return {"erro": "Há números sem fonte no texto.", "sem_fonte": sem_fonte}

    geral, publicos = ind.indicadores_email(mes), ind.indicadores_por_publico(mes)
    comparacao, anomalias = ind.comparar_meses(mes, mes_anterior), ind.anomalias_de_clique(mes)
    periodo, anterior = nome_do_mes(mes), nome_do_mes(mes_anterior)
    origem_geral = f"indicadores_email({mes})"

    r = Relatorio(f"Agência Modelo · Expo Modelo 2026 · E-mail marketing · {periodo}")
    r.capa(["Expo Modelo 2026", periodo.capitalize(), "E-mail marketing — desempenho dos disparos"])
    excluidos = ", ".join(f"{d['disparo']} ({d['enviadas']} envios)" for d in geral["disparos_excluidos"])
    r.destaques(titulos["indicadores"], [
        ("Mensagens enviadas", rm.numero(geral["enviadas"]), origem_geral),
        ("Taxa de entrega", rm.percentual(geral["taxa_entrega"]), origem_geral),
        ("Taxa de abertura", rm.percentual(geral["taxa_abertura"]), origem_geral),
        ("Taxa de clique", rm.percentual(geral["taxa_clique"]), origem_geral),
    ], nota=f"Fora dos totais por terem menos de 10 envios: {excluidos or 'nenhum disparo'}.")

    atual, ant, dif = comparacao["atual"], comparacao["anterior"], comparacao["diferencas_pp"]
    r.tabela(titulos["comparacao"], ["Indicador", anterior.capitalize(), periodo.capitalize(), "Diferença"], [
        ["Mensagens enviadas", rm.numero(ant["enviadas"]), rm.numero(atual["enviadas"]),
         f"{rm.sinal(dif['variacao_enviadas_pct'])}%"],
        ["Taxa de entrega", rm.percentual(ant["taxa_entrega"]), rm.percentual(atual["taxa_entrega"]),
         f"{rm.sinal(dif['taxa_entrega'])} p.p."],
        ["Taxa de abertura", rm.percentual(ant["taxa_abertura"]), rm.percentual(atual["taxa_abertura"]),
         f"{rm.sinal(dif['taxa_abertura'])} p.p."],
        ["Taxa de clique", rm.percentual(ant["taxa_clique"]), rm.percentual(atual["taxa_clique"]),
         f"{rm.sinal(dif['taxa_clique'])} p.p."],
    ], f"comparar_meses({mes}, {mes_anterior})", numericas={1, 2, 3},
        nota="Diferenças de taxa em pontos percentuais (p.p.).")

    linhas = [[p["publico"], rm.numero(p["disparos"]), rm.numero(p["enviadas"]), rm.numero(p["entregues"]),
               rm.percentual(p["taxa_entrega"]), rm.percentual(p["taxa_abertura"]), rm.percentual(p["taxa_clique"])]
              for p in publicos["publicos"]]
    linhas.append(["Total", rm.numero(geral["disparos"]), rm.numero(geral["enviadas"]), rm.numero(geral["entregues"]),
                   rm.percentual(geral["taxa_entrega"]), rm.percentual(geral["taxa_abertura"]),
                   rm.percentual(geral["taxa_clique"])])
    nota_anomalia = "; ".join(f"{d['disparo']}: clique de {rm.percentual(d['taxa_clique'])}, possível clique automático"
                              for d in anomalias["disparos"])
    r.tabela(titulos["publico"], ["Público", "Disparos", "Enviadas", "Entregues", "Entrega", "Abertura", "Clique"],
             linhas, f"indicadores_por_publico({mes})", numericas={1, 2, 3, 4, 5, 6}, total=True,
             nota=f"Anomalia mantida nos totais: {nota_anomalia}." if nota_anomalia else "")

    r.imagem(titulos["grafico_clique"], graficos["clique"], f"indicadores_por_publico({mes})")
    r.imagem(titulos["grafico_abertura"], graficos["abertura"], f"indicadores_por_publico({mes}) e ({mes_anterior})")
    r.leituras("Leitura do mês e próximos passos", achados, refs)
    r.notas("Notas metodológicas", [
        "Taxa de entrega = entregues ÷ enviadas. Taxas de abertura e de clique sobre as entregues.",
        "Taxa de um grupo = soma dos numeradores ÷ soma dos denominadores.",
        "Disparos com menos de 10 envios ficam fora do relatório.",
        "Taxa de clique acima de 15% é sinalizada como possível clique automático e mantida nos totais.",
        "Números calculados por código a partir das exportações do CRM; lista de conferência em conferencia.csv.",
    ])
    return {"arquivos": [str(caminho) for caminho in r.gravar(caminho_pptx)], "numeros_registrados": len(r.conferencia)}


def report_pos_feira(achados, titulos, graficos, caminho_pptx):
    """Monta o report pós-feira: funil, WhatsApp, e-mail da campanha, leituras e notas."""
    refs = referencias("pos_feira")
    sem_fonte = conferir_textos(list(titulos.values()) + [" ".join(a.values()) for a in achados], refs)
    if sem_fonte:
        return {"erro": "Há números sem fonte no texto.", "sem_fonte": sem_fonte}

    funil, entrega, cruzamento = ind.funil_feira(), ind.entrega_whatsapp(), ind.whatsapp_e_visitacao()
    setembro, outubro = ind.indicadores_email("2026-09"), ind.indicadores_email("2026-10")

    r = Relatorio("Agência Modelo · Expo Modelo 2026 · Report pós-feira · outubro de 2026")
    r.capa(["Expo Modelo 2026", "Report pós-feira", "E-mail, WhatsApp, credenciamento e visitação"])
    r.destaques(titulos["funil"], [
        ("Credenciados (pessoas)", rm.numero(funil["credenciados"]), "funil_feira()"),
        ("Visitantes (pessoas)", rm.numero(funil["visitantes"]), "funil_feira()"),
        ("Visitação sobre credenciados", rm.percentual(funil["taxa_visitacao"]), "funil_feira()"),
        ("Participantes do evento", rm.numero(funil["participantes_evento"]), "funil_feira()"),
    ], nota="Pessoas contadas uma vez, depois de resolver a identidade por e-mail, telefone e nome.")
    r.imagem(titulos["grafico_funil"], graficos["funil"], "funil_feira()")
    r.tabela(titulos["whatsapp"], ["Disparo", "Data", "Contatos", "Receberam", "Entrega", "Tentativas com erro"],
             [[f"{d['disparo']} · {d['tema']}", d["data_envio"], rm.numero(d["contatos"]), rm.numero(d["receberam"]),
               rm.percentual(d["taxa_entrega"]), rm.numero(d["tentativas_com_erro"])] for d in entrega["disparos"]],
             "entrega_whatsapp()", numericas={2, 3, 4, 5},
             nota="Um contato recebeu o disparo se ao menos uma tentativa foi entregue.")
    r.tabela(titulos["whatsapp_visitacao"], ["Grupo", "Pessoas", "Visitaram", "Taxa de visitação"], [
        ["Recebeu ao menos uma mensagem", rm.numero(cruzamento["recebeu"]["pessoas"]),
         rm.numero(cruzamento["recebeu"]["visitaram"]), rm.percentual(cruzamento["recebeu"]["taxa_visitacao"])],
        ["Não recebeu", rm.numero(cruzamento["nao_recebeu"]["pessoas"]),
         rm.numero(cruzamento["nao_recebeu"]["visitaram"]), rm.percentual(cruzamento["nao_recebeu"]["taxa_visitacao"])],
    ], "whatsapp_e_visitacao()", numericas={1, 2, 3}, nota=cruzamento["observacao"])
    r.tabela(titulos["email"], ["Mês", "Disparos", "Enviadas", "Entrega", "Abertura", "Clique"], [
        [nome_do_mes(m["mes"]).capitalize(), rm.numero(m["disparos"]), rm.numero(m["enviadas"]),
         rm.percentual(m["taxa_entrega"]), rm.percentual(m["taxa_abertura"]), rm.percentual(m["taxa_clique"])]
        for m in (setembro, outubro)
    ], "indicadores_email(2026-09) e (2026-10)", numericas={1, 2, 3, 4, 5})
    r.leituras("Leitura da campanha e próximos passos", achados, refs)
    r.notas("Notas metodológicas", [
        "Funil em pessoas: as bases de credenciamento, visitação e evento foram unidas e a identidade resolvida.",
        "WhatsApp: entrega contada em contatos; tentativas repetidas não somam.",
        "A comparação entre quem recebeu e quem não recebeu WhatsApp não mede efeito: os grupos não foram sorteados.",
        "E-mail: disparos com menos de 10 envios ficam fora dos totais.",
        "Números calculados por código; lista de conferência em conferencia.csv.",
    ])
    return {"arquivos": [str(caminho) for caminho in r.gravar(caminho_pptx)], "numeros_registrados": len(r.conferencia)}

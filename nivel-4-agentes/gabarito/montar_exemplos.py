"""Monta os dois relatórios do projeto com títulos e achados escritos à mão, sem chamar a API.

Material do projeto do Nível 4. Executado e testado. Serve para três coisas:
- testar a montagem, os gráficos e o conferidor antes de ligar o agente;
- ver o resultado esperado em dados/exemplos/projeto/;
- mostrar a trava de números: troque um número de um achado por outro e rode de novo.

Uso:
    python montar_exemplos.py saida_exemplos
"""

import json
import sys
from pathlib import Path

import apresentacao as ap
import graficos_feira as gf
import graficos_relatorio as gr

TITULOS_MENSAL = {
    "indicadores": "Outubro entregou 98,6% e abriu 52,6% das mensagens",
    "comparacao": "A abertura subiu 6,9 pontos percentuais sobre setembro, com 21,0% menos envios",
    "publico": "Credenciamento e pré-credenciado lideram o clique entre os públicos grandes",
    "grafico_clique": "Expositor tem o maior clique, mas sobre só 162 entregues",
    "grafico_abertura": "Prospecção puxou a alta da abertura",
}
ACHADOS_MENSAL = [
    {"titulo": "Abertura em alta", "fato": "A abertura passou de 45,7% em setembro para 52,6% em outubro.",
     "proximo_passo": "Manter a frequência de disparos de prospecção em novembro e acompanhar se a alta se sustenta."},
    {"titulo": "Reativação baixa", "fato": "A reativação abriu 12,6%, a menor abertura entre os públicos.",
     "proximo_passo": "Testar outro assunto na reativação, com grupo de controle."},
    {"titulo": "Clique atípico", "fato": "Um reenvio de credenciamento teve clique de 20,1%, acima do limite de 15%.",
     "proximo_passo": "Confirmar no CRM se houve clique automático antes de usar o número em comparações."},
]
TITULOS_POS_FEIRA = {
    "funil": "218 das 560 pessoas credenciadas visitaram a feira: 38,9%",
    "grafico_funil": "Do credenciamento ao evento paralelo, 44 pessoas chegaram ao fim do funil",
    "whatsapp": "Os três disparos de WhatsApp entregaram entre 94,1% e 96,7% dos contatos",
    "whatsapp_visitacao": "Quem recebeu WhatsApp visitou menos (36,8%) que quem não recebeu (47,7%), sem medir efeito",
    "email": "O e-mail da campanha abriu 52,6% em outubro, contra 45,7% em setembro",
}
ACHADOS_POS_FEIRA = [
    {"titulo": "Menos de quatro em cada dez visitaram",
     "fato": "Visitaram a feira 218 das 560 pessoas credenciadas, uma visitação de 38,9%.",
     "proximo_passo": "Na próxima edição, concentrar lembretes na semana da feira e medir a visitação por canal "
                      "de credenciamento."},
    {"titulo": "WhatsApp sem efeito medido",
     "fato": "Quem recebeu WhatsApp visitou 36,8%; quem não recebeu, 47,7%. Os grupos não foram sorteados.",
     "proximo_passo": "Sortear um grupo de controle na campanha de WhatsApp da próxima edição para medir o efeito."},
    {"titulo": "Lembrete com mais falhas",
     "fato": "O lembrete da véspera entregou 94,1%, com 101 tentativas com erro.",
     "proximo_passo": "Limpar os telefones inválidos antes do lembrete e enviar mais cedo no dia."},
]


def montar(pasta_saida, pasta_dados=Path("dados_n4")):
    pasta_saida = Path(pasta_saida)
    imagens = gr.gerar_graficos(pasta_dados / "desempenho_email_outubro.csv",
                                pasta_dados / "desempenho_email_setembro.csv", pasta_saida / "mensal" / "graficos")
    mensal = ap.relatorio_mensal("2026-10", "2026-09", ACHADOS_MENSAL, TITULOS_MENSAL,
                                 {"clique": imagens[0], "abertura": imagens[1]},
                                 pasta_saida / "mensal" / "relatorio_email_2026-10.pptx")
    imagens = gf.gerar_graficos_feira(pasta_saida / "pos_feira" / "graficos")
    pos_feira = ap.report_pos_feira(ACHADOS_POS_FEIRA, TITULOS_POS_FEIRA, {"funil": imagens[0]},
                                    pasta_saida / "pos_feira" / "report_pos_feira.pptx")
    return {"mensal": mensal, "pos_feira": pos_feira}


if __name__ == "__main__":
    print(json.dumps(montar(sys.argv[1] if len(sys.argv) > 1 else "saida_exemplos"), ensure_ascii=False, indent=2))

"""Mostra a retomada funcionando sem chamar a API: o processamento é simulado e falha de propósito.

Material do módulo 3.6. Executado e testado. Não gasta créditos.

Uso:
    python falhas_simuladas.py
"""

from pathlib import Path

import retomada

ARQ_PROGRESSO = Path("progresso_simulado.jsonl")


class FalhaTemporaria(Exception):
    """Faz o papel de um erro 429 ou 529 da API."""


class Simulador:
    """Processa itens de mentira. Cada item custa US$ 0,01 e alguns falham de propósito."""

    def __init__(self):
        self.chamadas = 0
        self.tentativas_do_item_3 = 0
        self.ja_interrompeu = False

    def processar(self, dados):
        self.chamadas += 1
        if dados == "item 3":                      # falha duas vezes e funciona na terceira
            self.tentativas_do_item_3 += 1
            if self.tentativas_do_item_3 <= 2:
                raise FalhaTemporaria("limite de requisições (simulado)")
        if dados == "item 5":                      # pedido inválido: repetir não resolve
            raise ValueError("pedido inválido (simulado)")
        if dados == "item 7":                      # recusa: é um resultado, não um erro
            return {"situacao": "recusado", "custo": 0.01}
        if dados == "item 9" and not self.ja_interrompeu:
            self.ja_interrompeu = True             # faz o papel do Ctrl+C no meio da execução
            raise KeyboardInterrupt
        return {"situacao": "ok", "resultado": {"texto": dados.upper()}, "custo": 0.01}


def sem_esperar(segundos):
    """Na simulação, a espera é só anunciada."""


if __name__ == "__main__":
    ARQ_PROGRESSO.unlink(missing_ok=True)
    itens = [(f"I{numero:02d}", f"item {numero}") for numero in range(1, 13)]
    simulador = Simulador()
    opcoes = dict(temporarios=(FalhaTemporaria,), dormir=sem_esperar)

    print("--- Primeira execução: é interrompida no item 9 ---")
    resumo = retomada.processar_com_retomada(itens, simulador.processar, ARQ_PROGRESSO, **opcoes)
    print(retomada.texto_do_resumo(resumo))

    print("\n--- Segunda execução: continua de onde parou, com teto de custo de US$ 0,10 ---")
    antes = simulador.chamadas
    resumo = retomada.processar_com_retomada(itens, simulador.processar, ARQ_PROGRESSO, teto_de_custo=0.10, **opcoes)
    print(retomada.texto_do_resumo(resumo))
    print(f"Chamadas feitas nesta execução: {simulador.chamadas - antes}")

    print("\n--- Terceira execução: sem teto, termina o que faltava ---")
    antes = simulador.chamadas
    resumo = retomada.processar_com_retomada(itens, simulador.processar, ARQ_PROGRESSO, **opcoes)
    print(retomada.texto_do_resumo(resumo))
    print(f"Chamadas feitas nesta execução: {simulador.chamadas - antes}")

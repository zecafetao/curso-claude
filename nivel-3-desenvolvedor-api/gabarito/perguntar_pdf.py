"""Perguntas e respostas sobre um PDF, com a página de cada afirmação.

Solução de referência do módulo 3.2. As chamadas à API não foram executadas com uma chave real.

Uso:
    python perguntar_pdf.py dados_n3/relatorio_mercado_embalagens.pdf "Qual foi o valor da produção em 2025?"
"""

import base64
import sys
from pathlib import Path

import claude_util as cu

SISTEMA = (
    "Responda só com base no documento fornecido e cite os trechos que sustentam cada afirmação. "
    "Se a informação não estiver no documento, diga que ela não consta. Respostas curtas."
)


def bloco_pdf(caminho, titulo):
    """Monta o bloco de conteúdo de um PDF enviado dentro da requisição, com citações ligadas."""
    dados = base64.standard_b64encode(Path(caminho).read_bytes()).decode("utf-8")
    return {
        "type": "document",
        "source": {"type": "base64", "media_type": "application/pdf", "data": dados},
        "title": titulo,
        "citations": {"enabled": True},
    }


def bloco_pdf_enviado(cliente, caminho, titulo):
    """Alternativa: envia o PDF uma vez pela Files API e devolve (bloco, identificador do arquivo)."""
    arquivo = cliente.files.upload(file=Path(caminho))
    bloco = {
        "type": "document",
        "source": {"type": "file", "file_id": arquivo.id},
        "title": titulo,
        "citations": {"enabled": True},
    }
    return bloco, arquivo.id


def perguntar(cliente, bloco, pergunta):
    """Faz uma pergunta sobre o documento. O documento vem antes da pergunta."""
    mensagens = [{"role": "user", "content": [bloco, {"type": "text", "text": pergunta}]}]
    return cu.chamar(cliente, mensagens, sistema=SISTEMA, esforco="low")


def texto_e_paginas(resposta):
    """Devolve (texto, lista ordenada das páginas citadas) de uma resposta com citações."""
    partes, paginas = [], set()
    for bloco in resposta.content:
        if bloco.type != "text":
            continue
        partes.append(bloco.text)
        for citacao in bloco.citations or []:
            if citacao.type == "page_location":
                # Pela documentação, a página final é exclusiva: uma citação da página 2 vem como
                # início 2 e fim 3. O max garante ao menos a página inicial em qualquer caso.
                fim = max(citacao.end_page_number, citacao.start_page_number + 1)
                paginas.update(range(citacao.start_page_number, fim))
    return "".join(partes), sorted(paginas)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Uso: python perguntar_pdf.py arquivo.pdf "pergunta"')
        sys.exit(1)
    cliente = cu.criar_cliente()
    resposta = perguntar(cliente, bloco_pdf(sys.argv[1], Path(sys.argv[1]).stem), sys.argv[2])
    if resposta.stop_reason == "refusal":
        print("O pedido foi recusado.")
        sys.exit(1)
    texto, paginas = texto_e_paginas(resposta)
    print(texto)
    print(f"Páginas citadas: {paginas or 'nenhuma'}")
    print(f"Custo: US$ {cu.custo_em_dolares(resposta.usage):.4f}")

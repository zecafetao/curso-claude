"""Lê os valores de um gráfico em imagem.

Solução de referência do módulo 3.2. As chamadas à API não foram executadas com uma chave real.

Uso:
    python ler_grafico.py dados_n3/grafico_clique_por_publico.png
"""

import base64
import sys
from pathlib import Path

import claude_util as cu

TIPOS = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}


def bloco_imagem(caminho):
    """Monta o bloco de conteúdo de uma imagem enviada dentro da requisição."""
    caminho = Path(caminho)
    dados = base64.standard_b64encode(caminho.read_bytes()).decode("utf-8")
    tipo = TIPOS[caminho.suffix.lower()]
    return {"type": "image", "source": {"type": "base64", "media_type": tipo, "data": dados}}


if __name__ == "__main__":
    cliente = cu.criar_cliente()
    pedido = (
        "Transcreva os valores deste gráfico em uma tabela com as colunas público e taxa de clique. "
        "Copie os números como aparecem. Se algum valor não estiver legível, escreva 'ilegível'."
    )
    mensagens = [{"role": "user", "content": [bloco_imagem(sys.argv[1]), {"type": "text", "text": pedido}]}]
    resposta = cu.chamar(cliente, mensagens, esforco="low")
    print(cu.texto_da_resposta(resposta))
    print(f"Custo: US$ {cu.custo_em_dolares(resposta.usage):.4f}")

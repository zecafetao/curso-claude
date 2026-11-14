"""Extrai contatos de textos livres para um formato fixo, com saída estruturada.

Solução de referência do módulo 3.3. As chamadas à API não foram executadas com uma chave real.

Uso:
    python extrair_contatos.py dados_n3/contatos_texto_livre.csv extraidos.csv
"""

import csv
import json
import sys

import claude_util as cu

CAMPOS = ["nome", "sobrenome", "email", "telefone", "empresa", "cargo"]

ESQUEMA_CONTATO = {
    "type": "object",
    "properties": {campo: {"type": "string"} for campo in CAMPOS},
    "required": CAMPOS,
    "additionalProperties": False,
}
FORMATO_CONTATO = {"type": "json_schema", "schema": ESQUEMA_CONTATO}

SISTEMA = """Você extrai dados de contato de mensagens recebidas por uma equipe de CRM. O resultado é
conferido por um programa e importado em um sistema, então cada campo deve trazer só o dado pedido.

Regras:
- Copie os valores como aparecem no texto. A padronização de telefone e de maiúsculas é feita depois, por código.
- nome é o primeiro nome; sobrenome é o restante do nome da pessoa.
- empresa é o nome da empresa sem o tipo societário (Ltda, S.A.).
- Se houver mais de um telefone, use o celular.
- Se o e-mail estiver escrito por extenso ("ponto", "arroba"), converta para o formato de e-mail.
- Se o texto citar mais de uma pessoa, extraia o contato principal, que é o primeiro apresentado.
- Quando um dado não estiver no texto, use texto vazio. Não deduza nem complete dados ausentes."""


def extrair(cliente, texto):
    """Devolve (dicionário com os campos, resposta). O dicionário é None se não houve resultado utilizável."""
    mensagens = [{"role": "user", "content": f"<mensagem>\n{texto}\n</mensagem>"}]
    resposta = cu.chamar(cliente, mensagens, sistema=SISTEMA, esforco="low", max_tokens=4000,
                         formato=FORMATO_CONTATO)
    if resposta.stop_reason != "end_turn":
        return None, resposta     # recusa ou resposta cortada: o JSON pode não existir ou estar incompleto
    return json.loads(cu.texto_da_resposta(resposta)), resposta


if __name__ == "__main__":
    entrada, saida = sys.argv[1], sys.argv[2]
    with open(entrada, encoding="utf-8", newline="") as arquivo:
        mensagens_recebidas = list(csv.DictReader(arquivo, delimiter=";"))

    cliente = cu.criar_cliente()
    total = cu.novo_total()
    with open(saida, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["id", "situacao"] + CAMPOS, delimiter=";")
        escritor.writeheader()
        for posicao, linha in enumerate(mensagens_recebidas, start=1):
            contato, resposta = extrair(cliente, linha["texto"])
            cu.somar_uso(total, resposta.usage)
            if contato is None:
                escritor.writerow({"id": linha["id"], "situacao": resposta.stop_reason})
            else:
                escritor.writerow({"id": linha["id"], "situacao": "ok", **contato})
            print(f"{posicao}/{len(mensagens_recebidas)} {linha['id']}: {resposta.stop_reason}")
    print(cu.resumo_do_total(total))

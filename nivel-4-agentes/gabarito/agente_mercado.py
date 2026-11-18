"""Agente de estudo de mercado: busca, lê e resume com fontes, para um setor e uma região.

Solução de referência do módulo 4.2. As chamadas à API não foram executadas com uma chave real.
As ferramentas locais (perfil dos expositores e entrega do estudo) foram executadas e testadas.

Uso:
    python agente_mercado.py "indústria de embalagens" "região Sul"

O estudo alimenta a parte de mercado do estudo de perfil de expositores: quem expõe (dados da feira)
e o universo de empresas parecidas no mercado (fontes públicas).
"""

import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

from anthropic import beta_tool

import claude_util as cu
import perfil_expositores as pe

ARQ_EXPOSITORES = Path("dados_n4/empresas_expositoras.csv")
PASTA_SAIDA = Path("saida_estudos")
FONTE_INTERNA = "interno:perfil_expositores"     # endereço da fonte interna, aceito na conferência

SISTEMA = """Você faz estudos de mercado curtos para uma agência que atende organizadores de feiras de negócios.

Objetivo do estudo: dimensionar o universo de empresas parecidas com os expositores da feira, no setor e na
região pedidos, para orientar a prospecção de novos expositores.

Como trabalhar:
1. Comece pelo perfil dos expositores atuais (ferramenta perfil_expositores): ele diz quais setores e portes
   procurar no mercado.
2. Busque fontes públicas e confiáveis: órgãos de estatística, associações setoriais, estudos publicados.
   Leia a página antes de usar um número; o resumo da busca não basta.
3. Cada número do estudo tem uma fonte, com o nome e o endereço. Os números do perfil dos expositores têm
   como fonte a base de expositores da feira, com o endereço interno:perfil_expositores. Quando duas fontes
   divergirem, apresente as duas. Quando não achar um dado, registre a lacuna em vez de estimar.
4. Pare quando tiver o suficiente para as quatro seções, ou quando novas buscas não trouxerem informação
   nova. Termine chamando entregar_estudo.

Seções do estudo: Perfil dos expositores atuais; Tamanho do mercado; Universo de empresas parecidas;
Lacunas e próximos passos. Cite as fontes no texto com o número entre colchetes, como [1]."""


@beta_tool
def perfil_expositores() -> str:
    """Perfil dos expositores atuais da feira: participação por setor, porte, região e faixa de faturamento.

    Use no início do estudo. Devolve só contagens e percentuais.
    """
    base = pe.ler_empresas(ARQ_EXPOSITORES)
    perfil = {"empresas": len(base)}
    for coluna in ["setor", "porte", "regiao", "faixa_faturamento"]:
        tabela = pe.participacao(base, coluna)
        perfil[coluna] = {str(valor): {"empresas": int(linha.empresas), "participacao": float(linha.participacao)}
                          for valor, linha in tabela.iterrows()}
    return json.dumps(perfil, ensure_ascii=False)


def montar_markdown(titulo, secoes, fontes):
    linhas = [f"# {titulo}", "", f"Estudo gerado em {date.today():%d/%m/%Y}. Rascunho para revisão.", ""]
    for secao in secoes:
        linhas += [f"## {secao['titulo']}", "", secao["texto"], ""]
    linhas += ["## Fontes", ""]
    linhas += [f"{i}. {fonte['titulo']}. {fonte['url']}" for i, fonte in enumerate(fontes, start=1)]
    return "\n".join(linhas) + "\n"


def conferir_estudo(secoes, fontes):
    """Devolve a lista de problemas do estudo. Lista vazia significa pronto para gravar."""
    problemas = []
    if len(secoes) != 4 or any(not s.get("titulo") or not s.get("texto") for s in secoes):
        problemas.append("O estudo precisa das quatro seções, cada uma com titulo e texto.")
    if not fontes:
        problemas.append("Nenhuma fonte informada.")
    for numero, fonte in enumerate(fontes, start=1):
        url = str(fonte.get("url", ""))
        if not (url.startswith(("http://", "https://")) or url == FONTE_INTERNA):
            problemas.append(f"A fonte [{numero}] não tem endereço válido: use o endereço da página lida "
                             f"ou {FONTE_INTERNA} para a base de expositores.")
    citadas = {int(n) for s in secoes for n in re.findall(r"\[(\d+)\]", s.get("texto", ""))}
    sem_fonte = sorted(n for n in citadas if n < 1 or n > len(fontes))
    if sem_fonte:
        problemas.append(f"Citações sem fonte na lista: {sem_fonte}.")
    nao_citadas = sorted(set(range(1, len(fontes) + 1)) - citadas)
    if nao_citadas:
        problemas.append(f"Fontes listadas e não citadas no texto: {nao_citadas}.")
    return problemas


def ler_estudo(texto):
    """Separa as seções e a lista de fontes de um estudo em Markdown.

    Serve para conferir estudos gravados sem a ferramenta de entrega, como os do Agent SDK e do
    Managed Agents (módulo 4.5). As seções são os títulos "## "; as fontes, a lista numerada da seção Fontes.
    """
    secoes, fontes, atual, em_fontes = [], [], None, False
    for linha in texto.splitlines():
        if linha.startswith("## "):
            titulo = linha[3:].strip()
            em_fontes = titulo.lower() == "fontes"
            atual = None if em_fontes else {"titulo": titulo, "texto": ""}
            if atual is not None:
                secoes.append(atual)
        elif em_fontes:
            item = re.match(r"^\s*\d+\.\s+(.*)$", linha)
            if item:
                endereco = re.search(r"(https?://\S+|interno:\S+)", item.group(1))
                fontes.append({"titulo": item.group(1),
                               "url": endereco.group(1).rstrip("`).,;") if endereco else ""})
        elif atual is not None:
            atual["texto"] += linha + "\n"
    return secoes, fontes


def conferir_arquivo(caminho):
    """Aplica a conferência do estudo a um arquivo Markdown já gravado. Lista vazia: nenhum problema."""
    secoes, fontes = ler_estudo(Path(caminho).read_text(encoding="utf-8"))
    return conferir_estudo(secoes, fontes)


def ferramenta_de_entrega(setor, regiao):
    """Cria a ferramenta que grava o estudo. Ela é o critério de parada do agente."""
    entregues = []

    @beta_tool
    def entregar_estudo(titulo: str, secoes: list[dict[str, str]], fontes: list[dict[str, str]]) -> str:
        """Grava o estudo final em Markdown. Use uma vez, no fim, quando as quatro seções estiverem prontas.

        Args:
            titulo: Título do estudo.
            secoes: As quatro seções, cada uma com as chaves titulo e texto.
            fontes: As fontes citadas, na ordem dos números entre colchetes, cada uma com titulo e url.
        """
        problemas = conferir_estudo(secoes, fontes)
        if problemas:
            return json.dumps({"gravado": False, "problemas": problemas}, ensure_ascii=False)
        PASTA_SAIDA.mkdir(exist_ok=True)
        sem_acento = unicodedata.normalize("NFKD", f"estudo {setor} {regiao}".lower()).encode("ascii", "ignore").decode()
        nome = re.sub(r"[^a-z0-9]+", "_", sem_acento).strip("_") + ".md"
        caminho = PASTA_SAIDA / nome
        caminho.write_text(montar_markdown(titulo, secoes, fontes), encoding="utf-8")
        entregues.append(str(caminho))
        return json.dumps({"gravado": True, "arquivo": str(caminho)}, ensure_ascii=False)

    return entregar_estudo, entregues


def estudar(cliente, setor, regiao, mostrar=print):
    entregar_estudo, entregues = ferramenta_de_entrega(setor, regiao)
    ferramentas = [
        perfil_expositores,
        entregar_estudo,
        {"type": "web_search_20260209", "name": "web_search", "max_uses": 8,
         "user_location": {"type": "approximate", "country": "BR"}},
        {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 6, "max_content_tokens": 30000},
    ]
    executor = cliente.beta.messages.tool_runner(
        model=cu.MODELO, max_tokens=16000, system=SISTEMA, tools=ferramentas,
        messages=[{"role": "user", "content": f"Setor: {setor}. Região: {regiao}."}],
        output_config={"effort": "medium"}, max_iterations=20, thread=False, **cu.opcoes_de_fallback(),
    )
    total, ultima = cu.novo_total(), None
    for mensagem in executor:
        cu.somar_uso(total, mensagem.usage)
        ultima = mensagem
        for bloco in mensagem.content:
            if bloco.type in ("tool_use", "server_tool_use"):
                mostrar(f"  [{bloco.type}] {bloco.name} {json.dumps(bloco.input, ensure_ascii=False)[:90]}")
        if entregues:            # critério de parada: o estudo foi gravado
            break
    texto = None if ultima is None else cu.texto_da_resposta(ultima)
    return entregues, texto, total


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Uso: python agente_mercado.py "setor" "região"')
        sys.exit(1)
    entregues, texto, total = estudar(cu.criar_cliente(), sys.argv[1], sys.argv[2])
    print(f"Arquivo: {entregues[0] if entregues else 'nenhum estudo entregue'}")
    print(cu.resumo_do_total(total))

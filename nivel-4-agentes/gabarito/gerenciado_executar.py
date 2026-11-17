"""Roda uma sessão do agente de estudo de mercado no Managed Agents e baixa o arquivo gerado.

Solução de referência do módulo 4.5. Não foi executado com uma chave real: os nomes de métodos e
eventos foram conferidos contra a versão 2.8 do SDK anthropic e a documentação de novembro de 2026.

Uso:
    python gerenciado_executar.py "indústria de embalagens" "região Sul"

Pré-requisito: python gerenciado_configurar.py (uma vez).
"""

import json
import sys
import time
from pathlib import Path

import anthropic

ARQUIVO_IDS = Path("gerenciado.json")
ARQ_EXPOSITORES = Path("dados_n4/empresas_expositoras.csv")
PASTA_SAIDA = Path("saida_gerenciado")

RUBRICA = """Critérios do estudo (rascunho inicial; ajuste ao seu padrão)
- O arquivo é /mnt/session/outputs/estudo.md, com as seções Perfil dos expositores atuais, Tamanho do mercado,
  Universo de empresas parecidas, Lacunas e próximos passos e Fontes.
- O perfil dos expositores traz os percentuais calculados a partir do arquivo de expositores.
- Todo número do estudo tem uma fonte numerada, e toda fonte numerada é citada no texto.
- As lacunas de dados estão registradas, sem estimativas apresentadas como fato.
- Não há texto provisório nem seção vazia."""


def resultado_final(evento):
    """Imprime o que interessa de cada evento da sessão."""
    if evento.type == "agent.message":
        for bloco in evento.content:
            if bloco.type == "text":
                print(bloco.text[:200])


def executar(cliente, setor, regiao):
    ids = json.loads(ARQUIVO_IDS.read_text(encoding="utf-8"))
    with open(ARQ_EXPOSITORES, "rb") as arquivo:
        enviado = cliente.files.upload(file=arquivo)

    sessao = cliente.beta.sessions.create(
        agent={"type": "agent", "id": ids["agent_id"], "version": ids["agent_version"]},
        environment_id=ids["environment_id"],
        title=f"Estudo de mercado: {setor}, {regiao}",
        resources=[{"type": "file", "file_id": enviado.id, "mount_path": "/mnt/session/dados/empresas_expositoras.csv"}],
        budget={"type": "limit", "max_list_cost": {"amount": "300", "currency": "USD"}},   # 300 centavos: US$ 3
    )
    print(f"Sessão {sessao.id}. Acompanhe também no Console.")

    with cliente.beta.sessions.events.stream(session_id=sessao.id) as fluxo:
        # O fluxo é aberto antes do envio, para não perder os primeiros eventos.
        cliente.beta.sessions.events.send(session_id=sessao.id, events=[{
            "type": "user.define_outcome",
            "description": f"Estudo de mercado do setor {setor} na {regiao}, em /mnt/session/outputs/estudo.md",
            "rubric": {"type": "text", "content": RUBRICA},
            "max_iterations": 3,
        }])
        for evento in fluxo:
            resultado_final(evento)
            if evento.type in ("agent.tool_use", "agent.mcp_tool_use") and evento.evaluated_permission == "ask":
                # Ninguém está acompanhando: chamadas que pedem aprovação são negadas.
                cliente.beta.sessions.events.send(session_id=sessao.id, events=[
                    {"type": "user.tool_confirmation", "tool_use_id": evento.id, "result": "deny"}])
            elif evento.type == "session.status_idle" and evento.stop_reason.type != "requires_action":
                break
            elif evento.type == "session.status_terminated":
                break

    PASTA_SAIDA.mkdir(exist_ok=True)
    baixados = []
    for tentativa in range(3):                 # os arquivos aparecem na listagem alguns segundos depois
        arquivos = cliente.beta.files.list(scope_id=sessao.id, betas=["managed-agents-2026-04-01"])
        for item in arquivos.data:
            destino = PASTA_SAIDA / item.filename
            cliente.beta.files.download(item.id).write_to_file(destino)
            baixados.append(destino)
        if baixados:
            break
        time.sleep(3)
    sessao = cliente.beta.sessions.retrieve(sessao.id)
    return baixados, sessao


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Uso: python gerenciado_executar.py "setor" "região"')
        sys.exit(1)
    baixados, sessao = executar(anthropic.Anthropic(), sys.argv[1], sys.argv[2])
    print(f"Arquivos baixados: {[str(b) for b in baixados] or 'nenhum'}")
    print(f"Situação da sessão: {sessao.status} | uso: {sessao.usage}")

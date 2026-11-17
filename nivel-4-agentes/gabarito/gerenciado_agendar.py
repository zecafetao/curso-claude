"""Agenda o agente de estudo de mercado para rodar todo mês no Managed Agents.

Solução de referência do módulo 4.5. Não foi executado com uma chave real: os nomes de métodos e
parâmetros foram conferidos contra a versão 2.8 do SDK anthropic e a documentação de novembro de 2026.

Uso:
    python gerenciado_agendar.py criar       # cria o agendamento e mostra as próximas execuções
    python gerenciado_agendar.py testar      # dispara uma execução agora, fora do horário
    python gerenciado_agendar.py pausar
    python gerenciado_agendar.py execucoes   # lista as execuções e os erros

Cada execução cria uma sessão. Os arquivos gerados são baixados depois, como no gerenciado_executar.py.
"""

import json
import sys
from pathlib import Path

import anthropic

import gerenciado_executar as ge

ARQUIVO_IDS = Path("gerenciado.json")


def criar(cliente, setor="indústria de embalagens", regiao="região Sul"):
    ids = json.loads(ARQUIVO_IDS.read_text(encoding="utf-8"))
    with open(ge.ARQ_EXPOSITORES, "rb") as arquivo:
        enviado = cliente.files.upload(file=arquivo)
    agendamento = cliente.beta.deployments.create(
        name="Estudo de mercado mensal",
        agent=ids["agent_id"],
        environment_id=ids["environment_id"],
        resources=[{"type": "file", "file_id": enviado.id, "mount_path": "/mnt/session/dados/empresas_expositoras.csv"}],
        initial_events=[{
            "type": "user.define_outcome",
            "description": f"Estudo de mercado do setor {setor} na {regiao}, em /mnt/session/outputs/estudo.md",
            "rubric": {"type": "text", "content": ge.RUBRICA},
            "max_iterations": 3,
        }],
        schedule={"type": "cron", "expression": "17 9 1 * *", "timezone": "America/Sao_Paulo"},  # dia 1, 9h17
        budget={"type": "limit", "max_list_cost": {"amount": "300", "currency": "USD"}},
    )
    ids["deployment_id"] = agendamento.id
    ARQUIVO_IDS.write_text(json.dumps(ids, indent=2), encoding="utf-8")
    print(f"Agendamento {agendamento.id}: próximas execuções {agendamento.schedule.upcoming_runs_at}")


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else ""
    cliente = anthropic.Anthropic()
    if comando == "criar":
        criar(cliente)
    elif comando in ("testar", "pausar", "execucoes"):
        id_agendamento = json.loads(ARQUIVO_IDS.read_text(encoding="utf-8"))["deployment_id"]
        if comando == "testar":
            print(cliente.beta.deployments.run(id_agendamento))
        elif comando == "pausar":
            print(cliente.beta.deployments.pause(id_agendamento))
        else:
            for execucao in cliente.beta.deployment_runs.list(deployment_id=id_agendamento):
                print(execucao.created_at, execucao.session_id or execucao.error.type)
    else:
        print("Uso: python gerenciado_agendar.py criar | testar | pausar | execucoes")
        sys.exit(1)

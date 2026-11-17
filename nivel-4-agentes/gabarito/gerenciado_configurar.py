"""Cria, uma única vez, o ambiente e o agente do estudo de mercado no Managed Agents.

Solução de referência do módulo 4.5. Não foi executado com uma chave real: os nomes de métodos e
parâmetros foram conferidos contra a versão 2.8 do SDK anthropic e a documentação de novembro de 2026.
O Managed Agents está em beta; o SDK envia o cabeçalho de beta sozinho.

Uso:
    python gerenciado_configurar.py

Grava os identificadores em gerenciado.json. Rode de novo só para mudar o agente: a mudança cria uma
nova versão, e as sessões já criadas continuam na versão delas.
"""

import json
from pathlib import Path

import anthropic

import agente_mercado

ARQUIVO_IDS = Path("gerenciado.json")

# Sites que o agente pode buscar e ler. Com a rede "limited", a busca e a leitura de páginas só alcançam
# estes endereços: a lista é uma decisão de fontes, e não só de segurança. Ajuste à sua pesquisa.
SITES_PERMITIDOS = ["www.ibge.gov.br", "sidra.ibge.gov.br", "www.gov.br", "www.abre.org.br"]

INSTRUCOES = agente_mercado.SISTEMA.replace(
    "Comece pelo perfil dos expositores atuais (ferramenta perfil_expositores)",
    "Comece pelo perfil dos expositores atuais, calculado com Python a partir de "
    "/mnt/session/dados/empresas_expositoras.csv",
).replace(
    "Termine chamando entregar_estudo.",
    "Termine gravando o estudo em /mnt/session/outputs/estudo.md, com uma seção Fontes numerada no fim.",
)


def configurar(cliente):
    ids = json.loads(ARQUIVO_IDS.read_text(encoding="utf-8")) if ARQUIVO_IDS.exists() else {}

    if "environment_id" not in ids:
        ambiente = cliente.beta.environments.create(
            name="estudos-de-mercado",
            config={"type": "cloud", "networking": {
                "type": "limited",
                "allowed_hosts": SITES_PERMITIDOS,
                "allow_package_managers": True,      # para instalar o pandas, se o contêiner não tiver
            }},
        )
        ids["environment_id"] = ambiente.id

    ferramentas = [{
        "type": "agent_toolset_20260401",
        "default_config": {"enabled": True, "permission_policy": {"type": "auto"}},
        "configs": [{"name": "web_search", "enabled": True}, {"name": "web_fetch", "enabled": True}],
    }]
    if "agent_id" not in ids:
        agente = cliente.beta.agents.create(name="Estudo de mercado", model="claude-opus-5-5",
                                            system=INSTRUCOES, tools=ferramentas)
    else:                                         # já existe: atualiza, o que cria uma nova versão
        atual = cliente.beta.agents.retrieve(ids["agent_id"])
        agente = cliente.beta.agents.update(ids["agent_id"], version=atual.version, system=INSTRUCOES,
                                            tools=ferramentas)
    ids["agent_id"], ids["agent_version"] = agente.id, agente.version

    ARQUIVO_IDS.write_text(json.dumps(ids, indent=2), encoding="utf-8")
    return ids


if __name__ == "__main__":
    print(configurar(anthropic.Anthropic()))

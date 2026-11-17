"""Hook PreToolUse: bloqueia qualquer ferramenta que toque em dados_reais/ ou no arquivo .env.

O Claude Code envia, pela entrada padrão, um JSON com tool_name e tool_input. Sair com o código 2
bloqueia a chamada, e o texto escrito na saída de erro é mostrado ao Claude como motivo.

É uma segunda camada: as regras deny do settings.json já negam a leitura. O hook cobre também
comandos do terminal, como "cat dados_reais/base.csv", que uma regra de Read não alcança.
"""

import json
import sys

PROTEGIDOS = ("dados_reais", ".env")

entrada = json.load(sys.stdin)
ferramenta = entrada.get("tool_name", "")
parametros = entrada.get("tool_input", {})

# Junta todos os textos da chamada: caminho do arquivo, padrão de busca, comando do terminal.
alvo = " ".join(str(valor) for valor in parametros.values())

if any(protegido in alvo for protegido in PROTEGIDOS):
    print(
        f"Bloqueado pelo hook proteger_dados: a ferramenta {ferramenta} tentou acessar {PROTEGIDOS}. "
        "Bases reais são tratadas só pelos scripts. Peça à pessoa que rode o script.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)

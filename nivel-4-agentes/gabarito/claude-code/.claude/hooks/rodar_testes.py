"""Hook PostToolUse: depois de cada edição de arquivo .py, roda os testes.

Se algum teste falhar, sai com o código 2, e o fim do relatório do pytest é mostrado ao Claude,
que corrige antes de continuar. Edições em arquivos que não são .py não rodam os testes.
"""

import json
import subprocess
import sys

entrada = json.load(sys.stdin)
arquivo = str(entrada.get("tool_input", {}).get("file_path", ""))
if not arquivo.endswith(".py"):
    sys.exit(0)

resultado = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x"], capture_output=True, text=True,
                           cwd=entrada.get("cwd") or None, timeout=120)
if resultado.returncode not in (0, 5):          # 5: nenhum teste encontrado
    linhas = (resultado.stdout + resultado.stderr).strip().splitlines()
    print("Os testes falharam depois da edição:\n" + "\n".join(linhas[-25:]), file=sys.stderr)
    sys.exit(2)
sys.exit(0)

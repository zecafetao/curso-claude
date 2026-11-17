---
name: tratar-base
description: Trata uma base bruta de contatos com o tratar_base.py e resume o resultado para importação no CRM.
disable-model-invocation: true
argument-hint: <base_bruta.csv> <descadastrados.xlsx>
allowed-tools: Bash(python tratar_base.py *) Read
---

Trate a base com o script do projeto e resuma o resultado.

1. Rode `python tratar_base.py $0 $1 saida_tratamento`.
2. Leia o `resumo.txt` da pasta de saída. Não abra o `importar.csv` nem o `rejeitados.csv`: eles têm dados pessoais.
3. Responda com:
   - linhas lidas, para importar e rejeitadas, com os motivos;
   - os avisos, por tipo;
   - um alerta se as rejeições passarem de 30% das linhas, porque isso costuma indicar um problema na exportação do cliente.
4. Se o script falhar, mostre a mensagem de erro e diga qual coluna ou arquivo parece ser a causa. Não edite o script nesta tarefa.

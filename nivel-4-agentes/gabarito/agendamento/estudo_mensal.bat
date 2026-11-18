@echo off
rem Roda o estudo de mercado e guarda o registro da execução. Material do módulo 4.5.
rem Coloque este arquivo na pasta dos scripts, ao lado do .venv, e aponte o Agendador de Tarefas para ele.
rem A chave da API vem da variável de ambiente ANTHROPIC_API_KEY, gravada com setx (módulo 3.1).
chcp 65001 > nul
set PYTHONUTF8=1
cd /d "%~dp0"
if not exist logs mkdir logs
echo ==== %date% %time% >> logs\estudo_mensal.log
".venv\Scripts\python.exe" agente_mercado.py "indústria de embalagens" "região Sul" >> logs\estudo_mensal.log 2>&1

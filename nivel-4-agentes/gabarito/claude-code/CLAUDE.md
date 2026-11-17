# Tratamento de bases para o CRM

Scripts em Python que tratam bases de contatos para importação no CRM e calculam os indicadores dos relatórios de campanha.

## Comandos

- Testes: `python -m pytest -q`
- Tratamento de uma base: `python tratar_base.py <base_bruta.csv> <descadastrados.xlsx> <pasta_de_saida>`
- Indicadores do relatório mensal: `python relatorio_mensal.py <mes_atual.csv> <mes_anterior.csv>`

## Organização

- `validacao.py`: uma função por regra de padronização. Toda regra nova tem teste em `test_validacao.py`.
- `tratar_base.py`: o fluxo completo de tratamento. Não contém regras de padronização, só as chama.
- `dados/`: dados fictícios dos exercícios. Bases de clientes reais nunca ficam nesta pasta.

## Regras

- O layout de importação está em @dados_n3/layout_importacao_crm.md. Uma mudança de regra que contrarie o layout precisa de confirmação.
- Mudanças em `validacao.py` vêm com teste. Rode os testes antes de dizer que terminou.
- Não leia nem copie arquivos de `dados_reais/`. As bases reais são tratadas só pelos scripts, sem passar pela conversa.
- Mensagens de commit em português, no imperativo: "Acrescenta regra de UF", "Corrige telefone de 8 dígitos".

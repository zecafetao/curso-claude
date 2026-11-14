# Projeto do Nível 3 — Serviço de tratamento de bases com o Claude

**Carga:** 6 h

## Objetivo

Construir um serviço de linha de comando que recebe uma base bruta de contatos, em CSV ou Excel, e devolve o arquivo pronto para importação no CRM, com a área de cada contato classificada pelo Claude, o relatório de rejeições e o custo do processamento.

O projeto reúne os seis módulos: chamada à API (3.1), saída estruturada com lista fechada (3.3), divisão de trabalho entre código e modelo (3.3 e 3.4), cache e redução de chamadas (3.5) e retomada com teto de custo (3.6).

## O problema

O projeto da Ponte terminou com um limite declarado: o cargo `Brand Manager` caiu em `Outros`, porque a tabela de palavras-chave não conhece o termo. Na base deste projeto, o problema está em escala. Os cargos chegam em inglês, abreviados e com siglas, e a regra de palavras-chave acerta a área de 105 dos 179 contatos aprovados, ou 58,7%.

O serviço mantém tudo o que a Ponte construiu e troca uma única etapa: a área deixa de vir das palavras-chave e passa a vir do Claude, a partir da definição das áreas.

## Material

Na pasta `dados_n3`:

| Arquivo | O que é |
| --- | --- |
| `base_bruta_projeto.csv` | 212 contatos fictícios, com as mesmas colunas da base da Ponte e 50 cargos distintos |
| `descadastrados_projeto.xlsx` | E-mails que pediram descadastro |
| `definicao_areas.md` | A definição de cada área e as regras de classificação. É o documento de negócio que o Claude deve seguir |
| `cargos_gabarito.csv` | A área correta de cada cargo. Use só para medir |
| `conferir_projeto_n3.py` e `saida_esperada_projeto/` | O conferidor e a saída esperada |

Da Ponte, você usa o seu `validacao.py` e o seu `tratar_base.py`. Deste nível, o `claude_util.py` e o seu `retomada.py`.

## Como o serviço é chamado

```
python tratar_base_claude.py dados_n3/base_bruta_projeto.csv dados_n3/descadastrados_projeto.xlsx saida_projeto
```

O primeiro arquivo pode ser `.csv` ou `.xlsx`. O terceiro valor é a pasta de saída. Se a execução for interrompida, o mesmo comando continua de onde parou.

## Divisão de trabalho

| Etapa | Quem faz | Observação |
| --- | --- | --- |
| Ler a base, em CSV ou Excel | Código | Tudo como texto, para não perder zeros à esquerda |
| Padronizar e-mail, nome, telefone, empresa, CNPJ, cidade, UF, origem e consentimento | Código | As funções da Ponte, sem mudança |
| Rejeitar linhas e montar avisos | Código | As regras da Ponte, sem mudança |
| Classificar a área de cada cargo | Claude | Só os cargos distintos das linhas aprovadas |
| Montar os arquivos de saída e o custo | Código | |

**O que sai do computador.** Só os textos dos cargos distintos das linhas aprovadas, e a definição das áreas. Nenhum nome, e-mail, telefone, empresa ou CNPJ é enviado. Esse é um requisito do projeto, e não uma recomendação.

## Arquivos de saída

| Arquivo | Conteúdo | Colunas |
| --- | --- | --- |
| `importar.csv` | As linhas aprovadas, no layout do CRM, com a área final | As 13 colunas do layout |
| `rejeitados.csv` | As linhas que não serão importadas | `linha`, `email_bruto`, `motivo` |
| `avisos.csv` | Campos corrigidos de forma conservadora | `linha`, `email`, `aviso` |
| `decisoes_cargos.csv` | Uma linha por cargo distinto | `cargo`, `contatos`, `area_regra`, `area_claude`, `area_final`, `fonte` |
| `revisar_areas.csv` | Os cargos em que a área final difere da regra de palavras-chave, ou que ficaram sem resposta do Claude | As mesmas colunas, do cargo com mais contatos para o com menos |
| `custo.txt` | Modelo, cargos classificados, tokens por tipo, custo total, custo por contato e por mil contatos | — |
| `resumo.txt` | Os totais, que o script também mostra na tela | — |
| `progresso_cargos.jsonl` | O arquivo de progresso da retomada | — |

Todos os CSVs são separados por ponto e vírgula, em UTF-8.

## Regras da classificação pelo Claude

1. **Entrada.** Uma chamada por cargo distinto, com o texto do cargo como o contato informou.
2. **Instruções.** As instruções de sistema trazem o conteúdo de `definicao_areas.md` dentro de uma tag, com a marca de cache no fim. Você pode acrescentar exemplos, desde que os cargos dos exemplos não estejam na base do projeto.
3. **Saída.** Saída estruturada com um campo `area`, em lista fechada com as seis áreas do layout.
4. **Esforço.** Comece com `low`.
5. **Cargo vazio.** Não é enviado. A área é `Outros`.
6. **Sem resposta.** Se um cargo terminar como `recusado`, `erro` ou `pendente`, a área final é a da regra de palavras-chave, e a coluna `fonte` registra o motivo. Nenhum contato fica sem área.
7. **Retomada e teto.** A classificação usa a sua retomada, com o arquivo de progresso na pasta de saída e teto de custo de 2 dólares.

Por que manter a regra de palavras-chave: ela é a rede de segurança quando não há resposta e é a base de comparação. O `revisar_areas.csv` mostra a uma pessoa onde o Claude mudou a decisão da regra. É por esse arquivo que o resultado é auditado antes da importação.

## Passos

### 1. Planeje (30 min)

1. Leia `definicao_areas.md` e classifique à mão dez cargos da base, antes de ver o gabarito. Anote os que geraram dúvida.
2. Liste as funções do script. Marque quais chamam a API e quais não.
3. Estime o custo: conte os cargos distintos e use a projeção do módulo 3.5.

### 2. Construa a parte sem API (1 h 30)

4. Faça o script ler CSV e Excel. Para testar a leitura de Excel, gere o arquivo com duas linhas de Python: leia o CSV com `dtype=str` e `keep_default_na=False` e grave com `to_excel`.
5. Reaproveite as funções do `tratar_base.py` para padronizar, rejeitar e montar os avisos.
6. Escreva a função que monta o `decisoes_cargos.csv` a partir das linhas aprovadas e dos registros da retomada. Teste com registros montados à mão, sem chamar a API: um cargo `ok`, um `recusado`, um ausente.
7. Escreva a função que monta o texto do `custo.txt` a partir dos registros.
8. Confira os números do gabarito que não dependem do modelo.

### 3. Ligue o Claude (1 h 30)

9. Escreva as instruções de sistema, o formato de saída e a função que classifica um cargo e devolve o registro no formato da retomada, com o custo e os tokens.
10. Rode primeiro com uma base de 10 linhas, cortada da base do projeto.
11. Rode a base inteira. Confira no `custo.txt` que houve leitura de cache. Se não houve, conte os tokens da parte fixa: ela precisa ter ao menos 512.

### 4. Meça, revise e teste as falhas (1 h 30)

12. Rode o conferidor:

```
python dados_n3/conferir_projeto_n3.py saida_projeto
```

13. Leia os erros de área que o conferidor listar. Classifique cada um: erro do modelo, definição ambígua ou gabarito discutível. Ajuste as instruções uma vez, rode em uma pasta de saída nova e compare.
14. Abra o `revisar_areas.csv` e leia linha a linha, como quem vai autorizar a importação.
15. **Teste de retomada.** Em uma pasta de saída nova, interrompa a execução com Ctrl+C no meio da classificação e rode de novo. Confira no `progresso_cargos.jsonl` que nenhum cargo tem duas linhas com situação `ok`.
16. **Teste de privacidade.** Procure o caractere `@` no `progresso_cargos.jsonl`. Não deve haver nenhum. Depois, aponte no seu código a linha que monta a mensagem enviada e confirme que ela só recebe o cargo.
17. **Teste do Excel.** Rode com a base em `.xlsx` em outra pasta de saída e confirme que o `importar.csv` é igual.

### 5. Documente (1 h)

18. Escreva um `README_servico.md` de uma página: o que o serviço faz, como chamar, os arquivos de saída, o que sai do computador, quanto custa por mil contatos e o que uma pessoa precisa revisar antes de importar.
19. Faça o commit final. As pastas de saída e os arquivos de progresso ficam fora do repositório.

## Gabarito

Os números abaixo não dependem do modelo. Foram calculados pela solução de referência e conferidos por um segundo cálculo independente.

```
Linhas lidas: 212
Linhas para importar: 179
Linhas rejeitadas: 33
  descadastrado: 8
  e-mail inválido: 6
  e-mail repetido: 12
  nome ausente: 3
  origem não reconhecida: 4
Avisos: 44
  cnpj descartado: 7
  consentimento rebaixado: 18
  telefone descartado: 19
Cargos distintos: 50
```

| Verificação | Valor |
| --- | --- |
| Acerto da regra de palavras-chave, por contato | 105 de 179 (58,7%) |
| Acerto da regra de palavras-chave, por cargo | 30 de 50 |
| Contatos por área, com a classificação correta | Produção 36, Compras 32, Diretoria 32, Comercial 31, Marketing 27, Outros 21 |

A conta fecha: 212 lidas = 179 para importar + 33 rejeitadas.

O que depende do modelo, e que você mede: o acerto da área pelo Claude, os tokens e o custo. O conferidor informa o acerto por contato e lista os erros por cargo.

Cargos que costumam gerar discussão, com a decisão do gabarito e a regra da definição que a sustenta:

| Cargo | Área no gabarito | Regra |
| --- | --- | --- |
| `Head of Procurement` | Compras | Regra 2: heads ficam na área em que atuam |
| `Engenheiro de Vendas` | Comercial | Regra 3: vale a função, não a formação |
| `Gerente de Desenvolvimento de Negócios` | Comercial | A definição de Comercial cita desenvolvimento de negócios |
| `Gerente de Logística` | Outros | A definição de Outros cita logística |
| `Dir. de Operações` | Diretoria | Regra 4: abreviações são classificadas pelo significado |
| `Product Manager` | Marketing | A definição de Marketing cita produto |

Se o Claude discordar do gabarito em um desses cargos, leia a definição antes de concluir quem errou. Em um trabalho real, a dúvida vai para quem escreveu a definição, e a resposta entra no documento.

## Critérios de aprovação

- [ ] O conferidor informa "Projeto aprovado no conferidor": as colunas determinísticas iguais à saída esperada e pelo menos 90% dos contatos com a área correta.
- [ ] O resumo na tela traz os números do gabarito.
- [ ] O `custo.txt` mostra tokens lidos do cache e o custo por mil contatos.
- [ ] O teste de retomada não gerou cargos pagos duas vezes.
- [ ] O `progresso_cargos.jsonl` não contém nenhum `@`, e você aponta a linha do código que garante que só o cargo é enviado.
- [ ] A base em Excel produz o mesmo `importar.csv`.
- [ ] As funções que não chamam a API têm testes, e todos passam.
- [ ] O `README_servico.md` informa o custo por mil contatos, o acerto medido e o que precisa de revisão humana.
- [ ] Você leu o `revisar_areas.csv` inteiro e consegue justificar cada linha.

## Entregável

1. O repositório com `tratar_base_claude.py`, os testes e o `README_servico.md`.
2. A mensagem do conferidor e o conteúdo do `custo.txt`.
3. Um registro de uma página com: o acerto antes e depois do ajuste das instruções, a classificação dos erros, os resultados dos três testes do passo 4 e o que você mudaria na definição das áreas.

## Desafios opcionais

**Memória de cargos.** Guarde as decisões em um arquivo `cargos_conhecidos.csv`, fora da pasta de saída. A cada nova base, o serviço consulta o arquivo e envia ao Claude só os cargos que nunca viu. É a alavanca 1 do módulo 3.5 aplicada ao longo do tempo: depois de algumas bases, a maior parte dos cargos já está resolvida, e o custo por base cai. Decida como uma correção humana entra nesse arquivo e como ela tem prioridade sobre a resposta do modelo.

**Modelo menor.** Rode o serviço com o Haiku 5.5 em outra pasta de saída e compare acerto e custo por mil contatos. Escreva a recomendação com os dois números.

**Lote.** Para bases sem urgência, envie os cargos em um lote, como no módulo 3.5, e monte a saída na coleta.

## O que este projeto ainda não resolve

O serviço faz uma tarefa: classifica a área. Quem decide o que fazer é o seu script, passo a passo, sempre na mesma ordem. Para uma base em que as colunas vêm com outros nomes, ou em que falta decidir se dois registros são a mesma pessoa, alguém precisa alterar o código.

No Nível 4, o controle muda de lado. O Claude recebe um objetivo e um conjunto de ferramentas, como as do módulo 3.4, e decide a sequência de passos. O que você construiu aqui passa a ser uma das ferramentas desse agente: uma função confiável, testada, com custo conhecido e limites definidos no código.

A solução de referência está em [`gabarito/tratar_base_claude.py`](gabarito/tratar_base_claude.py).

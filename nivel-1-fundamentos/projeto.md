# Projeto do Nível 1 — Assistente do relatório mensal de e-mail

**Carga:** 2 h

## Objetivo

Montar, em um Project, um assistente que recebe a exportação de desempenho por disparo e devolve os indicadores do mês, a tabela por público e a leitura do mês. O projeto reúne os cinco módulos: você escolhe o modelo, escreve as instruções, fornece o material, confere os números e valida o resultado.

## Material

- [`dados/desempenho_email_outubro.csv`](dados/desempenho_email_outubro.csv): exportação fictícia com 15 disparos de outubro de 2026 da Expo Modelo.

Colunas do arquivo: `disparo`, `data_envio`, `hora_envio`, `enviadas`, `entregues`, `aberturas_unicas`, `cliques_unicos`, `descadastros`.

O público de cada disparo está no nome, na quarta parte separada por sublinhado. Em `2026_10_EXPOMODELO_Prospeccao_Faltam15Dias`, o público é `Prospeccao`.

## Passos

### 1. Escreva o arquivo de método (20 min)

Crie um documento chamado `metodo_relatorio_mensal.md` com as regras que o assistente deve seguir. Ele é o equivalente às suas notas metodológicas. Inclua, no mínimo:

- **Definições:**
  - taxa de entrega = entregues ÷ enviadas;
  - taxa de abertura = aberturas únicas ÷ entregues;
  - taxa de clique = cliques únicos ÷ entregues.
- **Exclusão:** disparos com menos de 10 envios ficam fora do relatório e são listados em nota.
- **Público:** vem do nome do disparo, na quarta parte separada por sublinhado.
- **Anomalia:** disparo com taxa de clique acima de 15% é sinalizado como possível clique automático de filtro de segurança e continua nos totais.
- **Arredondamento:** taxas com uma casa decimal; totais sem arredondar.
- **Taxa de um grupo:** soma dos numeradores ÷ soma dos denominadores do grupo, nunca a média das taxas dos disparos.

### 2. Crie o Project e escreva as instruções (30 min)

Crie o Project "Relatório mensal de e-mail" e adicione o arquivo de método como conhecimento.

Escreva as instruções você mesmo, usando o que aprendeu no módulo 1.4. Elas devem cobrir:

1. **Papel e leitor:** quem é o assistente e para quem o relatório vai.
2. **Método:** seguir o arquivo de método e calcular com a ferramenta de análise, nunca de cabeça.
3. **Formato:** como apresentar indicadores, tabela e leitura.
4. **Regras da leitura:** citar só números do arquivo, separar fato de hipótese, sem adjetivos.
5. **Dado ausente:** dizer o que falta em vez de supor.

### 3. Rode as cinco conversas de teste (50 min)

Abra uma conversa nova para cada teste, sempre anexando o CSV.

| # | Pedido | O que o teste verifica |
| --- | --- | --- |
| 1 | "Calcule os indicadores gerais de outubro." | Totais, taxas e a regra de exclusão |
| 2 | "Monte a tabela de desempenho por público." | Classificação pelo nome e taxa de grupo |
| 3 | "Escreva a leitura do mês com três achados e um próximo passo para cada." | Texto fiel aos números, fato separado de hipótese |
| 4 | "Compare os disparos ConviteDireto e ConviteCompleto." | Leitura de um teste de formato |
| 5 | "Compare outubro com setembro." | Comportamento com dado ausente |

### 4. Confira com o gabarito (20 min)

Compare cada resposta com o gabarito abaixo. Onde houver diferença, descubra a causa (instrução ambígua, regra faltando no método, cálculo feito sem ferramenta), corrija as instruções ou o método e repita o teste em uma conversa nova.

## Gabarito

Os números abaixo foram calculados por código a partir do CSV.

### Teste 1 — Indicadores gerais

| Indicador | Valor |
| --- | --- |
| Disparos considerados | 14 |
| Disparo excluído | `2026_10_EXPOMODELO_Confirmacao_RespostaAutomatica` (6 envios) |
| Mensagens enviadas | 50.812 |
| Mensagens entregues | 50.116 |
| Taxa de entrega | 98,6% |
| Aberturas únicas | 26.385 |
| Taxa de abertura | 52,6% |
| Cliques únicos | 1.218 |
| Taxa de clique | 2,4% |

O assistente também deve sinalizar o disparo `2026_09_EXPOMODELO_Credenciamento_Acao2oEnvio`: 61 cliques em 304 entregues, taxa de 20,1%.

Erro frequente: incluir o disparo de 6 envios, o que leva a 50.818 enviadas e 15 disparos.

### Teste 2 — Tabela por público

| Público | Disparos | Enviadas | Entregues | Entrega | Abertura | Cliques | Clique |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Prospecção | 4 | 26.540 | 26.225 | 98,8% | 54,7% | 427 | 1,6% |
| Credenciamento | 5 | 16.860 | 16.701 | 99,1% | 59,1% | 593 | 3,6% |
| Pré-credenciado | 2 | 4.350 | 4.248 | 97,7% | 40,6% | 159 | 3,7% |
| Reativação | 1 | 2.900 | 2.780 | 95,9% | 12,6% | 28 | 1,0% |
| Expositor | 2 | 162 | 162 | 100,0% | 64,8% | 11 | 6,8% |
| **Total** | **14** | **50.812** | **50.116** | **98,6%** | **52,6%** | **1.218** | **2,4%** |

Conferências:

- A soma das linhas bate com o total em todas as colunas de contagem.
- Sem o disparo com possível clique automático, o clique de Credenciamento cai de 3,6% para 3,2%. Uma boa resposta menciona esse efeito.

Erro frequente: calcular a taxa do grupo como média das taxas dos disparos. Em Prospecção, a média simples das quatro aberturas dá 51,2%, e o valor correto é 54,7%.

### Teste 3 — Leitura do mês

Não há texto único correto. A leitura é aprovada se:

1. Cada número citado existe no arquivo ou no gabarito.
2. Os três achados são relevantes. Exemplos de achados que os dados sustentam:
   - Prospecção concentra 52% do volume enviado e tem o menor clique entre os públicos de volume, 1,6%.
   - O convite pessoal para pré-credenciados teve 5,4% de clique, a maior taxa entre os disparos com mais de 1.000 envios.
   - A reativação abriu 12,6%, com 12 descadastros, o maior número do mês.
3. Nenhuma causa é afirmada como fato. "O convite pessoal converteu mais" é fato; "porque o público confia no remetente" é hipótese.
4. Cada próximo passo decorre de um achado.

### Teste 4 — Teste de formato

| Versão | Entregues | Abertura | Clique | Cliques únicos |
| --- | --- | --- | --- | --- |
| ConviteDireto | 3.968 | 62,0% | 3,0% | 119 |
| ConviteCompleto | 3.960 | 57,8% | 2,0% | 79 |

A versão direta teve 4,2 pontos percentuais a mais de abertura e 51% mais cliques. Com cerca de 4 mil entregas em cada versão, a diferença é grande demais para ser atribuída ao acaso.

Uma boa resposta diferencia ponto percentual de percentual e lembra que, se os assuntos eram diferentes, parte da diferença de abertura vem do assunto e não do formato.

### Teste 5 — Dado ausente

O arquivo não tem dados de setembro. A resposta correta diz que a comparação não pode ser feita com o material fornecido e pede o arquivo de setembro.

Se o assistente inventar números de setembro, as instruções falharam no item "dado ausente". Reforce a regra e repita.

## Critérios de aprovação

- [ ] Testes 1, 2 e 4 batem com o gabarito em todos os números.
- [ ] O disparo de 6 envios foi excluído e listado em nota.
- [ ] O disparo com 20,1% de clique foi sinalizado.
- [ ] A leitura do teste 3 cumpre os quatro critérios.
- [ ] No teste 5, o assistente não inventou dados.
- [ ] Você fez pelo menos um ajuste nas instruções ou no método a partir de um erro encontrado e registrou qual foi.

## Entregável

1. O Project com as instruções finais e o arquivo de método.
2. Um registro de uma página com: o resultado de cada teste, os erros encontrados e o ajuste feito para cada um.

## Próximo passo

Use o assistente com uma exportação real de um mês já fechado e compare o resultado com o relatório que você entregou. As diferenças mostram quais regras do seu método ainda não estão escritas. No nível 2, esse assistente ganha um padrão visual e passa a gerar o relatório em PowerPoint.

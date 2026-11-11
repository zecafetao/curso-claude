---
name: relatorio-mensal-email
description: Gera o relatório mensal de e-mail marketing em PowerPoint a partir da exportação de desempenho por disparo do CRM (CSV ou Excel com enviadas, entregues, aberturas e cliques). Use quando o usuário pedir o relatório mensal de e-mail, os indicadores de e-mail de um mês ou enviar uma exportação de disparos para análise.
---

# Relatório mensal de e-mail

Produz uma apresentação em PowerPoint com o desempenho dos disparos de e-mail de um mês, para o organizador de uma feira de negócios. O leitor usa o relatório para decidir os disparos do mês seguinte e precisa confiar em cada número.

## Entrada

Uma exportação com uma linha por disparo e as colunas `disparo`, `data_envio`, `hora_envio`, `enviadas`, `entregues`, `aberturas_unicas`, `cliques_unicos` e `descadastros`. Se os nomes das colunas forem outros, identifique a correspondência e confirme com o usuário antes de calcular.

Se o usuário enviar também a exportação do mês anterior, inclua a comparação entre os dois meses.

## Método

Siga `references/metodo.md` para definições, exclusões, classificação por público, anomalias e arredondamento. Faça todos os cálculos com código, a partir do arquivo. Nenhum número do relatório vem de estimativa.

## Estrutura da apresentação

Um slide por mensagem. O título de cada slide de conteúdo é o achado, não o assunto: "Credenciamento teve o dobro do clique da prospecção", e não "Desempenho por público".

1. **Capa:** nome da feira, mês de referência e "E-mail marketing — desempenho dos disparos".
2. **Indicadores do mês:** mensagens enviadas, mensagens entregues com a taxa de entrega, taxa de abertura e cliques únicos com a taxa de clique. Em nota, os disparos excluídos e o motivo.
3. **Do envio ao clique:** as quatro etapas em barras proporcionais às mensagens enviadas.
4. **Comparação com o mês anterior:** só quando houver o arquivo do mês anterior. Diferenças de taxa em pontos percentuais.
5. **Desempenho por público:** tabela com disparos, enviadas, entregues, taxa de entrega, taxa de abertura, cliques únicos e taxa de clique, com a linha de total.
6. **Desempenho por disparo:** uma tabela por público ou por grupo de públicos, com no máximo 10 linhas por slide. Disparos com anomalia recebem um asterisco e uma nota.
7. **Leitura do mês e próximos passos:** três achados, cada um com um próximo passo que decorre dele.
8. **Notas metodológicas:** definições das taxas, critérios de exclusão, anomalias e limitações dos dados.

Aplique `references/padrao-visual.md` a todos os slides.

## Texto

Cite só números calculados a partir do arquivo. Separe fato de hipótese: o que os dados mostram é afirmado; a explicação de uma diferença é apresentada como hipótese. Escreva em português do Brasil, com frases curtas e sem adjetivos de avaliação.

## Verificação antes de entregar

1. A soma das linhas por público é igual ao total em enviadas, entregues, aberturas e cliques.
2. O total bate com a soma do arquivo, descontados os disparos excluídos.
3. Cada número citado em texto aparece em uma tabela do relatório.
4. Nenhum texto ultrapassa a área do slide.

Se alguma verificação falhar, corrija antes de entregar.

## Resposta ao usuário

Entregue o arquivo e, em poucas linhas, informe os disparos considerados e excluídos, as anomalias encontradas e qualquer dado que faltou.

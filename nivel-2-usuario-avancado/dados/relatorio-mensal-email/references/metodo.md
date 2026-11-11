# Método do relatório mensal de e-mail

## Definições

| Indicador | Cálculo |
| --- | --- |
| Taxa de entrega | entregues ÷ enviadas |
| Taxa de abertura | aberturas únicas ÷ entregues |
| Taxa de clique | cliques únicos ÷ entregues |
| Clique entre quem abriu | cliques únicos ÷ aberturas únicas |

A taxa de um grupo de disparos é a soma dos numeradores dividida pela soma dos denominadores do grupo. Não use a média das taxas dos disparos, porque ela dá o mesmo peso a um disparo de 80 envios e a um de 8 mil.

## Exclusões

Disparos com menos de 10 envios ficam fora do relatório. São respostas automáticas e testes, que distorcem as taxas. Liste os excluídos em nota, com o número de envios de cada um.

## Público

O público vem do nome do disparo, na quarta parte separada por sublinhado. Em `2026_10_EXPOMODELO_Prospeccao_Faltam15Dias`, o público é `Prospeccao`.

| Código no nome | Nome no relatório |
| --- | --- |
| `Prospeccao` | Prospecção |
| `Credenciamento` | Credenciamento |
| `PreCredenciado` | Pré-credenciado |
| `Reativacao` | Reativação |
| `Expositor` | Expositor |

Se um nome não seguir o padrão, não adivinhe o público: liste o disparo e pergunte ao usuário.

## Anomalias

Disparo com taxa de clique acima de 15% é sinalizado como possível clique automático de filtro de segurança. Ele continua nos totais, recebe um asterisco na tabela e uma nota que informa como ficaria a taxa do público sem ele.

## Arredondamento e formato

- Contagens sem arredondar, com ponto como separador de milhar: 50.812.
- Taxas com uma casa decimal e vírgula: 52,6%.
- Diferenças entre taxas em pontos percentuais: "+4,2 pontos percentuais".

## Comparações

- Comparar taxas só entre grupos com pelo menos 200 mensagens entregues. Em listas menores, um clique muda a taxa em mais de meio ponto.
- Em teste de duas versões, informar o tamanho de cada grupo junto das taxas.

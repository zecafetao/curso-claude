# Projeto do Nível 2 — Biblioteca de prompts testados

**Carga:** 4 h

## Objetivo

Montar uma biblioteca de 10 prompts para o seu trabalho, cada um com três casos de teste e o resultado esperado. A biblioteca transforma o que você aprendeu no nível em um ativo reutilizável: pedidos que você sabe que funcionam, porque foram testados.

## O que é uma entrada da biblioteca

Cada prompt é registrado em uma ficha com os mesmos campos:

| Campo | Conteúdo |
| --- | --- |
| **Nome** | Curto e descritivo |
| **Quando usar** | A situação em que o prompt se aplica e quando não se aplica |
| **Entradas** | O que precisa ser fornecido: arquivos, tabelas, parâmetros |
| **Prompt** | O texto, com os pontos variáveis entre chaves: `{publico}`, `{tabela}` |
| **Saída esperada** | O formato e o padrão de qualidade da resposta |
| **Casos de teste** | Três casos, cada um com entrada, resultado esperado e resultado obtido |
| **Configuração** | Modelo e esforço usados no teste; Project ou Skill necessários |
| **Limites** | O que o prompt não cobre e o que conferir sempre |
| **Versão e data** | Para saber o que mudou e quando |

## Os 10 prompts

Cubra as seis áreas do seu trabalho. A lista abaixo é a sugestão; você pode trocar um item por outro da mesma área que seja mais útil para você.

| # | Área | Prompt | Base no curso |
| --- | --- | --- | --- |
| 1 | Tratamento de base | Diagnóstico de uma base contra o layout de importação | 1.3, 1.5 |
| 2 | Tratamento de base | Padronização de valores distintos de uma coluna (cargos em áreas) | 1.5, 2.2 |
| 3 | Segmentação | Proposta de segmentos e argumentos a partir de um estudo de público | 2.4 |
| 4 | Segmentação | Classificação de contatos em segmentos, por regra | 2.2 |
| 5 | E-mail | Convite a partir de briefing, para um segmento informado | 2.1 |
| 6 | E-mail | Variações de assunto para teste | 1.4 |
| 7 | Landing page | Página em HTML a partir de briefing | 2.7 |
| 8 | Relatório | Leitura de um quadro de desempenho | 1.4, 2.1 e 2.6 |
| 9 | Relatório | Análise de um teste de duas versões | 2.6 |
| 10 | Estudo de público ou de mercado | Extração de fatos de fontes, com escopo e origem | 2.3 |

## Os três casos de teste

Cada prompt precisa de um caso de cada tipo:

| Tipo | O que verifica | Exemplo para o prompt 8 |
| --- | --- | --- |
| **Típico** | O uso normal funciona | A tabela por público de outubro |
| **De borda** | O prompt lida com uma situação difícil | Uma tabela com um público de 162 entregas, em que a comparação de taxas não é confiável |
| **Armadilha** | O prompt não inventa nem cede | Pedir a comparação com um mês que não está na tabela |

Defina o resultado esperado **antes** de rodar. Para resultados numéricos, o esperado é o valor exato. Para texto, o esperado é uma lista de critérios verificáveis.

## Passos

### 1. Monte a estrutura (20 min)

Crie um Project "Biblioteca de prompts" ou uma pasta de documentos, com uma ficha por prompt. Copie o modelo de ficha da seção seguinte.

### 2. Escreva e teste os prompts (3 h)

Para cada um dos 10:

1. Escreva o prompt, aplicando o que couber: os cinco elementos (1.4), regras com motivo (2.1), exemplos e tags (2.2), documentos antes da pergunta (2.3), verificação e ausência de solução (2.4).
2. Escreva os três casos de teste e os resultados esperados.
3. Rode cada caso em uma conversa nova.
4. Registre o resultado obtido e marque se passou.
5. Se algum caso falhar, ajuste o prompt, mudando uma coisa por vez, e rode os três casos de novo.

Reaproveite o que você já produziu: o classificador do módulo 2.2, as instruções do redator do 2.1 e os pedidos do 2.3 já são prompts testados. Passe-os para a ficha e complete os casos que faltam.

### 3. Revise a biblioteca (40 min)

1. Releia os 10 prompts em sequência e remova o que estiver datado: ênfase em maiúsculas, "pense passo a passo", listas de proibições sem motivo, regras escritas para um único caso.
2. Peça a um colega, ou a você mesmo no dia seguinte, que use dois prompts só com a ficha. Se surgirem dúvidas, a ficha está incompleta.
3. Preencha o índice da biblioteca: nome, área e quando usar.

## Modelo de ficha, com um exemplo preenchido

```
NOME
Leitura de quadro de desempenho

QUANDO USAR
Para escrever o texto que acompanha uma tabela de resultados em um
relatório de e-mail. Não usar para tabelas com dados pessoais nem para
calcular as taxas: a tabela já deve chegar calculada.

ENTRADAS
{tabela}: a tabela de desempenho, com as taxas já calculadas.
{leitor}: quem vai ler o relatório e o que decide com ele.

PROMPT
Escreva a leitura do quadro em <tabela> para um relatório mensal de e-mail
marketing. O leitor é {leitor}.

A leitura acompanha a tabela em um slide, então deve caber em três frases.
Aponte a diferença mais relevante entre as linhas, com os números. Cite só
valores que aparecem na tabela. Afirme o que os dados mostram; se propuser
uma explicação, apresente-a como hipótese. Não compare taxas de linhas com
menos de 200 mensagens entregues, porque nelas um clique muda a taxa em
mais de meio ponto; se houver uma linha assim, diga isso.

Se a tabela não tiver os dados necessários para o que foi pedido, diga o
que falta.

<tabela>
{tabela}
</tabela>

SAÍDA ESPERADA
Três frases, em parágrafo único, com números no formato da tabela.

CASOS DE TESTE

1. Típico
Entrada: tabela por público de outubro (gabarito do projeto do Nível 1).
Esperado: (a) todos os números citados existem na tabela; (b) menciona a
diferença de clique entre prospecção (1,6%) e credenciamento (3,6%) ou
pré-credenciado (3,7%); (c) no máximo três frases; (d) nenhuma causa
afirmada como fato.
Obtido: ...            Passou: sim / não

2. De borda
Entrada: a mesma tabela, com a instrução de comentar o público Expositor.
Esperado: informa que a linha tem 162 mensagens entregues e que a taxa não
é comparável com as demais.
Obtido: ...            Passou: sim / não

3. Armadilha
Entrada: a mesma tabela, com o pedido "compare com setembro".
Esperado: diz que a tabela não tem dados de setembro e pede o arquivo.
Obtido: ...            Passou: sim / não

CONFIGURAÇÃO
Modelo: ...   Esforço: padrão   Project: nenhum

LIMITES
Não calcula. Conferir sempre cada número citado contra a tabela.

VERSÃO E DATA
v1 — ...
```

## Critérios de aprovação

- [ ] A biblioteca tem 10 fichas completas, cobrindo as seis áreas.
- [ ] Cada ficha tem três casos de teste: típico, de borda e armadilha.
- [ ] Os resultados esperados foram escritos antes dos testes e são verificáveis.
- [ ] Os 30 casos passam na versão final dos prompts.
- [ ] Nenhum prompt usa dado pessoal real nos casos de teste.
- [ ] Os prompts numéricos (8 e 9) foram conferidos contra o gabarito do projeto do Nível 1.
- [ ] Você registrou pelo menos três ajustes feitos a partir de falhas, com a causa de cada uma.

## Entregável

1. A biblioteca, com o índice e as 10 fichas.
2. Um registro de uma página com os casos que falharam na primeira rodada, a causa de cada falha e o ajuste feito.

## Próximo passo

Use a biblioteca no trabalho por duas semanas e anote cada vez que um prompt não servir. Essas anotações são casos de teste novos.

A próxima etapa é a Ponte de Python. Nela, o trabalho determinístico dos seus fluxos (tratar bases, calcular taxas, remover duplicados) passa de planilhas para scripts que rodam no seu computador, e os dados reais deixam de precisar de qualquer envio.

# Projeto do Nível 4 — Agente de relatórios

**Carga:** 8 h

## Objetivo

Construir um agente que recebe as exportações do CRM de um período e entrega o rascunho do relatório pedido, o mensal de e-mail ou o report pós-feira: indicadores calculados e gráficos gerados por ferramentas, comparação com o período anterior, leituras em texto e a lista de conferência de cada número, para revisão humana.

O projeto reúne os oito módulos: a escolha da arquitetura (4.1), o laço e o desenho das ferramentas (4.2), o servidor MCP sobre o banco da campanha (4.3), a Skill do relatório e o repositório configurado (4.4), a entrega do arquivo (4.5), o contexto enxuto (4.6) e a verificação de números por código (4.7). A busca no acervo (4.8) entra como desafio opcional.

## O problema

Os dois relatórios recorrentes do seu trabalho têm a mesma estrutura de risco. A maior parte é cálculo com regra fixa: taxas, comparações, tabelas, gráficos. Uma parte pequena é interpretação: o título de cada slide, os achados, os próximos passos. O erro que mais custa é um número errado no texto interpretativo, porque é o que o cliente lê primeiro e o que ninguém confere contra a tabela.

O agente deste projeto separa as duas partes. As ferramentas calculam e montam; o modelo escreve os textos; e uma ferramenta de verificação recusa qualquer texto com número que não exista nos resultados das ferramentas. O rascunho chega à revisão com a lista de onde veio cada número.

O módulo 4.1 classificou o relatório mensal como workflow, com a ressalva de que pedidos variáveis e dois tipos de relatório justificam um agente. É o caso aqui: o mesmo agente atende aos dois relatórios e a variações do pedido.

## Material

Na pasta `dados_n4`, copiada de `dados/`:

| Arquivo | O que é |
| --- | --- |
| `desempenho_email_setembro.csv`, `desempenho_email_outubro.csv` | Exportações de e-mail por disparo, as mesmas da Ponte |
| `feira_credenciados.csv`, `feira_visitantes.csv`, `feira_inscritos_evento.csv`, `feira_whatsapp_tentativas.csv` | Exportações da feira e do WhatsApp da Expo Modelo 2026 |
| `relatorio-mensal-email/` | A Skill do relatório mensal, criada no módulo 2.5 |
| `report-pos-feira/` | A Skill do report pós-feira: método em pessoas, definição de visitante, WhatsApp por contato, estrutura de 8 slides |
| `conferir_projeto_n4.py` | O conferidor |
| `exemplos/projeto/` | Os dois relatórios montados com textos escritos à mão, para você ver o resultado esperado |

Do gabarito, você reaproveita: `montar_banco.py`, `indicadores.py` e `servidor_campanha.py` (módulo 4.3), `verificar_numeros.py`, `apresentacao.py`, `graficos_relatorio.py` (Ponte), `graficos_feira.py`, `relatorio_mensal.py`, `reconciliar.py`, `validacao.py` e `claude_util.py`. Se você escreveu as suas versões nos módulos, use as suas.

## Como o agente é chamado

```bash
python agente_relatorios.py mensal 2026-10 2026-09
python agente_relatorios.py pos_feira
```

A saída vai para `saida_relatorios/mensal_2026-10/` ou `saida_relatorios/pos_feira/`.

## Arquitetura

```
Pedido ──> Agente (Opus 5.5, instruções = regras + Skill do relatório)
              │
              ├── servidor MCP da campanha (stdio, só leitura, só agregados)
              │     indicadores_email, indicadores_por_publico, anomalias_de_clique,
              │     comparar_meses, entrega_whatsapp, funil_feira, whatsapp_e_visitacao
              │
              ├── verificar_textos   (local: confere cada número dos textos)
              └── montar_relatorio   (local: gráficos + apresentação + lista de conferência;
                                      recusa texto com número sem fonte)
```

| Etapa | Quem faz |
| --- | --- |
| Consultar os indicadores | O agente decide quais; o servidor MCP calcula |
| Escrever os títulos-achado dos slides e os três achados | O agente |
| Conferir cada número dos textos | Código: `verificar_textos` |
| Gerar os gráficos no padrão visual | Código: `graficos_relatorio.py` e `graficos_feira.py` |
| Montar a apresentação, com tabelas e destaques | Código: `apresentacao.py` |
| Registrar a origem de cada número | Código: `conferencia.csv` |
| Revisar o rascunho e decidir o envio | Você |

A referência completa está em [`gabarito/agente_relatorios.py`](gabarito/agente_relatorios.py). As instruções do agente são as regras do projeto mais o conteúdo da Skill do relatório pedido, lido dos arquivos: uma mudança no método da Skill vale para o app, para o Claude Code e para o agente.

**O que sai do computador.** As instruções, com a Skill; o pedido; e os resultados das ferramentas, que são só contagens e taxas. Nenhum nome, e-mail ou telefone é enviado à API. É um requisito do projeto.

## Arquivos de saída

| Arquivo | Conteúdo |
| --- | --- |
| `relatorio_email_<mês>.pptx` ou `report_pos_feira.pptx` | Os 8 slides da estrutura da Skill, no padrão visual |
| `conferencia.csv` | Uma linha por número da apresentação: `slide`, `elemento`, `valor`, `origem` (a ferramenta e os parâmetros que o produziram) |
| `graficos/` | Os gráficos em PNG, cada um com o CSV dos valores desenhados (padrão da Ponte) |

## Requisitos

1. **Ferramentas.** Pelo menos três ferramentas, das quais pelo menos uma vem de um servidor MCP. O gabarito usa nove: sete do servidor e duas locais.
2. **Skill.** As instruções incluem a Skill do relatório pedido.
3. **Números.** Todo número em texto escrito pelo modelo passa pela verificação antes da montagem. A montagem recusa texto com número sem fonte, mesmo que o agente não tenha chamado a verificação.
4. **Arquivo final** no padrão visual: 8 slides, rodapé em todos os de conteúdo, cores do padrão, gráficos com o CSV ao lado.
5. **Lista de conferência** com a origem de cada número.
6. **Limites.** Limite de voltas no laço (o gabarito usa 15) e registro do custo de cada execução.
7. **Revisão humana.** O agente não envia nada a ninguém. A resposta final diz o que a pessoa revisora deve conferir.

## Passos

### 1. Planeje (30 min)

1. Abra os dois exemplos em `dados_n4/exemplos/projeto/`. Para cada slide, anote que ferramenta produz os números e que parte é texto do modelo.
2. Liste as ferramentas do seu agente e marque, para cada uma, o que ela devolve e se algum resultado pode conter dado pessoal.
3. Estime o custo de uma execução: número de voltas esperado, tamanho das instruções (a Skill entra inteira) e preço do módulo 3.5.

### 2. Banco e servidor (1 h)

4. Monte o banco com `montar_banco.py`.
5. Confira o servidor MCP com o `cliente_mcp.py`: os números do gabarito abaixo devem aparecer.
6. **Teste de privacidade das ferramentas.** Adapte o cliente para chamar as sete ferramentas e procure, nas respostas, o caractere `@` e sequências de 10 ou mais dígitos. Não deve haver nenhum.

### 3. Montagem sem a API (1 h 30)

7. Rode o [`gabarito/montar_exemplos.py`](gabarito/montar_exemplos.py), que monta os dois relatórios com textos escritos à mão:

```bash
python montar_exemplos.py saida_exemplos
python dados_n4/conferir_projeto_n4.py mensal saida_exemplos/mensal/relatorio_email_2026-10.pptx
python dados_n4/conferir_projeto_n4.py pos_feira saida_exemplos/pos_feira/report_pos_feira.pptx
```

   As duas conferências devem terminar com "Projeto aprovado no conferidor."

8. **Teste da trava.** No `montar_exemplos.py`, troque o título do primeiro achado do pós-feira por "Visitação abaixo de 40%" e rode de novo. A montagem deve ser recusada, com o número 40 apontado como sem fonte, e nenhum arquivo `.pptx` deve ser gravado. Volte o título.

   É exatamente o que aconteceu na primeira versão deste exemplo, escrita à mão: "40%" parecia um arredondamento inocente de 38,9%, mas não é um número que alguma ferramenta produz.

9. Abra as duas apresentações e o `conferencia.csv`. Confira três números ao acaso contra a origem indicada.

### 4. O agente (1 h 30)

10. Escreva as regras do agente: como trabalhar, de onde vêm os números, o que ele escreve e o que não escreve, quando verificar, como terminar. Use o `REGRAS` do gabarito como ponto de partida e ajuste ao seu vocabulário.
11. Escreva as duas ferramentas locais, `verificar_textos` e `montar_relatorio`, com mensagens de erro que dizem como corrigir (módulo 4.2).
12. Ligue o servidor MCP ao executor com `async_mcp_tool` (módulo 4.3).
13. Rode o relatório mensal. Acompanhe a sequência de ferramentas na tela.
14. Rode o conferidor sobre a apresentação gerada. Corrija até aprovar.
15. Rode o report pós-feira e o conferidor.

### 5. Teste e meça (2 h)

16. **Repetição.** Rode cada relatório mais duas vezes. Para as três execuções de cada, registre: aprovado ou não no conferidor, número de ferramentas chamadas, quantas vezes a verificação recusou um texto, custo e tempo.
17. **Pedido variável.** Rode um pedido diferente do padrão, como "relatório de outubro com destaque para o público de credenciamento". Se o seu agente aceita só os dois tipos fixos, anote o que seria preciso mudar e por quê.
18. **Pedido que convida a inventar.** Acrescente ao pedido: "inclua a projeção da taxa de abertura de novembro". Confirme que a projeção não chega à apresentação, e anote como o agente lidou com o pedido.
19. **Revisão humana.** Leia uma apresentação gerada como quem vai enviá-la ao cliente. Liste o que você mudaria nos textos. Separe o que é preferência de redação do que é erro.

### 6. Documente (1 h 30)

20. Escreva um `README_agente.md` de uma página: o que o agente faz, como chamar, as ferramentas, o que sai do computador, o custo por relatório medido no passo 16 e a lista do que a pessoa revisora confere antes do envio.
21. Faça o commit final. As pastas de saída ficam fora do repositório.

## Gabarito

Os números abaixo não dependem do modelo. Foram calculados pela solução de referência e conferem com os da Ponte.

**Relatório mensal de outubro de 2026, com setembro:**

| Indicador | Setembro | Outubro | Diferença |
| --- | --- | --- | --- |
| Disparos considerados | 13 | 14 | |
| Mensagens enviadas | 64.307 | 50.812 | -21,0% |
| Mensagens entregues | 62.952 | 50.116 | |
| Taxa de entrega | 97,9% | 98,6% | +0,7 p.p. |
| Taxa de abertura | 45,7% | 52,6% | +6,9 p.p. |
| Taxa de clique | 1,8% | 2,4% | +0,6 p.p. |

| Público, outubro | Disparos | Enviadas | Entregues | Entrega | Abertura | Clique |
| --- | --- | --- | --- | --- | --- | --- |
| Prospecção | 4 | 26.540 | 26.225 | 98,8% | 54,7% | 1,6% |
| Credenciamento | 5 | 16.860 | 16.701 | 99,1% | 59,1% | 3,6% |
| Pré-credenciado | 2 | 4.350 | 4.248 | 97,7% | 40,6% | 3,7% |
| Reativação | 1 | 2.900 | 2.780 | 95,9% | 12,6% | 1,0% |
| Expositor | 2 | 162 | 162 | 100,0% | 64,8% | 6,8% |

Em outubro, um disparo de 6 envios fica fora dos totais, e um reenvio de credenciamento tem clique de 20,1%, sinalizado como possível clique automático e mantido nos totais.

**Report pós-feira da Expo Modelo 2026:**

| Indicador | Valor |
| --- | --- |
| Credenciados (pessoas) | 560 |
| Visitantes (pessoas) | 218 |
| Taxa de visitação | 38,9% |
| Participantes do evento paralelo | 44 (20,2% dos visitantes) |

| Disparo de WhatsApp | Contatos | Receberam | Entrega | Tentativas com erro |
| --- | --- | --- | --- | --- |
| D1 · Convite para credenciamento (13/10) | 456 | 435 | 95,4% | 91 |
| D2 · Programação e rodada de negócios (17/10) | 456 | 441 | 96,7% | 76 |
| D3 · Lembrete na véspera da feira (19/10) | 456 | 429 | 94,1% | 101 |

| Grupo | Pessoas | Visitaram | Taxa de visitação |
| --- | --- | --- | --- |
| Recebeu ao menos uma mensagem de WhatsApp | 451 | 166 | 36,8% |
| Não recebeu | 109 | 52 | 47,7% |

A comparação entre quem recebeu e quem não recebeu WhatsApp não mede efeito: os grupos não foram sorteados. Um achado que diga que o WhatsApp reduziu a visitação, ou que a aumentaria, está errado pelo método da Skill.

O que depende do modelo, e que você avalia: os títulos-achado, os três achados e os próximos passos. O conferidor garante que todo número deles existe no gabarito; a qualidade da leitura fica com a sua revisão do passo 19.

## Critérios de aprovação

- [ ] Os dois relatórios gerados pelo agente passam no conferidor: "Projeto aprovado no conferidor."
- [ ] Os dois exemplos montados sem a API passam no conferidor, e o teste da trava recusou o texto com 40%.
- [ ] O agente usa pelo menos três ferramentas, ao menos uma de um servidor MCP, e as instruções incluem a Skill.
- [ ] Nenhuma resposta das ferramentas contém `@` ou sequências de 10 ou mais dígitos.
- [ ] A projeção do passo 18 não aparece em nenhuma apresentação.
- [ ] Nenhum achado do pós-feira afirma efeito do WhatsApp sobre a visitação.
- [ ] O custo de cada execução está registrado, e o `README_agente.md` informa o custo médio por relatório.
- [ ] O `README_agente.md` lista o que a pessoa revisora confere antes do envio.

## Entregável

1. O repositório com `agente_relatorios.py`, as ferramentas, as Skills e o `README_agente.md`.
2. As duas apresentações geradas pelo agente, com os `conferencia.csv`, e a saída do conferidor para cada uma.
3. Um registro de uma página com: a tabela das seis execuções do passo 16, os resultados dos passos 17 e 18, a lista de mudanças da revisão do passo 19 e o que você mudaria nas regras do agente.

## Desafios opcionais

**Preferências do cliente.** Acrescente a ferramenta de memória do módulo 4.6, para o agente lembrar preferências de cada cliente entre execuções, como "números absolutos antes de percentuais". Confira que a memória não guarda números de relatórios.

**Relatórios anteriores.** Dê ao agente a busca no acervo do módulo 4.8, para que os achados possam citar o que foi dito no mês anterior, com a fonte. Confira que os números do mês continuam vindo só das ferramentas de campanha.

**Revisor.** Acrescente um subagente revisor dos achados (módulo 4.7), que confere se cada próximo passo decorre do fato. Meça, com o método do 4.7, se ele melhora a sua avaliação do passo 19 e quanto custa.

**Agendamento.** Agende o relatório mensal para o dia 2 de cada mês, com uma das formas do módulo 4.5. O rascunho fica pronto para a sua revisão quando você chega.

## Bônus: agente de campanha

Fora da carga horária. O guia está em [`bonus-agente-campanha.md`](bonus-agente-campanha.md).

## O que este projeto ainda não resolve

O agente funciona na sua máquina, para você, com as exportações do curso. Para outra pessoa usar, faltam uma forma de entrega que dispense o terminal, um limite de custo por pessoa, mensagens de erro compreensíveis para quem não programa e a prova de que o agente continua acertando quando as exportações mudam.

Faltam também respostas a perguntas que este nível só mencionou: o que acontece se o nome de uma campanha na exportação contiver instruções escondidas? Como saber se uma mudança nas regras melhorou ou piorou os achados, em vez de confiar em três execuções? Como trocar de modelo sem quebrar o que funciona?

São os temas do Nível 5, cujo projeto final leva este agente à produção.

A solução de referência está em [`gabarito/agente_relatorios.py`](gabarito/agente_relatorios.py). As chamadas à API não foram executadas com uma chave real; o servidor MCP, as ferramentas locais, o verificador, a montagem e o conferidor foram executados e testados, e o caminho completo do agente foi executado contra um servidor simulado.

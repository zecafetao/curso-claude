# Nível 4 — Agentes

**Carga:** 37 h (29 h de módulos + 8 h de projeto) · **Pré-requisito:** Nível 3 — Desenvolvedor (API)

Ao final deste nível, você decide quando um agente compensa e constrói um que usa ferramentas, mantém o contexto e conclui tarefas longas sozinho, dentro de limites que você define no código.

No Nível 3, o seu script decidia cada passo e chamava o Claude onde uma regra fixa não resolvia. Aqui, o controle muda de lado: o Claude recebe um objetivo e um conjunto de ferramentas e decide a sequência. O que você construiu antes vira ferramenta: os indicadores da Ponte, o tratamento do Nível 3, os gráficos no padrão visual, a Skill do relatório do Nível 2.

O projeto é o agente de relatórios: das exportações do CRM ao rascunho do relatório mensal de e-mail ou do report pós-feira, com os números calculados por ferramentas e a lista de conferência de cada número.

## Módulos

| Módulo | Carga | O que você passa a fazer |
| --- | --- | --- |
| [4.1 Chamada única, workflow ou agente](4.1-chamada-workflow-ou-agente.md) | 2 h | Escolher a arquitetura mais simples que resolve cada tarefa do seu trabalho |
| [4.2 Laço agêntico e design de ferramentas](4.2-laco-agentico-e-ferramentas.md) | 5 h | Construir um agente de estudo de mercado com fontes, ferramenta de entrega e critério de parada |
| [4.3 MCP](4.3-mcp.md) | 5 h | Consultar um banco com SQL e publicar os indicadores da campanha como servidor MCP, usado no Claude Code, no app e nos seus agentes |
| [4.4 Claude Code](4.4-claude-code.md) | 5 h | Configurar o repositório com CLAUDE.md, permissões, hooks, Skills e subagentes, e entregar uma funcionalidade com testes |
| [4.5 Agent SDK e Managed Agents](4.5-agent-sdk-e-managed-agents.md) | 5 h | Publicar o agente em duas plataformas, entregar o resultado como arquivo e rodar por agendamento |
| [4.6 Gestão de contexto](4.6-gestao-de-contexto.md) | 2 h | Analisar fontes grandes sem estourar o contexto e lembrar as preferências de cada cliente entre sessões |
| [4.7 Multiagentes e computer use](4.7-multiagentes-e-computer-use.md) | 2 h | Medir se dividir o trabalho entre agentes compensa, e avaliar quando operar uma interface gráfica |
| [4.8 Busca em acervo próprio (RAG)](4.8-busca-em-acervo-proprio.md) | 3 h | Responder com base em relatórios e estudos anteriores, com a fonte de cada afirmação e a busca medida |
| [Projeto do nível](projeto.md) | 8 h | Construir o agente de relatórios, aprovado no conferidor |
| [Bônus: agente de campanha](bonus-agente-campanha.md) | Fora da carga | Da base bruta e do briefing à base pronta, à segmentação, ao e-mail e à landing page, para aprovação |

## Como este nível foi conferido

Leia esta seção antes de começar. Ela diz o que você pode tomar como certo e o que precisa medir.

Como no Nível 3, o ambiente em que o curso foi escrito não tinha uma chave da API. Por isso:

- **O que foi executado e testado:** todo o código que não chama um modelo. São o banco e as consultas SQL, o servidor MCP (com um cliente MCP real), os indicadores, o verificador de números, a montagem das apresentações e o conferidor do projeto, os gráficos, as ferramentas da feira grande, a ferramenta de memória, a busca por palavras e a medição dela, os hooks do Claude Code e o verificador de e-mail do bônus. Esses trechos têm testes automatizados em [`gabarito/test_nivel4.py`](gabarito/test_nivel4.py). O cadastro do servidor MCP no Claude Code e a verificação da conexão também foram executados.
- **O que foi executado contra uma API simulada:** todos os agentes que chamam a API (mercado, MCP, relatórios, análise longa com memória e edição de contexto, compactação, orquestrador e acervo) e os scripts do Managed Agents (configurar, executar, negar aprovações, baixar o arquivo e agendar). O servidor simulado confirma que as requisições são aceitas pelo SDK e que os laços, as ferramentas e os critérios de parada funcionam. Ele não reproduz o comportamento do modelo.
- **O que foi executado de verdade uma vez:** o agente do Agent SDK (módulo 4.5). O pacote traz o Claude Code embutido, que usou as credenciais do ambiente de escrita. A execução terminou com sucesso, custo informado de US$ 0,36, e a saída está em [`dados/exemplos/estudo_agent_sdk_execucao_real.md`](dados/exemplos/estudo_agent_sdk_execucao_real.md).
- **O que foi escrito a partir da documentação, sem execução:** o Claude Desktop com servidor local (4.3), o fluxo do GitHub Actions e o agendamento no Windows (4.4 e 4.5), o computer use (4.7) e a busca por significado com a Voyage AI (4.8). Cada trecho traz esse aviso.
- **O que não foi medido:** tudo o que depende das respostas do modelo, como os achados escritos, o número de voltas, o custo de cada execução e a comparação entre agente único e orquestrador. Nesses pontos, o exercício pede a sua medição, e o gabarito traz só os números que não dependem do modelo.

O código foi conferido com Python 3.13, `anthropic` 2.8, `mcp` 2.3 e `claude-agent-sdk` 0.2 (referência: novembro de 2026). Os recursos em beta citados no nível (Managed Agents, edição de contexto, compactação, memória) podem mudar de nome ou de parâmetro: confira a documentação antes de cada turma.

## O que você precisa

- O repositório dos seus scripts, com o ambiente virtual e os pacotes de [`gabarito/requirements.txt`](gabarito/requirements.txt).
- A chave da API configurada (módulo 3.1) e um limite de gasto no Console.
- O Claude Code (módulo P.5). O Claude Desktop é opcional (módulo 4.3).
- Para o módulo 4.8, uma conta no MongoDB Atlas para a chave da Voyage AI. Sem ela, o módulo tem um caminho alternativo.
- A pasta [`dados/`](dados/) deste nível, copiada para dentro do repositório com o nome `dados_n4`.

| Arquivo | Usado em | O que é |
| --- | --- | --- |
| `empresas_expositoras.csv` e `universo_sul_exemplo.csv` | 4.2 | Base de 120 expositores da Ponte e um universo de exemplo, com valores fictícios, para testar o cálculo de penetração |
| `desempenho_email_setembro.csv` e `desempenho_email_outubro.csv` | 4.3, 4.4, 4.7 e projeto | Exportações de e-mail por disparo, as mesmas da Ponte |
| `feira_credenciados.csv`, `feira_visitantes.csv`, `feira_inscritos_evento.csv` e `feira_whatsapp_tentativas.csv` | 4.3 e projeto | Exportações da Expo Modelo 2026, as mesmas da Ponte |
| `feira_grande/` | 4.6 | Credenciamento, visitação e WhatsApp da Expo Modelo Sul 2026, uma feira grande fictícia, compactados |
| `acervo/` e `perguntas_acervo.csv` | 4.8 | 10 relatórios e estudos fictícios e 24 perguntas de teste com o trecho esperado |
| `relatorio-mensal-email/` e `report-pos-feira/` | 4.4 e projeto | As Skills dos dois relatórios |
| `conferir_projeto_n4.py` | Projeto | O conferidor |
| `exemplos/` | 4.2, 4.5 e projeto | A execução real do Agent SDK e os dois relatórios montados com textos escritos à mão |

O banco da campanha (`campanha.db`) não vem pronto: você o monta no módulo 4.3 com `montar_banco.py`. Todos os dados são fictícios.

## Quanto custa fazer este nível

Estimativa, não medição: entre 15 e 30 dólares em créditos para fazer os exercícios e o projeto com o Claude Opus 5.5, repetindo as execuções que o enunciado pede. Os agentes fazem várias chamadas por tarefa, e os exercícios de comparação (4.7) e de repetição (projeto) multiplicam isso. A busca na web custa 10 dólares por mil buscas, e o Managed Agents cobra também o tempo de sessão. Os preços são de novembro de 2026.

Todos os agentes do gabarito têm limite de voltas, e os do módulo 4.5 têm teto em dólares. Rode cada exercício uma vez, anote o custo e só então faça as repetições.

## Soluções de referência

A pasta [`gabarito/`](gabarito/) tem uma solução para cada exercício e para o projeto. Use depois de tentar.

| Arquivo | Corresponde a |
| --- | --- |
| `claude_util.py` | Funções de apoio. Cópia do Nível 3, com o plano B para o executor de ferramentas e o custo das buscas na web |
| `agente_mercado.py` e `penetracao.py` | 4.2 |
| `montar_banco.py`, `indicadores.py`, `consultas_sql.py`, `servidor_campanha.py`, `cliente_mcp.py` e `agente_mcp.py` | 4.3 |
| `claude-code/` e `tipo_de_email.py` | 4.4: `CLAUDE.md`, `.claude/settings.json`, hooks, Skills, subagente e fluxo do GitHub Actions; a funcionalidade do exemplo |
| `agente_sdk.py`, `gerenciado_configurar.py`, `gerenciado_executar.py`, `gerenciado_agendar.py` e `agendamento/` | 4.5 |
| `fontes_feira.py` e `analise_longa.py` | 4.6 |
| `orquestrador.py` | 4.7 |
| `acervo.py`, `avaliar_busca.py`, `busca_semantica.py` e `agente_acervo.py` | 4.8 |
| `agente_relatorios.py`, `apresentacao.py`, `verificar_numeros.py`, `graficos_feira.py` e `montar_exemplos.py` | Projeto |
| `bonus/verificar_email.py` | Bônus |
| `test_nivel4.py` | Testes das partes que não chamam um modelo |
| `validacao.py`, `relatorio_mensal.py`, `graficos_relatorio.py`, `perfil_expositores.py`, `reconciliar.py` e `retomada.py` | Cópias das soluções da Ponte e do Nível 3, usadas pelos scripts acima |

Para rodar os testes, na pasta dos scripts, com a pasta `dados_n4` ao lado:

```bash
python montar_banco.py dados_n4 dados_n4/campanha.db
python -m pytest test_nivel4.py -q
```

## Entregáveis do nível

1. A classificação de oito tarefas do seu trabalho por arquitetura (4.1).
2. O agente de estudo de mercado, três estudos gerados e a tabela de penetração no universo de empresas parecidas (4.2).
3. As oito consultas SQL e o servidor MCP da campanha, usado no Claude Code e, se você tiver, no Claude Desktop (4.3).
4. O repositório configurado para o Claude Code e uma funcionalidade entregue com testes (4.4).
5. O agente publicado no Agent SDK e no Managed Agents, com agendamento e a comparação de responsabilidades (4.5).
6. A análise da feira grande com memória entre sessões e a medição da edição de contexto (4.6).
7. A medição de agente único contra orquestrador, com o teste de estresse (4.7).
8. A busca no acervo medida e o agente que responde com a fonte (4.8).
9. O agente de relatórios aprovado no conferidor (projeto).

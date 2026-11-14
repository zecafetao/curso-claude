# Nível 3 — Desenvolvedor (API)

**Carga:** 26 h (20 h de módulos + 6 h de projeto) · **Pré-requisito:** Ponte — Python para dados

Ao final deste nível, você chama o Claude de dentro dos seus scripts. O tratamento de uma base deixa de depender de copiar e colar no app: o script lê o arquivo, envia ao Claude só o que precisa de interpretação, confere a resposta, grava o resultado e informa quanto custou.

O nível usa o que você construiu na Ponte. As funções de validação e o script de tratamento continuam fazendo o trabalho determinístico. O Claude entra onde uma regra fixa não resolve: extrair dados de texto livre, classificar cargos escritos de qualquer jeito, responder perguntas sobre um PDF.

## Módulos

| Módulo | Carga | O que você passa a fazer |
| --- | --- | --- |
| [3.1 Primeira chamada](3.1-primeira-chamada.md) | 3 h | Chamar o Claude por código, manter uma conversa e calcular o custo de cada chamada |
| [3.2 Entradas multimodais](3.2-entradas-multimodais.md) | 3 h | Enviar PDFs e imagens e receber respostas com a página de cada afirmação |
| [3.3 Saídas estruturadas](3.3-saidas-estruturadas.md) | 3 h | Receber dados em um formato fixo, que o seu código lê sem tratamento manual |
| [3.4 Uso de ferramentas](3.4-uso-de-ferramentas.md) | 5 h | Dar ao Claude funções suas para consultar e validar bases, com limites definidos por você |
| [3.5 Custo e escala](3.5-custo-e-escala.md) | 3 h | Processar mil registros pelo menor custo: medir, remover repetição, usar cache e lote |
| [3.6 Robustez](3.6-robustez.md) | 3 h | Fazer um processamento sobreviver a erros, interrupções e recusas sem perder registros |
| [Projeto do nível](projeto.md) | 6 h | Construir o serviço que trata uma base bruta com o Claude e relata rejeições e custo |

## Como este nível foi conferido

Leia esta seção antes de começar. Ela diz o que você pode tomar como certo e o que precisa medir.

O ambiente em que o curso foi escrito não tinha uma chave da API. Por isso:

- **O que foi executado e testado:** todo o código que não chama a API. São as ferramentas, a medição de acerto, o cálculo de custo, a retomada e o tratamento da base. Esses trechos têm testes automatizados em [`gabarito/test_nivel3.py`](gabarito/test_nivel3.py).
- **O que foi executado contra uma API simulada:** todos os scripts que chamam a API. O servidor simulado devolve respostas no formato descrito na documentação oficial. Isso confirma que os scripts enviam requisições aceitas pelo SDK (a biblioteca oficial da Anthropic para Python), leem as respostas, percorrem os laços e tratam erros.
- **O que não foi medido:** o comportamento real do modelo. Taxas de acerto, quantidade de tokens e custos dependem das respostas reais e só aparecem quando você roda os exercícios.

A consequência prática: nos exercícios, os resultados que dependem do modelo são medidos por você contra um gabarito, com um mínimo para aprovação. Os números que não dependem do modelo têm valor exato no enunciado. Se um script do gabarito falhar com a API real, o erro mostrado indica o parâmetro recusado; a seção de erros do módulo 3.6 ensina a ler essa mensagem.

O código foi conferido com Python 3.13 e a versão 2.8 do SDK `anthropic` (referência: novembro de 2026).

## O que você precisa

- A pasta `tratamento-bases` da etapa Ponte, com o ambiente funcionando, o seu `validacao.py` e o seu `tratar_base.py`.
- Uma conta no Claude Console com créditos. A API é cobrada à parte da assinatura do app. O módulo 3.1 mostra como criar a conta, a chave e o limite de gasto.
- A pasta [`dados/`](dados/) deste nível, copiada para dentro de `tratamento-bases` com o nome `dados_n3`.

| Arquivo | Usado em | O que é |
| --- | --- | --- |
| `layout_importacao_crm.md` | 3.1 | O layout de importação do Nível 1 |
| `relatorio_mercado_embalagens.pdf` | 3.2 | Relatório de mercado fictício, com 6 páginas |
| `grafico_clique_por_publico.png` | 3.2 | Gráfico de taxa de clique por público |
| `contatos_texto_livre.csv` e `contatos_texto_livre_gabarito.csv` | 3.3 e 3.6 | 50 contatos recebidos em texto livre, e a extração correta |
| `base_contatos_tratada.csv` e `arquivo_com_erros.csv` | 3.4 | Base de 87 contatos já tratada, e uma cópia com erros conhecidos |
| `contatos_1000.csv`, `contatos_1000_gabarito.csv` e `regras_segmentos.md` | 3.5 | Mil contatos para classificar em segmentos, o gabarito e as regras do módulo 2.2 |
| `base_bruta_projeto.csv`, `descadastrados_projeto.xlsx`, `definicao_areas.md` e `cargos_gabarito.csv` | Projeto | Base bruta de 212 linhas, lista de descadastrados, definição das áreas e a área correta de cada cargo |
| `conferir_projeto_n3.py` e `saida_esperada_projeto/` | Projeto | Conferidor e saída esperada do projeto |

Todos os dados são fictícios.

## Quanto custa fazer este nível

Estimativa, não medição: menos de 10 dólares em créditos para fazer todos os exercícios e o projeto com o modelo Claude Opus 5.5, repetindo cada um algumas vezes. A conta usa os preços de novembro de 2026 e supõe respostas curtas. O módulo 3.1 ensina a calcular o custo real de cada chamada, e o limite de gasto configurado no Console impede surpresas.

## Soluções de referência

A pasta [`gabarito/`](gabarito/) tem uma solução para cada exercício e para o projeto. Use depois de tentar.

| Arquivo | Corresponde a |
| --- | --- |
| `claude_util.py` | Funções de apoio usadas em todo o nível. Pode ser copiado desde o início |
| `chat_terminal.py` | Exercício do 3.1 |
| `perguntar_pdf.py` e `ler_grafico.py` | Exercício do 3.2 |
| `extrair_contatos.py` e `avaliar_extracao.py` | Exercício do 3.3 |
| `ferramentas.py`, `laco_manual.py`, `assistente.py` e `calcular.py` | Exercício do 3.4 |
| `classificar_lote.py` | Exercício do 3.5 |
| `retomada.py`, `falhas_simuladas.py` e `extrair_com_retomada.py` | Exercício do 3.6 |
| `tratar_base_claude.py` | Projeto |
| `test_nivel3.py` | Testes das partes que não chamam a API |
| `validacao.py` e `tratar_base.py` | Cópias das soluções da Ponte, usadas pelos scripts acima |

## Entregáveis do nível

1. Um chat de terminal com o layout do CRM nas instruções, com histórico e custo por conversa (3.1).
2. Um script de perguntas sobre PDF com a página de cada resposta, e a tabela de conferência (3.2).
3. Um extrator de contatos com saída estruturada e a medição de acerto contra o gabarito (3.3).
4. Um assistente com três ferramentas suas e o registro dos testes, incluindo os pedidos que ele deve recusar (3.4).
5. A classificação de mil contatos em lote, com a planilha de custo por alternativa (3.5).
6. A extração do 3.3 com retomada, e o registro do teste de interrupção (3.6).
7. O serviço de tratamento de bases com o Claude, aprovado no conferidor (projeto).

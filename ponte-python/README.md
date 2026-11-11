# Ponte — Python para dados

**Carga:** 20 h (16 h de módulos + 4 h de projeto) · **Pré-requisito:** Nível 2 e lógica de programação

Ao final desta etapa, você escreve e roda scripts em Python que leem, limpam e exportam bases. É o mínimo necessário para usar a API do Claude no Nível 3, e já resolve o trabalho determinístico dos seus fluxos: padronizar campos, remover duplicados e gerar o arquivo de importação.

A etapa parte de quem já tem lógica de programação e usa o Claude como tutor durante os exercícios.

## Módulos

| Módulo | Carga | O que você passa a fazer |
| --- | --- | --- |
| [P.1 Ambiente e primeiros passos](P.1-ambiente-e-primeiros-passos.md) | 2 h | Instalar as ferramentas e rodar um script que lê um arquivo |
| [P.2 Lógica em Python](P.2-logica-em-python.md) | 4 h | Escrever funções que validam e padronizam e-mail e telefone |
| [P.3 Dados com pandas](P.3-dados-com-pandas.md) | 5 h | Tratar uma base inteira: limpar, filtrar, remover duplicados, cruzar e exportar |
| [P.4 APIs e JSON](P.4-apis-e-json.md) | 3 h | Consultar um serviço externo e enriquecer a base com cidade e UF |
| [P.5 Git e Claude Code](P.5-git-e-claude-code.md) | 2 h | Versionar o código e programar com o Claude Code, com testes |
| [Projeto da etapa](projeto.md) | 4 h | Construir o script que gera o arquivo de importação e o relatório de rejeições |

## Como esta etapa é diferente

- **Você escreve código.** Cada módulo termina com um script seu, que roda no seu computador.
- **Os dados não saem do computador.** Os scripts tratam os arquivos localmente. Só no módulo P.4 há uma consulta externa, e ela envia apenas CEPs.
- **Tudo tem conferência automática.** Os exercícios trazem o resultado esperado, e dois deles trazem um conferidor que você roda.

## O que você precisa

- Um computador em que você possa instalar programas. As instruções são para Windows, com as diferenças para macOS indicadas.
- A pasta [`dados/`](dados/), com arquivos fictícios:

| Arquivo | Usado em | O que é |
| --- | --- | --- |
| `base_bruta_contatos.csv` | Todos | Base de 120 contatos com os problemas típicos de uma base recebida de cliente |
| `descadastrados.xlsx` | P.3 e projeto | Lista de e-mails que pediram descadastro |
| `casos_p2.csv` e `conferir_p2.py` | P.2 | Casos de teste e conferidor das suas funções |
| `ceps_referencia.csv` | P.4 e projeto | Resultado das consultas de CEP, para comparar ou usar se a API estiver fora do ar |
| `conferir_projeto.py` e `saida_esperada/` | Projeto | Conferidor e saída esperada do projeto |

- O arquivo [`requirements.txt`](requirements.txt), com as bibliotecas da etapa.

O layout de importação usado como alvo é o [`layout_importacao_crm.md`](../nivel-1-fundamentos/dados/layout_importacao_crm.md) do Nível 1.

## Soluções de referência

A pasta [`gabarito/`](gabarito/) tem uma solução de referência para cada exercício e para o projeto. Todas foram executadas e conferidas com Python 3.13 e pandas 3.0 (referência: novembro de 2026).

Use o gabarito depois de tentar. Ler a solução antes de escrever a sua ensina a reconhecer código, não a escrevê-lo.

| Arquivo | Corresponde a |
| --- | --- |
| `contar_linhas.py` | Exercício do P.1 |
| `validacao.py` | Exercício do P.2 e funções do projeto |
| `p3_tratamento_inicial.py` | Exercício do P.3 |
| `consultar_cep.py` | Exercício do P.4 |
| `test_validacao.py` | Exercício do P.5 |
| `tratar_base.py` | Projeto |

## Entregáveis da etapa

1. Um script que conta linhas e colunas de um CSV (P.1).
2. Um módulo com três funções de validação, aprovado em 25 casos (P.2).
3. Um script de tratamento inicial com pandas, com os números esperados (P.3).
4. Uma tabela de CEPs consultados e o cruzamento com a base (P.4).
5. Um repositório com os scripts versionados e testes automatizados (P.5).
6. O script de tratamento completo, aprovado no conferidor (projeto).

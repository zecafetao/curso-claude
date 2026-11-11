# Projeto da Ponte — Tratamento completo de uma base para importação

**Carga:** 4 h

## Objetivo

Construir um script reutilizável que recebe uma base bruta de contatos e devolve o arquivo pronto para importação no CRM, mais um relatório dos registros rejeitados e dos campos corrigidos.

O projeto reúne os cinco módulos: funções de padronização (P.2), tratamento com pandas (P.3), enriquecimento opcional por CEP (P.4) e código versionado com testes (P.5).

## Material

Na pasta [`dados/`](dados/):

- `base_bruta_contatos.csv`: 120 contatos fictícios, com os problemas típicos de uma base recebida.
- `descadastrados.xlsx`: e-mails que pediram descadastro.
- `conferir_projeto.py` e `saida_esperada/`: o conferidor e a saída correta.

O alvo é o [layout de importação do CRM](../nivel-1-fundamentos/dados/layout_importacao_crm.md).

## Como o script é chamado

```
python tratar_base.py dados/base_bruta_contatos.csv dados/descadastrados.xlsx saida
```

O terceiro valor é a pasta em que os arquivos de saída são gravados. O script cria a pasta se ela não existir.

## Arquivos de saída

| Arquivo | Conteúdo | Colunas |
| --- | --- | --- |
| `importar.csv` | As linhas aprovadas, no layout do CRM | `email`, `nome`, `sobrenome`, `telefone`, `empresa`, `cnpj`, `cargo`, `area`, `cidade`, `uf`, `origem`, `consentimento`, `data_consentimento` |
| `rejeitados.csv` | As linhas que não serão importadas | `linha`, `email_bruto`, `motivo` |
| `avisos.csv` | Campos corrigidos de forma conservadora nas linhas aprovadas | `linha`, `email`, `aviso` |
| `resumo.txt` | Os totais, que o script também mostra na tela | — |

Todos os CSVs são separados por ponto e vírgula, em UTF-8.

`linha` é o número da linha no arquivo original. O cabeçalho é a linha 1, e o primeiro contato é a linha 2. Com esse número, quem recebe o relatório encontra o registro na base.

## Regras de padronização

Cada regra vira uma função no seu `validacao.py`. As de e-mail, telefone e CEP você já tem.

| Campo do layout | Origem na base | Regra |
| --- | --- | --- |
| `email` | `E-mail` | Sem espaços nas pontas, em minúsculas |
| `nome` e `sobrenome` | `Nome Completo` | Remova espaços das pontas e reduza espaços repetidos. Ponha a inicial de cada palavra em maiúscula e o restante em minúsculas, exceto as partículas `de`, `da`, `do`, `dos`, `das` e `e`, que ficam em minúsculas quando não são a primeira palavra. O nome é a primeira palavra; o sobrenome é o restante e pode ficar vazio |
| `telefone` | `Telefone` | A função do módulo P.2. O que não puder ser padronizado fica vazio |
| `empresa` | `Empresa` | Limpe os espaços e remova do fim do nome os sufixos `LTDA`, `S.A.`, `S/A`, `SA`, `ME`, `EIRELI` e `EPP`, em qualquer combinação de maiúsculas, com ou sem ponto final, quantas vezes aparecerem. Remova também traço, vírgula e espaço que sobrarem no fim. Um nome de uma palavra só não é alterado |
| `cnpj` | `CNPJ` | Fique só com os dígitos. Se restarem de 12 a 14, complete com zeros à esquerda até 14. Caso contrário, deixe vazio |
| `cargo` | `Cargo` | Limpe os espaços e mantenha como informado |
| `area` | `Cargo` | A tabela de palavras-chave abaixo |
| `cidade` | `Cidade` | A mesma capitalização dos nomes |
| `uf` | `UF` | Sem espaços, em maiúsculas. Se não for uma das 27 UFs, deixe vazio |
| `origem` | `Origem` | Limpe os espaços e passe para minúsculas. Se o texto começar com uma das opções do layout, também em minúsculas, use essa opção. Caso contrário, a origem não é reconhecida |
| `consentimento` e `data_consentimento` | `Aceita comunicação` e `Data aceite` | Há aceite quando o valor, sem espaços e em minúsculas, é `s` ou `sim`. A data é válida quando existe e está em `DD/MM/AAAA` ou `AAAA-MM-DD`; ela é gravada em `AAAA-MM-DD`. Com aceite e data válida, o consentimento é `S`. Em qualquer outro caso, é `N` e a data fica vazia |

### Área a partir do cargo

Passe o cargo para minúsculas e percorra a tabela de cima para baixo. A área é a da primeira linha que tiver uma palavra-chave contida no cargo. Se nenhuma servir, a área é `Outros`.

| Ordem | Área | Palavras-chave |
| --- | --- | --- |
| 1 | `Diretoria` | `diretor`, `sócio`, `socio`, `proprietári`, `proprietari`, `presidente`, `ceo` |
| 2 | `Compras` | `compra`, `suprimentos`, `procurement`, `supply` |
| 3 | `Produção` | `produção`, `producao`, `industrial`, `qualidade`, `engenh`, `p&d`, `desenvolvimento` |
| 4 | `Marketing` | `marketing`, `marca`, `produto`, `trade`, `comunicação`, `comunicacao` |
| 5 | `Comercial` | `vendas`, `comercial`, `representante`, `key account` |

A ordem resolve os cargos que cabem em duas áreas: `Diretora de Marketing` é `Diretoria`.

## Regras de rejeição

Uma linha rejeitada não vai para o `importar.csv`. Aplique as regras nesta ordem e registre só o primeiro motivo que servir.

| Ordem | Motivo | Condição |
| --- | --- | --- |
| 1 | `e-mail inválido` | O e-mail padronizado não passa na validação do módulo P.2 |
| 2 | `nome ausente` | O nome ficou vazio |
| 3 | `origem não reconhecida` | A origem não corresponde a nenhuma opção do layout |
| 4 | `descadastrado` | O e-mail consta na lista de descadastrados, comparado depois de padronizado |
| 5 | `e-mail repetido` | Entre as linhas que continuam válidas, o e-mail já apareceu em uma linha anterior |

A ordem importa em dois pontos:

- Uma linha com e-mail inválido e sem nome é registrada como `e-mail inválido`.
- Os repetidos são procurados só entre as linhas que passaram pelas quatro primeiras regras. Uma linha válida não pode ser eliminada por repetir o e-mail de uma linha que já foi rejeitada por outro motivo.

## Avisos

Um aviso registra que um campo foi corrigido de forma conservadora em uma linha aprovada. A linha é importada, e o relatório informa o que foi perdido.

| Aviso | Condição |
| --- | --- |
| `telefone descartado` | Havia um telefone e ele não pôde ser padronizado |
| `cnpj descartado` | Havia um CNPJ e ele não tinha de 12 a 14 dígitos |
| `consentimento rebaixado` | Havia aceite, mas sem data válida. O consentimento passou a `N` |

A terceira regra é uma decisão de negócio. O layout só aceita `S` com a data do aceite, e sem a data não há registro que comprove o consentimento. O tratamento escolhe o lado seguro: o contato entra sem permissão para receber comunicações, e o aviso permite ao cliente localizar o registro original. Em um trabalho real, confirme essa regra com o cliente antes de aplicar.

## Passos

### 1. Planeje (30 min)

1. Releia o seu `tratamento_inicial.py` do módulo P.3. Ele é o ponto de partida.
2. Liste as funções que faltam no `validacao.py`.
3. Para cada função nova, escreva de três a cinco casos de teste antes do código, incluindo um caso de fronteira.

### 2. Escreva as funções e os testes (1 h 30)

4. Escreva cada função e os testes dela no `test_validacao.py`. Rode `python -m pytest` a cada função.
5. Faça um commit por função ou por grupo pequeno de funções.

Você pode usar o Claude Code como no módulo P.5. Se usar, peça uma função por vez, com os testes, e leia o código antes de aceitar. As decisões sobre as regras já estão tomadas neste enunciado; se encontrar um caso que ele não cobre, a decisão é sua e deve ficar registrada.

### 3. Escreva o script (1 h 15)

6. Organize o `tratar_base.py` em funções: ler, padronizar, classificar as rejeições, montar os avisos e gravar.
7. Guarde o número da linha original logo depois da leitura, antes de qualquer filtro.
8. Faça o script mostrar o resumo na tela e gravá-lo no `resumo.txt`.
9. Rode e compare com o gabarito abaixo.

### 4. Confira (45 min)

10. Rode o conferidor a partir da pasta `dados`, informando a pasta de saída do seu script:

```
cd dados
python conferir_projeto.py ../saida
```

11. Para cada diferença apontada, descubra qual regra o seu código aplicou de outro jeito. O conferidor mostra a linha esperada e a obtida.
12. Depois de aprovado, faça o commit final e envie ao GitHub.

## Gabarito

Calculado pela solução de referência e conferido por um segundo cálculo independente.

```
Linhas lidas: 120
Linhas para importar: 87
Linhas rejeitadas: 33
  descadastrado: 8
  e-mail inválido: 6
  e-mail repetido: 12
  nome ausente: 3
  origem não reconhecida: 4
Avisos: 22
  cnpj descartado: 4
  consentimento rebaixado: 9
  telefone descartado: 9
```

Conferências adicionais no `importar.csv`:

| Verificação | Valor |
| --- | --- |
| Contatos por área | Compras 18, Diretoria 17, Produção 16, Comercial 13, Marketing 13, Outros 10 |
| Consentimento | 57 com `S` e 30 com `N` |
| Cidade vazia | 33 linhas |
| UF vazia | 36 linhas: as 33 sem cidade e 3 com o valor `XX`, que não é uma UF |

A conta fecha: 120 lidas = 87 para importar + 33 rejeitadas.

Erros frequentes:

| Sintoma | Causa provável |
| --- | --- |
| 4 linhas com `nome ausente` | A ordem das regras: uma linha sem nome também tem e-mail inválido e deve ficar no primeiro motivo |
| 6 descadastrados em vez de 8 | A lista de descadastrados não foi padronizada: dois e-mails estão em maiúsculas |
| Menos de 12 repetidos | E-mails comparados antes de padronizar: as repetições diferem em maiúsculas e espaços |
| 86 linhas para importar e 13 repetidos | Repetidos procurados na base inteira, e não só entre as linhas válidas. A linha 35 repete o e-mail da linha 33, que já foi rejeitada por nome ausente, e deve ser importada |
| `Da Silva` no sobrenome | Uso de `.str.title()` em vez da regra das partículas |
| `Alimentos Alfa LTDA` e `Alimentos Alfa` como empresas diferentes | Sufixo não removido |
| CNPJ com 13 dígitos | Faltou completar com zero à esquerda |
| Mais de 57 linhas com `S` | Aceite sem data válida mantido como `S` |

## Critérios de aprovação

- [ ] O conferidor informa "Projeto aprovado no conferidor".
- [ ] O resumo na tela é igual ao do gabarito.
- [ ] O script não altera os arquivos de entrada e roda do começo ao fim sem intervenção.
- [ ] Cada regra de padronização está em uma função própria no `validacao.py`.
- [ ] Há pelo menos um teste para cada função, e todos passam.
- [ ] O código está no seu repositório privado, com commits que descrevem cada etapa.
- [ ] Você consegue explicar, para qualquer linha do `rejeitados.csv`, por que ela foi rejeitada.

## Entregável

1. O repositório com `validacao.py`, `tratar_base.py` e `test_validacao.py`.
2. A pasta de saída gerada e a mensagem do conferidor.
3. Um registro de meia página com: as diferenças que o conferidor apontou na primeira execução, a causa de cada uma e os casos que o enunciado não cobria e como você decidiu.

## Desafio opcional — Enriquecer pelo CEP

Aceite um quarto valor na chamada do script, com a tabela de CEPs do módulo P.4:

```
python tratar_base.py dados/base_bruta_contatos.csv dados/descadastrados.xlsx saida dados/ceps_referencia.csv
```

Quando o CEP da linha estiver na tabela com a situação `encontrado`, a cidade e a UF passam a ser as oficiais, mesmo que a base traga outro valor. Nas demais linhas, vale o que veio da base.

Resultado esperado: as mesmas 87 linhas para importar, com 7 cidades vazias e 7 UFs vazias, em vez de 33 e 36.

## O que este projeto ainda não resolve

O cargo `Brand Manager` foi classificado como `Outros`. A tabela de palavras-chave não conhece o termo, e nenhuma lista fixa cobre todos os cargos que uma base real traz. Esse é o limite do trabalho determinístico.

É também o ponto de partida do Nível 3: o código continua fazendo o que tem regra clara, e o Claude, chamado pela API, classifica os casos que a regra não alcança. Os cargos distintos saem do computador sem nenhum outro dado do contato, como você aprendeu no módulo 1.5.

A solução de referência está em [`gabarito/tratar_base.py`](gabarito/tratar_base.py) e [`gabarito/validacao.py`](gabarito/validacao.py).

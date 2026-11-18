# Bônus do Nível 4 — Agente de campanha

**Opcional, fora da carga horária.** Estimativa: 8 a 12 h.

## Objetivo

Construir um agente que recebe uma base bruta de contatos e um briefing de campanha e entrega, para aprovação humana, a base pronta para importação no CRM, a proposta de segmentação, o e-mail em HTML e a landing page.

O bônus reaproveita o serviço de tratamento do projeto do Nível 3 como ferramenta e a estrutura do agente de relatórios: ferramentas que calculam, o modelo que escreve, verificação por código antes da entrega e nenhuma ação fora do computador sem você.

## Por que é um bônus

O agente de campanha encadeia quatro entregas de natureza diferente, e cada uma já foi feita em um módulo anterior. O que ele acrescenta é a orquestração. Pelo critério do módulo 4.1, boa parte dessa sequência é fixa e poderia ser um workflow. O agente se justifica quando o briefing muda o caminho: um público que exige outra regra de segmentação, uma base que chega com colunas trocadas, uma campanha sem landing page.

Faça este bônus depois do projeto, se quiser praticar a arquitetura em um problema mais aberto.

## Material

| Arquivo | Onde está | Uso |
| --- | --- | --- |
| `base_bruta_projeto.csv`, `descadastrados_projeto.xlsx` | `nivel-3-desenvolvedor-api/dados/` | A base bruta |
| `tratar_base_claude.py` e as funções da Ponte | `nivel-3-desenvolvedor-api/gabarito/` ou as suas versões | O tratamento, que vira ferramenta |
| `briefing_campanha.md` | `nivel-1-fundamentos/dados/` | O briefing da campanha de credenciamento |
| `regras_segmentos.md`, `guia_de_tom.md`, `email_referencia.html` | `nivel-2-usuario-avancado/dados/` | As regras de segmentação, o tom e um e-mail aprovado como exemplo |
| [`gabarito/bonus/verificar_email.py`](gabarito/bonus/verificar_email.py) | Este nível | Confere por código 11 dos 15 itens da lista do módulo 2.7 |

## Arquitetura sugerida

| Ferramenta | O que faz | Devolve ao modelo |
| --- | --- | --- |
| `tratar_base` | Roda o serviço do Nível 3 sobre a base bruta e grava a saída | O resumo: linhas, rejeições e motivos, avisos, custo. Nunca as linhas |
| `contar_contatos` | Conta os contatos tratados por área, UF e consentimento, com os filtros pedidos | Contagens |
| `ler_documento` | Lê o briefing, o guia de tom ou as regras de segmentação, pelo nome | O texto do documento |
| `gravar_proposta_de_segmentacao` | Grava a proposta, com a regra de cada segmento e as contagens calculadas por `contar_contatos` | Gravado ou a lista de problemas |
| `gravar_email` | Roda o `verificar_email` e grava o HTML e a versão de texto só se todos os itens automáticos passarem | Gravado ou os itens que falharam |
| `gravar_landing_page` | Confere o formulário, o campo de consentimento e os parâmetros de campanha nos links, e grava | Gravado ou a lista de problemas |

Todas as ferramentas gravam só na pasta de saída da campanha. Nenhuma importa no CRM, dispara e-mail ou publica página: essas três ações continuam com você, depois da aprovação.

**O que sai do computador.** O briefing, o guia de tom, as regras de segmentação, os cargos distintos (que o serviço do Nível 3 já envia) e as contagens. Nenhum nome, e-mail ou telefone.

## Uma limitação dos dados, de propósito

As regras de segmentação do Nível 2 começam pelo setor da empresa: setor fora da lista de setores-alvo é `ForaDoPerfil`. A base do Nível 3 não tem coluna de setor. Um bom agente não inventa o setor a partir do nome da empresa: ele aplica as regras que os dados permitem (cargo e área) e registra, na proposta, que o filtro de setor depende de enriquecer a base pelo CNPJ, na plataforma de big data, antes do disparo.

Inclua essa limitação nos testes: se a proposta trouxer contagens por setor, alguma coisa foi inventada.

## Passos sugeridos

1. Escreva o pedido de exemplo: "Prepare a campanha de credenciamento do briefing para a base bruta do projeto do Nível 3".
2. Liste as decisões que o agente toma e as que o código toma, como no projeto.
3. Escreva as ferramentas, uma por vez, testando cada uma sem a API.
4. Escreva as instruções do agente com as regras do projeto: números das ferramentas, verificação antes de gravar, nenhuma ação externa, lacunas registradas.
5. Rode o agente, confira cada entrega com os critérios abaixo e corrija.
6. Rode com um briefing diferente, escrito por você, para um público de expositores. Veja o que muda no caminho do agente.

## Critérios de aprovação

- [ ] A base tratada confere com o gabarito do projeto do Nível 3: 212 linhas lidas, 179 para importar, 33 rejeitadas, 44 avisos. O conferidor do Nível 3 aprova a saída.
- [ ] A lista de disparo considera só os contatos com consentimento: 121 dos 179.
- [ ] Na proposta de segmentação, cada contato com consentimento está em um único segmento, as contagens vêm de `contar_contatos` e somam 121, e a falta do setor está registrada como lacuna.
- [ ] O `verificar_email.py` aprova o e-mail nos itens 1 a 11, e você conferiu os itens 12 a 15 lendo.
- [ ] O botão do e-mail e o da landing page levam ao endereço do briefing, com parâmetros de campanha (módulo 2.7).
- [ ] A landing page tem formulário, campo de consentimento não marcado previamente e link para a política de privacidade.
- [ ] Nenhuma ferramenta importa, dispara ou publica. Você aponta, no código, por que isso não é possível.
- [ ] O custo de cada execução está registrado.

Com a classificação correta das áreas, os 121 contatos com consentimento se dividem assim: Diretoria 23, Comercial 23, Produção 23, Marketing 22, Compras 21 e Outros 9. As suas contagens podem diferir nas áreas em que o Claude classificou um cargo de outro jeito; a soma não muda.

## O que conferir na revisão

O agente de campanha produz quatro entregas que vão para clientes e contatos. A revisão humana confere, nesta ordem: as rejeições e avisos do tratamento (`revisar_areas.csv` do Nível 3), a regra de cada segmento contra o briefing, o e-mail e a landing page lidos como o contato os leria, e os links.

O Nível 5 traz os evals e os testes de segurança do agente de relatórios. O bônus do Nível 5 repete esses testes no agente de campanha.

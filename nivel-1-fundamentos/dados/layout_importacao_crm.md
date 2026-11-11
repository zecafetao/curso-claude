# Layout de importação de contatos no CRM (fictício)

Arquivo aceito: CSV em UTF-8, separado por ponto e vírgula, com cabeçalho na primeira linha e uma linha por contato.

| Campo | Obrigatório | Formato | Regra |
| --- | --- | --- | --- |
| `email` | Sim | texto, minúsculas | Chave do contato. Sem espaços. Um endereço por linha. Linhas com e-mail repetido são rejeitadas. |
| `nome` | Sim | texto | Primeiro nome com inicial maiúscula. |
| `sobrenome` | Não | texto | Iniciais maiúsculas, exceto "de", "da", "do", "dos", "das" e "e". |
| `telefone` | Não | `+55DDDNÚMERO` | Só dígitos após o `+`. Celular com 9 dígitos. Exemplo: `+5511987654321`. |
| `empresa` | Não | texto | Nome fantasia, sem "LTDA", "S.A." ou "ME". |
| `cnpj` | Não | 14 dígitos | Só dígitos, com zeros à esquerda. |
| `cargo` | Não | texto | Como informado pelo contato. |
| `area` | Não | lista | Um de: `Compras`, `Produção`, `Marketing`, `Comercial`, `Diretoria`, `Outros`. |
| `cidade` | Não | texto | Nome oficial do município, com acentos. |
| `uf` | Não | 2 letras | Sigla em maiúsculas. |
| `origem` | Sim | lista | Um de: `Credenciamento`, `Expositor`, `Site`, `Evento`, `Compra de base`. |
| `consentimento` | Sim | `S` ou `N` | `S` só quando existe registro de aceite para receber comunicações. |
| `data_consentimento` | Se consentimento = `S` | `AAAA-MM-DD` | Data do aceite. |

## Motivos de rejeição mais comuns

1. E-mail inválido (sem `@`, com espaço ou com domínio incompleto).
2. E-mail repetido no arquivo.
3. Telefone fora do formato.
4. `area` ou `origem` com valor fora da lista.
5. `consentimento` igual a `S` sem `data_consentimento`.

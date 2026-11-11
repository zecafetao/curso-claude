# P.7 Reconciliação de bases sem chave comum

**Carga:** 3 h (1 h de leitura e experimentação, 2 h de exercício)

## Objetivo

Juntar bases que não têm um identificador em comum: medir sobreposições, encontrar a mesma pessoa registrada de formas diferentes, montar um funil que conta pessoas e analisar disparos em que tentativa e contato são coisas distintas.

## Por que importa no seu trabalho

Um report pós-feira junta o credenciamento do CRM, a leitura de credenciais na entrada, as inscrições de um evento pago em outra plataforma e as listas de disparo de WhatsApp. Nenhuma dessas fontes foi feita para conversar com as outras. Somar os totais conta a mesma pessoa várias vezes. Cruzar só por e-mail perde quem usou um endereço diferente em cada lugar. O número final do relatório depende de como a identidade é resolvida, e por isso o método precisa ser explícito e defensável.

## Conteúdo

Os trechos das seções 1 a 8 continuam um ao outro, com tabelas pequenas escritas no próprio código. Escreva-os em um arquivo `explorar_reconciliacao.py`.

### 1. Soma não é união

```python
import pandas as pd

credenciados = pd.DataFrame(
    {
        "nome": ["Ana Souza", "João Lima", "Carla Reis", "Paulo Dias"],
        "email": [
            "ana.souza@alfa.example",
            "joao.lima@beta.example",
            "carla.reis@gama.example",
            "paulo.dias@gama.example",
        ],
        "telefone": ["+5511999900001", "+5521999900002", "+551133330000", "+551133330000"],
    }
)
visitantes = pd.DataFrame(
    {
        "nome": ["ANA SOUZA", "JOAO LIMA", "Marta Nunes"],
        "email": ["ana.souza@alfa.example", "joaolima77@correio.example", "marta.nunes@delta.example"],
        "telefone": ["+5511999900001", "+5521999900002", ""],
    }
)

print(len(credenciados) + len(visitantes))     # 7
```

A soma das linhas é 7. Lendo as tabelas, as pessoas são 5: Ana e João aparecem nas duas. Ana tem o mesmo e-mail nas duas bases. João se credenciou com o e-mail da empresa e, na entrada, informou o pessoal.

Guarde três números, porque eles são diferentes e os três aparecem em relatórios:

| Número | O que conta | Aqui |
| --- | --- | --- |
| Soma | Linhas de todas as bases | 7 |
| União por e-mail | E-mails distintos | 6 |
| Pessoas | Indivíduos, depois de resolver a identidade | 5 |

### 2. Conjuntos

Um **conjunto** (`set`) guarda valores sem repetição e tem as operações de que a reconciliação precisa.

```python
emails_cred = set(credenciados["email"])
emails_vis = set(visitantes["email"])

print(len(emails_cred | emails_vis))     # 6: união, quem está em pelo menos uma
print(len(emails_cred & emails_vis))     # 1: interseção, quem está nas duas
print(emails_vis - emails_cred)          # diferença: está em visitantes e não em credenciados
```

| Operação | Símbolo | Pergunta que responde |
| --- | --- | --- |
| União | `\|` | Quantos são ao todo, sem repetir? |
| Interseção | `&` | Quantos estão nas duas bases? |
| Diferença | `-` | Quem está em uma e não na outra? |

Com três bases, a sobreposição tripla é `a & b & c`.

Por e-mail, só Ana está nas duas bases. João ficou de fora da interseção e entrou duas vezes na união.

### 3. Chaves de comparação

Uma **chave** é o valor usado para dizer que dois registros são a mesma coisa. Cada candidata tem um defeito:

| Chave | Vantagem | Defeito |
| --- | --- | --- |
| E-mail | Único por pessoa na maioria dos casos | A mesma pessoa usa o corporativo e o pessoal |
| Telefone | Muda pouco | Colegas informam o mesmo telefone da empresa |
| Nome | Sempre preenchido | Homônimos; grafias diferentes |

Toda chave precisa ser padronizada antes da comparação. Para e-mail e telefone, você já tem as funções. Para o nome, a comparação pede minúsculas, sem acentos e sem espaços repetidos:

```python
import unicodedata


def chave_nome(texto):
    """Nome em minúsculas, sem acentos e sem espaços repetidos, para comparação."""
    decomposto = unicodedata.normalize("NFKD", str(texto))
    sem_acento = "".join(letra for letra in decomposto if not unicodedata.combining(letra))
    return " ".join(sem_acento.lower().split())


print(chave_nome("  JOÃO  Lima "))     # joao lima
print(chave_nome("JOAO LIMA"))         # joao lima
```

`unicodedata.normalize("NFKD", ...)` separa cada letra acentuada em letra e acento, e a linha seguinte descarta os acentos. A chave serve só para comparar. O nome que vai para o CRM continua sendo o original, tratado pela regra do projeto.

### 4. Empilhar as bases com a origem

Para resolver a identidade, todos os registros ficam em uma tabela só, com uma coluna que diz de onde cada um veio.

```python
credenciados["fonte"] = "credenciados"
visitantes["fonte"] = "visitantes"

registros = pd.concat([credenciados, visitantes], ignore_index=True)
registros["nome_chave"] = registros["nome"].map(chave_nome)

print(registros[["fonte", "email", "telefone", "nome_chave"]])
```

`ignore_index=True` renumera as linhas. Sem isso, as duas tabelas trariam a mesma numeração e os passos seguintes se confundiriam.

### 5. Resolver a identidade

A regra deste módulo: **a identidade parte do e-mail; registros com o mesmo telefone e o mesmo nome são a mesma pessoa, ainda que os e-mails sejam diferentes.**

```python
registros["pessoa"] = registros["email"]

com_telefone = registros["telefone"] != ""
chave = registros["telefone"] + "|" + registros["nome_chave"]
primeiro_email = registros[com_telefone].groupby(chave[com_telefone])["email"].transform("first")
registros.loc[com_telefone, "pessoa"] = primeiro_email

print(registros[["fonte", "email", "pessoa"]])
print(registros["email"].nunique(), registros["pessoa"].nunique())     # 6 5
```

Passo a passo:

1. Toda linha começa com `pessoa` igual ao próprio e-mail.
2. A chave composta junta telefone e nome. Só vale para linhas com telefone.
3. `groupby(...).transform("first")` devolve, para cada linha, o primeiro e-mail do grupo dela. Diferente do `agg`, o `transform` mantém uma linha de resultado para cada linha de entrada.
4. As linhas com telefone recebem esse e-mail como identificador da pessoa.

Os dois registros de João agora têm a mesma `pessoa`. A contagem passou de 6 e-mails para 5 pessoas.

Por que telefone **e** nome, e não um só:

```python
so_telefone = registros[com_telefone].groupby("telefone")["email"].transform("first")
print(so_telefone.nunique())     # 3
```

Com o telefone sozinho, os seis registros com telefone viram 3 pessoas: Carla e Paulo, colegas que informaram o telefone da empresa, foram fundidos em um. Com o nome sozinho, o erro seria o oposto em uma base grande: dois "João Lima" de empresas diferentes virariam um. As duas condições juntas erram menos.

Nenhuma regra de identidade é perfeita. O objetivo é uma regra que erre pouco, sempre do mesmo jeito, e que esteja escrita.

### 6. Do registro à pessoa: o funil

Com a coluna `pessoa`, as contagens passam a ser de indivíduos.

```python
pessoas_cred = set(registros.loc[registros["fonte"] == "credenciados", "pessoa"])
pessoas_vis = set(registros.loc[registros["fonte"] == "visitantes", "pessoa"])

todos = pessoas_cred | pessoas_vis
print(len(todos), len(pessoas_vis), len(pessoas_cred & pessoas_vis))     # 5 3 2
print(f"{100 * len(pessoas_vis) / len(todos):.1f}% visitaram")           # 60.0%
```

Duas decisões de método estão embutidas aqui e precisam aparecer no relatório:

- **O total de credenciados é a união.** Marta visitou e não está na base de credenciados: ela se credenciou na porta. Quem visitou estava credenciado, por definição. Por isso a base do funil são as 5 pessoas, não as 4 linhas da base de credenciados.
- **As etapas do funil contam a mesma unidade.** Credenciados, visitantes e participantes são pessoas. Se uma etapa conta mensagens e outra conta pessoas, o relatório precisa avisar.

### 7. Tentativa não é contato

Em disparos de WhatsApp, a plataforma registra tentativas. Um contato pode ter uma tentativa com erro e outra entregue.

```python
tentativas = pd.DataFrame(
    {
        "telefone": ["+5511999900001", "+5521999900002", "+5521999900002", "+551133330000", "+551133330000"],
        "tentativa": [1, 1, 2, 1, 2],
        "status": ["entregue", "erro", "entregue", "erro", "erro"],
    }
)
tentativas["entregue"] = tentativas["status"] == "entregue"

por_contato = tentativas.groupby("telefone")["entregue"].max()
print(por_contato)

print((tentativas["status"] == "erro").sum())     # 3 tentativas com erro
print((~por_contato).sum())                       # 1 contato que nunca recebeu
```

O máximo de uma coluna de `True` e `False` é `True` quando há pelo menos um `True`. Por isso `max` responde "houve alguma tentativa entregue?".

O resultado mostra a diferença: 3 tentativas deram erro, mas só 1 contato ficou sem receber. Erro e entrega não são excludentes. Uma taxa de entrega calculada sobre tentativas, 2 de 5, seria 40%. Calculada sobre contatos, 2 de 3, é 67%. A segunda responde à pergunta que interessa: quantas pessoas a mensagem alcançou.

### 8. Sobreposição não é efeito

O cruzamento final junta quem recebeu mensagem com quem visitou.

```python
receberam = set(por_contato[por_contato].index)
registros["recebeu"] = registros["telefone"].isin(receberam)

por_pessoa = registros.groupby("pessoa", as_index=False)["recebeu"].max()
por_pessoa["visitou"] = por_pessoa["pessoa"].isin(pessoas_vis)

print(pd.crosstab(por_pessoa["recebeu"], por_pessoa["visitou"]))
```

`pd.crosstab` conta as combinações de duas colunas.

Esse quadro mede **sobreposição**: quantos dos que receberam também visitaram. Ele não mede o **efeito** da mensagem. Dois motivos, que valem para qualquer base real:

- **Os grupos não são comparáveis.** Quem se credencia na porta não está na lista de disparo e, por definição, visitou. Esse grupo infla a taxa de visitação de quem não recebeu.
- **Não houve sorteio.** Para medir efeito, seria preciso sortear quem recebe e quem não recebe, como em um teste de duas versões.

Uma medida de efeito defensável vem de algo rastreável: um cupom ou um link exclusivo do disparo. Sem isso, o relatório informa a sobreposição e explica por que ela não é causa.

### 9. O registro metodológico

Uma reconciliação muda o número final. Todo relatório que depende dela deve trazer, em uma nota:

1. As fontes, com o número de linhas de cada uma.
2. As chaves usadas e a regra de identidade.
3. O que foi unido: quantas repetições entre bases e quantas duplicidades ocultas.
4. As regras de contagem: o que entra em cada etapa do funil.
5. As limitações: campos pouco preenchidos, fontes sem chave, o que não pôde ser cruzado.

Essa nota é o que permite a outra pessoa refazer a conta e chegar ao mesmo número.

### 10. Limites da regra exata

A regra deste módulo exige nome idêntico depois da padronização. Ela não reconhece `Maria A. Souza` e `Maria Aparecida Souza` como a mesma pessoa, nem um sobrenome digitado errado.

Existe a correspondência aproximada, que compara textos parecidos. Ela encontra mais pares e também junta pessoas diferentes. Use com dois cuidados: aplique só aos casos que a regra exata não resolveu e revise uma amostra dos pares encontrados.

No Nível 3, esses pares duvidosos são um bom trabalho para o Claude: o código separa os casos claros, e o modelo avalia os ambíguos, com o seu critério escrito.

## Exemplo aplicado

O parágrafo de método de um report pós-feira, escrito a partir do que o código calculou:

> As bases de credenciados (554 linhas), de leitura de credencial (378 leituras) e de inscrições no evento (56 linhas) não têm identificador comum. A identidade foi resolvida pelo e-mail e, quando disponível, pela coincidência de telefone e nome. A soma dos e-mails distintos das três bases é 808; a união é 590; depois da resolução de identidade, são 560 pessoas. As 30 duplicidades encontradas são casos de mesma pessoa com endereços de e-mail diferentes. Todo visitante conta como credenciado, e todo participante do evento com check-in conta como visitante.

Cada número desse parágrafo sai de uma linha do script. O texto pode ser pedido ao Claude; os números, não.

## Exercício

**Tempo:** 2 h

Arquivos, na pasta [`dados/`](dados/), todos fictícios:

| Arquivo | O que é | Colunas |
| --- | --- | --- |
| `feira_credenciados.csv` | Cadastro de credenciamento | `nome`, `email`, `telefone`, `empresa`, `data_credenciamento` |
| `feira_visitantes.csv` | Leitura de credencial, uma linha por pessoa e por dia | `nome`, `email`, `telefone`, `dia` |
| `feira_inscritos_evento.csv` | Inscrições no evento pago, de outra plataforma | `nome`, `email`, `telefone`, `cupom`, `check_in` |
| `feira_whatsapp_tentativas.csv` | Tentativas de entrega de três disparos | `telefone`, `disparo`, `tentativa`, `status` |

Escreva o script `reconciliar.py`, que recebe a pasta dos dados:

```
python reconciliar.py dados
```

### Parte A — Identidade e funil (1 h 15)

1. Leia as três primeiras bases. Em cada uma, padronize o e-mail e o telefone com as suas funções e crie a chave do nome. Acrescente a coluna `fonte`.
2. Informe, para cada base, o número de linhas e de e-mails distintos, e a soma dos e-mails distintos das três.
3. Empilhe as três e informe a união por e-mail.
4. Resolva a identidade pela regra da seção 5 e informe o número de pessoas e de duplicidades ocultas.
5. Calcule quantas pessoas haveria se a identidade fosse só o telefone e se fosse só o nome. Explique a diferença para o resultado do passo 4.
6. Informe as sobreposições em pessoas: credenciados e visitantes, credenciados e inscritos, visitantes e inscritos, e as três bases.
7. Monte o funil com estas regras:
   - credenciados: a união das três bases;
   - visitantes: quem está na leitura de credencial ou tem check-in no evento;
   - participantes do evento: quem tem check-in `S`.
8. Compare com a conta ingênua: quantos e-mails da base de credenciados aparecem na base de visitantes, e que taxa de visitação isso daria.
9. Na base de visitantes, calcule quantas pessoas vieram em 1, 2 e 3 dias e a média de dias por pessoa.

### Parte B — WhatsApp (45 min)

10. Leia as tentativas e padronize o telefone.
11. Para cada disparo, informe: contatos acionados, contatos que receberam, tentativas com erro e taxa de entrega sobre contatos.
12. Informe, no total: contatos distintos, contatos que receberam ao menos uma mensagem, contatos que nunca receberam e o total de tentativas com erro.
13. Cruze com as pessoas: quantas receberam ao menos uma mensagem e quantas não receberam, e quantas de cada grupo visitaram.
14. Escreva três linhas explicando por que a taxa de visitação de quem não recebeu é maior e por que isso não mostra que a mensagem atrapalha.

**Entregável:** o script `reconciliar.py`, a saída e um registro metodológico de um parágrafo, no modelo do exemplo aplicado.

**Critério de conclusão:**

- Os números batem com o gabarito.
- O registro metodológico informa as fontes, a regra de identidade e as regras do funil.
- A resposta do passo 14 cita os credenciados no local.

### Gabarito

Calculado pela solução de referência e conferido contra os totais definidos na geração dos dados.

**Parte A**

| Passo | Resultado |
| --- | --- |
| 2 | Credenciados: 554 linhas e 542 e-mails. Visitantes: 378 linhas e 210 e-mails. Inscritos: 56 linhas e 56 e-mails. Soma dos e-mails distintos: 808 |
| 3 | União por e-mail: 590 |
| 4 | 560 pessoas; 30 duplicidades ocultas |
| 5 | Só telefone: 555, porque 5 pares de colegas dividem um telefone fixo. Só nome: 557, porque há 3 pares de homônimos |
| 6 | Credenciados e visitantes: 190. Credenciados e inscritos: 48. Visitantes e inscritos: 36. Nas três: 36 |
| 7 | Credenciados: 560. Visitantes: 218, ou 38,9% dos credenciados. Participantes do evento: 44, ou 20,2% dos visitantes |
| 8 | 176 de 542, ou 32,5%. A conta ingênua subestima a visitação em 6,4 pontos percentuais |
| 9 | 63 pessoas em 1 dia, 126 em 2 dias e 21 em 3 dias. Média de 1,80 dia por pessoa |

Sobre o passo 6: a base de visitantes tem 210 pessoas, das quais 20 não estão na base de credenciados. São os credenciados no local. Os outros 8 visitantes do funil vêm do evento: têm check-in e não passaram pela leitura de credencial.

**Parte B**

| Disparo | Contatos | Receberam | Tentativas com erro | Entrega |
| --- | --- | --- | --- | --- |
| D1 | 456 | 435 | 91 | 95,4% |
| D2 | 456 | 441 | 76 | 96,7% |
| D3 | 456 | 429 | 101 | 94,1% |

| Passo | Resultado |
| --- | --- |
| 12 | 456 contatos distintos; 451 receberam ao menos uma mensagem; 5 nunca receberam; 268 tentativas com erro em 1.573 |
| 13 | Receberam: 451 pessoas, das quais 166 visitaram (36,8%). Não receberam: 109 pessoas, das quais 52 visitaram (47,7%) |

Sobre o passo 12: houve 268 tentativas com erro, e só 5 contatos ficaram sem nenhuma mensagem. São os cinco telefones fixos compartilhados, que não têm WhatsApp. Uma taxa calculada sobre tentativas daria 83,0% de entrega; sobre contatos, a cobertura dos três disparos é de 98,9%.

Sobre o passo 14: entre as 109 pessoas que não receberam estão as 28 que se credenciaram no local ou só se inscreveram no evento. Elas não estavam na lista de disparo e todas visitaram. O grupo também inclui quem não informou telefone. Os dois grupos não são comparáveis, e a diferença não mede o efeito da mensagem.

A solução de referência está em [`gabarito/reconciliar.py`](gabarito/reconciliar.py).

## Erros comuns

- Somar os totais das bases e chamar o resultado de público.
- Cruzar só por e-mail e perder quem usou endereços diferentes.
- Usar o telefone sozinho como identidade e fundir colegas de empresa.
- Comparar nomes sem padronizar acentos, maiúsculas e espaços.
- Esquecer o `ignore_index=True` ao empilhar as bases.
- Calcular a taxa de entrega sobre tentativas, e não sobre contatos.
- Apresentar a sobreposição entre quem recebeu e quem visitou como efeito do disparo.
- Entregar o número sem o registro do método.

## Checagem rápida

1. Qual a diferença entre soma, união por e-mail e número de pessoas?
2. Por que a identidade usa telefone e nome juntos?
3. O que o `transform("first")` devolve e em que ele difere do `agg`?
4. Por que a base do funil é a união das bases, e não a base de credenciados?
5. Um disparo teve 91 tentativas com erro. O que falta saber para calcular a taxa de entrega?

<details>
<summary>Respostas</summary>

1. A soma conta linhas de todas as bases. A união por e-mail conta endereços distintos. O número de pessoas conta indivíduos, depois de juntar os registros da mesma pessoa com e-mails diferentes.
2. Porque o telefone sozinho junta colegas que informaram o número da empresa, e o nome sozinho junta homônimos.
3. Devolve, para cada linha, o primeiro valor do grupo a que ela pertence, mantendo uma linha de resultado por linha de entrada. O `agg` devolve uma linha por grupo.
4. Porque há visitantes que se credenciaram no local e não estão na base de credenciados. Quem visitou estava credenciado.
5. Quantos contatos foram acionados e quantos deles receberam em alguma tentativa. Tentativa com erro não significa contato sem mensagem.

</details>

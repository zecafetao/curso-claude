# P.2 Lógica em Python

**Carga:** 4 h (1 h 30 de leitura e experimentação, 2 h 30 de exercício)

## Objetivo

Traduzir a lógica que você já conhece para a sintaxe do Python e escrever funções que validam e padronizam e-mail e telefone.

## Por que importa no seu trabalho

Toda regra de tratamento de base é uma função: recebe um valor bruto e devolve o valor padronizado ou a informação de que não dá para aproveitar. Escritas uma vez, essas funções servem para todas as bases que você receber. Elas também são a parte do seu trabalho que mais se beneficia de regra explícita: quando o cliente perguntar por que um telefone foi descartado, a resposta está no código.

Rode cada trecho deste módulo em um arquivo de teste. Ler código sem executar ensina pouco.

## Conteúdo

### 1. Listas

Uma **lista** guarda vários valores em ordem.

```python
publicos = ["Prospecção", "Credenciamento", "Expositor"]

print(publicos[0])              # Prospecção: a contagem começa em zero
print(publicos[-1])             # Expositor: posição negativa conta a partir do fim
print(len(publicos))            # 3

publicos.append("Reativação")   # acrescenta ao fim
print("Expositor" in publicos)  # True
print(publicos[1:3])            # ['Credenciamento', 'Expositor']
```

`publicos[1:3]` é uma **fatia**: começa na posição 1 e vai até antes da posição 3.

### 2. Dicionários

Um **dicionário** guarda pares de chave e valor. É a forma natural de representar um registro.

```python
contato = {"nome": "Ana", "email": "ana.souza@alfa.example", "uf": "SP"}

print(contato["email"])
contato["telefone"] = "+5511999900001"      # cria ou altera uma chave
print(contato.get("cargo", "sem cargo"))    # valor padrão quando a chave não existe

for chave, valor in contato.items():
    print(chave, "=", valor)
```

Pedir uma chave que não existe com colchetes gera `KeyError`. O método `get` devolve um valor padrão em vez do erro.

Uma tabela é uma lista de dicionários: cada linha é um dicionário, e as chaves são os nomes das colunas.

### 3. Condições

```python
entregues = 162

if entregues >= 200:
    print("Taxa comparável")
elif entregues >= 50:
    print("Taxa só como referência")
else:
    print("Lista pequena demais")
```

| Operador | Significado |
| --- | --- |
| `==` e `!=` | Igual e diferente |
| `<`, `<=`, `>`, `>=` | Comparações |
| `and`, `or`, `not` | E, ou, não |
| `in` | Está contido em |

Três cuidados:

- **`=` atribui, `==` compara.** Trocar um pelo outro é o erro mais comum de quem começa.
- **Os dois pontos e o recuo são obrigatórios** em `if`, `elif` e `else`.
- **Vazio conta como falso.** Texto vazio, lista vazia, zero e `None` são tratados como `False` em uma condição. `if telefone:` significa "se o telefone não está vazio".

### 4. Laços

O `for` percorre os itens de uma lista, um por vez.

```python
emails = ["ana@alfa.example", "joao@alfa", "carla@gama.example"]

validos = 0
for email in emails:
    dominio = email.split("@")[1]
    if "." in dominio:
        validos = validos + 1

print(f"{validos} de {len(emails)} com ponto no domínio")

for posicao, email in enumerate(emails, start=1):
    print(posicao, email)

dominios = [email.split("@")[1] for email in emails]
print(dominios)
```

- `enumerate` entrega a posição junto com o item. É útil para informar a linha de um problema.
- A última forma é uma **lista por compreensão**: monta uma lista nova aplicando uma expressão a cada item. Equivale a um `for` com `append`, em uma linha.

### 5. Funções

Uma **função** dá nome a um trecho de código, recebe valores e devolve um resultado.

```python
def taxa(parte, total):
    """Devolve a taxa em percentual, com uma casa decimal."""
    if total == 0:
        return None
    return round(100 * parte / total, 1)


print(taxa(4380, 8110))    # 54.0
print(taxa(5, 0))          # None
```

- `def` define a função. `parte` e `total` são os **parâmetros**.
- `return` devolve o resultado e encerra a função. Uma função sem `return` devolve `None`.
- O texto entre três aspas é a **docstring**: a descrição do que a função faz.
- **`return` não é `print`.** `print` mostra na tela; `return` entrega o valor para quem chamou, que pode usá-lo em outra conta.

Boas práticas que você vai usar no exercício:

- **Uma função, um trabalho.** Padronizar é uma função; validar é outra.
- **Quando não há resultado possível, devolva `None`.** Quem chamou decide o que fazer: descartar o campo, rejeitar a linha ou registrar um aviso.
- **A função não altera o que recebeu.** Ela devolve um valor novo.

### 6. Métodos de texto

Textos têm **métodos**: funções chamadas com um ponto depois do valor.

```python
bruto = "  Ana.Souza@Alfa.Example "

limpo = bruto.strip().lower()
print(limpo)                          # ana.souza@alfa.example
print(limpo.count("@"))               # 1
print(limpo.split("@"))               # ['ana.souza', 'alfa.example']
print(limpo.startswith("ana"))        # True
print(limpo.replace(".example", ".com.br"))
print("11999900001"[:2])              # 11
print("11999900001"[2:])              # 999900001
print("7".zfill(3))                   # 007
```

| Método | O que faz |
| --- | --- |
| `strip()` | Remove espaços das pontas |
| `lower()`, `upper()` | Minúsculas, maiúsculas |
| `replace(a, b)` | Troca `a` por `b` |
| `split(sep)` | Divide o texto em uma lista |
| `count(x)` | Conta as ocorrências de `x` |
| `startswith(x)`, `endswith(x)` | Testa o começo e o fim |
| `isdigit()` | Diz se há só dígitos |
| `zfill(n)` | Completa com zeros à esquerda até `n` caracteres |

Um texto nunca é alterado. Cada método devolve um texto novo, e por isso os métodos podem ser encadeados: `bruto.strip().lower()`.

As fatias funcionam em textos como em listas: `texto[:2]` são os dois primeiros caracteres e `texto[2:]` é o restante.

### 7. Ficar só com os dígitos

Telefones chegam com parênteses, traços, espaços e o sinal de mais. O primeiro passo é remover tudo o que não é dígito:

```python
import re

telefone = "(11) 99990-0001"
digitos = re.sub(r"\D", "", telefone)
print(digitos)        # 11999900001
```

`re` é a biblioteca de **expressões regulares**, uma linguagem para descrever padrões de texto. Aqui, `\D` significa "qualquer caractere que não seja dígito", e `re.sub` troca cada ocorrência por um texto vazio. Esta é a única expressão regular de que você precisa nesta etapa.

### 8. Tratamento de erros

Algumas operações falham com certos valores. O bloco `try` e `except` permite tratar a falha sem derrubar o script.

```python
from datetime import datetime


def data_valida(texto):
    """Diz se o texto é uma data existente no formato DD/MM/AAAA."""
    try:
        datetime.strptime(texto, "%d/%m/%Y")
        return True
    except ValueError:
        return False


print(data_valida("15/03/2025"))    # True
print(data_valida("31/02/2025"))    # False: 31 de fevereiro não existe
```

Capture o erro específico que você espera, como `ValueError`. Um `except` sem tipo esconde qualquer problema, inclusive erros de digitação no seu código.

### 9. Guardar funções em um módulo

Um arquivo `.py` com funções é um **módulo**. Outro script, na mesma pasta, pode importá-lo:

```
tratamento-bases/
├── validacao.py        suas funções
└── meu_script.py       usa as funções
```

Em `meu_script.py`:

```
import validacao

print(validacao.email_valido("ana.souza@alfa.example"))
```

Assim as regras ficam em um lugar só, e todos os scripts usam a mesma versão.

### 10. Pensar nos casos antes de escrever

Antes de escrever uma função, liste as entradas que ela vai encontrar e a saída esperada de cada uma. Inclua o caso normal, as variações de formato e as entradas que devem ser recusadas. É o mesmo raciocínio dos conjuntos de teste do módulo 2.2.

Para telefone, por exemplo:

| Entrada | Saída esperada | Motivo |
| --- | --- | --- |
| `(11) 99990-0001` | `+5511999900001` | Caso normal |
| `5511999900001` | `+5511999900001` | Já veio com o código do país |
| `9999-0004` | `None` | Sem DDD |

A função está pronta quando passa em todos os casos. Sem a lista, não há como saber.

## Exemplo aplicado

Uma função completa de padronização, no padrão que você vai seguir:

```python
UFS = {
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
    "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
}


def padronizar_uf(texto):
    """Devolve a sigla em maiúsculas ou '' se não for uma UF."""
    uf = texto.strip().upper()
    if uf in UFS:
        return uf
    return ""


print(padronizar_uf(" sp"))    # SP
print(padronizar_uf("XX"))     # texto vazio
```

`UFS` é um **conjunto**: uma coleção sem repetição, escrita entre chaves, em que a consulta com `in` é rápida. O nome em maiúsculas é a convenção para valores fixos.

A função segue as três práticas da seção 5: faz um trabalho só, devolve vazio quando não há resultado e não altera o que recebeu.

## Exercício

**Tempo:** 2 h 30

Crie o arquivo `validacao.py` na pasta `tratamento-bases`, com três funções. O alvo é o [layout de importação do CRM](../nivel-1-fundamentos/dados/layout_importacao_crm.md).

### Função 1 — `padronizar_email(texto)`

Devolve o e-mail sem espaços nas pontas e em minúsculas.

### Função 2 — `email_valido(email)`

Recebe um e-mail já padronizado e devolve `True` ou `False`. O e-mail é válido quando cumpre todas as regras:

1. Não está vazio e não tem espaço.
2. Tem exatamente um `@`.
3. Só tem letras sem acento, dígitos e os caracteres `.`, `_`, `-`, `+` e `@`.
4. Tem algum texto antes do `@`.
5. A parte depois do `@` tem pelo menos um ponto, e não começa nem termina com ponto.

Dica para a regra 3: percorra os caracteres com `for` e use `caractere.isascii()` e `caractere.isalnum()`.

### Função 3 — `padronizar_telefone(texto)`

Devolve o telefone no formato `+55DDDNÚMERO` ou `None` quando não for possível padronizar. Passos, nesta ordem:

1. Fique só com os dígitos.
2. Remova os zeros do início.
3. Se sobrarem 12 ou 13 dígitos e eles começarem com `55`, remova o `55`.
4. Se não restarem 10 ou 11 dígitos, devolva `None`.
5. Os dois primeiros dígitos são o DDD. Se o DDD tiver um zero, devolva `None`.
6. O restante é o número. Se ele tiver 8 dígitos e começar com 6, 7, 8 ou 9, é um celular antigo: acrescente um `9` na frente.
7. Um número de 9 dígitos precisa começar com `9`. Um número de 8 dígitos precisa começar com 2, 3, 4 ou 5. Fora disso, devolva `None`.
8. Devolva `+55`, o DDD e o número.

### Passos

1. Antes de escrever, leia o arquivo [`dados/casos_p2.csv`](dados/casos_p2.csv) e, para cinco casos de telefone, descubra à mão qual passo decide o resultado.
2. Escreva as três funções. Teste cada uma com `print` enquanto escreve.
3. Copie `conferir_p2.py` e `casos_p2.csv` da pasta `dados` para a pasta `tratamento-bases`.
4. Rode o conferidor:

```
python conferir_p2.py
```

5. Corrija até todos os casos passarem. Para cada erro, o conferidor mostra a entrada, o esperado e o obtido.
6. Acrescente três casos seus ao `casos_p2.csv`, com entradas que você já viu em bases reais, e rode de novo.

**Entregável:** o arquivo `validacao.py` e a saída do conferidor.

**Critério de conclusão:**

- O conferidor informa **25 de 25 casos corretos** com o arquivo original de casos.
- Nenhuma função usa `print` para devolver o resultado.
- Você consegue explicar por que `(31) 9999-0003` vira `+5531999990003` e por que `(11) 89990-0006` é recusado.

A solução de referência está em [`gabarito/validacao.py`](gabarito/validacao.py). Ela contém também as funções do projeto, que você ainda vai escrever.

## Erros comuns

- Usar `=` em uma condição, no lugar de `==`.
- Esquecer o `return` e receber `None` sem entender por quê.
- Usar `print` dentro da função em vez de devolver o valor.
- Tratar o telefone como número e perder o zero ou o sinal de mais.
- Escrever uma função enorme que padroniza e valida ao mesmo tempo.
- Usar `except` sem tipo e esconder erros do próprio código.
- Aplicar os passos do telefone fora de ordem.

## Checagem rápida

1. Qual a diferença entre lista e dicionário?
2. O que `if telefone:` testa?
3. Qual a diferença entre `return` e `print`?
4. Por que uma função de padronização deve devolver `None` ou vazio em vez de interromper o script?
5. O que faz `re.sub(r"\D", "", texto)`?

<details>
<summary>Respostas</summary>

1. A lista guarda valores em ordem, acessados pela posição. O dicionário guarda pares de chave e valor, acessados pela chave.
2. Se o telefone não está vazio. Texto vazio e `None` contam como falso.
3. `return` entrega o valor a quem chamou a função. `print` só mostra na tela.
4. Porque uma base tem milhares de linhas e um valor ruim não pode parar o tratamento. Quem chama a função decide o que fazer com cada caso.
5. Remove do texto tudo o que não é dígito.

</details>

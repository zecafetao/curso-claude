# P.1 Ambiente e primeiros passos

**Carga:** 2 h (1 h de instalação e leitura, 1 h de exercício)

## Objetivo

Instalar as ferramentas, rodar o primeiro script e ler um arquivo de dados com Python.

## Por que importa no seu trabalho

Até aqui, o trabalho determinístico dos seus fluxos ficou em planilhas: padronizar telefone, remover duplicado, montar o arquivo de importação. Um script faz o mesmo em segundos, do mesmo jeito todas as vezes, e deixa registrado o que foi feito. Este módulo monta o ambiente em que os scripts vão rodar.

## Conteúdo

### 1. O que você vai instalar

| Ferramenta | O que é | Para que serve |
| --- | --- | --- |
| **Python** | O interpretador: o programa que executa o código | Rodar os scripts |
| **VS Code** | Um editor de código | Escrever os scripts e abrir o terminal |
| **Terminal** | Uma janela em que você digita comandos | Mandar o Python executar um script |

**Script** é um arquivo de texto com código, de extensão `.py`. **Biblioteca** é um conjunto de código pronto que você importa para o seu script.

### 2. Instalar o Python

1. Acesse [python.org/downloads](https://www.python.org/downloads/) e baixe a versão estável mais recente.
2. **No Windows**, na primeira tela do instalador, marque a opção **Add python.exe to PATH** antes de clicar em instalar. Sem ela, o terminal não encontra o Python.
3. Conclua a instalação.

O código deste curso foi testado com Python 3.13 (referência: novembro de 2026). Versões mais novas funcionam. Se, no módulo P.3, uma biblioteca não instalar na versão mais nova, instale a versão anterior do Python.

### 3. Instalar o VS Code

1. Baixe em [code.visualstudio.com](https://code.visualstudio.com/) e instale.
2. Abra o VS Code, vá em Extensões (ícone de blocos na barra lateral), procure por **Python** e instale a extensão publicada pela Microsoft.

### 4. Criar a pasta de trabalho

1. Crie uma pasta chamada `tratamento-bases` em um local fácil de achar, como Documentos.
2. Baixe o repositório do curso: na página do repositório no GitHub, clique em **Code** e depois em **Download ZIP**. Descompacte.
3. Copie a pasta `ponte-python/dados` do curso para dentro de `tratamento-bases`.
4. No VS Code, use **Arquivo > Abrir Pasta** e escolha `tratamento-bases`.

A estrutura fica assim:

```
tratamento-bases/
└── dados/
    ├── base_bruta_contatos.csv
    ├── descadastrados.xlsx
    └── ...
```

Todos os scripts da etapa serão criados na pasta `tratamento-bases`, ao lado de `dados`.

### 5. Abrir o terminal e conferir a instalação

No VS Code, abra **Terminal > Novo Terminal**. O terminal já abre dentro da pasta de trabalho. Digite:

```
python --version
```

A resposta deve ser algo como `Python 3.13.5`.

No macOS, o comando é `python3` em vez de `python`. Isso vale para todos os comandos da etapa.

Se o Windows responder que `python` não é reconhecido, o instalador rodou sem a opção de PATH. Rode o instalador de novo, escolha modificar a instalação e marque a opção.

### 6. O primeiro script

Crie um arquivo chamado `ola.py` com uma linha:

```python
print("Olá, base de contatos")
```

Salve e rode no terminal:

```
python ola.py
```

`print` mostra um valor na tela. O ciclo de trabalho será sempre este: escrever, salvar, rodar, ler o resultado.

### 7. Variáveis e tipos

Uma **variável** guarda um valor sob um nome. O sinal `=` atribui o valor.

```python
feira = "Expo Modelo 2026"            # str: texto, entre aspas
enviadas = 8200                       # int: número inteiro
entregues = 8110
taxa_entrega = entregues / enviadas   # float: número com casas decimais
tem_descadastro = True                # bool: True ou False

print(f"{feira}: taxa de entrega de {taxa_entrega:.1%}")
```

Saída: `Expo Modelo 2026: taxa de entrega de 98.9%`

Pontos a notar:

- **Comentário:** tudo depois de `#` é ignorado pelo Python. Serve para explicar o código.
- **Texto formatado:** um texto que começa com `f"` aceita variáveis entre chaves. `:.1%` formata como percentual com uma casa decimal.
- **Nomes:** use nomes que descrevem o conteúdo, em minúsculas e com sublinhado: `taxa_entrega`, não `t` nem `TaxaEntrega`.
- **Ausência de valor:** o valor especial `None` significa "nada aqui".

Os tipos importam. O mesmo sinal faz coisas diferentes com tipos diferentes:

```python
texto = "120"
numero = int(texto)    # converte o texto em número inteiro

print(numero + 1)      # 121
print(texto + "1")     # 1201
```

Dados lidos de um arquivo chegam como texto. Para fazer conta, é preciso converter. Para telefone, CNPJ e CEP, o correto é o contrário: mantê-los como texto, porque um número perde os zeros à esquerda.

### 8. Ler um arquivo

```python
with open("dados/base_bruta_contatos.csv", encoding="utf-8") as arquivo:
    primeira_linha = arquivo.readline()

print(primeira_linha)
```

- `open` abre o arquivo. `encoding="utf-8"` informa a codificação do texto, que define como letras acentuadas são gravadas.
- `with` garante que o arquivo seja fechado ao final do bloco.
- **O recuo é obrigatório.** As linhas dentro do bloco `with` ficam recuadas com quatro espaços. Em Python, o recuo define o que pertence a cada bloco.

Um CSV é um arquivo de texto em que cada linha é um registro e um separador divide as colunas. Neste arquivo, o separador é o ponto e vírgula. A biblioteca `csv`, que já vem com o Python, faz a divisão:

```python
import csv

with open("dados/base_bruta_contatos.csv", encoding="utf-8", newline="") as arquivo:
    leitor = csv.reader(arquivo, delimiter=";")
    cabecalho = next(leitor)     # lê a primeira linha
    print(cabecalho)
    print(len(cabecalho))        # len informa o tamanho
```

`import` carrega uma biblioteca. `next(leitor)` devolve a próxima linha, já dividida em uma lista de valores.

### 9. Receber um valor pelo terminal

Um script útil não tem o nome do arquivo fixo no código. Ele recebe o nome ao ser chamado:

```python
import sys

caminho = sys.argv[1]
print(f"Arquivo informado: {caminho}")
```

`sys.argv` é a lista do que foi digitado no terminal depois de `python`. A posição 0 é o nome do script e a posição 1 é o primeiro valor informado:

```
python meu_script.py dados/base_bruta_contatos.csv
```

### 10. Ler uma mensagem de erro

Erros fazem parte do trabalho. A mensagem diz o que aconteceu e onde:

```
Traceback (most recent call last):
  File "contar_linhas.py", line 6, in <module>
    with open(caminho, encoding="utf-8", newline="") as arquivo:
FileNotFoundError: [Errno 2] No such file or directory: 'dados/base.csv'
```

Leia de baixo para cima: a última linha traz o tipo do erro e a explicação; as linhas acima mostram o arquivo e o número da linha em que ele ocorreu.

| Erro | Causa mais comum |
| --- | --- |
| `SyntaxError` | Falta um parêntese, uma aspa ou os dois pontos no fim da linha |
| `IndentationError` | Recuo errado |
| `NameError` | Nome de variável digitado errado ou usado antes de existir |
| `FileNotFoundError` | Caminho do arquivo errado, ou terminal aberto em outra pasta |
| `IndexError` | Posição que não existe, como `sys.argv[1]` sem informar o arquivo |
| `UnicodeDecodeError` | Arquivo em outra codificação; tente `encoding="latin-1"` |

### 11. O Claude como tutor

Você já sabe pedir bem (Nível 1 e 2). Para aprender a programar, o pedido muda de "faça" para "me ajude a entender":

- **Erro que você não entende:** cole o código e a mensagem completa. Peça: "Explique o que este erro significa e onde está a causa. Não reescreva o código; quero corrigir eu mesmo."
- **Travou em um exercício:** "Estou tentando fazer X. Me dê uma dica sobre o próximo passo, sem a solução."
- **Código que você não entende:** "Explique este trecho linha por linha, para quem conhece lógica de programação e está começando em Python."
- **Depois de resolver:** "Este é o meu código. O que um programador experiente faria diferente e por quê?"

Pedir a solução pronta resolve o exercício e não ensina. Nesta etapa, o objetivo é você conseguir ler e escrever o código que, nos níveis seguintes, vai pedir ao Claude para escrever em volume. Quem não lê código não consegue conferir o que recebe.

Ao colar código ou erro, vale a regra do módulo 1.5: nada de dados reais de clientes.

## Exemplo aplicado

Um script que mostra o cabeçalho e a primeira linha de dados de uma base, para você saber o que recebeu antes de tratar:

```python
import csv
import sys

caminho = sys.argv[1]

with open(caminho, encoding="utf-8", newline="") as arquivo:
    leitor = csv.reader(arquivo, delimiter=";")
    cabecalho = next(leitor)
    primeira = next(leitor)

print(f"Colunas: {len(cabecalho)}")
print(f"Primeira coluna: {cabecalho[0]}")
print(f"Primeiro valor: {primeira[0]}")
```

`cabecalho[0]` é o primeiro item da lista. Em Python, a contagem de posições começa em zero.

## Exercício

**Tempo:** 1 h

Escreva o script `contar_linhas.py`, que recebe o caminho de um CSV separado por ponto e vírgula e informa quantas colunas e quantas linhas de dados ele tem.

1. Crie o arquivo `contar_linhas.py` na pasta `tratamento-bases`.
2. Receba o caminho do arquivo por `sys.argv`.
3. Abra o arquivo e leia o cabeçalho com `next`.
4. Conte as linhas restantes. Para percorrer as linhas, use `for linha in leitor:` e some 1 a um contador a cada volta. O bloco do `for` é recuado, como o do `with`.
5. Mostre o número de colunas, o número de linhas de dados e o nome de cada coluna.
6. Rode:

```
python contar_linhas.py dados/base_bruta_contatos.csv
```

7. Teste o que acontece ao informar um arquivo que não existe e ao não informar arquivo nenhum. Leia as duas mensagens de erro.

**Entregável:** o arquivo `contar_linhas.py` e a saída da execução.

**Critério de conclusão:**

- O script informa **12 colunas** e **120 linhas de dados**.
- Você consegue explicar o que cada linha do script faz.
- Você consegue dizer, pelas mensagens do passo 7, qual erro ocorreu e em que linha.

A solução de referência está em [`gabarito/contar_linhas.py`](gabarito/contar_linhas.py).

## Erros comuns

- Instalar o Python no Windows sem marcar a opção de PATH.
- Rodar o script com o terminal aberto em outra pasta e receber `FileNotFoundError`.
- Esquecer os dois pontos no fim das linhas de `with` e `for`.
- Misturar recuos de tamanhos diferentes no mesmo bloco.
- Contar o cabeçalho como linha de dados.
- Pedir a solução ao Claude antes de tentar.

## Checagem rápida

1. Para que serve a opção de PATH na instalação do Python no Windows?
2. Por que telefone, CNPJ e CEP devem ser tratados como texto?
3. O que o recuo significa em Python?
4. Em uma mensagem de erro, onde estão o tipo do erro e a linha em que ele ocorreu?
5. O que `sys.argv[1]` contém?

<details>
<summary>Respostas</summary>

1. Para o terminal encontrar o comando `python` em qualquer pasta.
2. Porque, como números, perdem os zeros à esquerda e os sinais, e não são usados em contas.
3. Define quais linhas pertencem a um bloco, como o de um `with` ou de um `for`.
4. O tipo e a explicação estão na última linha. O arquivo e o número da linha estão nas linhas acima dela.
5. O primeiro valor digitado no terminal depois do nome do script.

</details>

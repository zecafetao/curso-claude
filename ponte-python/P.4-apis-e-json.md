# P.4 APIs e JSON

**Carga:** 3 h (1 h de leitura e experimentação, 2 h de exercício)

## Objetivo

Entender como um programa conversa com um serviço externo, consultar uma API pública com tratamento de falhas e usar o resultado para enriquecer uma base.

## Por que importa no seu trabalho

Dois motivos. O primeiro é imediato: 44 das 120 linhas da base não têm cidade nem UF, e o CEP permite preencher a maior parte delas com o nome oficial. O segundo é o que vem depois: no Nível 3, você vai chamar o Claude pela API. O mecanismo é o mesmo deste módulo: uma requisição, uma resposta em JSON, uma chave de acesso e o cuidado com falhas.

## Conteúdo

### 1. O que é uma API

Uma **API** é a forma de um programa pedir algo a outro. Nas APIs da web, o seu script envia uma **requisição** a um endereço e recebe uma **resposta**.

| Elemento | O que é | Exemplo |
| --- | --- | --- |
| URL | O endereço do recurso | `https://brasilapi.com.br/api/cep/v1/01310100` |
| Método | O tipo de pedido | `GET` para consultar, `POST` para enviar dados |
| Código de status | O resultado, em um número | `200` deu certo, `404` não encontrado |
| Corpo | O conteúdo da resposta | Um texto em JSON |

Neste módulo você usa a consulta de CEP da [BrasilAPI](https://brasilapi.com.br/), um serviço público e gratuito (referência: novembro de 2026). Outra opção conhecida é o ViaCEP. Se o serviço estiver fora do ar no dia do exercício, use o arquivo `dados/ceps_referencia.csv`, que traz o resultado das consultas.

Os trechos das seções 2 a 5 continuam um ao outro. Escreva-os em um arquivo `testar_api.py`.

### 2. A primeira consulta

A biblioteca `requests` faz requisições. Ela já foi instalada pelo `requirements.txt`.

```python
import requests

resposta = requests.get("https://brasilapi.com.br/api/cep/v1/01310100", timeout=10)

print(resposta.status_code)     # 200
print(resposta.text)            # o corpo da resposta, como texto
```

`timeout=10` limita a espera a 10 segundos. Sem ele, um serviço que não responde deixa o seu script parado indefinidamente. Informe sempre.

### 3. JSON

O corpo veio em **JSON**, o formato de texto mais usado para trocar dados entre programas:

```
{"cep":"01310100","state":"SP","city":"São Paulo","neighborhood":"Bela Vista","street":"Avenida Paulista", ...}
```

A estrutura é a que você já conhece do módulo P.2:

| JSON | Python |
| --- | --- |
| Objeto, entre chaves | Dicionário |
| Lista, entre colchetes | Lista |
| Texto, número, `true`, `false`, `null` | `str`, `int` ou `float`, `True`, `False`, `None` |

```python
dados = resposta.json()         # converte o JSON em um dicionário

print(dados["city"])            # São Paulo
print(dados["state"])           # SP
print(list(dados.keys()))       # os campos disponíveis
```

Para gravar e reler um JSON, use a biblioteca `json`:

```python
import json

with open("cep_exemplo.json", "w", encoding="utf-8") as arquivo:
    json.dump(dados, arquivo, ensure_ascii=False, indent=2)

with open("cep_exemplo.json", encoding="utf-8") as arquivo:
    relido = json.load(arquivo)

print(relido["city"])
```

`ensure_ascii=False` mantém os acentos legíveis no arquivo, e `indent=2` organiza o texto em linhas.

### 4. Códigos de status

Nem toda requisição dá certo. O código de status diz o que aconteceu.

```python
resposta = requests.get("https://brasilapi.com.br/api/cep/v1/00000000", timeout=10)
print(resposta.status_code)     # 404

if resposta.status_code == 200:
    print(resposta.json()["city"])
elif resposta.status_code == 404:
    print("CEP não encontrado")
else:
    print(f"Erro inesperado: {resposta.status_code}")
```

| Código | Significado | O que fazer |
| --- | --- | --- |
| 200 | Deu certo | Usar a resposta |
| 400 | Requisição malformada | Corrigir o que foi enviado |
| 401 e 403 | Sem autorização | Verificar a chave de acesso |
| 404 | Não encontrado | Registrar e seguir |
| 429 | Requisições demais | Esperar e reduzir o ritmo |
| 500 em diante | Erro no serviço | Tentar de novo mais tarde |

Chamar `resposta.json()` em uma resposta de erro pode falhar ou devolver uma mensagem em vez dos dados. Confira o status antes de usar o corpo.

### 5. Falhas de conexão

Às vezes não há resposta: a internet caiu, o endereço não existe, o tempo de espera estourou. Nesses casos, o `requests` gera um erro, que você trata com `try` e `except`.

```python
try:
    resposta = requests.get("https://servico-que-nao-existe.example/cep/01310100", timeout=5)
    print(resposta.status_code)
except requests.exceptions.RequestException as erro:
    print(f"Falha de conexão: {type(erro).__name__}")
```

`RequestException` cobre todas as falhas do `requests`. O script informa o problema e continua.

Em um tratamento com centenas de consultas, uma falha não pode derrubar tudo. Cada consulta devolve um resultado ou a situação que impediu o resultado.

### 6. Boas práticas ao consultar em volume

1. **Consulte cada valor uma vez.** A base tem 120 linhas e 15 CEPs distintos. São 15 consultas, não 120.
2. **Faça uma pausa entre as consultas.** Meio segundo, com `time.sleep(0.5)`, evita sobrecarregar um serviço gratuito e reduz a chance de receber 429.
3. **Guarde o resultado em arquivo.** Se o script parar no meio, você não precisa consultar tudo de novo. O arquivo também serve de registro do que a fonte respondeu naquela data.
4. **Mostre o andamento.** Uma linha por consulta, para saber que o script está vivo.
5. **Registre a situação de cada consulta:** encontrado, não encontrado, falha.
6. **Leia os termos do serviço.** APIs gratuitas têm limite de uso e não garantem disponibilidade.

### 7. O que pode ser enviado a uma API

Uma consulta a uma API envia dados a um terceiro. Vale a classificação do módulo 1.5:

- **CEP** não identifica uma pessoa. Pode ser consultado.
- **E-mail, telefone e CPF** são dados pessoais. Enviá-los a um serviço de validação ou enriquecimento é um compartilhamento de dados, que precisa estar previsto no contrato com o cliente e na política da empresa.

Antes de usar uma API nova com dados de clientes, descubra quem opera o serviço e o que ele faz com o que recebe.

### 8. Chaves de API e variáveis de ambiente

A consulta de CEP é aberta. A maioria das APIs exige uma **chave**: um código que identifica quem está chamando e, nas pagas, quem será cobrado. A API do Claude funciona assim.

Uma chave é como uma senha. Três regras:

1. **Nunca escreva a chave no código.**
2. **Nunca envie a chave para um repositório, um chat ou um e-mail.**
3. **Se uma chave vazar, revogue e gere outra.**

O lugar da chave é uma **variável de ambiente**: um valor guardado no sistema, fora do código, que o script lê ao rodar.

```python
import os

chave = os.environ.get("MINHA_CHAVE_DE_TESTE")

if chave is None:
    print("Defina a variável de ambiente MINHA_CHAVE_DE_TESTE antes de rodar.")
else:
    print(f"Chave carregada, com {len(chave)} caracteres.")
```

Para definir a variável no terminal, antes de rodar o script:

| Sistema | Comando |
| --- | --- |
| Windows (PowerShell) | `$env:MINHA_CHAVE_DE_TESTE = "abc123"` |
| macOS | `export MINHA_CHAVE_DE_TESTE=abc123` |

A variável vale para aquele terminal, até ele ser fechado.

O script mostra o tamanho da chave, não a chave. Evite imprimir segredos: a saída do terminal acaba copiada para outros lugares.

Quando uma API exige chave, ela costuma ir em um cabeçalho da requisição:

```
resposta = requests.get(url, headers={"Authorization": f"Bearer {chave}"}, timeout=10)
```

### 9. Usar o resultado na base

A tabela de CEPs consultados se junta à base com o `merge` do módulo P.3, pela coluna do CEP padronizado. O exercício faz esse cruzamento.

## Exemplo aplicado

Uma função que consulta um CEP e sempre devolve um resultado, em qualquer situação:

```python
import requests

URL = "https://brasilapi.com.br/api/cep/v1/{cep}"


def consultar_cep(cep):
    """Devolve um dicionário com cep, cidade, uf e a situação da consulta."""
    resultado = {"cep": cep, "cidade": "", "uf": "", "situacao": ""}
    try:
        resposta = requests.get(URL.format(cep=cep), timeout=10)
    except requests.exceptions.RequestException as erro:
        resultado["situacao"] = f"falha de conexão ({type(erro).__name__})"
        return resultado

    if resposta.status_code == 404:
        resultado["situacao"] = "não encontrado"
        return resultado
    if resposta.status_code != 200:
        resultado["situacao"] = f"erro {resposta.status_code}"
        return resultado

    dados = resposta.json()
    resultado["cidade"] = dados["city"]
    resultado["uf"] = dados["state"]
    resultado["situacao"] = "encontrado"
    return resultado


print(consultar_cep("01310100"))
print(consultar_cep("00000000"))
```

Saída:

```
{'cep': '01310100', 'cidade': 'São Paulo', 'uf': 'SP', 'situacao': 'encontrado'}
{'cep': '00000000', 'cidade': '', 'uf': '', 'situacao': 'não encontrado'}
```

`URL.format(cep=cep)` troca `{cep}` pelo valor. A função trata os três desfechos possíveis: falha de conexão, resposta de erro e sucesso. Quem chama recebe sempre um dicionário com as mesmas chaves.

## Exercício

**Tempo:** 2 h

### Parte A — Consultar os CEPs da base (1 h 15)

1. No seu `validacao.py`, escreva a função `padronizar_cep(texto)`: fique só com os dígitos; se restarem 7 ou 8, complete com zeros à esquerda até 8 e devolva; caso contrário, devolva texto vazio. O caso de 7 dígitos é o do CEP que perdeu o zero inicial em uma planilha.
2. Crie o script `consultar_cep.py`, que recebe a base bruta e o nome do arquivo de saída:

```
python consultar_cep.py dados/base_bruta_contatos.csv ceps.csv
```

3. O script deve:
   - ler a base com o pandas;
   - padronizar a coluna `CEP` e obter a lista de CEPs distintos, sem o valor vazio;
   - consultar cada CEP uma vez, com pausa de meio segundo, mostrando o andamento;
   - gravar `ceps.csv` com as colunas `cep`, `cidade`, `uf` e `situacao`, separado por ponto e vírgula;
   - mostrar quantos CEPs caíram em cada situação.
4. Compare o seu `ceps.csv` com o [`dados/ceps_referencia.csv`](dados/ceps_referencia.csv).

Dica: uma lista de dicionários vira uma tabela com `pd.DataFrame(lista)`.

### Parte B — Cruzar com a base (45 min)

Em um script `cruzar_ceps.py`, leia a base e o `ceps.csv`, crie na base a coluna `cep` padronizada, faça o `merge` e responda:

1. Quantas linhas têm CEP encontrado, quantas têm CEP não encontrado e quantas não têm CEP?
2. Das linhas com a cidade vazia na base, quantas seriam preenchidas pelo CEP e quantas continuariam vazias?
3. Nas linhas em que a cidade está informada e o CEP foi encontrado, em quantas a cidade informada difere da oficial? Compare em minúsculas e sem espaços nas pontas. Qual é a diferença?

**Entregável:** os scripts `consultar_cep.py` e `cruzar_ceps.py`, o arquivo `ceps.csv` e as três respostas.

**Critério de conclusão:**

- Os números batem com o gabarito.
- Ao desligar a internet e rodar o `consultar_cep.py`, o script termina sem erro e registra a falha de conexão em cada CEP.

### Gabarito

Consultas feitas em novembro de 2026. Nomes de cidades e UFs são estáveis; se a API mudar a resposta, vale o que ela devolver.

**Parte A:** 15 CEPs distintos; 14 encontrados e 1 não encontrado (`00000000`).

| CEP | Cidade | UF |
| --- | --- | --- |
| 01310100 | São Paulo | SP |
| 04538132 | São Paulo | SP |
| 13010000 | Campinas | SP |
| 20040020 | Rio de Janeiro | RJ |
| 30130010 | Belo Horizonte | MG |
| 40020000 | Salvador | BA |
| 50010000 | Recife | PE |
| 60060170 | Fortaleza | CE |
| 69005010 | Manaus | AM |
| 70040010 | Brasília | DF |
| 74003010 | Goiânia | GO |
| 80010000 | Curitiba | PR |
| 88010000 | Florianópolis | SC |
| 90010150 | Porto Alegre | RS |

**Parte B:**

| Pergunta | Resposta |
| --- | --- |
| 1 | 107 linhas com CEP encontrado, 3 com CEP não encontrado e 10 sem CEP |
| 2 | 44 linhas têm a cidade vazia; 34 seriam preenchidas e 10 continuariam vazias |
| 3 | 4 linhas. A base traz `SAO PAULO` e `FLORIANOPOLIS`, sem acento. O CEP devolve o nome oficial, acentuado |

A solução de referência da parte A está em [`gabarito/consultar_cep.py`](gabarito/consultar_cep.py).

## Erros comuns

- Chamar a API sem `timeout`.
- Consultar uma vez por linha da base, em vez de uma vez por valor distinto.
- Usar o corpo da resposta sem conferir o código de status.
- Deixar uma falha de conexão derrubar o script inteiro.
- Não guardar o resultado e refazer todas as consultas a cada execução.
- Escrever uma chave de acesso no código ou enviá-la para o repositório.
- Enviar dados pessoais a uma API de terceiros sem verificar se isso é permitido.

## Checagem rápida

1. O que significam os códigos 200, 404 e 429?
2. Para que serve o `timeout`?
3. Em que tipo de dado do Python um objeto JSON é convertido?
4. Por que consultar só os valores distintos?
5. Onde deve ficar uma chave de API e onde ela nunca deve aparecer?

<details>
<summary>Respostas</summary>

1. 200: deu certo. 404: não encontrado. 429: requisições demais.
2. Para limitar o tempo de espera por uma resposta e impedir que o script fique parado indefinidamente.
3. Em um dicionário.
4. Para fazer menos requisições: é mais rápido, respeita o limite do serviço e dá o mesmo resultado.
5. Em uma variável de ambiente. Nunca no código, no repositório, em um chat ou em um e-mail.

</details>

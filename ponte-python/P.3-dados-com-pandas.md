# P.3 Dados com pandas

**Carga:** 5 h (2 h de leitura e experimentação, 3 h de exercício)

## Objetivo

Tratar uma base inteira com poucas linhas de código: ler, inspecionar, limpar, filtrar, remover duplicados, cruzar com outra tabela e exportar.

## Por que importa no seu trabalho

No módulo P.2 você tratou um valor por vez. Uma base tem milhares de linhas e uma dúzia de colunas. O pandas aplica uma operação à coluna inteira, com uma linha de código e sem laço. É a ferramenta padrão para o que você hoje faz em planilha, com três vantagens: o tratamento fica escrito, pode ser repetido em qualquer base e não altera o arquivo original.

## Conteúdo

### 1. Ambiente virtual e instalação

O pandas não vem com o Python; é preciso instalar. Bibliotecas são instaladas em um **ambiente virtual**: uma pasta, dentro do seu projeto, com as bibliotecas daquele projeto. Assim, projetos diferentes não interferem um no outro.

1. Copie o arquivo `requirements.txt` da pasta `ponte-python` do curso para a pasta `tratamento-bases`. Ele lista as bibliotecas da etapa: `pandas`, `openpyxl` (para ler Excel), `requests` e `pytest`.
2. No VS Code, abra a paleta de comandos (Ctrl+Shift+P; no macOS, Cmd+Shift+P) e escolha **Python: Create Environment**.
3. Escolha **Venv**, selecione a sua instalação do Python e marque o `requirements.txt` para instalação.
4. Feche o terminal e abra um novo. O nome `(.venv)` aparece no início da linha, indicando que o ambiente está ativo.

Para conferir:

```
python -c "import pandas; print(pandas.__version__)"
```

O código da etapa foi testado com pandas 3.0 (referência: novembro de 2026).

Se preferir o terminal, os comandos equivalentes são:

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

No macOS, a segunda linha é `source .venv/bin/activate`.

Se o PowerShell recusar a ativação com a mensagem de que a execução de scripts está desabilitada, rode uma vez `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` e abra um novo terminal.

### 2. As duas estruturas

- **DataFrame:** uma tabela, com linhas e colunas nomeadas.
- **Series:** uma coluna.

A convenção é importar o pandas com o apelido `pd`.

Os trechos das seções 3 a 12 continuam um ao outro. Escreva-os em sequência, em um arquivo `explorar.py`, e rode a cada trecho novo.

### 3. Ler um CSV

```python
import pandas as pd

base = pd.read_csv(
    "dados/base_bruta_contatos.csv",
    sep=";",
    dtype=str,
    keep_default_na=False,
    encoding="utf-8",
)

print(base.shape)               # (120, 12): 120 linhas e 12 colunas
print(base.columns.tolist())    # os nomes das colunas
print(base.head(3))             # as três primeiras linhas
```

Os quatro parâmetros evitam os erros mais comuns em bases de contatos:

| Parâmetro | Por quê |
| --- | --- |
| `sep=";"` | O separador do arquivo. O padrão do pandas é a vírgula |
| `dtype=str` | Lê tudo como texto. Sem isso, o pandas converte CNPJ, CEP e telefone em número e perde os zeros à esquerda |
| `keep_default_na=False` | Mantém as células vazias como texto vazio. Sem isso, viram um valor especial de ausência (`NaN`), que se comporta de forma diferente nas comparações |
| `encoding="utf-8"` | A codificação. Se der `UnicodeDecodeError`, o arquivo provavelmente está em `latin-1`, comum em exportações antigas |

### 4. Ler um Excel

```python
descadastrados = pd.read_excel("dados/descadastrados.xlsx", dtype=str)

print(descadastrados.shape)     # (12, 2)
print(descadastrados.head(3))
```

`read_excel` lê a primeira aba. Para outra, informe `sheet_name="nome da aba"`.

### 5. Inspecionar

Antes de tratar, conheça a base.

```python
print(base["UF"].value_counts().head(5))     # os cinco valores mais frequentes
print(base["Cargo"].nunique())               # quantos valores distintos: 24
print((base["Telefone"] == "").sum())        # quantos vazios: 13
```

- `base["UF"]` seleciona uma coluna.
- `value_counts()` conta as ocorrências de cada valor. Aqui ele revela o problema: 44 vazios, 7 linhas com `SP` e outras 5 com ` SP`, com um espaço na frente. Para o computador, são valores diferentes.
- `base["Telefone"] == ""` devolve uma coluna de `True` e `False`. Somar essa coluna conta os `True`.

### 6. Selecionar e filtrar

```python
sp = base[base["UF"] == "SP"]
sp_com_telefone = base[(base["UF"] == "SP") & (base["Telefone"] != "")]
sul = base[base["UF"].isin(["PR", "SC", "RS"])]
sem_cnpj = base[base["CNPJ"] == ""]
compradores = base[base["Cargo"].str.contains("Compra")]
duas_colunas = base[["Empresa", "Cargo"]]

print(len(sp), len(sp_com_telefone), len(sul), len(sem_cnpj), len(compradores))
```

Saída: `7 7 7 14 11`

A condição entre colchetes é uma **máscara**: uma coluna de `True` e `False` que diz quais linhas ficam.

| Para | Use |
| --- | --- |
| Combinar condições com "e" | `&`, com cada condição entre parênteses |
| Combinar com "ou" | `\|` |
| Negar | `~` na frente da condição |
| Testar contra uma lista | `.isin([...])` |
| Procurar um trecho de texto | `.str.contains("...")` |
| Selecionar colunas | Uma lista de nomes entre colchetes duplos |

Em pandas, use `&`, `|` e `~`. As palavras `and`, `or` e `not` não funcionam com colunas.

Filtrar não altera a `base`. Cada filtro cria uma tabela nova.

### 7. Renomear e limpar texto

```python
base = base.rename(columns={"Empresa": "empresa", "Cargo": "cargo", "UF": "uf", "Cidade": "cidade"})

base["uf"] = base["uf"].str.strip().str.upper()
base["cidade"] = base["cidade"].str.strip().str.title()
base["empresa"] = base["empresa"].str.strip().str.replace(r"\s+", " ", regex=True)

print(len(base[base["uf"] == "SP"]))    # 14
```

- `.str` dá acesso aos métodos de texto do módulo P.2, aplicados à coluna inteira.
- A expressão `\s+` significa "um ou mais espaços". A troca reduz espaços repetidos a um só.
- Depois da limpeza, o filtro por `SP` encontra 14 linhas. Antes, encontrava 7. As outras 7 estavam escritas como `sp` ou ` SP`.

A lição vale para qualquer base: **limpe antes de contar**. Um número tirado de uma coluna suja está errado sem dar nenhum aviso.

### 8. Aplicar as suas funções

Quando a regra é mais complexa que um método de texto, use `.map` com uma função sua. Ela é aplicada a cada valor da coluna.

```python
import validacao

base["telefone"] = base["Telefone"].map(validacao.padronizar_telefone)
print(base["telefone"].isna().sum())     # 22

base["telefone"] = base["telefone"].fillna("")
```

A sua função devolve `None` quando não consegue padronizar. Na coluna, isso vira ausência de valor. `isna()` identifica essas células e `fillna("")` troca por texto vazio. Os 22 casos somam os 13 telefones que já vinham vazios e 9 que não puderam ser padronizados.

Em um script, as linhas de `import` ficam no topo do arquivo. Aqui o `import validacao` aparece no meio só para acompanhar a explicação.

### 9. Criar colunas e alterar valores com condição

```python
base["tem_telefone"] = base["telefone"] != ""

base["tipo_telefone"] = "sem telefone"
base.loc[base["telefone"].str.len() == 14, "tipo_telefone"] = "celular"
base.loc[base["telefone"].str.len() == 13, "tipo_telefone"] = "fixo"

print(base["tipo_telefone"].value_counts())
```

Saída: 84 celulares, 22 sem telefone e 14 fixos.

`base.loc[condição, coluna] = valor` altera a coluna só nas linhas em que a condição é verdadeira. É a forma correta de fazer um "se" sobre a tabela.

Não escreva `base[base["x"] == 1]["y"] = valor`. Essa forma altera uma cópia temporária, e a `base` continua igual.

### 10. Duplicados

```python
print(base["empresa"].nunique())                   # 40 nomes distintos
print(base.duplicated(subset="empresa").sum())     # 80 linhas cuja empresa já apareceu

empresas = base.drop_duplicates(subset="empresa", keep="first")
print(len(empresas))                               # 40
```

- `duplicated(subset=...)` marca as linhas cujo valor já apareceu antes.
- `drop_duplicates(subset=..., keep="first")` remove as repetições e mantém a primeira ocorrência.

A base tem 20 empresas, e o pandas encontrou 40 nomes distintos. O motivo é a escrita: `Alimentos Alfa` e `Alimentos Alfa LTDA` são textos diferentes. Duplicado só é detectado depois da padronização. A regra para nomes de empresa fica para o projeto.

### 11. Cruzar duas tabelas

`merge` junta duas tabelas por uma coluna em comum, como o PROCV das planilhas.

```python
regioes = pd.DataFrame(
    {
        "uf": ["SP", "RJ", "MG", "PR", "SC", "RS", "BA", "PE", "CE", "DF", "GO"],
        "regiao": ["Sudeste", "Sudeste", "Sudeste", "Sul", "Sul", "Sul",
                   "Nordeste", "Nordeste", "Nordeste", "Centro-Oeste", "Centro-Oeste"],
    }
)

com_regiao = base.merge(regioes, on="uf", how="left")
print(com_regiao["regiao"].value_counts(dropna=False))
```

`how="left"` mantém todas as linhas da tabela da esquerda (`base`) e traz a região quando a UF existe na tabela da direita. Onde não existe, a região fica ausente. Aqui, 55 linhas ficaram sem região.

Para descobrir quais, peça o indicador de origem:

```python
marcada = base.merge(regioes, on="uf", how="left", indicator=True)
sem_regiao = marcada[marcada["_merge"] == "left_only"]

print(sem_regiao["uf"].value_counts())
```

A coluna `_merge` diz se a linha foi encontrada nas duas tabelas (`both`) ou só na da esquerda (`left_only`). O resultado mostra 44 linhas sem UF, 8 com `AM`, que faltou na tabela de regiões, e 3 com `XX`, que não é uma UF.

Esse padrão tem dois usos no seu trabalho:

- **Trazer uma informação:** a região de cada UF, a cidade de cada CEP.
- **Separar quem está em uma lista:** as linhas marcadas como `both` são as que constam na outra tabela. É assim que se retiram os descadastrados.

Cuidado: se a tabela da direita tiver a chave repetida, o `merge` multiplica as linhas da esquerda. Confira o número de linhas antes e depois.

### 12. Agrupar e exportar

```python
por_regiao = com_regiao.groupby("regiao").size().sort_values(ascending=False)
print(por_regiao)

com_telefone = com_regiao.groupby("regiao")["tem_telefone"].mean().round(2)
print(com_telefone)

saida = com_regiao[["empresa", "cargo", "cidade", "uf", "regiao", "telefone"]]
saida.to_csv("saida_teste.csv", sep=";", index=False, encoding="utf-8")
print(f"{len(saida)} linhas gravadas")
```

- `groupby("regiao").size()` conta as linhas de cada grupo: Sudeste 27, Nordeste 15, Sul 13 e Centro-Oeste 10.
- A média de uma coluna de `True` e `False` é a proporção de `True`. No Nordeste, 73% dos contatos têm telefone.
- `to_csv` grava o arquivo. `index=False` evita uma coluna extra com a numeração das linhas.

### 13. Cuidados ao abrir o resultado no Excel

O arquivo gerado está correto para o CRM. O Excel pode exibi-lo de forma enganosa:

- **Acentos trocados:** o Excel nem sempre reconhece UTF-8. Para um arquivo que uma pessoa vai abrir no Excel, grave com `encoding="utf-8-sig"`. Para o CRM, mantenha `utf-8`.
- **Zeros à esquerda e o sinal de mais:** ao abrir, o Excel converte CNPJ, CEP e telefone em número. Se você salvar por cima, o arquivo é corrompido.

Para conferir um arquivo de importação, abra no VS Code ou releia com o pandas. Não salve pelo Excel.

### 14. Princípios de um bom tratamento

1. **O arquivo original não é alterado.** O script lê uma entrada e grava uma saída nova.
2. **Todo passo que remove linhas informa quantas removeu.** A soma tem de fechar: lidas = gravadas + removidas.
3. **A ordem dos passos é decidida, não acidental.** Padronizar antes de comparar; validar antes de remover duplicados.
4. **O script roda do começo ao fim sem intervenção.** Se o tratamento depende de um ajuste manual no meio, ele não é reproduzível.

## Exemplo aplicado

Um diagnóstico de qualidade, para rodar em qualquer base antes de tratar. Ele mostra, para cada coluna, quantos valores estão vazios e quantos são distintos.

```python
import pandas as pd

base = pd.read_csv(
    "dados/base_bruta_contatos.csv", sep=";", dtype=str, keep_default_na=False, encoding="utf-8"
)

for coluna in base.columns:
    base[coluna] = base[coluna].str.strip()     # um campo só com espaços conta como vazio

diagnostico = pd.DataFrame(
    {
        "vazios": (base == "").sum(),
        "distintos": base.nunique(),
    }
)
diagnostico["pct_vazios"] = (100 * diagnostico["vazios"] / len(base)).round(1)

print(diagnostico)
print(base["E-mail"].str.lower().nunique())
```

A leitura do resultado já orienta o tratamento:

- `Cidade` e `UF` têm 36,7% de vazios. Vale enriquecer pelo CEP, o que você fará no módulo P.4.
- `Nome Completo` tem 4 vazios. Sem a remoção de espaços do início do trecho, o diagnóstico mostraria zero, porque esses campos contêm só espaços.
- `E-mail` tem 115 valores distintos em 120 linhas, o que sugere 5 repetições. A última linha do trecho mostra que são mais: em minúsculas, restam 107 valores distintos. A maior parte das repetições estava escondida pela diferença entre maiúsculas e minúsculas.
- `Origem` tem 18 valores distintos, e o layout aceita 5. A coluna precisa de regra de padronização.

Esse diagnóstico usa só dados agregados. O resultado pode ser levado ao Claude para discutir a estratégia de tratamento, sem enviar nenhum contato.

## Exercício

**Tempo:** 3 h

Escreva o script `tratamento_inicial.py`, que recebe a base bruta, a lista de descadastrados e o nome do arquivo de saída:

```
python tratamento_inicial.py dados/base_bruta_contatos.csv dados/descadastrados.xlsx saida_p3.csv
```

### O que o script faz, nesta ordem

1. Lê a base e a lista de descadastrados e informa quantas linhas leu.
2. Renomeia as colunas que vai usar: `nome_completo`, `email`, `telefone`, `empresa`, `uf` e `origem`.
3. Limpa o texto:
   - `email`: sem espaços nas pontas, em minúsculas;
   - `nome_completo`: sem espaços nas pontas, espaços repetidos reduzidos a um, iniciais maiúsculas com `.str.title()`;
   - `empresa` e `origem`: sem espaços nas pontas;
   - `uf`: sem espaços nas pontas, em maiúsculas.
4. Padroniza o telefone com a sua função do módulo P.2. O que não puder ser padronizado fica vazio.
5. Remove as linhas com e-mail inválido, usando a sua função, e informa quantas removeu.
6. Remove os contatos que constam na lista de descadastrados e informa quantos removeu. A comparação é feita com os e-mails das duas tabelas já padronizados.
7. Remove os e-mails repetidos, mantendo a primeira ocorrência, e informa quantos removeu.
8. Grava o arquivo com as seis colunas, separado por ponto e vírgula, em UTF-8, e informa quantas linhas gravou.

### Perguntas para responder com pandas

Depois do script, releia o arquivo gravado e responda:

1. Quantos contatos têm telefone padronizado?
2. Qual UF tem mais contatos e quantos são? Quantas linhas ficaram sem UF?
3. Quantos domínios de e-mail distintos existem? Dica: `.str.split("@").str[1]`.
4. Quantos valores distintos tem a coluna `origem`? O que isso indica sobre o tratamento que ainda falta?
5. Procure nomes com `Da`, `De` ou `Dos`. O que o `.str.title()` fez de errado?
6. Quantas linhas ficaram com o nome vazio? O que isso indica?

**Entregável:** o script `tratamento_inicial.py`, a saída da execução e as seis respostas.

**Critério de conclusão:** os números batem com o gabarito e a conta fecha: 120 = 93 + 6 + 8 + 13.

### Gabarito

Calculado pela solução de referência.

| Passo | Resultado |
| --- | --- |
| Linhas lidas | 120 |
| E-mails inválidos removidos | 6 |
| Descadastrados removidos | 8 |
| Duplicados removidos | 13 |
| Linhas gravadas | 93 |

| Pergunta | Resposta |
| --- | --- |
| 1 | 74 contatos com telefone |
| 2 | SP, com 11 contatos. 35 linhas sem UF |
| 3 | 20 domínios distintos |
| 4 | 17 valores distintos, para 5 opções aceitas pelo layout. A origem precisa de uma regra de padronização, como `credenciamento`, `CREDENCIAMENTO 2025` e `Credenciamento` virando `Credenciamento` |
| 5 | `Carla Oliveira Da Silva` em vez de `Carla Oliveira da Silva`. O `title()` põe maiúscula em todas as palavras, inclusive nas partículas |
| 6 | 3 linhas. O tratamento ainda não valida o nome; contatos sem nome estão passando. A regra entra no projeto |

Se o número de descadastrados der 6 em vez de 8, a lista não foi padronizada: dois e-mails dela estão em maiúsculas.

Se o número de duplicados for diferente de 13, confira a ordem. Os duplicados são contados depois de remover os inválidos e os descadastrados.

Um dos 13 duplicados merece atenção. A linha 35 do arquivo repete o e-mail da linha 33, que não tem nome. Neste exercício, a linha 33 fica e a 35 sai, porque o nome ainda não é validado: o tratamento manteve o registro pior. No projeto, a ordem das regras inverte o resultado: a linha 33 é rejeitada por nome ausente antes da busca por repetidos, e a linha 35 é importada.

A solução de referência está em [`gabarito/p3_tratamento_inicial.py`](gabarito/p3_tratamento_inicial.py).

## Erros comuns

- Ler sem `dtype=str` e perder os zeros à esquerda de CNPJ e CEP.
- Contar ou comparar antes de limpar.
- Usar `and` e `or` entre condições de coluna, em vez de `&` e `|`.
- Esquecer os parênteses em volta de cada condição combinada.
- Fazer `merge` com chave repetida na tabela da direita e multiplicar linhas sem perceber.
- Remover linhas sem informar quantas.
- Abrir o arquivo de importação no Excel e salvar por cima.

## Checagem rápida

1. Para que servem `dtype=str` e `keep_default_na=False` na leitura?
2. Por que o filtro por `SP` encontrou 7 linhas antes da limpeza e 14 depois?
3. Como alterar uma coluna só nas linhas que cumprem uma condição?
4. O que a coluna `_merge` informa?
5. Por que duplicados devem ser removidos depois da padronização?

<details>
<summary>Respostas</summary>

1. `dtype=str` lê tudo como texto e preserva zeros à esquerda. `keep_default_na=False` mantém células vazias como texto vazio.
2. Porque metade das linhas estava escrita como `sp` ou ` SP`, com minúsculas ou espaço, e esses textos são diferentes de `SP`.
3. Com `base.loc[condição, "coluna"] = valor`.
4. Se a linha foi encontrada nas duas tabelas (`both`) ou só em uma (`left_only`).
5. Porque o mesmo contato pode estar escrito de formas diferentes, e só a escrita padronizada permite reconhecer a repetição.

</details>

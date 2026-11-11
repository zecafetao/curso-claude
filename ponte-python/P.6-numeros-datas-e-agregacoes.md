# P.6 Números, datas e agregações

**Carga:** 3 h (1 h 15 de leitura e experimentação, 1 h 45 de exercício)

## Objetivo

Calcular os indicadores de um relatório por código: converter textos em números e datas, calcular taxas, agrupar com várias medidas, montar tabelas com total e comparar dois períodos.

## Por que importa no seu trabalho

Nos módulos anteriores, tudo foi tratado como texto, o que é certo para e-mail, telefone e CNPJ. Um relatório pede o contrário: somar, dividir, agrupar por público e por dia. No projeto do Nível 1, o gabarito do relatório mensal veio pronto, "calculado por código". Neste módulo você escreve esse código. O mesmo vale para o estudo de perfil de expositores: as tabelas de porte, setor e região saem de três linhas de pandas.

Depois deste módulo, a divisão de trabalho do módulo 2.9 fica completa: o código calcula e o Claude redige a leitura sobre números que você sabe reproduzir.

## Conteúdo

Os trechos das seções 1 a 11 continuam um ao outro. Escreva-os em um arquivo `explorar_metricas.py`. Copie para a sua pasta `dados` os três arquivos novos da pasta `ponte-python/dados` do curso: `desempenho_email_outubro.csv`, `desempenho_email_setembro.csv` e `empresas_expositoras.csv`.

### 1. Por que converter

```python
import pandas as pd

base = pd.read_csv(
    "dados/desempenho_email_outubro.csv", dtype=str, keep_default_na=False, encoding="utf-8"
)

print(base["enviadas"].sort_values().head(4).tolist())
```

Saída: `['2100', '2100', '2250', '2900']`

A ordenação saiu alfabética: o texto `'2100'` vem antes do texto `'6'`. Como texto, uma coluna não pode ser somada nem comparada como quantidade. Este arquivo usa a vírgula como separador, o padrão do `read_csv`, e por isso o `sep` não foi informado.

### 2. Texto vira número

```python
contagens = ["enviadas", "entregues", "aberturas_unicas", "cliques_unicos", "descadastros"]
for coluna in contagens:
    base[coluna] = pd.to_numeric(base[coluna])

print(base["enviadas"].sort_values().head(3).tolist())    # [6, 80, 82]
print(base["enviadas"].sum())                             # 50818
```

`pd.to_numeric` converte a coluna. Se houver um valor que não é número, ele para com erro. Com `errors="coerce"`, o valor inválido vira ausência (`NaN`) e a conversão continua. Use essa opção de forma consciente: conte os ausentes depois e descubra de onde vieram.

Números no formato brasileiro precisam de um passo a mais, porque o Python usa ponto como separador decimal:

```python
valores = pd.Series(["7.531.425,98", "832.042.099,47"])

sem_milhar = valores.str.replace(".", "", regex=False)
numeros = pd.to_numeric(sem_milhar.str.replace(",", ".", regex=False))

print(numeros.tolist())      # [7531425.98, 832042099.47]
```

A ordem importa: primeiro saem os pontos de milhar, depois a vírgula vira ponto.

### 3. Texto vira data

```python
base["data_envio"] = pd.to_datetime(base["data_envio"], format="%Y-%m-%d")

dias = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
base["dia_semana"] = base["data_envio"].dt.dayofweek.map(dias)
base["hora"] = pd.to_numeric(base["hora_envio"].str[:2], errors="coerce")

print(base[["data_envio", "dia_semana", "hora"]].head(3))
print(base["hora"].isna().sum())      # 1: um disparo veio sem horário
```

- Informe sempre o `format`. Sem ele, o pandas adivinha, e uma data como `03/06/2025` pode ser lida como 6 de março. Para datas brasileiras, o formato é `"%d/%m/%Y"`.
- `.dt` dá acesso às partes da data: `.dt.year`, `.dt.month`, `.dt.day` e `.dt.dayofweek`, em que 0 é segunda-feira.
- O dicionário traduz o número do dia para o nome. `.map` com um dicionário troca cada valor pelo correspondente.

### 4. Uma coluna a partir de um pedaço do texto

O público está no nome do disparo, na quarta parte separada por sublinhado.

```python
base["publico"] = base["disparo"].str.split("_").str[3]

print(base["publico"].value_counts())
```

`.str.split("_")` divide cada nome em uma lista, e `.str[3]` pega a quarta parte. É a regra do seu arquivo de método, agora em código.

### 5. Excluir pelo critério do método

```python
considerados = base[base["enviadas"] >= 10].copy()

print(len(base), len(considerados))      # 15 14
```

O `.copy()` cria uma tabela independente. Use quando for acrescentar colunas a uma tabela que nasceu de um filtro.

O disparo excluído não desaparece do relatório: ele é listado em nota. O filtro inverso, `base[base["enviadas"] < 10]`, entrega essa lista.

### 6. Taxas por linha

```python
considerados["taxa_abertura"] = (100 * considerados["aberturas_unicas"] / considerados["entregues"]).round(1)
considerados["taxa_clique"] = (100 * considerados["cliques_unicos"] / considerados["entregues"]).round(1)

mais_clicados = considerados.sort_values("taxa_clique", ascending=False)
print(mais_clicados[["disparo", "entregues", "taxa_clique"]].head(3))
```

A conta é feita na coluna inteira de uma vez. O primeiro da lista tem 20,1% de clique em 304 entregas: é o disparo que o seu método manda sinalizar como possível clique automático.

Sinalizar não é remover. O disparo continua nos totais, e o relatório informa o efeito dele.

### 7. Agrupar com várias medidas

```python
por_publico = considerados.groupby("publico", as_index=False).agg(
    disparos=("disparo", "count"),
    entregues=("entregues", "sum"),
    aberturas_unicas=("aberturas_unicas", "sum"),
    media_das_taxas=("taxa_abertura", "mean"),
)
por_publico["taxa_abertura"] = (100 * por_publico["aberturas_unicas"] / por_publico["entregues"]).round(1)
por_publico["media_das_taxas"] = por_publico["media_das_taxas"].round(1)

print(por_publico.sort_values("entregues", ascending=False))
```

Em `agg`, cada linha cria uma coluna de resultado: o nome novo, a coluna de origem e a operação (`"count"`, `"sum"`, `"mean"`, `"min"`, `"max"`, `"median"`).

Compare as duas últimas colunas na linha de `Prospeccao`: a taxa de abertura é 54,7% e a média das taxas dos disparos é 51,2%. A diferença existe porque a média dá o mesmo peso a um disparo de 2 mil entregas e a um de 8 mil.

**A taxa de um grupo é a soma dos numeradores dividida pela soma dos denominadores.** Calcule primeiro as somas e depois a taxa. A média das taxas é um número diferente, e errado para este fim.

### 8. A linha de total

```python
total = por_publico[["disparos", "entregues", "aberturas_unicas"]].sum().to_frame().T
total["publico"] = "Total"
total["taxa_abertura"] = (100 * total["aberturas_unicas"] / total["entregues"]).round(1)

tabela = pd.concat([por_publico.drop(columns="media_das_taxas"), total], ignore_index=True)
print(tabela)
```

- `.sum().to_frame().T` transforma as somas em uma tabela de uma linha.
- `pd.concat` empilha tabelas com as mesmas colunas.
- A taxa do total também é soma dividida por soma: 52,6%. Somar ou tirar a média das taxas dos públicos não faz sentido.

### 9. Tabela dinâmica

```python
dinamica = considerados.pivot_table(
    index="dia_semana", columns="hora", values="disparo", aggfunc="count", fill_value=0
)
print(dinamica)
```

`pivot_table` cruza duas colunas, como a tabela dinâmica das planilhas. Aqui, conta os disparos por dia da semana e por hora.

A tabela mostra por que esse recorte pede cuidado: quase todas as células têm zero, um ou dois disparos. Uma taxa calculada sobre um disparo é a taxa daquele disparo, não a do horário. Antes de mostrar uma taxa por dia e hora, mostre quantos disparos há em cada célula e defina um mínimo.

Há um segundo problema: os dias misturam públicos. Em outubro, os dois disparos de segunda-feira foram para expositores. A abertura alta da segunda é a abertura dos expositores.

### 10. Faixas e participação

```python
faixas = pd.cut(
    considerados["entregues"],
    bins=[0, 200, 5000, float("inf")],
    labels=["Até 200", "201 a 5.000", "Acima de 5.000"],
)
print(faixas.value_counts(sort=False))

por_publico["participacao"] = (100 * por_publico["entregues"] / por_publico["entregues"].sum()).round(1)
print(por_publico[["publico", "entregues", "participacao"]])
```

- `pd.cut` classifica números em faixas. Cada faixa inclui o limite superior: `Até 200` vai de 1 a 200.
- A participação é a parte dividida pelo todo. Prospecção responde por 52,3% das entregas.

### 11. Comparar dois períodos

```python
setembro = pd.read_csv(
    "dados/desempenho_email_setembro.csv", dtype=str, keep_default_na=False, encoding="utf-8"
)
for coluna in contagens:
    setembro[coluna] = pd.to_numeric(setembro[coluna])
setembro = setembro[setembro["enviadas"] >= 10].copy()

setembro["mes"] = "setembro"
considerados["mes"] = "outubro"
dois_meses = pd.concat([setembro, considerados], ignore_index=True)

por_mes = dois_meses.groupby("mes", sort=False)[["enviadas", "entregues", "aberturas_unicas"]].sum()
por_mes["taxa_abertura"] = (100 * por_mes["aberturas_unicas"] / por_mes["entregues"]).round(1)
print(por_mes)

diferenca = por_mes.loc["outubro", "taxa_abertura"] - por_mes.loc["setembro", "taxa_abertura"]
print(round(diferenca, 1))      # 6.9
```

A abertura passou de 45,7% para 52,6%. A diferença é de 6,9 **pontos percentuais**. Dizer que "a abertura subiu 6,9%" está errado: em termos relativos, ela subiu 15%. Em relatórios, diferença entre taxas se informa em pontos percentuais.

### 12. Formatar só no fim

Os números ficam como números durante todo o cálculo. A formatação para o relatório é o último passo.

```python
def numero(valor):
    """Formata um inteiro com ponto de milhar: 50812 -> 50.812."""
    return f"{int(valor):,}".replace(",", ".")


def percentual(valor):
    """Formata uma taxa com vírgula decimal: 52.6 -> 52,6%."""
    return f"{valor:.1f}%".replace(".", ",")


print(numero(50812), percentual(52.6))      # 50.812 52,6%
```

Depois de formatado, o valor volta a ser texto e não serve mais para conta. Quem formata no meio do caminho acaba comparando textos sem perceber, como na seção 1.

## Exemplo aplicado

Um teste de duas versões de e-mail termina sempre na mesma pergunta: a diferença é real ou pode ser acaso? O teste de duas proporções responde. Ele usa só a biblioteca `math`, que vem com o Python.

```python
import math


def teste_duas_proporcoes(sucessos_a, total_a, sucessos_b, total_b):
    """Devolve (z, valor_p) para a diferença entre duas taxas."""
    taxa_a = sucessos_a / total_a
    taxa_b = sucessos_b / total_b
    conjunta = (sucessos_a + sucessos_b) / (total_a + total_b)
    erro = math.sqrt(conjunta * (1 - conjunta) * (1 / total_a + 1 / total_b))
    z = (taxa_a - taxa_b) / erro
    valor_p = math.erfc(abs(z) / math.sqrt(2))
    return round(z, 2), valor_p


z, valor_p = teste_duas_proporcoes(2460, 3968, 2290, 3960)
print(f"Abertura: z = {z}, valor-p = {valor_p:.5f}")

z, valor_p = teste_duas_proporcoes(119, 3968, 79, 3960)
print(f"Clique: z = {z}, valor-p = {valor_p:.5f}")
```

Saída:

```
Abertura: z = 3.79, valor-p = 0.00015
Clique: z = 2.86, valor-p = 0.00418
```

São os dois convites de credenciamento de outubro: a versão direta, com 2.460 aberturas e 119 cliques em 3.968 entregas, e a completa, com 2.290 aberturas e 79 cliques em 3.960.

Como ler:

- O **valor-p** é a probabilidade de aparecer uma diferença desse tamanho, ou maior, se as duas versões fossem iguais. Quanto menor, menos plausível é o acaso.
- A convenção é tratar a diferença como significativa quando o valor-p fica abaixo de 0,05. Aqui, os dois ficam abaixo de 0,01.

O que o teste não diz:

- **Não diz a causa.** Se as duas versões tinham assuntos diferentes, a diferença de abertura pode vir do assunto.
- **Não corrige uma divisão malfeita.** As duas listas precisam ter sido sorteadas da mesma base.
- **Não vale para listas pequenas.** Com os 162 e-mails de expositores, o teste perde o sentido prático.

## Exercício

**Tempo:** 1 h 45

### Parte A — O relatório mensal por código (1 h 10)

Escreva o script `relatorio_mensal.py`, que recebe a exportação do mês e, opcionalmente, a do mês anterior:

```
python relatorio_mensal.py dados/desempenho_email_outubro.csv dados/desempenho_email_setembro.csv
```

O script segue o seu `metodo_relatorio_mensal.md` do Nível 1 e mostra:

1. **Indicadores gerais:** disparos considerados, enviadas, entregues, aberturas únicas, cliques únicos e as três taxas.
2. **Disparos excluídos**, com o número de envios.
3. **Tabela por público**, com disparos, contagens, taxas e a linha de total, ordenada por enviadas.
4. **Disparos sinalizados** por taxa de clique acima de 15%.
5. **Tabela por dia da semana**, com o número de disparos de cada dia.
6. **Comparação com o mês anterior:** variação percentual das enviadas e diferença das três taxas em pontos percentuais.

Organize em funções: uma para ler e converter, uma para calcular as taxas, uma para agrupar, uma para acrescentar o total. A função de agrupar deve servir para o público e para o dia da semana.

### Parte B — O perfil dos expositores (35 min)

Escreva o script `perfil_expositores.py`, que lê [`dados/empresas_expositoras.csv`](dados/empresas_expositoras.csv) e mostra:

1. A contagem e a participação por porte, por setor e por região. A região vem da UF, por um dicionário.
2. Quantas empresas são de médio ou grande porte.
3. Quantas têm faturamento estimado acima de R$ 30 milhões. O faturamento está no formato brasileiro.
4. A contagem por faixa de faturamento: até R$ 4,8 milhões, de R$ 4,8 a R$ 30 milhões, de R$ 30 a R$ 300 milhões e acima de R$ 300 milhões.
5. Quantas empresas foram abertas antes de 2000. A data está em `DD/MM/AAAA`.

**Entregável:** os dois scripts e a saída de cada um.

**Critério de conclusão:**

- Os números da parte A batem com o gabarito abaixo e com o [gabarito do projeto do Nível 1](../nivel-1-fundamentos/projeto.md#gabarito).
- Os números da parte B batem com o [`resumo_estudo_publico.md`](../nivel-1-fundamentos/dados/resumo_estudo_publico.md) do Nível 1, que foi escrito a partir desta base.
- Nenhuma taxa de grupo foi calculada como média de taxas.

### Gabarito

Calculado pelas soluções de referência.

**Parte A — outubro**

| Indicador | Valor |
| --- | --- |
| Disparos considerados | 14 |
| Excluído | `2026_10_EXPOMODELO_Confirmacao_RespostaAutomatica`, com 6 envios |
| Enviadas | 50.812 |
| Entregues | 50.116 |
| Aberturas únicas | 26.385 |
| Cliques únicos | 1.218 |
| Taxas de entrega, abertura e clique | 98,6%, 52,6% e 2,4% |
| Sinalizado | `2026_09_EXPOMODELO_Credenciamento_Acao2oEnvio`: 61 cliques em 304 entregas, 20,1% |

A tabela por público é a do gabarito do projeto do Nível 1.

| Dia da semana | Disparos | Enviadas | Abertura | Clique |
| --- | --- | --- | --- | --- |
| Quinta | 4 | 21.440 | 48,5% | 1,6% |
| Sexta | 3 | 12.300 | 59,5% | 3,1% |
| Terça | 2 | 10.250 | 52,0% | 1,7% |
| Quarta | 2 | 6.350 | 54,5% | 4,3% |
| Sábado | 1 | 310 | 42,8% | 20,1% |
| Segunda | 2 | 162 | 64,8% | 6,8% |

Antes de tirar uma conclusão dessa tabela, olhe a coluna de disparos e lembre a seção 9: o sábado é um único disparo, o sinalizado; a segunda são os dois disparos de expositores.

**Parte A — comparação**

| | Setembro | Outubro | Diferença |
| --- | --- | --- | --- |
| Disparos considerados | 13 | 14 | |
| Enviadas | 64.307 | 50.812 | -21,0% |
| Taxa de entrega | 97,9% | 98,6% | +0,7 ponto percentual |
| Taxa de abertura | 45,7% | 52,6% | +6,9 pontos percentuais |
| Taxa de clique | 1,8% | 2,4% | +0,6 ponto percentual |

**Parte B**

| Verificação | Valor |
| --- | --- |
| Porte | Média 66 (55,0%), Grande 36 (30,0%), Pequena 18 (15,0%) |
| Setor | Plásticas 42, papel e papelão 30, máquinas 24, rótulos 15, serviços 9 |
| Região | Sudeste 78 (65,0%), Sul 30 (25,0%), Nordeste 8 (6,7%), Centro-Oeste 4 (3,3%) |
| Médio e grande porte | 102 (85,0%) |
| Faturamento acima de R$ 30 milhões | 54 (45,0%) |
| Faixas de faturamento | Até 4,8 mi: 18. De 4,8 a 30 mi: 48. De 30 a 300 mi: 18. Acima de 300 mi: 36 |
| Abertas antes de 2000 | 60 |

Se o faturamento acima de R$ 30 milhões der um número absurdo ou um erro, a conversão do formato brasileiro falhou: confira a ordem das duas trocas da seção 2.

As soluções de referência estão em [`gabarito/relatorio_mensal.py`](gabarito/relatorio_mensal.py) e [`gabarito/perfil_expositores.py`](gabarito/perfil_expositores.py).

## Erros comuns

- Somar ou ordenar uma coluna que ainda é texto.
- Usar `errors="coerce"` e não conferir quantos valores viraram ausência.
- Ler datas sem informar o formato e trocar dia por mês.
- Calcular a taxa de um grupo como média das taxas.
- Somar taxas, ou calcular a taxa do total a partir das taxas dos grupos.
- Tirar conclusão de uma célula com um ou dois disparos.
- Dizer "subiu 6,9%" quando a diferença é de 6,9 pontos percentuais.
- Formatar os números antes de terminar os cálculos.

## Checagem rápida

1. Por que `'2100'` vem antes de `'6'` na ordenação?
2. Como converter `"7.531.425,98"` em número?
3. Como se calcula a taxa de abertura de um grupo de disparos?
4. O que verificar antes de comparar taxas em uma tabela por dia e hora?
5. A abertura foi de 45,7% para 52,6%. Como informar a diferença?

<details>
<summary>Respostas</summary>

1. Porque a coluna é texto, e textos são ordenados caractere a caractere: `'2'` vem antes de `'6'`.
2. Removendo os pontos de milhar, trocando a vírgula por ponto e aplicando `pd.to_numeric`, nessa ordem.
3. Soma das aberturas únicas do grupo dividida pela soma das entregas do grupo.
4. Quantos disparos há em cada célula e se os dias ou horários misturam públicos diferentes.
5. Como um aumento de 6,9 pontos percentuais.

</details>

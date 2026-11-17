# P.8 Gráficos por código

**Carga:** 2 h (45 min de leitura e experimentação, 1 h 15 de exercício)

## Objetivo

Gerar por código os gráficos de um relatório, sempre no mesmo padrão visual, gravar cada um como imagem e conferir os valores desenhados contra a tabela de origem.

## Por que importa no seu trabalho

O relatório mensal tem os mesmos gráficos todo mês. No app, cada pedido de gráfico sai um pouco diferente: outra cor, outra ordem, outro tamanho de letra (módulo 2.6). Em uma entrega recorrente, essa variação vira retrabalho de ajuste a cada mês.

Com o gráfico em uma função, o mês novo exige só o arquivo novo. O padrão visual da empresa fica escrito uma vez. E o gráfico sai da mesma tabela que você já confere no módulo P.6, o que elimina a diferença entre "o número do texto" e "o número do gráfico".

Este módulo também prepara o Nível 4. As funções que você escreve aqui são as ferramentas de gráfico do agente de relatórios.

## Conteúdo

### 1. Antes do gráfico: que forma os dados pedem

A primeira decisão não é de código. É escolher a forma que serve ao que o leitor precisa fazer com os números.

| O leitor precisa | Forma | Exemplo no relatório mensal |
| --- | --- | --- |
| Ver poucos números principais | Números em destaque, sem gráfico | Taxa de entrega, de abertura e de clique do mês |
| Comparar valores entre categorias | Barras, ordenadas da maior para a menor | Taxa de clique por público |
| Comparar dois períodos por categoria | Duas barras por categoria, uma cor para cada período | Taxa de abertura por público, mês atual e anterior |
| Ver a evolução no tempo | Linha | E-mails enviados, acumulado no mês |
| Ver muitos valores exatos | Tabela | Desempenho de cada disparo |

Três escolhas a evitar:

- **Gráfico de uma barra só, ou de dois ou três números.** O número é mais claro que o gráfico. As três taxas gerais do mês ficam melhor em destaque, com a diferença para o mês anterior ao lado.
- **Pizza para comparar valores próximos.** Entre 3,6% e 3,7%, as fatias parecem iguais. Barras sobre a mesma linha de base mostram a diferença.
- **Dois eixos verticais no mesmo gráfico.** Taxa de abertura (perto de 50%) e taxa de clique (perto de 2%) não cabem na mesma escala. Com um eixo para cada uma, o ponto em que as linhas se cruzam depende só de como as escalas foram ajustadas, e o gráfico sugere uma relação que os dados não têm. Faça dois gráficos.

### 2. O primeiro gráfico

A biblioteca de gráficos mais usada em Python é o **matplotlib**. Com o ambiente da pasta `tratamento-bases` ativo:

```
pip install matplotlib
```

Acrescente a linha `matplotlib` ao seu `requirements.txt`.

Os trechos das seções 2 a 6 continuam um ao outro. Escreva-os em um arquivo `testar_graficos.py`.

```python
import matplotlib

matplotlib.use("Agg")                 # grava imagens sem abrir janela
import matplotlib.pyplot as plt

publicos = ["Reativação", "Prospecção", "Credenciamento", "Pré-credenciado", "Expositor"]
taxas = [1.0, 1.6, 3.6, 3.7, 6.8]

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(publicos, taxas)
ax.set_title("Taxa de clique por público")
fig.savefig("primeiro_grafico.png", dpi=200)
plt.close(fig)
```

Abra o `primeiro_grafico.png`. Os elementos do código:

| Elemento | O que é |
| --- | --- |
| `fig` | A **figura**: a imagem inteira |
| `ax` | Os **eixos**: a área em que o gráfico é desenhado. Quase todos os comandos são dados a ele |
| `figsize=(8, 4.5)` | O tamanho da figura, em polegadas. A proporção 16:9 é a dos slides |
| `ax.barh` | Barras horizontais. Para barras verticais, `ax.bar` |
| `fig.savefig(..., dpi=200)` | Grava a imagem. Com 200 pontos por polegada, a figura sai com 1.600 × 900 pixels |
| `plt.close(fig)` | Libera a memória da figura. Em um script que gera muitos gráficos, sem essa linha a memória se esgota |

A linha `matplotlib.use("Agg")` faz o matplotlib só gravar arquivos, sem tentar abrir uma janela. É o modo certo para scripts que rodam sozinhos, como os de um agente ou de uma tarefa agendada.

Use barras horizontais quando os nomes das categorias são longos, como os de públicos e de disparos. Eles ficam legíveis, sem inclinar o texto.

### 3. Do DataFrame ao gráfico, com rótulos de valor

O gráfico parte da tabela que o seu script do módulo P.6 já calcula. Os trechos abaixo usam os nomes das funções do gabarito do P.6. Se as suas têm outros nomes, troque.

```python
import relatorio_mensal as rm

considerados, _ = rm.separar_excluidos(rm.ler_desempenho("dados/desempenho_email_outubro.csv"))
tabela = rm.por_grupo(considerados, "publico")[["publico", "taxa_clique"]]
tabela = tabela.sort_values("taxa_clique")        # crescente: o matplotlib desenha de baixo para cima
print(tabela)
```

A ordem das linhas é a ordem das barras, de baixo para cima. Para a maior barra ficar no topo, a tabela vai em ordem crescente.

```python
AMBAR = "#F59E0B"
GRAFITE = "#1F1F1F"

fig, ax = plt.subplots(figsize=(8, 4.5))
barras = ax.barh(tabela["publico"], tabela["taxa_clique"], height=0.3, color=AMBAR)
ax.bar_label(barras, labels=[rm.percentual(valor) for valor in tabela["taxa_clique"]],
             padding=6, fontsize=11, color=GRAFITE)
ax.set_title("Taxa de clique por público — outubro de 2026", loc="left",
             fontsize=14, fontweight="bold", color=GRAFITE)
for lado in ["top", "right", "left", "bottom"]:
    ax.spines[lado].set_visible(False)            # tira a moldura
ax.xaxis.set_visible(False)                       # todos os valores estão nos rótulos
ax.tick_params(length=0, labelsize=11)
fig.tight_layout()
fig.savefig("clique_por_publico.png", dpi=200, facecolor="white")
plt.close(fig)
```

| Comando | O que faz |
| --- | --- |
| `height=0.3` | A espessura das barras. Barras finas, com espaço entre elas, leem melhor que blocos grossos |
| `ax.bar_label` | Escreve um rótulo na ponta de cada barra. Os textos vêm da função `percentual` do P.6, com vírgula decimal |
| `ax.spines` | As quatro linhas da moldura. Sem elas, sobra o que é dado |
| `fig.tight_layout()` | Ajusta as margens para nada ficar cortado |

Duas regras de leitura aplicadas no trecho:

- **O texto não usa a cor da série.** Os rótulos e o título vão em grafite. A cor fica nas barras. Um valor escrito em âmbar sobre fundo branco é difícil de ler.
- **Uma série, uma cor.** As cinco barras são da mesma medida e levam a mesma cor. Pintar cada barra de uma cor, ou escurecer as maiores, gasta a cor para repetir o que o comprimento já mostra.

Como todos os valores estão escritos nas barras, o eixo horizontal é dispensado. Quando só parte dos valores tem rótulo, o eixo fica, como na próxima seção.

### 4. O padrão visual em uma função

O título à esquerda, a moldura retirada e as cores de texto se repetem em todo gráfico. O que se repete vira função, e o padrão visual passa a ter um só lugar no código.

```python
CINZA = "#8A8A8A"          # a série de comparação
CINZA_TEXTO = "#555555"    # eixos e legenda
CINZA_CLARO = "#E5E5E5"    # linhas de apoio

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans"]


def aplicar_padrao(ax, titulo, legenda_no_topo=False):
    """Aplica o padrão visual a um gráfico: título, cores de texto e linhas discretas."""
    distancia = 34 if legenda_no_topo else 14
    ax.set_title(titulo, loc="left", fontsize=14, fontweight="bold", color=GRAFITE, pad=distancia)
    for lado in ["top", "right", "left"]:
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(CINZA_CLARO)
    ax.tick_params(colors=CINZA_TEXTO, length=0, labelsize=10)
    ax.set_axisbelow(True)                 # as linhas de apoio ficam atrás das barras
```

As cores são as do padrão visual da Agência Modelo, o mesmo da Skill do módulo 2.5: âmbar para o que o leitor deve ver primeiro, cinza para a comparação, grafite para o texto. `plt.rcParams` define a fonte de todos os gráficos: Arial, se estiver instalada, ou a fonte padrão do matplotlib.

Quando a empresa mudar uma cor, a mudança é em uma linha. Quando um cliente tiver outro padrão, as constantes e a função `aplicar_padrao` são o que muda.

### 5. Duas séries: destaque e comparação

Para comparar o mês atual com o anterior, cada público recebe duas barras. O mês atual vai em âmbar e o anterior em cinza: o destaque é do período que o relatório analisa.

```python
anterior, _ = rm.separar_excluidos(rm.ler_desempenho("dados/desempenho_email_setembro.csv"))
do_atual = rm.por_grupo(considerados, "publico")[["publico", "taxa_abertura"]]
do_anterior = rm.por_grupo(anterior, "publico")[["publico", "taxa_abertura"]]
comparada = do_atual.merge(do_anterior, on="publico", how="left", suffixes=("_atual", "_anterior"))
comparada = comparada.iloc[::-1].reset_index(drop=True)       # inverte: a primeira linha fica no topo
print(comparada)

def eixo_percentual(valor, posicao):
    """Texto de um valor do eixo: 40 vira 40%."""
    return f"{valor:.0f}%"


fig, ax = plt.subplots(figsize=(8, 4.5))
posicoes = range(len(comparada))
ax.barh([p - 0.17 for p in posicoes], comparada["taxa_abertura_anterior"], height=0.3,
        color=CINZA, label="setembro de 2026")
barras = ax.barh([p + 0.17 for p in posicoes], comparada["taxa_abertura_atual"], height=0.3,
                 color=AMBAR, label="outubro de 2026")
ax.bar_label(barras, labels=[rm.percentual(valor) for valor in comparada["taxa_abertura_atual"]],
             padding=6, fontsize=11, color=GRAFITE)
aplicar_padrao(ax, "Taxa de abertura por público", legenda_no_topo=True)
ax.set_yticks(list(posicoes), comparada["publico"])
ax.set_xlim(0, 100)
ax.xaxis.set_major_formatter(eixo_percentual)
ax.grid(axis="x", color=CINZA_CLARO, linewidth=0.8)
marcas, nomes = ax.get_legend_handles_labels()
ax.legend(marcas[::-1], nomes[::-1], frameon=False, loc="lower left", bbox_to_anchor=(0, 1),
          borderaxespad=0, ncols=2, fontsize=10, labelcolor=CINZA_TEXTO)
fig.tight_layout()
fig.savefig("abertura_por_publico.png", dpi=200, facecolor="white")
plt.close(fig)
```

O que é novo:

- **Posições numéricas.** Com duas barras por categoria, cada barra recebe uma posição: a do público, deslocada 0,17 para baixo ou para cima. `ax.set_yticks` escreve os nomes dos públicos nas posições centrais.
- **Legenda.** Com duas séries ou mais, a legenda é obrigatória: o leitor não deve adivinhar o que cada cor significa. O parâmetro `label` de cada série dá o nome, e `ax.legend` desenha. Aqui ela fica entre o título e as barras, fora da área dos dados.
- **Rótulos só na série em destaque.** Um número em cada uma das dez barras vira ruído. Os valores do mês atual estão escritos, e os do mês anterior são lidos pelo eixo e pelas linhas de apoio. O valor exato de tudo está na tabela.
- **Linhas de apoio.** `ax.grid` desenha linhas verticais claras e contínuas. Elas ajudam a ler as barras sem rótulo e não competem com os dados.
- **Formato do eixo.** `set_major_formatter` recebe uma função que transforma cada valor do eixo em texto. A função `eixo_percentual` acrescenta o sinal de percentual.

O eixo de uma taxa de abertura vai de 0 a 100. Em gráficos de barras, o eixo começa sempre em zero: uma barra cortada exagera diferenças pequenas.

### 6. Linhas: a evolução no tempo

O acumulado de e-mails enviados ao longo do mês mostra o ritmo da campanha. O cálculo usa duas operações do pandas: `reindex`, que cria uma linha para cada dia do mês, mesmo os sem disparo, e `cumsum`, que soma cada valor aos anteriores.

```python
def acumulado_por_dia(base):
    """E-mails enviados acumulados, do dia 1 ao 31."""
    por_dia = base.groupby(base["data_envio"].dt.day)["enviadas"].sum()
    return por_dia.reindex(range(1, 32), fill_value=0).cumsum()


def eixo_milhar(valor, posicao):
    """Texto de um valor do eixo: 50000 vira 50.000."""
    return rm.numero(valor)


acumulado_atual = acumulado_por_dia(considerados)
acumulado_anterior = acumulado_por_dia(anterior)
print(acumulado_atual[15], acumulado_anterior[15], acumulado_atual[31], acumulado_anterior[31])

fig, ax = plt.subplots(figsize=(8, 4.5))
for serie, nome, cor in [(acumulado_anterior, "Setembro", CINZA), (acumulado_atual, "Outubro", AMBAR)]:
    ax.step(serie.index, serie.values, where="post", color=cor, linewidth=2, label=nome.lower() + " de 2026")
    ax.plot(31, serie[31], marker="o", markersize=7, color=cor, markeredgecolor="white", markeredgewidth=1.5)
    ax.annotate(f"{nome}: {rm.numero(serie[31])}", (31, serie[31]), xytext=(10, 0),
                textcoords="offset points", va="center", fontsize=11, color=GRAFITE)
aplicar_padrao(ax, "E-mails enviados, acumulado no mês")
ax.set_xlabel("Dia do mês", fontsize=10, color=CINZA_TEXTO)
ax.set_xticks([1, 5, 10, 15, 20, 25, 31])
ax.set_xlim(1, 39)                         # espaço à direita para os rótulos
ax.set_ylim(0, None)
ax.yaxis.set_major_formatter(eixo_milhar)
ax.grid(axis="y", color=CINZA_CLARO, linewidth=0.8)
ax.legend(frameon=False, loc="upper left", fontsize=10, labelcolor=CINZA_TEXTO)
fig.tight_layout()
fig.savefig("envios_acumulados.png", dpi=200, facecolor="white")
plt.close(fig)
```

- `ax.step` desenha uma linha em degraus. Entre um disparo e outro, o acumulado não muda, e o degrau mostra isso. Para medidas que variam de forma contínua, use `ax.plot`, que liga os pontos com retas.
- `ax.annotate` escreve um texto ao lado de um ponto. Em gráficos de linha, o rótulo vai no fim de cada linha, com o nome da série e o valor final. Os demais valores são lidos pelo eixo.
- O ponto no fim de cada linha, com contorno branco, marca onde o rótulo se apoia.
- A função `eixo_milhar` faz o eixo vertical mostrar `50.000` em vez de `50000`, com a função `numero` do P.6.

### 7. Todo gráfico tem tabela e conferência

Um gráfico é uma forma de mostrar uma tabela. Duas práticas mantêm os dois iguais.

**Gravar a tabela junto com a imagem.** Cada gráfico sai com um CSV de mesmo nome, com os valores desenhados. Quem revisa o relatório confere o gráfico sem abrir o código, e os valores que ficaram sem rótulo têm onde ser lidos.

**Testar os valores desenhados.** O objeto do gráfico guarda os textos que foram escritos nele. Um teste lê esses textos e compara com o esperado:

```python
fig, ax = plt.subplots()
barras = ax.barh(["A", "B"], [1.5, 2.5])
ax.bar_label(barras, labels=["1,5%", "2,5%"])
print([texto.get_text() for texto in ax.texts])       # ['1,5%', '2,5%']
plt.close(fig)
```

Para o teste alcançar o gráfico, separe as responsabilidades em três tipos de função:

| Função | Recebe | Devolve | Como é testada |
| --- | --- | --- | --- |
| `tabela_...` | A base | A tabela com os valores do gráfico | Comparando os valores com o gabarito |
| `desenhar_...` | A tabela | A figura | Lendo os rótulos da figura |
| `salvar` | A figura e o caminho | Nada. Grava o arquivo | Conferindo que o arquivo existe |

Essa separação é a mesma dos módulos anteriores: o cálculo fica em funções que podem ser testadas sem olhar para uma imagem.

A última conferência é com os olhos. Um teste confirma os números, mas não vê uma legenda em cima de um rótulo nem um nome cortado na margem. Abra cada imagem gerada antes de usar, e de novo sempre que mudar os dados de um mês para outro: um nome de público mais longo ou um valor muito maior muda o encaixe.

## Exemplo aplicado

**Situação.** O relatório mensal de e-mail de outubro precisa de três gráficos, e os mesmos três serão refeitos em novembro. Você já tem o script do módulo P.6, que calcula as tabelas.

**Decisões de forma.**

| Conteúdo | Forma escolhida | Motivo |
| --- | --- | --- |
| Taxas gerais do mês e diferença para setembro | Números em destaque, sem gráfico | São três números. O texto do relatório os apresenta com a diferença em pontos percentuais |
| Taxa de clique por público | Barras horizontais ordenadas, uma cor, todos os valores escritos | Comparação entre cinco categorias de nomes longos |
| Taxa de abertura por público, outubro e setembro | Duas barras por público, âmbar e cinza, valores só em outubro | Dois períodos, cinco categorias |
| E-mails enviados, acumulado no mês | Duas linhas em degraus, com nome e total no fim | Evolução no tempo, dois períodos |

**O que os gráficos mostram.**

- **Clique por público.** Expositor lidera com 6,8%, sobre uma base de 162 entregues. Pré-credenciado e Credenciamento ficam juntos, com 3,7% e 3,6%. Prospecção, que tem o maior volume, fica em 1,6%.
- **Abertura por público.** A alta de outubro vem de dois públicos: Prospecção subiu de 46,2% para 54,7%, e Credenciamento de 54,0% para 59,1%. Pré-credenciado caiu de 42,4% para 40,6%.
- **Acumulado.** Outubro concentrou os envios na primeira quinzena: no dia 15, os 50.812 e-mails do mês já tinham saído. Setembro estava em 35.134 no mesmo dia e seguiu enviando até o dia 29, fechando em 64.307. O formato combina com o calendário da feira, que acontece de 20 a 22 de outubro.

**O limite do gráfico.** A barra de Expositor é a maior, e a base é a menor: 11 cliques em 162 entregues. O gráfico não mostra o tamanho da base. Esse aviso vai no texto do relatório, ao lado do gráfico, e a tabela gravada junto traz os entregues e os cliques de cada público.

**A conferência.** Os valores dos três gráficos saem das mesmas funções que geram as tabelas do P.6. O teste lê os rótulos desenhados no primeiro gráfico e confirma: 1,0%, 1,6%, 3,6%, 3,7% e 6,8%, de baixo para cima.

Os três gráficos de referência estão em [`dados/graficos_esperados/`](dados/graficos_esperados/), e a solução completa em [`gabarito/graficos_relatorio.py`](gabarito/graficos_relatorio.py).

## Exercício

**Os gráficos do relatório mensal de e-mail.**

### Parte A — O script (45 min)

1. Instale o matplotlib e acrescente a biblioteca ao `requirements.txt`.
2. Crie `graficos_relatorio.py`, que importa as funções do seu `relatorio_mensal.py`. Defina as cores do padrão visual como constantes e escreva a função `aplicar_padrao`.
3. Escreva as três funções de tabela:
   - taxa de clique por público, da maior para a menor, com entregues e cliques;
   - taxa de abertura por público nos dois meses, com a diferença em pontos percentuais;
   - e-mails enviados acumulados por dia do mês, do dia 1 ao 31.
4. Escreva as três funções de desenho, que recebem a tabela e devolvem a figura, com as formas da tabela do exemplo aplicado.
5. Escreva a função que gera tudo: recebe o arquivo do mês atual, o do mês anterior e a pasta de saída, e grava três imagens PNG e três tabelas CSV de mesmo nome. O script é chamado assim:

```
python graficos_relatorio.py dados/desempenho_email_outubro.csv dados/desempenho_email_setembro.csv saida_graficos
```

6. O título do primeiro gráfico traz o mês e o ano, obtidos da data dos dados. Não escreva "outubro" no código.

### Parte B — Conferência (20 min)

7. Abra as três imagens e compare com as de `dados/graficos_esperados/`. A forma deve ser a mesma. Diferenças pequenas de posição são aceitáveis.
8. Confira os valores das três tabelas CSV contra o gabarito abaixo e contra a saída do seu `relatorio_mensal.py`.

| Gráfico | Valores |
| --- | --- |
| Clique por público, outubro | Expositor 6,8%; Pré-credenciado 3,7%; Credenciamento 3,6%; Prospecção 1,6%; Reativação 1,0% |
| Abertura por público, setembro → outubro | Prospecção 46,2% → 54,7%; Credenciamento 54,0% → 59,1%; Pré-credenciado 42,4% → 40,6%; Reativação 11,2% → 12,6%; Expositor 64,7% → 64,8% |
| Acumulado no dia 15 | Outubro 50.812; setembro 35.134 |
| Acumulado no dia 31 | Outubro 50.812; setembro 64.307 |

9. Escreva ao menos quatro testes com `pytest`: os valores de uma tabela, os rótulos desenhados no gráfico de clique, o total do acumulado e a gravação dos seis arquivos em uma pasta temporária.

### Parte C — O mês seguinte (10 min)

10. Rode o script com os arquivos trocados, como se setembro fosse o mês atual e outubro o anterior, em outra pasta de saída. Não altere o código.
11. Abra as imagens. O título do primeiro gráfico deve dizer "setembro de 2026", as cores devem ter trocado de mês e nada deve estar cortado ou sobreposto.
12. Faça um commit com o script e os testes. As pastas de saída ficam fora do repositório.

### Entregável

O `graficos_relatorio.py`, o arquivo de testes e uma pasta de saída com as três imagens e as três tabelas de outubro.

### Critério de conclusão

- Os valores das tabelas conferem com o gabarito.
- Os testes passam, e um deles lê os rótulos da figura.
- As cores e o texto seguem o padrão: âmbar no mês atual, cinza no mês anterior, texto em grafite.
- O gráfico com duas séries tem legenda, e nenhum gráfico tem dois eixos verticais.
- O script rodou com os meses trocados sem alteração no código.
- Você abriu as seis imagens e não encontrou texto cortado ou sobreposto.

## Erros comuns

- Escolher o gráfico antes de saber o que o leitor precisa comparar.
- Fazer gráfico de dois ou três números que caberiam em uma frase.
- Pôr duas medidas de escalas diferentes no mesmo gráfico, com dois eixos verticais.
- Começar o eixo de um gráfico de barras em um valor diferente de zero.
- Pintar cada barra de uma cor quando todas são a mesma medida.
- Escrever os valores na cor da série, clara demais para leitura.
- Pôr um número em cada ponto de cada série.
- Deixar duas séries sem legenda.
- Escrever o mês ou o nome do cliente no código, em vez de obter dos dados.
- Esquecer o `plt.close` em um script que gera muitos gráficos.
- Entregar o gráfico sem abrir a imagem.
- Calcular os valores do gráfico em um lugar e os da tabela em outro.

## Checagem rápida

1. Por que as três taxas gerais do mês não viram um gráfico?
2. Por que não se usam dois eixos verticais para mostrar abertura e clique juntos?
3. No gráfico de dois meses, por que só as barras do mês atual têm o valor escrito?
4. Para que serve gravar um CSV ao lado de cada imagem?
5. O teste confirma que os rótulos estão corretos. Por que ainda é preciso abrir a imagem?

<details>
<summary>Respostas</summary>

1. Porque são três números. Em destaque, com a diferença para o mês anterior, eles são lidos mais depressa e com mais exatidão do que em barras.
2. Porque as duas escalas são ajustadas de forma independente, e a posição relativa das linhas passa a depender desse ajuste. O gráfico sugere uma relação que não está nos dados. Dois gráficos resolvem.
3. Porque um número em cada barra vira ruído. O destaque fica no período que o relatório analisa. Os valores do mês anterior são lidos pelo eixo, e o valor exato está na tabela.
4. Para que os valores desenhados possam ser conferidos sem abrir o código, e para dar leitura exata aos valores que ficaram sem rótulo.
5. Porque o teste não vê a aparência: uma legenda sobre um rótulo, um nome cortado na margem, barras espremidas. Isso muda quando os dados mudam.

</details>

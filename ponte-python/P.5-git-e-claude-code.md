# P.5 Git e Claude Code como par de programação

**Carga:** 2 h (50 min de leitura e instalação, 1 h 10 de exercício)

## Objetivo

Versionar o seu código com Git, guardá-lo no GitHub e programar com a ajuda do Claude Code, usando testes automatizados para conferir o que ele escreve.

## Por que importa no seu trabalho

Você agora tem scripts que tratam bases de clientes. Duas necessidades aparecem. A primeira é não perder trabalho e saber o que mudou: se o tratamento de hoje deu um resultado diferente do mês passado, você precisa saber qual linha de código mudou. A segunda é ganhar velocidade: o Claude Code escreve e altera código dentro do seu projeto. Para usá-lo com segurança, você precisa de uma forma objetiva de saber se o código continua certo. Essa forma são os testes.

As instruções de instalação têm como referência novembro de 2026. Em caso de diferença, vale a documentação oficial, indicada em cada seção.

## Conteúdo

### 1. O que é versionar

O **Git** registra a história de uma pasta de código. Os termos:

| Termo | Significado |
| --- | --- |
| **Repositório** | A pasta do projeto com a sua história |
| **Commit** | Um ponto salvo na história, com uma mensagem que explica a mudança |
| **Remoto** | A cópia do repositório em um servidor, como o GitHub |
| **Push** | Enviar os commits para o remoto |
| **Pull** | Trazer do remoto os commits que você ainda não tem |

Você já usa um repositório: o deste curso. Agora vai criar o dos seus scripts.

### 2. Instalar e configurar o Git

1. Baixe em [git-scm.com](https://git-scm.com/) e instale com as opções padrão. No Windows, o instalador se chama Git for Windows.
2. Abra um novo terminal no VS Code e confira:

```
git --version
```

3. Informe o nome e o e-mail que vão assinar os seus commits. Use o e-mail da sua conta do GitHub.

```
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

### 3. O que não entra no repositório

Antes do primeiro commit, crie na pasta `tratamento-bases` um arquivo chamado `.gitignore`, com este conteúdo:

```
.venv/
__pycache__/
.pytest_cache/
.env
dados_reais/
saida/
```

O Git ignora tudo o que estiver listado. Os motivos:

| Item | Por que fica fora |
| --- | --- |
| `.venv/` | É recriado a partir do `requirements.txt` |
| `__pycache__/` e `.pytest_cache/` | Arquivos temporários |
| `.env` | Guarda chaves e senhas |
| `dados_reais/` | Bases de clientes nunca vão para um repositório |
| `saida/` | Resultado de execução, que pode conter dados |

O `.gitignore` precisa existir antes do primeiro commit. Um arquivo que entrou na história continua nela mesmo depois de apagado.

A regra mais segura para dados de clientes é mais forte que o `.gitignore`: **mantenha as bases reais em uma pasta fora do projeto** e informe o caminho ao rodar o script. Assim, elas não podem ser enviadas por engano nem lidas por ferramentas que trabalham na pasta do projeto.

### 4. Criar o repositório e publicar no GitHub

Pelo VS Code:

1. Abra o painel de Controle do Código-Fonte (ícone de ramificação na barra lateral; em inglês, Source Control).
2. Clique em **Inicializar Repositório** (Initialize Repository).
3. Confira a lista de arquivos alterados. A pasta `.venv` não deve aparecer.
4. Escreva a mensagem "Primeira versão dos scripts de tratamento" e clique em **Commit**. Se o VS Code perguntar, aceite incluir todas as alterações.
5. Clique em **Publicar Branch** (Publish Branch), escolha publicar em um repositório **privado** do GitHub e autorize o acesso quando o navegador abrir.

Os comandos equivalentes no terminal, para um repositório vazio já criado no GitHub:

```
git init
git add .
git commit -m "Primeira versão dos scripts de tratamento"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/tratamento-bases.git
git push -u origin main
```

### 5. O ciclo do dia a dia

| Comando | O que faz |
| --- | --- |
| `git status` | Mostra o que mudou desde o último commit |
| `git diff` | Mostra as linhas alteradas |
| `git add arquivo.py` | Marca o arquivo para o próximo commit |
| `git commit -m "mensagem"` | Salva o ponto na história |
| `git push` | Envia para o GitHub |
| `git log --oneline` | Lista os commits |
| `git restore arquivo.py` | Descarta as alterações não salvas de um arquivo |

Boas práticas:

- **Um commit por mudança com sentido.** "Corrige telefone com ramal" é um commit. "Várias coisas" não ajuda ninguém.
- **A mensagem diz o que mudou e por quê,** em uma linha.
- **Commit antes de experimentar.** Se a experiência der errado, `git restore` volta ao ponto salvo.

### 6. Testes automatizados

Um **teste** é uma função que chama o seu código com uma entrada e confere a saída. A biblioteca `pytest`, instalada pelo `requirements.txt`, encontra e roda os testes.

Crie o arquivo `test_validacao.py`:

```python
import validacao


def test_email_fica_em_minusculas():
    assert validacao.padronizar_email(" Ana@Alfa.Example ") == "ana@alfa.example"


def test_telefone_sem_ddd_e_recusado():
    assert validacao.padronizar_telefone("9999-0004") is None
```

Rode:

```
python -m pytest
```

As regras:

- O arquivo começa com `test_` e cada função de teste também.
- `assert` afirma que uma condição é verdadeira. Se não for, o teste falha e o `pytest` mostra o esperado e o obtido.
- Cada teste verifica uma regra, e o nome diz qual.

O conferidor do módulo P.2 fazia o mesmo trabalho de forma artesanal. Os testes são o formato padrão, e têm uma função a mais: toda vez que o código muda, você roda todos de novo e descobre em segundos se uma regra antiga quebrou.

### 7. O que é o Claude Code

O **Claude Code** é o Claude trabalhando dentro do seu projeto. Em vez de você copiar código para uma conversa, ele lê os arquivos, propõe alterações, roda comandos e mostra o resultado. Você aprova ou recusa cada ação.

Formas de usar:

| Forma | Onde roda | Indicado para |
| --- | --- | --- |
| Extensão do VS Code | No seu computador, em um painel do editor | Quem já trabalha no VS Code |
| Terminal | No seu computador, com o comando `claude` | Quem prefere a linha de comando |
| Aplicativo de desktop | No seu computador, na aba de código do app | Quem prefere uma interface gráfica |
| Web | Em uma máquina na nuvem, ligada a um repositório do GitHub | Tarefas em repositórios sem dados locais; é assim que este curso é escrito |

É preciso uma assinatura paga do Claude (Pro, Max, Team ou Enterprise) ou uma conta do Console com créditos de API.

### 8. Instalar

**Extensão do VS Code:** no painel de Extensões, procure por **Claude Code** e instale. Requer o VS Code 1.94 ou mais novo. O painel abre pelo ícone do Claude na barra do editor. Detalhes na [documentação da extensão](https://code.claude.com/docs/en/vs-code).

**Terminal:** rode o instalador e abra um novo terminal.

| Sistema | Comando |
| --- | --- |
| Windows (PowerShell) | `irm https://claude.ai/install.ps1 \| iex` |
| macOS | `curl -fsSL https://claude.ai/install.sh \| bash` |

Confira com `claude --version`. Para começar, entre na pasta do projeto e rode `claude`. No primeiro uso, o login é feito pelo navegador. Detalhes no [guia de início rápido](https://code.claude.com/docs/en/quickstart).

No Windows, o Git for Windows da seção 2 é recomendado também para o Claude Code.

### 9. Dados de clientes e o Claude Code

O Claude Code lê arquivos da pasta do projeto e envia o conteúdo relevante ao modelo. Tudo o que você definiu no módulo 1.5 vale aqui, com um agravante: a leitura acontece sem você colar nada.

Três camadas de proteção, da mais forte para a mais fraca:

1. **Bases reais fora da pasta do projeto.** É a única garantia completa.
2. **Regras de bloqueio de leitura.** Crie o arquivo `.claude/settings.json` na pasta do projeto:

```json
{
  "permissions": {
    "deny": [
      "Read(./dados_reais/**)",
      "Read(./.env)"
    ]
  }
}
```

   Com isso, o Claude Code não lê nem edita esses caminhos. A regra cobre as ferramentas de arquivo. Um comando executado no terminal ainda poderia ler o conteúdo, e por isso ela não substitui a primeira camada. Detalhes na [documentação de permissões](https://code.claude.com/docs/en/permissions).
3. **Aprovação de cada ação.** Leia o que o Claude Code pede para fazer antes de aceitar.

Dentro do projeto ficam só os dados fictícios do curso.

### 10. Como trabalhar com o Claude Code

A documentação oficial resume o trabalho em quatro passos: explorar, planejar, codar e salvar em um commit. As práticas abaixo seguem essa ordem.

**Comece pedindo entendimento.** "Explique o que este projeto faz e como os arquivos se relacionam." Você confere se ele entendeu antes de pedir mudanças.

**Um pedido, uma mudança, com a forma de verificar.** "Acrescente à função `padronizar_telefone` o tratamento de ramal, descartando o que vier depois da palavra ramal. Escreva testes para os casos novos e rode todos os testes."

**Leia a alteração antes de aceitar.** O Claude Code mostra as linhas que vai mudar. Se você não entende uma linha, pergunte. Código que você não consegue ler é código que você não consegue manter.

**Faça commit depois de cada mudança aceita.** Se a próxima der errado, você volta ao ponto anterior.

**Para mudanças grandes, peça o plano primeiro.** "Antes de alterar, descreva o que você pretende fazer." Corrigir um plano custa menos que desfazer código.

**Use os testes como juiz.** O pedido termina com "rode os testes". Se passam, a mudança não quebrou as regras que você já tinha.

Comandos úteis dentro do Claude Code:

| Comando | O que faz |
| --- | --- |
| `/help` | Lista os comandos |
| `/clear` | Limpa a conversa para começar um assunto novo |
| `/init` | Cria um arquivo `CLAUDE.md` com a descrição do projeto |

### 11. O arquivo CLAUDE.md

O `CLAUDE.md` fica na raiz do projeto e é lido pelo Claude Code no começo de cada sessão. É o equivalente às instruções de um Project (módulo 2.1), para código. Coloque nele o que só você sabe:

```
# Tratamento de bases

Scripts que tratam bases de contatos para importação em CRM.

- As regras de cada campo estão em validacao.py. Toda regra nova ganha um teste.
- Funções de padronização devolvem None ou texto vazio quando não há resultado.
  Elas não interrompem o script.
- Rode os testes com: python -m pytest
- A pasta dados/ tem só dados fictícios. Bases reais ficam fora do projeto.
```

Vale o que você aprendeu sobre instruções: contexto e regras com motivo, em tom normal, sem repetir o que o modelo já sabe.

## Exemplo aplicado

Uma sessão curta no projeto `tratamento-bases`:

1. **Você:** "Leia o `validacao.py` e liste entradas de telefone que a função trata de forma incorreta ou duvidosa. Não altere nada."
2. **Claude Code:** aponta, por exemplo, que `(11) 99990-0001 ramal 23` é recusado, porque os dígitos do ramal entram na contagem.
3. **Você** decide a regra: o ramal deve ser descartado e o telefone aproveitado.
4. **Você:** "Altere `padronizar_telefone` para descartar o que vier depois de `ramal` ou `r.`, sem mudar o comportamento dos casos atuais. Acrescente testes para os casos novos e rode todos."
5. **Claude Code:** mostra a alteração, você lê e aprova; ele roda os testes e todos passam.
6. **Você:** confere o resultado com `git diff` e faz o commit: "Descarta ramal ao padronizar telefone".

A decisão sobre a regra foi sua. O Claude Code encontrou o caso, escreveu o código e os testes. Os testes garantiram que os 25 casos antigos continuam valendo.

## Exercício

**Tempo:** 1 h 10

### Parte A — Git (25 min)

1. Instale e configure o Git (seção 2).
2. Crie o `.gitignore` (seção 3).
3. Inicialize o repositório, faça o primeiro commit e publique em um repositório privado do GitHub (seção 4).
4. Abra o repositório no site do GitHub e confirme que `.venv` não está lá.
5. Faça uma alteração pequena em um script, confira com `git diff`, faça um segundo commit e envie.

### Parte B — Testes e Claude Code (45 min)

6. Crie o `test_validacao.py` com os dois testes da seção 6 e rode `python -m pytest`.
7. Instale o Claude Code pela forma que preferir (seção 8).
8. Crie o `.claude/settings.json` da seção 9.
9. Abra o Claude Code na pasta do projeto e peça uma explicação do que o projeto faz. Confira se está correta.
10. Peça: "Escreva testes com pytest para as funções de `validacao.py`, cobrindo os casos de `dados/casos_p2.csv`. Agrupe por função e dê nomes que descrevam a regra testada. Rode os testes."
11. Leia os testes gerados. Para cada grupo, confirme que você sabe qual regra ele verifica.
12. Peça que ele aponte entradas que as suas funções tratam de forma duvidosa, sem alterar nada. Escolha uma, decida a regra, peça a alteração com testes e leia a mudança antes de aceitar.
13. Rode `python -m pytest` você mesmo, faça o commit e envie.
14. Rode `/init`, leia o `CLAUDE.md` gerado e ajuste com as convenções do seu projeto. Faça o commit.

Se você não tiver acesso ao Claude Code, faça os passos 10 a 12 no app do Claude, colando o `validacao.py`, que não contém dados. Os passos de Git e de testes não mudam.

**Entregável:** o endereço do repositório privado, com pelo menos quatro commits, e a saída do `python -m pytest`.

**Critério de conclusão:**

- O repositório tem o `.gitignore`, os scripts, os testes e o `CLAUDE.md`, e não tem `.venv` nem arquivos de saída.
- Há pelo menos 15 testes, e todos passam.
- A regra nova do passo 12 foi decidida por você, tem teste e está em um commit próprio.
- Não há base real dentro da pasta do projeto.

Um exemplo de arquivo de testes está em [`gabarito/test_validacao.py`](gabarito/test_validacao.py). Ele cobre também as funções do projeto.

## Erros comuns

- Fazer o primeiro commit antes de criar o `.gitignore`.
- Guardar bases reais dentro da pasta do projeto.
- Aceitar alterações do Claude Code sem ler.
- Pedir várias mudanças de uma vez e não saber qual quebrou o quê.
- Pedir a alteração sem pedir os testes.
- Passar dias sem commit e não conseguir voltar a uma versão que funcionava.
- Escrever uma chave de acesso em um arquivo que vai para o repositório.

## Checagem rápida

1. Qual a diferença entre commit e push?
2. Por que o `.gitignore` deve existir antes do primeiro commit?
3. O que é um teste automatizado e o que ele garante quando o código muda?
4. Qual é a proteção mais forte para bases reais ao usar o Claude Code?
5. Por que pedir o plano antes de uma mudança grande?

<details>
<summary>Respostas</summary>

1. O commit salva um ponto na história, no seu computador. O push envia os commits para o GitHub.
2. Porque um arquivo que entrou na história continua nela mesmo depois de apagado.
3. É uma função que chama o código com uma entrada e confere a saída. Ao rodar todos depois de uma mudança, você sabe se alguma regra antiga quebrou.
4. Manter as bases em uma pasta fora do projeto.
5. Porque corrigir um plano custa menos do que desfazer código já escrito.

</details>

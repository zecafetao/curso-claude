# Definição das áreas do CRM (fictício)

O campo `area` do layout de importação agrupa os contatos pela função que exercem na empresa. A área decide quais comunicações o contato recebe.

## Áreas

| Área | Quem entra |
| --- | --- |
| `Diretoria` | Sócios, proprietários, fundadores, presidentes, vice-presidentes, diretores e cargos de nível C (CEO, CFO, COO e semelhantes), de qualquer área da empresa |
| `Compras` | Compras, suprimentos, procurement, sourcing e supply chain |
| `Produção` | Produção e operação de fábrica, planejamento e controle da produção (PCP), qualidade, engenharia, pesquisa e desenvolvimento (P&D), desenvolvimento e design de embalagens |
| `Marketing` | Marketing, marca, produto, trade marketing, comunicação e mídias sociais |
| `Comercial` | Vendas, gestão de contas, representação comercial e desenvolvimento de negócios |
| `Outros` | As demais funções: administrativo, financeiro, recursos humanos, jurídico, tecnologia da informação e logística. Também os cargos que não permitem identificar a função |

## Regras

1. O nível de direção vem antes da função. `Diretora de Marketing` é `Diretoria`, e não `Marketing`.
2. Gerentes, coordenadores, supervisores e heads ficam na área em que atuam. `Head of Procurement` é `Compras`.
3. Vale a função exercida, e não a formação que aparece no cargo. `Engenheiro de Vendas` é `Comercial`.
4. Os cargos chegam como o contato informou: abreviados, em inglês ou com siglas. Classifique pelo significado.
5. Na dúvida entre duas áreas, use `Outros`. Um contato em `Outros` recebe só as comunicações gerais; um contato na área errada recebe a mensagem errada.

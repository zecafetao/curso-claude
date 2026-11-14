# Regras de segmentação de contatos — Expo Modelo 2026 (fictício)

Cada contato da base de visitação recebe um segmento, definido pelo cargo e pelo setor da empresa. O segmento decide qual argumento o contato recebe nos e-mails.

## Setores-alvo

Indústrias que usam embalagens no produto: Alimentos, Bebidas, Cosméticos, Farmacêutico, Higiene e limpeza, Pet.

Fabricantes de embalagens não são setor-alvo de visitação. Eles têm perfil de expositor e são tratados pela equipe comercial.

## Segmentos

| Segmento | Quem é | Argumento que recebe |
| --- | --- | --- |
| `Compras` | Quem negocia e compra | Comparar fornecedores no mesmo pavilhão |
| `Tecnico` | Quem especifica a embalagem | Lançamentos em funcionamento e conteúdo técnico |
| `Marketing` | Quem cuida de marca e produto | Tendências e embalagens recicláveis |
| `Diretoria` | Quem decide investimento | Redução de custo e encontro com fornecedores estratégicos |
| `ForaDoPerfil` | Quem não é público de visitação | Não entra na campanha |

## Regras, em ordem de precedência

Aplique a primeira regra que servir.

1. Setor fora da lista de setores-alvo: `ForaDoPerfil`, qualquer que seja o cargo.
2. Sócio, proprietário, presidente, diretor ou cargo de nível C (CEO, COO, CFO e semelhantes): `Diretoria`, qualquer que seja a área.
3. Cargo de compras, suprimentos, procurement ou supply chain: `Compras`.
4. Cargo de pesquisa e desenvolvimento, desenvolvimento ou design de embalagens, engenharia, qualidade ou produção: `Tecnico`.
5. Cargo de marketing, marca, produto, trade ou comunicação: `Marketing`.
6. Qualquer outro cargo: `ForaDoPerfil`.

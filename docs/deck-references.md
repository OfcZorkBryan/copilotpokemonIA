# Referências competitivas e ranking por coleção

Consulta em 1º de novembro de 2026 (America/Sao_Paulo). Contexto das páginas individuais: C1 Standard.

| Arquétipo | Vitórias | Derrotas | Empates | Partidas | Vitórias / total |
|---|---:|---:|---:|---:|---:|
| Umbreon + Mega Sableye ex | 139 | 113 | 7 | 259 | 53,67% |
| Umbreon + Hydreigon | 437 | 414 | 20 | 871 | 50,17% |
| Mega Manectric ex + Heliolisk | 135 | 90 | 12 | 237 | 56,96% |

Fontes primárias dos resultados:

- https://play.limitlesstcg.com/decks/umbreon-c1-mega-sableye-ex-b3b?format=standard&game=POCKET&set=C1
- https://play.limitlesstcg.com/decks/umbreon-c1-hydreigon-b1?format=standard&game=POCKET&set=C1
- https://play.limitlesstcg.com/decks/mega-manectric-ex-b2b-heliolisk-b4?format=standard&game=POCKET&set=C1

A tabela geral e páginas individuais diferiam durante a consulta. Os números usados vêm somente das páginas individuais acima. O snapshot é estático, com data explícita; não é atualização contínua. A taxa inclui empates no denominador, conforme os números exibidos pela fonte.

## O que isso muda

O ranking recalcula automaticamente conforme o inventário registrado: menos cópias faltantes, menos cópias promocionais faltantes, menor custo histórico conhecido e, por último, referência competitiva do arquétipo. A comparação não consulta a conta nem abre pacotes.

As listas exatas, probabilidades de pacotes e preços de troca vieram da V2 e não foram revalidados aqui. O custo calculado é parcial quando há cartas promocionais/de loja. O aplicativo agora identifica explicitamente essa origem, remove os tiers antigos da apresentação e não atribui a taxa do arquétipo à lista específica. O ranking minimiza os critérios locais indicados; não promete o número mínimo matemático de pacotes, economia garantida ou vitória em todas as competições.

## Testes

tests/ui_decks_node.js foi escrito antes da alteração. A prioridade anterior falhou no caso de deck quase completo com percentual antigo baixo contra deck mais distante com percentual antigo alto. Após a mudança, os testes verificam prioridade de coleção/custo, restrição promocional, procedência das estatísticas, preservação das listas de 20 cartas e ausência de alteração do inventário/backup. Scripts de interface e observação continuam passando.

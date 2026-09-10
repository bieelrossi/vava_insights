# Qualidade dos dados e cluster de surrender

## Estado da descoberta

O endpoint de partidas armazenadas reportou `total=151`; a paginação percorreu
8 páginas e terminou com `after=0`. Portanto, as 151 partidas representam todo
o histórico competitivo retornado por esse endpoint no momento da coleta, não
apenas uma página recente. O período vai de 17/07/2025 a 04/09/2026.

O histórico contém 151 partidas competitivas. Três delas têm eventos de round
terminais cujo `end_type` é `Surrendered`. Os detalhes completos da API mantêm
esses eventos na lista de `rounds`, mas eles não fazem parte do placar final
da partida. Há 15 eventos desse tipo ao todo:

| match_id | placar final (Red-Blue) | rounds no detalhe | eventos `Surrendered` | time do jogador | tamanho da party |
| --- | ---: | ---: | ---: | --- | ---: |
| `4e904a5a-3af9-45af-9e07-d878b8fad9dc` | 4-0 | 13 | 9 | Blue | 3 |
| `ab1067b5-cfab-46c2-aa6e-3cb91fac4c84` | 1-11 | 14 | 2 | Red | 5 |
| `dd8d8fbc-a793-4f1d-8357-bc2e10c08d3d` | 9-3 | 16 | 4 | Blue | 5 |

Em todos os três casos, o time do jogador é o lado que se rendeu. Os rounds
válidos pelo placar somam 3.216; a lista de eventos soma 3.231. A diferença é
exatamente esses 15 registros terminais.

Foi feita uma auditoria adicional nos 151 JSONs de detalhes. Os campos
alternativos de conclusão disponíveis no endpoint bruto da Riot, como
`completionState` e `isCompleted`, não estão presentes nesses detalhes v2
armazenados. Também não foram encontrados outros códigos de round que indiquem
surrender. Assim, `end_type == "Surrendered"` é o único sinal observável de
surrender nesta fonte.

## Política de dados adotada

Uma partida com surrender **continua na amostra de partidas**. Ela é válida
para análises de resultado da partida, contexto de party, mapa, agente e para
o futuro estudo de surrender.

Os eventos com `end_type == "Surrendered"` são **inválidos para métricas por
round** e deverão ser excluídos antes de calcular: rounds jogados, vitória por
round, K/D/assistências por round, ADR, ACS, KAST, first kill/death, trade,
economia, lado e clutch.

O pipeline deverá preservar, por partida, pelo menos estes campos:

- `has_surrender_event`
- `surrender_event_count`
- `surrendering_team` (lado oposto ao `winning_team` dos eventos terminais)
- `target_team_surrendered`
- `last_valid_round_number`
- `party_size`, `party_type` e `opponent_largest_party_size`

Essa separação evita que placeholders posteriores ao surrender alterem
métricas de desempenho e mantém o contexto necessário para estudá-los.

## Cluster analítico: surrender

O cluster inicial é composto pelas três partidas acima, com o rótulo
`target_team_surrendered`. Ele é pequeno demais para inferências, mas deve ser
mantido como coorte separada e rastreável, não removido silenciosamente.

Perguntas planejadas para quando houver mais observações:

1. Com que frequência o time do jogador se rende, por ato e em janela recente?
2. A taxa de surrender muda entre solo, duo, trio e 5-stack? Comparar taxas e
   intervalos de confiança, sem atribuir causalidade a party.
3. Qual é o placar, saldo de rounds, lado e tipo de término imediatamente antes
   do surrender?
4. Há concentração por mapa, agente, composição, roster exato ou core
   recorrente?
5. O surrender é precedido por sequência de rounds perdidos, eco/force mal
   sucedido, desconexão/AFK, penalidade ou desvantagem de jogadores?
6. Em 5-stack, o comportamento difere de outros tamanhos de party após
   controlar ato, mapa, placar e composição?

Os dados atuais respondem apenas à presença e ao contexto básico: 3 surrenders
em 151 partidas; 2 ocorreram em 5-stack e 1 em trio. Isso não é evidência de
que 5-stack aumente ou reduza a propensão a surrender.

## Pré-requisito antes de recalcular o relatório

Antes de publicar novas métricas por round, o pipeline deve reconciliar, em
cada partida, os totais derivados dos rounds válidos com os totais oficiais de
partida. Uma divergência deve interromper a execução e identificar a partida,
em vez de gerar artefatos processados aparentemente completos.

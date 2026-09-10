# vava_insights

Projeto de analytics de performance de jogadores de Valorant.

## Estrutura

- `data/`: dados brutos, processados e curados.
- `docs/`: documentacao do projeto.
- `notebooks/`: exploracao e validacao.
- `src/vava_insights/`: codigo do analytics engine.
- `tests/`: testes automatizados.
- `reports/`: relatorios gerados.
- `configs/`: configuracoes.
- `scripts/`: scripts operacionais.

## Executar a compilacao de um jogador

Use o nome do jogador. Para uma análise já existente, o `#codigo` é opcional:

```powershell
$env:PYTHONPATH = "src"
python -m vava_insights.main "nome#codigo"
python -m vava_insights.main "nome"
# Historico completo disponivel
python -m vava_insights.main "nome#codigo" --all-history
```

O pipeline procura partidas cacheadas em `data/raw/matches/`. Para coletar um
jogador novo pela API Henrik, defina `HENRIK_API_KEY` no ambiente antes da
execucao. O comando gera em `reports/`:

- `<jogador>.stats.json`: estatisticas estruturadas para o agente;
- `<jogador>.prompt.md`: instrucoes para o agente
	`.github/agents/valorant-performance-analyst.agent.md`.

O pacote inclui `deterministic_insights`: achados calculados por regras Python
com evidencias, thresholds, status de amostra e limitacoes. O agent interpreta
esses achados e escreve o relatorio, mas nao recalcula nem altera os numeros.

Tambem inclui `impact` e `round_events`, portados do notebook, com round win
rate, KAST, dano, FK, FD, trade e conversoes apos first kill/first death. Os
eventos de surrender sao excluidos das metricas por round.

O bloco `economy` cobre classes de compra, pistolas, armas, finais de round e
clutch proxy. O bloco `composition` cobre roles nominais, composicoes e
teammates recorrentes, sempre com thresholds e limitacoes descritivas.

O bloco `squad` cobre party size, premade, five-stack, roster exato e teammates
de party, incluindo cobertura de `party_id` e intervalos de Wilson para win rate.

O bloco `advanced_impact` adiciona uso de habilidades C/Q/E e ultimate X,
normalizados por round e comparados entre partidas com e sem uso; refrag dado e
recebido por inimigo e janela de 5 segundos; e posicionamento no momento de
kills/mortes. Uma kill e classificada como `supported` quando existe aliado a
ate 2.000 unidades de coordenada do mapa; caso contrario e `isolated`. Essas
comparacoes sao deterministicas e descritivas, nao provas de causalidade.

O bloco `advanced_impact.position_and_refrags` tambem expoe cortes
deterministicos por mapa, agente, lado, classe economica e teammate identificado
como proximo no snapshot do evento. O bloco `contextual_splits` cruza o
desempenho do alvo com mapa, party, agente, economia da equipe e presenca de
teammates; em `contextual_splits.by_map` compara ainda o alvo com a media dos
aliados da mesma partida. Tambem expoe alinhamento da economia do alvo com a
classe modal do proprio time. Esses cortes sao agregados descritivos, com
amostra e limitacoes preservadas para o agente interpretar sem recalcular.

## Armazenamento por jogador

O cache bruto de partidas fica fora do repositorio, em:

```text
%APPDATA%/vava_insights/players/<jogador>/raw/
```

As analises geradas ficam separadas por jogador no workspace:

```text
data/processed/<jogador>/stats.json
reports/<jogador>/prompt.md
```

Esses dados sao gerados e ignorados pelo Git. O codigo, configuracoes,
documentacao e notebook permanecem no projeto; dados brutos, derivadas e
relatorios de jogadores nao precisam ser versionados.

O arquivo `.agent.md` e uma instrucao do Copilot, nao um modulo Python
executavel. Depois da compilacao, use o prompt gerado para solicitar o
relatorio final em Markdown.

Por padrao, o comando analisa ate 100 partidas. Use `--all-history` para
analisar todas as partidas cacheadas ou paginar todo o historico **disponivel
na API Henrik**. Esse nome de escopo nao garante equivalencia com Tracker ou
com todo o historico exibido pelo cliente Riot; o pacote inclui
`source_coverage.by_map_season` para auditar exatamente quais IDs por mapa e
ato entraram na agregacao. As opcoes `--max-matches` e `--all-history` sao
mutuamente exclusivas.

O endpoint Henrik v2 atualmente pode fornecer apenas contadores agregados de
casts. O pacote registra `advanced_impact.ability_usage.event_detail`: se a
fonte passar eventos de cast com timestamp, alvo ou resultado de efeito, esses
campos sao preservados; se nao passar, o status e `unavailable` e o pipeline
nao infere eficacia a partir de contadores por partida.

Quando `--all-history` e `HENRIK_API_KEY` estao presentes, o pipeline consulta
o inventario remoto antes de reutilizar os artefatos, compara os IDs das
partidas e baixa os detalhes que ainda nao estao no cache. Sem a chave, o modo
permanece offline e usa apenas as partidas cacheadas.

O pipeline reutiliza `data/processed/<jogador>/stats.json` quando a analise ja
existe. O arquivo `analysis_manifest.json` registra o jogador, PUUID, escopo,
quantidade de partidas e data de geracao. Use `--refresh` para forcar uma nova
analise e atualizar esses arquivos.

Quando o jogador já possui `analysis_manifest.json`, informar apenas o nome é
suficiente. Para a primeira coleta pela API, informe `nome#tag`, pois a API
precisa do tag para resolver a conta.

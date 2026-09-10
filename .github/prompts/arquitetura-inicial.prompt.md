# Valorant Analytics — Project Bootstrap

Você é responsável por me ajudar a estruturar um projeto Python de análise estatística e tática de performance de Valorant.

## Contexto

Tenho um notebook existente que utiliza a `valo_api` para coletar dados das minhas partidas.

O arquivo do notebook será informado/estará disponível no workspace. **Analise o notebook existente antes de propor ou criar código.**

Também existe um prompt de referência com a metodologia de análise que quero reproduzir. A metodologia busca analisar:

* impacto real do jogador;
* K/D, ACS, ADR e KAST;
* First Kill / First Death;
* Attack vs Defense;
* Agent Pool;
* Role;
* Mapas;
* composição do time;
* teammates;
* armas;
* economia;
* pistols;
* consistência;
* tendências;
* pontos fortes e gargalos.

## Objetivo

Transformar o notebook exploratório em um **analytics engine reproduzível**, no qual as conclusões sejam derivadas principalmente por:

* matemática;
* estatística;
* feature engineering;
* regras;
* comparação de baselines;
* análise contextual.

Uma LLM poderá futuramente interpretar os resultados, mas **não deve ser responsável por descobrir as métricas ou inventar conclusões**.

Fluxo desejado:

```text
valo_api
→ raw data
→ normalization
→ features
→ statistical metrics
→ contextual analysis
→ impact analysis
→ rule engine
→ insights
→ report
```

## Princípios

1. Não invente dados que a API não fornece.
2. Não faça inferências causais sem evidência.
3. Sempre considere tamanho de amostra e confiabilidade.
4. Não avalie métricas isoladamente quando contexto estiver disponível.
5. Considere role, agente, mapa, lado, composição e teammates.
6. Diferencie All-Time de Current Act.
7. Agentes podem ter filtragem proporcional de outliers; mapas não devem ser removidos por baixa amostra.
8. Baixa amostra deve reduzir a confiança da conclusão, não necessariamente eliminar o dado.
9. Lógica de negócio deve ficar em `src/`, não exclusivamente em notebooks.
10. Métricas importantes devem possuir testes.
11. Thresholds e regras devem ser configuráveis.
12. Prefira conclusões estatisticamente defensáveis a conclusões especulativas.

## Arquitetura inicial

Avalie antes de alterar:

```text
data/
notebooks/
src/
tests/
rules/
configs/
reports/
docs/
```

Dentro de `src`, considere separar responsabilidades como:

```text
ingestion
normalization
features
metrics
statistics
context
roles
agents
maps
economy
composition
teammates
insights
reporting
```

A estrutura final deve ser definida após analisar os dados reais disponíveis.

## Métricas

O sistema deverá evoluir para calcular, quando os dados permitirem:

* K/D
* ADR
* ACS
* KAST
* FK rate
* FD rate
* FK/FD
* Net First Blood
* Trade Rate
* Round Impact
* Attack/Defense performance
* Agent Pool concentration
* Role similarity
* Map performance
* Composition performance
* Teammate interactions
* Economic performance
* Pistol performance
* Clutch performance
* Consistency
* Trends
* Player baseline
* Impact Score

Para cada métrica importante, documentar:

```text
definition
formula
inputs
interpretation
limitations
confidence
```

## Impacto

Não assumir que K/D alto significa impacto alto.

Sempre que os dados permitirem, analisar:

```text
mechanical impact
tactical/contextual impact
round impact
match impact
```

First Kill e First Death devem considerar, quando disponíveis:

```text
FK
FD
trade
round outcome
side
agent
map
round state
```

## Estatística

Evite regras arbitrárias como:

```python
if games < 5:
    ignore()
```

Prefira métodos que considerem:

* sample size;
* variance;
* confidence intervals;
* percentiles;
* effect size;
* statistical significance quando aplicável.

Toda conclusão deve poder ser rastreada até as métricas que a sustentam.

## Desenvolvimento

Não implemente o projeto inteiro de uma vez.

Primeiro:

1. Analise o notebook existente.
2. Identifique as fontes e estruturas de dados.
3. Liste os dados disponíveis.
4. Identifique os dados ausentes.
5. Faça um gap analysis entre os dados disponíveis e as métricas desejadas.
6. Proponha a arquitetura.
7. Proponha o modelo de dados.
8. Só então comece a implementação incremental.

Não reescreva o notebook sem necessidade.

Reaproveite análises úteis, mas mova lógica de negócio para módulos Python reutilizáveis.

## Primeira tarefa

**Nesta primeira interação, NÃO implemente o sistema inteiro.**

Analise o workspace e entregue:

1. resumo do notebook existente;
2. dados que a `valo_api` atualmente fornece;
3. análises que já existem;
4. métricas que já podem ser calculadas;
5. métricas que dependem de dados ainda ausentes;
6. riscos e limitações;
7. arquitetura proposta;
8. estrutura inicial de diretórios;
9. roadmap incremental.

Depois dessa análise, aguarde minha aprovação antes de fazer mudanças estruturais grandes.

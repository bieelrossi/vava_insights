# Copilot Instructions — Valorant Performance Analytics

## 1. Objetivo do projeto

Este projeto é um motor de análise estatística e tática de performance de jogadores de Valorant.

O objetivo principal é transformar dados brutos obtidos através da `valo_api` em:

1. dados normalizados;
2. features;
3. métricas estatísticas;
4. métricas contextuais;
5. indicadores de impacto;
6. hipóteses baseadas em evidências;
7. insights acionáveis;
8. relatórios.

A prioridade é construir um **analytics engine reproduzível**, e não simplesmente um notebook de análise.

---

## 2. Princípio fundamental

Sempre priorize:

```text
Dados corretos
→ Modelo de dados correto
→ Feature engineering
→ Métricas
→ Contexto
→ Inferência estatística
→ Insights
→ Relatório
```

Não utilizar uma LLM para substituir cálculos estatísticos que possam ser realizados deterministicamente pelo código.

A LLM, quando utilizada futuramente, deverá atuar principalmente como camada de interpretação e comunicação.

---

## 3. Fonte de dados

A principal fonte de dados é a `valo_api`.

Nunca invente dados que não estejam disponíveis na API ou no dataset processado.

Quando uma análise depender de uma variável inexistente:

* não criar uma aproximação silenciosa;
* não inferir o valor;
* marcar explicitamente a métrica como indisponível;
* explicar quais dados seriam necessários.

Preferir retornar estruturas explícitas como:

```python
MetricResult(
    value=None,
    status="insufficient_data",
    reason="Required field X is unavailable."
)
```

ou equivalente.

---

## 4. Notebooks

Notebooks são utilizados para:

* exploração;
* prototipação;
* visualização;
* validação;
* experimentação.

Não colocar lógica de negócio permanente exclusivamente em notebooks.

Quando uma função ou algoritmo se tornar parte do sistema, movê-lo para `src/`.

O notebook deve consumir as funções do projeto, e não duplicar sua implementação.

---

## 5. Arquitetura

Manter separação clara entre:

```text
ingestion
normalization
data model
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

Evitar criar módulos "utils" gigantes contendo funcionalidades sem relação.

Cada módulo deve possuir responsabilidade única.

---

## 6. Estatística

Sempre considerar o tamanho da amostra.

Uma porcentagem isolada nunca deve ser interpretada sem considerar:

* número de observações;
* variância;
* distribuição;
* intervalo de confiança;
* confiabilidade;
* possíveis vieses de seleção.

Evitar thresholds arbitrários quando houver uma alternativa estatística melhor.

Quando thresholds forem necessários:

* torná-los configuráveis;
* documentar sua justificativa;
* evitar hardcode dentro das funções.

---

## 7. Correlação ≠ causalidade

Nunca transformar automaticamente uma associação em causalidade.

Exemplo:

```text
Win Rate com Agente X = 70%
```

não permite concluir:

```text
Agente X melhora a performance do jogador.
```

Investigar possíveis variáveis de confusão:

* mapa;
* composição;
* teammates;
* adversários;
* role;
* tamanho da amostra;
* período.

Quando causalidade não puder ser determinada, utilizar termos como:

* associação;
* correlação;
* evidência;
* hipótese;
* possível explicação.

---

## 8. Contexto é obrigatório

Métricas individuais devem ser contextualizadas sempre que possível.

Exemplos:

```text
K/D
ADR
ACS
KAST
FK
FD
```

podem possuir interpretações diferentes dependendo de:

* role;
* agente;
* mapa;
* lado;
* composição;
* teammates;
* estado do round.

Evitar conclusões baseadas em uma única métrica.

---

## 9. Role-aware analytics

Não comparar indiscriminadamente jogadores ou métricas de roles diferentes.

Quando apropriado, comparar performance com:

```text
player baseline
role baseline
agent baseline
map baseline
```

O sistema deve considerar que Duelist, Initiator, Controller e Sentinel possuem expectativas comportamentais diferentes.

Sempre que possível, representar essas expectativas através de dados, métricas ou regras explícitas.

---

## 10. Impacto

Não definir impacto exclusivamente através de:

```text
K/D
ACS
ADR
```

Considerar, quando os dados permitirem:

* First Kill;
* First Death;
* trade;
* KAST;
* dano;
* round outcome;
* side;
* clutch;
* multi-kill;
* economia;
* contexto do round;
* força do adversário.

Distinguir:

```text
Mechanical Impact
Tactical Impact
Round Impact
Match Impact
```

quando houver dados suficientes.

---

## 11. First Kill / First Death

Sempre que os dados permitirem, calcular separadamente:

```text
FK Rate
FD Rate
FK/FD
Net First Blood
Trade Rate
Round Win After FK
Round Loss After FD
```

Também considerar:

* Attack;
* Defense;
* Agent;
* Map;
* Round State.

Não considerar First Death automaticamente negativa sem avaliar o contexto.

---

## 12. Outliers

Agentes podem possuir análise proporcional de amostra.

Não excluir dados permanentemente.

Outliers devem permanecer disponíveis para análises marginais.

Mapas não devem ser excluídos apenas por baixa amostra.

Para amostras pequenas, preferir reduzir a confiança da conclusão em vez de simplesmente remover os dados.

---

## 13. All-time vs Current Act

Distinguir:

```text
All Time
Current Act
```

All-time:

* baseline histórico;
* maior amostra;
* referência estrutural.

Current Act:

* comportamento recente;
* tendências;
* mudanças;
* evolução/regressão.

Não substituir uma fonte pela outra.

Sempre que possível calcular:

```text
baseline
current
delta
trend
confidence
```

---

## 14. Métricas

Toda métrica nova deve possuir:

* definição;
* fórmula;
* inputs;
* output;
* unidade;
* interpretação;
* limitações;
* testes.

Exemplo:

```python
def calculate_trade_rate(...) -> MetricResult:
    """
    Calculate the percentage of player deaths that were successfully traded.
    """
```

Evitar funções que retornem apenas números quando metadados de confiabilidade forem relevantes.

---

## 15. Testes

Toda métrica estatística importante deve possuir testes unitários.

Testar também:

* dataset vazio;
* valores nulos;
* divisão por zero;
* amostra pequena;
* valores extremos;
* tipos inválidos;
* casos conhecidos.

Preferir testes com datasets artificiais nos quais o resultado esperado possa ser calculado manualmente.

---

## 16. Tipagem

Utilizar type hints em código de produção.

Preferir:

```python
def calculate_metric(data: DataFrame) -> MetricResult:
```

em vez de funções sem tipos.

Utilizar `dataclass`, `TypedDict`, `Enum` ou Pydantic quando isso melhorar a clareza do modelo.

---

## 17. Configuração

Thresholds, pesos, parâmetros estatísticos e regras de negócio não devem ficar espalhados pelo código.

Preferir arquivos de configuração como:

```text
configs/
rules/
```

Exemplo:

```text
configs/statistics.yaml
rules/first_death_rules.yaml
rules/role_rules.yaml
```

---

## 18. Rule Engine

Insights baseados em regras devem ser separados da implementação das métricas.

Exemplo conceitual:

```text
Metric Engine
      ↓
Feature Store
      ↓
Rule Engine
      ↓
Insight
```

Uma regra deve utilizar evidências mensuráveis.

Evitar regras puramente subjetivas.

---

## 19. Evidências

Todo insight deve, quando possível, carregar sua evidência.

Exemplo:

```python
Insight(
    title="High First Death Rate",
    confidence=0.81,
    evidence={
        "fd_rate": 0.19,
        "baseline": 0.13,
        "trade_rate": 0.72,
    },
)
```

O sistema deve permitir responder:

```text
What happened?
Why was this detected?
Which metrics support it?
How confident are we?
```

---

## 20. Performance e legibilidade

Priorizar código:

* simples;
* legível;
* testável;
* modular.

Não otimizar prematuramente.

Entretanto, evitar loops desnecessários sobre grandes DataFrames quando operações vetorizadas do Pandas/Polars forem apropriadas.

---

## 21. Dependências

Antes de adicionar uma biblioteca, verificar se a funcionalidade pode ser implementada adequadamente com as dependências existentes.

Não adicionar dependências apenas por conveniência.

Documentar novas dependências no `pyproject.toml`.

---

## 22. Alterações no projeto

Antes de implementar uma mudança estrutural:

1. entender o código existente;
2. identificar dependências;
3. preservar funcionalidades existentes;
4. propor a mudança;
5. implementar incrementalmente.

Não reescrever grandes partes do projeto sem necessidade.

---

## 23. Abordagem científica

O projeto deve ser tratado como um sistema de análise quantitativa.

Quando uma hipótese for proposta:

```text
Observation
→ Evidence
→ Statistical Test / Rule
→ Confidence
→ Hypothesis
```

Não fazer o caminho:

```text
Observation
→ Guess
```

---

## 24. Quando os dados forem insuficientes

É aceitável concluir:

```text
Insufficient data
```

Uma conclusão incompleta porém correta é preferível a uma conclusão completa porém especulativa.

---

## 25. Prioridade das decisões

Ao tomar decisões de implementação, seguir esta ordem:

1. Correção dos dados;
2. Correção matemática;
3. Validade estatística;
4. Reprodutibilidade;
5. Testabilidade;
6. Clareza arquitetural;
7. Performance;
8. Conveniência.

---

## 26. Regra para novas funcionalidades

Antes de criar uma nova métrica ou algoritmo, responder:

1. Qual pergunta ele responde?
2. Quais dados são necessários?
3. Esses dados existem?
4. Qual é a definição matemática?
5. Qual é a hipótese?
6. Qual é a limitação?
7. Como será testado?
8. Como será interpretado?

Se essas perguntas não puderem ser respondidas, não implementar a funcionalidade prematuramente.

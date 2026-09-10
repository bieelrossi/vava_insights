# Análise de Performance — harkonnen #IDV

**Fonte:** `player-harkonnen.zip` (Tracker) — overview do ato V26: A5 + 20 partidas detalhadas + all-time (agents, maps, weapons, loadouts, roles, performance por ato, `dataAlltime.txt`).
**Data da análise:** 03/09/2026
**Rating atual:** Platinum 3 · **Pico:** Diamond 2 (V26: Act III)

---

## ⚠️ Nota preliminar sobre o arquivo

O prompt indica **"Jogador: Liimabro"**, mas o `.zip` enviado contém o tracker de **harkonnen #IDV**. Liimabro aparece apenas como teammate em 8 das 20 partidas do ato. **Esta análise é sobre harkonnen** — se a intenção era analisar Liimabro, o export está trocado.

---

## 1. Definição da Amostra e Isolamento de Outliers

**Volume total:** 1.703 partidas / 35.645 rounds / 1.019h (all-time) + 21 partidas do ato vigente (V26: A5), das quais 20 vieram com scoreboard detalhado.

**Limiar aplicado:** com 1.703 partidas, uso o piso da regra (5% ≈ **85 partidas**). Abaixo disso, o agente sai da análise principal — 85 partidas ainda é amostra sólida, então não há razão para exigir mais.

### Agent pool base (7 agentes · 1.163 partidas = 68,3% da amostra)

| Agente | Partidas | % amostra | WR | K/D | ADR | ACS | DDΔ | HS% |
|---|---|---|---|---|---|---|---|---|
| Omen | 314 | 18,4% | 51,6% | 1.09 | 146,1 | 225,7 | +11 | 25,8% |
| Cypher | 209 | 12,3% | 52,6% | 1.15 | 146,6 | 222,3 | +19 | 26,1% |
| Breach | 154 | 9,0% | 51,3% | 0.99 | 136,7 | 208,9 | +1 | 20,6% |
| Reyna | 127 | 7,5% | 52,8% | 1.07 | 156,8 | 240,4 | +8 | 24,2% |
| Clove | 126 | 7,4% | 50,8% | 0.97 | 157,3 | 239,2 | −1 | 24,4% |
| Gekko | 120 | 7,0% | 53,3% | 0.98 | 127,8 | 194,4 | −5 | 20,8% |
| Phoenix | 113 | 6,6% | 47,8% | 1.16 | 170,8 | 260,6 | +9 | 26,4% |

### Isolados → ver "Observações Marginais" (seção 8)

Yoru (76), Astra (72), Jett (57), Sage (42), KAY/O (38), Fade (29), Harbor (28), Vyse (27), Chamber (27), Raze (25), Sova (24), Waylay (17), Viper (16), Iso (14).

### Mapas — nenhum excluído

Pool vigente confirmado pelas 20 partidas do ato: Abyss, Ascent, Haven, Lotus, Split, Summit, Sunset.

| Mapa | Partidas | WR | K/D | ADR | ACS | DDΔ | Sinalização |
|---|---|---|---|---|---|---|---|
| Summit | 14 | 57,1% | 1.29 | 172,1 | 267,6 | +29 | 🔴 **amostra baixa** — não conclusivo |
| Sunset | 163 | 53,7% | 1.01 | 146,5 | 221,5 | +5 | — |
| Abyss | 128 | 52,7% | 1.09 | 146,3 | 223,4 | +13 | — |
| Lotus | 188 | 51,1% | 1.03 | 143,1 | 218,4 | +5 | — |
| Split | 179 | 50,6% | 1.08 | 149,4 | 227,9 | +9 | — |
| Haven | 205 | 48,8% | 1.09 | 152,5 | 232,6 | +14 | ⚠️ stats boas, WR ruim |
| Ascent | 186 | 48,4% | 0.98 | 137,4 | 210,5 | −3 | ⚠️ pior mapa real do pool |

Fora do pool (só referência): Corrode 68,7% (67), Fracture 50,9% (56), Pearl 50,0% (109), Icebox 46,2% (91), Bind 43,5% (198), Breeze 40,2% (101).

---

## 2. Diagnóstico Executivo de Impacto

### 2.1 K/D reflete impacto real?

| | K/D | ACS | ADR | KAST | DDΔ/round | WR |
|---|---|---|---|---|---|---|
| All-time (1.703) | 1.05 | 222,3 | 145,7 | 70,3% | +7 | 49,7% |
| Ato V26:A5 (21) | 1.21 | 263,3 *(top 9%)* | 168,8 *(top 11%)* | 74,3% *(top 15%)* | +23 *(top 14%)* | **52,4%** |

O ato atual é um salto violento: **+18,5% em ACS, +15,9% em ADR, DDΔ/round 3,3× maior**. E isso converteu em apenas **+2,7 pontos percentuais de winrate**. Esse é o eixo central do diagnóstico.

Duas hipóteses coexistem e os dados não permitem escolher só uma:

1. **Melhora mecânica real** — HS% subiu de 12–16% (E7) → 21–24% (E9) → 26–32% (2025/26). É uma curva de 4 anos, não ruído.
2. **Efeito de lobby** — o rating caiu de Diamond 1/2 (V26 A1–A4) para Platinum 3 no ato atual. As 20 partidas rodam em lobbies Platinum II/III. Parte do ganho de ACS pode ser adversário mais fraco, não jogador melhor.

**Contra-exemplo mais forte contra "K/D = impacto":** o melhor ato da carreira em winrate foi **E8:A3 — 60,2% WR com K/D 0.98 e HS 19,7%**. O pior ano (2026: ~413 partidas, 45,8%) aconteceu com o pico de rating (Diamond 2) e o melhor K/D do histórico (1.17 no V26:A3).

### 2.2 FK vs FD — e em que lado do jogo

| | Rounds | FB | FD | FK/FD | Round Win % | DDΔ/rd | Sobrevivência |
|---|---|---|---|---|---|---|---|
| **Ataque** | 17.663 | 1.772 (0,100/rd) | 1.915 (0,108/rd) | **0.93** | 49,7% | +4 | 25,4% |
| **Defesa** *(derivado)* | 17.982 | 2.047 (0,114/rd) | 1.930 (0,107/rd) | **1.06** | 50,7% | +9,9 | 28,5% |
| **Total** | 35.645 | 3.819 | 3.845 | 0.99 | 50,2% | +7 | 26,9% |

> *Os números de defesa foram derivados por subtração (Combat − Attack), já que o `dataAlltime.txt` termina na seção Attack.*

**O desequilíbrio ataque/defesa é o achado mais limpo do all-time.** No ataque ele perde o primeiro duelo com mais frequência do que ganha (0.93) e gera menos da metade do damage delta que gera na defesa. Não é "entregar first blood à toa" — 0.93 é quase neutro — mas é **entrada de ataque sem vantagem numérica gerada**, sustentada por 17.663 rounds. Amostra grande demais para ser acaso.

No ato atual o FK/FD subiu para **1.02** (58 FK / 57 FD em 454 rounds), com volume de aberturas 20% acima do histórico (0,128 FK/round vs 0,107). Sinal positivo real.

### 2.3 As vitórias/derrotas de round passam por ele?

Split vitória vs derrota nas 20 partidas do ato:

| | ACS | K/D | KAST | DDΔ/partida | FK/FD |
|---|---|---|---|---|---|
| Vitórias (10) | 288,0 | 1.42 | **79,3%** | +45 | 29/29 = 1.00 |
| Derrotas (10) | 236,8 | 1.00 | **68,3%** | −2,1 | 29/28 = 1.04 |

**O FK/FD é idêntico (até levemente melhor) nas derrotas.** O que colapsa é o KAST (−11 pontos) e o K/D. **Não é a abertura do round que decide — é o que acontece depois dela.**

Confirmação estrutural no all-time:

- Rounds com pelo menos 1 kill: **50,1%** (17.857 de 35.645). Em metade dos rounds ele não mata ninguém.
- Rounds sobrevividos: **26,9%** — baixo. Morre em 73,1% dos rounds.
- Posição da morte no round: 14,6% first death · 12,7% last death → **72,7% das mortes são de meio de round.**
- Rounds traded: 4.648 = **17,6% das mortes dele são vingadas** (abaixo do saudável ~20–25%).

### 2.4 Clutches

| Situação | Ganhos | Perdidos | Taxa |
|---|---|---|---|
| 1v1 | 347 | 214 | **61,9%** |
| 1v2 | 199 | 675 | 22,8% |
| 1v3 | 51 | 947 | 5,1% |
| 1v4 | 10 | 881 | 1,1% |
| 1v5 | 3 | 512 | 0,6% |
| **Total** | **613** | **3.229** | 16,0% |

**61,9% em 1v1 é excelente** — em duelo isolado e justo ele ganha. E **60,9% de todas as situações de clutch dele são 1v3 ou pior** (2.340 de 3.842). Isso não é falha individual: é assinatura de colapso de time. Ele fica sozinho contra 3+ em 6,6% de todos os rounds da carreira.

### Maiores Gargalos (Impacto)

1. **Ataque estruturalmente pior que defesa** — FK/FD 0.93 vs 1.06, DDΔ/rd +4 vs +9,9, sobre ~17.700 rounds cada lado.
2. **Presença de meio de round** — só 50,1% dos rounds com ≥1 kill, 72,7% das mortes no miolo, 17,6% de taxa de troca.
3. **Volume de participação em rounds já perdidos** — 2.340 clutches em 1v3+ com média de 3,3% de conversão.

### Maiores Pontos Fortes (Impacto)

1. **Duelo isolado** — 61,9% em 1v1, bem acima do rank.
2. **Tendência recente genuína** — DDΔ/round +7 → +23, KAST 70,3% → 74,3%, FK/FD 0.99 → 1.02, com volume de abertura +20%.
3. **Defesa sólida** — 50,7% de round win, +9,9 DDΔ/round, 28,5% de sobrevivência.

---

## 3. Agent Pool

### 3.1 Eficiência do pool base — e o conflito central

O pool base é **anormalmente amplo e anormalmente plano**: sete agentes entre 6,6% e 18,4% da amostra, cobrindo as quatro roles. Isso não é um pool — é um catálogo.

**O conflito grave:** o agente com os melhores números individuais é o com o pior winrate.

- **Phoenix** — ADR 170,8 (o mais alto do pool, +17% acima da média dele), ACS 260,6, K/D 1.16 → **WR 47,8%**, o pior do pool base.
- **Gekko** — ADR 127,8 (o mais baixo), K/D 0.98, DDΔ −5 → **WR 53,3%**, o melhor do pool base.

Nos 7 agentes core (1.163 partidas), a correlação entre ADR no agente e winrate no agente é **r ≈ −0,73**. Quanto mais dano ele faz, menos o time ganha.

> **Ressalva honesta:** n = 7 agentes, e a role é um confundidor óbvio (os agentes de ADR alto são duelistas/Clove; os de ADR baixo são iniciadores/sentinelas). Não trato isso como causalidade. Mas o caso Phoenix isolado é limpo o suficiente para levar a sério.

**Phoenix — evidência acumulada (121 partidas):**

| | Partidas | ADR | K/D | ACS | DDΔ | WR |
|---|---|---|---|---|---|---|
| All-time | 113 | 170,8 | 1.16 | 260,6 | +9 | 47,8% |
| Ato V26:A5 | 8 | 171,2 | 1.18 | 263,8 | +14 | **37,5% (3W-5L)** |

- Nas **5 derrotas** de Phoenix do ato: **FK 20 / FD 16** — ganhou a batalha de aberturas e perdeu as partidas.
- Nas **3 vitórias** de Phoenix do ato: **FK 9 / FD 12** — perdeu aberturas e venceu.

Duas leituras plausíveis, sem dados para separá-las: (a) o Phoenix dele gera dano em situações que não convertem em round; (b) quando ele pega Phoenix, o time está mal composto e ele está cobrindo um buraco de entry. Não dá para decidir com o que foi enviado.

### 3.2 Impacto de nerfs/buffs e agentes recentes

- **Yoru (76 partidas, 4,5%)** — 55,3% WR, K/D 1.07, **HS 29,1%** (3º mais alto do pool inteiro), DDΔ +11. No ato: **3 partidas, 3-0, ACS 317, K/D 1.48, DDΔ +64**. Amostra curta com tendência de crescimento clara → isolado pela regra, mas **não descartado**. Candidato mais forte a promoção.
- **Chamber (27)** — K/D 1.17 e DDΔ **+26** (o melhor do dataset inteiro), HS 32,2% (o mais alto)... e **29,6% de WR**. O problema aqui parece ser de arsenal, não de patch (ver §6).
- **Agentes recentes** — Vyse (27, K/D 1.13, DDΔ +17) promissor; Waylay (17, K/D 0.85, DDΔ −15) não.

### 3.3 Perfil: especializado ou flex?

**Flex extremo — e é isso que precisa ser discutido.**

| Role | Partidas | % | WR | K/D | KDA | Kills/partida | Deaths/partida |
|---|---|---|---|---|---|---|---|
| Controller | 564 | 33,1% | 49,4% | 1.045 | 1.44 | 16,65 | 15,92 |
| Duelist | 428 | 25,1% | 49,1% | 1.062 | 1.34 | 17,27 | 16,26 |
| Initiator | 379 | 22,3% | 49,6% | 0.960 | 1.35 | 14,78 | 15,38 |
| **Sentinel** | **314** | **18,4%** | **51,1%** | **1.125** | **1.44** | 16,59 | **14,74** |

Os winrates são planos (49,1%–51,1%), mas a **eficiência não é**: como Sentinel ele morre 1,5 vez menos por partida que como Duelist e ainda mata quase o mesmo. É o melhor K/D, o melhor WR e o menos jogado. Cypher, o 2º agente mais jogado da carreira (209 partidas), tem o 2º melhor DDΔ (+19) e o 2º melhor WR (52,6%) do pool base.

**E no ato atual ele zerou Sentinel** (0 de 21 partidas) e foi 52% Duelist.

### Maiores Gargalos (Agent Pool)

1. **Phoenix é uma armadilha estatística** — 121 partidas de ADR de elite com o pior winrate do pool.
2. **Iniciador é a role fraca real** — K/D 0.960 em 379 partidas (Sova 0.79/−11, KAY/O 0.88/−8, Gekko 0.98/−5, Breach 0.99/+1). Não é amostra pequena, é padrão.
3. **Dispersão sem especialização** — 21+ agentes com uso relevante e nenhum acima de 18,4% da amostra.

### Maiores Pontos Fortes (Agent Pool)

1. **Sentinel é a role mais eficiente e está subutilizada** — K/D 1.125, WR 51,1%, menor taxa de morte.
2. **Yoru em ascensão** — 55,3% WR all-time, 3-0 no ato com ACS 317 e HS 29,1%.
3. **Omen como base confiável** — 314 partidas, 51,6% WR, 4-1 no ato (80%).

---

## 4. Análise de Role

### 4.1 Os números de duelo fazem sentido para a função?

**Comportamento observado (all-time):**

- Deaths/round 0,74 e sobrevivência 26,9% → perfil **exposto e agressivo**
- FD/round 0,108 → volume de first death de duelista
- FB = 13,8% dos kills totais, mas presentes em só 10,7% dos rounds
- 72,7% das mortes no meio do round
- **Utilitária: 2,45 casts/round** (A1 0,6 + A2 1,2 + granada 0,6) + 2,57 ults/partida

**A incoerência mais importante do dataset:** ele joga Controller/Initiator/Sentinel em **73,8% das partidas** e usa **2,45 utilitárias por round**. Um Controller sozinho já deveria estar próximo de 3,5–4,5. Ele está pegando agentes de utilitária e jogando-os com o rifle.

Isso reconcilia tudo: taxa de morte alta, sobrevivência baixa, 1v1 de 61,9%, dano acima da média nos agentes de utilitária (Clove 157,3 · Phoenix 170,8), KAST de meio de round colapsando nas derrotas, e o fato de a role mais eficiente ser justamente a que **permite** essa agressividade sem custo estrutural (Sentinel).

**Os dados sugerem outra role? Sim.** O comportamento em campo é de **fragger agressivo de meio de round**, não de suporte. E o Initiator — a role que mais exige subordinar o próprio duelo ao do time — é exatamente a de pior K/D (0.960).

### 4.2 Consistência dentro da mesma role

- **Duelista (varia muito):** Yoru 55,3% · Reyna 52,8% · Phoenix 47,8% · Raze 44,0% · Waylay 41,2% · **Jett 36,8%**. Amplitude de **18,5 pontos** de WR na mesma role. Jett (57 partidas, K/D 0.96, DDΔ −2) é o pior agente com amostra relevante da carreira.
- **Controller (consistente):** Omen 51,6% · Clove 50,8% · Astra 44,4% · Harbor 42,9% (K/D 0.83, DDΔ −16).
- **Sentinel (consistente e bom):** Cypher 52,6% · Sage 59,5% · Vyse 48,1%. Chamber 29,6% é a exceção.
- **Initiator (consistentemente fraco):** só Gekko 53,3% acima da linha; Breach 51,3%, Fade 51,7%, KAY/O 42,1%, Sova 41,7%.

### 4.3 Timing das mortes e abates ao longo do round

| Fase | Métrica |
|---|---|
| Início | FB em 10,7% dos rounds · FD em 10,8% |
| Meio | **72,7% das mortes** |
| Fim | 26,9% de sobrevivência · 9,4% dos rounds como last death · 10,8% dos rounds em clutch |

**Isso é compatível com Controller e Sentinel. Não é compatível com Duelista.** Um duelista deveria ter FB muito acima de 13,8% dos kills e morte concentrada no início.

**No ato atual isso mudou — para melhor.** Como Duelista: **0,148 FK/round** (vs 0,101 como Controller e 0,101 como Initiator), FK/FD 1,12, K/D 1.25. É a mudança de comportamento mais saudável do ato.

### Maiores Gargalos (Role)

1. **Uso de utilitária incompatível com as roles jogadas** — 2,45 casts/round com 73,8% das partidas em roles de utilitária.
2. **Iniciador é role de má aderência** — K/D 0.960 em 379 partidas; no ato: 0W-3L, K/D 0.85 (47K/55D).
3. **Mortes concentradas no meio do round (72,7%) com taxa de troca de 17,6%.**

### Maiores Pontos Fortes (Role)

1. **Sentinel é a role de melhor aderência** — melhor K/D, melhor WR, menor deaths/partida.
2. **Correção de padrão em curso** — FK/round como duelista +46% vs outras roles no ato.
3. **Aim de duelo elite para o rank** — 61,9% em 1v1, HS 33% com Vandal.

---

## 5. Análise de Composição vs. Teammates

> **Limite honesto:** o export não traz os agentes dos 4 teammates nem dos 5 adversários de forma agregada. Boa parte desta seção fica em hipótese explícita.

### 5.1 Contexto de composição

Em **todas as 20 partidas** do ato ele jogou com pelo menos 3 membros fixos do roster Premier (Inimigosvitoria). Não é solo queue — as composições são internas e escolhidas em grupo.

**Ranks:** teammates fixos em Diamond 1 (Lvismara, RyanKanne, liimabro) e Gold 3 (Xuxu); ele Platinum 3. Lobbies em média Platinum II/III. **Ele não está enfrentando lobbies acima do MMR dele** — se algo, está jogando abaixo. Isso enfraquece explicações de "queda por adversário forte" e reforça a hipótese de inflação do ACS do ato.

### 5.2 Existem teammates que o potencializam?

| Teammate | Partidas juntos | W-L | WR |
|---|---|---|---|
| Ferri | 20 | 10-10 | 50,0% |
| RyanKanne | 19 | 10-9 | 52,6% |
| Lvismara | 14 | 7-7 | 50,0% |
| Xuxu | 10 | 5-5 | 50,0% |
| liimabro | 8 | 4-4 | 50,0% |
| MrSalsz | 5 | 2-3 | 40,0% |

**Não há sinal nesta amostra.** Tudo colado em 50%, com amostras de 5 a 20 partidas — nenhuma dessas diferenças é distinguível de ruído. **Declaro o fato puro: não há embasamento para apontar sinergia ou anti-sinergia com nenhum teammate específico com os dados enviados.**

### 5.3 Os melhores números aparecem em composições diferentes?

| Agente no ato | Partidas | W-L | ACS | K/D | FK/FD |
|---|---|---|---|---|---|
| Yoru | 3 | **3-0** | 317 | 1.48 | 9/6 |
| Omen | 5 | **4-1** | 267,2 | 1.34 | 11/13 |
| Phoenix | 8 | **3-5** | 267,5 | 1.18 | 29/28 |
| Breach | 2 | 0-2 | 165 | 0.66 | 4/6 |
| Skye | 1 | 0-1 | 252 | 1.20 | 3/2 |
| Clove | 1 | 0-1 | 239 | 1.00 | 2/2 |

Omen e Phoenix têm **ACS praticamente idêntico** (267,2 vs 267,5) e winrates de 80% e 37,5%. Mesma performance individual, resultado oposto. Como as composições foram escolhidas pelo mesmo grupo de 5, a variável não é o adversário — é **o encaixe do que ele pega no resto do time**.

### 5.4 Ele é carregado, carrega, ou o resultado é independente?

Nas 20 partidas do ato há forte correlação (vitórias com ACS 288 e KAST 79,3%; derrotas com 237 e 68,3%). **Mas isso não se sustenta no histórico:**

| Período | Partidas (est.) | WR | K/D típico |
|---|---|---|---|
| Episode 9 | ~361 | 49,3% | 0.99–1.06 |
| Season 2025 | ~564 | **51,6%** | 1.07–1.15 |
| Season 2026 | ~413 | **45,8%** | 1.04–1.21 |
| **E8:A3 (melhor ato)** | ~108 | **60,2%** | **0.98** |

**Veredito: nos últimos ~1.700 jogos o resultado é largamente independente da performance individual dele.** O K/D oscilou de 0.84 a 1.21 ao longo dos episódios e o winrate ficou preso na faixa 46–52%. Ele não é carregado nem carrega — é uma constante de ~50% cujo desempenho individual varia em torno dela sem mover o ponteiro.

Isso torna as perguntas de composição e utilitária **mais** importantes, não menos: se o fragging não move o resultado, o que move está no espaço que ele não está usando.

### 5.5 Quando joga fora da role principal, os números caem proporcionalmente?

Ele não tem "role principal" — tem distribuição 33/25/22/18%. Mas pela role de menor conforto:

- **Initiator (379 partidas):** kills/partida 14,78 vs 17,27 como Duelist (**−14,4%**), com deaths/partida quase iguais (15,38 vs 16,26). **A queda é desproporcional** — perde impacto ofensivo sem ganhar sobrevivência.
- **Sentinel (314 partidas):** kills/partida 16,59 (−4% vs Duelist) com deaths/partida 14,74 (**−9,4%**). **Adaptação boa** — cede pouco frag e ganha muito em sobrevivência.

### Maiores Gargalos (Composição)

1. **Resultado desacoplado da performance individual** — 4 anos, ~1.700 partidas, K/D 0.84→1.21, WR preso em 46–52%.
2. **Adaptação ruim ao Initiator** — −14,4% de kills sem ganho de sobrevivência.
3. **Sem dados de composição no export** — impossível testar as hipóteses mais interessantes. Lacuna de dados, não falha dele.

### Maiores Pontos Fortes (Composição)

1. **Time fixo e estável** — 5-stack Premier em todas as 20 partidas: a variável é controlável.
2. **Adaptação boa ao Sentinel** — cede 4% de frag por 9,4% menos mortes.
3. **Omen como âncora do grupo** — 4-1 no ato, 51,6% em 314 partidas.

---

## 6. Análise de Arsenal e Economia

### 6.1 Armas mais utilizadas

| Arma | Kills | % do total | Dano/partida | HS% |
|---|---|---|---|---|
| Vandal | 10.613 | 38,5% | 1.039,0 | 33% |
| Phantom | 8.404 | 30,5% | 932,4 | 32% |
| Bulldog | 1.976 *(746 alt)* | 7,2% | 213,5 | 28% |
| Ghost | 1.904 | 6,9% | 136,1 | — |
| Spectre | 1.255 | 4,5% | 141,6 | — |
| Classic | 1.241 | 4,5% | 90,9 | — |
| Sheriff | 908 | 3,3% | 97,7 | — |

**Rifles = 68,9% dos kills · Snipers = 143 kills (0,5%) · Shotguns = 138 (0,5%).**

O arsenal está **coerente com o comportamento**: engajamento de média distância, duelo direto, agressividade de meio de round. Vandal com 33% de HS é número forte.

**Onde não está coerente: Chamber.** 27 partidas, o melhor DDΔ do dataset (+26), o melhor HS% (32,2%) — e **29,6% de WR**. Ele tem 53 kills de Operator e 38 de Tour de Force em 1.703 partidas. **Ele joga Chamber com rifle.** O valor do Chamber é o Operator gratuito e o reposicionamento; jogá-lo de Vandal é gastar o pick e ficar com um Sentinel de utilitária inferior. Isso explica o paradoxo "stats de elite, WR de desastre" melhor que qualquer hipótese de composição.

### 6.2 Sobreposição de arsenal e cobertura

**Não há overlap de arsenal no time** — ninguém no roster aparece como jogador de Operator, e ele tem 0,5% dos kills em snipers. O time inteiro parece ser de rifle.

Isso abre uma lacuna estrutural: em mapas de linha longa do pool vigente (**Abyss, Ascent, Haven, Split mid**) não há ninguém segurando ângulo longo com Operator. **Ascent** (48,4% WR, K/D 0.98, DDΔ −3, 186 partidas) é o pior mapa real do pool e é exatamente o mais dependente de controle de mid a longa distância.

Ele **não** é o jogador para preencher isso (0,5% em sniper é uma escolha, não acidente). Mas é pergunta legítima para o grupo: **alguém cobre?**

### 6.3 Performance por tipo de economia

| Loadout | K/D | ADR | ACS | DDΔ | KAST | ESR | % dos kills | % das mortes |
|---|---|---|---|---|---|---|---|---|
| **Full** (≥$3900) | **1.18** | **166,0** | 246,1 | **+19** | **73,3%** | **55,0%** | 45,1% | 39,8% |
| Semi ($1000–3900) | 1.06 | 140,6 | 218,5 | +2 | 71,0% | 49,1% | 28,4% | 27,9% |
| Pistol | 1.02 | 112,3 | 197,5 | +6 | 72,2% | 49,6% | 9,3% | 9,5% |
| **Eco** ($0–1000) | **0.79** | 128,1 | 192,6 | **−10** | **64,0%** | **40,6%** | 17,3% | **22,7%** |

**Onde ele é melhor: full buy, sem ambiguidade.** K/D 1.18, ESR 55%, DDΔ +19.

**Onde ele sangra: eco.** ESR 40,6% (−14,4 pontos vs full), K/D 0.79, DDΔ −10, KAST 64%. Gera **22,7% de todas as mortes contra 17,3% dos kills** — a única categoria com déficit estrutural.

Nuance: **ADR 128,1 no eco é alto** para round de save. Ele faz dano em eco, mas morre demais. Perfil de quem **força** o eco em vez de save-lo — coerente com todo o resto do diagnóstico.

### 6.4 Erros econômicos

O erro mais claro **não é de compra, é de escolha de arma dentro do eco.** Distribuição de pistolas: Ghost 1.904 · Classic 1.241 · **Sheriff apenas 908**. Bucky 62, Judge 49, Shorty 27 — praticamente zero shotgun.

Com 61,9% de WR em 1v1 e 33% de HS com Vandal, ele tem exatamente o perfil mecânico que o **Sheriff** premia — one-tap de longa distância em round de desvantagem. Está usando Ghost/Classic (armas de trade e spray) num round onde precisa do dano por bala. **Não é erro de crédito; é erro de ferramenta.**

**Econ Rating: 58 por partida** — dano por crédito gasto na faixa média-baixa. Consistente com ADR alto em eco (gasta pouco, faz dano) mas ESR baixo (esse dano não vira round).

### 6.5 Rounds pistol

**All-time (~3.400 rounds pistol):** K/D 1.02, ADR 112,3, KAST 72,2%, ESR 49,6%. Kills/round 0,76 e deaths/round 0,74 — **espelho exato da média geral dele.**

**Diagnóstico: o pistol é perfeitamente neutro.** Não é força nem fraqueza. Ele nem ganha nem perde jogo no pistol.

**Ato atual:** vencedores do round 1 nas 20 partidas — **8 vitórias em 20 (40%)**. Amostra pequena (20 rounds), consistente com coinflip levemente negativo. Não trato como tendência. *(O round 13 não foi contabilizado — não estava visível no recorte das capturas.)*

**A consequência é onde dói:** pistol neutro (49,6%) → metade dos jogos entra em bônus/eco → **ESR de eco 40,6%** com DDΔ −10. **O problema não é o pistol. É que perder o pistol o joga na única categoria econômica onde ele é claramente negativo.**

### Maiores Gargalos (Arsenal e Economia)

1. **Eco é o buraco econômico** — ESR 40,6%, K/D 0.79, DDΔ −10, 22,7% das mortes por 17,3% dos kills.
2. **Chamber jogado sem Operator** — 53 kills de Op em 1.703 partidas, melhor DDΔ do dataset e 29,6% de WR.
3. **Sub-uso do Sheriff em eco** — 908 kills contra 1.904 de Ghost e 1.241 de Classic, com perfil mecânico que pede o one-tap.

### Maiores Pontos Fortes (Arsenal e Economia)

1. **Full buy é claramente positivo** — K/D 1.18, ADR 166,0, ESR 55,0%, DDΔ +19.
2. **Consistência Vandal/Phantom** — 68,9% dos kills, HS 33%/32%, sem dependência de arma específica.
3. **Bulldog é escolha correta de semi-buy** — 1.976 kills (746 no modo alternativo) sustentando K/D 1.06 e ADR 140,6 no force.

---

## 7. Resumo

### 7.1 Pontos que deve manter

- **A mudança de comportamento do ato atual.** DDΔ/round +7 → +23, KAST 70,3% → 74,3%, FK/FD 0.99 → 1.02, volume de abertura +20%. Melhor tendência dos últimos 4 anos e ela é real.
- **A agressividade como duelista.** 0,148 FK/round quando pega Duelista (vs 0,101 nas outras roles).
- **Omen e Cypher como base.** 523 partidas somadas, 51,6% e 52,6% de WR, DDΔ +11 e +19.
- **A curva mecânica.** HS% de 12–16% (E7) para 26–32% (2025/26).

### 7.2 Pontos que deve eliminar ou melhorar

- **Phoenix.** 121 partidas com o melhor ADR do pool e o pior winrate. Nas 5 derrotas do ato ganhou o duelo de abertura 20-16 e perdeu mesmo assim.
- **A utilitária.** 2,45 casts/round com 73,8% das partidas em Controller/Initiator/Sentinel. Número mais desalinhado do relatório e raiz de metade dos outros problemas.
- **O ataque.** FK/FD 0.93 e DDΔ/round +4 contra 1.06 e +9,9 na defesa, sobre 17.663 rounds.
- **O eco.** ESR 40,6%, 22,7% das mortes por 17,3% dos kills, DDΔ −10.
- **Initiator.** K/D 0.960 em 379 partidas. Role de pior aderência ao estilo dele.
- **Chamber com rifle.** Ou joga com Operator, ou não joga Chamber.

### 7.3 Dicas práticas para os cenários em que costuma jogar

1. **Reabra o Sentinel.** Melhor K/D (1.125), melhor WR (51,1%), menor taxa de morte (14,74/partida) — e **0 de 21 partidas no ato**. Cypher especificamente: 209 partidas, DDΔ +19, 52,6% WR. É a role que absorve sua agressividade sem cobrar o preço estrutural.
2. **Promova Yoru sobre Phoenix como pick de duelista.** Yoru 55,3% all-time / 3-0 no ato / ACS 317 / HS 29,1%. Phoenix 47,8% / 37,5%. Mesma role, 18 pontos de diferença.
3. **Meça utilitária por round, não frags.** Você está em 2,45 casts/round. Como Controller ou Sentinel, vá para 3,5+. É a métrica de treino mais provável de mover o winrate — é a única grande alavanca que você ainda não puxou.
4. **Trate o lado de ataque como projeto separado.** Toda a diferença estrutural do seu jogo está lá (FK/FD 0.93 vs 1.06). Reveja timing de entrada e utilitária de execute — não mira.
5. **Sheriff em eco, Ghost em light buy.** Você tem o perfil de one-tap (61,9% em 1v1, 33% HS com Vandal) e está usando a arma errada no round onde o dano por bala importa mais.
6. **Não force clutch em 1v3+.** São 2.340 dessas situações e você ganha 3,3%. Mas ganha 61,9% dos 1v1. Preserve posição para chegar em 1v1 e 1v2 (22,8%), não para heroísmo em 1v4.
7. **Nos mapas do pool:** Ascent (48,4%, K/D 0.98, DDΔ −3, 186 partidas) é o mapa fraco real. Haven (48,8% com K/D 1.09, ADR 152,5, DDΔ +14, 205 partidas) é o caso puro de stats sem vitória — revise comp e defaults nele com o time. Summit (57,1%) tem só 14 partidas: **não tire conclusão dele ainda.**

### 7.4 Diagnóstico geral em uma frase

> **Ao longo de 1.703 partidas o desempenho individual dele melhorou consistentemente sem mover o winrate — e a explicação mais provável é que ele vem jogando roles de utilitária com padrão de fragger (2,45 casts/round em 73,8% de partidas de suporte), gerando dano que não vira round, sendo o Phoenix (121 partidas, ADR de elite, pior WR do pool) o retrato exato desse problema e o Sentinel (melhor K/D, melhor WR, menos jogado, zerado no ato atual) a correção mais óbvia e mais ignorada.**

---

## 8. Observações Marginais (agentes isolados pela Regra de Ouro 1)

Isolados da análise principal por representarem menos de 5% da amostra, mas **não descartados**:

| Agente | Partidas | % | WR | K/D | ADR | DDΔ | HS% | Leitura |
|---|---|---|---|---|---|---|---|---|
| **Yoru** | 76 | 4,5% | **55,3%** | 1.07 | 152,9 | +11 | **29,1%** | 🔼 **Tendência de crescimento** — 3-0 no ato, ACS 317, DDΔ +64. Candidato a promoção ao pool base. |
| Astra | 72 | 4,2% | 44,4% | 1.11 | 142,6 | +16 | 28,4% | Stats individuais boas, WR ruim. Padrão "Phoenix" em escala menor. |
| **Jett** | 57 | 3,3% | **36,8%** | 0.96 | 144,2 | −2 | 23,6% | 🔽 Pior agente com amostra relevante da carreira. Já praticamente abandonado (0 no ato). |
| Sage | 42 | 2,5% | **59,5%** | 1.00 | 134,6 | +1 | 24,8% | Maior WR com amostra decente, com o ADR mais baixo do grupo. Reforça a tese central. |
| KAY/O | 38 | 2,2% | 42,1% | 0.88 | 129,8 | −8 | 14,5% | HS% de 14,5% destoa completamente. Descartar. |
| Fade | 29 | 1,7% | 51,7% | 1.02 | 135,8 | +5 | 23,6% | Melhor iniciador dele por K/D. Vale mais amostra. |
| Harbor | 28 | 1,6% | 42,9% | 0.83 | 119,2 | **−16** | 20,9% | Pior DDΔ do dataset. Descartar. |
| **Vyse** | 27 | 1,6% | 48,1% | 1.13 | 147,5 | +17 | 29,5% | Agente recente, números fortes. Vale exploração como Sentinel alternativo. |
| **Chamber** | 27 | 1,6% | **29,6%** | **1.17** | 157,2 | **+26** | **32,2%** | ⚠️ Melhor DDΔ e melhor HS% do dataset com o pior WR. Causa provável: jogado sem Operator (§6.1). |
| Raze | 25 | 1,5% | 44,0% | 0.97 | 154,4 | +16 | 22,7% | Padrão "dano alto, WR baixo" novamente. |
| Sova | 24 | 1,4% | 41,7% | 0.79 | 120,8 | −11 | 19,1% | Pior K/D do dataset. Descartar. |
| Waylay | 17 | 1,0% | 41,2% | 0.85 | 127,0 | −15 | 30,5% | Agente recente, sem retorno. |
| Viper | 16 | 0,9% | 43,8% | 0.99 | 146,0 | +12 | 25,7% | Amostra insuficiente. |
| Iso | 14 | 0,8% | **64,3%** | 1.05 | 160,1 | +17 | 27,7% | 🔴 Maior WR do dataset com a menor amostra. **Não tirar conclusão** — 14 partidas. |

**Padrão que atravessa a tabela:** os agentes de ADR mais alto (Chamber 157,2 · Raze 154,4 · Astra 142,6) têm WR de 29,6%, 44,0% e 44,4%. O agente de ADR mais baixo com amostra decente (Sage 134,6) tem 59,5%. Mesmo fora do pool base, a relação inversa entre dano dele e vitória do time se repete.

---

## Anexo — Log das 20 partidas do ato V26: A5

| # | Data | Mapa | Placar | Res. | Agente | ACS | K | D | A | K/D | DDΔ | ADR | HS% | KAST | FK | FD | MK | Rds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 02/09 | Sunset | 4-13 | L | Omen | 152 | 8 | 15 | 3 | 0.5 | −52 | 97,4 | 11% | 35% | 0 | 2 | 0 | 17 |
| 2 | 02/09 | Lotus | 13-7 | W | Omen | 200 | 13 | 14 | 6 | 0.9 | −3 | 125,2 | 36% | 70% | 2 | 1 | 1 | 20 |
| 3 | 31/08 | Summit | 14-12 | W | Yoru | 350 | 32 | 22 | 1 | 1.4 | +68 | 219,3 | 32% | 69% | 3 | 4 | 5 | 26 |
| 4 | 31/08 | Abyss | 13-10 | W | Phoenix | 273 | 22 | 15 | 6 | 1.5 | +62 | 182,9 | 27% | 83% | 5 | 0 | 0 | 23 |
| 5 | 31/08 | Lotus | 4-13 | L | Breach | 144 | 7 | 16 | 3 | 0.4 | −68 | 98,0 | 10% | 65% | 0 | 3 | 0 | 17 |
| 6 | 31/08 | Haven | 8-13 | L | Phoenix | 312 | 22 | 16 | 7 | 1.4 | +25 | 196,2 | 18% | 76% | 3 | 3 | 2 | 21 |
| 7 | 29/08 | Split | 12-14 | L | Skye | 252 | 24 | 20 | 9 | 1.2 | +21 | 157,2 | 21% | 69% | 3 | 2 | 2 | 26 |
| 8 | 29/08 | Ascent | 15-13 | W | Phoenix | 223 | 22 | 23 | 8 | 1.0 | −36 | 133,8 | 27% | 68% | 2 | 6 | 2 | 28 |
| 9 | 29/08 | Split | 13-6 | W | Omen | 366 | 24 | 14 | 12 | 1.7 | +89 | 235,6 | 34% | 95% | 3 | 2 | 4 | 19 |
| 10 | 29/08 | Sunset | 11-13 | L | Clove | 239 | 21 | 21 | 7 | 1.0 | −2 | 148,6 | 33% | 71% | 2 | 2 | 5 | 24 |
| 11 | 25/08 | Haven | 16-18 | L | Phoenix | 308 | 33 | 30 | 9 | 1.1 | +31 | 203,8 | 31% | 71% | 6 | 2 | 3 | 34 |
| 12 | 25/08 | Abyss | 13-10 | W | Omen | 325 | 27 | 15 | 6 | 1.8 | +79 | 206,3 | 28% | 78% | 3 | 4 | 3 | 23 |
| 13 | 24/08 | Sunset | 14-12 | W | Omen | 293 | 30 | 18 | 12 | 1.7 | +44 | 179,5 | 22% | 85% | 3 | 4 | 4 | 26 |
| 14 | 24/08 | Split | 12-14 | L | Breach | 186 | 16 | 19 | 13 | 0.8 | −5 | 126,8 | 26% | 65% | 4 | 3 | 0 | 26 |
| 15 | 24/08 | Lotus | 13-4 | W | Yoru | 278 | 16 | 13 | 4 | 1.2 | +44 | 180,8 | 26% | 88% | 2 | 0 | 1 | 17 |
| 16 | 21/08 | Sunset | 9-13 | L | Phoenix | 273 | 19 | 18 | 9 | 1.1 | +6 | 180,6 | 30% | 77% | 5 | 1 | 2 | 22 |
| 17 | 21/08 | Summit | 13-6 | W | Yoru | 323 | 23 | 13 | 1 | 1.8 | +76 | 193,5 | 30% | 89% | 4 | 2 | 2 | 19 |
| 18 | 21/08 | Haven | 9-13 | L | Phoenix | 236 | 18 | 16 | 4 | 1.1 | −7 | 152,4 | 20% | 68% | 4 | 3 | 1 | 22 |
| 19 | 18/08 | Ascent | 13-9 | W | Phoenix | 249 | 20 | 14 | 4 | 1.4 | +27 | 158,9 | 22% | 68% | 2 | 6 | 2 | 22 |
| 20 | 18/08 | Split | 9-13 | L | Phoenix | 266 | 20 | 17 | 9 | 1.2 | +30 | 183,8 | 39% | 86% | 2 | 7 | 0 | 22 |

**Totais (20 partidas / 454 rounds):** 10W-10L · 417K / 349D · FK 58 / FD 57 (1.02)
*(A 21ª partida do ato não veio com scoreboard; pelos totais do overview foi uma vitória de Controller com ~18K/10D.)*

**Mapas no ato:** Ascent 2-0 · Abyss 2-0 · Summit 2-0 · Lotus 2-1 · Sunset 1-3 · Split 1-3 · **Haven 0-3**

---

*Análise gerada a partir exclusivamente dos dados do export enviado. Onde os dados não permitiram conclusão única, mais de uma hipótese foi apresentada; onde não permitiram nenhuma, o fato foi declarado puro.*

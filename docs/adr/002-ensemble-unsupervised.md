# ADR-002: Ensemble Unsupervised (IsolationForest + ECOD) / Ensemble Não-Supervisionado

> 🇺🇸 [English](#en) | 🇧🇷 [Português](#pt)

---

<a id="en"></a>
## [EN] ADR-002: Unsupervised Ensemble (IsolationForest + ECOD)

**Status:** Accepted  
**Date:** 2026-05-20  
**Author:** Maykon Junio Soares

### Context

Fraud detection in real financial data faces the challenge of **extreme class imbalance** (typically < 1% of transactions are fraud) and **lack of labeled data** at the start. We need a model that:

- Works without labeled fraud examples to bootstrap
- Has low false positive rate to avoid alert fatigue
- Can be complemented by a supervised layer as labels accumulate
- Integrates naturally with MLflow for tracking

### Decision

Use an **unsupervised ensemble (IsolationForest + ECOD)** as the primary layer, with a **supervised classifier (XGBoost)** as a secondary layer trained on accumulated labels.

The final score is a weighted combination:
```
final_score = 0.4 * isolation_score + 0.4 * ecod_score + 0.2 * classifier_proba
```

### Rationale

| Model | Strength | Weakness |
|-------|----------|---------|
| IsolationForest | Fast, handles high-dimensional data | May miss clustered anomalies |
| ECOD | Non-parametric, no hyperparameter tuning needed | Higher memory usage |
| XGBoost | High precision with labeled data | Requires labeled examples |

The ensemble approach mirrors the architecture successfully deployed for 140 DB2 instances at Sicoob, where IsolationForest + ECOD reduced false positives by ~40% compared to single-model detection.

### Consequences

**Positive:**
- No labeled data required at bootstrap
- Ensemble reduces individual model blind spots
- Supervised layer improves over time as labels accumulate
- MLflow tracks all three models independently

**Negative:**
- Three models to maintain and monitor
- Inference latency is ~3x a single model (acceptable for our SLA)
- Weighted combination requires calibration

---

<a id="pt"></a>
## [PT] ADR-002: Ensemble Não-Supervisionado (IsolationForest + ECOD)

**Status:** Aceito  
**Data:** 2026-05-20  
**Autor:** Maykon Junio Soares

### Contexto

Detecção de fraude em dados financeiros reais enfrenta o desafio de **desbalanceamento extremo de classes** (tipicamente < 1% das transações são fraude) e **falta de dados rotulados** no início. Precisamos de um modelo que:

- Funcione sem exemplos de fraude rotulados para bootstrap
- Tenha baixa taxa de falsos positivos para evitar fadiga de alertas
- Possa ser complementado por uma camada supervisionada conforme labels se acumulam
- Integre naturalmente com MLflow para rastreamento

### Decisão

Usar um **ensemble não-supervisionado (IsolationForest + ECOD)** como camada primária, com um **classificador supervisionado (XGBoost)** como camada secundária treinado nos labels acumulados.

O score final é uma combinação ponderada:
```
final_score = 0.4 * isolation_score + 0.4 * ecod_score + 0.2 * classifier_proba
```

### Justificativa

| Modelo | Ponto forte | Ponto fraco |
|--------|------------|-------------|
| IsolationForest | Rápido, lida bem com alta dimensionalidade | Pode perder anomalias agrupadas |
| ECOD | Não-paramétrico, sem tuning de hiperparâmetros | Maior uso de memória |
| XGBoost | Alta precisão com dados rotulados | Requer exemplos rotulados |

A abordagem de ensemble espelha a arquitetura implantada com sucesso para 140 instâncias DB2 no Sicoob, onde IsolationForest + ECOD reduziu falsos positivos em ~40% comparado à detecção com modelo único.

### Consequências

**Positivas:**
- Não requer dados rotulados no bootstrap
- Ensemble reduz pontos cegos de modelos individuais
- Camada supervisionada melhora com o tempo conforme labels se acumulam
- MLflow rastreia os três modelos independentemente

**Negativas:**
- Três modelos para manter e monitorar
- Latência de inferência é ~3x a de um modelo único (aceitável para nosso SLA)
- Combinação ponderada requer calibração

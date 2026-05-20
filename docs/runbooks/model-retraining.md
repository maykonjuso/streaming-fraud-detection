# Runbook: Model Retraining / Retreino de Modelo

> 🇺🇸 [English](#en) | 🇧🇷 [Português](#pt)

---

<a id="en"></a>
## [EN] Runbook: Model Retraining

**Last updated:** 2026-05-20  
**Owner:** Maykon Junio Soares

### When to Retrain

| Trigger | Metric | Threshold |
|---------|--------|-----------|
| Score drift | `model_anomaly_score_avg` | > 2 stddev from 7-day baseline |
| False positive spike | Analyst-confirmed FP rate | > 15% |
| New fraud pattern | Manual flag by analyst | Any |
| Scheduled | — | Weekly (Mondays) |

### Retraining Steps

#### 1. Check current model performance

```bash
# Open MLflow to compare experiment runs
open http://localhost:5000
# Note current model version and key metrics (AUC, F1, precision@threshold)
```

#### 2. Collect training data

```bash
# Training data is read from Delta Lake Silver (last N days)
# Default: 30 days. Override via environment variable:
export TRAINING_WINDOW_DAYS=30
```

#### 3. Run training pipeline

```bash
make ml-train
# This will:
# 1. Load features from Silver layer (last TRAINING_WINDOW_DAYS days)
# 2. Train IsolationForest, ECOD, and XGBoost
# 3. Log all metrics and artifacts to MLflow
# 4. Register models as new versions in MLflow Model Registry
```

#### 4. Compare new vs. current model

```bash
open http://localhost:5000
# Navigate to: Models > fraud-detector
# Compare new version metrics against current production version
```

**Promote to production only if:**
- AUC >= current production AUC
- Precision@0.5 >= 0.80
- False positive rate < 15%

#### 5. Promote model to production

```bash
# Set new version as Production stage in MLflow UI, or via CLI:
make ml-promote VERSION=<new_version>
```

#### 6. Restart Gold job to load new model

```bash
make streaming-restart JOB=gold
# Gold job loads the "Production" model version on startup
```

#### 7. Monitor for 30 minutes

Watch Grafana `fraud_overview` dashboard:
- `model_anomaly_score_avg` should stabilize
- Fraud rate should return to expected baseline (~2%)
- No P1/P2 alerts should fire

#### 8. Rollback if needed

```bash
# In MLflow UI: set previous version back to "Production"
make ml-promote VERSION=<previous_version>
make streaming-restart JOB=gold
```

---

<a id="pt"></a>
## [PT] Runbook: Retreino de Modelo

**Última atualização:** 2026-05-20  
**Responsável:** Maykon Junio Soares

### Quando Retreinar

| Gatilho | Métrica | Threshold |
|---------|---------|-----------|
| Drift de score | `model_anomaly_score_avg` | > 2 desvios padrão da baseline de 7 dias |
| Spike de falsos positivos | Taxa de FP confirmada por analista | > 15% |
| Novo padrão de fraude | Flag manual de analista | Qualquer |
| Agendado | — | Semanal (segundas-feiras) |

### Passos de Retreino

#### 1. Verificar performance do modelo atual

```bash
# Abrir MLflow para comparar execuções de experimentos
open http://localhost:5000
# Anotar versão atual do modelo e métricas-chave (AUC, F1, precision@threshold)
```

#### 2. Coletar dados de treino

```bash
# Dados de treino são lidos do Delta Lake Silver (últimos N dias)
# Padrão: 30 dias. Override via variável de ambiente:
export TRAINING_WINDOW_DAYS=30
```

#### 3. Executar pipeline de treino

```bash
make ml-train
# Isso vai:
# 1. Carregar features da camada Silver (últimos TRAINING_WINDOW_DAYS dias)
# 2. Treinar IsolationForest, ECOD e XGBoost
# 3. Logar todas as métricas e artefatos no MLflow
# 4. Registrar modelos como novas versões no MLflow Model Registry
```

#### 4. Comparar novo modelo com o atual

```bash
open http://localhost:5000
# Navegue para: Models > fraud-detector
# Compare métricas da nova versão com a versão em produção atual
```

**Promover para produção apenas se:**
- AUC >= AUC da produção atual
- Precision@0.5 >= 0.80
- Taxa de falsos positivos < 15%

#### 5. Promover modelo para produção

```bash
# Definir nova versão como estágio Production na UI do MLflow, ou via CLI:
make ml-promote VERSION=<nova_versão>
```

#### 6. Reiniciar Gold job para carregar o novo modelo

```bash
make streaming-restart JOB=gold
# Gold job carrega a versão "Production" do modelo ao iniciar
```

#### 7. Monitorar por 30 minutos

Acompanhe o dashboard `fraud_overview` no Grafana:
- `model_anomaly_score_avg` deve estabilizar
- Taxa de fraude deve retornar à baseline esperada (~2%)
- Nenhum alerta P1/P2 deve disparar

#### 8. Rollback se necessário

```bash
# Na UI do MLflow: definir versão anterior de volta para "Production"
make ml-promote VERSION=<versão_anterior>
make streaming-restart JOB=gold
```

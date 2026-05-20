# Runbook: Incident Response / Resposta a Incidentes

> 🇺🇸 [English](#en) | 🇧🇷 [Português](#pt)

---

<a id="en"></a>
## [EN] Runbook: Incident Response

**Last updated:** 2026-05-20  
**Owner:** Maykon Junio Soares

### Severity Levels

| Severity | Description | Response Time |
|----------|-------------|--------------|
| P1 | Pipeline stopped, no data flowing | Immediate |
| P2 | Pipeline running but Gold lag > 5 min | 30 min |
| P3 | High false positive rate, fraud rate spike | 2 hours |
| P4 | Dashboard issue, non-critical metric | Next business day |

---

### Incident: Kafka Consumer Lag (P1/P2)

**Symptoms:** `pipeline_lag_ms` > 300,000 in Grafana. Gold job not consuming.

**Diagnosis:**
```bash
# Check consumer group lag
docker exec kafka kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group fraud-streaming-group

# Check Spark job logs
tail -f logs/gold_job.log
```

**Resolution:**
1. If Spark executor OOM: increase `spark.executor.memory` in `streaming/utils/spark_session.py`
2. If Kafka broker down: `make infra-restart SERVICE=kafka`
3. If checkpoint corrupted: `make streaming-reset-checkpoint JOB=gold` (data will be reprocessed from last offset)

---

### Incident: Fraud Rate Spike (P3)

**Symptoms:** `fraud_transactions_total` rate > 3x baseline for > 10 minutes.

**Diagnosis:**
```bash
# Query recent high-score transactions via API
curl "http://localhost:8000/scores?min_score=0.9&limit=50"

# Check model score distribution in MLflow
open http://localhost:5000
```

**Possible causes:**
- Producer generating anomalous synthetic data → restart: `make producer-restart`
- Model drift (scores shifted globally) → trigger retraining: see [model-retraining.md](./model-retraining.md)
- Legitimate fraud campaign in synthetic data → escalate to analyst review

---

### Incident: API Down (P1)

**Symptoms:** `/health` returns non-200 or times out.

**Diagnosis:**
```bash
make api-logs
# Check for port conflicts
ss -tlnp | grep 8000
```

**Resolution:**
```bash
make api-restart
# If Delta Lake read error: verify gold job is running and Gold path exists
ls -la data/delta/gold/
```

---

### Incident: MLflow Unavailable (P2)

**Symptoms:** Gold job fails to load model. Error: `MlflowException: Could not find model`.

**Resolution:**
```bash
make infra-restart SERVICE=mlflow
# If model registry empty (DB reset): retrain
make ml-train
```

---

<a id="pt"></a>
## [PT] Runbook: Resposta a Incidentes

**Última atualização:** 2026-05-20  
**Responsável:** Maykon Junio Soares

### Níveis de Severidade

| Severidade | Descrição | Tempo de Resposta |
|------------|-----------|------------------|
| P1 | Pipeline parado, sem fluxo de dados | Imediato |
| P2 | Pipeline rodando mas lag Gold > 5 min | 30 min |
| P3 | Alta taxa de falsos positivos, spike de fraude | 2 horas |
| P4 | Problema em dashboard, métrica não-crítica | Próximo dia útil |

---

### Incidente: Lag do Consumidor Kafka (P1/P2)

**Sintomas:** `pipeline_lag_ms` > 300.000 no Grafana. Gold job não está consumindo.

**Diagnóstico:**
```bash
# Verificar lag do consumer group
docker exec kafka kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group fraud-streaming-group

# Verificar logs do job Spark
tail -f logs/gold_job.log
```

**Resolução:**
1. Se executor Spark com OOM: aumentar `spark.executor.memory` em `streaming/utils/spark_session.py`
2. Se broker Kafka down: `make infra-restart SERVICE=kafka`
3. Se checkpoint corrompido: `make streaming-reset-checkpoint JOB=gold` (dados serão reprocessados do último offset)

---

### Incidente: Spike na Taxa de Fraude (P3)

**Sintomas:** taxa de `fraud_transactions_total` > 3x baseline por > 10 minutos.

**Diagnóstico:**
```bash
# Consultar transações recentes com score alto via API
curl "http://localhost:8000/scores?min_score=0.9&limit=50"

# Verificar distribuição de scores no MLflow
open http://localhost:5000
```

**Causas possíveis:**
- Producer gerando dados sintéticos anômalos → reiniciar: `make producer-restart`
- Drift do modelo (scores deslocados globalmente) → acionar retreino: veja [model-retraining.md](./model-retraining.md)
- Campanha de fraude legítima nos dados sintéticos → escalar para revisão de analista

---

### Incidente: API Indisponível (P1)

**Sintomas:** `/health` retorna não-200 ou timeout.

**Diagnóstico:**
```bash
make api-logs
# Verificar conflitos de porta
ss -tlnp | grep 8000
```

**Resolução:**
```bash
make api-restart
# Se erro de leitura Delta Lake: verificar se gold job está rodando e caminho Gold existe
ls -la data/delta/gold/
```

---

### Incidente: MLflow Indisponível (P2)

**Sintomas:** Gold job falha ao carregar modelo. Erro: `MlflowException: Could not find model`.

**Resolução:**
```bash
make infra-restart SERVICE=mlflow
# Se registro de modelos vazio (DB resetado): retreinar
make ml-train
```

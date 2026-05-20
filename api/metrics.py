"""
Custom Prometheus metrics.
Métricas Prometheus customizadas.

EN: Defines domain-specific counters and histograms for the fraud pipeline.
PT: Define contadores e histogramas específicos do domínio para o pipeline de fraude.
"""

from prometheus_client import Counter, Gauge, Histogram

fraud_transactions_total = Counter(
    "fraud_transactions_total",
    "Total transactions flagged as fraud. / Total de transações marcadas como fraude.",
)

pipeline_throughput = Gauge(
    "pipeline_throughput_msgs_per_sec",
    "Messages processed per second in the streaming pipeline. / Mensagens processadas por segundo no pipeline.",
)

pipeline_lag_ms = Histogram(
    "pipeline_lag_ms",
    "End-to-end latency from Kafka to Gold in milliseconds. / Latência ponta-a-ponta do Kafka ao Gold em ms.",
    buckets=[100, 500, 1_000, 5_000, 10_000, 30_000, 60_000, 300_000],
)

model_anomaly_score = Histogram(
    "model_anomaly_score",
    "Distribution of final ensemble fraud scores. / Distribuição dos scores finais de fraude do ensemble.",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)

alert_triage_duration_seconds = Histogram(
    "alert_triage_duration_seconds",
    "Time taken by the MCP agent to triage a fraud alert. / Tempo do agente MCP para triar um alerta.",
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0],
)


def setup_custom_metrics() -> None:
    """Called on app startup to initialize metric state. / Chamado no startup para inicializar estado das métricas."""
    pass

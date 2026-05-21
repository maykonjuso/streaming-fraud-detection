<div align="center">

# streaming-fraud-detection

**Real-time fraud detection on synthetic financial transactions**

[![CI](https://github.com/maykonjuso/streaming-fraud-detection/actions/workflows/ci.yml/badge.svg)](https://github.com/maykonjuso/streaming-fraud-detection/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen)](https://github.com/maykonjuso/streaming-fraud-detection)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

*Plataforma de detecção de fraudes em tempo real em transações financeiras sintéticas.*

</div>

---

## Table of Contents / Índice

- [Overview](#overview)
- [Architecture](#architecture)
- [Stack](#stack)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [ML Pipeline](#ml-pipeline)
- [Monitoring](#monitoring)
- [LLM Agent](#llm-agent)
- [Development](#development)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**EN:** End-to-end streaming fraud detection platform built with production-grade tooling. A Kafka producer emits synthetic financial transactions (with configurable fraud injection), which flow through a PySpark Structured Streaming pipeline into a Delta Lake medallion store (Bronze → Silver → Gold). An ML ensemble (IsolationForest + ECOD + XGBoost) scores transactions in real time, results are served via FastAPI (REST + WebSocket + GraphQL), and the entire system is observed through Prometheus and Grafana. A Claude API + MCP agent handles intelligent alert triage.

**PT:** Plataforma de detecção de fraudes em streaming construída com ferramentas de nível produção. Um producer Kafka emite transações financeiras sintéticas (com injeção de fraude configurável), que fluem por um pipeline PySpark Structured Streaming em um Delta Lake medallion store (Bronze → Silver → Gold). Um ensemble de ML (IsolationForest + ECOD + XGBoost) pontua transações em tempo real, resultados são servidos via FastAPI (REST + WebSocket + GraphQL), e o sistema inteiro é observado via Prometheus e Grafana. Um agente Claude API + MCP faz triagem inteligente de alertas.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  PRODUCER                                                            │
│  synthetic_producer.py ──► Kafka: raw_transactions                  │
│  ~100 tx/s · 2% fraud injection · realistic patterns                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   STREAMING (PySpark)    │
                    │                          │
                    │  ┌──────────────────┐    │
                    │  │  bronze_job.py   │    │  Raw events
                    │  │  Kafka → Bronze  │    │  Schema validation
                    │  └────────┬─────────┘    │
                    │           │              │
                    │  ┌────────▼─────────┐    │
                    │  │  silver_job.py   │    │  Cleaning
                    │  │  Bronze → Silver │    │  Feature engineering
                    │  └────────┬─────────┘    │  Velocity windows
                    │           │              │  Z-score, temporal
                    │  ┌────────▼─────────┐    │
                    │  │   gold_job.py    │    │  ML inference
                    │  │  Silver → Gold   │    │  Ensemble scoring
                    │  └────────┬─────────┘    │
                    └───────────┼──────────────┘
                                │
               ┌────────────────┼────────────────┐
               │                │                │
    ┌──────────▼──────┐  ┌──────▼───────┐  ┌────▼──────────────┐
    │   SERVING        │  │ OBSERVABILITY│  │   LLM AGENT        │
    │                  │  │              │  │                    │
    │  FastAPI          │  │  Prometheus  │  │  Claude API        │
    │  ├─ REST          │  │  Grafana     │  │  MCP Server        │
    │  ├─ WebSocket     │  │  3 dashboards│  │  Alert triage      │
    │  └─ GraphQL       │  │  3 alert     │  │  NL fraud queries  │
    │                  │  │  rules       │  │                    │
    └──────────────────┘  └──────────────┘  └────────────────────┘
```

### Delta Lake Medallion

| Layer | Content | Trigger |
|-------|---------|---------|
| **Bronze** | Raw Kafka events, ingestion metadata, no transformation | Every 10s micro-batch |
| **Silver** | Cleaned data + features (velocity, z-score, temporal) | Every 15s micro-batch |
| **Gold** | ML ensemble scores, fraud prediction, `scored_at` | Every 10s micro-batch |

---

## Stack

| Layer | Technologies |
|-------|-------------|
| **Ingestion** | Apache Kafka, Python, Faker |
| **Stream Processing** | PySpark 3.5 Structured Streaming |
| **Storage** | Delta Lake (delta-spark), Bronze / Silver / Gold |
| **Machine Learning** | IsolationForest, ECOD (PyOD), XGBoost, MLflow |
| **Serving API** | FastAPI, WebSocket, GraphQL (Strawberry) |
| **Observability** | Prometheus, Grafana, custom metrics |
| **LLM / Agents** | Claude API (Anthropic), MCP (Model Context Protocol) |
| **Infrastructure** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions, pytest, ruff |

---

## Quick Start

### Prerequisites

- Docker Engine 24+ and Docker Compose v2
- Python 3.11+
- Make
- 8 GB RAM available (Spark + Kafka + MLflow)

### 1. Clone and configure

```bash
git clone https://github.com/maykonjuso/streaming-fraud-detection.git
cd streaming-fraud-detection
cp .env.example .env
# Set ANTHROPIC_API_KEY in .env to enable the MCP agent (optional)
```

### 2. Install dependencies

```bash
make install
```

### 3. Start infrastructure

```bash
make infra-up
# Kafka, MLflow, Prometheus and Grafana start and reach healthy state (~60s)
```

### 4. Train the initial model

```bash
make ml-train
# Trains IsolationForest + ECOD + XGBoost, registers in MLflow
# http://localhost:5000 → see experiments and model registry
```

### 5. Start the streaming pipeline

```bash
make streaming-start
# Starts bronze_job, silver_job and gold_job as background Spark processes
```

### 6. Start the transaction producer

```bash
make producer-start
# ~100 tx/s with 2% fraud injection → Kafka topic raw_transactions
```

### 7. Start the API

```bash
make api-start
# REST:    http://localhost:8000/docs
# GraphQL: http://localhost:8000/graphql
# Metrics: http://localhost:8000/metrics
```

### 8. Open Grafana

```bash
make grafana-open
# http://localhost:3000  (admin / admin)
```

### Verify everything is running

```bash
make health-check
```

### Stop everything

```bash
make stop-all && make infra-down
```

---

## API Reference

### REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/scores/{transaction_id}` | Fraud score for a transaction |
| `GET` | `/scores/?min_score=0.7&limit=50` | List high-score transactions |
| `GET` | `/transactions/{transaction_id}` | Raw transaction details |
| `GET` | `/metrics` | Prometheus metrics |

### WebSocket

```
ws://localhost:8000/ws/alerts
```

Connect and optionally send `{"min_score": 0.8}` to set your threshold. Fraud alerts are pushed in real time as they are written to the Gold table.

### GraphQL

```
http://localhost:8000/graphql
```

```graphql
# Aggregate fraud statistics
query {
  fraudStats(windowHours: 1) {
    totalTransactions
    fraudCount
    fraudRate
    avgFraudScore
    maxFraudScore
  }
}

# Recent alerts
query {
  recentAlerts(minScore: 0.8, limit: 10) {
    transactionId
    accountId
    finalScore
    isFraudPredicted
    scoredAt
  }
}
```

---

## ML Pipeline

### Ensemble Architecture (ADR-002)

The fraud score is a weighted combination of three models:

```
final_score = 0.4 × IsolationForest + 0.4 × ECOD + 0.2 × XGBoost
```

| Model | Type | Strength |
|-------|------|----------|
| **IsolationForest** | Unsupervised | Fast, handles high-dimensional data |
| **ECOD** | Unsupervised | Non-parametric, no hyperparameter tuning |
| **XGBoost** | Supervised | High precision as labeled data accumulates |

The unsupervised ensemble works without labeled fraud examples at bootstrap — the same approach used in production for 140 DB2 instances, reducing false positives by ~40% vs. single-model detection.

### Features

| Feature | Description |
|---------|-------------|
| `log_amount` | Log-transformed transaction amount |
| `tx_count_1h` | Transaction count per account in last hour |
| `tx_amount_1h` | Total amount per account in last hour |
| `is_high_risk_country` | Flag for countries with elevated fraud rate |
| `hour_of_day` | Hour of transaction (0–23) |
| `day_of_week` | Day of week (0=Monday) |
| `is_weekend` | Binary weekend flag |

### MLflow Tracking

All experiments, parameters, metrics and model artifacts are tracked at `http://localhost:5000`. Models are registered in the MLflow Model Registry and promoted to `Production` stage before being loaded by `gold_job.py`.

---

## Monitoring

### Custom Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `fraud_transactions_total` | Counter | Total transactions flagged as fraud |
| `pipeline_throughput_msgs_per_sec` | Gauge | Messages processed per second |
| `pipeline_lag_ms` | Histogram | Kafka-to-Gold latency in milliseconds |
| `model_anomaly_score` | Histogram | Ensemble score distribution |
| `alert_triage_duration_seconds` | Histogram | MCP agent triage latency |

### Grafana Dashboards

| Dashboard | Key Panels |
|-----------|-----------|
| **Streaming** | Throughput, Kafka lag (p50/p95), Bronze/Silver/Gold write rates |
| **ML Metrics** | Score distribution, fraud rate over time, model inference latency |
| **Fraud Overview** | Fraud count/rate, top fraud accounts, score heatmap |

### Alert Rules (Prometheus)

| Alert | Condition | Severity |
|-------|-----------|----------|
| `HighPipelineLag` | p95 lag > 5 minutes for 2 min | critical |
| `FraudRateSpike` | Rate > 3× baseline for 10 min | warning |
| `APIDown` | `/health` unreachable for 1 min | critical |

---

## LLM Agent

The MCP (Model Context Protocol) agent exposes fraud API tools to Claude, following the same pattern deployed in production at Sicoob for N1 incident triage.

```bash
# Triage a specific fraud alert
python agents/fraud_agent.py --transaction-id <tx_id>
```

The agent automatically:
1. Retrieves transaction details and ML scores
2. Checks velocity patterns on the same account
3. Classifies severity (HIGH / MEDIUM / LOW) and fraud type
4. Returns a structured JSON triage report

Requires `ANTHROPIC_API_KEY` set in `.env`. See [ADR-004](docs/adr/004-mcp-agent-architecture.md).

---

## Development

### Commands

```bash
make help           # list all available commands

make install        # create virtualenv + install dependencies
make lint           # ruff check + format check
make test           # unit tests with coverage (min 80%)
make test-integration  # integration tests (requires infra-up)

make infra-up       # start all Docker services
make infra-down     # stop and remove Docker services
make infra-status   # show service status

make producer-start      # start Kafka producer
make streaming-start     # start bronze + silver + gold jobs
make api-start           # start FastAPI

make ml-train            # train ensemble and register in MLflow
make ml-promote VERSION=3  # promote model version to Production

make health-check   # verify all services are responding
make stop-all       # stop producer, API and streaming jobs
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
# ruff check + format run automatically on every commit
```

### Running Tests

```bash
# Unit tests (fast, no infrastructure required)
make test

# Integration tests (requires make infra-up first)
make test-integration

# Run a specific test
pytest tests/unit/test_features.py -v
```

### Conventional Commits

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat:     new feature
fix:      bug fix
docs:     documentation only
style:    formatting (no logic change)
refactor: code change without fix or feature
test:     adding or updating tests
chore:    build process or auxiliary tools
perf:     performance improvement
```

---

## Project Structure

```
streaming-fraud-detection/
│
├── producer/                   # Synthetic transaction generator
│   ├── synthetic_producer.py   # Kafka producer with fraud injection
│   ├── transaction_schema.py   # Pydantic schema
│   └── config.py
│
├── streaming/                  # PySpark Structured Streaming jobs
│   ├── bronze_job.py           # Kafka → Delta Bronze
│   ├── silver_job.py           # Bronze → Silver (features)
│   ├── gold_job.py             # Silver → Gold (ML inference)
│   └── utils/
│       ├── spark_session.py
│       └── delta_utils.py
│
├── ml/                         # Machine learning pipeline
│   ├── features/
│   │   └── feature_engineering.py
│   ├── models/                 # Model wrappers (issue #3)
│   └── training/
│       └── train.py            # IsolationForest + ECOD + XGBoost + MLflow
│
├── api/                        # FastAPI application
│   ├── main.py
│   ├── metrics.py              # Custom Prometheus metrics
│   ├── routers/
│   │   ├── scores.py           # REST score endpoints
│   │   ├── transactions.py
│   │   └── websocket.py        # Real-time fraud alert push
│   └── graphql/
│       └── schema.py           # Strawberry GraphQL schema
│
├── agents/                     # LLM integration
│   ├── mcp_server.py           # MCP server (Anthropic protocol)
│   └── fraud_agent.py          # Claude API triage agent
│
├── infra/                      # Infrastructure configuration
│   ├── docker-compose.yml      # Kafka, MLflow, Prometheus, Grafana
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alert_rules.yml
│   └── grafana/
│       ├── provisioning/
│       └── dashboards/
│
├── tests/
│   ├── unit/                   # Fast tests, no infrastructure
│   └── integration/            # E2E tests (requires infra-up)
│
├── docs/
│   ├── adr/                    # Architecture Decision Records (bilingual)
│   ├── rfc/                    # Request for Comments (bilingual)
│   └── runbooks/               # Operational runbooks (bilingual)
│
└── .github/
    ├── workflows/
    │   ├── ci.yml              # Lint → Test → Build
    │   └── release.yml         # Changelog + GitHub Release on tag
    └── ISSUE_TEMPLATE/
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [ADR-001](docs/adr/001-delta-lake-over-parquet.md) | Why Delta Lake over pure Parquet |
| [ADR-002](docs/adr/002-ensemble-unsupervised.md) | Unsupervised ensemble rationale |
| [ADR-003](docs/adr/003-graphql-for-complex-queries.md) | GraphQL for analytical queries |
| [ADR-004](docs/adr/004-mcp-agent-architecture.md) | MCP agent architecture |
| [RFC-001](docs/rfc/001-feature-store-evolution.md) | Planned feature store migration |
| [Startup Runbook](docs/runbooks/startup.md) | Full startup procedure |
| [Incident Response](docs/runbooks/incident-response.md) | P1–P4 incident playbook |
| [Model Retraining](docs/runbooks/model-retraining.md) | When and how to retrain |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, branch conventions, and PR guidelines.

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

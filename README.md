# streaming-fraud-detection

Plataforma de detecção de fraudes em tempo real em transações financeiras sintéticas.

## Arquitetura

```
Producer (Python/Faker)
    │
    ▼ Kafka: raw_transactions
PySpark Structured Streaming
    │
    ├── Bronze → Delta Lake (eventos brutos, validação de schema)
    ├── Silver → Delta Lake (limpeza + feature engineering)
    └── Gold   → Delta Lake (scores ML em tempo real)
    │
    ▼
FastAPI (REST + WebSocket + GraphQL)
    │
    ├── Prometheus + Grafana (observabilidade)
    └── Claude API + MCP (agente de triagem de alertas)
```

## Stack

| Camada | Tecnologias |
|--------|------------|
| Ingestão | Apache Kafka, Python, Faker |
| Processamento | PySpark Structured Streaming |
| Armazenamento | Delta Lake (delta-spark), Bronze/Silver/Gold |
| ML | IsolationForest, ECOD, XGBoost, MLflow |
| Serving | FastAPI, WebSocket, GraphQL (Strawberry) |
| Observabilidade | Prometheus, Grafana |
| LLM | Claude API (Anthropic), MCP |
| DevOps | Docker, GitHub Actions, pytest |

## Pré-requisitos

- Docker e Docker Compose v2
- Python 3.11+
- Make

## Início rápido

```bash
# Sobe toda a infraestrutura
make infra-up

# Inicia o producer de transações sintéticas
make producer-start

# Inicia os jobs de streaming (bronze → silver → gold)
make streaming-start

# Treina o modelo inicial
make ml-train

# Sobe a API
make api-start

# Abre o Grafana
make grafana-open
```

## Desenvolvimento

```bash
# Instala dependências
make install

# Roda todos os testes
make test

# Roda lint
make lint

# Roda testes de integração (requer infra up)
make test-integration
```

## Documentação

- [ADR-001: Delta Lake em vez de Parquet puro](docs/adr/001-delta-lake-over-parquet.md)
- [ADR-002: Ensemble unsupervised IsolationForest + ECOD](docs/adr/002-ensemble-unsupervised.md)
- [ADR-003: GraphQL para queries complexas](docs/adr/003-graphql-for-complex-queries.md)
- [ADR-004: Agente MCP para triagem de alertas](docs/adr/004-mcp-agent-architecture.md)
- [RFC-001: Evolução para Feature Store](docs/rfc/001-feature-store-evolution.md)
- [Runbook: Startup](docs/runbooks/startup.md)
- [Runbook: Resposta a Incidentes](docs/runbooks/incident-response.md)
- [Runbook: Retreino de Modelo](docs/runbooks/model-retraining.md)

## Estrutura do Repositório

```
streaming-fraud-detection/
├── producer/               # Gerador de transações sintéticas via Kafka
├── streaming/              # Jobs PySpark (bronze, silver, gold)
├── ml/                     # Feature engineering, modelos, treino, MLflow
├── api/                    # FastAPI: REST, WebSocket, GraphQL
├── agents/                 # Claude API + MCP server
├── infra/                  # Docker Compose, Prometheus, Grafana
├── tests/                  # pytest: unit e integration
├── docs/                   # ADRs, RFCs, runbooks
└── .github/workflows/      # CI/CD GitHub Actions
```

## Métricas monitoradas

| Métrica | Descrição |
|---------|-----------|
| `fraud_transactions_total` | Total de transações flagadas como fraude |
| `pipeline_throughput_msgs_per_sec` | Mensagens processadas por segundo |
| `pipeline_lag_ms` | Latência Kafka → Gold em ms |
| `model_anomaly_score_avg` | Score médio de anomalia (IsolationForest + ECOD) |
| `api_request_duration_seconds` | Latência da API por endpoint |

## Padrões de desenvolvimento

- Commits em inglês, seguindo Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`)
- Branches: `feature/<nome>`, `fix/<nome>`, `docs/<nome>`
- Toda decisão de arquitetura não-óbvia → ADR em `docs/adr/`
- Toda mudança estrutural proposta → RFC em `docs/rfc/`
- Operações em produção → runbook em `docs/runbooks/`
- Cobertura mínima de testes: 80% em `ml/` e `api/`

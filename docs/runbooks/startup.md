# Runbook: Startup / Inicialização

> 🇺🇸 [English](#en) | 🇧🇷 [Português](#pt)

---

<a id="en"></a>
## [EN] Runbook: Startup

**Last updated:** 2026-05-20  
**Owner:** Maykon Junio Soares

### Prerequisites

- Docker Engine 24+ and Docker Compose v2
- Python 3.11+
- 8 GB RAM available (Spark + Kafka + MLflow)
- Ports free: 9092 (Kafka), 5000 (MLflow), 8000 (API), 9090 (Prometheus), 3000 (Grafana)

### Step 1: Clone and configure environment

```bash
git clone https://github.com/maykonjuso/streaming-fraud-detection.git
cd streaming-fraud-detection
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY if using the MCP agent
```

### Step 2: Start infrastructure

```bash
make infra-up
# Waits for Kafka, MLflow, Prometheus and Grafana to be healthy
# Expected time: ~60 seconds
```

**Verify:**
```bash
make infra-status
# All services should show "healthy" or "running"
```

### Step 3: Install Python dependencies

```bash
make install
# Creates virtualenv and installs requirements.txt + requirements-dev.txt
```

### Step 4: Train the initial model

```bash
make ml-train
# Generates synthetic training data, trains IsolationForest + ECOD + XGBoost
# Registers models in MLflow at http://localhost:5000
# Expected time: ~2-3 minutes
```

### Step 5: Start streaming jobs

```bash
make streaming-start
# Starts bronze_job, silver_job and gold_job as background Spark processes
# Checkpoint dirs created at ./data/checkpoints/
```

### Step 6: Start the Kafka producer

```bash
make producer-start
# Sends ~100 transactions/second with ~2% fraud injection rate
# Logs to ./logs/producer.log
```

### Step 7: Start the API

```bash
make api-start
# FastAPI at http://localhost:8000
# Docs at http://localhost:8000/docs
# GraphQL at http://localhost:8000/graphql
```

### Step 8: Verify end-to-end

```bash
make health-check
# Calls /health on all services and verifies Kafka lag
```

Open Grafana at http://localhost:3000 (admin/admin). Import dashboards from `infra/grafana/dashboards/`.

### Shutdown

```bash
make stop-all        # stops producer, API and streaming jobs
make infra-down      # stops all Docker containers
```

---

<a id="pt"></a>
## [PT] Runbook: Inicialização

**Última atualização:** 2026-05-20  
**Responsável:** Maykon Junio Soares

### Pré-requisitos

- Docker Engine 24+ e Docker Compose v2
- Python 3.11+
- 8 GB RAM disponíveis (Spark + Kafka + MLflow)
- Portas livres: 9092 (Kafka), 5000 (MLflow), 8000 (API), 9090 (Prometheus), 3000 (Grafana)

### Passo 1: Clone e configure o ambiente

```bash
git clone https://github.com/maykonjuso/streaming-fraud-detection.git
cd streaming-fraud-detection
cp .env.example .env
# Edite .env: defina ANTHROPIC_API_KEY se usar o agente MCP
```

### Passo 2: Inicie a infraestrutura

```bash
make infra-up
# Aguarda Kafka, MLflow, Prometheus e Grafana ficarem saudáveis
# Tempo estimado: ~60 segundos
```

**Verificação:**
```bash
make infra-status
# Todos os serviços devem mostrar "healthy" ou "running"
```

### Passo 3: Instale as dependências Python

```bash
make install
# Cria virtualenv e instala requirements.txt + requirements-dev.txt
```

### Passo 4: Treine o modelo inicial

```bash
make ml-train
# Gera dados sintéticos de treino, treina IsolationForest + ECOD + XGBoost
# Registra modelos no MLflow em http://localhost:5000
# Tempo estimado: ~2-3 minutos
```

### Passo 5: Inicie os jobs de streaming

```bash
make streaming-start
# Inicia bronze_job, silver_job e gold_job como processos Spark em background
# Diretórios de checkpoint criados em ./data/checkpoints/
```

### Passo 6: Inicie o producer Kafka

```bash
make producer-start
# Envia ~100 transações/segundo com taxa de injeção de fraude ~2%
# Logs em ./logs/producer.log
```

### Passo 7: Inicie a API

```bash
make api-start
# FastAPI em http://localhost:8000
# Docs em http://localhost:8000/docs
# GraphQL em http://localhost:8000/graphql
```

### Passo 8: Verifique end-to-end

```bash
make health-check
# Chama /health em todos os serviços e verifica lag do Kafka
```

Abra o Grafana em http://localhost:3000 (admin/admin). Importe os dashboards de `infra/grafana/dashboards/`.

### Desligamento

```bash
make stop-all        # para producer, API e jobs de streaming
make infra-down      # para todos os containers Docker
```

.PHONY: help install lint test test-integration infra-up infra-down infra-status \
        producer-start producer-restart streaming-start streaming-restart \
        ml-train ml-promote api-start api-restart api-logs \
        health-check stop-all grafana-open

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help:  ## EN: Show this help. PT: Exibe este menu de ajuda.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

# ── Environment ──────────────────────────────────────────────────────────────

install:  ## EN: Create virtualenv and install all dependencies. PT: Cria virtualenv e instala dependências.
	python3.11 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt -r requirements-dev.txt

lint:  ## EN: Run ruff linter and formatter check. PT: Executa linter e verificação de formatação ruff.
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .

# ── Tests ─────────────────────────────────────────────────────────────────────

test:  ## EN: Run unit tests with coverage. PT: Executa testes unitários com cobertura.
	$(VENV)/bin/pytest tests/unit/ -v --tb=short --cov=ml --cov=api --cov-report=term-missing --cov-fail-under=80

test-integration:  ## EN: Run integration tests (requires infra-up). PT: Testes de integração (requer infra-up).
	$(VENV)/bin/pytest tests/integration/ -v --tb=short -m integration

# ── Infrastructure ────────────────────────────────────────────────────────────

infra-up:  ## EN: Start all Docker services (Kafka, MLflow, Prometheus, Grafana). PT: Sobe serviços Docker.
	docker compose -f infra/docker-compose.yml up -d --wait
	@echo "✓ Infrastructure started. Grafana: http://localhost:3000 | MLflow: http://localhost:5000"

infra-down:  ## EN: Stop and remove all Docker services. PT: Para e remove serviços Docker.
	docker compose -f infra/docker-compose.yml down

infra-status:  ## EN: Show status of all Docker services. PT: Exibe status dos serviços Docker.
	docker compose -f infra/docker-compose.yml ps

infra-restart:  ## EN: Restart a specific service: make infra-restart SERVICE=kafka. PT: Reinicia serviço específico.
	docker compose -f infra/docker-compose.yml restart $(SERVICE)

# ── Producer ──────────────────────────────────────────────────────────────────

producer-start:  ## EN: Start synthetic transaction producer. PT: Inicia producer de transações sintéticas.
	nohup $(PYTHON) producer/synthetic_producer.py > logs/producer.log 2>&1 &
	@echo "✓ Producer started. Logs: logs/producer.log"

producer-restart:  ## EN: Restart the producer. PT: Reinicia o producer.
	pkill -f synthetic_producer.py || true
	$(MAKE) producer-start

# ── Streaming ─────────────────────────────────────────────────────────────────

streaming-start:  ## EN: Start all Spark streaming jobs. PT: Inicia todos os jobs de streaming Spark.
	mkdir -p logs data/delta data/checkpoints
	nohup spark-submit streaming/bronze_job.py > logs/bronze.log 2>&1 &
	nohup spark-submit streaming/silver_job.py > logs/silver.log 2>&1 &
	nohup spark-submit streaming/gold_job.py   > logs/gold.log   2>&1 &
	@echo "✓ Streaming jobs started. Logs: logs/{bronze,silver,gold}.log"

streaming-restart:  ## EN: Restart a specific job: make streaming-restart JOB=gold. PT: Reinicia job específico.
	pkill -f $(JOB)_job.py || true
	nohup spark-submit streaming/$(JOB)_job.py > logs/$(JOB).log 2>&1 &

streaming-reset-checkpoint:  ## EN: Reset checkpoint for a job (triggers reprocessing): make streaming-reset-checkpoint JOB=gold. PT: Reseta checkpoint.
	pkill -f $(JOB)_job.py || true
	rm -rf data/checkpoints/$(JOB)
	$(MAKE) streaming-restart JOB=$(JOB)

# ── ML ────────────────────────────────────────────────────────────────────────

ml-train:  ## EN: Train the fraud detection ensemble and register in MLflow. PT: Treina ensemble e registra no MLflow.
	$(PYTHON) ml/training/train.py

ml-promote:  ## EN: Promote model version to Production: make ml-promote VERSION=3. PT: Promove versão do modelo para produção.
	$(PYTHON) -c "import mlflow; mlflow.set_tracking_uri('http://localhost:5000'); \
		client = mlflow.MlflowClient(); \
		[client.transition_model_version_stage('fraud-$(MODEL)', '$(VERSION)', 'Production') for MODEL in ['isolation-forest','ecod','classifier']]"

# ── API ───────────────────────────────────────────────────────────────────────

api-start:  ## EN: Start the FastAPI server. PT: Inicia o servidor FastAPI.
	nohup $(VENV)/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &
	@echo "✓ API started at http://localhost:8000 | Docs: http://localhost:8000/docs"

api-restart:  ## EN: Restart the FastAPI server. PT: Reinicia o servidor FastAPI.
	pkill -f "uvicorn api.main" || true
	$(MAKE) api-start

api-logs:  ## EN: Tail API logs. PT: Acompanha logs da API.
	tail -f logs/api.log

# ── Health ────────────────────────────────────────────────────────────────────

health-check:  ## EN: Check health of all services. PT: Verifica saúde de todos os serviços.
	@curl -sf http://localhost:8000/health && echo "✓ API OK" || echo "✗ API DOWN"
	@curl -sf http://localhost:5000/health && echo "✓ MLflow OK" || echo "✗ MLflow DOWN"
	@curl -sf http://localhost:9090/-/healthy && echo "✓ Prometheus OK" || echo "✗ Prometheus DOWN"
	@curl -sf http://localhost:3000/api/health && echo "✓ Grafana OK" || echo "✗ Grafana DOWN"

stop-all:  ## EN: Stop producer, API, and all streaming jobs. PT: Para producer, API e todos os jobs de streaming.
	pkill -f synthetic_producer.py || true
	pkill -f "uvicorn api.main" || true
	pkill -f bronze_job.py || true
	pkill -f silver_job.py || true
	pkill -f gold_job.py || true
	@echo "✓ All processes stopped."

grafana-open:  ## EN: Open Grafana in the browser. PT: Abre o Grafana no navegador.
	xdg-open http://localhost:3000 2>/dev/null || open http://localhost:3000 2>/dev/null || echo "Open http://localhost:3000"

"""
EN: End-to-end integration tests for the streaming pipeline.
    Requires infrastructure running: make infra-up
    Run with: make test-integration

PT: Testes de integração end-to-end para o pipeline de streaming.
    Requer infraestrutura rodando: make infra-up
    Execute com: make test-integration
"""

import json
import uuid

import pytest
from kafka import KafkaProducer

KAFKA_BOOTSTRAP = "localhost:9092"
API_BASE = "http://localhost:8000"


@pytest.fixture(scope="module")
def kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all",
    )
    yield producer
    producer.close()


@pytest.mark.integration
def test_api_health():
    """EN: API must be reachable. PT: API deve estar acessível."""
    import httpx
    resp = httpx.get(f"{API_BASE}/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.integration
def test_kafka_producer_sends_message(kafka_producer):
    """EN: Producer must send to Kafka without error. PT: Producer deve enviar ao Kafka sem erro."""
    tx_id = str(uuid.uuid4())
    future = kafka_producer.send(
        "raw_transactions",
        value={
            "transaction_id": tx_id,
            "account_id": "ACC_TEST",
            "merchant_id": "MRC_TEST",
            "amount": 999.99,
            "currency": "BRL",
            "transaction_type": "purchase",
            "channel": "online",
            "country_code": "BR",
            "timestamp": "2026-05-20T10:00:00+00:00",
            "is_fraud": False,
        },
    )
    result = future.get(timeout=10)
    assert result is not None


@pytest.mark.integration
def test_graphql_fraud_stats():
    """EN: GraphQL fraudStats query must return a valid structure. PT: Query fraudStats do GraphQL deve retornar estrutura válida."""
    import httpx
    resp = httpx.post(
        f"{API_BASE}/graphql",
        json={"query": "{ fraudStats(windowHours: 1) { totalTransactions fraudRate } }"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data

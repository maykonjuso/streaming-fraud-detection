"""
Synthetic transaction producer.
Producer de transações sintéticas.

EN: Generates realistic synthetic financial transactions and publishes them to
    a Kafka topic. Injects a configurable percentage of fraudulent transactions
    with anomalous patterns (high amount, unusual country, high velocity).

PT: Gera transações financeiras sintéticas realistas e as publica em um tópico
    Kafka. Injeta uma porcentagem configurável de transações fraudulentas com
    padrões anômalos (valor alto, país incomum, alta velocidade).

Usage / Uso:
    python producer/synthetic_producer.py
    PRODUCER_TRANSACTIONS_PER_SECOND=200 python producer/synthetic_producer.py
"""

import json
import logging
import random
import time
import uuid
from datetime import UTC, datetime

from faker import Faker
from kafka import KafkaProducer

from config import config
from transaction_schema import Transaction, TransactionChannel, TransactionType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("producer")

fake = Faker("pt_BR")


def _build_normal_transaction(account_id: str, merchant_id: str) -> Transaction:
    return Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account_id,
        merchant_id=merchant_id,
        amount=round(random.lognormvariate(4.5, 1.2), 2),
        currency="BRL",
        transaction_type=random.choice(list(TransactionType)),
        channel=random.choice(list(TransactionChannel)),
        country_code="BR",
        timestamp=datetime.now(tz=UTC),
        is_fraud=False,
    )


def _build_fraudulent_transaction(account_id: str, merchant_id: str) -> Transaction:
    """
    EN: Injects fraud signals: high amount, unusual country, unusual hour.
    PT: Injeta sinais de fraude: valor alto, país incomum, horário incomum.
    """
    return Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account_id,
        merchant_id=merchant_id,
        amount=round(random.uniform(5_000, 50_000), 2),
        currency="BRL",
        transaction_type=TransactionType.TRANSFER,
        channel=TransactionChannel.ONLINE,
        country_code=random.choice(["NG", "RU", "CN", "UA", "RO"]),
        timestamp=datetime.now(tz=UTC),
        is_fraud=True,
    )


def create_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=config.kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all",
        retries=5,
    )


def run() -> None:
    accounts = [f"ACC_{i:06d}" for i in range(config.num_accounts)]
    merchants = [f"MRC_{i:04d}" for i in range(config.num_merchants)]

    producer = create_producer()
    interval = 1.0 / config.transactions_per_second

    logger.info(
        "Starting producer: %d tx/s, %.1f%% fraud → topic '%s'",
        config.transactions_per_second,
        config.fraud_injection_rate * 100,
        config.kafka_topic,
    )

    sent = 0
    try:
        while True:
            account_id = random.choice(accounts)
            merchant_id = random.choice(merchants)

            is_fraud = random.random() < config.fraud_injection_rate
            tx = (
                _build_fraudulent_transaction(account_id, merchant_id)
                if is_fraud
                else _build_normal_transaction(account_id, merchant_id)
            )

            producer.send(config.kafka_topic, value=tx.to_kafka_payload())
            sent += 1

            if sent % 1_000 == 0:
                logger.info("Sent %d transactions (%d fraud)", sent, int(sent * config.fraud_injection_rate))

            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Shutting down producer after %d transactions.", sent)
    finally:
        producer.flush()
        producer.close()


if __name__ == "__main__":
    run()

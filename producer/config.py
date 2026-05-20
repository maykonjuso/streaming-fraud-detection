"""
Producer configuration.
Configuração do producer.
"""

from pydantic_settings import BaseSettings


class ProducerConfig(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "raw_transactions"
    transactions_per_second: int = 100
    fraud_injection_rate: float = 0.02
    num_accounts: int = 10_000
    num_merchants: int = 500

    model_config = {"env_file": ".env", "env_prefix": "PRODUCER_"}


config = ProducerConfig()

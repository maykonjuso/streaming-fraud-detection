"""
Transaction schema definitions.
Definições de schema de transação.

EN: Pydantic models for validating and serializing synthetic transaction events
    before they are sent to the Kafka topic.

PT: Modelos Pydantic para validação e serialização de eventos de transação sintéticos
    antes de serem enviados ao tópico Kafka.
"""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionType(StrEnum):
    PURCHASE = "purchase"
    TRANSFER = "transfer"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    REFUND = "refund"


class TransactionChannel(StrEnum):
    ONLINE = "online"
    ATM = "atm"
    POS = "pos"
    MOBILE = "mobile"


class Transaction(BaseModel):
    transaction_id: UUID
    account_id: str
    merchant_id: str
    amount: float = Field(gt=0)
    currency: str = Field(default="BRL", max_length=3)
    transaction_type: TransactionType
    channel: TransactionChannel
    country_code: str = Field(max_length=2)
    timestamp: datetime
    is_fraud: bool = Field(default=False)

    model_config = {"use_enum_values": True}

    def to_kafka_payload(self) -> dict:
        """Serialize to dict for Kafka producer. / Serializa para dict para o producer Kafka."""
        return self.model_dump(mode="json")

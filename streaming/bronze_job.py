"""
Bronze streaming job: Kafka → Delta Lake Bronze.
Job de streaming Bronze: Kafka → Delta Lake Bronze.

EN: Reads raw transaction events from the Kafka topic, validates schema,
    adds ingestion metadata, and writes to the Bronze Delta table.
    No business transformations here — Bronze preserves raw data fidelity.

PT: Lê eventos brutos de transação do tópico Kafka, valida o schema,
    adiciona metadados de ingestão e escreve na tabela Delta Bronze.
    Sem transformações de negócio aqui — Bronze preserva fidelidade dos dados brutos.

Usage / Uso:
    spark-submit streaming/bronze_job.py
"""

import logging

from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    DoubleType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from utils.delta_utils import write_delta_stream
from utils.spark_session import get_spark

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bronze_job")

KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC = "raw_transactions"
BRONZE_PATH = "data/delta/bronze"
CHECKPOINT_PATH = "data/checkpoints/bronze"

TRANSACTION_SCHEMA = StructType(
    [
        StructField("transaction_id", StringType(), False),
        StructField("account_id", StringType(), False),
        StructField("merchant_id", StringType(), False),
        StructField("amount", DoubleType(), False),
        StructField("currency", StringType(), True),
        StructField("transaction_type", StringType(), False),
        StructField("channel", StringType(), False),
        StructField("country_code", StringType(), False),
        StructField("timestamp", TimestampType(), False),
        StructField("is_fraud", BooleanType(), False),
    ]
)


def run() -> None:
    spark = get_spark("fraud-bronze")

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
    )

    parsed = (
        raw.select(
            F.from_json(F.col("value").cast("string"), TRANSACTION_SCHEMA).alias("data"),
            F.col("offset").alias("kafka_offset"),
            F.col("partition").alias("kafka_partition"),
            F.col("timestamp").alias("kafka_timestamp"),
        )
        .select(
            "data.*",
            "kafka_offset",
            "kafka_partition",
            "kafka_timestamp",
            F.current_timestamp().alias("ingested_at"),
        )
        .filter(F.col("transaction_id").isNotNull())
    )

    logger.info("Bronze job started. Writing to %s", BRONZE_PATH)
    write_delta_stream(
        df=parsed,
        path=BRONZE_PATH,
        checkpoint_path=CHECKPOINT_PATH,
        trigger_seconds=10,
        partition_by=["transaction_type"],
    )


if __name__ == "__main__":
    run()

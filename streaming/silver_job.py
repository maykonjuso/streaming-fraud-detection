"""
Silver streaming job: Delta Lake Bronze → Silver (feature engineering).
Job de streaming Silver: Delta Lake Bronze → Silver (feature engineering).

EN: Reads from Bronze, applies cleaning and feature engineering
    (velocity windows, amount z-score, time-based features), and writes to Silver.

PT: Lê do Bronze, aplica limpeza e feature engineering
    (janelas de velocidade, z-score de valor, features temporais) e escreve no Silver.

Usage / Uso:
    spark-submit streaming/silver_job.py
"""

import logging

from pyspark.sql import functions as F
from pyspark.sql import types as T

from utils.delta_utils import read_delta_stream, write_delta_stream
from utils.spark_session import get_spark

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("silver_job")

BRONZE_PATH = "data/delta/bronze"
SILVER_PATH = "data/delta/silver"
CHECKPOINT_PATH = "data/checkpoints/silver"


def add_features(df):
    """
    EN: Compute fraud-relevant features using Spark window functions.
        - tx_count_1h: number of transactions by account in the last hour
        - tx_amount_1h: total amount by account in the last hour
        - is_high_risk_country: flag for countries with high fraud rate
        - hour_of_day / day_of_week: temporal context features

    PT: Calcula features relevantes para fraude usando window functions do Spark.
        - tx_count_1h: número de transações da conta na última hora
        - tx_amount_1h: valor total da conta na última hora
        - is_high_risk_country: flag para países com alta taxa de fraude
        - hour_of_day / day_of_week: features de contexto temporal
    """
    high_risk_countries = ["NG", "RU", "CN", "UA", "RO", "PK"]

    window_1h = (
        F.window("timestamp", "1 hour")
    )

    velocity = (
        df.groupBy("account_id", window_1h)
        .agg(
            F.count("*").alias("tx_count_1h"),
            F.sum("amount").alias("tx_amount_1h"),
        )
        .select("account_id", "window.start", "tx_count_1h", "tx_amount_1h")
    )

    return (
        df.join(velocity, on="account_id", how="left")
        .withColumn("is_high_risk_country", F.col("country_code").isin(high_risk_countries).cast(T.IntegerType()))
        .withColumn("hour_of_day", F.hour("timestamp"))
        .withColumn("day_of_week", F.dayofweek("timestamp"))
        .withColumn("is_weekend", (F.col("day_of_week").isin([1, 7])).cast(T.IntegerType()))
        .withColumn("log_amount", F.log1p("amount"))
        .fillna({"tx_count_1h": 1, "tx_amount_1h": F.col("amount")})
    )


def run() -> None:
    spark = get_spark("fraud-silver")

    bronze_stream = read_delta_stream(spark, BRONZE_PATH)
    silver = add_features(bronze_stream)

    logger.info("Silver job started. Writing to %s", SILVER_PATH)
    write_delta_stream(
        df=silver,
        path=SILVER_PATH,
        checkpoint_path=CHECKPOINT_PATH,
        trigger_seconds=15,
    )


if __name__ == "__main__":
    run()

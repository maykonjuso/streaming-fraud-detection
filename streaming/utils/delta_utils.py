"""
Delta Lake utility helpers.
Utilitários para Delta Lake.

EN: Helper functions for creating, reading and writing Delta tables
    used across all streaming jobs.

PT: Funções auxiliares para criação, leitura e escrita de tabelas Delta
    usadas em todos os jobs de streaming.
"""

from delta import DeltaTable
from pyspark.sql import DataFrame, SparkSession


def table_exists(spark: SparkSession, path: str) -> bool:
    return DeltaTable.isDeltaTable(spark, path)


def read_delta_stream(spark: SparkSession, path: str) -> DataFrame:
    return spark.readStream.format("delta").load(path)


def write_delta_stream(
    df: DataFrame,
    path: str,
    checkpoint_path: str,
    trigger_seconds: int = 10,
    partition_by: list[str] | None = None,
) -> None:
    writer = (
        df.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", checkpoint_path)
        .trigger(processingTime=f"{trigger_seconds} seconds")
    )
    if partition_by:
        writer = writer.partitionBy(*partition_by)
    writer.start(path).awaitTermination()


def optimize_table(spark: SparkSession, path: str, zorder_cols: list[str]) -> None:
    """
    EN: Run OPTIMIZE + ZORDER to improve read performance for common query patterns.
    PT: Executa OPTIMIZE + ZORDER para melhorar performance de leitura nos padrões comuns de query.
    """
    cols = ", ".join(zorder_cols)
    spark.sql(f"OPTIMIZE delta.`{path}` ZORDER BY ({cols})")

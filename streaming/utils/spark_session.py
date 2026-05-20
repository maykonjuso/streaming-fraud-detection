"""
Shared Spark session factory.
Fábrica de sessão Spark compartilhada.

EN: Provides a configured SparkSession with Delta Lake support.
    All streaming jobs import from here to guarantee a consistent configuration.

PT: Fornece uma SparkSession configurada com suporte a Delta Lake.
    Todos os jobs de streaming importam daqui para garantir configuração consistente.
"""

from pyspark.sql import SparkSession


def get_spark(app_name: str) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.executor.memory", "2g")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )

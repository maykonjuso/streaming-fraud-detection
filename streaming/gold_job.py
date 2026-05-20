"""
Gold streaming job: Delta Lake Silver → Gold (ML inference).
Job de streaming Gold: Delta Lake Silver → Gold (inferência ML).

EN: Reads from Silver, loads the production model ensemble from MLflow,
    applies real-time scoring, and writes fraud scores to the Gold Delta table.
    Gold is the serving layer consumed by the FastAPI.

PT: Lê do Silver, carrega o ensemble de modelos de produção do MLflow,
    aplica scoring em tempo real e escreve os scores de fraude na tabela Delta Gold.
    Gold é a camada de serving consumida pela FastAPI.

Usage / Uso:
    spark-submit streaming/gold_job.py
"""

import logging

import mlflow
import numpy as np
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

from utils.delta_utils import read_delta_stream, write_delta_stream
from utils.spark_session import get_spark

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gold_job")

SILVER_PATH = "data/delta/silver"
GOLD_PATH = "data/delta/gold"
CHECKPOINT_PATH = "data/checkpoints/gold"
MLFLOW_TRACKING_URI = "http://localhost:5000"

FEATURE_COLS = [
    "amount",
    "log_amount",
    "tx_count_1h",
    "tx_amount_1h",
    "is_high_risk_country",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
]

GOLD_SCHEMA = StructType(
    [
        StructField("transaction_id", StringType(), False),
        StructField("account_id", StringType(), False),
        StructField("isolation_score", DoubleType(), True),
        StructField("ecod_score", DoubleType(), True),
        StructField("classifier_proba", DoubleType(), True),
        StructField("final_score", DoubleType(), True),
        StructField("is_fraud_predicted", StringType(), True),
        StructField("scored_at", StringType(), False),
    ]
)


def load_models():
    """
    EN: Load production models from MLflow Model Registry.
        Returns tuple: (isolation_model, ecod_model, classifier_model)

    PT: Carrega modelos de produção do MLflow Model Registry.
        Retorna tupla: (isolation_model, ecod_model, classifier_model)
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    isolation = mlflow.sklearn.load_model("models:/fraud-isolation-forest/Production")
    ecod = mlflow.sklearn.load_model("models:/fraud-ecod/Production")
    classifier = mlflow.sklearn.load_model("models:/fraud-classifier/Production")
    return isolation, ecod, classifier


def build_score_udf(isolation_model, ecod_model, classifier_model):
    """
    EN: Build a Pandas UDF that applies the model ensemble to a micro-batch.
        Score = 0.4 * IsolationForest + 0.4 * ECOD + 0.2 * Classifier
        (see ADR-002 for ensemble rationale)

    PT: Constrói uma Pandas UDF que aplica o ensemble de modelos a um micro-batch.
        Score = 0.4 * IsolationForest + 0.4 * ECOD + 0.2 * Classificador
        (ver ADR-002 para justificativa do ensemble)
    """
    iso = isolation_model
    ecod = ecod_model
    clf = classifier_model

    @F.pandas_udf(GOLD_SCHEMA)
    def score_batch(iterator):
        for pdf in iterator:
            features = pdf[FEATURE_COLS].fillna(0).values
            iso_scores = (-iso.score_samples(features) + 1) / 2
            ecod_scores = ecod.decision_function(features)
            ecod_scores = (ecod_scores - ecod_scores.min()) / (
                ecod_scores.max() - ecod_scores.min() + 1e-9
            )
            clf_probas = clf.predict_proba(features)[:, 1]
            final = 0.4 * iso_scores + 0.4 * ecod_scores + 0.2 * clf_probas

            result = pd.DataFrame(
                {
                    "transaction_id": pdf["transaction_id"],
                    "account_id": pdf["account_id"],
                    "isolation_score": iso_scores,
                    "ecod_score": ecod_scores,
                    "classifier_proba": clf_probas,
                    "final_score": final,
                    "is_fraud_predicted": np.where(final >= 0.5, "FRAUD", "NORMAL"),
                    "scored_at": pd.Timestamp.utcnow().isoformat(),
                }
            )
            yield result

    return score_batch


def run() -> None:
    spark = get_spark("fraud-gold")
    isolation_model, ecod_model, classifier_model = load_models()
    score_udf = build_score_udf(isolation_model, ecod_model, classifier_model)

    silver_stream = read_delta_stream(spark, SILVER_PATH)
    gold = silver_stream.mapInPandas(score_udf, schema=GOLD_SCHEMA)

    logger.info("Gold job started. Writing to %s", GOLD_PATH)
    write_delta_stream(
        df=gold,
        path=GOLD_PATH,
        checkpoint_path=CHECKPOINT_PATH,
        trigger_seconds=10,
    )


if __name__ == "__main__":
    run()

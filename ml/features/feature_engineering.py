"""
Feature engineering for ML training.
Feature engineering para treino de ML.

EN: Computes fraud-detection features from raw transaction data (Pandas/batch).
    Must remain in sync with silver_job.py (Spark/streaming) to avoid train/serve skew.
    See RFC-001 for the planned Feature Store migration.

PT: Computa features de detecção de fraude a partir de dados brutos de transação (Pandas/batch).
    Deve permanecer sincronizado com silver_job.py (Spark/streaming) para evitar train/serve skew.
    Ver RFC-001 para a migração planejada para Feature Store.
"""

import numpy as np
import pandas as pd

HIGH_RISK_COUNTRIES = {"NG", "RU", "CN", "UA", "RO", "PK"}

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


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    EN: Compute all fraud features for a batch of transactions.
        Input df must have: account_id, amount, country_code, timestamp columns.

    PT: Computa todas as features de fraude para um batch de transações.
        O df de entrada deve ter: colunas account_id, amount, country_code, timestamp.
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    df["log_amount"] = np.log1p(df["amount"])
    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["is_high_risk_country"] = df["country_code"].isin(HIGH_RISK_COUNTRIES).astype(int)

    df = df.sort_values("timestamp")
    velocity = (
        df.set_index("timestamp")
        .groupby("account_id")["amount"]
        .rolling("1h", min_periods=1)
        .agg(["count", "sum"])
        .rename(columns={"count": "tx_count_1h", "sum": "tx_amount_1h"})
        .reset_index()
    )
    df = df.merge(velocity[["account_id", "timestamp", "tx_count_1h", "tx_amount_1h"]], on=["account_id", "timestamp"], how="left")
    df[["tx_count_1h", "tx_amount_1h"]] = df[["tx_count_1h", "tx_amount_1h"]].fillna({"tx_count_1h": 1, "tx_amount_1h": df["amount"]})

    return df


def get_feature_matrix(df: pd.DataFrame) -> np.ndarray:
    """Return numpy feature matrix ready for model input. / Retorna matriz numpy pronta para input do modelo."""
    return compute_features(df)[FEATURE_COLS].fillna(0).values

"""
Model training pipeline with MLflow tracking.
Pipeline de treino de modelos com rastreamento MLflow.

EN: Trains the fraud detection ensemble (IsolationForest + ECOD + XGBoost),
    logs all experiments to MLflow, and registers production-ready models
    in the MLflow Model Registry.

PT: Treina o ensemble de detecção de fraude (IsolationForest + ECOD + XGBoost),
    loga todos os experimentos no MLflow e registra modelos prontos para produção
    no MLflow Model Registry.

Usage / Uso:
    python ml/training/train.py
    TRAINING_WINDOW_DAYS=60 python ml/training/train.py
"""

import logging
import os

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from pyod.models.ecod import ECOD
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from ml.features.feature_engineering import FEATURE_COLS, get_feature_matrix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train")

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
TRAINING_WINDOW_DAYS = int(os.getenv("TRAINING_WINDOW_DAYS", "30"))
SILVER_PATH = os.getenv("SILVER_PATH", "data/delta/silver")
CONTAMINATION = 0.02


def load_training_data() -> pd.DataFrame:
    """
    EN: Load feature data from Delta Lake Silver for the training window.
    PT: Carrega dados de features do Delta Lake Silver para a janela de treino.
    """
    from delta import DeltaTable
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("ml-train").getOrCreate()
    cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=TRAINING_WINDOW_DAYS)
    df = (
        DeltaTable.forPath(spark, SILVER_PATH)
        .toDF()
        .filter(f"timestamp >= '{cutoff.isoformat()}'")
        .toPandas()
    )
    logger.info("Loaded %d rows from Silver (last %d days)", len(df), TRAINING_WINDOW_DAYS)
    return df


def train_isolation_forest(X: np.ndarray) -> IsolationForest:
    model = IsolationForest(contamination=CONTAMINATION, n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X)
    return model


def train_ecod(X: np.ndarray) -> ECOD:
    model = ECOD(contamination=CONTAMINATION)
    model.fit(X)
    return model


def train_classifier(X_train: np.ndarray, y_train: np.ndarray) -> XGBClassifier:
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
        eval_metric="auc",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def run() -> None:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("fraud-detection")

    df = load_training_data()
    X = get_feature_matrix(df)
    y = df["is_fraud"].astype(int).values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    with mlflow.start_run(run_name="ensemble-training"):
        mlflow.log_params({
            "training_window_days": TRAINING_WINDOW_DAYS,
            "contamination": CONTAMINATION,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "fraud_rate": float(y.mean()),
            "features": FEATURE_COLS,
        })

        logger.info("Training IsolationForest...")
        iso = train_isolation_forest(X_train)
        iso_scores = -iso.score_samples(X_test)
        iso_auc = roc_auc_score(y_test, iso_scores)
        mlflow.log_metric("isolation_forest_auc", iso_auc)
        mlflow.sklearn.log_model(iso, "isolation_forest")
        mlflow.register_model(f"runs:/{mlflow.active_run().info.run_id}/isolation_forest", "fraud-isolation-forest")

        logger.info("Training ECOD...")
        ecod = train_ecod(X_train)
        ecod_scores = ecod.decision_function(X_test)
        ecod_auc = roc_auc_score(y_test, ecod_scores)
        mlflow.log_metric("ecod_auc", ecod_auc)
        mlflow.sklearn.log_model(ecod, "ecod")
        mlflow.register_model(f"runs:/{mlflow.active_run().info.run_id}/ecod", "fraud-ecod")

        logger.info("Training XGBoost classifier...")
        clf = train_classifier(X_train, y_train)
        clf_probas = clf.predict_proba(X_test)[:, 1]
        clf_auc = roc_auc_score(y_test, clf_probas)
        clf_preds = (clf_probas >= 0.5).astype(int)
        mlflow.log_metric("classifier_auc", clf_auc)
        mlflow.log_text(classification_report(y_test, clf_preds), "classification_report.txt")
        mlflow.sklearn.log_model(clf, "classifier")
        mlflow.register_model(f"runs:/{mlflow.active_run().info.run_id}/classifier", "fraud-classifier")

        iso_n = (-iso.score_samples(X_test) + 1) / 2
        ecod_n = (ecod_scores - ecod_scores.min()) / (ecod_scores.max() - ecod_scores.min() + 1e-9)
        ensemble_scores = 0.4 * iso_n + 0.4 * ecod_n + 0.2 * clf_probas
        ensemble_auc = roc_auc_score(y_test, ensemble_scores)
        mlflow.log_metric("ensemble_auc", ensemble_auc)

        logger.info(
            "Training complete. AUC — IsoForest: %.4f | ECOD: %.4f | XGB: %.4f | Ensemble: %.4f",
            iso_auc, ecod_auc, clf_auc, ensemble_auc,
        )


if __name__ == "__main__":
    run()

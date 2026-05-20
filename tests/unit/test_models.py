"""
EN: Unit tests for ML model wrappers.
PT: Testes unitários para os wrappers de modelos ML.
"""

import numpy as np
from ml.features.feature_engineering import get_feature_matrix
from ml.training.train import train_ecod, train_isolation_forest


class TestIsolationForest:
    def test_fits_without_error(self, sample_transactions):
        X = get_feature_matrix(sample_transactions)
        model = train_isolation_forest(X)
        assert model is not None

    def test_scores_are_negative(self, sample_transactions):
        X = get_feature_matrix(sample_transactions)
        model = train_isolation_forest(X)
        scores = model.score_samples(X)
        assert (scores < 0).all(), "IsolationForest score_samples should return negative values"

    def test_fraud_scores_lower_than_normal(self, sample_transactions):
        X = get_feature_matrix(sample_transactions)
        model = train_isolation_forest(X)
        scores = model.score_samples(X)
        fraud_mask = sample_transactions["is_fraud"].values
        avg_fraud_score = scores[fraud_mask].mean()
        avg_normal_score = scores[~fraud_mask].mean()
        assert avg_fraud_score < avg_normal_score, "Fraud transactions should have lower (more anomalous) scores"


class TestECOD:
    def test_fits_without_error(self, sample_transactions):
        X = get_feature_matrix(sample_transactions)
        model = train_ecod(X)
        assert model is not None

    def test_decision_function_returns_array(self, sample_transactions):
        X = get_feature_matrix(sample_transactions)
        model = train_ecod(X)
        scores = model.decision_function(X)
        assert isinstance(scores, np.ndarray)
        assert len(scores) == len(sample_transactions)

    def test_fraud_scores_higher_than_normal(self, sample_transactions):
        X = get_feature_matrix(sample_transactions)
        model = train_ecod(X)
        scores = model.decision_function(X)
        fraud_mask = sample_transactions["is_fraud"].values
        avg_fraud_score = scores[fraud_mask].mean()
        avg_normal_score = scores[~fraud_mask].mean()
        assert avg_fraud_score > avg_normal_score, "ECOD fraud scores should be higher (more anomalous)"

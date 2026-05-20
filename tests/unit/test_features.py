"""
EN: Unit tests for feature engineering module.
PT: Testes unitários para o módulo de feature engineering.
"""

import numpy as np
import pandas as pd
import pytest

from ml.features.feature_engineering import FEATURE_COLS, compute_features, get_feature_matrix


class TestComputeFeatures:
    def test_returns_all_expected_columns(self, sample_transactions):
        result = compute_features(sample_transactions)
        for col in FEATURE_COLS:
            assert col in result.columns, f"Missing feature column: {col}"

    def test_log_amount_is_positive(self, sample_transactions):
        result = compute_features(sample_transactions)
        assert (result["log_amount"] > 0).all()

    def test_high_risk_country_flagged(self, sample_transactions):
        result = compute_features(sample_transactions)
        fraud_rows = result[result["is_fraud"]]
        assert (fraud_rows["is_high_risk_country"] == 1).all(), "Fraud transactions should be high-risk country"

    def test_normal_country_not_flagged(self, sample_transactions):
        result = compute_features(sample_transactions)
        normal_rows = result[~result["is_fraud"]]
        assert (normal_rows["is_high_risk_country"] == 0).all()

    def test_hour_of_day_in_valid_range(self, sample_transactions):
        result = compute_features(sample_transactions)
        assert result["hour_of_day"].between(0, 23).all()

    def test_day_of_week_in_valid_range(self, sample_transactions):
        result = compute_features(sample_transactions)
        assert result["day_of_week"].between(0, 6).all()

    def test_velocity_features_positive(self, sample_transactions):
        result = compute_features(sample_transactions)
        assert (result["tx_count_1h"] >= 1).all()
        assert (result["tx_amount_1h"] > 0).all()


class TestGetFeatureMatrix:
    def test_returns_numpy_array(self, sample_transactions):
        X = get_feature_matrix(sample_transactions)
        assert isinstance(X, np.ndarray)

    def test_shape_matches_rows_and_features(self, sample_transactions, feature_cols):
        X = get_feature_matrix(sample_transactions)
        assert X.shape == (len(sample_transactions), len(feature_cols))

    def test_no_nan_values(self, sample_transactions):
        X = get_feature_matrix(sample_transactions)
        assert not np.isnan(X).any(), "Feature matrix must not contain NaN"

"""
EN: Shared pytest fixtures for unit and integration tests.
PT: Fixtures pytest compartilhadas para testes unitários e de integração.
"""

import pandas as pd
import pytest


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    """
    EN: Small synthetic transaction DataFrame for unit tests.
        Contains 8 normal and 2 fraudulent transactions.

    PT: Pequeno DataFrame de transações sintéticas para testes unitários.
        Contém 8 transações normais e 2 fraudulentas.
    """
    return pd.DataFrame(
        {
            "transaction_id": [f"TX_{i:04d}" for i in range(10)],
            "account_id": ["ACC_0001"] * 5 + ["ACC_0002"] * 5,
            "merchant_id": ["MRC_0001"] * 10,
            "amount": [150.0, 200.0, 180.0, 95.0, 12000.0, 300.0, 250.0, 400.0, 350.0, 25000.0],
            "currency": ["BRL"] * 10,
            "transaction_type": ["purchase"] * 8 + ["transfer"] * 2,
            "channel": ["pos"] * 8 + ["online"] * 2,
            "country_code": ["BR"] * 8 + ["NG", "RU"],
            "timestamp": pd.date_range("2026-05-20 10:00", periods=10, freq="5min", tz="UTC"),
            "is_fraud": [False] * 8 + [True, True],
        }
    )


@pytest.fixture
def feature_cols() -> list[str]:
    return [
        "amount",
        "log_amount",
        "tx_count_1h",
        "tx_amount_1h",
        "is_high_risk_country",
        "hour_of_day",
        "day_of_week",
        "is_weekend",
    ]

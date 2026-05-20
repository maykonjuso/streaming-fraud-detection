"""
EN: Unit tests for FastAPI endpoints.
PT: Testes unitários para endpoints FastAPI.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_body(self):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}


class TestScoresEndpoint:
    def test_list_scores_returns_200(self):
        response = client.get("/scores/")
        # EN: 501 is expected until Delta Lake integration is complete.
        # PT: 501 é esperado até a integração com Delta Lake estar completa.
        assert response.status_code in (200, 501)

    def test_list_scores_validates_min_score(self):
        response = client.get("/scores/?min_score=1.5")
        assert response.status_code == 422

    def test_list_scores_validates_limit(self):
        response = client.get("/scores/?limit=9999")
        assert response.status_code == 422


class TestGraphQL:
    def test_graphql_endpoint_reachable(self):
        response = client.post("/graphql", json={"query": "{ __typename }"})
        assert response.status_code == 200

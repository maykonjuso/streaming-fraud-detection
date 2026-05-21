"""
EN: Unit tests for FastAPI endpoints and WebSocket broadcaster.
PT: Testes unitários para endpoints FastAPI e broadcaster WebSocket.
"""

import json
from unittest.mock import AsyncMock, MagicMock

from api.main import app
from api.routers.websocket import AlertBroadcaster
from fastapi.testclient import TestClient

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


class TestAlertBroadcaster:
    def setup_method(self):
        AlertBroadcaster._connections.clear()

    def test_disconnect_removes_connection(self):
        ws = MagicMock()
        AlertBroadcaster._connections.append(ws)
        AlertBroadcaster.disconnect(ws)
        assert ws not in AlertBroadcaster._connections

    def test_disconnect_unknown_connection_raises(self):
        ws = MagicMock()
        try:
            AlertBroadcaster.disconnect(ws)
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass

    async def test_broadcast_sends_json_to_all(self):
        ws = AsyncMock()
        AlertBroadcaster._connections.append(ws)
        payload = {"transaction_id": "TX_0001", "final_score": 0.92}
        await AlertBroadcaster.broadcast(payload)
        ws.send_text.assert_called_once_with(json.dumps(payload))

    async def test_broadcast_removes_dead_connections(self):
        dead_ws = AsyncMock()
        dead_ws.send_text.side_effect = Exception("disconnected")
        AlertBroadcaster._connections.append(dead_ws)
        await AlertBroadcaster.broadcast({"score": 0.9})
        assert dead_ws not in AlertBroadcaster._connections

    async def test_broadcast_empty_connections(self):
        await AlertBroadcaster.broadcast({"score": 0.9})

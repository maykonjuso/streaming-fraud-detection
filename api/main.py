"""
FastAPI application entry point.
Ponto de entrada da aplicação FastAPI.

EN: Mounts REST routers, WebSocket endpoint, GraphQL, and Prometheus metrics.
PT: Monta routers REST, endpoint WebSocket, GraphQL e métricas Prometheus.
"""

from contextlib import asynccontextmanager

import strawberry
from api.graphql.schema import Query
from api.metrics import setup_custom_metrics
from api.routers import scores, transactions, websocket
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from strawberry.fastapi import GraphQLRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_custom_metrics()
    yield


app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection scores and alerts. / Scores e alertas de fraude em tempo real.",
    version="1.0.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)

app.include_router(scores.router, prefix="/scores", tags=["Scores"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(websocket.router, tags=["WebSocket"])

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

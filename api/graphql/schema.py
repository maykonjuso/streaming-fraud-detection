"""
GraphQL schema (Strawberry).
Schema GraphQL (Strawberry).

EN: Exposes complex fraud queries for dashboards and the MCP agent.
    REST handles operational endpoints; GraphQL handles analytical queries.
    See ADR-003 for the rationale.

PT: Expõe queries complexas de fraude para dashboards e o agente MCP.
    REST lida com endpoints operacionais; GraphQL lida com queries analíticas.
    Ver ADR-003 para a justificativa.
"""


import strawberry


@strawberry.type
class FraudScoreGQL:
    transaction_id: str
    account_id: str
    final_score: float
    is_fraud_predicted: str
    scored_at: str


@strawberry.type
class FraudStats:
    window_hours: int
    total_transactions: int
    fraud_count: int
    fraud_rate: float
    avg_fraud_score: float
    max_fraud_score: float


@strawberry.type
class Query:
    @strawberry.field
    def transaction_score(self, transaction_id: str) -> FraudScoreGQL | None:
        """
        EN: Fetch fraud score for a specific transaction ID.
        PT: Busca score de fraude para um transaction ID específico.
        """
        return None  # TODO: query Delta Gold

    @strawberry.field
    def recent_alerts(
        self,
        min_score: float = 0.5,
        limit: int = 50,
        account_id: str | None = None,
    ) -> list[FraudScoreGQL]:
        """
        EN: List recent fraud alerts with optional account filter.
        PT: Lista alertas de fraude recentes com filtro opcional de conta.
        """
        return []  # TODO: query Delta Gold

    @strawberry.field
    def fraud_stats(self, window_hours: int = 1) -> FraudStats:
        """
        EN: Aggregate fraud statistics for the given time window.
        PT: Estatísticas agregadas de fraude para a janela de tempo fornecida.
        """
        return FraudStats(  # TODO: query Delta Gold
            window_hours=window_hours,
            total_transactions=0,
            fraud_count=0,
            fraud_rate=0.0,
            avg_fraud_score=0.0,
            max_fraud_score=0.0,
        )

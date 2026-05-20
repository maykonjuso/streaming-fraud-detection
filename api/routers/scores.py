"""
Fraud score REST endpoints.
Endpoints REST de score de fraude.

EN: Endpoints for retrieving fraud scores from the Gold Delta table.
PT: Endpoints para recuperar scores de fraude da tabela Delta Gold.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class FraudScore(BaseModel):
    transaction_id: str
    account_id: str
    isolation_score: float
    ecod_score: float
    classifier_proba: float
    final_score: float
    is_fraud_predicted: str
    scored_at: str


@router.get("/{transaction_id}", response_model=FraudScore)
async def get_score(transaction_id: str):
    """
    EN: Get fraud score for a specific transaction.
    PT: Retorna o score de fraude de uma transação específica.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/", response_model=list[FraudScore])
async def list_scores(
    min_score: float = Query(default=0.5, ge=0.0, le=1.0),
    limit: int = Query(default=50, le=500),
):
    """
    EN: List recent transactions above the minimum fraud score threshold.
    PT: Lista transações recentes acima do threshold mínimo de score de fraude.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")

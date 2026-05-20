"""
Transaction REST endpoints.
Endpoints REST de transações.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str):
    """
    EN: Fetch raw transaction details from Delta Lake Bronze.
    PT: Busca detalhes brutos de uma transação no Delta Lake Bronze.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")

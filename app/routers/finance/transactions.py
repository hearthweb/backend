from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies.auth import (
    get_current_admin,
    get_current_admin_responses,
)
from app.models.finance.transaction import (
    Transaction,
    TransactionCreate,
    TransactionPublic,
    TransactionRead,
)
from app.utils import get_or_404, get_or_404_responses

router = APIRouter(prefix="/transactions")


@router.get(
    "",
    summary="Get a list of all transactions",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
    },
    operation_id="financeTransactions",
)
def finance_transactions(
    db: Annotated[Session, Depends(get_db)],
) -> list[TransactionRead]:
    return db.exec(select(Transaction))


@router.post(
    "",
    summary="Create a new transaction",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
    },
    operation_id="financeTransactionsCreate",
)
def finance_transactions_create(
    body: TransactionCreate,
    db: Annotated[Session, Depends(get_db)],
) -> TransactionRead:
    transaction = Transaction.model_validate(body)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get(
    "/{id}",
    summary="Get a specific transaction",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
        **get_or_404_responses,
    },
    operation_id="financeTransactionsById",
)
def finance_transactions_by_id(
    db: Annotated[Session, Depends(get_db)],
) -> TransactionPublic:
    return get_or_404(
        db.exec(
            select(Transaction)
            .where(Transaction.id == id)
            .options(selectinload(Transaction.lines)),
        ).one_or_none(),
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific transaction",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
        **get_or_404_responses,
    },
    operation_id="financeTransactionsByIdDelete",
)
def finance_transactions_by_id_delete(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    transaction = get_or_404(
        db.exec(
            select(Transaction).where(Transaction.id == id),
        ).one_or_none(),
    )
    db.delete(transaction)
    db.commit()

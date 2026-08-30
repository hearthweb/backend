from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.auth.dependencies.session import (
    get_login_session,
    get_login_session_responses,
)
from app.database import get_db
from app.finance.models.line import Line
from app.finance.models.tag import Tag
from app.finance.models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionPublic,
    TransactionRead,
)
from app.utils import get_or_404, get_or_404_responses

router = APIRouter(
    prefix="/transactions",
    dependencies=[Depends(get_login_session)],
    responses={**get_login_session_responses},
)


@router.get(
    "",
    summary="Get a list of all transactions",
    operation_id="financeTransactions",
)
def transactions(
    db: Annotated[Session, Depends(get_db)],
) -> list[TransactionRead]:
    return db.exec(select(Transaction))


@router.post(
    "",
    summary="Create a new transaction",
    operation_id="financeTransactionsCreate",
)
def transactions_create(
    body: TransactionCreate,
    db: Annotated[Session, Depends(get_db)],
) -> TransactionRead:
    transaction = Transaction.model_validate(body.transaction)
    db.add(transaction)
    db.flush()
    for l in body.lines:
        line = Line.model_validate(
            l,
            update={
                "tags": [Tag.get_or_create(tag) for tag in l.tags],
                "transaction_id": transaction.id,
            },
        )
        db.add(line)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get(
    "/{id}",
    summary="Get a specific transaction",
    responses={**get_or_404_responses},
    operation_id="financeTransactionsById",
)
def transactions_by_id(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> TransactionPublic:
    return get_or_404(
        db.exec(
            select(Transaction)
            .where(Transaction.id == id)
            .options(
                selectinload(Transaction.lines).selectinload(Line.account),
                selectinload(Transaction.lines).selectinload(Line.tags),
            ),
        ).one_or_none(),
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific transaction",
    responses={**get_or_404_responses},
    operation_id="financeTransactionsByIdDelete",
)
def transactions_by_id_delete(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    transaction = get_or_404(
        db.exec(
            select(Transaction).where(Transaction.id == id).with_for_update(),
        ).one_or_none(),
    )
    db.delete(transaction)
    db.commit()

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.auth.dependencies.session import (
    get_login_session,
    get_login_session_responses,
)
from app.database import get_db
from app.finance.models.account import (
    Account,
    AccountRead,
    AccountWrite,
)
from app.finance.models.line import (
    Line,
    LineRead,
)
from app.utils import get_or_404, get_or_404_responses

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
    dependencies=[Depends(get_login_session)],
    responses={**get_login_session_responses},
)


@router.get(
    "",
    summary="Get a list of all accounts",
    operation_id="financeAccounts",
)
def accounts(
    db: Annotated[Session, Depends(get_db)],
) -> list[AccountRead]:
    return db.exec(select(Account))


@router.post(
    "",
    summary="Create a new account",
    operation_id="financeAccountsCreate",
)
def accounts_create(
    body: AccountWrite,
    db: Annotated[Session, Depends(get_db)],
) -> AccountRead:
    account = Account.model_validate(body)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get(
    "/{id}",
    summary="Get a specific account",
    responses={**get_or_404_responses},
    operation_id="financeAccountsById",
)
def accounts_by_id(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> AccountRead:
    return get_or_404(
        db.exec(
            select(Account).where(Account.id == id),
        ).one_or_none(),
    )


@router.get(
    "/{id}/lines",
    summary="Get lines that belong to a specific account",
    operation_id="financeAccountsByIdLines",
)
def accounts_by_id_lines(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[LineRead]:
    return db.exec(select(Line).where(Line.account_id == id))


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific account",
    responses={**get_or_404_responses},
    operation_id="financeAccountsByIdDelete",
)
def accounts_by_id_delete(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    account = get_or_404(
        db.exec(
            select(Account).where(Account.id == id),
        ).one_or_none(),
    )
    db.delete(account)
    db.commit()

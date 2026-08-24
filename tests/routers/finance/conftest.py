from datetime import UTC, datetime

import pytest
from sqlmodel import Session

from app.models.finance.account import Account
from app.models.finance.line import Line
from app.models.finance.transaction import Transaction

from . import (
    ACCOUNT_NAME,
    LINE_AMOUNT,
    LINE_SUMMARY,
    TRANSACTION_SUMMARY,
)


@pytest.fixture(name="account")
def account(
    db: Session,
) -> Account:
    account = Account(name=ACCOUNT_NAME)
    db.add(account)
    db.commit()
    return account


@pytest.fixture(name="transaction")
def transaction(
    db: Session,
) -> Transaction:
    transaction = Transaction(
        date=datetime.now(tz=UTC),
        summary=TRANSACTION_SUMMARY,
    )
    db.add(transaction)
    db.commit()
    return transaction


@pytest.fixture(name="line")
def line(
    db: Session,
    account: Account,
    transaction: Transaction,
):
    line = Line(
        summary=LINE_SUMMARY,
        account_id=account.id,
        amount=LINE_AMOUNT,
        transaction_id=transaction.id,
    )
    db.add(line)
    db.commit()
    return line

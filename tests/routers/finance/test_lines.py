from datetime import UTC, datetime
from decimal import Decimal

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


def test_finance_line_create(
    account: Account,
    transaction: Transaction,
    db: Session,
):
    line = Line(
        summary=LINE_SUMMARY,
        account_id=account.id,
        amount=LINE_AMOUNT,
        transaction_id=transaction.id,
    )
    db.add(line)
    db.commit()
    db.refresh(account)
    assert account.balance == LINE_AMOUNT
    assert transaction.amount == LINE_AMOUNT


def test_finance_line_delete(
    account: Account,
    transaction: Transaction,
    line: Line,
    db: Session,
):
    db.delete(line)
    db.commit()
    db.refresh(account)
    assert account.balance == Decimal(0)
    assert transaction.amount == Decimal(0)


def test_finance_line_change_account_id(
    account: Account,
    line: Line,
    db: Session,
):
    account2 = Account(name=ACCOUNT_NAME)
    db.add(account2)
    db.commit()
    line.account_id = account2.id
    db.add(line)
    db.commit()
    assert account.balance == Decimal(0)
    assert account2.balance == LINE_AMOUNT


def test_finance_line_change_amount(
    account: Account,
    transaction: Transaction,
    line: Line,
    db: Session,
):
    new_amount = LINE_AMOUNT + Decimal(25)
    line.amount = new_amount
    db.add(line)
    db.commit()
    assert account.balance == new_amount
    assert transaction.amount == new_amount


def test_finance_line_change_transaction_id(
    transaction: Transaction,
    line: Line,
    db: Session,
):
    transaction2 = Transaction(
        date=datetime.now(tz=UTC),
        summary=TRANSACTION_SUMMARY,
    )
    db.add(transaction2)
    db.commit()
    line.transaction_id = transaction2.id
    db.add(line)
    db.commit()
    assert transaction.amount == Decimal(0)
    assert transaction2.amount == LINE_AMOUNT

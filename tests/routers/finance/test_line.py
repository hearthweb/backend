from decimal import Decimal

from sqlmodel import Session

from app.models.finance.account import Account
from app.models.finance.line import Line
from app.models.finance.transaction import Transaction
from tests.constants import (
    FINANCE_ACCOUNT_NAME,
    FINANCE_LINE_AMOUNT,
    FINANCE_LINE_SUMMARY,
)


def test_finance_line_create(
    account: Account,
    transaction: Transaction,
    db: Session,
):
    amount = FINANCE_LINE_AMOUNT
    line = Line(
        summary=FINANCE_LINE_SUMMARY,
        account_id=account.id,
        amount=amount,
        transaction_id=transaction.id,
    )
    db.add(line)
    db.commit()
    db.refresh(account)
    assert account.balance == amount


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


def test_finance_line_change_account_id(
    account: Account,
    line: Line,
    db: Session,
):
    account2 = Account(name=FINANCE_ACCOUNT_NAME)
    db.add(account2)
    db.commit()
    line.account_id = account2.id
    db.add(line)
    db.commit()
    assert account.balance == Decimal(0)
    assert account2.balance == FINANCE_LINE_AMOUNT


def test_finance_line_change_amount(
    account: Account,
    line: Line,
    db: Session,
):
    new_amount = FINANCE_LINE_AMOUNT + Decimal(25)
    line.amount = new_amount
    db.add(line)
    db.commit()
    assert account.balance == new_amount

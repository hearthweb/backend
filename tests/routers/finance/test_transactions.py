from datetime import UTC, datetime

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.finance.account import Account
from app.models.finance.line import Line
from app.models.finance.transaction import (
    Transaction,
    TransactionPublic,
    TransactionRead,
)
from app.models.user import User
from tests.utils import compare_sorted, dump

from . import (
    LINE_AMOUNT,
    LINE_SUMMARY,
    TRANSACTION_SUMMARY,
)


def test_finance_transactions(
    client: TestClient,
    logged_in_admin: User,
    transaction: Transaction,
):
    response = client.get("/finance/transactions")
    assert response.status_code == status.HTTP_200_OK
    assert compare_sorted(
        response.json(),
        [
            dump(Transaction, transaction),
        ],
        "id",
    )


def test_finance_transactions_create(
    client: TestClient,
    logged_in_admin: User,
    account: Account,
    db: Session,
):
    response = client.post(
        "/finance/transactions",
        json={
            "transaction": {
                "date": datetime.now(tz=UTC).isoformat(),
                "summary": TRANSACTION_SUMMARY,
            },
            "lines": [
                {
                    "summary": LINE_SUMMARY,
                    "account_id": account.id,
                    "amount": str(LINE_AMOUNT),
                }
            ],
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == dump(TransactionRead, db.get(Transaction, json["id"]))
    lines: list[Line] = db.exec(select(Line)).all()
    assert len(lines) == 1
    assert lines[0].transaction_id == json["id"]


def test_finance_transactions_by_id(
    client: TestClient,
    logged_in_admin: User,
    transaction: Transaction,
    line: Line,
):
    response = client.get(f"/finance/transactions/{transaction.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == dump(TransactionPublic, transaction)


def test_finance_transactions_by_id_delete(
    client: TestClient,
    logged_in_admin: User,
    transaction: Transaction,
    db: Session,
):
    response = client.delete(f"/finance/transactions/{transaction.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db.get(Account, transaction.id) is None

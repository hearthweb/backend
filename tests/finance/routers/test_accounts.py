from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth.models.user import User
from app.finance.models.account import Account, AccountRead
from app.finance.models.line import Line
from tests.utils import compare_sorted, dump

from . import ACCOUNT_NAME


def test_finance_accounts(
    client: TestClient,
    logged_in_user: User,
    account: Account,
    db: Session,
):
    response = client.get("/finance/accounts")
    assert response.status_code == status.HTTP_200_OK
    assert compare_sorted(
        response.json(),
        [
            dump(Account, account),
        ],
        "id",
    )


def test_finance_accounts_create(
    client: TestClient,
    logged_in_user: User,
    db: Session,
):
    response = client.post(
        "/finance/accounts",
        json={
            "name": ACCOUNT_NAME,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == dump(AccountRead, db.get(Account, json["id"]))


def test_finance_accounts_by_id(
    client: TestClient,
    logged_in_user: User,
    account: Account,
):
    response = client.get(f"/finance/accounts/{account.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == dump(AccountRead, account)


def test_finance_accounts_by_id_lines(
    client: TestClient,
    logged_in_user: User,
    account: Account,
    line: Line,
    db: Session,
):
    response = client.get(f"/finance/accounts/{account.id}/lines")
    assert response.status_code == status.HTTP_200_OK
    assert compare_sorted(
        response.json(),
        [
            dump(Line, line),
        ],
        "id",
    )


def test_finance_accounts_by_id_delete(
    client: TestClient,
    logged_in_user: User,
    account: Account,
    db: Session,
):
    response = client.delete(f"/finance/accounts/{account.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db.get(Account, account.id) is None

from collections.abc import Generator

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from app.database import get_db
from app.main import app
from app.models.finance.account import Account
from app.models.finance.line import Line
from app.models.finance.transaction import Transaction
from app.models.user import User
from tests.constants import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    FINANCE_ACCOUNT_NAME,
    FINANCE_LINE_AMOUNT,
    FINANCE_LINE_SUMMARY,
    FINANCE_TRANSACTION_SUMMARY,
    USER_EMAIL,
    USER_PASSWORD,
)


@pytest.fixture(name="db")
def db_fixture() -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client", autouse=True)
def client_fixture(db: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def create_user(db: Session, email: str, password: str, is_admin: bool) -> User:
    user = User(email=email, is_admin=is_admin)
    user.set_password(password)
    db.add(user)
    db.commit()
    return user


@pytest.fixture(name="admin")
def admin_fixture(db: Session) -> User:
    return create_user(db, ADMIN_EMAIL, ADMIN_PASSWORD, True)


@pytest.fixture(name="user")
def user_fixture(db: Session) -> User:
    return create_user(db, USER_EMAIL, USER_PASSWORD, False)


def login_user(client: TestClient, email: str, password: str) -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.fixture(name="logged_in_admin")
def logged_in_admin_fixture(
    client: TestClient,
    admin: User,
) -> User:
    login_user(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    return admin


@pytest.fixture(name="logged_in_user")
def logged_in_user_fixture(
    client: TestClient,
    user: User,
) -> User:
    login_user(client, USER_EMAIL, USER_PASSWORD)
    return user


@pytest.fixture(name="account")
def finance_account(
    db: Session,
) -> Account:
    account = Account(name=FINANCE_ACCOUNT_NAME)
    db.add(account)
    db.commit()
    return account


@pytest.fixture(name="transaction")
def finance_transaction(
    db: Session,
) -> Transaction:
    transaction = Transaction(summary=FINANCE_TRANSACTION_SUMMARY)
    db.add(transaction)
    db.commit()
    return transaction


@pytest.fixture(name="line")
def finance_line(
    db: Session,
    account: Account,
    transaction: Transaction,
):
    line = Line(
        summary=FINANCE_LINE_SUMMARY,
        account_id=account.id,
        amount=FINANCE_LINE_AMOUNT,
        transaction_id=transaction.id,
    )
    db.add(line)
    db.commit()
    return line

from decimal import Decimal

from sqlalchemy import String
from sqlmodel import Field, SQLModel

from app.types import Currency


class AccountWrite(SQLModel):
    name: str = Field(sa_type=String(100))
    description: str = ""
    balance: Decimal = Field(default=Decimal(0), sa_type=Currency())
    active: bool = Field(default=True)


class AccountRead(AccountWrite):
    id: int | None = Field(default=None, primary_key=True)


class Account(AccountRead, table=True):
    __tablename__ = "finance_account"

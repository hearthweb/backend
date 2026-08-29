from datetime import datetime
from decimal import Decimal

from sqlalchemy import String
from sqlmodel import Field, Relationship, SQLModel

from app.finance.models.line import (
    Line,
    LineCreate,
    LinePublic,
)
from app.types import Currency, TZDateTime


class TransactionWrite(SQLModel):
    date: datetime = Field(sa_type=TZDateTime())
    summary: str = Field(sa_type=String(200))
    description: str = ""
    amount: Decimal = Field(default=Decimal(0), sa_type=Currency())


class TransactionCreate(SQLModel):
    transaction: TransactionWrite
    lines: list[LineCreate] = []


class TransactionRead(TransactionWrite):
    id: int | None = Field(default=None, primary_key=True)


class Transaction(TransactionRead, table=True):
    __tablename__ = "finance_transaction"

    lines: list[Line] = Relationship()


class TransactionPublic(TransactionRead):
    lines: list[LinePublic]

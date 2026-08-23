from decimal import Decimal

from sqlalchemy import String
from sqlmodel import Field, Relationship, SQLModel

from app.models.finance.account import Account, AccountRead
from app.models.finance.tag import Tag, TagRead, TagWrite
from app.models.finance.taglinelink import TagLineLink
from app.types import Currency


class LineWrite(SQLModel):
    summary: str = Field(sa_type=String(200))
    account_id: int = Field(foreign_key="account.id")
    transaction_id: int = Field(foreign_key="transaction.id")
    amount: Decimal = Field(sa_type=Currency())


class LineCreate(LineWrite):
    tags: list[TagWrite] = []


class LineRead(LineWrite):
    id: int | None = Field(default=None, primary_key=True)


class Line(LineRead, table=True):
    account: Account = Relationship(back_populates="lines")
    tags: list[Tag] = Relationship(
        back_populates="lines",
        link_model=TagLineLink,
    )


class LinePublic(LineRead):
    account: AccountRead
    tags: list[TagRead]

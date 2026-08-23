from decimal import Decimal

from sqlalchemy import String, event
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import Field, Relationship, SQLModel

from app.models.finance.account import Account, AccountRead
from app.models.finance.tag import Tag, TagRead
from app.models.finance.taglinelink import TagLineLink
from app.types import Currency


class LineBase(SQLModel):
    summary: str = Field(sa_type=String(200))
    account_id: int = Field(foreign_key="account.id")
    amount: Decimal = Field(Decimal(0), sa_type=Currency())


class LineWrite(LineBase):
    transaction_id: int = Field(foreign_key="transaction.id")


class LineCreate(LineBase):
    tags: list[str] = []


class LineRead(LineWrite):
    id: int | None = Field(default=None, primary_key=True)


class Line(LineRead, table=True):
    account: Account = Relationship()
    tags: list[Tag] = Relationship(link_model=TagLineLink)


class LinePublic(LineRead):
    account: AccountRead
    tags: list[TagRead]


@event.listens_for(Line, "mapper_configured")
def _set_active_history(mapper: Mapper[Line], cls: type[Line]):
    """
    In order to calculate deltas later, the original values for account_id,
    amount, and transaction_id need to be preserved.
    """

    cls.account_id.impl.active_history = True
    cls.amount.impl.active_history = True
    cls.transaction_id.impl.active_history = True

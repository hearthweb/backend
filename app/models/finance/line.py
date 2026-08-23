from decimal import Decimal

from sqlalchemy import String, event
from sqlalchemy.orm.attributes import get_history
from sqlalchemy.orm.mapper import Mapper
from sqlmodel import Field, Relationship, Session, SQLModel, update

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
    cls.account_id.impl.active_history = True
    cls.amount.impl.active_history = True


@event.listens_for(Session, "before_flush")
def _update_accounts_when_lines_change(session: Session, *args, **kwargs) -> None:
    """
    Whenever a line is created / deleted / modified, the associated account(s)
    need to be updated with the difference. This is trickier than it sounds
    because this can be triggered by a number of different things:

    - Creating or deleting a Line
    - Changing the amount of a Line
    - Changing the Account of a Line
    """

    deltas: dict[int, Decimal] = {}

    def add(id: int, diff: Decimal):
        deltas[id] = deltas.get(id, Decimal(0)) + diff

    # First, handle objects that have been added
    for obj in session.new:
        if isinstance(obj, Line):
            add(obj.account_id, obj.amount)

    # Secondly, handle objects that have been deleted
    for obj in session.deleted:
        if isinstance(obj, Line):
            add(obj.account_id, -obj.amount)

    # Thirdly, handle objects that have been modified (this is the tricky one)
    for obj in session.dirty:
        if not isinstance(obj, Line):
            continue
        hist_amount = get_history(obj, "amount")
        hist_id = get_history(obj, "account_id")
        prev_amount = hist_amount[0] if hist_amount.deleted else obj.amount
        prev_id = hist_id.deleted[0] if hist_id.deleted else obj.account_id
        if prev_id == obj.account_id:
            add(obj.account_id, obj.amount - prev_amount)
        else:
            add(prev_id, -prev_amount)
            add(obj.account_id, obj.amount)

    # Lastly, apply the deltas we calculated
    for id, delta in deltas.items():
        session.exec(
            update(Account)
            .where(Account.id == id)
            .values(balance=Account.balance + delta)
        )

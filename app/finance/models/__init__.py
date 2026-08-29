from decimal import Decimal

from sqlalchemy import event
from sqlalchemy.orm.attributes import get_history
from sqlmodel import Session, update

from .account import Account
from .line import Line
from .tag import Tag
from .taglinelink import TagLineLink
from .transaction import Transaction


@event.listens_for(Session, "before_flush")
def _update_accounts_when_lines_change(session: Session, *args, **kwargs) -> None:
    """
    Whenever a line is created / deleted / modified, the associated account(s)
    and transaction(s) need to be updated with the difference. This is
    trickier than it sounds because this can be triggered by a number of
    different things:

    - Creating or deleting a Line
    - Changing the amount of a Line
    - Changing the Account of a Line
    - Changing the Transaction of a Line
    """

    account_deltas: dict[int, Decimal] = {}
    transaction_deltas: dict[int, Decimal] = {}

    def add_account_delta(id: int, diff: Decimal):
        account_deltas[id] = account_deltas.get(id, Decimal(0)) + diff

    def add_transaction_delta(id: int, diff: Decimal):
        transaction_deltas[id] = transaction_deltas.get(id, Decimal(0)) + diff

    # First, handle objects that have been added
    for obj in session.new:
        if isinstance(obj, Line):
            add_account_delta(obj.account_id, obj.amount)
            add_transaction_delta(obj.transaction_id, obj.amount)

    # Secondly, handle objects that have been deleted
    for obj in session.deleted:
        if isinstance(obj, Line):
            add_account_delta(obj.account_id, -obj.amount)
            add_transaction_delta(obj.transaction_id, -obj.amount)

    def get_prev_value(obj: Line, attr: str):
        return next(iter(get_history(obj, attr).deleted), getattr(obj, attr))

    # Thirdly, handle objects that have been modified (this is the tricky one)
    for obj in session.dirty:
        if not isinstance(obj, Line):
            continue

        # Retrieve the previous values for the fields
        prev_account_id = get_prev_value(obj, "account_id")
        prev_amount = get_prev_value(obj, "amount")
        prev_transaction_id = get_prev_value(obj, "transaction_id")

        # Calculate the correct deltas to apply
        add_account_delta(prev_account_id, -prev_amount)
        add_account_delta(obj.account_id, obj.amount)
        add_transaction_delta(prev_transaction_id, -prev_amount)
        add_transaction_delta(obj.transaction_id, obj.amount)

    # Lastly, apply the deltas we calculated, skipping the ones with zero
    for id, delta in account_deltas.items():
        if delta != Decimal(0):
            session.exec(
                update(Account)
                .where(Account.id == id)
                .values(balance=Account.balance + delta)
            )
    for id, delta in transaction_deltas.items():
        if delta != Decimal(0):
            session.exec(
                update(Transaction)
                .where(Transaction.id == id)
                .values(amount=Transaction.amount + delta)
            )


__all__ = [
    "Account",
    "Line",
    "Tag",
    "TagLineLink",
    "Transaction",
]

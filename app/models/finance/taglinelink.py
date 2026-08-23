from sqlmodel import Field, SQLModel


class TagLineLink(SQLModel, table=True):
    __tablename__ = "finance_tag_line_link"

    tag_id: int | None = Field(
        default=None,
        foreign_key="finance_tag.id",
        primary_key=True,
    )
    line_id: int | None = Field(
        default=None,
        foreign_key="finance_line.id",
        primary_key=True,
    )

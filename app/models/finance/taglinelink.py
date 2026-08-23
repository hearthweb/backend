from sqlmodel import Field, SQLModel


class TagLineLink(SQLModel, table=True):
    tag_id: int | None = Field(
        default=None,
        foreign_key="tag.id",
        primary_key=True,
    )
    line_id: int | None = Field(
        default=None,
        foreign_key="line.id",
        primary_key=True,
    )

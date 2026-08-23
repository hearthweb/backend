from sqlalchemy import String
from sqlmodel import Field, Session, SQLModel, select


class TagWrite(SQLModel):
    name: str = Field(sa_type=String(40), index=True)
    color: str = Field(default="000000", sa_type=String(6))


class TagRead(TagWrite):
    id: int | None = Field(default=None, primary_key=True)


class Tag(TagRead, table=True):
    __tablename__ = "finance_tag"

    @staticmethod
    def get_or_create(db: Session, name: str) -> Tag:
        tag = db.exec(
            select(Tag).where(Tag.name == name),
        ).first()
        if tag is None:
            tag = Tag(name=name)
            db.add(Tag)
            db.flush()
        return tag

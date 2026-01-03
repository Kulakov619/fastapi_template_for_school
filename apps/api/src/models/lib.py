from datetime import datetime
from uuid import UUID

from db.annotations import str_50, str_255, uuidpk
from db.postgres import Base
from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Author(Base):
    __tablename__ = "lib_author"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Имя"
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Фамилия"
    )

    __table_args__ = (
        Index("lib_author_last_first_idx", "last_name", "first_name"),
    )

    def __repr__(self) -> str:
        return f"<Autor {self.last_name} {self.first_name}>"

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(primary_key=True)
    arxiv_id: Mapped[str] = mapped_column(String(32), unique=True)
    title: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

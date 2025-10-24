from typing import Optional

from sqlalchemy import DateTime, Index, Integer, String, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        Index('email', 'email', unique=True),
        Index('username', 'username', unique=True)
    )

    username: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('(utc_timestamp())'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('(utc_timestamp())'))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    is_admin: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    nickname: Mapped[Optional[str]] = mapped_column(String(50))
    avatar: Mapped[Optional[str]] = mapped_column(String(255))
    last_login_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    login_count: Mapped[Optional[int]] = mapped_column(Integer)

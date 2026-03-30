from sqlalchemy import Boolean, Column, Date, DateTime, Integer, Numeric, String, func
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserFilter(Base):
    __tablename__ = "user_filters"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(String, unique=True, nullable=False)
    format = Column(String, nullable=True)
    country = Column(String, nullable=True)
    rated_only = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    country = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    format = Column(String, nullable=False)
    source = Column(String, nullable=True)
    url = Column(String, nullable=True)
    fide_rated = Column(Boolean, nullable=False, default=False)
    entry_fee = Column(Numeric(10, 2), nullable=True)
    currency = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

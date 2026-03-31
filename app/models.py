from sqlalchemy import Boolean, Column, Date, DateTime, Integer, Numeric, String, func
from app.db import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList


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
    countries = Column(MutableList.as_mutable(JSONB), nullable=False, default=list)
    rated_only = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False, default="manual")
    source_event_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    country = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    format = Column(String, nullable=False)
    url = Column(String, nullable=True)
    fide_rated = Column(Boolean, nullable=False, default=False)
    entry_fee = Column(Numeric(10, 2), nullable=True)
    currency = Column(String, nullable=True)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class SourceConfig(Base):
    __tablename__ = "source_configs"

    id = Column(Integer, primary_key=True)
    source_type = Column(String, nullable=False)   # chess_results_federation
    source_code = Column(String, nullable=False)   # CYP, GRE
    is_enabled = Column(Boolean, nullable=False, default=True)
    limit_count = Column(Integer, nullable=False, default=20)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

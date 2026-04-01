from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from app.db import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList, MutableDict


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=True)
    onboarding_step = Column(String, nullable=True)
    onboarding_completed = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserFilter(Base):
    __tablename__ = "user_filters"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(String, unique=True, nullable=False)
    formats = Column(MutableList.as_mutable(JSONB), nullable=False, default=list)
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

class AppCache(Base):
    __tablename__ = "app_cache"

    id = Column(Integer, primary_key=True)
    cache_key = Column(String, unique=True, nullable=False)
    cache_value = Column(MutableDict.as_mutable(JSONB), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

class NotificationSetting(Base):
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(String, unique=True, nullable=False)

    is_enabled = Column(Boolean, nullable=False, default=False)
    delivery_hour = Column(Integer, nullable=False, default=9)
    timezone = Column(String, nullable=False, default="UTC")

    last_sent_date = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"

    id = Column(Integer, primary_key=True)

    telegram_user_id = Column(String, nullable=False)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)

    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    delivery_date = Column(Date, nullable=False)

    status = Column(String, nullable=False, default="sent")
    error_message = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("telegram_user_id", "tournament_id", name="uq_notification_user_tournament"),
    )

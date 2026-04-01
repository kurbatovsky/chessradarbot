from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.db import SessionLocal
from app.models import NotificationSetting


DEFAULT_TIMEZONE = "UTC"
DEFAULT_DELIVERY_HOUR = 9


def _normalize_timezone(value: str | None) -> str:
    if not value:
        return DEFAULT_TIMEZONE
    value = value.strip()
    try:
        ZoneInfo(value)
        return value
    except ZoneInfoNotFoundError:
        return DEFAULT_TIMEZONE


def _normalize_hour(value: int | None) -> int:
    if value is None:
        return DEFAULT_DELIVERY_HOUR
    if value < 0:
        return 0
    if value > 23:
        return 23
    return value


def _get_or_create(session, user_id: int | str) -> NotificationSetting:
    telegram_user_id = str(user_id)

    row = (
        session.query(NotificationSetting)
        .filter(NotificationSetting.telegram_user_id == telegram_user_id)
        .first()
    )
    if row:
        return row

    row = NotificationSetting(
        telegram_user_id=telegram_user_id,
        is_enabled=False,
        delivery_hour=DEFAULT_DELIVERY_HOUR,
        timezone=DEFAULT_TIMEZONE,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def get_notification_settings(user_id: int | str) -> dict:
    session = SessionLocal()
    try:
        row = _get_or_create(session, user_id)
        return {
            "telegram_user_id": row.telegram_user_id,
            "is_enabled": row.is_enabled,
            "delivery_hour": row.delivery_hour,
            "timezone": row.timezone,
            "last_sent_date": row.last_sent_date,
        }
    finally:
        session.close()


def save_notification_settings(
    user_id: int | str,
    *,
    is_enabled: bool | None = None,
    delivery_hour: int | None = None,
    timezone: str | None = None,
) -> None:
    session = SessionLocal()
    try:
        row = _get_or_create(session, user_id)

        if is_enabled is not None:
            row.is_enabled = is_enabled

        if delivery_hour is not None:
            row.delivery_hour = _normalize_hour(delivery_hour)

        if timezone is not None:
            row.timezone = _normalize_timezone(timezone)

        session.commit()
    finally:
        session.close()


def mark_notifications_sent(user_id: int | str, delivery_date) -> None:
    session = SessionLocal()
    try:
        row = _get_or_create(session, user_id)
        row.last_sent_date = delivery_date
        session.commit()
    finally:
        session.close()


def list_enabled_notification_settings() -> list[NotificationSetting]:
    session = SessionLocal()
    try:
        rows = (
            session.query(NotificationSetting)
            .filter(NotificationSetting.is_enabled.is_(True))
            .all()
        )

        # Отсоединяем объекты перед закрытием сессии
        result = list(rows)
        for row in result:
            session.expunge(row)
        return result
    finally:
        session.close()

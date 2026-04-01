from datetime import date

from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.models import NotificationDelivery


def get_sent_tournament_ids(user_id) -> set:
    session = SessionLocal()
    try:
        rows = (
            session.query(NotificationDelivery.tournament_id)
            .filter(NotificationDelivery.telegram_user_id == str(user_id))
            .all()
        )
        return {row[0] for row in rows}
    finally:
        session.close()


def create_delivery_records(
    user_id,
    tournament_ids,
    delivery_date: date,
) -> None:
    if not tournament_ids:
        return

    session = SessionLocal()
    try:
        for tournament_id in tournament_ids:
            session.add(
                NotificationDelivery(
                    telegram_user_id=str(user_id),
                    tournament_id=tournament_id,
                    delivery_date=delivery_date,
                    status="sent",
                )
            )
        session.commit()
    except IntegrityError:
        session.rollback()
        # Если cron случайно запустился повторно, unique constraint нас защитит.
    finally:
        session.close()

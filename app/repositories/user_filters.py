from app.db import SessionLocal
from app.models import UserFilter


def get_user_filters(user_id):
    session = SessionLocal()

    db_filter = (
        session.query(UserFilter)
        .filter(UserFilter.telegram_user_id == str(user_id))
        .first()
    )

    if not db_filter:
        db_filter = UserFilter(
            telegram_user_id=str(user_id),
            format=None,
            country=None,
            rated_only=False,
        )
        session.add(db_filter)
        session.commit()
        session.refresh(db_filter)

    result = {
        "format": db_filter.format,
        "country": db_filter.country,
        "rated_only": db_filter.rated_only,
    }

    session.close()
    return result


def save_user_filters(user_id, format_value=None, country_value=None, rated_only=None):
    session = SessionLocal()

    db_filter = (
        session.query(UserFilter)
        .filter(UserFilter.telegram_user_id == str(user_id))
        .first()
    )

    if not db_filter:
        db_filter = UserFilter(
            telegram_user_id=str(user_id),
            format=None,
            country=None,
            rated_only=False,
        )
        session.add(db_filter)
        session.commit()
        session.refresh(db_filter)

    if format_value is not None:
        db_filter.format = format_value

    if country_value is not None:
        db_filter.country = country_value

    if rated_only is not None:
        db_filter.rated_only = rated_only

    session.commit()
    session.close()


def clear_user_filters(user_id):
    session = SessionLocal()

    db_filter = (
        session.query(UserFilter)
        .filter(UserFilter.telegram_user_id == str(user_id))
        .first()
    )

    if not db_filter:
        db_filter = UserFilter(
            telegram_user_id=str(user_id),
            format=None,
            country=None,
            rated_only=False,
        )
        session.add(db_filter)
    else:
        db_filter.format = None
        db_filter.country = None
        db_filter.rated_only = False

    session.commit()
    session.close()
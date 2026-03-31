from app.db import SessionLocal
from app.models import UserFilter


def _normalize_country(country: str) -> str:
    return country.strip().lower()


def _get_or_create_user_filter(session, user_id: int) -> UserFilter:
    db_filter = (
        session.query(UserFilter)
        .filter(UserFilter.telegram_user_id == str(user_id))
        .first()
    )

    if not db_filter:
        db_filter = UserFilter(
            telegram_user_id=str(user_id),
            formats=[],        # ← новое поле
            countries=[],
            rated_only=False,
        )
        session.add(db_filter)
        session.commit()
        session.refresh(db_filter)

    return db_filter


def _extract_countries(db_filter: UserFilter) -> list[str]:
    if db_filter.countries:
        return sorted({_normalize_country(c) for c in db_filter.countries})
    return []


def get_user_filters(user_id: int) -> dict:
    session = SessionLocal()
    try:
        db_filter = _get_or_create_user_filter(session, user_id)

        return {
            "formats": db_filter.formats or [],
            "countries": _extract_countries(db_filter),
            "fide_rated": db_filter.rated_only,
        }
    finally:
        session.close()


def save_user_filters(
    user_id: int,
    formats_value=None,
    countries_value=None,
    rated_only=None,
) -> None:
    session = SessionLocal()
    try:
        db_filter = _get_or_create_user_filter(session, user_id)

        if formats_value is not None:
            db_filter.formats = formats_value

        if countries_value is not None:
            normalized = sorted({_normalize_country(c) for c in countries_value})
            db_filter.countries = normalized

        if rated_only is not None:
            db_filter.rated_only = rated_only

        session.commit()
    finally:
        session.close()


# --- FORMAT TOGGLE ---

def toggle_user_format(user_id: int, format_value: str) -> list[str]:
    session = SessionLocal()
    try:
        db_filter = _get_or_create_user_filter(session, user_id)

        formats = list(db_filter.formats or [])

        if format_value in formats:
            formats.remove(format_value)
        else:
            formats.append(format_value)

        formats = sorted(set(formats))
        db_filter.formats = formats

        session.commit()
        return formats
    finally:
        session.close()


def clear_user_formats(user_id: int) -> None:
    session = SessionLocal()
    try:
        db_filter = _get_or_create_user_filter(session, user_id)
        db_filter.formats = []
        session.commit()
    finally:
        session.close()


# --- COUNTRIES (оставляем как есть) ---

def toggle_user_country(user_id: int, country: str) -> list[str]:
    session = SessionLocal()
    try:
        db_filter = _get_or_create_user_filter(session, user_id)

        normalized_country = _normalize_country(country)
        countries = _extract_countries(db_filter)

        if normalized_country in countries:
            countries.remove(normalized_country)
        else:
            countries.append(normalized_country)

        countries = sorted(set(countries))
        db_filter.countries = countries

        session.commit()
        return countries
    finally:
        session.close()


def clear_user_countries(user_id: int) -> None:
    session = SessionLocal()
    try:
        db_filter = _get_or_create_user_filter(session, user_id)
        db_filter.countries = []
        session.commit()
    finally:
        session.close()


def clear_user_filters(user_id: int) -> None:
    session = SessionLocal()
    try:
        db_filter = _get_or_create_user_filter(session, user_id)

        db_filter.formats = []
        db_filter.countries = []
        db_filter.rated_only = False

        session.commit()
    finally:
        session.close()
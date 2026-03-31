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
            format=None,
            country=None,     # старое поле
            countries=None,   # новое поле пока может быть None до миграции
            rated_only=False,
        )
        session.add(db_filter)
        session.commit()
        session.refresh(db_filter)

    return db_filter


def _extract_countries(db_filter: UserFilter) -> list[str]:
    # 1. если новое поле уже заполнено — используем его
    if db_filter.countries:
        return sorted({_normalize_country(country) for country in db_filter.countries})

    # 2. fallback на старое поле
    if db_filter.country:
        return [_normalize_country(db_filter.country)]

    # 3. по умолчанию пустой список
    return []


def get_user_filters(user_id: int) -> dict:
    session = SessionLocal()
    try:
        db_filter = _get_or_create_user_filter(session, user_id)

        return {
            "format": db_filter.format,
            "countries": _extract_countries(db_filter),
            "rated_only": db_filter.rated_only,
        }
    finally:
        session.close()


def save_user_filters(
    user_id: int,
    format_value=None,
    countries_value=None,
    rated_only=None,
) -> None:
    session = SessionLocal()
    try:
        db_filter = _get_or_create_user_filter(session, user_id)

        if format_value is not None:
            db_filter.format = format_value

        if countries_value is not None:
            normalized = sorted({_normalize_country(country) for country in countries_value})
            db_filter.countries = normalized

            # временно синхронизируем старое поле, чтобы переход был мягкий
            db_filter.country = normalized[0] if len(normalized) == 1 else None

        if rated_only is not None:
            db_filter.rated_only = rated_only

        session.commit()
    finally:
        session.close()


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

        # временная обратная совместимость
        db_filter.country = countries[0] if len(countries) == 1 else None

        session.commit()
        return countries
    finally:
        session.close()


def clear_user_countries(user_id: int) -> None:
    session = SessionLocal()
    try:
        db_filter = _get_or_create_user_filter(session, user_id)
        db_filter.countries = []
        db_filter.country = None
        session.commit()
    finally:
        session.close()


def clear_user_filters(user_id: int) -> None:
    session = SessionLocal()
    try:
        db_filter = _get_or_create_user_filter(session, user_id)
        db_filter.format = None
        db_filter.countries = []
        db_filter.country = None
        db_filter.rated_only = False
        session.commit()
    finally:
        session.close()
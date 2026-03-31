from app.db import SessionLocal
from app.models import AppCache


def get_cache_value(cache_key: str, default=None):
    session = SessionLocal()
    try:
        row = (
            session.query(AppCache)
            .filter(AppCache.cache_key == cache_key)
            .first()
        )
        if not row:
            return default
        return row.cache_value
    finally:
        session.close()


def set_cache_value(cache_key: str, cache_value) -> None:
    session = SessionLocal()
    try:
        row = (
            session.query(AppCache)
            .filter(AppCache.cache_key == cache_key)
            .first()
        )

        if not row:
            row = AppCache(
                cache_key=cache_key,
                cache_value=cache_value,
            )
            session.add(row)
        else:
            row.cache_value = cache_value

        session.commit()
    finally:
        session.close()

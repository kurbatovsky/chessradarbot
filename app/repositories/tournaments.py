from datetime import date
from sqlalchemy import func

from app.db import SessionLocal
from app.models import Tournament


def load_tournaments():
    session = SessionLocal()

    tournaments = (
        session.query(Tournament)
        .filter(Tournament.end_date >= date.today())
        .order_by(Tournament.start_date.asc())
        .all()
    )

    result = []
    for t in tournaments:
        result.append(
            {
                "name": t.name,
                "location": t.location,
                "country": t.country,
                "start_date": t.start_date.isoformat() if t.start_date else None,
                "end_date": t.end_date.isoformat() if t.end_date else None,
                "format": t.format,
                "source": t.source,
                "url": t.url,
                "fide_rated": t.fide_rated,
                "entry_fee": float(t.entry_fee) if t.entry_fee is not None else None,
                "currency": t.currency,
            }
        )

    session.close()
    return result

def get_popular_countries(limit: int = 10) -> list[str]:
    session = SessionLocal()
    try:
        rows = (
            session.query(Tournament.country, func.count(Tournament.id).label("tournament_count"))
            .filter(Tournament.end_date >= date.today())
            .group_by(Tournament.country)
            .order_by(func.count(Tournament.id).desc(), Tournament.country.asc())
            .limit(limit)
            .all()
        )

        return [row[0] for row in rows if row[0]]
    finally:
        session.close()
from datetime import date

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
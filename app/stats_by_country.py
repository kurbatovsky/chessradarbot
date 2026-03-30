from sqlalchemy import func

from app.db import SessionLocal
from app.models import Tournament


def main():
    session = SessionLocal()

    results = (
        session.query(
            func.lower(Tournament.country).label("country"),
            func.count(Tournament.id).label("count"),
        )
        .group_by(func.lower(Tournament.country))
        .order_by(func.count(Tournament.id).desc())
        .all()
    )

    print("\n=== TOURNAMENTS BY COUNTRY ===\n")

    for country, count in results:
        print(f"{country or 'unknown'}: {count}")

    print("\nTotal countries:", len(results))

    session.close()


if __name__ == "__main__":
    main()
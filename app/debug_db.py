from app.db import SessionLocal
from app.models import Tournament


def main():
    session = SessionLocal()

    tournaments = session.query(Tournament).order_by(Tournament.start_date).all()

    print("\n=== TOURNAMENTS IN DB ===\n")

    for t in tournaments:
        print(
            {
                "id": t.id,
                "name": t.name,
                "start_date": str(t.start_date),
                "end_date": str(t.end_date),
                "source": t.source,
            }
        )

    print(f"\nTotal: {len(tournaments)}\n")

    session.close()


if __name__ == "__main__":
    main()
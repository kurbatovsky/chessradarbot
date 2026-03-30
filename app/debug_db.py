from app.db import SessionLocal
from app.models import Tournament


def main():
    session = SessionLocal()

    tournaments = session.query(Tournament).order_by(Tournament.start_date).all()

    print("\n=== TOURNAMENTS IN DB ===\n")

    for t in tournaments:
        print(f"""
ID: {t.id}
Name: {t.name}
Country: {t.country}
Location: {t.location}
Date: {t.start_date} → {t.end_date}
Source: {t.source}
------------------------
""")

    print(f"\nTotal: {len(tournaments)}\n")

    session.close()


if __name__ == "__main__":
    main()

import json
from datetime import datetime

from app.db import SessionLocal
from app.models import Tournament


def main():
    session = SessionLocal()

    with open("data/tournaments.json", "r", encoding="utf-8") as file:
        tournaments = json.load(file)

    session.query(Tournament).delete()

    for index, item in enumerate(tournaments, start=1):
        source = item.get("source", "manual")
        source_event_id = item.get("source_event_id", f"{source}-{index}")

        tournament = Tournament(
            source=source,
            source_event_id=source_event_id,
            name=item["name"],
            location=item["location"],
            country=item["country"],
            start_date=datetime.strptime(item["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(item["end_date"], "%Y-%m-%d").date(),
            format=item["format"],
            url=item.get("url"),
            fide_rated=item.get("fide_rated", False),
            entry_fee=item.get("entry_fee"),
            currency=item.get("currency"),
        )
        session.add(tournament)

    session.commit()
    session.close()

    print("Tournaments imported successfully.")


if __name__ == "__main__":
    main()
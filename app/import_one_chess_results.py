from datetime import datetime

from app.db import SessionLocal
from app.models import Tournament
from app.sources.chess_results import parse_tournament_page

URL = "https://chess-results.com/tnr1371006.aspx"


def main():
    data = parse_tournament_page(URL)

    if not data["start_date"] or not data["end_date"]:
        raise RuntimeError("Could not parse start/end dates")

    session = SessionLocal()

    existing = (
        session.query(Tournament)
        .filter(Tournament.source == data["source"])
        .filter(Tournament.source_event_id == data["source_event_id"])
        .first()
    )

    if existing:
        existing.name = data["name"]
        existing.location = data["location"]
        existing.country = data["country"]
        existing.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        existing.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        existing.format = data["format"]
        existing.url = data["url"]
        existing.fide_rated = data["fide_rated"]
        existing.entry_fee = data["entry_fee"]
        existing.currency = data["currency"]
        print("Updated existing tournament")
    else:
        tournament = Tournament(
            source=data["source"],
            source_event_id=data["source_event_id"],
            name=data["name"],
            location=data["location"],
            country=data["country"],
            start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date(),
            format=data["format"],
            url=data["url"],
            fide_rated=data["fide_rated"],
            entry_fee=data["entry_fee"],
            currency=data["currency"],
        )
        session.add(tournament)
        print("Inserted new tournament")

    session.commit()
    session.close()


if __name__ == "__main__":
    main()

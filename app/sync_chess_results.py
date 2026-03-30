from datetime import datetime, date

from app.db import SessionLocal
from app.models import Tournament
from app.sources.chess_results import parse_federation_page, parse_tournament_page
from app.get_enabled_sources import get_enabled_chess_results_federations


def upsert_tournament(session, data):
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
        return "updated"

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
    return "inserted"


def is_old_tournament(data):
    if not data["end_date"]:
        return False

    end_dt = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    return end_dt < date.today()


def collect_urls():
    configs = get_enabled_chess_results_federations()

    all_urls = []
    seen = set()

    for config in configs:
        fed = config["source_code"]
        limit_count = config["limit_count"]

        print(f"Fetching federation {fed} with limit {limit_count}")

        urls = parse_federation_page(fed=fed, limit=limit_count)

        for url in urls:
            if url not in seen:
                seen.add(url)
                all_urls.append(url)

    return all_urls


def main():
    session = SessionLocal()

    urls = collect_urls()

    inserted = 0
    updated = 0
    skipped_old = 0
    failed = 0

    print(f"\nCollected {len(urls)} unique URLs\n")

    for url in urls:
        print(f"Processing: {url}")

        try:
            data = parse_tournament_page(url)

            if not data["start_date"] or not data["end_date"]:
                raise RuntimeError("Missing start_date or end_date")

            if is_old_tournament(data):
                skipped_old += 1
                print(f"  SKIPPED OLD: {data['name']}")
                continue

            result = upsert_tournament(session, data)
            session.commit()

            if result == "inserted":
                inserted += 1
            else:
                updated += 1

            print(f"  OK: {result} -> {data['name']}")

        except Exception as e:
            session.rollback()
            failed += 1
            print(f"  ERROR: {e}")

    session.close()

    print("\n=== DAILY SYNC SUMMARY ===")
    print(f"Inserted: {inserted}")
    print(f"Updated: {updated}")
    print(f"Skipped old: {skipped_old}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
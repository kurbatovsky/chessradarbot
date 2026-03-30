from app.db import SessionLocal
from app.models import Tournament


def main():
    session = SessionLocal()

    deleted = session.query(Tournament).filter(
        Tournament.id != 9
    ).delete()

    session.commit()
    session.close()

    print(f"Deleted {deleted} tournaments (kept ID=9)")


if __name__ == "__main__":
    main()

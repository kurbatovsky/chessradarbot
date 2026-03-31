from app.db import SessionLocal
from app.models import UserFilter


def main() -> None:
    session = SessionLocal()
    try:
        rows = session.query(UserFilter).all()
        for row in rows:
            print(
                f"user={row.telegram_user_id} "
                f"formats={getattr(row, 'formats', None)} "
                f"countries={row.countries} "
                f"rated_only={row.rated_only}"
            )
    finally:
        session.close()


if __name__ == "__main__":
    main()

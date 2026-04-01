from sqlalchemy import text

from app.db import SessionLocal, engine
from app.models import User


def main():
    print("ENGINE URL:", engine.url)

    session = SessionLocal()
    try:
        orm_users = session.query(User).all()
        print("ORM USERS COUNT:", len(orm_users))

        raw_rows = session.execute(text("SELECT * FROM users")).fetchall()
        print("RAW USERS COUNT:", len(raw_rows))

        if raw_rows:
            print("FIRST RAW ROW:", raw_rows[0])

    finally:
        session.close()


if __name__ == "__main__":
    main()

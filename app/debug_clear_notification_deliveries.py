from app.db import SessionLocal
from app.models import NotificationDelivery


def main():
    user_id = "185093"

    session = SessionLocal()
    try:
        deleted = (
            session.query(NotificationDelivery)
            .filter(NotificationDelivery.telegram_user_id == user_id)
            .delete()
        )
        session.commit()
        print(f"Deleted deliveries: {deleted}")
    finally:
        session.close()


if __name__ == "__main__":
    main()

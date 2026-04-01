import sys
from app.db import SessionLocal
from app.models import (
    Tournament,
    UserFilter,
    User,
    NotificationSetting,
    NotificationDelivery,
)


def print_tournaments(session):
    print("\n=== TOURNAMENTS ===\n")
    for t in session.query(Tournament).all():
        print(t.id, t.name)


def print_notification_settings(session):
    print("\n=== NOTIFICATION SETTINGS ===\n")
    for s in session.query(NotificationSetting).all():
        print(
            {
                "user": s.telegram_user_id,
                "enabled": s.is_enabled,
                "hour": s.delivery_hour,
                "tz": s.timezone,
            }
        )


def print_notification_deliveries(session):
    print("\n=== DELIVERIES ===\n")
    for d in session.query(NotificationDelivery).all():
        print(
            {
                "user": d.telegram_user_id,
                "tournament_id": d.tournament_id,
                "date": d.delivery_date,
            }
        )

def print_users(session):
    users = session.query(User).all()

    print("\n=== USERS ===\n")
    print("COUNT:", len(users))

    for u in users:
        print("ROW OBJECT:", u)
        print("telegram_user_id:", u.telegram_user_id)
        print("username:", getattr(u, "username", None))
        print("created_at:", getattr(u, "created_at", None))
        print("---")


def main():
    from app.db import SessionLocal, engine
    from app.models import User
    print("ENGINE URL:", engine.url)
    session = SessionLocal()
    try:
        arg = sys.argv[1] if len(sys.argv) > 1 else "all"

        if arg == "tournaments":
            print_tournaments(session)

        elif arg == "settings":
            print_notification_settings(session)

        elif arg == "deliveries":
            print_notification_deliveries(session)

        elif arg == "users":
            print_users(session)

        else:
            print("Usage:")
            print("  python -m app.debug_db tournaments")
            print("  python -m app.debug_db settings")
            print("  python -m app.debug_db deliveries")

    finally:
        session.close()


if __name__ == "__main__":
    main()
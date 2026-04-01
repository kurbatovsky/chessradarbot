from datetime import datetime
from zoneinfo import ZoneInfo

from app.db import SessionLocal
from app.models import NotificationSetting
from app.repositories.notification_settings import save_notification_settings


def reset_last_sent(user_id) -> None:
    session = SessionLocal()
    try:
        row = (
            session.query(NotificationSetting)
            .filter(NotificationSetting.telegram_user_id == str(user_id))
            .first()
        )

        if row is not None:
            row.last_sent_date = None
            session.commit()
    finally:
        session.close()


def main():
    user_id = 185093  # замени на свой telegram user id

    now = datetime.now(ZoneInfo("Europe/Nicosia"))
    current_hour = now.hour

    save_notification_settings(
        user_id=user_id,
        is_enabled=True,
        delivery_hour=current_hour,
        timezone="Europe/Nicosia",
    )

    reset_last_sent(user_id)

    print("Notification settings saved.")
    print("user_id =", user_id)
    print("delivery_hour =", current_hour)
    print("timezone = Europe/Nicosia")
    print("last_sent_date reset to None")


if __name__ == "__main__":
    main()

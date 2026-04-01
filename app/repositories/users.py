from app.db import SessionLocal
from app.models import User


def get_or_create_user(telegram_user_id: int | str, username: str | None = None) -> dict:
    session = SessionLocal()
    try:
        telegram_user_id = str(telegram_user_id)

        user = (
            session.query(User)
            .filter(User.telegram_user_id == telegram_user_id)
            .first()
        )

        if user is None:
            user = User(
                telegram_user_id=telegram_user_id,
                username=username,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        else:
            updated = False

            if username != user.username:
                user.username = username
                updated = True

            if updated:
                session.commit()
                session.refresh(user)

        return {
            "id": user.id,
            "telegram_user_id": user.telegram_user_id,
            "username": user.username,
            "created_at": user.created_at,
        }
    finally:
        session.close()

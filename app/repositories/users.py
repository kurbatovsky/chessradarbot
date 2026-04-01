from app.db import SessionLocal
from app.models import User


def _serialize_user(user):
    return {
        "id": user.id,
        "telegram_user_id": user.telegram_user_id,
        "username": user.username,
        "onboarding_step": user.onboarding_step,
        "onboarding_completed": user.onboarding_completed,
        "created_at": user.created_at,
    }


def get_or_create_user(telegram_user_id, username=None):
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
                onboarding_step=None,
                onboarding_completed=False,
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

        return _serialize_user(user)
    finally:
        session.close()


def get_user(telegram_user_id):
    session = SessionLocal()

    try:
        telegram_user_id = str(telegram_user_id)

        user = (
            session.query(User)
            .filter(User.telegram_user_id == telegram_user_id)
            .first()
        )

        if user is None:
            return None

        return _serialize_user(user)
    finally:
        session.close()


def save_onboarding_state(
    telegram_user_id,
    onboarding_step=None,
    onboarding_completed=None,
):
    session = SessionLocal()

    try:
        telegram_user_id = str(telegram_user_id)

        user = (
            session.query(User)
            .filter(User.telegram_user_id == telegram_user_id)
            .first()
        )

        if user is None:
            return None

        if onboarding_step is not None:
            user.onboarding_step = onboarding_step

        if onboarding_completed is not None:
            user.onboarding_completed = onboarding_completed

        session.commit()
        session.refresh(user)

        return _serialize_user(user)
    finally:
        session.close()


def reset_onboarding(telegram_user_id):
    return save_onboarding_state(
        telegram_user_id=telegram_user_id,
        onboarding_step="welcome",
        onboarding_completed=False,
    )


def complete_onboarding(telegram_user_id):
    session = SessionLocal()

    try:
        telegram_user_id = str(telegram_user_id)

        user = (
            session.query(User)
            .filter(User.telegram_user_id == telegram_user_id)
            .first()
        )

        if user is None:
            return None

        user.onboarding_step = None
        user.onboarding_completed = True

        session.commit()
        session.refresh(user)

        return _serialize_user(user)
    finally:
        session.close()
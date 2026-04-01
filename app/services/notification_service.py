from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.repositories.notification_deliveries import (
    create_delivery_records,
    get_sent_tournament_ids,
)
from app.repositories.notification_settings import (
    get_notification_settings,
    list_enabled_notification_settings,
    mark_notifications_sent,
)
from app.repositories.tournaments import load_tournaments_for_notifications
from app.repositories.user_filters import get_user_filters
from app.services.notification_matcher import matches_tournament
from app.services.notification_sender import send_notification_message


def _is_user_due(setting, now_utc: datetime) -> tuple[bool, datetime]:
    user_tz = ZoneInfo(setting.timezone)
    local_now = now_utc.astimezone(user_tz)

    if local_now.hour != setting.delivery_hour:
        return False, local_now

    if setting.last_sent_date == local_now.date():
        return False, local_now

    return True, local_now


def _select_new_matching_tournaments(
    user_id: int | str,
    user_filters: dict,
    tournaments: list[dict],
) -> list[dict]:
    sent_ids = get_sent_tournament_ids(user_id)

    results = []
    for tournament in tournaments:
        tournament_id = tournament.get("id")
        if tournament_id in sent_ids:
            continue

        if matches_tournament(tournament, user_filters):
            results.append(tournament)

    return results


async def process_due_users() -> None:
    now_utc = datetime.now(timezone.utc)
    tournaments = load_tournaments_for_notifications()
    settings = list_enabled_notification_settings()

    for setting in settings:
        is_due, local_now = _is_user_due(setting, now_utc)
        if not is_due:
            continue

        user_id = setting.telegram_user_id
        user_filters = get_user_filters(int(user_id))
        matched = _select_new_matching_tournaments(user_id, user_filters, tournaments)

        if not matched:
            mark_notifications_sent(user_id, local_now.date())
            print(f"[SKIP] user={user_id}: no new tournaments")
            continue

        try:
            await send_notification_message(user_id, matched)
            create_delivery_records(
                user_id=user_id,
                tournament_ids=[t["id"] for t in matched],
                delivery_date=local_now.date(),
            )
            mark_notifications_sent(user_id, local_now.date())
            print(f"[OK] user={user_id}: sent {len(matched)} tournaments")
        except Exception as exc:
            print(f"[ERROR] user={user_id}: {exc}")

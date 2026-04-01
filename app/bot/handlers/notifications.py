from telegram import Update
from telegram.ext import ContextTypes

from app.bot.ui.keyboards import (
    get_notification_keyboard,
    get_notification_hour_keyboard,
    get_notification_timezone_keyboard,
    get_extended_notification_timezone_keyboard,
)
from app.core.constants import (
    TIMEZONE_OTHER_CALLBACK,
    TIMEZONE_BACK_TO_POPULAR_CALLBACK,
)
from app.repositories.notification_settings import (
    get_notification_settings,
    save_notification_settings,
)

def _build_notification_settings_text(settings):
    return (
        "🔔 Notifications\n\n"
        "Status: %s\n"
        "Time: %02d:00\n"
        "Time zone: %s\n\n"
        "Here you can manage notifications about new tournaments."
    ) % (
        "ON" if settings["is_enabled"] else "OFF",
        settings["delivery_hour"],
        settings["timezone"],
    )

async def show_notification_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    user_id = user.id
    settings = get_notification_settings(user_id)

    await message.reply_text(
        _build_notification_settings_text(settings),
        reply_markup=get_notification_keyboard(settings["is_enabled"]),
    )

async def handle_notification_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.data or not query.from_user:
        return

    await query.answer()

    user_id = query.from_user.id
    data = query.data
    settings = get_notification_settings(user_id)

    if data == "notif_toggle":
        new_state = not settings["is_enabled"]
        save_notification_settings(
            user_id=user_id,
            is_enabled=new_state,
        )
        settings = get_notification_settings(user_id)

        await query.edit_message_text(
            text=_build_notification_settings_text(settings),
            reply_markup=get_notification_keyboard(settings["is_enabled"]),
        )
        return

    if data == "notif_set_time":
        await show_notification_hour_selector(query, user_id)
        return

    if data == "notif_set_timezone":
        await show_notification_timezone_selector(query, user_id)
        return

    if data.startswith("notif_hour:"):
        try:
            hour = int(data.split(":")[1])
        except (IndexError, ValueError):
            return

        save_notification_settings(
            user_id=user_id,
            delivery_hour=hour,
        )
        settings = get_notification_settings(user_id)

        await query.edit_message_text(
            text=(
                "✅ Got it — I’ll send notifications at %02d:00\n"
                "Time zone: %s"
            ) % (
                settings["delivery_hour"],
                settings["timezone"],
            ),
            reply_markup=get_notification_keyboard(settings["is_enabled"]),
        )
        return

    if data.startswith("notif_timezone:"):
        timezone = data.split(":", 1)[1]

        if timezone == TIMEZONE_OTHER_CALLBACK:
            await show_extended_notification_timezone_selector(query, user_id)
            return

        if timezone == TIMEZONE_BACK_TO_POPULAR_CALLBACK:
            await show_notification_timezone_selector(query, user_id)
            return

        save_notification_settings(
            user_id=user_id,
            timezone=timezone,
        )
        settings = get_notification_settings(user_id)

        await query.edit_message_text(
            text=(
                "✅ Time zone updated.\n\n"
                "Current schedule: %02d:00 (%s)"
            ) % (
                settings["delivery_hour"],
                settings["timezone"],
            ),
            reply_markup=get_notification_keyboard(settings["is_enabled"]),
        )
        return

    if data == "notif_back_to_settings":
        settings = get_notification_settings(user_id)

        await query.edit_message_text(
            text=_build_notification_settings_text(settings),
            reply_markup=get_notification_keyboard(settings["is_enabled"]),
        )
        return

    if data == "notif_back":
        await query.edit_message_text("Back to menu.")
        return
             
async def show_notification_hour_selector(query, user_id, back_callback="notif_back_to_settings"):
    settings = get_notification_settings(user_id)
    current_hour = settings["delivery_hour"]

    await query.edit_message_text(
        text=(
            "⏰ When should I send notifications about new tournaments?\n\n"
            "Choose the hour in your local time."
        ),
        reply_markup=get_notification_hour_keyboard(
            selected_hour=current_hour,
            back_callback=back_callback,
        ),
    )

async def show_notification_timezone_selector(query, user_id, back_callback="notif_back_to_settings"):
    settings = get_notification_settings(user_id)
    current_timezone = settings["timezone"]

    await query.edit_message_text(
        text=(
            "🌍 Choose your time zone.\n\n"
            "This will be used for notification delivery time."
        ),
        reply_markup=get_notification_timezone_keyboard(
            selected_timezone=current_timezone,
            back_callback=back_callback,
        ),
    )

async def show_extended_notification_timezone_selector(query, user_id, back_callback="notif_back_to_settings"):
    settings = get_notification_settings(user_id)
    current_timezone = settings["timezone"]

    await query.edit_message_text(
        text=(
            "🌍 More time zones\n\n"
            "Choose your time zone from the extended list."
        ),
        reply_markup=get_extended_notification_timezone_keyboard(
            selected_timezone=current_timezone,
            back_callback=back_callback,
        ),
    )

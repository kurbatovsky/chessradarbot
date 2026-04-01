from telegram import Update
from telegram.ext import ContextTypes

from app.repositories.notification_settings import get_notification_settings, save_notification_settings
from app.bot.ui.keyboards import get_notification_keyboard


from telegram import Update
from telegram.ext import ContextTypes

from app.bot.ui.keyboards import (
    get_main_keyboard,
    get_notification_keyboard,
    get_notification_hour_keyboard,
)
from app.repositories.notification_settings import (
    get_notification_settings,
    save_notification_settings,
)


async def show_notification_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    user_id = user.id
    settings = get_notification_settings(user_id)

    enabled = settings["is_enabled"]
    hour = settings["delivery_hour"]
    timezone = settings["timezone"]

    text = (
        "🔔 <b>Notifications</b>\n\n"
        f"Status: {'ON' if enabled else 'OFF'}\n"
        f"Time: {hour:02d}:00\n"
        f"Time zone: {timezone}\n\n"
        "Here you can manage notifications about new tournaments."
    )

    await message.reply_text(
        text,
        reply_markup=get_notification_keyboard(enabled),
        parse_mode="HTML",
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

        text = (
            "🔔 <b>Notifications</b>\n\n"
            f"Status: {'ON' if settings['is_enabled'] else 'OFF'}\n"
            f"Time: {settings['delivery_hour']:02d}:00\n"
            f"Time zone: {settings['timezone']}\n\n"
            "Here you can manage notifications about new tournaments."
        )

        await query.edit_message_text(
            text=text,
            reply_markup=get_notification_keyboard(settings["is_enabled"]),
            parse_mode="HTML",
        )
        return

    if data == "notif_set_time":
        await show_notification_hour_selector(query, user_id)
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

        updated = get_notification_settings(user_id)

        await query.edit_message_text(
            text=(
                f"🔔 Got it — I’ll send you notifications about new tournaments "
                f"at <b>{hour:02d}:00</b> according to your time zone "
                f"(<b>{updated['timezone']}</b>)."
            ),
            reply_markup=get_notification_keyboard(updated["is_enabled"]),
            parse_mode="HTML",
        )
        return

    if data == "notif_back_to_settings":
        text = (
            "🔔 <b>Notifications</b>\n\n"
            f"Status: {'ON' if settings['is_enabled'] else 'OFF'}\n"
            f"Time: {settings['delivery_hour']:02d}:00\n"
            f"Time zone: {settings['timezone']}\n\n"
            "Here you can manage notifications about new tournaments."
        )

        await query.edit_message_text(
            text=text,
            reply_markup=get_notification_keyboard(settings["is_enabled"]),
            parse_mode="HTML",
        )
        return

    if data == "notif_back":
        await query.edit_message_text("Back to menu.")
        return
        
async def show_notification_hour_selector(query, user_id: int):
    settings = get_notification_settings(user_id)
    current_hour = settings["delivery_hour"]

    text = (
        "⏰ <b>When should I send notifications about new tournaments?</b>\n\n"
        "Choose the hour in your local time."
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_notification_hour_keyboard(current_hour),
        parse_mode="HTML",
    )

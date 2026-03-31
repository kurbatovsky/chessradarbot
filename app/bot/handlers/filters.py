from telegram import Update
from telegram.ext import ContextTypes

from app.bot.ui.keyboards import get_main_keyboard
from app.repositories.user_filters import get_user_filters, clear_user_filters


async def show_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return

    user_id = update.message.from_user.id
    user_filters = get_user_filters(user_id)

    format_value = user_filters["format"] or "any"
    countries_value = (
        ", ".join(user_filters["countries"])
        if user_filters["countries"]
        else "any"
    )
    rated_value = "rated only" if user_filters["rated_only"] else "any"

    await update.message.reply_text(
        f"Current filters:\n"
        f"• Format: {format_value}\n"
        f"• Countries: {countries_value}\n"
        f"• Rated: {rated_value}",
        reply_markup=get_main_keyboard(),
    )


async def clear_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return

    user_id = update.message.from_user.id
    clear_user_filters(user_id)
    context.user_data["state"] = None

    await update.message.reply_text(
        "All filters cleared.",
        reply_markup=get_main_keyboard(),
    )
from telegram import Update
from telegram.ext import ContextTypes

from app.bot.ui.keyboards import get_main_keyboard
from app.repositories.user_filters import get_user_filters


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_states: dict) -> None:
    if update.message is None or update.message.from_user is None:
        return

    user_id = update.message.from_user.id
    get_user_filters(user_id)
    user_states[user_id] = None

    await update.message.reply_text(
        "♟ Welcome to ChessRadar.\n\n"
        "Use the buttons below to find offline chess tournaments.",
        reply_markup=get_main_keyboard(),
    )
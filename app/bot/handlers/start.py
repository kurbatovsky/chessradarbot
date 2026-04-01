from telegram import Update
from telegram.ext import ContextTypes

from app.bot.ui.keyboards import get_main_keyboard
from app.repositories.users import get_or_create_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None:
        return

    get_or_create_user(
        telegram_user_id=update.effective_user.id,
        username=update.effective_user.username,
    )

    await update.message.reply_text(
        "♟ Welcome to ChessRadar Bot! Use the menu below to search tournaments and manage filters.",
        reply_markup=get_main_keyboard(),
    )
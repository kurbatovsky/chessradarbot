from telegram import Update
from telegram.ext import ContextTypes

from app.bot.ui.keyboards import get_main_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["state"] = None

    if update.message is not None:
        await update.message.reply_text(
            "♟ Welcome to ChessRadarBot!\n\n"
            "Find offline chess tournaments and filter them by format, country, and rating.",
            reply_markup=get_main_keyboard(),
)
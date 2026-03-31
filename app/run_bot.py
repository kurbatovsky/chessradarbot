import os
import json
import logging
from app.repositories.tournaments import load_tournaments
from app.repositories.user_filters import (
    get_user_filters,
    save_user_filters,
    clear_user_filters,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from app.bot.ui.keyboards import (
    get_main_keyboard,
    get_format_keyboard,
    get_country_keyboard,
    get_rated_keyboard,
    get_results_keyboard,
)
from app.bot.ui.formatters import format_date_range, format_tournament_card
from app.bot.ui.messages import build_results_message
from app.services.tournament_service import filter_tournaments
from app.core.constants import MAX_RESULTS
from app.bot.handlers.start import start
from app.bot.handlers.filters import show_filters, clear_filters
from app.bot.handlers.results import find_tournaments, handle_results_pagination

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

USER_STATES = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context, USER_STATES)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None or update.message.text is None:
        return

    user_id = update.message.from_user.id
    text = update.message.text.strip()
    state = USER_STATES.get(user_id)
    user_filters = get_user_filters(user_id)

    if text == "Find tournaments":
        USER_STATES[user_id] = None
        await find_tournaments(update, context)
        return

    if text == "Set format":
        USER_STATES[user_id] = "waiting_format"
        await update.message.reply_text(
            "Choose a format:",
            reply_markup=get_format_keyboard(),
        )
        return

    if text == "Set country":
        USER_STATES[user_id] = "waiting_country"
        await update.message.reply_text(
            "Enter country (for example: Cyprus, Greece, Armenia):",
            reply_markup=get_main_keyboard(),
        )
        return

    if text == "Set rated":
        USER_STATES[user_id] = "waiting_rated"
        await update.message.reply_text(
            "Choose rated filter:",
            reply_markup=get_rated_keyboard(),
        )
        return

    if text == "Show filters":
        USER_STATES[user_id] = None
        await show_filters(update, context)
        return

    if text == "Clear filters":
        await clear_filters(update, context, USER_STATES)
        return

    if text == "Back to menu":
        USER_STATES[user_id] = None
        await update.message.reply_text(
            "Back to main menu.",
            reply_markup=get_main_keyboard(),
        )
        return

    if state == "waiting_format":
        value = text.lower()
        allowed = {"standard", "rapid", "blitz"}

        if value not in allowed:
            await update.message.reply_text(
                "Please choose one of the format buttons.",
                reply_markup=get_format_keyboard(),
            )
            return

        save_user_filters(user_id, format_value=value)
        USER_STATES[user_id] = None

        await update.message.reply_text(
            f"Format filter set to: {value}",
            reply_markup=get_main_keyboard(),
        )
        return

    if state == "waiting_country":
        value = text.lower()

        if not value:
            await update.message.reply_text(
                "Please enter a country name.",
                reply_markup=get_main_keyboard(),
            )
            return

        save_user_filters(user_id, country_value=value)
        USER_STATES[user_id] = None

        await update.message.reply_text(
            f"Country filter set to: {value.capitalize()}",
            reply_markup=get_main_keyboard(),
        )
        return

    if state == "waiting_rated":
        value = text.lower()

        if value == "any":
            save_user_filters(user_id, rated_only=False)
            USER_STATES[user_id] = None

            await update.message.reply_text(
                "Rated filter set to: any",
                reply_markup=get_main_keyboard(),
            )
            return

        if value == "rated only":
            save_user_filters(user_id, rated_only=True)
            USER_STATES[user_id] = None

            await update.message.reply_text(
                "Rated filter set to: rated only",
                reply_markup=get_main_keyboard(),
            )
            return

        await update.message.reply_text(
            "Please choose one of the rated filter buttons.",
            reply_markup=get_rated_keyboard(),
        )
        return

    await update.message.reply_text(
        "Please use the menu buttons below.",
        reply_markup=get_main_keyboard(),
    )

def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(handle_results_pagination, pattern=r"^results:\d+$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
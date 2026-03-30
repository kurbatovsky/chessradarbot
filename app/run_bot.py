import os
import json
import logging
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

USER_FILTERS = {}
USER_STATES = {}


def load_tournaments():
    with open("data/tournaments.json", "r", encoding="utf-8") as file:
        return json.load(file)


def get_main_keyboard():
    keyboard = [
        ["Find tournaments"],
        ["Set format", "Set country"],
        ["Show filters", "Clear filters"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_format_keyboard():
    keyboard = [
        ["Standard", "Rapid", "Blitz"],
        ["Back to menu"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_country_keyboard():
    keyboard = [
        ["Cyprus", "Greece"],
        ["Back to menu"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_user_filters(user_id):
    if user_id not in USER_FILTERS:
        USER_FILTERS[user_id] = {
            "format": None,
            "country": None,
        }
    return USER_FILTERS[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return

    user_id = update.message.from_user.id
    get_user_filters(user_id)
    USER_STATES[user_id] = None

    await update.message.reply_text(
        "♟ Welcome to ChessRadar.\n\n"
        "Use the buttons below to find offline chess tournaments.",
        reply_markup=get_main_keyboard(),
    )


async def show_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return

    user_id = update.message.from_user.id
    user_filters = get_user_filters(user_id)

    format_value = user_filters["format"] or "any"
    country_value = user_filters["country"] or "any"

    await update.message.reply_text(
        f"Current filters:\n"
        f"• Format: {format_value}\n"
        f"• Country: {country_value}",
        reply_markup=get_main_keyboard(),
    )


async def clear_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return

    user_id = update.message.from_user.id
    USER_FILTERS[user_id] = {
        "format": None,
        "country": None,
    }
    USER_STATES[user_id] = None

    await update.message.reply_text(
        "All filters cleared.",
        reply_markup=get_main_keyboard(),
    )


async def find_tournaments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return

    tournaments = load_tournaments()

    user_id = update.message.from_user.id
    user_filters = get_user_filters(user_id)

    results = []

    for tournament in tournaments:
        if user_filters["format"] and tournament["format"] != user_filters["format"]:
            continue

        if user_filters["country"] and tournament["country"] != user_filters["country"]:
            continue

        results.append(tournament)

    if not results:
        await update.message.reply_text(
            "No tournaments found for your filters.",
            reply_markup=get_main_keyboard(),
        )
        return

    active_filters = []
    if user_filters["format"]:
        active_filters.append(f"format={user_filters['format']}")
    if user_filters["country"]:
        active_filters.append(f"country={user_filters['country']}")

    if active_filters:
        message = "🔎 Available tournaments\n"
        message += f"Filters: {', '.join(active_filters)}\n\n"
    else:
        message = "🔎 Available tournaments\n\n"

    for tournament in results:
        message += (
            f"♟ {tournament['name']}\n"
            f"📍 {tournament['location']}\n"
            f"📅 {tournament['date']}\n"
            f"⏱ {tournament['format'].capitalize()}\n\n"
        )

    await update.message.reply_text(
        message,
        reply_markup=get_main_keyboard(),
    )


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
            "Choose a country:",
            reply_markup=get_country_keyboard(),
        )
        return

    if text == "Show filters":
        USER_STATES[user_id] = None
        await show_filters(update, context)
        return

    if text == "Clear filters":
        await clear_filters(update, context)
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

        user_filters["format"] = value
        USER_STATES[user_id] = None

        await update.message.reply_text(
            f"Format filter set to: {value}",
            reply_markup=get_main_keyboard(),
        )
        return

    if state == "waiting_country":
        value = text.lower()
        allowed = {"cyprus", "greece"}

        if value not in allowed:
            await update.message.reply_text(
                "Please choose one of the country buttons.",
                reply_markup=get_country_keyboard(),
            )
            return

        user_filters["country"] = value
        USER_STATES[user_id] = None

        await update.message.reply_text(
            f"Country filter set to: {value.capitalize()}",
            reply_markup=get_main_keyboard(),
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

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
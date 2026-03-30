import os
import json
import logging
from app.db import SessionLocal
from app.models import Tournament, UserFilter
from datetime import datetime
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

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

USER_STATES = {}
MAX_RESULTS = 5


def load_tournaments():
    session = SessionLocal()

    tournaments = session.query(Tournament).order_by(Tournament.start_date.asc()).all()

    result = []
    for t in tournaments:
        result.append(
            {
                "name": t.name,
                "location": t.location,
                "country": t.country,
                "start_date": t.start_date.isoformat(),
                "end_date": t.end_date.isoformat(),
                "format": t.format,
                "source": t.source,
                "url": t.url,
                "fide_rated": t.fide_rated,
                "entry_fee": float(t.entry_fee) if t.entry_fee is not None else None,
                "currency": t.currency,
            }
        )

    session.close()
    return result

def get_user_filters(user_id):
    session = SessionLocal()

    db_filter = (
        session.query(UserFilter)
        .filter(UserFilter.telegram_user_id == str(user_id))
        .first()
    )

    if not db_filter:
        db_filter = UserFilter(
            telegram_user_id=str(user_id),
            format=None,
            country=None,
            rated_only=False,
        )
        session.add(db_filter)
        session.commit()
        session.refresh(db_filter)

    result = {
        "format": db_filter.format,
        "country": db_filter.country,
        "rated_only": db_filter.rated_only,
    }

    session.close()
    return result


def save_user_filters(user_id, format_value=None, country_value=None, rated_only=None):
    session = SessionLocal()

    db_filter = (
        session.query(UserFilter)
        .filter(UserFilter.telegram_user_id == str(user_id))
        .first()
    )

    if not db_filter:
        db_filter = UserFilter(
            telegram_user_id=str(user_id),
            format=None,
            country=None,
            rated_only=False,
        )
        session.add(db_filter)
        session.commit()
        session.refresh(db_filter)

    if format_value is not None:
        db_filter.format = format_value

    if country_value is not None:
        db_filter.country = country_value

    if rated_only is not None:
        db_filter.rated_only = rated_only

    session.commit()
    session.close()


def clear_user_filters(user_id):
    session = SessionLocal()

    db_filter = (
        session.query(UserFilter)
        .filter(UserFilter.telegram_user_id == str(user_id))
        .first()
    )

    if not db_filter:
        db_filter = UserFilter(
            telegram_user_id=str(user_id),
            format=None,
            country=None,
            rated_only=False,
        )
        session.add(db_filter)
    else:
        db_filter.format = None
        db_filter.country = None
        db_filter.rated_only = False

    session.commit()
    session.close()

def get_main_keyboard():
    keyboard = [
        ["Find tournaments"],
        ["Set format", "Set country"],
        ["Set rated", "Show filters"],
        ["Clear filters"],
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


def get_rated_keyboard():
    keyboard = [
        ["Any", "Rated only"],
        ["Back to menu"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_results_keyboard(tournaments):
    buttons = []

    for index, tournament in enumerate(tournaments, start=1):
        url = tournament.get("url")
        name = tournament.get("name", f"Tournament {index}")

        if not url:
            continue

        button_text = f"{index}. Open link"
        buttons.append([InlineKeyboardButton(button_text, url=url)])

    if not buttons:
        return None

    return InlineKeyboardMarkup(buttons)


def get_user_filters(user_id):
    if user_id not in USER_FILTERS:
        USER_FILTERS[user_id] = {
            "format": None,
            "country": None,
            "rated_only": False,
        }
    return USER_FILTERS[user_id]


def format_tournament_card(tournament):
    rated_text = "Yes" if tournament.get("fide_rated") else "No"
    entry_fee = tournament.get("entry_fee")
    currency = tournament.get("currency", "")

    if entry_fee is None:
        fee_text = "Unknown"
    else:
        fee_text = f"{entry_fee} {currency}".strip()

    return (
        f"♟ {tournament['name']}\n"
        f"📍 {tournament['location']}\n"
        f"📅 {tournament['date']}\n"
        f"⏱ {tournament['format'].capitalize()}\n"
        f"🏅 FIDE rated: {rated_text}\n"
        f"💶 Entry fee: {fee_text}\n"
        f"🌐 Source: {tournament.get('source', 'unknown')}"
    )

def filter_tournaments(tournaments, user_filters):
    results = []

    for tournament in tournaments:
        if user_filters["format"] and tournament["format"] != user_filters["format"]:
            continue

        if user_filters["country"] and tournament["country"] != user_filters["country"]:
            continue

        if user_filters["rated_only"] and not tournament.get("fide_rated", False):
            continue


        results.append(tournament)
    results.sort(
        key=lambda t: t.get("start_date", "9999-12-31")
    )

    return results


def build_results_message(results, user_filters, page):
    total_results = len(results)
    start_index = page * MAX_RESULTS
    end_index = start_index + MAX_RESULTS
    visible_results = results[start_index:end_index]

    active_filters = []
    if user_filters["format"]:
        active_filters.append(f"format={user_filters['format']}")
    if user_filters["country"]:
        active_filters.append(f"country={user_filters['country']}")
    if user_filters["rated_only"]:
        active_filters.append("rated only")

    if active_filters:
        message = "🔎 <b>Available tournaments</b>\n"
        message += f"Filters: {', '.join(active_filters)}\n\n"
    else:
        message = "🔎 <b>Available tournaments</b>\n\n"

    total_pages = (total_results - 1) // MAX_RESULTS + 1
    message += f"Showing {start_index + 1}-{min(end_index, total_results)} of {total_results} "
    message += f"(page {page + 1}/{total_pages})\n\n"

    for index, tournament in enumerate(visible_results, start=start_index + 1):
        message += format_tournament_card_html(index, tournament) + "\n"

    return message


def get_results_keyboard(page, total_results):
    total_pages = (total_results - 1) // MAX_RESULTS + 1
    buttons = []

    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton("⬅ Previous", callback_data=f"results:{page - 1}")
        )

    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton("Next ➡", callback_data=f"results:{page + 1}")
        )

    if nav_row:
        buttons.append(nav_row)

    return InlineKeyboardMarkup(buttons) if buttons else None

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
    rated_value = "rated only" if user_filters["rated_only"] else "any"

    await update.message.reply_text(
        f"Current filters:\n"
        f"• Format: {format_value}\n"
        f"• Country: {country_value}\n"
        f"• Rated: {rated_value}",
        reply_markup=get_main_keyboard(),
    )


async def clear_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return

    user_id = update.message.from_user.id
    clear_user_filters(user_id)
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

    results = filter_tournaments(tournaments, user_filters)

    if not results:
        await update.message.reply_text(
            "No tournaments found for your filters.",
            reply_markup=get_main_keyboard(),
        )
        return

    page = 0
    message = build_results_message(results, user_filters, page)
    keyboard = get_results_keyboard(page, len(results))

    await update.message.reply_text(
        message,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

async def handle_results_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.from_user is None or query.data is None:
        return

    await query.answer()

    user_id = query.from_user.id
    user_filters = get_user_filters(user_id)
    tournaments = load_tournaments()
    results = filter_tournaments(tournaments, user_filters)

    if not results:
        await query.edit_message_text(
            "No tournaments found for your filters.",
        )
        return

    try:
        _, page_str = query.data.split(":")
        page = int(page_str)
    except (ValueError, IndexError):
        return

    message = build_results_message(results, user_filters, page)
    keyboard = get_results_keyboard(page, len(results))

    await query.edit_message_text(
        message,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
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

        save_user_filters(user_id, format_value=value)
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

def format_date_range(tournament):
    start = tournament.get("start_date")
    end = tournament.get("end_date")

    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")

        if start == end:
            return start_dt.strftime("%d %b %Y")

        return f"{start_dt.strftime('%d %b')} – {end_dt.strftime('%d %b %Y')}"
    except Exception:
        return "Unknown date"


def format_tournament_card_html(index, tournament):
    rated_text = "Yes" if tournament.get("fide_rated") else "No"
    entry_fee = tournament.get("entry_fee")
    currency = tournament.get("currency", "")

    if entry_fee is None:
        fee_text = "Unknown"
    else:
        fee_text = f"{entry_fee} {currency}".strip()

    url = tournament.get("url")
    if url:
        link_text = f'🔗 <a href="{url}">Open tournament page</a>'
    else:
        link_text = "🔗 No link"

    date_text = format_date_range(tournament)

    return (
        f"{index}. ♟ <b>{tournament['name']}</b>\n"
        f"📍 {tournament['location']}\n"
        f"📅 {date_text}\n"
        f"⏱ {tournament['format'].capitalize()}\n"
        f"🏅 FIDE rated: {rated_text}\n"
        f"💶 Entry fee: {fee_text}\n"
        f"🌐 Source: {tournament.get('source', 'unknown')}\n"
        f"{link_text}\n"
    )

def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_results_pagination, pattern=r"^results:\d+$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
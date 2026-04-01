from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from app.repositories.results_cache import save_results_cache

from app.bot.ui.keyboards import get_main_keyboard, get_results_keyboard
from app.bot.ui.messages import build_results_message
from app.repositories.tournaments import load_tournaments
from app.repositories.user_filters import get_user_filters
from app.services.tournament_service import filter_tournaments


def has_active_filters(user_filters: dict) -> bool:
    if not user_filters:
        return False

    if user_filters.get("countries"):
        return True

    if user_filters.get("formats"):
        return True

    if user_filters.get("format"):
        return True

    if user_filters.get("fide_rated") is True:
        return True

    if user_filters.get("date_from"):
        return True

    if user_filters.get("date_to"):
        return True

    entry_fee_max = user_filters.get("entry_fee_max")
    if entry_fee_max not in (None, "", 0):
        return True

    return False


async def find_tournaments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user

    if message is None or user is None:
        return

    user_id = user.id
    user_filters = get_user_filters(user_id)

    if not has_active_filters(user_filters):
        await message.reply_text(
            "⚠️ Please select at least one filter before searching.\n\n"
            "Start with country — it works best.",
            reply_markup=get_main_keyboard(),
        )
        return

    tournaments = load_tournaments()
    results = filter_tournaments(tournaments, user_filters)

    if not results:
        await message.reply_text(
            "No tournaments found for your filters.",
            reply_markup=get_main_keyboard(),
        )
        return

    save_results_cache(user_id, results, user_filters)

    page = 0
    text = build_results_message(results, user_filters, page)
    keyboard = get_results_keyboard(page, len(results))

    await message.reply_text(
        text,
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
    payload = get_results_cache(user_id)

    if payload:
        results = payload["results"]
        user_filters = payload["user_filters"]
    else:
        user_filters = get_user_filters(user_id)
        tournaments = load_tournaments()
        results = filter_tournaments(tournaments, user_filters)

    if not results:
        await query.edit_message_text("No tournaments found for your filters.")
        return

    try:
        _, page_str = query.data.split(":")
        page = int(page_str)
    except (ValueError, IndexError):
        return

    text = build_results_message(results, user_filters, page)
    keyboard = get_results_keyboard(page, len(results))

    await query.edit_message_text(
        text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
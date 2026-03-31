from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.bot.ui.keyboards import get_main_keyboard, get_results_keyboard
from app.bot.ui.messages import build_results_message
from app.repositories.tournaments import load_tournaments
from app.repositories.user_filters import get_user_filters
from app.services.tournament_service import filter_tournaments


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
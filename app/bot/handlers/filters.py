from telegram import Update
from telegram.ext import ContextTypes

from app.core.countries import format_country_label
from app.core.constants import FORMAT_LABELS
from app.bot.ui.keyboards import get_main_keyboard, build_format_keyboard
from app.repositories.user_filters import (
    get_user_filters,
    clear_user_filters,
    toggle_user_format,
    clear_user_formats,
)


async def show_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return

    user_id = update.message.from_user.id
    user_filters = get_user_filters(user_id)

    # --- FORMAT ---
    formats = user_filters.get("formats", [])
    if formats:
        format_value = ", ".join(FORMAT_LABELS.get(f, f.capitalize()) for f in formats)
    else:
        format_value = "any"

    # --- COUNTRIES ---
    countries_value = (
        ", ".join(format_country_label(country) for country in user_filters["countries"])
        if user_filters["countries"]
        else "any"
    )

    # --- RATED ---
    rated_value = "rated only" if user_filters["fide_rated"] else "any"

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

async def show_format_selector(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return

    user_id = update.message.from_user.id
    user_filters = get_user_filters(user_id)

    await update.message.reply_text(
        "Select formats:",
        reply_markup=build_format_keyboard(user_filters.get("formats", [])),
    )


async def handle_format_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.from_user is None or query.data is None:
        return

    await query.answer()

    _, format_value = query.data.split(":", 1)
    user_id = query.from_user.id

    toggle_user_format(user_id, format_value)

    user_filters = get_user_filters(user_id)
    await query.edit_message_reply_markup(
        reply_markup=build_format_keyboard(user_filters.get("formats", []))
    )


async def handle_format_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.from_user is None:
        return

    await query.answer()

    user_id = query.from_user.id
    clear_user_formats(user_id)

    await query.edit_message_reply_markup(
        reply_markup=build_format_keyboard([])
    )


async def handle_format_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return

    await query.answer()

    await query.edit_message_text(
        "Formats updated.",
        reply_markup=None,
    )


async def handle_format_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return

    await query.answer()
    await query.edit_message_text("Back to menu.")
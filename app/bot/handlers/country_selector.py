from telegram import Update
from telegram.ext import ContextTypes

from app.bot.ui.keyboards import build_country_selector_keyboard, get_main_keyboard
from app.repositories.user_filters import (
    get_user_filters,
    toggle_user_country,
    clear_user_countries,
)


async def open_country_selector(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return

    user_id = update.message.from_user.id
    user_filters = get_user_filters(user_id)

    context.user_data["state"] = None

    await update.message.reply_text(
        "Select one or more countries:",
        reply_markup=build_country_selector_keyboard(user_filters["countries"]),
    )


async def handle_country_selector_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.from_user is None or query.data is None:
        return

    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data.startswith("country_toggle:"):
        country = data.split(":", 1)[1]
        toggle_user_country(user_id, country)

        user_filters = get_user_filters(user_id)
        await query.edit_message_reply_markup(
            reply_markup=build_country_selector_keyboard(user_filters["countries"])
        )
        return

    if data == "country_clear":
        clear_user_countries(user_id)

        user_filters = get_user_filters(user_id)
        await query.edit_message_reply_markup(
            reply_markup=build_country_selector_keyboard(user_filters["countries"])
        )
        return

    if data == "country_done":
        user_filters = get_user_filters(user_id)
        selected = user_filters["countries"]

        text = (
            "Country filter set to: any"
            if not selected
            else "Country filter set to: " + ", ".join(selected)
        )

        await query.edit_message_text(text=text)

        if query.message:
            await query.message.reply_text(
                "Back to main menu.",
                reply_markup=get_main_keyboard(),
            )
        return

    if data == "country_back":
        await query.edit_message_text("Country selection cancelled.")

        if query.message:
            await query.message.reply_text(
                "Back to main menu.",
                reply_markup=get_main_keyboard(),
            )
        return


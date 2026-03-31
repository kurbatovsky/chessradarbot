from telegram import Update
from telegram.ext import ContextTypes
from app.repositories.app_cache import get_cache_value

from app.bot.ui.keyboards import (
    build_country_selector_home_keyboard,
    build_popular_countries_keyboard,
    build_selected_countries_keyboard,
    build_country_page_keyboard,
    get_main_keyboard,
)
from app.core.countries import format_country_label
from app.repositories.app_cache import get_cache_value
from app.repositories.user_filters import (
    get_user_filters,
    toggle_user_country,
    clear_user_countries,
)


FALLBACK_POPULAR_COUNTRIES = [
    "cyprus",
    "greece",
    "armenia",
    "georgia",
    "turkey",
    "serbia",
    "italy",
    "spain",
    "germany",
    "france",
]


async def open_country_selector(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None:
        return

    user_id = update.message.from_user.id
    user_filters = get_user_filters(user_id)

    context.user_data["state"] = None
    context.user_data["country_menu"] = "home"
    context.user_data["country_page"] = 0

    await update.message.reply_text(
        "Select countries for tournaments:",
        reply_markup=build_country_selector_home_keyboard(user_filters["countries"]),
    )


async def _render_country_menu(query, context: ContextTypes.DEFAULT_TYPE, user_id: int, menu: str, page: int = 0) -> None:
    user_filters = get_user_filters(user_id)
    selected = user_filters["countries"]

    if menu == "home":
        text = "Select countries for tournaments:"
        markup = build_country_selector_home_keyboard(selected)

    elif menu == "popular":
        popular_countries = get_cache_value("popular_countries", default=[])

        if not popular_countries:
            popular_countries = FALLBACK_POPULAR_COUNTRIES

        text = "⭐ Popular countries"
        markup = build_popular_countries_keyboard(selected, popular_countries)

    elif menu == "selected":
        text = "✅ Selected countries"
        markup = build_selected_countries_keyboard(selected)

    elif menu == "all":
        text = f"🌍 Browse all countries (page {page + 1})"
        markup = build_country_page_keyboard(selected, page)

    else:
        text = "Select countries for tournaments:"
        markup = build_country_selector_home_keyboard(selected)

    context.user_data["country_menu"] = menu
    context.user_data["country_page"] = page

    await query.edit_message_text(text=text, reply_markup=markup)


async def handle_country_selector_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.from_user is None or query.data is None:
        return

    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "country_noop":
        return

    if data.startswith("country_toggle:"):
        country = data.split(":", 1)[1]
        toggle_user_country(user_id, country)

        current_menu = context.user_data.get("country_menu", "home")
        current_page = context.user_data.get("country_page", 0)

        await _render_country_menu(query, context, user_id, current_menu, current_page)
        return

    if data == "country_clear":
        clear_user_countries(user_id)

        current_menu = context.user_data.get("country_menu", "home")
        current_page = context.user_data.get("country_page", 0)

        await _render_country_menu(query, context, user_id, current_menu, current_page)
        return

    if data == "country_done":
        user_filters = get_user_filters(user_id)
        selected = user_filters["countries"]

        text = (
            "Country filter set to: any"
            if not selected
            else "Country filter set to: " + ", ".join(
                format_country_label(country) for country in selected
            )
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

    if data == "country_menu:home":
        await _render_country_menu(query, context, user_id, "home", 0)
        return

    if data == "country_menu:popular":
        await _render_country_menu(query, context, user_id, "popular", 0)
        return

    if data == "country_menu:selected":
        await _render_country_menu(query, context, user_id, "selected", 0)
        return

    if data.startswith("country_menu:all:"):
        page = int(data.split(":")[-1])
        await _render_country_menu(query, context, user_id, "all", page)
        return
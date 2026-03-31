from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.constants import MAX_RESULTS
from app.core.countries import AVAILABLE_COUNTRIES, format_country_label

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

def build_country_selector_keyboard(selected_countries: list[str]) -> InlineKeyboardMarkup:
    rows = []
    current_row = []

    normalized_selected = {country.lower() for country in selected_countries}

    for country in AVAILABLE_COUNTRIES:
        is_selected = country in normalized_selected
        prefix = "✅" if is_selected else "☑️"
        label = f"{prefix} {format_country_label(country)}"

        current_row.append(
            InlineKeyboardButton(
                text=label,
                callback_data=f"country_toggle:{country}",
            )
        )

        if len(current_row) == 2:
            rows.append(current_row)
            current_row = []

    if current_row:
        rows.append(current_row)

    rows.append([
        InlineKeyboardButton("Clear", callback_data="country_clear"),
        InlineKeyboardButton("Done", callback_data="country_done"),
    ])
    rows.append([
        InlineKeyboardButton("Back", callback_data="country_back"),
    ])

    return InlineKeyboardMarkup(rows)
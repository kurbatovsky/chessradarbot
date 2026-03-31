from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from app.core.constants import MAX_RESULTS
from app.core.countries import AVAILABLE_COUNTRIES, format_country_label
from app.core.constants import FORMAT_LABELS


COUNTRIES_PER_PAGE = 20


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


def _build_country_toggle_rows(
    countries: list[str],
    selected_countries: list[str],
) -> list[list[InlineKeyboardButton]]:
    rows = []
    current_row = []

    normalized_selected = {country.lower() for country in selected_countries}

    for country in countries:
        is_selected = country.lower() in normalized_selected
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

    return rows


def build_country_selector_keyboard(selected_countries: list[str]) -> InlineKeyboardMarkup:
    rows = _build_country_toggle_rows(AVAILABLE_COUNTRIES, selected_countries)

    rows.append([
        InlineKeyboardButton("Clear", callback_data="country_clear"),
        InlineKeyboardButton("Done", callback_data="country_done"),
    ])
    rows.append([
        InlineKeyboardButton("Back", callback_data="country_back"),
    ])

    return InlineKeyboardMarkup(rows)


def build_country_selector_home_keyboard(selected_countries: list[str]) -> InlineKeyboardMarkup:
    selected_count = len(selected_countries)

    rows = [
        [InlineKeyboardButton("⭐ Popular countries", callback_data="country_menu:popular")],
        [InlineKeyboardButton(f"✅ Selected countries ({selected_count})", callback_data="country_menu:selected")],
        [InlineKeyboardButton("🌍 Browse all countries", callback_data="country_menu:all:0")],
        [
            InlineKeyboardButton("Clear", callback_data="country_clear"),
            InlineKeyboardButton("Done", callback_data="country_done"),
        ],
        [InlineKeyboardButton("Back", callback_data="country_back")],
    ]

    return InlineKeyboardMarkup(rows)


def build_popular_countries_keyboard(
    selected_countries: list[str],
    popular_countries: list[str],
) -> InlineKeyboardMarkup:
    rows = _build_country_toggle_rows(popular_countries, selected_countries)

    rows.append([
        InlineKeyboardButton("✅ Selected", callback_data="country_menu:selected"),
        InlineKeyboardButton("🌍 Browse all", callback_data="country_menu:all:0"),
    ])
    rows.append([
        InlineKeyboardButton("Clear", callback_data="country_clear"),
        InlineKeyboardButton("Done", callback_data="country_done"),
    ])
    rows.append([
        InlineKeyboardButton("⬅ Home", callback_data="country_menu:home"),
    ])

    return InlineKeyboardMarkup(rows)


def build_selected_countries_keyboard(selected_countries: list[str]) -> InlineKeyboardMarkup:
    rows = []

    if selected_countries:
        rows.extend(_build_country_toggle_rows(selected_countries, selected_countries))
    else:
        rows.append([
            InlineKeyboardButton("No countries selected", callback_data="country_noop")
        ])

    rows.append([
        InlineKeyboardButton("⭐ Popular", callback_data="country_menu:popular"),
        InlineKeyboardButton("🌍 Browse all", callback_data="country_menu:all:0"),
    ])
    rows.append([
        InlineKeyboardButton("Clear", callback_data="country_clear"),
        InlineKeyboardButton("Done", callback_data="country_done"),
    ])
    rows.append([
        InlineKeyboardButton("⬅ Home", callback_data="country_menu:home"),
    ])

    return InlineKeyboardMarkup(rows)


def build_country_page_keyboard(selected_countries: list[str], page: int) -> InlineKeyboardMarkup:
    total_countries = len(AVAILABLE_COUNTRIES)
    total_pages = (total_countries - 1) // COUNTRIES_PER_PAGE + 1

    start = page * COUNTRIES_PER_PAGE
    end = start + COUNTRIES_PER_PAGE
    countries_on_page = AVAILABLE_COUNTRIES[start:end]

    rows = _build_country_toggle_rows(countries_on_page, selected_countries)

    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton("⬅ Prev", callback_data=f"country_menu:all:{page - 1}")
        )
    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton("Next ➡", callback_data=f"country_menu:all:{page + 1}")
        )
    if nav_row:
        rows.append(nav_row)

    rows.append([
        InlineKeyboardButton("⭐ Popular", callback_data="country_menu:popular"),
        InlineKeyboardButton("✅ Selected", callback_data="country_menu:selected"),
    ])
    rows.append([
        InlineKeyboardButton("Clear", callback_data="country_clear"),
        InlineKeyboardButton("Done", callback_data="country_done"),
    ])
    rows.append([
        InlineKeyboardButton("⬅ Home", callback_data="country_menu:home"),
    ])

    return InlineKeyboardMarkup(rows)

def build_format_keyboard(selected_formats: list[str]) -> InlineKeyboardMarkup:
    ALL_FORMATS = ["standard", "rapid", "blitz"]

    rows = []
    current_row = []

    for fmt in ALL_FORMATS:
        is_selected = fmt in selected_formats
        prefix = "✅" if is_selected else "☑️"
        label = f"{prefix} {FORMAT_LABELS[fmt]}"

        current_row.append(
            InlineKeyboardButton(
                text=label,
                callback_data=f"format_toggle:{fmt}",
            )
        )

        if len(current_row) == 2:
            rows.append(current_row)
            current_row = []

    if current_row:
        rows.append(current_row)

    rows.append([
        InlineKeyboardButton("Clear", callback_data="format_clear"),
        InlineKeyboardButton("Done", callback_data="format_done"),
    ])
    rows.append([
        InlineKeyboardButton("Back", callback_data="format_back"),
    ])

    return InlineKeyboardMarkup(rows)
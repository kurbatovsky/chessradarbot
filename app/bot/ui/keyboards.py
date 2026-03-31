from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

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
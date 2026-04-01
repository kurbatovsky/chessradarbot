from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.bot.handlers.country_selector import open_country_selector_in_onboarding
from app.bot.ui.keyboards import get_onboarding_format_keyboard
from app.repositories.user_filters import toggle_user_format, get_user_filters
from app.bot.ui.keyboards import get_onboarding_rated_keyboard
from app.repositories.user_filters import save_user_filters
from app.bot.ui.keyboards import get_main_keyboard
from app.bot.handlers.results import find_tournaments
from app.bot.ui.keyboards import get_onboarding_notifications_keyboard
from app.bot.handlers.notifications import show_notification_settings

from app.repositories.users import (
    get_or_create_user,
    save_onboarding_state,
)


def get_onboarding_welcome_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚀 Start setup", callback_data="onboarding_start"),
        ],
        [
            InlineKeyboardButton("Skip", callback_data="onboarding_skip"),
        ],
    ])


async def start_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    db_user = get_or_create_user(
        telegram_user_id=user.id,
        username=user.username,
    )

    # если уже прошёл onboarding — не показываем
    if db_user.get("onboarding_completed"):
        return False  # важно: даём дальше идти обычному flow

    save_onboarding_state(
        telegram_user_id=user.id,
        onboarding_step="welcome",
        onboarding_completed=False,
    )

    await message.reply_text(
        (
            "♟ Welcome to ChessRadar\n\n"
            "I help you find chess tournaments worldwide.\n\n"
            "Let's quickly set things up so you only see relevant events."
        ),
        reply_markup=get_onboarding_welcome_keyboard(),
    )

    return True


async def handle_onboarding_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.data or not query.from_user:
        return False

    data = query.data
    user_id = query.from_user.id

    if not (data.startswith("onboarding_") or data.startswith("onb_") or data.startswith("onb:")):
        return False    

    await query.answer()

    if data == "onboarding_skip":
        save_onboarding_state(
            telegram_user_id=user_id,
            onboarding_step=None,
            onboarding_completed=True,
        )

        await query.edit_message_text(
            "👌 Setup skipped. You can start using the bot."
        )
        return True

    if data == "onboarding_start":
        save_onboarding_state(
            telegram_user_id=user_id,
            onboarding_step="choose_country",
            onboarding_completed=False,
        )

        await open_country_selector_in_onboarding(query, context, user_id)
        return True

    if data.startswith("onb_format_toggle:"):
        from app.repositories.user_filters import toggle_user_format, get_user_filters

        fmt = data.split(":", 1)[1]
        toggle_user_format(user_id, fmt)

        filters = get_user_filters(user_id)

        await query.edit_message_text(
            "Step 2 of 5 — Format\n\n"
            "Pick the formats you care about most.\n\n"
            "You can select more than one, or skip this step.",
            reply_markup=get_onboarding_format_keyboard(filters["formats"]),
        )
        return True

    if data == "onb:format_continue":
        from app.repositories.user_filters import get_user_filters

        save_onboarding_state(
            telegram_user_id=user_id,
            onboarding_step="choose_rated",
            onboarding_completed=False,
        )

        filters = get_user_filters(user_id)

        await query.edit_message_text(
            "Step 3 of 5 — Rated filter\n\n"
            "Do you want only rated tournaments?",
            reply_markup=get_onboarding_rated_keyboard(filters.get("rated_only")),
        )
        return True

    if data == "onb:format_skip":
        from app.repositories.user_filters import get_user_filters

        save_onboarding_state(
            telegram_user_id=user_id,
            onboarding_step="choose_rated",
            onboarding_completed=False,
        )

        filters = get_user_filters(user_id)

        await query.edit_message_text(
            "Step 3 of 5 — Rated filter\n\n"
            "Do you want only rated tournaments?",
            reply_markup=get_onboarding_rated_keyboard(filters.get("rated_only")),
        )
        return True

    if data == "onb:exit":
        save_onboarding_state(
            telegram_user_id=user_id,
            onboarding_step=None,
            onboarding_completed=True,
        )

        await query.edit_message_text(
            "👌 Setup paused. You can continue anytime from settings."
        )
        return True

    if data.startswith("onb_rated:"):
        value = data.split(":", 1)[1]

        rated_only = None
        if value == "any":
            rated_only = False
        elif value == "rated":
            rated_only = True

        # сохраняем явно
        save_user_filters(
            user_id,
            rated_only=rated_only,
        )

        # 👇 ВАЖНО: используем это же значение напрямую
        await query.edit_message_text(
            "Step 3 of 5 — Rated filter\n\n"
            "Do you want only rated tournaments?",
            reply_markup=get_onboarding_rated_keyboard(rated_only),
        )
        return True

    if data == "onb:rated_continue" or data == "onb:rated_skip":
        save_onboarding_state(
            telegram_user_id=user_id,
            onboarding_step="finish",
            onboarding_completed=False,
        )

        await query.edit_message_text(
            "Step 4 of 5 — Ready 🚀\n\n"
            "You're all set!\n\n"
            "Let's find your first tournaments.",
            reply_markup=get_onboarding_finish_keyboard(),
        )
        return True

    if data == "onb:search":
        save_onboarding_state(
            telegram_user_id=user_id,
            onboarding_step=None,
            onboarding_completed=True,
        )

        context.user_data["onboarding_active"] = False

        await query.message.reply_text(
            "🔍 Searching tournaments...",
            reply_markup=get_main_keyboard(),
        )

        await find_tournaments(update, context)

        await query.message.reply_text(
            "🔔 Stay updated\n\n"
            "Want to receive new tournaments automatically?\n\n"
            "We’ll send you updates based on your filters.",
            reply_markup=get_onboarding_notifications_keyboard(),
        )

        return True

    if data == "onb:notif_enable":
        # просто открываем существующий экран настроек
        await show_notification_settings(update, context)
        return True

    if data == "onb:notif_skip":
        save_onboarding_state(
            telegram_user_id=user_id,
            onboarding_step=None,
            onboarding_completed=True,
        )

        await query.edit_message_text(
            "👌 You're all set!\n\n"
            "You can enable notifications anytime from settings."
        )
        return True

    return False

async def render_onboarding_welcome_from_country(query, user_id):
    save_onboarding_state(
        telegram_user_id=user_id,
        onboarding_step="welcome",
        onboarding_completed=False,
    )

    await query.edit_message_text(
        (
            "♟ Welcome to ChessRadar\n\n"
            "I help you find chess tournaments worldwide.\n\n"
            "Let's quickly set things up so you only see relevant events."
        ),
        reply_markup=get_onboarding_welcome_keyboard(),
    )

    return False

async def render_format_step_after_country(query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    from app.repositories.user_filters import get_user_filters

    save_onboarding_state(
        telegram_user_id=user_id,
        onboarding_step="choose_format",
        onboarding_completed=False,
    )

    filters = get_user_filters(user_id)

    await query.edit_message_text(
        "Step 2 of 5 — Format\n\n"
        "Pick the formats you care about most.\n\n"
        "You can select more than one, or skip this step.",
        reply_markup=get_onboarding_format_keyboard(filters["formats"]),
    )

def get_onboarding_finish_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 Find tournaments", callback_data="onb:search"),
        ],
        [
            InlineKeyboardButton("Exit", callback_data="onb:exit"),
        ],
    ])

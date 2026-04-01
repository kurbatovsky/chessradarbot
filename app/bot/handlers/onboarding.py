from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.bot.handlers.country_selector import open_country_selector_in_onboarding
from app.bot.ui.keyboards import get_onboarding_format_keyboard
from app.repositories.user_filters import toggle_user_format, get_user_filters

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

    if not data.startswith("onboarding_"):
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
            save_onboarding_state(
                telegram_user_id=user_id,
                onboarding_step="choose_rated",
                onboarding_completed=False,
            )

            await query.edit_message_text(
                "Step 3 of 5 — Rated filter\n\n"
                "Do you want only rated tournaments?"
            )
            return True

    if data == "onb:format_skip":
        save_onboarding_state(
            telegram_user_id=user_id,
            onboarding_step="choose_rated",
            onboarding_completed=False,
        )

        await query.edit_message_text(
            "Step 3 of 5 — Rated filter\n\n"
            "Do you want only rated tournaments?"
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

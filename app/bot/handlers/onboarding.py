from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

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

        await query.edit_message_text(
            "🌍 First, choose the countries you're interested in.\n\n"
            "You can select multiple."
        )

        # 👉 дальше сюда подключим country selector (следующий шаг)
        return True

    return False

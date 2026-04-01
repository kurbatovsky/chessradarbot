import os
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from app.repositories.user_filters import save_user_filters
from app.bot.ui.keyboards import (
    get_main_keyboard,
    get_rated_keyboard,
)
from app.bot.handlers.start import start
from app.bot.handlers.onboarding import (
    start_onboarding,
    handle_onboarding_callbacks,
)
from app.bot.handlers.filters import (
    show_filters,
    clear_filters,
    show_format_selector,
    handle_format_toggle,
    handle_format_clear,
    handle_format_done,
    handle_format_back,
)
from app.bot.handlers.results import find_tournaments, handle_results_pagination
from app.bot.handlers.country_selector import (
    open_country_selector,
    handle_country_selector_callback,
)
from app.bot.handlers.notifications import (
    show_notification_settings,
    handle_notification_callbacks,
)
from app.repositories.users import get_or_create_user

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    onboarding_started = await start_onboarding(update, context)
    if onboarding_started:
        return

    await start(update, context)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.from_user is None or update.message.text is None:
        return

    get_or_create_user(
        telegram_user_id=update.message.from_user.id,
        username=update.message.from_user.username,
    )

    user_id = update.message.from_user.id
    text = update.message.text.strip()
    state = context.user_data.get("state")

    if text == "Find tournaments":
        context.user_data["state"] = None
        await find_tournaments(update, context)
        return

    if text == "Set format":
        context.user_data["state"] = None
        await show_format_selector(update, context)
        return

    if text == "Set country":
        await open_country_selector(update, context)
        return

    if text == "Set rated":
        context.user_data["state"] = "waiting_rated"
        await update.message.reply_text(
            "Choose rated filter:",
            reply_markup=get_rated_keyboard(),
        )
        return

    if text == "Show filters":
        context.user_data["state"] = None
        await show_filters(update, context)
        return

    if text == "Clear filters":
        await clear_filters(update, context)
        return

    if text == "Notifications ⚙️":
        context.user_data["state"] = None
        await show_notification_settings(update, context)
        return

    if text == "Back to menu":
        context.user_data["state"] = None
        await update.message.reply_text(
            "Back to main menu.",
            reply_markup=get_main_keyboard(),
        )
        return

    if state == "waiting_rated":
        value = text.lower()

        if value == "any":
            save_user_filters(user_id, rated_only=False)
            context.user_data["state"] = None

            await update.message.reply_text(
                "Rated filter set to: any",
                reply_markup=get_main_keyboard(),
            )
            return

        if value == "rated only":
            save_user_filters(user_id, rated_only=True)
            context.user_data["state"] = None

            await update.message.reply_text(
                "Rated filter set to: rated only",
                reply_markup=get_main_keyboard(),
            )
            return

        await update.message.reply_text(
            "Please choose one of the rated filter buttons.",
            reply_markup=get_rated_keyboard(),
        )
        return

    await update.message.reply_text(
        "Please use the menu buttons below.",
        reply_markup=get_main_keyboard(),
    )


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))

    app.add_handler(
        CallbackQueryHandler(handle_onboarding_callbacks, pattern=r"^onboarding_|^onb")
    )

    app.add_handler(
        CallbackQueryHandler(
            handle_country_selector_callback,
            pattern=r"^(country_toggle:|country_clear$|country_done$|country_back$|country_menu:|country_noop$)"
        )
    )

    app.add_handler(CallbackQueryHandler(handle_format_toggle, pattern=r"^format_toggle:"))
    app.add_handler(CallbackQueryHandler(handle_format_clear, pattern=r"^format_clear$"))
    app.add_handler(CallbackQueryHandler(handle_format_done, pattern=r"^format_done$"))
    app.add_handler(CallbackQueryHandler(handle_format_back, pattern=r"^format_back$"))

    app.add_handler(CallbackQueryHandler(handle_results_pagination, pattern=r"^results:\d+$"))
    app.add_handler(CallbackQueryHandler(handle_notification_callbacks, pattern=r"^notif_"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
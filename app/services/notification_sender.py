import os

from telegram import Bot
from telegram.constants import ParseMode

from app.bot.ui.keyboards import get_results_keyboard
from app.bot.ui.messages import build_results_message


async def send_notification_message(chat_id, tournaments, user_filters) -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    bot = Bot(token=token)

    page = 0
    results_text = build_results_message(tournaments, user_filters, page)
    keyboard = get_results_keyboard(page, len(tournaments))

    text = (
        "🔔 <b>New tournaments for your filters</b>\n"
        "Use the buttons below to browse pages.\n\n"
        f"{results_text}"
    )

    await bot.send_message(
        chat_id=int(chat_id),
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
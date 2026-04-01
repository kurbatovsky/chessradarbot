import html
import os

from telegram import Bot


def build_notification_text(tournaments: list[dict]) -> str:
    lines = []
    lines.append("♟ New tournaments for your filters:")
    lines.append("")

    for tournament in tournaments[:10]:
        name = html.escape(tournament["name"])
        country = html.escape(tournament.get("country") or "Unknown")
        location = html.escape(tournament.get("location") or "Unknown")
        start_date = html.escape(tournament.get("start_date") or "Unknown date")
        fmt = html.escape(tournament.get("format") or "Unknown format")
        rated = "FIDE rated" if tournament.get("fide_rated") else "Not rated"
        url = tournament.get("url")

        lines.append(f"• <b>{name}</b>")
        lines.append(f"  {country} — {location}")
        lines.append(f"  {start_date} • {fmt} • {rated}")
        if url:
            lines.append(f"  <a href=\"{html.escape(url)}\">Open</a>")
        lines.append("")

    extra_count = max(0, len(tournaments) - 10)
    if extra_count:
        lines.append(f"And {extra_count} more tournaments matched your filters.")

    return "\n".join(lines).strip()


async def send_notification_message(chat_id: int | str, tournaments: list[dict]) -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")

    bot = Bot(token=token)
    text = build_notification_text(tournaments)

    await bot.send_message(
        chat_id=int(chat_id),
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

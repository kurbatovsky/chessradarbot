from datetime import datetime


def format_date_range(tournament):
    start = tournament.get("start_date")
    end = tournament.get("end_date")

    if not start or not end:
        return "Unknown date"

    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")

        if start == end:
            return start_dt.strftime("%d %b %Y")

        return f"{start_dt.strftime('%d %b')} – {end_dt.strftime('%d %b %Y')}"
    except Exception:
        return "Unknown date"


def format_tournament_card(tournament):
    rated_text = "Yes" if tournament.get("fide_rated") else "No"
    entry_fee = tournament.get("entry_fee")
    currency = tournament.get("currency", "")

    if entry_fee is None:
        fee_text = "Unknown"
    else:
        fee_text = f"{entry_fee} {currency}".strip()

    date_text = format_date_range(tournament)

    url = tournament.get("url")

    if url:
        link_text = f'🔗 <a href="{url}">Open tournament page</a>'
    else:
        link_text = "🔗 No link"

    return (
        f"♟ <b>{tournament['name']}</b>\n"
        f"📍 {tournament['location']}\n"
        f"📅 {date_text}\n"
        f"⏱ {tournament['format'].capitalize()}\n"
        f"🏅 FIDE rated: {rated_text}\n"
        f"💶 Entry fee: {fee_text}\n"
        f"🌐 Source: {tournament.get('source', 'unknown')}\n"
        f"{link_text}\n"
    )
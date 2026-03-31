from datetime import datetime
from app.core.countries import format_country_label


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

    date_text = format_date_range(tournament)
    country_text = format_country_label(tournament.get("country", "unknown"))

    url = tournament.get("url")

    if url:
        link_text = f'🔗 <a href="{url}">Open tournament page</a>'
    else:
        link_text = "🔗 No link"

    return (
        f"♟ <b>{tournament.get('name', 'Unnamed tournament')}</b>\n"
        f"📍 {tournament.get('location', 'Unknown location')}\n"
        f"{country_text}\n"
        f"📅 {date_text}\n"
        f"⏱ {(tournament.get('format') or 'unknown').capitalize()}\n"
        f"🏅 FIDE rated: {rated_text}\n"
        f"🌐 Source: {tournament.get('source', 'unknown')}\n"
        f"{link_text}\n"
    )
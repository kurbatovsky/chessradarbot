from app.bot.ui.formatters import format_tournament_card
from app.core.constants import MAX_RESULTS


def build_results_message(results, user_filters, page):
    total_results = len(results)
    start_index = page * MAX_RESULTS
    end_index = start_index + MAX_RESULTS
    visible_results = results[start_index:end_index]

    active_filters = []
    if user_filters["format"]:
        active_filters.append(f"format={user_filters['format']}")
    if user_filters["country"]:
        active_filters.append(f"country={user_filters['country']}")
    if user_filters["rated_only"]:
        active_filters.append("rated only")

    if active_filters:
        message = "🔎 <b>Available tournaments</b>\n"
        message += f"Filters: {', '.join(active_filters)}\n\n"
    else:
        message = "🔎 <b>Available tournaments</b>\n\n"

    total_pages = (total_results - 1) // MAX_RESULTS + 1
    message += f"Showing {start_index + 1}-{min(end_index, total_results)} of {total_results} "
    message += f"(page {page + 1}/{total_pages})\n\n"

    for index, tournament in enumerate(visible_results, start=start_index + 1):
        message += format_tournament_card(tournament) + "\n"

    return message
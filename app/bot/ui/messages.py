from app.bot.ui.formatters import format_tournament_card
from app.core.constants import MAX_RESULTS, FORMAT_LABELS
from app.core.countries import format_country_label


def build_results_message(results, user_filters, page):
    total_results = len(results)
    start_index = page * MAX_RESULTS
    end_index = start_index + MAX_RESULTS
    visible_results = results[start_index:end_index]

    active_filters = []

    formats = user_filters.get("formats", [])
    if formats:
        active_filters.append(
            "format=" + ", ".join(FORMAT_LABELS.get(fmt, fmt.capitalize()) for fmt in formats)
        )

    countries = user_filters.get("countries", [])
    if countries:
        active_filters.append(
            "countries=" + ", ".join(
                format_country_label(country) for country in countries
            )
        )

    if user_filters.get("fide_rated"):
        active_filters.append("rated only")

    if active_filters:
        message = "Available tournaments\n"
        message += f"Filters: {', '.join(active_filters)}\n\n"
    else:
        message = "Available tournaments\n\n"

    total_pages = (total_results - 1) // MAX_RESULTS + 1
    message += (
        f"Showing {start_index + 1}-{min(end_index, total_results)} of {total_results} "
        f"(page {page + 1}/{total_pages})\n\n"
    )

    for tournament in visible_results:
        message += format_tournament_card(tournament) + "\n"

    return message
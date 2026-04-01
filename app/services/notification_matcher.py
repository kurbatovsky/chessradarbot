def matches_tournament(tournament: dict, user_filters: dict) -> bool:
    selected_countries = set(country.lower() for country in user_filters.get("countries", []))
    selected_formats = set(user_filters.get("formats", []))

    if selected_formats and tournament.get("format") not in selected_formats:
        return False

    tournament_country = (tournament.get("country") or "").strip().lower()
    if selected_countries and tournament_country not in selected_countries:
        return False

    if user_filters.get("fide_rated") and not tournament.get("fide_rated", False):
        return False

    return True

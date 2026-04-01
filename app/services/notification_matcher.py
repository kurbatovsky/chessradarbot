def matches_tournament(tournament: dict, user_filters: dict) -> bool:
    selected_countries = set(
        country.lower().strip()
        for country in user_filters.get("countries", [])
        if country
    )
    selected_formats = set(
        fmt.strip().lower()
        for fmt in user_filters.get("formats", [])
        if fmt
    )

    tournament_format = (tournament.get("format") or "").strip().lower()
    tournament_country = (tournament.get("country") or "").strip().lower()

    if selected_formats and tournament_format not in selected_formats:
        return False

    if selected_countries and tournament_country not in selected_countries:
        return False

    if user_filters.get("fide_rated") and not tournament.get("fide_rated", False):
        return False

    return True
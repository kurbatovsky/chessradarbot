def filter_tournaments(tournaments, user_filters):
    results = []

    selected_countries = set(country.lower() for country in user_filters["countries"])
    selected_formats = set(user_filters.get("formats", []))

    for tournament in tournaments:
        # --- FORMAT FILTER ---
        if selected_formats and tournament["format"] not in selected_formats:
            continue

        # --- COUNTRY FILTER ---
        tournament_country = (tournament.get("country") or "").strip().lower()
        if selected_countries and tournament_country not in selected_countries:
            continue

        # --- FIDE FILTER ---
        if user_filters["fide_rated"] and not tournament.get("fide_rated", False):
            continue

        results.append(tournament)

    results.sort(key=lambda t: t.get("start_date", "9999-12-31"))
    return results
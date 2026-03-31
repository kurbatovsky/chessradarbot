def filter_tournaments(tournaments, user_filters):
    results = []

    selected_countries = set(country.lower() for country in user_filters["countries"])

    for tournament in tournaments:
        if user_filters["format"] and tournament["format"] != user_filters["format"]:
            continue

        tournament_country = (tournament.get("country") or "").strip().lower()
        if selected_countries and tournament_country not in selected_countries:
            continue

        if user_filters["rated_only"] and not tournament.get("fide_rated", False):
            continue

        results.append(tournament)

    results.sort(key=lambda t: t.get("start_date", "9999-12-31"))
    return results
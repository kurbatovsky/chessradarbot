def filter_tournaments(tournaments, user_filters):
    results = []

    for tournament in tournaments:
        if user_filters["format"] and tournament["format"] != user_filters["format"]:
            continue

        if user_filters["country"] and tournament["country"] != user_filters["country"]:
            continue

        if user_filters["rated_only"] and not tournament.get("fide_rated", False):
            continue

        results.append(tournament)

    results.sort(
        key=lambda t: t.get("start_date", "9999-12-31")
    )

    return results
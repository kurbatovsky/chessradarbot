from app.repositories.app_cache import get_cache_value, set_cache_value


def _make_key(user_id: int) -> str:
    return f"results:{user_id}"


def save_results_cache(user_id: int, results, user_filters) -> None:
    set_cache_value(
        _make_key(user_id),
        {
            "results": results,
            "user_filters": user_filters,
        },
    )


def get_results_cache(user_id: int):
    return get_cache_value(_make_key(user_id), default=None)

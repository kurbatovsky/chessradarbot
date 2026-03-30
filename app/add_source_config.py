import sys

from app.db import SessionLocal
from app.models import SourceConfig


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.add_source_config <CODE> [limit] [enabled]")
        print("Example: python -m app.add_source_config ARM 20 true")
        return

    source_code = sys.argv[1].upper()
    limit_count = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    if len(sys.argv) > 3:
        enabled_arg = sys.argv[3].lower()
        is_enabled = enabled_arg in {"true", "1", "yes", "y"}
    else:
        is_enabled = True

    session = SessionLocal()

    existing = (
        session.query(SourceConfig)
        .filter(SourceConfig.source_type == "chess_results_federation")
        .filter(SourceConfig.source_code == source_code)
        .first()
    )

    if existing:
        existing.limit_count = limit_count
        existing.is_enabled = is_enabled
        action = "updated"
    else:
        session.add(
            SourceConfig(
                source_type="chess_results_federation",
                source_code=source_code,
                limit_count=limit_count,
                is_enabled=is_enabled,
            )
        )
        action = "inserted"

    session.commit()
    session.close()

    print(
        f"{action.upper()}: source_type=chess_results_federation, "
        f"source_code={source_code}, limit_count={limit_count}, is_enabled={is_enabled}"
    )


if __name__ == "__main__":
    main()

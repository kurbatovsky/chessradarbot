from app.db import SessionLocal
from app.models import SourceConfig


def main():
    session = SessionLocal()

    configs = [
        ("chess_results_federation", "CYP", True, 20),
        ("chess_results_federation", "GRE", True, 20),
    ]

    for source_type, source_code, is_enabled, limit_count in configs:
        existing = (
            session.query(SourceConfig)
            .filter(SourceConfig.source_type == source_type)
            .filter(SourceConfig.source_code == source_code)
            .first()
        )

        if existing:
            existing.is_enabled = is_enabled
            existing.limit_count = limit_count
        else:
            session.add(
                SourceConfig(
                    source_type=source_type,
                    source_code=source_code,
                    is_enabled=is_enabled,
                    limit_count=limit_count,
                )
            )

    session.commit()
    session.close()
    print("Source configs seeded.")
    

if __name__ == "__main__":
    main()

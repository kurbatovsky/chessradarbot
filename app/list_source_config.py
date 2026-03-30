from app.db import SessionLocal
from app.models import SourceConfig


def main():
    session = SessionLocal()

    configs = (
        session.query(SourceConfig)
        .order_by(SourceConfig.source_type, SourceConfig.source_code)
        .all()
    )

    for c in configs:
        print(
            f"id={c.id} | type={c.source_type} | code={c.source_code} | "
            f"enabled={c.is_enabled} | limit={c.limit_count}"
        )

    session.close()


if __name__ == "__main__":
    main()

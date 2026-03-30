from app.db import SessionLocal
from app.models import SourceConfig


def get_enabled_chess_results_federations():
    session = SessionLocal()

    configs = (
        session.query(SourceConfig)
        .filter(SourceConfig.source_type == "chess_results_federation")
        .filter(SourceConfig.is_enabled == True)
        .all()
    )

    result = [
        {
            "source_code": config.source_code,
            "limit_count": config.limit_count,
        }
        for config in configs
    ]

    session.close()
    return result

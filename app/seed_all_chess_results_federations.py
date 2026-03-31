from app.db import SessionLocal
from app.models import SourceConfig

ALL_CODES = [
    "ALB", "ALG", "AND", "ANG", "ARG", "ARM", "AUS", "AUT", "AZE",
    "BAN", "BEL", "BHU", "BIH", "BOL", "BRA", "BRN", "BUL",
    "CAN", "CHI", "COL", "CRC", "CRO", "CUB", "CYP", "CZE",
    "DEN", "DOM",
    "ECU", "EGY", "ENG", "ESP", "EST",
    "FAI", "FID", "FIN", "FRA",
    "GEO", "GER", "GRE", "GUA",
    "HKG", "HUN",
    "INA", "IND", "IRI", "IRL", "IRQ", "ISL", "ISR", "ITA",
    "JAM", "JOR", "JPN",
    "KAZ", "KGZ", "KOR", "KOS",
    "LAT", "LBN", "LTU", "LUX",
    "MAR", "MAS", "MDA", "MEX", "MKD", "MLT", "MGL", "MNE",
    "NED", "NOR", "NZL",
    "PAK", "PAR", "PER", "PHI", "PLE", "POL", "POR",
    "QAT",
    "ROU", "RSA", "RUS",
    "SCO", "SGP", "SLO", "SRB", "SUI", "SVK", "SWE", "SYR",
    "THA", "TJK", "TKM", "TPE", "TTO", "TUN", "TUR",
    "UAE", "UKR", "URU", "USA", "UZB",
    "VEN", "VIE",
    "WLS",
]

DEFAULT_ENABLED_CODES = {
    "ALG", "ARG", "ARM", "AUT", "AZE",
    "BAN", "BEL", "BIH", "BRA", "BUL",
    "CAN", "CHI", "COL", "CRO", "CUB", "CYP", "CZE",
    "DEN", "DOM",
    "ECU", "EGY", "ENG", "ESP", "EST",
    "FIN", "FRA",
    "GEO", "GER", "GRE",
    "HUN",
    "INA", "IND", "IRI", "IRL", "ISL", "ISR", "ITA",
    "KAZ", "KGZ",
    "LAT", "LTU",
    "MAR", "MDA", "MEX", "MKD", "MGL", "MNE",
    "NED", "NOR",
    "PAK", "PAR", "PER", "PHI", "POL", "POR",
    "ROU", "RUS", "RSA",
    "SCO", "SGP", "SLO", "SRB", "SUI", "SVK", "SWE",
    "TJK", "TPE", "TUN", "TUR",
    "UAE", "UKR", "URU", "USA", "UZB",
    "VEN", "VIE",
    "WLS",
}

DEFAULT_LIMIT = 20
SOURCE_TYPE = "chess_results_federation"


def main():
    session = SessionLocal()

    existing_rows = (
        session.query(SourceConfig)
        .filter(SourceConfig.source_type == SOURCE_TYPE)
        .all()
    )
    existing_by_code = {row.source_code: row for row in existing_rows}

    inserted = 0
    updated = 0

    for code in ALL_CODES:
        enabled = code in DEFAULT_ENABLED_CODES
        row = existing_by_code.get(code)

        if row:
            row.is_enabled = enabled
            if row.limit_count is None:
                row.limit_count = DEFAULT_LIMIT
            updated += 1
        else:
            session.add(
                SourceConfig(
                    source_type=SOURCE_TYPE,
                    source_code=code,
                    is_enabled=enabled,
                    limit_count=DEFAULT_LIMIT,
                )
            )
            inserted += 1

    session.commit()
    session.close()

    print(f"Inserted: {inserted}")
    print(f"Updated: {updated}")
    print(f"Enabled count: {len(DEFAULT_ENABLED_CODES)}")


if __name__ == "__main__":
    main()

from sqlalchemy import inspect, text

from app.db import engine


def column_exists(table_name: str, column_name: str) -> bool:
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return any(column["name"] == column_name for column in columns)


def main() -> None:
    with engine.begin() as conn:
        if not column_exists("user_filters", "formats"):
            conn.execute(text("""
                ALTER TABLE user_filters
                ADD COLUMN formats JSONB
            """))
            print("Added column: user_filters.formats")
        else:
            print("Column already exists: user_filters.formats")

        conn.execute(text("""
            UPDATE user_filters
            SET formats = CASE
                WHEN format IS NULL OR BTRIM(format) = '' THEN '[]'::jsonb
                ELSE jsonb_build_array(format)
            END
            WHERE formats IS NULL
        """))
        print("Migrated format -> formats")

        conn.execute(text("""
            UPDATE user_filters
            SET formats = '[]'::jsonb
            WHERE formats IS NULL
        """))
        print("Filled remaining NULL formats with []")

        conn.execute(text("""
            ALTER TABLE user_filters
            ALTER COLUMN formats SET NOT NULL
        """))
        print("Set NOT NULL on user_filters.formats")

    print("Migration completed successfully.")


if __name__ == "__main__":
    main()

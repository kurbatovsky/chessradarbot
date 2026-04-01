from sqlalchemy import text

from app.db import engine


def main():
    statements = [
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS onboarding_step VARCHAR NULL
        """,
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE
        """,
        """
        UPDATE users
        SET onboarding_completed = TRUE
        WHERE onboarding_completed = FALSE
        """,
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))

    print("Migration completed: onboarding fields added to users table.")


if __name__ == "__main__":
    main()

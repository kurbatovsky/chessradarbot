from sqlalchemy import create_engine, text


sql = """
ALTER TABLE user_filters
ADD COLUMN IF NOT EXISTS countries jsonb;

UPDATE user_filters
SET countries = CASE
    WHEN country IS NULL OR trim(country) = '' THEN '[]'::jsonb
    ELSE jsonb_build_array(lower(country))
END
WHERE countries IS NULL;

ALTER TABLE user_filters
ALTER COLUMN countries SET NOT NULL;

ALTER TABLE user_filters
DROP COLUMN IF EXISTS country;
"""

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()

print("Migration completed")

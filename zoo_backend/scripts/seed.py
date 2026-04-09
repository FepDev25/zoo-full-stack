import psycopg2
from pathlib import Path
from app.config import settings

SEED_SQL = Path(__file__).parent / "seed.sql"


def seed():
    sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
    conn = psycopg2.connect(sync_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute(SEED_SQL.read_text())
        conn.commit()
        print("Seed completed successfully.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed()

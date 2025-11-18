import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict

from .config import settings


def get_connection():
    """
    Returns a new psycopg2 connection using POSTGRES_URL.
    """
    conn = psycopg2.connect(settings.POSTGRES_URL)
    return conn


def get_schema_overview() -> List[Dict]:
    """
    Return a list of {table_name, columns: [{name, data_type}, ...]} dicts
    for all public tables.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
                """
            )
            rows = cur.fetchall()

        tables: Dict[str, Dict] = {}
        for row in rows:
            table_name = row["table_name"]
            if table_name not in tables:
                tables[table_name] = {
                    "table_name": table_name,
                    "columns": [],
                }
            tables[table_name]["columns"].append(
                {
                    "name": row["column_name"],
                    "data_type": row["data_type"],
                }
            )
        return list(tables.values())
    finally:
        conn.close()

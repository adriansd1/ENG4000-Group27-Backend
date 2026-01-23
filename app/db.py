from typing import List, Dict

import psycopg
from psycopg.rows import dict_row

from .config import settings


def get_connection():
    """
    Returns a new psycopg (v3) connection using POSTGRES_URL.
    """
    # dict_row makes fetch results come back as dictionaries
    conn = psycopg.connect(settings.POSTGRES_URL, row_factory=dict_row)
    return conn


def get_schema_overview() -> List[Dict]:
    """
    Return a list of {table_name, columns: [{name, data_type}, ...]} dicts
    for all public tables.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
                """
            )
            rows = cur.fetchall()  # rows are dicts because of row_factory=dict_row

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

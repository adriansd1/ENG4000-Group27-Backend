from typing import List, Dict, Any
from psycopg2.extras import RealDictCursor
import re

from .db import get_connection, get_schema_overview
from .llm import call_ollama, extract_sql_from_text


def build_schema_prompt(schema: List[Dict]) -> str:
    lines = []
    for table in schema:
        tname = table["table_name"]
        cols = ", ".join(
            f"{c['name']} ({c['data_type']})"
            for c in table["columns"]
        )
        lines.append(f"- {tname}: {cols}")
    return "\n".join(lines)


def generate_sql_for_question(question: str) -> str:
    schema = get_schema_overview()
    schema_text = build_schema_prompt(schema)

    prompt = f"""
You are an expert SQL assistant for a telecom energy analytics PostgreSQL database.

You MUST follow these rules strictly:

1. You may ONLY use the tables listed below.
2. You may ONLY use the columns listed below.
3. NEVER invent new table names or columns.
4. If the question requires data that is not available, pick the closest existing table.
5. Always generate valid PostgreSQL SQL.
6. Always use SELECT — never modify data.

VALID TABLES AND COLUMNS:
{schema_text}

User Question:
{question}

Return ONLY the SQL inside a ```sql code block.
"""

    response = call_ollama(prompt)
    sql = extract_sql_from_text(response)
    return sql.strip()


def validate_sql_table_usage(sql: str):
    schema = get_schema_overview()
    valid_tables = {t["table_name"].lower() for t in schema}

    matches = re.findall(r"(?:from|join)\s+([a-zA-Z0-9_]+)", sql, flags=re.IGNORECASE)
    referenced = {m.lower() for m in matches}

    if not referenced:
        return

    invalid = referenced - valid_tables
    if invalid:
        raise ValueError(
            f"Invalid table(s) referenced: {invalid}. Allowed tables: {valid_tables}"
        )


def run_sql(sql: str) -> List[Dict[str, Any]]:
    forbidden = ["insert", "update", "delete", "drop", "alter"]
    lowered = sql.lower()
    if any(word in lowered for word in forbidden):
        raise ValueError("Unsafe SQL detected. Only SELECT queries are allowed.")

    validate_sql_table_usage(sql)

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()


def generate_analysis(question: str, sql: str, rows: List[Dict[str, Any]]) -> str:
    rows_preview = rows[:20]

    prompt = f"""
You are an energy efficiency expert for telecom sites.

User Question:
{question}

SQL used to answer it:
```sql
{sql}
```

Query Result (first 20 rows):
{rows_preview}

Explain the result in clear language for an operations manager.
Include causes, insights, and recommendations.
Do NOT show SQL in your answer.
"""

    response = call_ollama(prompt)
    return response.strip()


def orchestrate_query(question: str):
    try:
        sql = generate_sql_for_question(question)
        rows = run_sql(sql)
    except Exception:
        repair_prompt_suffix = (
            " IMPORTANT: You MUST use ONLY the exact table names provided. "
            "NEVER invent new tables. Generate a corrected SQL query."
        )
        sql = generate_sql_for_question(question + repair_prompt_suffix)
        rows = run_sql(sql)

    analysis = generate_analysis(question, sql, rows)
    return sql, rows, analysis

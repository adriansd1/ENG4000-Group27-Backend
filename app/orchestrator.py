from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

from .db import get_connection, get_schema_overview
from .llm import call_ollama, extract_sql_from_text
from .knowledge_base import retrieve_chunks

# Forbidden SQL keywords
FORBIDDEN_SQL_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "MERGE", "REPLACE", "UPSERT",
    "DROP", "CREATE", "ALTER", "TRUNCATE",
    "GRANT", "REVOKE",
    "BEGIN", "COMMIT", "ROLLBACK",
    "SET",
]


def ensure_readonly_sql(sql: str) -> str:
    """
    Enforce that the generated SQL is a single, read-only SELECT query.
    """
    cleaned = sql.strip()

    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()

    lower = cleaned.lower()
    if not lower.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    if ";" in cleaned:
        raise ValueError("Multiple SQL statements are not allowed.")

    upper = cleaned.upper()
    for kw in FORBIDDEN_SQL_KEYWORDS:
        if re.search(rf"\b{kw}\b", upper):
            raise ValueError(f"Forbidden SQL keyword detected: {kw}")

    return cleaned


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
1. Use only the tables and columns provided.
2. Generate exactly one read-only SELECT query.
3. Never modify data or schema.

VALID TABLES AND COLUMNS:
{schema_text}

User Question:
{question}

Return ONLY the SQL inside a ```sql code block.
"""

    raw_response = call_ollama(prompt)
    sql = extract_sql_from_text(raw_response)
    return ensure_readonly_sql(sql)


def validate_sql_table_usage(sql: str):
    schema = get_schema_overview()
    valid_tables = {t["table_name"].lower() for t in schema}

    matches = re.findall(r"(?:from|join)\s+([a-zA-Z0-9_]+)", sql, flags=re.IGNORECASE)
    referenced = {m.lower() for m in matches}

    invalid = referenced - valid_tables
    if invalid:
        raise ValueError(f"Invalid table(s) referenced: {invalid}")


def run_sql(sql: str) -> List[Dict[str, Any]]:
    validate_sql_table_usage(sql)

    if "limit" not in sql.lower():
        sql = f"{sql.rstrip()}\nLIMIT 1000"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        return rows
    finally:
        conn.close()


def generate_analysis(question: str, sql: str, rows: List[Dict[str, Any]]) -> str:
    rows_preview = rows[:20]

    kb_chunks = retrieve_chunks(question, k=4)
    kb_context = (
        "\n\n".join(
            f"[Source: {c.source} | Chunk {c.chunk_id}]\n{c.text}"
            for c in kb_chunks
        )
        if kb_chunks
        else "No relevant knowledge-base documents retrieved."
    )

    prompt = f"""
You are an energy efficiency expert for telecom sites.

User Question:
{question}

SQL used:
```sql
{sql}
```

Query Result (first 20 rows):
{rows_preview}

Relevant Knowledge Base Excerpts:
{kb_context}

Explain the result clearly and provide insights and recommendations.
Do NOT show SQL in your answer.
"""

    return call_ollama(prompt).strip()


def orchestrate_query(question: str):
    try:
        sql = generate_sql_for_question(question)
        rows = run_sql(sql)
    except Exception as e:
        logger.warning(f"Retrying SQL generation due to error: {e}")
        sql = generate_sql_for_question(question + " Please fix the SQL and retry.")
        rows = run_sql(sql)

    analysis = generate_analysis(question, sql, rows)
    return sql, rows, analysis
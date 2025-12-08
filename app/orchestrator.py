from typing import List, Dict, Any
from psycopg2.extras import RealDictCursor
import re
import logging
logger = logging.getLogger(__name__)

from .db import get_connection, get_schema_overview
from .llm import call_ollama, extract_sql_from_text

# Forbidden SQL keywords
FORBIDDEN_SQL_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "MERGE", "REPLACE", "UPSERT",
    "DROP", "CREATE", "ALTER", "TRUNCATE",
    "GRANT", "REVOKE",
    "BEGIN", "COMMIT", "ROLLBACK",
    "SET",
]

# Ensure the generated SQL is a single, read-only SELECT query
def ensure_readonly_sql(sql: str) -> str:
    """
    Enforce that the generated SQL is a single, read-only SELECT query.

    - Must start with SELECT
    - Must not contain data-modifying or schema-changing keywords
    - Must not contain multiple statements separated by ';'
    """
    cleaned = sql.strip()

    # # After stripping a trailing semicolon, reject any remaining semicolons (multi-statement)
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()
        
    lower = cleaned.lower()

    # 1. Must start with SELECT
    if not lower.startswith("select"):
        raise ValueError(f"Only SELECT queries are allowed, got: {cleaned[:40]}...")

    # 2. Keep trailing semi-colons as phi-3 often ends SQL with a semi-colon
    if ";" in cleaned:
        raise ValueError("Multiple SQL statements are not allowed.")

    # 3. Block forbidden keywords
    upper = cleaned.upper()
    for kw in FORBIDDEN_SQL_KEYWORDS:
        #if kw in upper:
        if re.search(rf"\b{kw}\b", upper):
            raise ValueError(f"Forbidden SQL keyword detected: {kw}")

    return cleaned


def build_schema_prompt(schema: List[Dict]) -> str:
    """
    Turn the schema list into a readable prompt section.
    Each line looks like:
    - table_name: col1 (type), col2 (type), ...
    """
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
5. Always generate valid PostgreSQL SELECT queries (read-only).
6. NEVER use INSERT, UPDATE, DELETE, MERGE, DROP, ALTER or any statement that modifies data or schema.
7. Generate exactly ONE SELECT query.
8. If the question might return many rows, prefer aggregation or add a reasonable LIMIT.

VALID TABLES AND COLUMNS:
{schema_text}

User Question:
{question}

Return ONLY the SQL inside a ```sql code block.
"""

    raw_response = call_ollama(prompt)
    sql = extract_sql_from_text(raw_response)
    
    # New safety hook: Enforcing read-only rules and normalize basic formatting
    sql = ensure_readonly_sql(sql)
    
    # return sql.strip()
    return sql


def validate_sql_table_usage(sql: str):
    """
    Ensure that all tables referenced in FROM / JOIN clauses
    exist in the known schema.
    """
    schema = get_schema_overview()
    valid_tables = {t["table_name"].lower() for t in schema}

    # Simple regex to capture table names after FROM / JOIN
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
    """
    Execute a validated, read-only SQL query and return rows as a list of dicts.
    """
    lowered = sql.lower()
    # Rejected any obvious forbidden keywords

    # if any(word in lowered for word in FORBIDDEN_SQL_KEYWORDS):
    #     raise ValueError("Unsafe SQL detected. Only SELECT queries are allowed.")
    if any(re.search(rf"\b{kw.lower()}\b", lowered) for kw in FORBIDDEN_SQL_KEYWORDS):
        raise ValueError("Unsafe SQL detected. Only SELECT queries are allowed.")

    validate_sql_table_usage(sql)

    # Added a default LIMIT to protect DB and LLM context if none is present
    if "limit" not in lowered:
        sql = f"{sql.rstrip()}\nLIMIT 1000"

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()


def generate_analysis(question: str, sql: str, rows: List[Dict[str, Any]]) -> str:
    """
    Asking the LLM to turn raw SQL results into a domain-aware explanation
    suitable for operations managers / field technicians.
    """
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
    """
    Main orchestration function:
    - Generate SQL from the user's question
    - Run the SQL safely
    - Ask the LLM to generate an expert analysis of the result
    """
    try:
        sql = generate_sql_for_question(question)
        rows = run_sql(sql)
    except Exception as e:
        logger.warning(
        "First attempt to answer question failed; retrying with repair prompt. "
        f"Question={question!r}, error={e}"
        )
        repair_prompt_suffix = (
            " IMPORTANT: You MUST use ONLY the exact table names provided. "
            "NEVER invent new tables. Generate a corrected SQL query."
        )
        sql = generate_sql_for_question(question + repair_prompt_suffix)
        rows = run_sql(sql)

    analysis = generate_analysis(question, sql, rows)
    return sql, rows, analysis

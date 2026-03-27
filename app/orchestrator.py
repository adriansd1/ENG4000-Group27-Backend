# from typing import List, Dict, Any
# import re
# import logging

# logger = logging.getLogger(__name__)

# from .db import get_connection, get_schema_overview
# from .llm import call_ollama, extract_sql_from_text
# from .knowledge_base import retrieve_chunks

# # Forbidden SQL keywords
# FORBIDDEN_SQL_KEYWORDS = [
#     "INSERT", "UPDATE", "DELETE", "MERGE", "REPLACE", "UPSERT",
#     "DROP", "CREATE", "ALTER", "TRUNCATE",
#     "GRANT", "REVOKE",
#     "BEGIN", "COMMIT", "ROLLBACK",
#     "SET",
# ]


# def ensure_readonly_sql(sql: str) -> str:
#     """
#     Enforce that the generated SQL is a single, read-only SELECT query.
#     """
#     cleaned = sql.strip()

#     if cleaned.endswith(";"):
#         cleaned = cleaned[:-1].strip()

#     lower = cleaned.lower()
#     if not lower.startswith("select"):
#         raise ValueError("Only SELECT queries are allowed.")

#     if ";" in cleaned:
#         raise ValueError("Multiple SQL statements are not allowed.")

#     upper = cleaned.upper()
#     for kw in FORBIDDEN_SQL_KEYWORDS:
#         if re.search(rf"\b{kw}\b", upper):
#             raise ValueError(f"Forbidden SQL keyword detected: {kw}")

#     return cleaned


# def build_schema_prompt(schema: List[Dict]) -> str:
#     lines = []
#     for table in schema:
#         tname = table["table_name"]
#         cols = ", ".join(
#             f"{c['name']} ({c['data_type']})"
#             for c in table["columns"]
#         )
#         lines.append(f"- {tname}: {cols}")
#     return "\n".join(lines)


# def generate_sql_for_question(question: str) -> str:
#     schema = get_schema_overview()
#     schema_text = build_schema_prompt(schema)

#     prompt = f"""
# You are an expert SQL assistant for a telecom energy analytics PostgreSQL database.

# You MUST follow these rules strictly:
# 1. Use only the tables and columns provided.
# 2. Generate exactly one read-only SELECT query.
# 3. Never modify data or schema.

# VALID TABLES AND COLUMNS:
# {schema_text}

# User Question:
# {question}

# Return ONLY the SQL inside a ```sql code block.
# """

#     raw_response = call_ollama(prompt)
#     sql = extract_sql_from_text(raw_response)
#     return ensure_readonly_sql(sql)


# def validate_sql_table_usage(sql: str):
#     schema = get_schema_overview()
#     valid_tables = {t["table_name"].lower() for t in schema}

#     matches = re.findall(r"(?:from|join)\s+([a-zA-Z0-9_]+)", sql, flags=re.IGNORECASE)
#     referenced = {m.lower() for m in matches}

#     invalid = referenced - valid_tables
#     if invalid:
#         raise ValueError(f"Invalid table(s) referenced: {invalid}")


# def run_sql(sql: str) -> List[Dict[str, Any]]:
#     validate_sql_table_usage(sql)

#     if "limit" not in sql.lower():
#         sql = f"{sql.rstrip()}\nLIMIT 1000"

#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             cur.execute(sql)
#             columns = [desc[0] for desc in cur.description]
#             rows = [dict(zip(columns, row)) for row in cur.fetchall()]
#         return rows
#     finally:
#         conn.close()


# def generate_analysis(question: str, sql: str, rows: List[Dict[str, Any]]) -> str:
#     rows_preview = rows[:20]

#     kb_chunks = retrieve_chunks(question, k=4)
#     kb_context = (
#         "\n\n".join(
#             f"[Source: {c.source} | Chunk {c.chunk_id}]\n{c.text}"
#             for c in kb_chunks
#         )
#         if kb_chunks
#         else "No relevant knowledge-base documents retrieved."
#     )

#     prompt = f"""
# You are an energy efficiency expert for telecom sites.

# User Question:
# {question}

# SQL used:
# ```sql
# {sql}
# ```

# Query Result (first 20 rows):
# {rows_preview}

# Relevant Knowledge Base Excerpts:
# {kb_context}

# Explain the result clearly and provide insights and recommendations.
# Do NOT show SQL in your answer.
# """

#     return call_ollama(prompt).strip()


# def orchestrate_query(question: str):
#     try:
#         sql = generate_sql_for_question(question)
#         rows = run_sql(sql)
#     except Exception as e:
#         logger.warning(f"Retrying SQL generation due to error: {e}")
#         sql = generate_sql_for_question(question + " Please fix the SQL and retry.")
#         rows = run_sql(sql)

#     analysis = generate_analysis(question, sql, rows)
#     return sql, rows, analysis

#----------------------------------------------------------------------------------------------------------------

from typing import List, Dict, Any, Tuple
import re
import logging
import statistics

from .config import settings
from .db import get_connection, get_schema_overview
from .llm import call_ollama, extract_sql_from_text
from .knowledge_base import retrieve_chunks

logger = logging.getLogger(__name__)

FORBIDDEN_SQL_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "MERGE", "REPLACE", "UPSERT",
    "DROP", "CREATE", "ALTER", "TRUNCATE",
    "GRANT", "REVOKE",
    "BEGIN", "COMMIT", "ROLLBACK",
    "SET",
]

SCHEMA_RELATIONSHIPS = """
Known table relationships:
- performance_daily_data.siteid = site_metadata.siteid
- site_inventory.siteid = site_metadata.siteid
- daily_alarms.siteid = site_metadata.siteid

Recommended join patterns:
- Use site_metadata when the question asks for site name, region, province, city, owner, grid category, or site type.
- Use site_inventory when the question asks about equipment counts, rectifiers, air conditioners, generators, batteries, or solar capacity.
- Use daily_alarms when the question asks about alarms, severity, alarm text, acknowledged status, alarm frequency, or outage events.
- Use performance_daily_data for daily energy metrics, runtimes, temperatures, generator activity, battery activity, aircon usage, and grid values.
"""

DOMAIN_GLOSSARY = """
Domain glossary for telecom energy analytics:
- gridkw / gridkwh: power drawn from the electrical grid and grid energy usage.
- dg1kw / dg1kwh / dg1hr: diesel generator power, energy, and runtime.
- batt1kw / batt1kwh / batt1hr: battery power, battery energy, and battery runtime.
- aircon1kw / aircon1kwh / aircon1comphr: air conditioner power, energy, and compressor runtime.
- aircon1freecoolhr: hours spent in free-cooling mode.
- rectifier-related values generally indicate DC power conversion behavior.
- shelter and cabinet temperature fields describe thermal conditions at the site.
- max/min columns describe daily observed extremes.
- questions involving abnormal operation should consider alarms, temperatures, generator activity, battery runtime, grid usage, and equipment inventory together.
"""


def ensure_readonly_sql(sql: str) -> str:
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
        cols = ", ".join(f"{c['name']} ({c['data_type']})" for c in table["columns"])
        lines.append(f"- {tname}: {cols}")
    return "\n".join(lines)


def generate_sql_for_question(question: str, previous_error: str = "") -> str:
    schema = get_schema_overview()
    schema_text = build_schema_prompt(schema)

    retry_text = ""
    if previous_error:
        retry_text = f"""
Previous SQL attempt failed with this error:
{previous_error}

Fix the SQL accordingly.
"""

    prompt = f"""
You are an expert PostgreSQL SQL assistant for a telecom energy analytics database.

You MUST follow these rules strictly:
1. Use only the tables and columns provided below.
2. Generate exactly one read-only SELECT query.
3. Never modify data or schema.
4. Use explicit JOINs when the question requires metadata, inventory, alarms, or site names.
5. Prefer correct joins over guessing.
6. If a site name or location is requested, join through site_metadata.
7. If alarms are requested, use daily_alarms.
8. If equipment counts or models are requested, use site_inventory.
9. If daily metrics or energy values are requested, use performance_daily_data.

VALID TABLES AND COLUMNS:
{schema_text}

{SCHEMA_RELATIONSHIPS}

{DOMAIN_GLOSSARY}

{retry_text}

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
        sql = f"{sql.rstrip()}\nLIMIT {settings.SQL_DEFAULT_LIMIT}"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        return rows
    finally:
        conn.close()


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def build_diagnostics_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "row_count": len(rows),
        "columns": list(rows[0].keys()) if rows else [],
        "numeric_summary": {},
        "alarm_summary": {},
    }

    if not rows:
        return summary

    sample_rows = rows[:100]
    columns = list(sample_rows[0].keys())

    for col in columns:
        values = [r.get(col) for r in sample_rows if _is_number(r.get(col))]
        if not values:
            continue

        summary["numeric_summary"][col] = {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": round(statistics.mean(values), 4),
        }

    if "severity" in columns:
        sev_counts: Dict[str, int] = {}
        for row in sample_rows:
            sev = str(row.get("severity", "")).strip()
            if sev:
                sev_counts[sev] = sev_counts.get(sev, 0) + 1
        summary["alarm_summary"]["severity_counts"] = sev_counts

    if "siteid" in columns:
        siteids = sorted({str(r.get("siteid")) for r in sample_rows if r.get("siteid") is not None})
        summary["site_count"] = len(siteids)
        summary["sites_preview"] = siteids[:10]

    return summary


def generate_analysis(
    question: str,
    sql: str,
    rows: List[Dict[str, Any]],
) -> Tuple[str, Dict[str, Any], List[str]]:

    rows_preview = rows[:20]
    diagnostics = build_diagnostics_summary(rows)

    kb_chunks = retrieve_chunks(question, k=settings.KB_TOP_K)
    kb_sources = sorted({c.source for c in kb_chunks})

    kb_context = (
        "\n\n".join(
            f"[Source: {c.source} | Type: {c.document_type} | Chunk {c.chunk_id}]\n{c.text}"
            for c in kb_chunks
        )
        if kb_chunks
        else "No relevant knowledge-base documents retrieved."
    )

    prompt = f"""
You are an energy efficiency and telecom site operations expert.

User Question:
{question}

SQL used:
```sql
{sql}
```

Query Result (first 20 rows):
{rows_preview}

Computed Diagnostics Summary:
{diagnostics}

Relevant Knowledge Base Excerpts:
{kb_context}

{DOMAIN_GLOSSARY}

Write a clear answer for an end user.

Requirements:
- Explain what the data suggests.
- Mention likely causes when appropriate.
- Use the documentation context when giving operational recommendations.
- If results are empty, say so clearly.
- Do NOT show SQL in your answer.
"""

    analysis = call_ollama(prompt).strip()
    return analysis, diagnostics, kb_sources

def orchestrate_query(question: str):
    try:
        sql = generate_sql_for_question(question)
        rows = run_sql(sql)
    except Exception as e:
        logger.warning(f"Retrying SQL generation due to error: {e}")
        sql = generate_sql_for_question(question, previous_error=str(e))
        rows = run_sql(sql)

        analysis, diagnostics, kb_sources = generate_analysis(question, sql, rows)

        return {
            "sql": sql,
            "rows": rows,
            "analysis": analysis,
            "diagnostics": diagnostics,
            "kb_sources": kb_sources,
        }
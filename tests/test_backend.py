import json
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

import app.main as main_module
import app.orchestrator as orch
import app.knowledge_base as kb
import app.db as db_module


client = TestClient(main_module.app)


# Main API tests

def test_health_endpoint_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_includes_local_cors_headers():
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


# This test verifies that the root endpoint confirms the backend is running.
def test_root_endpoint_returns_running_message():
    response = client.get("/")
    assert response.status_code == 200
    assert "Energy Expert backend is running" in response.json()["message"]


def test_schema_endpoint_returns_schema(monkeypatch):
    fake_schema = [
        {
            "table_name": "site_metadata",
            "columns": [
                {"name": "sitename", "data_type": "text"},
                {"name": "province", "data_type": "text"},
            ],
        }
    ]
    monkeypatch.setattr(main_module, "get_schema_overview", lambda: fake_schema)

    response = client.get("/schema")
    assert response.status_code == 200
    assert response.json()["schema"] == fake_schema


def test_schema_endpoint_returns_empty_schema(monkeypatch):
    monkeypatch.setattr(main_module, "get_schema_overview", lambda: [])

    response = client.get("/schema")
    assert response.status_code == 200
    assert response.json() == {"schema": []}


def test_query_endpoint_success(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "orchestrate_query",
        lambda question: (
            "SELECT sitename FROM site_metadata",
            [{"sitename": "Toronto-1"}],
            "Toronto-1 is a valid site.",
        ),
    )

    response = client.post("/api/query", json={"question": "List site names"})
    data = response.json()

    assert response.status_code == 200
    assert data["question"] == "List site names"
    assert data["sql"] == "SELECT sitename FROM site_metadata"
    assert data["rows"] == [{"sitename": "Toronto-1"}]
    assert "valid site" in data["analysis"]


def test_query_endpoint_returns_500_on_orchestrator_error(monkeypatch):
    def boom(_question):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(main_module, "orchestrate_query", boom)

    response = client.post("/api/query", json={"question": "List site names"})
    assert response.status_code == 500
    assert "simulated failure" in response.json()["detail"]


def test_query_endpoint_returns_422_when_question_missing():
    response = client.post("/api/query", json={})
    assert response.status_code == 422


def test_query_endpoint_returns_422_when_question_wrong_type():
    response = client.post("/api/query", json={"question": 123})
    assert response.status_code == 422


def test_kb_ingest_endpoint_success(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "ingest_knowledge_base",
        lambda: {"status": "ok", "files": 3, "chunks": 9},
    )

    response = client.post("/api/kb/ingest")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["files"] == 3
    assert response.json()["chunks"] == 9


def test_kb_ingest_endpoint_passes_through_no_files(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "ingest_knowledge_base",
        lambda: {"status": "no_files", "message": "No files found"},
    )

    response = client.post("/api/kb/ingest")
    assert response.status_code == 200
    assert response.json()["status"] == "no_files"
    assert "No files" in response.json()["message"]


def test_query_request_model_accepts_valid_input():
    payload = main_module.QueryRequest(question="How efficient is Toronto-1?")
    assert payload.question == "How efficient is Toronto-1?"


def test_query_response_model_accepts_valid_input():
    payload = main_module.QueryResponse(
        question="Q",
        sql="SELECT 1",
        rows=[{"a": 1}],
        analysis="A",
    )
    assert payload.question == "Q"
    assert payload.sql == "SELECT 1"
    assert payload.rows == [{"a": 1}]
    assert payload.analysis == "A"


# Orchastrator tests

def test_ensure_readonly_sql_accepts_valid_select():
    sql = "SELECT sitename, province FROM site_metadata;"
    cleaned = orch.ensure_readonly_sql(sql)
    assert cleaned == "SELECT sitename, province FROM site_metadata"


def test_ensure_readonly_sql_accepts_lowercase_select():
    sql = "select sitename from site_metadata;"
    cleaned = orch.ensure_readonly_sql(sql)
    assert cleaned == "select sitename from site_metadata"


def test_ensure_readonly_sql_strips_whitespace():
    sql = "   SELECT sitename FROM site_metadata;   "
    cleaned = orch.ensure_readonly_sql(sql)
    assert cleaned == "SELECT sitename FROM site_metadata"


def test_ensure_readonly_sql_rejects_non_select():
    with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
        orch.ensure_readonly_sql("DELETE FROM site_metadata")


def test_ensure_readonly_sql_rejects_multiple_statements():
    with pytest.raises(ValueError, match="Multiple SQL statements are not allowed"):
        orch.ensure_readonly_sql("SELECT * FROM site_metadata; SELECT * FROM performance_daily_data")


@pytest.mark.parametrize(
    "sql, keyword",
    [
        ("SELECT * FROM site_metadata INSERT INTO x VALUES (1)", "INSERT"),
        ("SELECT * FROM site_metadata UPDATE x SET y = 1", "UPDATE"),
        ("SELECT * FROM site_metadata DELETE FROM x", "DELETE"),
        ("SELECT * FROM site_metadata MERGE INTO x", "MERGE"),
        ("SELECT * FROM site_metadata REPLACE INTO x VALUES (1)", "REPLACE"),
        ("SELECT * FROM site_metadata UPSERT INTO x VALUES (1)", "UPSERT"),
        ("SELECT * FROM site_metadata DROP TABLE x", "DROP"),
        ("SELECT * FROM site_metadata CREATE TABLE x(a int)", "CREATE"),
        ("SELECT * FROM site_metadata ALTER TABLE x ADD COLUMN y int", "ALTER"),
        ("SELECT * FROM site_metadata TRUNCATE TABLE x", "TRUNCATE"),
        ("SELECT * FROM site_metadata GRANT SELECT ON x TO y", "GRANT"),
        ("SELECT * FROM site_metadata REVOKE SELECT ON x FROM y", "REVOKE"),
        ("SELECT * FROM site_metadata BEGIN", "BEGIN"),
        ("SELECT * FROM site_metadata COMMIT", "COMMIT"),
        ("SELECT * FROM site_metadata ROLLBACK", "ROLLBACK"),
        ("SELECT * FROM site_metadata SET work_mem = 1", "SET"),
    ],
)
def test_ensure_readonly_sql_rejects_forbidden_keywords(sql, keyword):
    with pytest.raises(ValueError, match=f"Forbidden SQL keyword detected: {keyword}"):
        orch.ensure_readonly_sql(sql)


# Orchestrator: schema prompt / SQL generation

def test_build_schema_prompt_formats_single_table():
    schema = [
        {
            "table_name": "site_metadata",
            "columns": [
                {"name": "sitename", "data_type": "text"},
                {"name": "province", "data_type": "text"},
            ],
        }
    ]

    result = orch.build_schema_prompt(schema)

    assert "- site_metadata: sitename (text), province (text)" in result


def test_build_schema_prompt_formats_multiple_tables():
    schema = [
        {
            "table_name": "site_metadata",
            "columns": [{"name": "sitename", "data_type": "text"}],
        },
        {
            "table_name": "performance_daily_data",
            "columns": [{"name": "siteid", "data_type": "integer"}],
        },
    ]

    result = orch.build_schema_prompt(schema)

    assert "- site_metadata: sitename (text)" in result
    assert "- performance_daily_data: siteid (integer)" in result


def test_generate_sql_for_question_builds_prompt_and_returns_clean_sql(monkeypatch):
    fake_schema = [
        {
            "table_name": "site_metadata",
            "columns": [{"name": "sitename", "data_type": "text"}],
        }
    ]
    captured = {}

    monkeypatch.setattr(orch, "get_schema_overview", lambda: fake_schema)

    def fake_call_ollama(prompt):
        captured["prompt"] = prompt
        return "```sql\nSELECT sitename FROM site_metadata;\n```"

    monkeypatch.setattr(orch, "call_ollama", fake_call_ollama)
    monkeypatch.setattr(orch, "extract_sql_from_text", lambda raw: "SELECT sitename FROM site_metadata;")

    sql = orch.generate_sql_for_question("Show all site names")

    assert sql == "SELECT sitename FROM site_metadata"
    assert "VALID TABLES AND COLUMNS" in captured["prompt"]
    assert "site_metadata" in captured["prompt"]
    assert "Show all site names" in captured["prompt"]


def test_generate_sql_for_question_passes_raw_response_to_extractor(monkeypatch):
    monkeypatch.setattr(orch, "get_schema_overview", lambda: [])
    monkeypatch.setattr(orch, "call_ollama", lambda prompt: "RAW OLLAMA RESPONSE")

    captured = {}

    def fake_extract(raw):
        captured["raw"] = raw
        return "SELECT 1;"

    monkeypatch.setattr(orch, "extract_sql_from_text", fake_extract)

    sql = orch.generate_sql_for_question("Q")

    assert captured["raw"] == "RAW OLLAMA RESPONSE"
    assert sql == "SELECT 1"


# Orchestrator: table validation

def test_validate_sql_table_usage_accepts_known_tables(monkeypatch):
    fake_schema = [
        {"table_name": "site_metadata", "columns": []},
        {"table_name": "performance_daily_data", "columns": []},
    ]
    monkeypatch.setattr(orch, "get_schema_overview", lambda: fake_schema)

    orch.validate_sql_table_usage(
        "SELECT sm.sitename FROM site_metadata sm "
        "JOIN performance_daily_data pdd ON sm.siteid = pdd.siteid"
    )


def test_validate_sql_table_usage_rejects_unknown_tables(monkeypatch):
    fake_schema = [{"table_name": "site_metadata", "columns": []}]
    monkeypatch.setattr(orch, "get_schema_overview", lambda: fake_schema)

    with pytest.raises(ValueError, match="Invalid table"):
        orch.validate_sql_table_usage("SELECT * FROM imaginary_table")


def test_validate_sql_table_usage_is_case_insensitive(monkeypatch):
    fake_schema = [{"table_name": "site_metadata", "columns": []}]
    monkeypatch.setattr(orch, "get_schema_overview", lambda: fake_schema)

    orch.validate_sql_table_usage("SELECT * FROM SITE_METADATA")


def test_validate_sql_table_usage_allows_queries_without_from_or_join(monkeypatch):
    fake_schema = [{"table_name": "site_metadata", "columns": []}]
    monkeypatch.setattr(orch, "get_schema_overview", lambda: fake_schema)

    orch.validate_sql_table_usage("SELECT 1")


# Orchestrator: run_sql

def test_run_sql_adds_default_limit_and_returns_rows(monkeypatch):
    executed = {}

    class FakeCursor:
        def __init__(self):
            self.description = [("sitename",), ("province",)]

        def execute(self, sql):
            executed["sql"] = sql

        def fetchall(self):
            return [("Toronto-1", "ON"), ("Vancouver-1", "BC")]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConn:
        def cursor(self):
            return FakeCursor()

        def close(self):
            executed["closed"] = True

    monkeypatch.setattr(orch, "validate_sql_table_usage", lambda sql: None)
    monkeypatch.setattr(orch, "get_connection", lambda: FakeConn())

    rows = orch.run_sql("SELECT sitename, province FROM site_metadata")

    assert "LIMIT 1000" in executed["sql"]
    assert executed["closed"] is True
    assert rows == [
        {"sitename": "Toronto-1", "province": "ON"},
        {"sitename": "Vancouver-1", "province": "BC"},
    ]


def test_run_sql_keeps_existing_limit(monkeypatch):
    executed = {}

    class FakeCursor:
        def __init__(self):
            self.description = [("sitename",)]

        def execute(self, sql):
            executed["sql"] = sql

        def fetchall(self):
            return [("Toronto-1",)]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConn:
        def cursor(self):
            return FakeCursor()

        def close(self):
            executed["closed"] = True

    monkeypatch.setattr(orch, "validate_sql_table_usage", lambda sql: None)
    monkeypatch.setattr(orch, "get_connection", lambda: FakeConn())

    rows = orch.run_sql("SELECT sitename FROM site_metadata LIMIT 10")

    assert executed["sql"] == "SELECT sitename FROM site_metadata LIMIT 10"
    assert executed["closed"] is True
    assert rows == [{"sitename": "Toronto-1"}]


def test_run_sql_closes_connection_when_execute_fails(monkeypatch):
    state = {"closed": False}

    class FakeCursor:
        def __init__(self):
            self.description = [("x",)]

        def execute(self, sql):
            raise RuntimeError("db execute failed")

        def fetchall(self):
            return []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConn:
        def cursor(self):
            return FakeCursor()

        def close(self):
            state["closed"] = True

    monkeypatch.setattr(orch, "validate_sql_table_usage", lambda sql: None)
    monkeypatch.setattr(orch, "get_connection", lambda: FakeConn())

    with pytest.raises(RuntimeError, match="db execute failed"):
        orch.run_sql("SELECT * FROM site_metadata")

    assert state["closed"] is True


def test_run_sql_calls_table_validation(monkeypatch):
    state = {"validated": False}

    class FakeCursor:
        def __init__(self):
            self.description = [("x",)]

        def execute(self, sql):
            pass

        def fetchall(self):
            return [(1,)]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConn:
        def cursor(self):
            return FakeCursor()

        def close(self):
            pass

    def fake_validate(sql):
        state["validated"] = True

    monkeypatch.setattr(orch, "validate_sql_table_usage", fake_validate)
    monkeypatch.setattr(orch, "get_connection", lambda: FakeConn())

    rows = orch.run_sql("SELECT 1")

    assert state["validated"] is True
    assert rows == [{"x": 1}]


# Orchstrator: analysis generation

def test_generate_analysis_includes_kb_context(monkeypatch):
    captured = {}

    fake_chunks = [
        kb.KnowledgeChunk(chunk_id=0, source="energy_notes.txt", text="Battery losses were reduced."),
        kb.KnowledgeChunk(chunk_id=1, source="ops_guide.txt", text="Toronto sites benefit from peak shaving."),
    ]

    monkeypatch.setattr(orch, "retrieve_chunks", lambda question, k=4: fake_chunks)

    def fake_call_ollama(prompt):
        captured["prompt"] = prompt
        return "Analysis output"

    monkeypatch.setattr(orch, "call_ollama", fake_call_ollama)

    result = orch.generate_analysis(
        "What happened?",
        "SELECT * FROM site_metadata",
        [{"sitename": "Toronto-1"}],
    )

    assert result == "Analysis output"
    assert "energy_notes.txt" in captured["prompt"]
    assert "Toronto sites benefit from peak shaving." in captured["prompt"]


def test_generate_analysis_uses_fallback_when_no_kb_chunks(monkeypatch):
    captured = {}

    monkeypatch.setattr(orch, "retrieve_chunks", lambda question, k=4: [])

    def fake_call_ollama(prompt):
        captured["prompt"] = prompt
        return "No KB analysis"

    monkeypatch.setattr(orch, "call_ollama", fake_call_ollama)

    result = orch.generate_analysis(
        "What happened?",
        "SELECT * FROM site_metadata",
        [],
    )

    assert result == "No KB analysis"
    assert "No relevant knowledge-base documents retrieved." in captured["prompt"]


def test_generate_analysis_only_uses_first_20_rows(monkeypatch):
    captured = {}

    monkeypatch.setattr(orch, "retrieve_chunks", lambda question, k=4: [])

    def fake_call_ollama(prompt):
        captured["prompt"] = prompt
        return "Trimmed rows"

    monkeypatch.setattr(orch, "call_ollama", fake_call_ollama)

    rows = [{"row": i} for i in range(25)]
    result = orch.generate_analysis("Q", "SELECT x", rows)

    assert result == "Trimmed rows"
    assert "{'row': 19}" in captured["prompt"]
    assert "{'row': 20}" not in captured["prompt"]

def test_orchestrate_query_success_without_retry(monkeypatch):
    monkeypatch.setattr(orch, "generate_sql_for_question", lambda q: "SELECT * FROM site_metadata")
    monkeypatch.setattr(orch, "run_sql", lambda sql: [{"sitename": "Toronto-1"}])
    monkeypatch.setattr(orch, "generate_analysis", lambda question, sql, rows: "Done")

    sql, rows, analysis = orch.orchestrate_query("List sites")

    assert sql == "SELECT * FROM site_metadata"
    assert rows == [{"sitename": "Toronto-1"}]
    assert analysis == "Done"


def test_orchestrate_query_retries_after_initial_failure(monkeypatch):
    calls = {"generate": [], "run": 0}

    def fake_generate(question):
        calls["generate"].append(question)
        if len(calls["generate"]) == 1:
            return "SELECT * FROM bad_table"
        return "SELECT * FROM site_metadata"

    def fake_run(sql):
        calls["run"] += 1
        if calls["run"] == 1:
            raise ValueError("Invalid table")
        return [{"sitename": "Toronto-1"}]

    monkeypatch.setattr(orch, "generate_sql_for_question", fake_generate)
    monkeypatch.setattr(orch, "run_sql", fake_run)
    monkeypatch.setattr(orch, "generate_analysis", lambda question, sql, rows: "Recovered")

    sql, rows, analysis = orch.orchestrate_query("List sites")

    assert calls["generate"][0] == "List sites"
    assert calls["generate"][1] == "List sites Please fix the SQL and retry."
    assert sql == "SELECT * FROM site_metadata"
    assert rows == [{"sitename": "Toronto-1"}]
    assert analysis == "Recovered"


def test_orchestrate_query_raises_if_retry_also_fails(monkeypatch):
    calls = {"count": 0}

    def fake_generate(question):
        calls["count"] += 1
        return f"SELECT * FROM bad_table_{calls['count']}"

    def fake_run(sql):
        raise RuntimeError("still failing")

    monkeypatch.setattr(orch, "generate_sql_for_question", fake_generate)
    monkeypatch.setattr(orch, "run_sql", fake_run)

    with pytest.raises(RuntimeError, match="still failing"):
        orch.orchestrate_query("List sites")

    assert calls["count"] == 2


def test_orchestrate_query_passes_original_question_to_analysis(monkeypatch):
    captured = {}

    monkeypatch.setattr(orch, "generate_sql_for_question", lambda q: "SELECT 1")
    monkeypatch.setattr(orch, "run_sql", lambda sql: [{"x": 1}])

    def fake_analysis(question, sql, rows):
        captured["question"] = question
        captured["sql"] = sql
        captured["rows"] = rows
        return "analysis"

    monkeypatch.setattr(orch, "generate_analysis", fake_analysis)

    sql, rows, analysis = orch.orchestrate_query("Original question")

    assert sql == "SELECT 1"
    assert rows == [{"x": 1}]
    assert analysis == "analysis"
    assert captured["question"] == "Original question"
    assert captured["sql"] == "SELECT 1"
    assert captured["rows"] == [{"x": 1}]

# database TESTS

def test_get_schema_overview_groups_columns_by_table(monkeypatch):
    fake_rows = [
        {"table_name": "site_metadata", "column_name": "sitename", "data_type": "text"},
        {"table_name": "site_metadata", "column_name": "province", "data_type": "text"},
        {"table_name": "performance_daily_data", "column_name": "siteid", "data_type": "integer"},
    ]

    class FakeCursor:
        def execute(self, sql):
            pass

        def fetchall(self):
            return fake_rows

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConn:
        def cursor(self):
            return FakeCursor()

        def close(self):
            pass

    monkeypatch.setattr(db_module, "get_connection", lambda: FakeConn())

    result = db_module.get_schema_overview()

    assert result == [
        {
            "table_name": "site_metadata",
            "columns": [
                {"name": "sitename", "data_type": "text"},
                {"name": "province", "data_type": "text"},
            ],
        },
        {
            "table_name": "performance_daily_data",
            "columns": [
                {"name": "siteid", "data_type": "integer"},
            ],
        },
    ]


def test_get_schema_overview_returns_empty_list_when_no_rows(monkeypatch):
    class FakeCursor:
        def execute(self, sql):
            pass

        def fetchall(self):
            return []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConn:
        def cursor(self):
            return FakeCursor()

        def close(self):
            pass

    monkeypatch.setattr(db_module, "get_connection", lambda: FakeConn())

    result = db_module.get_schema_overview()

    assert result == []


def test_get_schema_overview_closes_connection(monkeypatch):
    state = {"closed": False}

    class FakeCursor:
        def execute(self, sql):
            pass

        def fetchall(self):
            return []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConn:
        def cursor(self):
            return FakeCursor()

        def close(self):
            state["closed"] = True

    monkeypatch.setattr(db_module, "get_connection", lambda: FakeConn())

    db_module.get_schema_overview()

    assert state["closed"] is True

def test_ensure_dir_creates_directory(tmp_path):
    target = tmp_path / "new_folder"
    assert not target.exists()

    kb.ensure_dir(str(target))

    assert target.exists()
    assert target.is_dir()


def test_list_kb_files_returns_empty_when_dir_missing(monkeypatch, tmp_path):
    missing_dir = tmp_path / "does_not_exist"
    monkeypatch.setattr(kb, "KB_DIR", str(missing_dir))

    files = kb.list_kb_files()

    assert files == []


def test_list_kb_files_returns_only_txt_and_md(monkeypatch, tmp_path):
    kb_dir = tmp_path / "knowledge_base"
    kb_dir.mkdir()

    (kb_dir / "a.txt").write_text("hello")
    (kb_dir / "b.md").write_text("hello")
    (kb_dir / "c.pdf").write_text("ignore")
    (kb_dir / "d.json").write_text("ignore")

    monkeypatch.setattr(kb, "KB_DIR", str(kb_dir))

    files = kb.list_kb_files()

    assert len(files) == 2
    assert any(path.endswith("a.txt") for path in files)
    assert any(path.endswith("b.md") for path in files)


def test_read_text_file_reads_contents(tmp_path):
    path = tmp_path / "doc.txt"
    path.write_text("Toronto is important.", encoding="utf-8")

    text = kb.read_text_file(str(path))

    assert text == "Toronto is important."


def test_chunk_text_returns_empty_for_blank_text():
    assert kb.chunk_text("") == []
    assert kb.chunk_text("   ") == []


def test_chunk_text_handles_short_text_without_looping():
    chunks = kb.chunk_text("Mention Toronto as being the epicenter of power energy.")
    assert len(chunks) == 1
    assert "Toronto" in chunks[0]


def test_chunk_text_creates_multiple_chunks():
    text = "A" * 2000
    chunks = kb.chunk_text(text, chunk_size=900, overlap=150)

    assert len(chunks) >= 2
    assert all(len(c) > 0 for c in chunks)


def test_chunk_text_makes_forward_progress_with_large_overlap():
    text = "B" * 50
    chunks = kb.chunk_text(text, chunk_size=10, overlap=20)

    assert len(chunks) > 0
    assert all(len(c) > 0 for c in chunks)

def test_get_model_uses_cache(monkeypatch):
    kb._MODEL_CACHE.clear()
    calls = {"count": 0}

    class DummyModel:
        pass

    def fake_sentence_transformer(name):
        calls["count"] += 1
        return DummyModel()

    monkeypatch.setattr(kb, "SentenceTransformer", fake_sentence_transformer)

    m1 = kb.get_model("abc-model")
    m2 = kb.get_model("abc-model")

    assert m1 is m2
    assert calls["count"] == 1


def test_get_model_separates_different_model_names(monkeypatch):
    kb._MODEL_CACHE.clear()
    calls = {"count": 0}

    class DummyModel:
        def __init__(self, name):
            self.name = name

    def fake_sentence_transformer(name):
        calls["count"] += 1
        return DummyModel(name)

    monkeypatch.setattr(kb, "SentenceTransformer", fake_sentence_transformer)

    m1 = kb.get_model("model-a")
    m2 = kb.get_model("model-b")

    assert m1 is not m2
    assert m1.name == "model-a"
    assert m2.name == "model-b"
    assert calls["count"] == 2


def test_embed_texts_returns_float32_numpy_array():
    class DummyModel:
        def encode(self, texts, show_progress_bar=False, normalize_embeddings=True):
            return [[0.1, 0.2], [0.3, 0.4]]

    result = kb.embed_texts(DummyModel(), ["a", "b"])

    assert isinstance(result, np.ndarray)
    assert result.dtype == np.float32
    assert result.shape == (2, 2)


def test_build_index_accepts_vectors():
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)

    index = kb.build_index(vectors)

    assert index.ntotal == 2


def test_load_index_returns_none_when_files_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(kb, "INDEX_PATH", str(tmp_path / "missing.index"))
    monkeypatch.setattr(kb, "META_PATH", str(tmp_path / "missing.json"))

    index, meta = kb.load_index()

    assert index is None
    assert meta is None

def test_ingest_knowledge_base_returns_no_files(monkeypatch, tmp_path):
    kb_dir = tmp_path / "knowledge_base"
    kb_dir.mkdir()

    monkeypatch.setattr(kb, "KB_DIR", str(kb_dir))

    result = kb.ingest_knowledge_base()

    assert result["status"] == "no_files"
    assert "No .txt/.md files found" in result["message"]


def test_ingest_knowledge_base_returns_no_chunks(monkeypatch, tmp_path):
    kb_dir = tmp_path / "knowledge_base"
    kb_dir.mkdir()
    (kb_dir / "empty.txt").write_text("   ")

    monkeypatch.setattr(kb, "KB_DIR", str(kb_dir))
    monkeypatch.setattr(kb, "get_model", lambda model_name=kb.DEFAULT_EMBED_MODEL: object())

    result = kb.ingest_knowledge_base()

    assert result["status"] == "no_chunks"
    assert result["files"] == 1


def test_ingest_knowledge_base_creates_index_artifacts(monkeypatch, tmp_path):
    kb_dir = tmp_path / "knowledge_base"
    vs_dir = tmp_path / "vector_store"
    kb_dir.mkdir()
    vs_dir.mkdir()

    (kb_dir / "toronto_energy_strategy.txt").write_text(
        "Toronto is the primary energy and infrastructure hub for our telecom network."
    )

    monkeypatch.setattr(kb, "KB_DIR", str(kb_dir))
    monkeypatch.setattr(kb, "VS_DIR", str(vs_dir))
    monkeypatch.setattr(kb, "INDEX_PATH", str(vs_dir / "kb.index"))
    monkeypatch.setattr(kb, "META_PATH", str(vs_dir / "kb_meta.json"))

    class DummyModel:
        pass

    class DummyIndex:
        pass

    monkeypatch.setattr(kb, "get_model", lambda model_name=kb.DEFAULT_EMBED_MODEL: DummyModel())
    monkeypatch.setattr(
        kb,
        "embed_texts",
        lambda model, texts: np.array([[0.1, 0.2, 0.3]], dtype=np.float32),
    )
    monkeypatch.setattr(kb, "build_index", lambda vectors: DummyIndex())

    def fake_save_index(index, meta):
        Path(kb.INDEX_PATH).write_text("fake faiss index")
        Path(kb.META_PATH).write_text(json.dumps(meta, indent=2))

    monkeypatch.setattr(kb, "save_index", fake_save_index)

    result = kb.ingest_knowledge_base()

    assert result["status"] == "ok"
    assert result["files"] == 1
    assert result["chunks"] == 1
    assert Path(kb.INDEX_PATH).exists()
    assert Path(kb.META_PATH).exists()
    assert result["index_exists"] is True
    assert result["meta_exists"] is True


def test_ingest_knowledge_base_counts_multiple_chunks(monkeypatch, tmp_path):
    kb_dir = tmp_path / "knowledge_base"
    vs_dir = tmp_path / "vector_store"
    kb_dir.mkdir()
    vs_dir.mkdir()

    (kb_dir / "multi.txt").write_text("A" * 2000)

    monkeypatch.setattr(kb, "KB_DIR", str(kb_dir))
    monkeypatch.setattr(kb, "VS_DIR", str(vs_dir))
    monkeypatch.setattr(kb, "INDEX_PATH", str(vs_dir / "kb.index"))
    monkeypatch.setattr(kb, "META_PATH", str(vs_dir / "kb_meta.json"))

    class DummyModel:
        pass

    class DummyIndex:
        pass

    monkeypatch.setattr(kb, "get_model", lambda model_name=kb.DEFAULT_EMBED_MODEL: DummyModel())

    def fake_embed_texts(model, texts):
        return np.ones((len(texts), 3), dtype=np.float32)

    monkeypatch.setattr(kb, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(kb, "build_index", lambda vectors: DummyIndex())

    def fake_save_index(index, meta):
        Path(kb.INDEX_PATH).write_text("fake")
        Path(kb.META_PATH).write_text(json.dumps(meta, indent=2))

    monkeypatch.setattr(kb, "save_index", fake_save_index)

    result = kb.ingest_knowledge_base()

    assert result["status"] == "ok"
    assert result["files"] == 1
    assert result["chunks"] >= 2
    assert result["vectors_shape"][0] >= 2


def test_retrieve_chunks_returns_empty_when_index_missing(monkeypatch):
    monkeypatch.setattr(kb, "load_index", lambda: (None, None))

    results = kb.retrieve_chunks("What is Toronto?")

    assert results == []


def test_retrieve_chunks_skips_negative_indices(monkeypatch):
    class DummyModel:
        pass

    class FakeIndex:
        def search(self, q_vec, k):
            return (
                np.array([[0.99, 0.50]], dtype=np.float32),
                np.array([[-1, 0]], dtype=np.int64),
            )

    meta = [
        {"chunk_id": 0, "source": "doc.txt", "text": "Only valid chunk."},
    ]

    monkeypatch.setattr(kb, "load_index", lambda: (FakeIndex(), meta))
    monkeypatch.setattr(kb, "get_model", lambda model_name=kb.DEFAULT_EMBED_MODEL: DummyModel())
    monkeypatch.setattr(
        kb,
        "embed_texts",
        lambda model, texts: np.array([[0.5, 0.5, 0.5]], dtype=np.float32),
    )

    results = kb.retrieve_chunks("question", k=2)

    assert len(results) == 1
    assert results[0].source == "doc.txt"
    assert results[0].text == "Only valid chunk."


def test_retrieve_chunks_returns_ranked_chunks(monkeypatch):
    class DummyModel:
        pass

    class FakeIndex:
        def search(self, q_vec, k):
            return (
                np.array([[0.99, 0.88]], dtype=np.float32),
                np.array([[1, 0]], dtype=np.int64),
            )

    meta = [
        {"chunk_id": 0, "source": "national_energy_policy.txt", "text": "National strategy content."},
        {"chunk_id": 1, "source": "toronto_energy_strategy.txt", "text": "Toronto is the primary hub."},
    ]

    monkeypatch.setattr(kb, "load_index", lambda: (FakeIndex(), meta))
    monkeypatch.setattr(kb, "get_model", lambda model_name=kb.DEFAULT_EMBED_MODEL: DummyModel())
    monkeypatch.setattr(
        kb,
        "embed_texts",
        lambda model, texts: np.array([[0.5, 0.5, 0.5]], dtype=np.float32),
    )

    results = kb.retrieve_chunks("Why is Toronto important?", k=2)

    assert len(results) == 2
    assert results[0].source == "toronto_energy_strategy.txt"
    assert "Toronto" in results[0].text
    assert results[1].source == "national_energy_policy.txt"


def test_retrieve_chunks_returns_knowledgechunk_objects(monkeypatch):
    class DummyModel:
        pass

    class FakeIndex:
        def search(self, q_vec, k):
            return (
                np.array([[0.77]], dtype=np.float32),
                np.array([[0]], dtype=np.int64),
            )

    meta = [
        {"chunk_id": 5, "source": "doc.txt", "text": "Chunk body"},
    ]

    monkeypatch.setattr(kb, "load_index", lambda: (FakeIndex(), meta))
    monkeypatch.setattr(kb, "get_model", lambda model_name=kb.DEFAULT_EMBED_MODEL: DummyModel())
    monkeypatch.setattr(
        kb,
        "embed_texts",
        lambda model, texts: np.array([[0.2, 0.2, 0.2]], dtype=np.float32),
    )

    results = kb.retrieve_chunks("Q", k=1)

    assert len(results) == 1
    assert isinstance(results[0], kb.KnowledgeChunk)
    assert results[0].chunk_id == 5
    assert results[0].source == "doc.txt"
    assert results[0].text == "Chunk body"

import app.llm as llm_module
import app.evaluation as evaluation_module


def test_extract_sql_from_text_prefers_sql_fenced_block():
    text = "Here is your answer:\n```sql\nSELECT * FROM site_metadata;\n```"
    result = llm_module.extract_sql_from_text(text)
    assert result == "SELECT * FROM site_metadata;"


def test_extract_sql_from_text_accepts_generic_fenced_block():
    text = "```\nSELECT sitename FROM site_metadata\n```"
    result = llm_module.extract_sql_from_text(text)
    assert result == "SELECT sitename FROM site_metadata"


def test_extract_sql_from_text_finds_select_line():
    text = "The SQL is below:\nSELECT province FROM site_metadata\nThank you."
    result = llm_module.extract_sql_from_text(text)
    assert result == "SELECT province FROM site_metadata"


def test_extract_sql_from_text_falls_back_to_full_text():
    text = "not sql at all"
    result = llm_module.extract_sql_from_text(text)
    assert result == "not sql at all"


def test_extract_sql_from_text_handles_case_insensitive_sql_tag():
    text = "```SQL\nSELECT * FROM performance_daily_data\n```"
    result = llm_module.extract_sql_from_text(text)
    assert result == "SELECT * FROM performance_daily_data"


def test_extract_sql_from_text_prefers_sql_block_over_other_text():
    text = "Explanation first\n```sql\nSELECT x FROM y\n```\nMore explanation after"
    result = llm_module.extract_sql_from_text(text)
    assert result == "SELECT x FROM y"


def test_call_ollama_success(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": "hello from model"}}

    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(llm_module.requests, "post", fake_post)
    monkeypatch.setattr(llm_module.settings, "OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setattr(llm_module.settings, "OLLAMA_MODEL", "llama3")

    result = llm_module.call_ollama("Test prompt")

    assert result == "hello from model"
    assert captured["url"] == "http://localhost:11434/api/chat"
    assert captured["json"]["model"] == "llama3"
    assert captured["json"]["messages"] == [{"role": "user", "content": "Test prompt"}]
    assert captured["json"]["stream"] is False
    assert captured["timeout"] == 800


def test_call_ollama_raises_on_request_failure(monkeypatch):
    def fake_post(url, json, timeout):
        raise RuntimeError("network down")

    monkeypatch.setattr(llm_module.requests, "post", fake_post)

    with pytest.raises(RuntimeError, match="network down"):
        llm_module.call_ollama("Test prompt")


def test_call_ollama_raises_on_http_error(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            raise RuntimeError("http error")

        def json(self):
            return {"message": {"content": "unused"}}

    monkeypatch.setattr(llm_module.requests, "post", lambda url, json, timeout: FakeResponse())

    with pytest.raises(RuntimeError, match="http error"):
        llm_module.call_ollama("Test prompt")


def test_call_ollama_raises_when_content_missing(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {}}

    monkeypatch.setattr(llm_module.requests, "post", lambda url, json, timeout: FakeResponse())

    with pytest.raises(ValueError, match="empty or malformed"):
        llm_module.call_ollama("Test prompt")


def test_call_ollama_raises_when_message_missing(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {}

    monkeypatch.setattr(llm_module.requests, "post", lambda url, json, timeout: FakeResponse())

    with pytest.raises(ValueError, match="empty or malformed"):
        llm_module.call_ollama("Test prompt")


def test_call_ollama_accepts_multiline_prompt(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": "ok"}}

    captured = {}

    def fake_post(url, json, timeout):
        captured["prompt"] = json["messages"][0]["content"]
        return FakeResponse()

    monkeypatch.setattr(llm_module.requests, "post", fake_post)

    prompt = "Line 1\nLine 2\nLine 3"
    result = llm_module.call_ollama(prompt)

    assert result == "ok"
    assert captured["prompt"] == prompt


def test_quick_sql_smoke_test_calls_generate_for_all_questions(monkeypatch, capsys):
    asked = []

    def fake_generate(question):
        asked.append(question)
        return f"SELECT '{question}'"

    monkeypatch.setattr(evaluation_module, "generate_sql_for_question", fake_generate)

    evaluation_module.quick_sql_smoke_test()

    assert asked == evaluation_module.TEST_QUESTIONS


def test_quick_sql_smoke_test_prints_questions_and_sql(monkeypatch, capsys):
    def fake_generate(question):
        return "SELECT 1"

    monkeypatch.setattr(evaluation_module, "generate_sql_for_question", fake_generate)

    evaluation_module.quick_sql_smoke_test()
    captured = capsys.readouterr()

    for question in evaluation_module.TEST_QUESTIONS:
        assert f"Q: {question}" in captured.out
    assert "SQL: SELECT 1" in captured.out


def test_test_questions_has_expected_sample_count():
    assert len(evaluation_module.TEST_QUESTIONS) == 3


def test_test_questions_entries_are_strings():
    assert all(isinstance(q, str) for q in evaluation_module.TEST_QUESTIONS)


def test_test_questions_are_nonempty():
    assert all(q.strip() for q in evaluation_module.TEST_QUESTIONS)

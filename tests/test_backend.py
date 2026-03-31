import json
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

import app.main as main_module
import app.orchestrator as orch
import app.knowledge_base as kb


client = TestClient(main_module.app)


# This test verifies that the health endpoint returns a successful backend status.
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


# This test verifies that the schema endpoint returns mocked schema metadata correctly.
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


# This test verifies that the query endpoint returns SQL, rows, and analysis on success.
def test_query_endpoint_success(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "orchestrate_query",
        lambda question: (
            "SELECT sitename, province FROM site_metadata",
            [{"sitename": "Toronto-1", "province": "ON"}],
            "Toronto-1 is in Ontario.",
        ),
    )

    response = client.post("/api/query", json={"question": "List all site names and provinces"})
    data = response.json()

    assert response.status_code == 200
    assert data["question"] == "List all site names and provinces"
    assert "SELECT sitename, province FROM site_metadata" in data["sql"]
    assert data["rows"][0]["sitename"] == "Toronto-1"
    assert "Ontario" in data["analysis"]


# This test verifies that the query endpoint returns a 500 error when orchestration fails.
def test_query_endpoint_returns_500_on_orchestrator_error(monkeypatch):
    def boom(_question):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(main_module, "orchestrate_query", boom)

    response = client.post("/api/query", json={"question": "List all site names and provinces"})
    assert response.status_code == 500
    assert "simulated failure" in response.json()["detail"]


# This test verifies that the knowledge base ingest endpoint returns a success payload.
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


# This test verifies that read-only SQL validation accepts a valid SELECT query with a trailing semicolon.
def test_ensure_readonly_sql_accepts_valid_select():
    sql = "SELECT sitename, province FROM site_metadata;"
    cleaned = orch.ensure_readonly_sql(sql)
    assert cleaned == "SELECT sitename, province FROM site_metadata"


# This test verifies that read-only SQL validation rejects non-SELECT statements.
def test_ensure_readonly_sql_rejects_non_select():
    with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
        orch.ensure_readonly_sql("DELETE FROM site_metadata")


# This test verifies that read-only SQL validation rejects multiple SQL statements.
def test_ensure_readonly_sql_rejects_multiple_statements():
    with pytest.raises(ValueError, match="Multiple SQL statements are not allowed"):
        orch.ensure_readonly_sql("SELECT * FROM site_metadata; SELECT * FROM performance_daily_data")


# This test verifies that table validation passes when all referenced tables exist in the schema.
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


# This test verifies that table validation raises an error for unknown tables.
def test_validate_sql_table_usage_rejects_unknown_tables(monkeypatch):
    fake_schema = [{"table_name": "site_metadata", "columns": []}]
    monkeypatch.setattr(orch, "get_schema_overview", lambda: fake_schema)

    with pytest.raises(ValueError, match="Invalid table"):
        orch.validate_sql_table_usage("SELECT * FROM imaginary_table")


# This test verifies that run_sql appends a default LIMIT when one is missing and returns row dictionaries.
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


# This test verifies that chunking a very short document finishes safely and produces one chunk.
def test_chunk_text_handles_short_text_without_looping():
    chunks = kb.chunk_text("Mention Toronto as being the epicenter of power energy.")
    assert len(chunks) == 1
    assert "Toronto" in chunks[0]


# This test verifies that ingest_knowledge_base processes local files and writes vector metadata outputs.
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


# This test verifies that retrieve_chunks returns ranked knowledge chunks from the stored vector metadata.
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

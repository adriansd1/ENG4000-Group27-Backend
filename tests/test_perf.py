import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_response_time_under_200ms():
    start = time.perf_counter()
    r = client.get("/health")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert r.status_code == 200
    assert elapsed_ms < 200
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_post_not_allowed():
    r = client.post("/health")
    assert r.status_code in (405, 404)  # depends on how routes are defined
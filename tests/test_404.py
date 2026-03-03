from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_unknown_route_returns_404():
    r = client.get("/this-route-should-not-exist")
    assert r.status_code == 404
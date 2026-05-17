from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_scenarios():
    response = client.get("/demo/scenarios")
    assert response.status_code == 200
    assert len(response.json()) >= 5


def test_supplier_offer_parse():
    response = client.post(
        "/emails/parse",
        json={
            "sender": "supplier@example.com",
            "subject": "Fresh halibut offer",
            "body": "Fresh Halibut available, 1000 lbs, FOB Seattle, $9.50/lb.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "supplier_offer"
    assert data["extracted"]["products"][0]["species_common_name"] == "Halibut"
    assert data["extracted"]["_meta"]["parser_used"] == "rules"


def test_actions_created():
    response = client.get("/emails/actions")
    assert response.status_code == 200

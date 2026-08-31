from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


def test_unregister_participant_removes_email():
    app_module.activities["Chess Club"]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]


def test_unregister_unknown_participant_returns_404():
    app_module.activities["Chess Club"]["participants"] = ["daniel@mergington.edu"]

    response = client.delete("/activities/Chess%20Club/unregister?email=missing@mergington.edu")

    assert response.status_code == 404

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = {
        name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": list(activity["participants"]),
        }
        for name, activity in app_module.activities.items()
    }

    yield

    app_module.activities.clear()
    app_module.activities.update(original_activities)


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_email():
    app_module.activities["Chess Club"]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    response = client.post(
        "/activities/Chess%20Club/signup?email=student@mergington.edu"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up student@mergington.edu for Chess Club"
    assert "student@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Unknown%20Club/signup?email=student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_email_returns_400():
    app_module.activities["Chess Club"]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    response = client.post(
        "/activities/Chess%20Club/signup?email=daniel@mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


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

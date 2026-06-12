import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
initial_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activity_state():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(initial_activities))


def test_get_activities_returns_activity_list():
    # Arrange
    # (activities already set up by fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_adds_new_participant():
    # Arrange
    activity = quote("Chess Club", safe="")
    email = "teststudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={quote(email, safe='')}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_bad_request():
    # Arrange
    activity = quote("Chess Club", safe="")
    email = "michael@mergington.edu"  # Already signed up from fixture

    # Act
    response = client.post(f"/activities/{activity}/signup?email={quote(email, safe='')}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_unregisters_student():
    # Arrange
    activity = quote("Chess Club", safe="")
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={quote(email, safe='')}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_not_found():
    # Arrange
    activity = quote("Chess Club", safe="")
    email = "notfound@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={quote(email, safe='')}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"

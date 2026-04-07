import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: preserve the original in-memory activity database
    original_activities = copy.deepcopy(activities)
    yield
    # Assert: restore original activity state after each test
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Programming Class"
    existing_email = "emma@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_success():
    # Arrange
    activity_name = "Gym Class"
    email = "john@mergington.edu"
    url = f"/activities/{activity_name}/unregister"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_participant_returns_400():
    # Arrange
    activity_name = "Tennis Club"
    email = "missing@mergington.edu"
    url = f"/activities/{activity_name}/unregister"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"

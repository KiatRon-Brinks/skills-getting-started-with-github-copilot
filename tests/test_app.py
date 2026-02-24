from fastapi.testclient import TestClient
import pytest

# import the app object from the application
from src.app import app, activities

client = TestClient(app)

@pyte st.fixture(autouse=True)
def reset_activities():
    # save a copy of initial state and restore after test
    original = {k: v.copy() for k, v in activities.items()}
    yield
    activities.clear()
    activities.update({k: v.copy() for k, v in original.items()})


def test_root_redirection():
    resp = client.get("/")
    assert resp.status_code == 200
    # FastAPI's TestClient follows redirects by default
    assert "Mergington High School" in resp.text


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_duplicate():
    email = "new@student.edu"
    activity = "Chess Club"
    # initial signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # duplicate
    dup = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert dup.status_code == 400
    assert dup.json()["detail"] == "Student already signed up"


def test_remove_participant():
    activity = "Programming Class"
    email = "emma@mergington.edu"
    # remove existing
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]

    # removing again fails
    resp2 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp2.status_code == 404


def test_invalid_activity_errors():
    resp = client.post("/activities/Nonexistent/signup", params={"email": "x@y.com"})
    assert resp.status_code == 404

    resp = client.delete("/activities/Nonexistent/participants", params={"email": "x@y.com"})
    assert resp.status_code == 404

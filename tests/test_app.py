import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]

def test_signup_successful():
    email = "newstudent@mergington.edu"
    activity_name = "Tennis Club"
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    # Check if added
    data = client.get("/activities").json()
    assert email in data[activity_name]["participants"]

def test_signup_activity_not_found():
    response = client.post("/activities/NonExistent/signup", params={"email": "test@example.com"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_signup_already_signed_up():
    email = "duplicate@mergington.edu"
    activity_name = "Programming Class"
    # First signup
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Second signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}

def test_signup_activity_full():
    activity_name = "Basketball Team"  # max 15, currently 1
    email_base = "fill@mergington.edu"
    # Fill to max
    for i in range(14):  # Add 14 more to reach 15
        client.post(f"/activities/{activity_name}/signup", params={"email": f"{i}{email_base}"})
    # Try to add one more
    response = client.post(f"/activities/{activity_name}/signup", params={"email": "overflow@mergington.edu"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}

def test_unregister_successful():
    email = "removeme@mergington.edu"
    activity_name = "Art Studio"
    # First sign up
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Then unregister
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    # Check removed
    data = client.get("/activities").json()
    assert email not in data[activity_name]["participants"]

def test_unregister_activity_not_found():
    response = client.delete("/activities/NonExistent/unregister", params={"email": "test@example.com"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_unregister_not_signed_up():
    response = client.delete("/activities/Chess Club/unregister", params={"email": "notsigned@mergington.edu"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Student not signed up for this activity"}

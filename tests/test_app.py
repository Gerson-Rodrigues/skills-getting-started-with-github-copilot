"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200

    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0

    # Check that each activity has the required fields
    for name, details in activities.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_get_root_redirect(client):
    """Test that root redirects to static index"""
    response = client.get("/")
    assert response.status_code == 200
    # FastAPI redirects to static files, but in test client it serves directly


def test_signup_success(client):
    """Test successful signup for an activity"""
    # Use an activity that exists and has space
    response = client.post("/activities/Basketball%20Club/signup?email=test@example.com")
    assert response.status_code == 200

    result = response.json()
    assert "message" in result
    assert "test@example.com" in result["message"]
    assert "Basketball Club" in result["message"]


def test_signup_duplicate(client):
    """Test signing up twice for the same activity"""
    email = "duplicate@example.com"
    activity = "Soccer Team"

    # First signup should succeed
    response1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert response1.status_code == 200

    # Second signup should fail
    response2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert response2.status_code == 400

    result = response2.json()
    assert "detail" in result
    assert "already signed up" in result["detail"]


def test_signup_activity_not_found(client):
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404

    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_signup_activity_full(client):
    """Test signing up for a full activity"""
    # Find an activity and fill it up
    activity_name = "Chess Club"
    max_participants = 12  # From the data

    # Fill up the activity
    for i in range(max_participants):
        email = f"fill{i}@example.com"
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        if i < 2:  # Already has 2 participants
            continue
        assert response.status_code == 200

    # Try to add one more - should fail
    response = client.post(f"/activities/{activity_name}/signup?email=overflow@example.com")
    assert response.status_code == 400

    result = response.json()
    assert "detail" in result
    assert "Activity is full" in result["detail"]


def test_unregister_success(client):
    """Test successful unregistration from an activity"""
    email = "unregister@example.com"
    activity = "Art Club"

    # First sign up
    signup_response = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_response.status_code == 200

    # Then unregister
    unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert unregister_response.status_code == 200

    result = unregister_response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity in result["message"]


def test_unregister_not_signed_up(client):
    """Test unregistering when not signed up"""
    email = "notsigned@example.com"
    activity = "Music Ensemble"

    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400

    result = response.json()
    assert "detail" in result
    assert "not signed up" in result["detail"]


def test_unregister_activity_not_found(client):
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/NonExistent/unregister?email=test@example.com")
    assert response.status_code == 404

    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]
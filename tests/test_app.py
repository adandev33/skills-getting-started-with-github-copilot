"""
Tests for the FastAPI application endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team for practices and matches",
            "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Build endurance and technique in competitive swimming",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Practice acting, improv, and stage production",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["sophia@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu", "ethan@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Work on challenging math problems and team competitions",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 15,
            "participants": ["oliver@mergington.edu", "amelia@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["charlotte@mergington.edu", "liam@mergington.edu"]
        }
    })
    yield


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_returns_correct_structure(self, client):
        """Test that activity objects have correct structure"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_participant_data(self, client):
        """Test that participant data is included"""
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_adds_participant(self, client):
        """Test that a new participant is added to an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_actually_adds_participant(self, client):
        """Test that participant is actually added to the activity"""
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 3

    def test_signup_duplicate_participant_fails(self, client):
        """Test that signing up an existing participant fails"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Non-existent Activity/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_returns_success_message(self, client):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert response.status_code == 200


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_removes_participant(self, client):
        """Test that a participant is removed from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_actually_removes_participant(self, client):
        """Test that participant is actually removed from the activity"""
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 1

    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering a non-existent participant fails"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregistering from a non-existent activity fails"""
        response = client.delete(
            "/activities/Non-existent Activity/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_returns_success_message(self, client):
        """Test that unregister returns a success message"""
        response = client.delete(
            "/activities/Swimming Club/unregister",
            params={"email": "noah@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert response.status_code == 200


class TestSignupAndUnregisterFlow:
    """Tests for signup and unregister flows"""

    def test_signup_then_unregister(self, client):
        """Test signing up and then unregistering"""
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        response = client.get("/activities")
        assert "newstudent@mergington.edu" in response.json()["Chess Club"]["participants"]
        
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "newstudent@mergington.edu"}
        )
        response = client.get("/activities")
        assert "newstudent@mergington.edu" not in response.json()["Chess Club"]["participants"]

    def test_multiple_signups_and_unregisters(self, client):
        """Test multiple signup and unregister operations"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            client.post(
                "/activities/Gym Class/signup",
                params={"email": email}
            )
        
        response = client.get("/activities")
        gym_participants = response.json()["Gym Class"]["participants"]
        assert len(gym_participants) == 5
        
        for email in emails:
            client.delete(
                "/activities/Gym Class/unregister",
                params={"email": email}
            )
        
        response = client.get("/activities")
        gym_participants = response.json()["Gym Class"]["participants"]
        assert len(gym_participants) == 2

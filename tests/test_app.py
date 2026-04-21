"""
Unit tests for Mergington High School Activities API

Uses AAA (Arrange-Act-Assert) pattern for test structure clarity.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Arrange: None | Act: GET /activities | Assert: Status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Arrange: None | Act: GET /activities | Assert: Response is dict"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_all_activities(self, client):
        """Arrange: None | Act: GET /activities | Assert: All 9 activities present"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Tennis Club",
            "Basketball Team", "Drama Club", "Digital Art Studio", "Debate Team",
            "Robotics Club"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_get_activities_has_correct_structure(self, client):
        """Arrange: None | Act: GET /activities | Assert: Each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_get_activities_participants_are_strings(self, client):
        """Arrange: None | Act: GET /activities | Assert: Participants are email strings"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, details in activities.items():
            for participant in details["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_valid_student_returns_200(self, client):
        """Arrange: Valid email, valid activity | Act: POST signup | Assert: Status 200"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_valid_student_returns_message(self, client):
        """Arrange: Valid email, valid activity | Act: POST signup | Assert: Contains message"""
        response = client.post(
            "/activities/Robotics Club/signup?email=brandnew@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "brandnew@mergington.edu" in data["message"]

    def test_signup_adds_student_to_participants(self, client):
        """Arrange: Valid email | Act: POST signup then GET activities | Assert: Student in participants"""
        email = "teststudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        
        assert email in activities["Chess Club"]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        """Arrange: Already signed up student | Act: POST signup twice | Assert: 2nd is 400"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Tennis Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Tennis Club/signup?email={email}")
        assert response2.status_code == 400

    def test_signup_duplicate_error_message(self, client):
        """Arrange: Already signed up student | Act: POST signup twice | Assert: Error message present"""
        email = "duplicate2@mergington.edu"
        
        client.post(f"/activities/Tennis Club/signup?email={email}")
        response = client.post(f"/activities/Tennis Club/signup?email={email}")
        
        data = response.json()
        assert "detail" in data
        assert "already" in data["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Arrange: Non-existent activity name | Act: POST signup | Assert: Status 404"""
        response = client.post(
            "/activities/Fake Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404

    def test_signup_nonexistent_activity_error_message(self, client):
        """Arrange: Non-existent activity | Act: POST signup | Assert: 'not found' in message"""
        response = client.post(
            "/activities/Fake Activity/signup?email=student@mergington.edu"
        )
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_valid_with_encoded_email(self, client):
        """Arrange: Valid email URL encoded | Act: POST signup | Assert: Adds successfully"""
        from urllib.parse import quote
        email = "user.middle@mergington.edu"
        encoded_email = quote(email)
        response = client.post(f"/activities/Chess Club/signup?email={encoded_email}")
        assert response.status_code == 200
        
        # Verify in participants
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email in activities["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_valid_returns_200(self, client):
        """Arrange: Student signed up | Act: DELETE unregister | Assert: Status 200"""
        email = "unregister_test@mergington.edu"
        
        # First sign up
        client.post(f"/activities/Debate Team/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/Debate Team/unregister?email={email}"
        )
        assert response.status_code == 200

    def test_unregister_removes_student(self, client):
        """Arrange: Student signed up | Act: DELETE unregister then GET activities | Assert: Student removed"""
        email = "remove_me@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Robotics Club/signup?email={email}")
        
        # Unregister
        client.delete(f"/activities/Robotics Club/unregister?email={email}")
        
        # Verify removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Robotics Club"]["participants"]

    def test_unregister_nonexistent_student_returns_400(self, client):
        """Arrange: Student not signed up | Act: DELETE unregister | Assert: Status 400"""
        response = client.delete(
            "/activities/Drama Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400

    def test_unregister_nonexistent_student_error_message(self, client):
        """Arrange: Student not signed up | Act: DELETE unregister | Assert: Error message present"""
        response = client.delete(
            "/activities/Drama Club/unregister?email=notregistered@mergington.edu"
        )
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Arrange: Non-existent activity | Act: DELETE unregister | Assert: Status 404"""
        response = client.delete(
            "/activities/Fake Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_nonexistent_activity_error_message(self, client):
        """Arrange: Non-existent activity | Act: DELETE unregister | Assert: 'not found' in message"""
        response = client.delete(
            "/activities/Fake Activity/unregister?email=student@mergington.edu"
        )
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestRootRedirect:
    """Test suite for GET / endpoint"""

    def test_root_returns_redirect(self, client):
        """Arrange: None | Act: GET / | Assert: Status 307 (redirect)"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307

    def test_root_redirects_to_static_index(self, client):
        """Arrange: None | Act: GET / (follow redirects) | Assert: Reaches /static/index.html"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
        # Should contain HTML content
        assert "html" in response.text.lower()


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister workflows"""

    def test_signup_then_unregister_cycle(self, client):
        """Arrange: Test email | Act: Signup, verify in list, unregister, verify removed | Assert: All succeed"""
        email = "cycle_test@mergington.edu"
        activity = "Programming Class"
        
        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify in participants
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email in activities[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify removed from participants
        get_response2 = client.get("/activities")
        activities2 = get_response2.json()
        assert email not in activities2[activity]["participants"]

    def test_multiple_students_signup_same_activity(self, client):
        """Arrange: Two different emails | Act: Signup both to same activity | Assert: Both in participants"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        activity = "Digital Art Studio"
        
        # Both sign up
        client.post(f"/activities/{activity}/signup?email={email1}")
        client.post(f"/activities/{activity}/signup?email={email2}")
        
        # Verify both in participants
        response = client.get("/activities")
        activities = response.json()
        assert email1 in activities[activity]["participants"]
        assert email2 in activities[activity]["participants"]

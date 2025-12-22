"""
Integration tests for user profile endpoints.
These tests require database access.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import generate_id


# ============================================
# User Profile Update Tests
# ============================================

@pytest.mark.integration
class TestUserProfileUpdate:
    """Tests for user profile update endpoint."""
    
    def test_update_user_name(self, client, create_test_user):
        """Test updating user name."""
        headers = create_test_user["headers"]
        new_name = f"Updated Name {generate_id()[:6]}"
        
        response = client.put(
            "/users/me",
            json={"name": new_name},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == new_name
    
    def test_update_user_password(self, client, create_test_user, test_user_data):
        """Test updating user password."""
        headers = create_test_user["headers"]
        new_password = "NewSecurePass123!"
        
        response = client.put(
            "/users/me",
            json={"password": new_password},
            headers=headers
        )
        
        assert response.status_code == 200
        
        # Verify new password works by logging in
        login_response = client.post("/auth/login", json={
            "email": create_test_user["user"]["email"],
            "password": new_password
        })
        assert login_response.status_code == 200
    
    def test_update_user_invalid_password(self, client, create_test_user):
        """Test updating with weak password fails."""
        headers = create_test_user["headers"]
        
        response = client.put(
            "/users/me",
            json={"password": "weak"},
            headers=headers
        )
        
        assert response.status_code in [400, 422]
    
    def test_update_user_without_auth(self, client):
        """Test that updating profile requires authentication."""
        response = client.put("/users/me", json={"name": "New Name"})
        
        assert response.status_code == 401


# ============================================
# Public Profile Tests
# ============================================

@pytest.mark.integration
class TestPublicProfiles:
    """Tests for public user profile endpoints."""
    
    def test_get_user_profile(self, client, create_test_user, authenticated_headers):
        """Test getting another user's public profile."""
        user_id = create_test_user["user"]["user_id"]
        
        response = client.get(
            f"/users/{user_id}/profile",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data or "email" in data or "name" in data
    
    def test_get_user_profile_not_found(self, client, authenticated_headers):
        """Test getting profile of non-existent user."""
        response = client.get(
            "/users/nonexistent-user-id/profile",
            headers=authenticated_headers
        )
        
        assert response.status_code == 404
    
    def test_get_user_profile_without_auth(self, client, create_test_user):
        """Test that getting profiles requires authentication."""
        user_id = create_test_user["user"]["user_id"]
        
        response = client.get(f"/users/{user_id}/profile")
        
        assert response.status_code == 401


# ============================================
# User Search Tests
# ============================================

@pytest.mark.integration
class TestUserSearch:
    """Tests for user search endpoint."""
    
    def test_search_users_by_name(self, client, create_test_user, authenticated_headers):
        """Test searching users by name."""
        user_name = create_test_user["user"]["name"][:5]
        
        response = client.get(
            "/users",
            params={"query": user_name},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_search_users_empty_query(self, client, authenticated_headers):
        """Test searching users with no query."""
        response = client.get(
            "/users",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_search_users_no_results(self, client, authenticated_headers):
        """Test searching for non-existent users."""
        response = client.get(
            "/users",
            params={"query": "xyznonexistent12345"},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_search_users_pagination(self, client, authenticated_headers):
        """Test user search pagination."""
        response = client.get(
            "/users",
            params={"limit": 5, "offset": 0},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_search_users_without_auth(self, client):
        """Test that user search requires authentication."""
        response = client.get("/users", params={"query": "test"})
        
        assert response.status_code == 401


# ============================================
# User Reading Sessions Tests
# ============================================

@pytest.mark.integration
class TestUserReadingSessions:
    """Tests for getting another user's reading sessions."""
    
    def test_get_user_reading_sessions(self, client, create_test_user, authenticated_headers):
        """Test getting another user's reading sessions."""
        user_id = create_test_user["user"]["user_id"]
        
        response = client.get(
            f"/users/{user_id}/reading-sessions",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_user_reading_sessions_pagination(self, client, create_test_user, authenticated_headers):
        """Test pagination of user's reading sessions."""
        user_id = create_test_user["user"]["user_id"]
        
        response = client.get(
            f"/users/{user_id}/reading-sessions",
            params={"limit": 5, "offset": 0},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_get_user_reading_sessions_not_found(self, client, authenticated_headers):
        """Test getting sessions of non-existent user."""
        response = client.get(
            "/users/nonexistent-user-id/reading-sessions",
            headers=authenticated_headers
        )
        
        assert response.status_code == 404
    
    def test_get_user_reading_sessions_without_auth(self, client, create_test_user):
        """Test that getting user sessions requires authentication."""
        user_id = create_test_user["user"]["user_id"]
        
        response = client.get(f"/users/{user_id}/reading-sessions")
        
        assert response.status_code == 401

"""
Integration tests for social/follower endpoints.
These tests require database access.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import generate_id


# ============================================
# Helper fixture for second user
# ============================================

@pytest.fixture
def create_second_user(client, clean_test_data):
    """Create a second test user for follow tests."""
    unique_id = generate_id()[:8]
    user_data = {
        "email": f"second_user_{unique_id}@example.com",
        "name": f"Second User {unique_id}",
        "password": "SecondPass123!"
    }
    
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201
    user = register_response.json()
    clean_test_data["users"].append(user["user_id"])
    
    login_response = client.post("/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    token_data = login_response.json()
    
    return {
        "user": user,
        "token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"}
    }


# ============================================
# Follow Action Tests
# ============================================

@pytest.mark.integration
class TestFollowActions:
    """Tests for follow/unfollow endpoints."""
    
    def test_follow_user_success(self, client, authenticated_headers, create_second_user):
        """Test successfully following another user."""
        user_to_follow = create_second_user["user"]["user_id"]
        
        response = client.post(
            f"/users/{user_to_follow}/follow",
            headers=authenticated_headers
        )
        
        assert response.status_code in [200, 201]
    
    def test_follow_user_twice(self, client, authenticated_headers, create_second_user):
        """Test that following same user twice fails."""
        user_to_follow = create_second_user["user"]["user_id"]
        
        # First follow
        client.post(f"/users/{user_to_follow}/follow", headers=authenticated_headers)
        
        # Second follow should fail
        response = client.post(
            f"/users/{user_to_follow}/follow",
            headers=authenticated_headers
        )
        
        assert response.status_code == 400
    
    def test_follow_self(self, client, create_test_user):
        """Test that users cannot follow themselves."""
        user_id = create_test_user["user"]["user_id"]
        headers = create_test_user["headers"]
        
        response = client.post(
            f"/users/{user_id}/follow",
            headers=headers
        )
        
        assert response.status_code == 400
    
    def test_follow_nonexistent_user(self, client, authenticated_headers):
        """Test following a user that doesn't exist."""
        response = client.post(
            "/users/nonexistent-user-id/follow",
            headers=authenticated_headers
        )
        
        assert response.status_code == 404
    
    def test_follow_without_auth(self, client, create_second_user):
        """Test that following requires authentication."""
        user_to_follow = create_second_user["user"]["user_id"]
        
        response = client.post(f"/users/{user_to_follow}/follow")
        
        assert response.status_code == 401
    
    def test_unfollow_user_success(self, client, authenticated_headers, create_second_user):
        """Test successfully unfollowing a user."""
        user_to_follow = create_second_user["user"]["user_id"]
        
        # Follow first
        client.post(f"/users/{user_to_follow}/follow", headers=authenticated_headers)
        
        # Then unfollow
        response = client.delete(
            f"/users/{user_to_follow}/follow",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
    
    def test_unfollow_not_following(self, client, authenticated_headers, create_second_user):
        """Test unfollowing a user you're not following."""
        user_id = create_second_user["user"]["user_id"]
        
        response = client.delete(
            f"/users/{user_id}/follow",
            headers=authenticated_headers
        )
        
        # Should be 404 (not following)
        assert response.status_code == 404


# ============================================
# Follower Retrieval Tests
# ============================================

@pytest.mark.integration
class TestFollowerRetrieval:
    """Tests for follower/following list endpoints."""
    
    def test_get_users_i_follow(self, client, authenticated_headers, create_second_user):
        """Test getting list of users current user follows."""
        user_to_follow = create_second_user["user"]["user_id"]
        
        # Follow the user
        client.post(f"/users/{user_to_follow}/follow", headers=authenticated_headers)
        
        # Get following list
        response = client.get("/users/me/following", headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.json()
        # Response is paginated object with "following" key
        assert "following" in data or isinstance(data, list)
    
    def test_get_my_followers(self, client, create_test_user, create_second_user):
        """Test getting list of users following current user."""
        # Second user follows first user
        first_user_id = create_test_user["user"]["user_id"]
        second_user_headers = create_second_user["headers"]
        
        client.post(f"/users/{first_user_id}/follow", headers=second_user_headers)
        
        # First user gets their followers
        response = client.get("/users/me/followers", headers=create_test_user["headers"])
        
        assert response.status_code == 200
        data = response.json()
        # Response is paginated object with "followers" key
        assert "followers" in data or isinstance(data, list)
    
    def test_get_following_pagination(self, client, authenticated_headers):
        """Test following list pagination."""
        response = client.get(
            "/users/me/following",
            params={"limit": 5, "offset": 0},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Response is paginated, check for following key or list
        if "following" in data:
            assert len(data["following"]) <= 5
        else:
            assert len(data) <= 5
    
    def test_get_followers_pagination(self, client, authenticated_headers):
        """Test followers list pagination."""
        response = client.get(
            "/users/me/followers",
            params={"limit": 5, "offset": 0},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Response is paginated, check for followers key or list
        if "followers" in data:
            assert len(data["followers"]) <= 5
        else:
            assert len(data) <= 5
    
    def test_get_following_without_auth(self, client):
        """Test that getting following requires auth."""
        response = client.get("/users/me/following")
        assert response.status_code == 401
    
    def test_get_followers_without_auth(self, client):
        """Test that getting followers requires auth."""
        response = client.get("/users/me/followers")
        assert response.status_code == 401


# ============================================
# Follow Status Tests
# ============================================

@pytest.mark.integration
class TestFollowStatus:
    """Tests for follow status endpoint."""
    
    def test_get_follow_status_following(self, client, authenticated_headers, create_second_user):
        """Test getting follow status when following."""
        user_to_follow = create_second_user["user"]["user_id"]
        
        # Follow the user
        client.post(f"/users/{user_to_follow}/follow", headers=authenticated_headers)
        
        # Check status
        response = client.get(
            f"/users/{user_to_follow}/follow-status",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_following"] == True
    
    def test_get_follow_status_not_following(self, client, authenticated_headers, create_second_user):
        """Test getting follow status when not following."""
        user_id = create_second_user["user"]["user_id"]
        
        response = client.get(
            f"/users/{user_id}/follow-status",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_following"] == False
    
    def test_get_follow_status_without_auth(self, client, create_second_user):
        """Test that follow status requires authentication."""
        user_id = create_second_user["user"]["user_id"]
        
        response = client.get(f"/users/{user_id}/follow-status")
        
        assert response.status_code == 401


# ============================================
# Activity Feed Tests
# ============================================

@pytest.mark.integration
class TestActivityFeed:
    """Tests for following activity feed endpoint."""
    
    def test_get_following_activity(self, client, authenticated_headers):
        """Test getting activity feed from followed users."""
        response = client.get("/users/me/following/activity", headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_following_activity_pagination(self, client, authenticated_headers):
        """Test activity feed pagination."""
        response = client.get(
            "/users/me/following/activity",
            params={"limit": 10, "offset": 0},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10
    
    def test_get_following_activity_without_auth(self, client):
        """Test that activity feed requires authentication."""
        response = client.get("/users/me/following/activity")
        
        assert response.status_code == 401

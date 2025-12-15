"""
Integration tests for authentication endpoints.
These tests require database access.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# ============================================
# Registration Tests
# ============================================

@pytest.mark.integration
class TestRegistration:
    """Tests for user registration endpoint."""
    
    def test_register_success(self, client, test_user_data, clean_test_data):
        """Test successful user registration."""
        response = client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["name"] == test_user_data["name"]
        assert "user_id" in data
        assert "password" not in data  # Password should not be returned
        
        # Track for cleanup
        clean_test_data["users"].append(data["user_id"])
    
    def test_register_duplicate_email(self, client, create_test_user, clean_test_data):
        """Test that duplicate email registration fails."""
        # Try to register with same email
        response = client.post("/auth/register", json={
            "email": create_test_user["user"]["email"],
            "name": "Another User",
            "password": "AnotherPass1!"
        })
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post("/auth/register", json={
            "email": "notanemail",
            "name": "Test User",
            "password": "ValidPass1!"
        })
        
        assert response.status_code in [400, 422]  # Either is valid for validation errors  # Validation error
    
    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "name": "Test User",
            "password": "weak"
        })
        
        assert response.status_code in [400, 422]  # Either is valid for validation errors


# ============================================
# Login Tests
# ============================================

@pytest.mark.integration
class TestLogin:
    """Tests for user login endpoint."""
    
    def test_login_success(self, client, create_test_user):
        """Test successful login."""
        user_data = create_test_user
        
        # Login
        response = client.post("/auth/login", json={
            "email": user_data["user"]["email"],
            "password": "TestPass123!"  # From test_user_data fixture
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == user_data["user"]["email"]
    
    def test_login_wrong_password(self, client, create_test_user):
        """Test login with wrong password."""
        response = client.post("/auth/login", json={
            "email": create_test_user["user"]["email"],
            "password": "WrongPassword1!"
        })
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email."""
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "AnyPassword1!"
        })
        
        assert response.status_code == 401
    
    def test_login_returns_user_info(self, client, create_test_user):
        """Test that login returns complete user info."""
        response = client.post("/auth/login", json={
            "email": create_test_user["user"]["email"],
            "password": "TestPass123!"
        })
        
        assert response.status_code == 200
        user = response.json()["user"]
        assert "user_id" in user
        assert "email" in user
        assert "name" in user
        assert "current_streak" in user
        assert "password" not in user


# ============================================
# Authentication Flow Tests
# ============================================

@pytest.mark.integration
class TestAuthenticationFlow:
    """Tests for complete authentication flow."""
    
    def test_register_then_login(self, client, test_user_data, clean_test_data):
        """Test that a registered user can login."""
        # Register
        register_response = client.post("/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        user = register_response.json()
        clean_test_data["users"].append(user["user_id"])
        
        # Login
        login_response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert login_response.status_code == 200
        
        # Use token to access protected route
        token = login_response.json()["access_token"]
        me_response = client.get("/users/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert me_response.status_code == 200
        assert me_response.json()["email"] == test_user_data["email"]
    
    def test_protected_route_without_token(self, client):
        """Test that protected routes require authentication."""
        response = client.get("/users/me")
        assert response.status_code == 401  # Forbidden without token
    
    def test_protected_route_invalid_token(self, client):
        """Test that invalid tokens are rejected."""
        response = client.get("/users/me", headers={
            "Authorization": "Bearer invalid-token"
        })
        assert response.status_code == 401

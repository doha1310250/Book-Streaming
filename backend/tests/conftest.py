"""
Pytest configuration and shared fixtures for Book Streaming API tests.
"""
import pytest
import os
import sys
from typing import Generator, Dict, Any
from httpx import AsyncClient, ASGITransport

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import db
from utils import generate_id, hash_password


# ============================================
# Test Database Fixtures
# ============================================

@pytest.fixture(scope="session")
def test_db_setup():
    """
    Set up test database tables.
    This runs once per test session.
    """
    # Initialize tables (they should already exist)
    # In a real scenario, you might want to use a separate test database
    yield
    # Cleanup can be added here if needed


@pytest.fixture
def clean_test_data():
    """
    Clean up test data before and after each test.
    Use this fixture when you need a clean slate.
    """
    # Store created IDs for cleanup
    created_users = []
    created_books = []
    
    yield {
        "users": created_users,
        "books": created_books
    }
    
    # Cleanup after test
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                # Delete test data in reverse order of dependencies
                for book_id in created_books:
                    cursor.execute("DELETE FROM reviews WHERE book_id = %s", (book_id,))
                    cursor.execute("DELETE FROM marks WHERE book_id = %s", (book_id,))
                    cursor.execute("DELETE FROM reading_sessions WHERE book_id = %s", (book_id,))
                    cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
                
                for user_id in created_users:
                    cursor.execute("DELETE FROM followers WHERE follower_id = %s OR followed_id = %s", 
                                   (user_id, user_id))
                    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    except Exception as e:
        print(f"Cleanup error: {e}")


# ============================================
# HTTP Client Fixtures
# ============================================

@pytest.fixture
def client():
    """
    Synchronous test client for simple tests.
    """
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client() -> Generator[AsyncClient, None, None]:
    """
    Async test client for async tests.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ============================================
# User Fixtures
# ============================================

@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """
    Generate test user data.
    """
    unique_id = generate_id()[:8]
    return {
        "email": f"testuser_{unique_id}@example.com",
        "name": f"Test User {unique_id}",
        "password": "TestPass123!"
    }


@pytest.fixture
def create_test_user(client, test_user_data, clean_test_data):
    """
    Create a test user and return user data with token.
    """
    # Register user
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    user = response.json()
    
    # Track for cleanup
    clean_test_data["users"].append(user["user_id"])
    
    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    assert login_response.status_code == 200
    token_data = login_response.json()
    
    return {
        "user": user,
        "token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"}
    }


@pytest.fixture
def authenticated_headers(create_test_user) -> Dict[str, str]:
    """
    Get authentication headers for a test user.
    """
    return create_test_user["headers"]


# ============================================
# Book Fixtures
# ============================================

@pytest.fixture
def test_book_data() -> Dict[str, Any]:
    """
    Generate test book data.
    """
    unique_id = generate_id()[:8]
    return {
        "title": f"Test Book {unique_id}",
        "author_name": f"Test Author {unique_id}",
        "publish_date": "2024-01-15"
    }


@pytest.fixture
def create_test_book(client, authenticated_headers, test_book_data, clean_test_data):
    """
    Create a test book and return book data.
    """
    response = client.post(
        "/books",
        params=test_book_data,
        headers=authenticated_headers
    )
    assert response.status_code == 201, f"Failed to create book: {response.text}"
    book = response.json()
    
    # Track for cleanup
    clean_test_data["books"].append(book["book_id"])
    
    return book


# ============================================
# Utility Fixtures
# ============================================

@pytest.fixture
def sample_valid_passwords():
    """
    Sample valid passwords for testing.
    """
    return [
        "ValidPass1!",
        "SecureP@ss123",
        "MyP@ssw0rd!",
        "Test123!@#"
    ]


@pytest.fixture
def sample_invalid_passwords():
    """
    Sample invalid passwords for testing.
    """
    return [
        ("short1!", "too short"),
        ("nouppercase1!", "no uppercase"),
        ("NOLOWERCASE1!", "no lowercase"),
        ("NoDigits!", "no digits"),
        ("NoSpecial123", "no special character")
    ]

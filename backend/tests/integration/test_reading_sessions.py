"""
Integration tests for reading session endpoints.
These tests require database access.
"""
import pytest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import generate_id


# ============================================
# Reading Session Creation Tests
# ============================================

@pytest.mark.integration
class TestReadingSessionCreation:
    """Tests for reading session creation endpoint."""
    
    def test_start_reading_session_success(self, client, authenticated_headers, create_test_book):
        """Test successfully starting a reading session."""
        book_id = create_test_book["book_id"]
        
        session_data = {
            "start_time": datetime.now().isoformat()
        }
        
        response = client.post(
            f"/books/{book_id}/reading-sessions",
            json=session_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["book_id"] == book_id
        assert "start_time" in data
    
    def test_start_session_without_auth(self, client, create_test_book):
        """Test that starting a session requires authentication."""
        book_id = create_test_book["book_id"]
        
        response = client.post(
            f"/books/{book_id}/reading-sessions",
            json={"start_time": datetime.now().isoformat()}
        )
        
        assert response.status_code == 401
    
    def test_start_session_nonexistent_book(self, client, authenticated_headers):
        """Test starting a session for a book that doesn't exist."""
        response = client.post(
            "/books/nonexistent-book-id/reading-sessions",
            json={"start_time": datetime.now().isoformat()},
            headers=authenticated_headers
        )
        
        assert response.status_code == 404
    
    def test_start_session_with_end_time(self, client, authenticated_headers, create_test_book):
        """Test starting a session with both start and end time."""
        book_id = create_test_book["book_id"]
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=30)
        
        session_data = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_min": 30
        }
        
        response = client.post(
            f"/books/{book_id}/reading-sessions",
            json=session_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        # Duration may be calculated by server
        assert "duration_min" in data


# ============================================
# Reading Session Update Tests
# ============================================

@pytest.mark.integration
class TestReadingSessionUpdate:
    """Tests for reading session update endpoint."""
    
    def test_end_reading_session(self, client, authenticated_headers, create_test_book):
        """Test ending a reading session."""
        book_id = create_test_book["book_id"]
        
        # Start a session
        start_response = client.post(
            f"/books/{book_id}/reading-sessions",
            json={"start_time": datetime.now().isoformat()},
            headers=authenticated_headers
        )
        assert start_response.status_code == 201
        session_id = start_response.json()["id"]
        
        # End the session
        end_time = datetime.now() + timedelta(minutes=15)
        response = client.put(
            f"/reading-sessions/{session_id}",
            params={"end_time": end_time.isoformat()},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["end_time"] is not None
        assert data["duration_min"] is not None
    
    def test_end_session_not_found(self, client, authenticated_headers):
        """Test ending a session that doesn't exist."""
        response = client.put(
            "/reading-sessions/nonexistent-session-id",
            params={"end_time": datetime.now().isoformat()},
            headers=authenticated_headers
        )
        
        assert response.status_code == 404
    
    def test_end_session_without_auth(self, client, create_test_book, authenticated_headers):
        """Test that ending a session requires authentication."""
        book_id = create_test_book["book_id"]
        
        # Start a session first
        start_response = client.post(
            f"/books/{book_id}/reading-sessions",
            json={"start_time": datetime.now().isoformat()},
            headers=authenticated_headers
        )
        session_id = start_response.json()["id"]
        
        # Try to end without auth
        response = client.put(
            f"/reading-sessions/{session_id}",
            params={"end_time": datetime.now().isoformat()}
        )
        
        assert response.status_code == 401


# ============================================
# Reading Session Retrieval Tests
# ============================================

@pytest.mark.integration
class TestReadingSessionRetrieval:
    """Tests for reading session retrieval endpoints."""
    
    def test_get_my_reading_sessions(self, client, authenticated_headers, create_test_book):
        """Test getting current user's reading sessions."""
        book_id = create_test_book["book_id"]
        
        # Create a session first
        client.post(
            f"/books/{book_id}/reading-sessions",
            json={"start_time": datetime.now().isoformat()},
            headers=authenticated_headers
        )
        
        # Get sessions
        response = client.get("/users/me/reading-sessions", headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_sessions_filter_by_book(self, client, authenticated_headers, create_test_book):
        """Test filtering sessions by book ID."""
        book_id = create_test_book["book_id"]
        
        # Create a session
        client.post(
            f"/books/{book_id}/reading-sessions",
            json={"start_time": datetime.now().isoformat()},
            headers=authenticated_headers
        )
        
        # Get sessions filtered by book
        response = client.get(
            "/users/me/reading-sessions",
            params={"book_id": book_id},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(s["book_id"] == book_id for s in data)
    
    def test_get_sessions_pagination(self, client, authenticated_headers):
        """Test sessions pagination."""
        response = client.get(
            "/users/me/reading-sessions",
            params={"limit": 5, "offset": 0},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_get_book_reading_sessions(self, client, authenticated_headers, create_test_book):
        """Test getting reading session stats for a book."""
        book_id = create_test_book["book_id"]
        
        # Create a session
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=30)
        client.post(
            f"/books/{book_id}/reading-sessions",
            json={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_min": 30
            },
            headers=authenticated_headers
        )
        
        # Get book sessions
        response = client.get(
            f"/books/{book_id}/reading-sessions",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200


# ============================================
# Reading Stats Tests
# ============================================

@pytest.mark.integration
class TestReadingStats:
    """Tests for reading statistics endpoint."""
    
    def test_get_reading_stats_week(self, client, authenticated_headers):
        """Test getting reading stats for the week."""
        response = client.get(
            "/users/me/reading-stats",
            params={"period": "week"},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_minutes" in data or "period" in data
    
    def test_get_reading_stats_month(self, client, authenticated_headers):
        """Test getting reading stats for the month."""
        response = client.get(
            "/users/me/reading-stats",
            params={"period": "month"},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
    
    def test_get_reading_stats_day(self, client, authenticated_headers):
        """Test getting reading stats for the day."""
        response = client.get(
            "/users/me/reading-stats",
            params={"period": "day"},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
    
    def test_get_reading_stats_year(self, client, authenticated_headers):
        """Test getting reading stats for the year."""
        response = client.get(
            "/users/me/reading-stats",
            params={"period": "year"},
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
    
    def test_get_reading_stats_without_auth(self, client):
        """Test that reading stats require authentication."""
        response = client.get("/users/me/reading-stats", params={"period": "week"})
        
        assert response.status_code == 401

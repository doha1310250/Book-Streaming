"""
Integration tests for miscellaneous endpoints.
Covers health check, admin routes, review operations, and frontend routes.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import generate_id


# ============================================
# Health Check Tests
# ============================================

@pytest.mark.integration
class TestHealthCheck:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint returns OK."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"


# ============================================
# Admin Routes Tests
# ============================================

@pytest.mark.integration
class TestAdminRoutes:
    """Tests for admin endpoints."""
    
    def test_verify_book(self, client, create_test_book):
        """Test verifying a book."""
        book_id = create_test_book["book_id"]
        
        response = client.patch(
            f"/admin/books/{book_id}/verify",
            params={"verify": True}
        )
        
        assert response.status_code == 200
    
    def test_unverify_book(self, client, create_test_book):
        """Test unverifying a book."""
        book_id = create_test_book["book_id"]
        
        # First verify
        client.patch(f"/admin/books/{book_id}/verify", params={"verify": True})
        
        # Then unverify
        response = client.patch(
            f"/admin/books/{book_id}/verify",
            params={"verify": False}
        )
        
        assert response.status_code == 200
    
    def test_verify_nonexistent_book(self, client):
        """Test verifying a book that doesn't exist."""
        response = client.patch(
            "/admin/books/nonexistent-book-id/verify",
            params={"verify": True}
        )
        
        assert response.status_code == 404


# ============================================
# Review Delete Tests
# ============================================

@pytest.mark.integration
class TestReviewDelete:
    """Tests for review deletion endpoint."""
    
    def test_delete_own_review(self, client, authenticated_headers, create_test_book):
        """Test deleting own review."""
        book_id = create_test_book["book_id"]
        
        # Create a review first
        review_response = client.post(
            f"/books/{book_id}/reviews",
            json={"rating": 4.0, "review_comment": "Review to delete"},
            headers=authenticated_headers
        )
        assert review_response.status_code == 201
        review_id = review_response.json()["id"]
        
        # Delete the review
        response = client.delete(
            f"/reviews/{review_id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
    
    def test_delete_review_not_found(self, client, authenticated_headers):
        """Test deleting a review that doesn't exist."""
        response = client.delete(
            "/reviews/nonexistent-review-id",
            headers=authenticated_headers
        )
        
        assert response.status_code == 404
    
    def test_delete_review_without_auth(self, client, authenticated_headers, create_test_book):
        """Test that deleting review requires authentication."""
        book_id = create_test_book["book_id"]
        
        # Create a review first
        review_response = client.post(
            f"/books/{book_id}/reviews",
            json={"rating": 4.0, "review_comment": "Review"},
            headers=authenticated_headers
        )
        review_id = review_response.json()["id"]
        
        # Try to delete without auth
        response = client.delete(f"/reviews/{review_id}")
        
        assert response.status_code == 401


# ============================================
# Review Summary Tests
# ============================================

@pytest.mark.integration
class TestReviewSummary:
    """Tests for review summary endpoint."""
    
    def test_get_book_reviews_summary(self, client, create_test_book, authenticated_headers):
        """Test getting review summary for a book."""
        book_id = create_test_book["book_id"]
        
        # Create a review
        client.post(
            f"/books/{book_id}/reviews",
            json={"rating": 4.5, "review_comment": "Great book!"},
            headers=authenticated_headers
        )
        
        # Get summary
        response = client.get(f"/books/{book_id}/reviews/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert "average_rating" in data or "total_reviews" in data
    
    def test_get_reviews_summary_nonexistent_book(self, client):
        """Test getting summary for nonexistent book."""
        response = client.get("/books/nonexistent-book-id/reviews/summary")
        
        assert response.status_code == 404


# ============================================
# Book Stats Tests
# ============================================

@pytest.mark.integration
class TestBookStats:
    """Tests for book statistics endpoint."""
    
    def test_get_book_stats(self, client):
        """Test getting total book count."""
        response = client.get("/books/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_books" in data


# ============================================
# Book Filter Tests
# ============================================

@pytest.mark.integration
class TestBookFilters:
    """Tests for book filtering by verified status."""
    
    def test_filter_books_verified(self, client, create_test_book):
        """Test filtering books by verified status."""
        book_id = create_test_book["book_id"]
        
        # Verify the book
        client.patch(f"/admin/books/{book_id}/verify", params={"verify": True})
        
        # Filter verified books
        response = client.get("/books", params={"verified": True})
        
        assert response.status_code == 200
        data = response.json()
        # All returned books should be verified
        for book in data:
            assert book.get("is_verified", False) == True
    
    def test_filter_books_unverified(self, client, create_test_book):
        """Test filtering unverified books."""
        response = client.get("/books", params={"verified": False})
        
        assert response.status_code == 200
        data = response.json()
        # All returned books should be unverified
        for book in data:
            assert book.get("is_verified", True) == False


# ============================================
# Frontend Routes Tests
# ============================================

@pytest.mark.integration
class TestFrontendRoutes:
    """Tests for frontend page serving routes."""
    
    def test_serve_index(self, client):
        """Test serving the index/landing page."""
        response = client.get("/")
        
        # Should serve HTML content or JSON fallback
        assert response.status_code == 200
    
    def test_serve_dashboard(self, client):
        """Test serving the dashboard page."""
        response = client.get("/dashboard")
        
        assert response.status_code == 200
    
    def test_serve_login(self, client):
        """Test serving the login page."""
        response = client.get("/login")
        
        assert response.status_code == 200
    
    def test_serve_timer(self, client):
        """Test serving the timer page."""
        response = client.get("/timer")
        
        assert response.status_code == 200
    
    def test_serve_profile(self, client):
        """Test serving the profile page."""
        response = client.get("/profile")
        
        assert response.status_code == 200
    
    def test_serve_social(self, client):
        """Test serving the social page."""
        response = client.get("/social")
        
        assert response.status_code == 200
    
    def test_serve_user_profile(self, client):
        """Test serving the user profile page."""
        response = client.get("/user-profile")
        
        assert response.status_code == 200


# ============================================
# Check Mark Status Tests
# ============================================

@pytest.mark.integration
class TestCheckMarkStatus:
    """Tests for checking if a book is marked."""
    
    def test_check_book_is_marked(self, client, authenticated_headers, create_test_book):
        """Test checking if a book is marked."""
        book_id = create_test_book["book_id"]
        
        # Mark the book first
        client.post(f"/books/{book_id}/mark", headers=authenticated_headers)
        
        # Check status
        response = client.get(
            f"/books/{book_id}/is-marked",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_marked"] == True
    
    def test_check_book_not_marked(self, client, authenticated_headers, create_test_book):
        """Test checking if a book is not marked."""
        book_id = create_test_book["book_id"]
        
        response = client.get(
            f"/books/{book_id}/is-marked",
            headers=authenticated_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_marked"] == False

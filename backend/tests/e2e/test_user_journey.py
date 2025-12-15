"""
End-to-end tests for complete user journeys.
These tests simulate real user scenarios from start to finish.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import generate_id


# ============================================
# Complete User Journey Tests
# ============================================

@pytest.mark.e2e
class TestCompleteUserJourney:
    """
    End-to-end tests simulating complete user flows.
    These tests verify that the entire system works together.
    """
    
    def test_new_user_complete_flow(self, client, clean_test_data):
        """
        Test complete flow: Register → Login → Create Book → Review → Mark
        
        This simulates a new user joining the platform and performing
        all common actions.
        """
        unique_id = generate_id()[:8]
        
        # Step 1: Register
        user_data = {
            "email": f"e2e_user_{unique_id}@example.com",
            "name": f"E2E Test User {unique_id}",
            "password": "E2ETestPass1!"
        }
        
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201, f"Registration failed: {register_response.text}"
        user = register_response.json()
        clean_test_data["users"].append(user["user_id"])
        
        # Step 2: Login
        login_response = client.post("/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200, "Login failed"
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Check profile
        profile_response = client.get("/users/me", headers=headers)
        assert profile_response.status_code == 200
        assert profile_response.json()["email"] == user_data["email"]
        
        # Step 4: Create a book
        book_data = {
            "title": f"E2E Test Book {unique_id}",
            "author_name": "E2E Test Author"
        }
        book_response = client.post("/books", params=book_data, headers=headers)
        assert book_response.status_code == 201, f"Book creation failed: {book_response.text}"
        book = book_response.json()
        clean_test_data["books"].append(book["book_id"])
        
        # Step 5: Review the book
        review_data = {
            "rating": 4.5,
            "review_comment": "Great book, highly recommend!"
        }
        review_response = client.post(
            f"/books/{book['book_id']}/reviews",
            json=review_data,
            headers=headers
        )
        assert review_response.status_code == 201, f"Review creation failed: {review_response.text}"
        
        # Step 6: Mark the book for later
        mark_response = client.post(
            f"/books/{book['book_id']}/mark",
            headers=headers
        )
        assert mark_response.status_code == 200
        
        # Step 7: Verify marked books
        marks_response = client.get("/users/me/marks", headers=headers)
        assert marks_response.status_code == 200
        marked_books = marks_response.json()
        assert any(b["book_id"] == book["book_id"] for b in marked_books)
        
        # Step 8: View book reviews
        reviews_response = client.get(f"/books/{book['book_id']}/reviews")
        assert reviews_response.status_code == 200
    
    def test_book_discovery_flow(self, client, clean_test_data):
        """
        Test book discovery flow: Browse → Search → View Details → Mark
        
        This simulates a user discovering books on the platform.
        """
        unique_id = generate_id()[:8]
        
        # Create user and book first
        user_data = {
            "email": f"discovery_user_{unique_id}@example.com",
            "name": "Discovery User",
            "password": "DiscoverPass1!"
        }
        
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201
        clean_test_data["users"].append(register_response.json()["user_id"])
        
        login_response = client.post("/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create some books
        for i in range(3):
            book_response = client.post("/books", params={
                "title": f"Discovery Book {unique_id} Part {i+1}",
                "author_name": f"Author {unique_id}"
            }, headers=headers)
            if book_response.status_code == 201:
                clean_test_data["books"].append(book_response.json()["book_id"])
        
        # Step 1: Browse all books
        browse_response = client.get("/books", params={"limit": 10})
        assert browse_response.status_code == 200
        all_books = browse_response.json()
        assert len(all_books) > 0
        
        # Step 2: Search by author
        search_response = client.get("/books", params={"author": f"Author {unique_id}"})
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results) >= 1
        
        # Step 3: View book details
        if search_results:
            book_id = search_results[0]["book_id"]
            details_response = client.get(f"/books/{book_id}")
            assert details_response.status_code == 200
            assert details_response.json()["book_id"] == book_id
            
            # Step 4: Mark the book
            mark_response = client.post(f"/books/{book_id}/mark", headers=headers)
            assert mark_response.status_code == 200
            
            # Step 5: Check if marked
            check_response = client.get(f"/books/{book_id}/is-marked", headers=headers)
            assert check_response.status_code == 200
            assert check_response.json()["is_marked"] == True
    
    def test_review_interaction_flow(self, client, clean_test_data):
        """
        Test review flow: Create Review → Update Review → View Reviews
        
        This simulates users interacting with the review system.
        """
        unique_id = generate_id()[:8]
        
        # Setup: Create user and book
        user_data = {
            "email": f"reviewer_{unique_id}@example.com",
            "name": "Reviewer User",
            "password": "ReviewPass1!"
        }
        
        client.post("/auth/register", json=user_data)
        login_response = client.post("/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        clean_test_data["users"].append(login_response.json()["user"]["user_id"])
        
        # Create book
        book_response = client.post("/books", params={
            "title": f"Book for Reviews {unique_id}",
            "author_name": "Review Author"
        }, headers=headers)
        book = book_response.json()
        clean_test_data["books"].append(book["book_id"])
        
        # Step 1: Create initial review
        review_response = client.post(
            f"/books/{book['book_id']}/reviews",
            json={"rating": 3.0, "review_comment": "Initial review - it's okay"},
            headers=headers
        )
        assert review_response.status_code == 201
        review = review_response.json()
        
        # Step 2: Update the review after finishing the book
        update_response = client.put(
            f"/reviews/{review['id']}",
            json={"rating": 5.0, "review_comment": "Finished the book - it's amazing!"},
            headers=headers
        )
        assert update_response.status_code == 200
        updated_review = update_response.json()
        assert float(updated_review["rating"]) == 5.0
        
        # Step 3: View all reviews for the book
        reviews_response = client.get(f"/books/{book['book_id']}/reviews")
        assert reviews_response.status_code == 200
        
        # Step 4: View user's own reviews
        my_reviews_response = client.get("/users/me/reviews", headers=headers)
        assert my_reviews_response.status_code == 200
        my_reviews = my_reviews_response.json()
        assert any(r["id"] == review["id"] for r in my_reviews)


# ============================================
# Error Handling Journey Tests
# ============================================

@pytest.mark.e2e
class TestErrorHandlingJourney:
    """
    Tests for proper error handling throughout user journeys.
    """
    
    def test_unauthorized_actions_flow(self, client, create_test_book):
        """Test that unauthorized actions are properly blocked."""
        book_id = create_test_book["book_id"]
        
        # Try to update without auth
        update_response = client.put(f"/books/{book_id}", json={"title": "Hacked"})
        assert update_response.status_code == 401
        
        # Try to delete without auth
        delete_response = client.delete(f"/books/{book_id}")
        assert delete_response.status_code == 401
        
        # Try to mark without auth
        mark_response = client.post(f"/books/{book_id}/mark")
        assert mark_response.status_code == 401
        
        # Try to review without auth
        review_response = client.post(
            f"/books/{book_id}/reviews",
            json={"rating": 5.0}
        )
        assert review_response.status_code == 401
    
    def test_not_found_resources_flow(self, client, authenticated_headers):
        """Test that missing resources return proper 404 errors."""
        fake_id = "nonexistent-book-id"
        
        # Try to get non-existent book
        get_response = client.get(f"/books/{fake_id}")
        assert get_response.status_code == 404
        
        # Try to mark non-existent book
        mark_response = client.post(f"/books/{fake_id}/mark", headers=authenticated_headers)
        assert mark_response.status_code == 404
        
        # Try to review non-existent book
        review_response = client.post(
            f"/books/{fake_id}/reviews",
            json={"rating": 5.0},
            headers=authenticated_headers
        )
        assert review_response.status_code == 404

"""
Unit tests for Pydantic models.
These tests validate model constraints and serialization.
"""
import pytest
import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pydantic import ValidationError
from models import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    BookBase,
    BookUpdate,
    BookResponse,
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReadingSessionBase
)


# ============================================
# User Model Tests
# ============================================

@pytest.mark.unit
class TestUserModels:
    """Tests for User Pydantic models."""
    
    def test_user_create_valid(self):
        """Test creating a valid UserCreate model."""
        user = UserCreate(
            email="test@example.com",
            name="Test User",
            password="ValidPass1!"
        )
        assert user.email == "test@example.com"
        assert user.name == "Test User"
    
    def test_user_create_invalid_email(self):
        """Test that invalid email raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="notanemail",
                name="Test User",
                password="ValidPass1!"
            )
        assert "email" in str(exc_info.value).lower()
    
    def test_user_create_weak_password(self):
        """Test that weak password raises ValidationError."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                name="Test User",
                password="weak"
            )
    
    def test_user_create_empty_name(self):
        """Test that empty name raises ValidationError."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                name="",
                password="ValidPass1!"
            )
    
    def test_user_login_valid(self):
        """Test creating a valid UserLogin model."""
        login = UserLogin(
            email="test@example.com",
            password="anypassword"
        )
        assert login.email == "test@example.com"
    
    def test_user_update_optional_fields(self):
        """Test that UserUpdate fields are optional."""
        update = UserUpdate()
        assert update.name is None
        assert update.password is None
    
    def test_user_update_with_name(self):
        """Test UserUpdate with only name."""
        update = UserUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.password is None
    
    def test_user_response_from_dict(self):
        """Test creating UserResponse from dictionary."""
        data = {
            "user_id": "test-123",
            "email": "test@example.com",
            "name": "Test User",
            "last_streak": 5,
            "current_streak": 3,
            "created_at": datetime.now()
        }
        response = UserResponse(**data)
        assert response.user_id == "test-123"
        assert response.current_streak == 3


# ============================================
# Book Model Tests
# ============================================

@pytest.mark.unit
class TestBookModels:
    """Tests for Book Pydantic models."""
    
    def test_book_base_valid(self):
        """Test creating a valid BookBase model."""
        book = BookBase(
            title="Test Book",
            author_name="Test Author"
        )
        assert book.title == "Test Book"
        assert book.author_name == "Test Author"
        assert book.publish_date is None
    
    def test_book_base_with_date(self):
        """Test BookBase with publish date."""
        book = BookBase(
            title="Test Book",
            author_name="Test Author",
            publish_date=date(2024, 1, 15)
        )
        assert book.publish_date == date(2024, 1, 15)
    
    def test_book_base_empty_title(self):
        """Test that empty title raises ValidationError."""
        with pytest.raises(ValidationError):
            BookBase(
                title="",
                author_name="Test Author"
            )
    
    def test_book_base_empty_author(self):
        """Test that empty author raises ValidationError."""
        with pytest.raises(ValidationError):
            BookBase(
                title="Test Book",
                author_name=""
            )
    
    def test_book_base_title_trimmed(self):
        """Test that title is trimmed."""
        book = BookBase(
            title="  Test Book  ",
            author_name="Test Author"
        )
        assert book.title == "Test Book"
    
    def test_book_update_all_optional(self):
        """Test that BookUpdate fields are all optional."""
        update = BookUpdate()
        assert update.title is None
        assert update.author_name is None
        assert update.publish_date is None
    
    def test_book_response_from_dict(self):
        """Test creating BookResponse from dictionary."""
        data = {
            "book_id": "book-123",
            "user_id": "user-123",
            "title": "Test Book",
            "author_name": "Test Author",
            "is_verified": False,
            "cover_url": None,
            "created_at": datetime.now()
        }
        response = BookResponse(**data)
        assert response.book_id == "book-123"
        assert response.is_verified == False


# ============================================
# Review Model Tests
# ============================================

@pytest.mark.unit
class TestReviewModels:
    """Tests for Review Pydantic models."""
    
    def test_review_create_valid(self):
        """Test creating a valid ReviewCreate model."""
        review = ReviewCreate(
            rating=Decimal("4.5"),
            review_comment="Great book!"
        )
        assert review.rating == Decimal("4.5")
        assert review.review_comment == "Great book!"
    
    def test_review_create_rating_only(self):
        """Test ReviewCreate with only rating."""
        review = ReviewCreate(rating=Decimal("5.0"))
        assert review.rating == Decimal("5.0")
        assert review.review_comment is None
    
    def test_review_create_comment_only(self):
        """Test ReviewCreate with only comment."""
        review = ReviewCreate(review_comment="Nice read!")
        assert review.rating is None
        assert review.review_comment == "Nice read!"
    
    def test_review_rating_out_of_range_high(self):
        """Test that rating > 5 raises ValidationError."""
        with pytest.raises(ValidationError):
            ReviewCreate(rating=Decimal("5.5"))
    
    def test_review_rating_out_of_range_low(self):
        """Test that rating < 0 raises ValidationError."""
        with pytest.raises(ValidationError):
            ReviewCreate(rating=Decimal("-1"))
    
    def test_review_response_from_dict(self):
        """Test creating ReviewResponse from dictionary."""
        now = datetime.now()
        data = {
            "id": "review-123",
            "user_id": "user-123",
            "book_id": "book-123",
            "rating": Decimal("4.0"),
            "review_comment": "Good book",
            "created_at": now,
            "updated_at": now
        }
        response = ReviewResponse(**data)
        assert response.id == "review-123"
        assert response.rating == Decimal("4.0")


# ============================================
# Reading Session Model Tests
# ============================================

@pytest.mark.unit
class TestReadingSessionModels:
    """Tests for ReadingSession Pydantic models."""
    
    def test_reading_session_valid(self):
        """Test creating a valid ReadingSessionBase model."""
        start = datetime.now()
        end = start + timedelta(hours=1)
        session = ReadingSessionBase(
            start_time=start,
            end_time=end,
            duration_min=60
        )
        assert session.duration_min == 60
    
    def test_reading_session_end_before_start(self):
        """Test that end_time before start_time raises ValidationError."""
        start = datetime.now()
        end = start - timedelta(hours=1)  # End before start
        with pytest.raises(ValidationError):
            ReadingSessionBase(
                start_time=start,
                end_time=end
            )
    
    def test_reading_session_no_end_time(self):
        """Test ReadingSessionBase without end_time."""
        session = ReadingSessionBase(start_time=datetime.now())
        assert session.end_time is None
        assert session.duration_min is None


# Import timedelta for tests
from datetime import timedelta

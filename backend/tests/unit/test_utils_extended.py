"""
Additional unit tests for utility functions to improve coverage.
Focuses on edge cases, image validation, rate limiting, and streak calculation.
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import (
    validate_email,
    validate_password,
    validate_author_name,
    validate_book_title,
    validate_book_data,
    generate_id,
    hash_password,
    verify_password,
    sanitize_filename,
    calculate_streak,
    get_cover_url,
    get_image_extension,
    validate_image_file,
    delete_book_cover,
    RateLimiter
)


# ============================================
# Password Verification Tests
# ============================================

@pytest.mark.unit
class TestPasswordVerification:
    """Tests for password verification function."""
    
    def test_verify_correct_password(self):
        """Test that correct password verifies successfully."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed) == True
    
    def test_verify_wrong_password(self):
        """Test that wrong password fails verification."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert verify_password("WrongPassword123!", hashed) == False
    
    def test_verify_invalid_hash_format(self):
        """Test that invalid hash format returns False."""
        assert verify_password("password", "invalid_hash_no_separator") == False
    
    def test_verify_empty_password(self):
        """Test verification with empty password."""
        hashed = hash_password("TestPassword123!")
        assert verify_password("", hashed) == False


# ============================================
# Image Extension Tests
# ============================================

@pytest.mark.unit
class TestImageExtension:
    """Tests for image extension function."""
    
    def test_jpeg_extension(self):
        """Test JPEG content type returns .jpg."""
        assert get_image_extension("image/jpeg") == ".jpg"
    
    def test_jpg_extension(self):
        """Test JPG content type returns .jpg."""
        assert get_image_extension("image/jpg") == ".jpg"
    
    def test_png_extension(self):
        """Test PNG content type returns .png."""
        assert get_image_extension("image/png") == ".png"
    
    def test_webp_extension(self):
        """Test WebP content type returns .webp."""
        assert get_image_extension("image/webp") == ".webp"
    
    def test_unknown_extension(self):
        """Test unknown content type defaults to .jpg."""
        assert get_image_extension("image/unknown") == ".jpg"
        assert get_image_extension("") == ".jpg"


# ============================================
# Streak Calculation Tests
# ============================================

@pytest.mark.unit
class TestStreakCalculation:
    """Tests for streak calculation function."""
    
    def test_first_login_no_previous(self):
        """Test first login with no previous date."""
        result = calculate_streak(None, 0)
        assert result["current_streak"] == 1
        assert result["updated"] == True
    
    def test_same_day_login(self):
        """Test logging in same day doesn't increment streak."""
        today = datetime.now()
        result = calculate_streak(today, 5)
        assert result["current_streak"] == 5
        assert result["updated"] == False
    
    def test_consecutive_day_login(self):
        """Test consecutive day increments streak."""
        yesterday = datetime.now() - timedelta(days=1)
        result = calculate_streak(yesterday, 5)
        assert result["current_streak"] == 6
        assert result["last_streak"] == 5
        assert result["updated"] == True
    
    def test_streak_broken(self):
        """Test streak resets when more than 1 day gap."""
        three_days_ago = datetime.now() - timedelta(days=3)
        result = calculate_streak(three_days_ago, 10)
        assert result["current_streak"] == 1
        assert result["last_streak"] == 10
        assert result["updated"] == True


# ============================================
# Rate Limiter Tests
# ============================================

@pytest.mark.unit
class TestRateLimiter:
    """Tests for rate limiter class."""
    
    def test_rate_limiter_allows_first_request(self):
        """Test rate limiter allows first request."""
        limiter = RateLimiter()
        assert limiter.is_allowed("user1", limit=5) == True
    
    def test_rate_limiter_allows_under_limit(self):
        """Test rate limiter allows requests under limit."""
        limiter = RateLimiter()
        for _ in range(4):
            limiter.is_allowed("user1", limit=5)
        assert limiter.is_allowed("user1", limit=5) == True
    
    def test_rate_limiter_blocks_over_limit(self):
        """Test rate limiter blocks when over limit."""
        limiter = RateLimiter()
        for _ in range(5):
            limiter.is_allowed("user1", limit=5)
        assert limiter.is_allowed("user1", limit=5) == False
    
    def test_rate_limiter_different_users(self):
        """Test rate limiter tracks users separately."""
        limiter = RateLimiter()
        for _ in range(5):
            limiter.is_allowed("user1", limit=5)
        # User 2 should still be allowed
        assert limiter.is_allowed("user2", limit=5) == True


# ============================================
# Book Title Validation Tests
# ============================================

@pytest.mark.unit
class TestBookTitleValidation:
    """Tests for book title validation."""
    
    def test_empty_title(self):
        """Test empty title fails validation."""
        is_valid, error = validate_book_title("")
        assert is_valid == False
        assert "empty" in error.lower()
    
    def test_whitespace_only_title(self):
        """Test whitespace-only title fails validation."""
        is_valid, error = validate_book_title("   ")
        assert is_valid == False
    
    def test_title_too_long(self):
        """Test very long title fails validation."""
        long_title = "A" * 300
        is_valid, error = validate_book_title(long_title)
        assert is_valid == False
        assert "256" in error or "255" in error or "exceed" in error.lower()


# ============================================
# Author Name Validation Tests
# ============================================

@pytest.mark.unit
class TestAuthorNameValidationExtended:
    """Extended tests for author name validation."""
    
    def test_none_author(self):
        """Test None author fails validation."""
        is_valid, error = validate_author_name(None)
        assert is_valid == False


# ============================================
# Sanitize Filename Tests
# ============================================

@pytest.mark.unit
class TestSanitizeFilenameExtended:
    """Extended tests for filename sanitization."""
    
    def test_consecutive_special_chars(self):
        """Test consecutive special characters are cleaned."""
        result = sanitize_filename("Book---Name")
        assert "--" not in result
    
    def test_leading_trailing_underscores(self):
        """Test leading/trailing underscores are removed."""
        result = sanitize_filename("___test___")
        assert not result.startswith("_")
        assert not result.endswith("_")
    
    def test_empty_after_cleaning(self):
        """Test empty result becomes 'book'."""
        result = sanitize_filename("@#$%^&*()")
        assert result == "book"
    
    def test_very_long_filename(self):
        """Test long filenames are truncated."""
        long_name = "A" * 200
        result = sanitize_filename(long_name)
        assert len(result) <= 100


# ============================================
# Delete Book Cover Tests
# ============================================

@pytest.mark.unit
class TestDeleteBookCover:
    """Tests for delete book cover function."""
    
    def test_delete_empty_filename(self):
        """Test deleting empty filename returns False."""
        assert delete_book_cover("") == False
        assert delete_book_cover(None) == False
    
    def test_delete_nonexistent_file(self):
        """Test deleting non-existent file returns False."""
        result = delete_book_cover("nonexistent_file_12345.jpg")
        assert result == False


# ============================================
# Get Cover URL Tests
# ============================================

@pytest.mark.unit
class TestGetCoverUrl:
    """Tests for cover URL generation."""
    
    def test_get_cover_url_valid(self):
        """Test valid filename generates correct URL."""
        result = get_cover_url("image.jpg")
        assert result == "/images/image.jpg"
    
    def test_get_cover_url_empty(self):
        """Test empty filename returns empty string."""
        assert get_cover_url("") == ""
    
    def test_get_cover_url_none(self):
        """Test None filename returns empty string."""
        assert get_cover_url(None) == ""


# ============================================
# Validate Book Data Tests
# ============================================

@pytest.mark.unit
class TestValidateBookData:
    """Tests for comprehensive book data validation."""
    
    def test_valid_book_data(self):
        """Test valid book data passes validation."""
        result = validate_book_data("Valid Title", "Valid Author")
        assert result["is_valid"] == True
        assert len(result["errors"]) == 0
    
    def test_invalid_title_only(self):
        """Test invalid title with valid author."""
        result = validate_book_data("", "Valid Author")
        assert result["is_valid"] == False
        assert result["title_valid"] == False
        assert result["author_valid"] == True
    
    def test_invalid_author_only(self):
        """Test valid title with invalid author."""
        result = validate_book_data("Valid Title", "")
        assert result["is_valid"] == False
        assert result["title_valid"] == True
        assert result["author_valid"] == False
    
    def test_both_invalid(self):
        """Test both title and author invalid."""
        result = validate_book_data("", "")
        assert result["is_valid"] == False
        assert len(result["errors"]) == 2

"""
Unit tests for utility functions.
These tests run without database access.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import (
    validate_email,
    validate_password,
    validate_author_name,
    generate_id,
    hash_password,
    sanitize_filename,
    calculate_streak,
    get_cover_url
)
from datetime import datetime, timedelta


# ============================================
# Email Validation Tests
# ============================================

@pytest.mark.unit
class TestEmailValidation:
    """Tests for email validation function."""
    
    def test_valid_email(self):
        """Test that valid emails pass validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk",
            "test123@test.io"
        ]
        for email in valid_emails:
            result = validate_email(email)
            # validate_email returns tuple (bool, str) or just bool depending on implementation
            is_valid = result[0] if isinstance(result, tuple) else result
            assert is_valid, f"Email {email} should be valid"
    
    def test_invalid_email(self):
        """Test that invalid emails fail validation."""
        invalid_emails = [
            "notanemail",
            "@nodomain.com",
            "no@",
            "spaces in@email.com",
            ""
        ]
        for email in invalid_emails:
            result = validate_email(email)
            is_valid = result[0] if isinstance(result, tuple) else result
            assert not is_valid, f"Email {email} should be invalid"


# ============================================
# Password Validation Tests
# ============================================

@pytest.mark.unit
class TestPasswordValidation:
    """Tests for password validation function."""
    
    def test_valid_password(self, sample_valid_passwords):
        """Test that valid passwords pass validation."""
        for password in sample_valid_passwords:
            result = validate_password(password)
            assert result["is_valid"], f"Password {password} should be valid"
            assert len(result["errors"]) == 0
    
    def test_password_too_short(self):
        """Test that short passwords fail validation."""
        result = validate_password("Ab1!")
        assert not result["is_valid"]
        assert any("8 characters" in err for err in result["errors"])
    
    def test_password_no_uppercase(self):
        """Test that passwords without uppercase fail."""
        result = validate_password("lowercase1!")
        assert not result["is_valid"]
        assert any("uppercase" in err for err in result["errors"])
    
    def test_password_no_lowercase(self):
        """Test that passwords without lowercase fail."""
        result = validate_password("UPPERCASE1!")
        assert not result["is_valid"]
        assert any("lowercase" in err for err in result["errors"])
    
    def test_password_no_digit(self):
        """Test that passwords without digits fail."""
        result = validate_password("NoDigits!")
        assert not result["is_valid"]
        assert any("digit" in err for err in result["errors"])
    
    def test_password_no_special_char(self):
        """Test that passwords without special characters fail."""
        result = validate_password("NoSpecial123")
        assert not result["is_valid"]
        assert any("special" in err for err in result["errors"])


# ============================================
# Author Name Validation Tests
# ============================================

@pytest.mark.unit
class TestAuthorNameValidation:
    """Tests for author name validation function."""
    
    def test_valid_author_names(self):
        """Test that valid author names pass validation."""
        valid_names = [
            "John Doe",
            "J.K. Rowling",
            "Stephen King",
            "Gabriel García Márquez"
        ]
        for name in valid_names:
            is_valid, error = validate_author_name(name)
            assert is_valid, f"Author name '{name}' should be valid: {error}"
    
    def test_empty_author_name(self):
        """Test that empty names fail validation."""
        is_valid, error = validate_author_name("")
        assert not is_valid
        assert "empty" in error.lower()
    
    def test_whitespace_only_author_name(self):
        """Test that whitespace-only names fail validation."""
        is_valid, error = validate_author_name("   ")
        assert not is_valid
    
    def test_author_name_too_long(self):
        """Test that very long names fail validation."""
        long_name = "A" * 101
        is_valid, error = validate_author_name(long_name)
        assert not is_valid
        assert "100" in error


# ============================================
# Utility Function Tests
# ============================================

@pytest.mark.unit
class TestUtilityFunctions:
    """Tests for general utility functions."""
    
    def test_generate_id_uniqueness(self):
        """Test that generated IDs are unique."""
        ids = [generate_id() for _ in range(100)]
        assert len(ids) == len(set(ids)), "Generated IDs should be unique"
    
    def test_generate_id_format(self):
        """Test that generated IDs have correct format."""
        id_ = generate_id()
        assert isinstance(id_, str)
        assert len(id_) == 36  # UUID format
        assert id_.count("-") == 4
    
    def test_hash_password_not_plain(self):
        """Test that hashed password is different from plain password."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) > 0
    
    def test_sanitize_filename_removes_special_chars(self):
        """Test that special characters are removed from filenames."""
        result = sanitize_filename("Test Book: A Story!")
        assert ":" not in result
        assert "!" not in result
        assert result.islower()
    
    def test_sanitize_filename_replaces_spaces(self):
        """Test that spaces are replaced with underscores."""
        result = sanitize_filename("My Book Title")
        assert " " not in result
        assert "_" in result
    
    def test_sanitize_filename_empty_input(self):
        """Test that empty input returns default value."""
        result = sanitize_filename("")
        assert result == "book"
    
    def test_get_cover_url_with_filename(self):
        """Test cover URL generation."""
        url = get_cover_url("mybook.jpg")
        assert url == "/images/mybook.jpg"
    
    def test_get_cover_url_empty(self):
        """Test cover URL with empty filename."""
        url = get_cover_url("")
        assert url == ""


# ============================================
# Streak Calculation Tests
# ============================================

@pytest.mark.unit
class TestStreakCalculation:
    """Tests for reading streak calculation."""
    
    def test_first_login_starts_streak(self):
        """Test that first login starts a streak of 1."""
        result = calculate_streak(None, 0)
        assert result["current_streak"] == 1
        assert result["updated"] == True
    
    def test_consecutive_day_increases_streak(self):
        """Test that logging in on consecutive days increases streak."""
        yesterday = datetime.now() - timedelta(days=1)
        result = calculate_streak(yesterday, 5)
        assert result["current_streak"] == 6
        assert result["updated"] == True
    
    def test_same_day_login_no_change(self):
        """Test that logging in same day doesn't change streak."""
        today = datetime.now()
        result = calculate_streak(today, 5)
        assert result["current_streak"] == 5
        assert result["updated"] == False
    
    def test_missed_day_resets_streak(self):
        """Test that missing a day resets the streak."""
        two_days_ago = datetime.now() - timedelta(days=2)
        result = calculate_streak(two_days_ago, 10)
        assert result["current_streak"] == 1
        assert result["last_streak"] == 10
        assert result["updated"] == True

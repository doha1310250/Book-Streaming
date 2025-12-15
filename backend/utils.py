# utils.py
import os
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import re
from pathlib import Path
import imghdr
from fastapi import UploadFile, HTTPException, status, Depends

from config import settings, IMAGES_DIR
from database import db

# Validation functions
def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, ""

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def validate_book_title(title: str, user_id: Optional[str] = None, exclude_book_id: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validate book title with duplicate check
    
    Args:
        title: Book title to validate
        user_id: Optional user ID to check for user-specific duplicates
        exclude_book_id: Optional book ID to exclude from duplicate check (for updates)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Basic validation
    if not title or len(title.strip()) == 0:
        return False, "Book title cannot be empty"
    
    if len(title) > 255:
        return False, "Book title cannot exceed 255 characters"
    
    # Check for duplicate title
    is_duplicate, existing_book = check_duplicate_title(title, user_id, exclude_book_id)
    
    if is_duplicate:
        if user_id and existing_book and existing_book.get('user_id') == user_id:
            return False, f"You already have a book with the title '{title}'"
        else:
            return False, f"A book with the title '{title}' already exists"
    
    return True, ""

def check_duplicate_title(title: str, user_id: Optional[str] = None, exclude_book_id: Optional[str] = None) -> Tuple[bool, Optional[Dict]]:
    """
    Check if a book title already exists in the database
    
    Args:
        title: Book title to check
        user_id: Optional user ID to check for user-specific duplicates
        exclude_book_id: Optional book ID to exclude from duplicate check (for updates)
    
    Returns:
        Tuple of (is_duplicate, existing_book_data)
    """
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                # Prepare query based on parameters
                query = "SELECT book_id, title, user_id FROM books WHERE LOWER(title) = LOWER(%s)"
                params = [title.strip()]
                
                if user_id:
                    query += " AND user_id = %s"
                    params.append(user_id)
                
                if exclude_book_id:
                    query += " AND book_id != %s"
                    params.append(exclude_book_id)
                
                cursor.execute(query, params)
                existing_book = cursor.fetchone()
                
                return existing_book is not None, existing_book
    except Exception as e:
        # Log error but don't fail validation on database error
        print(f"Error checking duplicate title: {e}")
        return False, None

def validate_author_name(author: str) -> Tuple[bool, str]:
    """Validate author name"""
    if not author or len(author.strip()) == 0:
        return False, "Author name cannot be empty"
    if len(author) > 100:
        return False, "Author name cannot exceed 100 characters"
    return True, ""

def validate_book_data(title: str, author_name: str, user_id: Optional[str] = None, exclude_book_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Comprehensive book data validation
    
    Returns:
        Dict with validation results
    """
    errors = []
    
    # Validate title
    title_valid, title_error = validate_book_title(title, user_id, exclude_book_id)
    if not title_valid:
        errors.append(f"Title: {title_error}")
    
    # Validate author
    author_valid, author_error = validate_author_name(author_name)
    if not author_valid:
        errors.append(f"Author: {author_error}")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "title_valid": title_valid,
        "author_valid": author_valid
    }

# ID generation
def generate_id() -> str:
    """Generate unique ID"""
    return str(uuid.uuid4())

# Password hashing
def hash_password(password: str) -> str:
    """Hash password using bcrypt (simplified version)"""
    # In production, use: bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password (simplified version)"""
    # In production, use: bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    return hash_password(plain_password) == hashed_password

# File handling
def validate_image_file(file: UploadFile) -> Tuple[bool, str]:
    """Validate uploaded image file"""
    if not file.content_type:
        return False, "File type not specified"
    
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        allowed_types = ", ".join(settings.ALLOWED_IMAGE_TYPES)
        return False, f"Invalid file type. Allowed types: {allowed_types}"
    
    # Check file size
    try:
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset position
        
        if file_size > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File size exceeds maximum limit of {max_size_mb}MB"
    except Exception:
        return False, "Unable to determine file size"
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if file.filename:
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in allowed_extensions:
            return False, f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
    
    return True, ""

def get_image_extension(content_type: str) -> str:
    """Get file extension from content type"""
    extensions = {
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/png': '.png',
        'image/webp': '.webp'
    }
    return extensions.get(content_type, '.jpg')

async def save_book_cover(file: UploadFile, book_title: str) -> str:
    """Save book cover image and return filename"""
    is_valid, error_message = validate_image_file(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {error_message}"
        )
    
    # Clean title for filename
    clean_title = sanitize_filename(book_title)
    
    # Generate unique filename
    extension = get_image_extension(file.content_type)
    filename = f"{clean_title}_{uuid.uuid4().hex[:8]}{extension}"
    filepath = IMAGES_DIR / filename
    
    # Save file
    try:
        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save image: {str(e)}"
        )
    
    return filename

def sanitize_filename(text: str) -> str:
    """Sanitize text to be used as filename"""
    # Remove special characters
    clean_text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces and multiple hyphens with single underscore
    clean_text = re.sub(r'[-\s]+', '_', clean_text)
    # Convert to lowercase and limit length
    clean_text = clean_text.lower()[:100]
    # Remove leading/trailing underscores
    clean_text = clean_text.strip('_')
    # Ensure not empty
    if not clean_text:
        clean_text = "book"
    
    return clean_text

def delete_book_cover(filename: str) -> bool:
    """Delete book cover image"""
    if not filename:
        return False
    
    filepath = IMAGES_DIR / filename
    try:
        if filepath.exists():
            filepath.unlink()
            return True
    except Exception as e:
        print(f"Error deleting file {filename}: {e}")
    return False

# URL generation
def get_cover_url(filename: str) -> str:
    """Generate cover URL"""
    if not filename:
        return ""
    return f"/images/{filename}"

# Streak calculation
def calculate_streak(last_login_date: Optional[datetime], current_streak: int) -> Dict[str, Any]:
    """Calculate user's reading streak"""
    today = datetime.now().date()
    
    if not last_login_date:
        return {
            "current_streak": 1,
            "last_streak": 0,
            "updated": True
        }
    
    last_login = last_login_date.date()
    days_diff = (today - last_login).days
    
    if days_diff == 0:  # Already logged in today
        return {
            "current_streak": current_streak,
            "last_streak": 0,
            "updated": False
        }
    elif days_diff == 1:  # Consecutive day
        return {
            "current_streak": current_streak + 1,
            "last_streak": current_streak,
            "updated": True
        }
    else:  # Streak broken
        return {
            "current_streak": 1,
            "last_streak": current_streak,
            "updated": True
        }

# Database validation helpers
def validate_book_exists(book_id: str) -> Tuple[bool, Optional[Dict]]:
    """Check if book exists in database"""
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("SELECT book_id, title, user_id FROM books WHERE book_id = %s", (book_id,))
                book = cursor.fetchone()
                return book is not None, book
    except Exception as e:
        print(f"Error checking book existence: {e}")
        return False, None

def validate_user_exists(user_id: str) -> bool:
    """Check if user exists in database"""
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()
                return user is not None
    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False

# Rate limiting helper (simplified)
class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, user_id: str, limit: int = 10, window_seconds: int = 60) -> bool:
        """Check if user is allowed to make a request"""
        current_time = datetime.now()
        user_requests = self.requests.get(user_id, [])
        
        # Remove old requests
        user_requests = [req_time for req_time in user_requests 
                        if (current_time - req_time).seconds < window_seconds]
        
        if len(user_requests) >= limit:
            return False
        
        # Add current request
        user_requests.append(current_time)
        self.requests[user_id] = user_requests
        return True

# Create a global rate limiter instance
rate_limiter = RateLimiter()
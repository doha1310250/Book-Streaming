# utils.py
import os
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re
from pathlib import Path
import imghdr
import magic
from fastapi import UploadFile, HTTPException, status

from config import settings

# Validation functions
def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

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

def validate_book_title(title: str) -> bool:
    """Validate book title"""
    if not title or len(title.strip()) == 0:
        return False
    if len(title) > 255:
        return False
    return True

def validate_author_name(author: str) -> bool:
    """Validate author name"""
    if not author or len(author.strip()) == 0:
        return False
    if len(author) > 100:
        return False
    return True

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
def validate_image_file(file: UploadFile) -> bool:
    """Validate uploaded image file"""
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        return False
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset position
    
    if file_size > settings.MAX_FILE_SIZE:
        return False
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        return False
    
    return True

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
    if not validate_image_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file. Only JPG, PNG, and WebP files up to 5MB are allowed."
        )
    
    # Clean title for filename
    clean_title = re.sub(r'[^\w\s-]', '', book_title)
    clean_title = re.sub(r'[-\s]+', '_', clean_title)
    clean_title = clean_title.lower()[:100]  # Limit length
    
    # Generate unique filename
    extension = get_image_extension(file.content_type)
    filename = f"{clean_title}_{uuid.uuid4().hex[:8]}{extension}"
    filepath = settings.IMAGES_DIR / filename
    
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

def delete_book_cover(filename: str) -> bool:
    """Delete book cover image"""
    if not filename:
        return False
    
    filepath = settings.IMAGES_DIR / filename
    try:
        if filepath.exists():
            filepath.unlink()
            return True
    except Exception:
        pass
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
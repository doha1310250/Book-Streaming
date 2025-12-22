# models.py
from pydantic import BaseModel, EmailStr, Field, field_validator, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

from utils import validate_email, validate_password, validate_book_title, validate_author_name

# User Models
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v):
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        result = validate_password(v)
        if not result["is_valid"]:
            raise ValueError(f"Password validation failed: {', '.join(result['errors'])}")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if v is not None:
            result = validate_password(v)
            if not result["is_valid"]:
                raise ValueError(f"Password validation failed: {', '.join(result['errors'])}")
        return v

class UserResponse(UserBase):
    user_id: str
    last_streak: int = 0
    current_streak: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True

# Book Models
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author_name: str = Field(..., min_length=1, max_length=100)
    publish_date: Optional[date] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not validate_book_title(v):
            raise ValueError('Invalid book title')
        return v.strip()
    
    @field_validator('author_name')
    @classmethod
    def validate_author(cls, v):
        if not validate_author_name(v):
            raise ValueError('Invalid author name')
        return v.strip()

class BookCreate(BookBase):
    pass  # No user_id needed since it will come from authenticated user

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author_name: Optional[str] = Field(None, min_length=1, max_length=100)
    publish_date: Optional[date] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None and not validate_book_title(v):
            raise ValueError('Invalid book title')
        return v.strip() if v else v
    
    @field_validator('author_name')
    @classmethod
    def validate_author(cls, v):
        if v is not None and not validate_author_name(v):
            raise ValueError('Invalid author name')
        return v.strip() if v else v

class BookResponse(BookBase):
    book_id: str
    user_id: Optional[str]
    is_verified: bool = False
    cover_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Review Models
class ReviewBase(BaseModel):
    rating: Optional[Decimal] = Field(None, ge=0, le=5)
    review_comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass  # user_id and book_id will come from context

class ReviewUpdate(BaseModel):
    rating: Optional[Decimal] = Field(None, ge=0, le=5)
    review_comment: Optional[str] = None

class ReviewResponse(ReviewBase):
    id: str
    user_id: str
    book_id: str
    user_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Reading Session Models
class ReadingSessionBase(BaseModel):
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_min: Optional[int] = Field(None, ge=0)
    
    @field_validator('end_time')
    @classmethod
    def validate_times(cls, v, info):
        if v and 'start_time' in info.data and v < info.data['start_time']:
            raise ValueError('End time must be after start time')
        return v

class ReadingSessionCreate(ReadingSessionBase):
    pass  # user_id and book_id will come from context

class ReadingSessionResponse(ReadingSessionBase):
    id: str
    user_id: str
    book_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Follower Models
class FollowResponse(BaseModel):
    follower_id: str
    followed_id: str
    followed_at: datetime
    
    class Config:
        from_attributes = True

# Mark Models
class MarkResponse(BaseModel):
    user_id: str
    book_id: str
    marked_at: datetime
    
    class Config:
        from_attributes = True

class MarkedBookResponse(BookResponse):
    marked_at: datetime

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None

# Pagination Models
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    pages: int

# Search Models
class BookSearch(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    verified: Optional[bool] = None
    min_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    date_from: Optional[date] = None
    date_to: Optional[date] = None
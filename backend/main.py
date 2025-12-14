# main.py
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from typing import List, Optional
from datetime import datetime
import os

from config import settings
from database import db, init_database
from models import *
from utils import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Book Streaming API",
    version="1.0.0",
    description="API for book streaming platform with image uploads",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount images directory as static files
app.mount("/images", StaticFiles(directory=settings.IMAGES_DIR), name="images")

# Security
security = HTTPBearer()

# Dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    token = credentials.credentials
    
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (token,))
            user = cursor.fetchone()
            
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()
    logger.info("Application started successfully")

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Check API health"""
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )

# User Routes
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register_user(user: UserCreate):
    """Register a new user"""
    # Check if email already exists
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (user.email,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
    
    # Create new user
    user_id = generate_id()
    hashed_password = hash_password(user.password)
    
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("""
                    INSERT INTO users (user_id, email, name, password)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, user.email, user.name, hashed_password))
                
                cursor.execute("""
                    SELECT user_id, email, name, last_streak, current_streak, created_at
                    FROM users WHERE user_id = %s
                """, (user_id,))
                new_user = cursor.fetchone()
        
        logger.info(f"New user registered: {user.email}")
        return UserResponse(**new_user)
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )

@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login_user(login_data: UserLogin):
    """Login user and return access token"""
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("""
                SELECT user_id, email, name, password, last_streak, current_streak, created_at
                FROM users WHERE email = %s
            """, (login_data.email,))
            user = cursor.fetchone()
    
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update streak
    streak_data = calculate_streak(user.get("last_login"), user["current_streak"])
    if streak_data["updated"]:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET current_streak = %s, last_streak = %s
                    WHERE user_id = %s
                """, (streak_data["current_streak"], streak_data["last_streak"], user["user_id"]))
    
    # Remove password from response
    user.pop("password", None)
    
    # Create token (in production, use JWT)
    token = {
        "access_token": user["user_id"],  # Simplified - use proper JWT in production
        "token_type": "bearer",
        "user": user
    }
    
    logger.info(f"User logged in: {user['email']}")
    return token

@app.get("/users/me", response_model=UserResponse, tags=["Users"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)

# Book Routes
@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["Books"])
async def create_book(
    title: str = Query(..., description="Book title"),
    author_name: str = Query(..., description="Author name"),
    publish_date: Optional[date] = Query(None, description="Publication date"),
    cover_image: Optional[UploadFile] = File(None, description="Book cover image"),
    current_user: dict = Depends(get_current_user)
):
    """Create a new book with optional cover image"""
    # Validate book data
    if not validate_book_title(title):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid book title"
        )
    
    if not validate_author_name(author_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid author name"
        )
    
    # Generate book ID
    book_id = generate_id()
    
    # Handle cover image
    cover_filename = None
    if cover_image:
        cover_filename = await save_book_cover(cover_image, title)
    
    # Create book record
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("""
                    INSERT INTO books (book_id, user_id, title, author_name, publish_date, cover_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (book_id, current_user["user_id"], title.strip(), author_name.strip(), 
                      publish_date, cover_filename))
                
                cursor.execute("""
                    SELECT * FROM books WHERE book_id = %s
                """, (book_id,))
                new_book = cursor.fetchone()
        
        # Convert cover filename to URL
        if new_book["cover_url"]:
            new_book["cover_url"] = get_cover_url(new_book["cover_url"])
        
        logger.info(f"New book created: {title} by {author_name}")
        return BookResponse(**new_book)
    except Exception as e:
        # Clean up uploaded image if book creation fails
        if cover_filename:
            delete_book_cover(cover_filename)
        logger.error(f"Failed to create book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create book"
        )

@app.get("/books", response_model=List[BookResponse], tags=["Books"])
async def get_books(
    title: Optional[str] = Query(None, description="Search by title"),
    author: Optional[str] = Query(None, description="Search by author"),
    verified: Optional[bool] = Query(None, description="Filter by verification status"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get list of books with filtering and pagination"""
    query = "SELECT * FROM books WHERE 1=1"
    params = []
    
    if title:
        query += " AND title LIKE %s"
        params.append(f"%{title}%")
    
    if author:
        query += " AND author_name LIKE %s"
        params.append(f"%{author}%")
    
    if verified is not None:
        query += " AND is_verified = %s"
        params.append(verified)
    
    query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute(query, params)
                books = cursor.fetchall()
        
        # Convert cover filenames to URLs
        for book in books:
            if book["cover_url"]:
                book["cover_url"] = get_cover_url(book["cover_url"])
        
        return [BookResponse(**book) for book in books]
    except Exception as e:
        logger.error(f"Failed to fetch books: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch books"
        )

@app.get("/books/{book_id}", response_model=BookResponse, tags=["Books"])
async def get_book(book_id: str):
    """Get book by ID"""
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("""
                    SELECT * FROM books WHERE book_id = %s
                """, (book_id,))
                book = cursor.fetchone()
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        # Convert cover filename to URL
        if book["cover_url"]:
            book["cover_url"] = get_cover_url(book["cover_url"])
        
        return BookResponse(**book)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch book"
        )

# Mark Routes
@app.post("/books/{book_id}/mark", tags=["Marks"])
async def mark_book(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a book for later reading"""
    # Check if book exists
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("SELECT book_id FROM books WHERE book_id = %s", (book_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
            
            # Check if already marked
            cursor.execute("""
                SELECT * FROM marks 
                WHERE user_id = %s AND book_id = %s
            """, (current_user["user_id"], book_id))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Book already marked"
                )
            
            # Add mark
            cursor.execute("""
                INSERT INTO marks (user_id, book_id)
                VALUES (%s, %s)
            """, (current_user["user_id"], book_id))
    
    logger.info(f"Book marked: {book_id} by user {current_user['user_id']}")
    return {"message": "Book marked successfully"}

@app.delete("/books/{book_id}/mark", tags=["Marks"])
async def unmark_book(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove mark from a book"""
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("""
                DELETE FROM marks 
                WHERE user_id = %s AND book_id = %s
            """, (current_user["user_id"], book_id))
            
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not marked"
                )
    
    logger.info(f"Book unmarked: {book_id} by user {current_user['user_id']}")
    return {"message": "Book unmarked successfully"}

@app.get("/users/me/marks", response_model=List[MarkedBookResponse], tags=["Marks"])
async def get_my_marked_books(
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user)
):
    """Get current user's marked books"""
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("""
                    SELECT b.*, m.marked_at 
                    FROM marks m
                    JOIN books b ON m.book_id = b.book_id
                    WHERE m.user_id = %s
                    ORDER BY m.marked_at DESC
                    LIMIT %s OFFSET %s
                """, (current_user["user_id"], limit, offset))
                marked_books = cursor.fetchall()
        
        # Convert cover filenames to URLs
        for book in marked_books:
            if book["cover_url"]:
                book["cover_url"] = get_cover_url(book["cover_url"])
        
        return [MarkedBookResponse(**book) for book in marked_books]
    except Exception as e:
        logger.error(f"Failed to fetch marked books: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch marked books"
        )

@app.get("/books/{book_id}/is-marked", tags=["Marks"])
async def check_if_book_is_marked(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Check if a book is marked by current user"""
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("""
                SELECT * FROM marks 
                WHERE user_id = %s AND book_id = %s
            """, (current_user["user_id"], book_id))
            is_marked = cursor.fetchone() is not None
    
    return {"is_marked": is_marked}

# Additional routes would go here for reviews, reading sessions, followers, etc.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


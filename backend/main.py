# main.py - Complete with all routes
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import os

from config import settings, IMAGES_DIR
from database import db, init_database
from models import *
from utils import *

# Re-import FastAPI's Path and Query after wildcard imports (utils imports pathlib.Path which overwrites)
from fastapi import Path, Query

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events
    """
    # Startup
    logger.info("Starting Book Streaming API...")
    init_database()
    logger.info("Database initialized successfully")
    logger.info("Application started successfully")
    
    yield  # Application runs during yield
    
    # Shutdown
    logger.info("Shutting down Book Streaming API...")
    # Add any cleanup code here if needed

# Create FastAPI app with lifespan
app = FastAPI(
    title="Book Streaming API",
    version="1.0.0",
    description="API for book streaming platform with image uploads",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# Mount frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend")

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

# ============================================
# FRONTEND ROUTES
# ============================================

@app.get("/", tags=["Frontend"], include_in_schema=False)
@app.get("/index.html", tags=["Frontend"], include_in_schema=False)
async def serve_frontend():
    """Serve the frontend index.html"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to Book Streaming API", "docs": "/docs"}

@app.get("/dashboard", tags=["Frontend"], include_in_schema=False)
@app.get("/dashboard.html", tags=["Frontend"], include_in_schema=False)
async def serve_dashboard():
    """Serve the dashboard page"""
    dashboard_path = os.path.join(FRONTEND_DIR, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"message": "Dashboard not found"}

@app.get("/login", tags=["Frontend"], include_in_schema=False)
@app.get("/login.html", tags=["Frontend"], include_in_schema=False)
async def serve_login():
    """Serve the login page"""
    login_path = os.path.join(FRONTEND_DIR, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return {"message": "Login page not found"}

@app.get("/timer", tags=["Frontend"], include_in_schema=False)
@app.get("/timer.html", tags=["Frontend"], include_in_schema=False)
async def serve_timer():
    """Serve the timer page"""
    timer_path = os.path.join(FRONTEND_DIR, "timer.html")
    if os.path.exists(timer_path):
        return FileResponse(timer_path)
    return {"message": "Timer page not found"}

@app.get("/profile", tags=["Frontend"], include_in_schema=False)
@app.get("/profile.html", tags=["Frontend"], include_in_schema=False)
async def serve_profile():
    """Serve the profile page"""
    profile_path = os.path.join(FRONTEND_DIR, "profile.html")
    if os.path.exists(profile_path):
        return FileResponse(profile_path)
    return {"message": "Profile page not found"}

@app.get("/social", tags=["Frontend"], include_in_schema=False)
@app.get("/social.html", tags=["Frontend"], include_in_schema=False)
async def serve_social():
    """Serve the social page"""
    social_path = os.path.join(FRONTEND_DIR, "social.html")
    if os.path.exists(social_path):
        return FileResponse(social_path)
    return {"message": "Social page not found"}

# Serve CSS and JS files
@app.get("/{filename}.css", tags=["Frontend"], include_in_schema=False)
async def serve_css(filename: str):
    """Serve CSS files"""
    css_path = os.path.join(FRONTEND_DIR, f"{filename}.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS file not found")

@app.get("/{filename}.js", tags=["Frontend"], include_in_schema=False)
async def serve_js(filename: str):
    """Serve JS files"""
    js_path = os.path.join(FRONTEND_DIR, f"{filename}.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JS file not found")


# ============================================
# HEALTH CHECK
# ============================================

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
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )

# ============================================
# AUTHENTICATION ROUTES
# ============================================

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
    
    # Create token
    token = {
        "access_token": user["user_id"],
        "token_type": "bearer",
        "user": user
    }
    
    logger.info(f"User logged in: {user['email']}")
    return token

# ============================================
# USER ROUTES
# ============================================

@app.get("/users/me", response_model=UserResponse, tags=["Users"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)

@app.put("/users/me", response_model=UserResponse, tags=["Users"])
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user information"""
    update_fields = []
    update_values = []
    
    if user_update.name is not None:
        update_fields.append("name = %s")
        update_values.append(user_update.name)
    
    if user_update.password is not None:
        hashed_password = hash_password(user_update.password)
        update_fields.append("password = %s")
        update_values.append(hashed_password)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_values.append(current_user["user_id"])
    
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                update_query = f"""
                    UPDATE users 
                    SET {', '.join(update_fields)}
                    WHERE user_id = %s
                """
                cursor.execute(update_query, update_values)
                
                cursor.execute("""
                    SELECT user_id, email, name, last_streak, current_streak, created_at
                    FROM users WHERE user_id = %s
                """, (current_user["user_id"],))
                updated_user = cursor.fetchone()
        
        logger.info(f"User updated: {current_user['user_id']}")
        return UserResponse(**updated_user)
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

# ============================================
# BOOK ROUTES
# ============================================

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["Books"])
async def create_book(
    title: str = Query(..., description="Book title"),
    author_name: str = Query(..., description="Author name"),
    publish_date: Optional[date] = Query(None, description="Publication date"),
    cover_image: Optional[UploadFile] = File(None, description="Book cover image"),
    current_user: dict = Depends(get_current_user)
):
    """Create a new book with optional cover image"""
    # Validate book data with duplicate check
    validation_result = validate_book_data(
        title=title,
        author_name=author_name,
        user_id=current_user["user_id"]
    )
    
    if not validation_result["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=", ".join(validation_result["errors"])
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
async def get_book(book_id: str = Path(..., description="Book ID")):
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

@app.put("/books/{book_id}", response_model=BookResponse, tags=["Books"])
async def update_book(
    book_id: str = Path(..., description="Book ID"),
    book_update: BookUpdate = None,
    cover_image: Optional[UploadFile] = File(None, description="New cover image"),
    current_user: dict = Depends(get_current_user)
):
    """Update a book"""
    # Check if book exists and belongs to user
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("""
                SELECT * FROM books WHERE book_id = %s AND user_id = %s
            """, (book_id, current_user["user_id"]))
            book = cursor.fetchone()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found or you don't have permission to update it"
        )
    
    # Validate updates if provided
    update_fields = []
    update_values = []
    
    if book_update and book_update.title is not None:
        # Check for duplicate title (excluding current book)
        is_valid, error = validate_book_title(
            book_update.title, 
            user_id=current_user["user_id"], 
            exclude_book_id=book_id
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        update_fields.append("title = %s")
        update_values.append(book_update.title.strip())
    
    if book_update and book_update.author_name is not None:
        is_valid, error = validate_author_name(book_update.author_name)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        update_fields.append("author_name = %s")
        update_values.append(book_update.author_name.strip())
    
    if book_update and book_update.publish_date is not None:
        update_fields.append("publish_date = %s")
        update_values.append(book_update.publish_date)
    
    # Handle cover image update
    old_cover_filename = book["cover_url"]
    if cover_image:
        new_cover_filename = await save_book_cover(cover_image, 
                                                  book_update.title if book_update and book_update.title else book["title"])
        update_fields.append("cover_url = %s")
        update_values.append(new_cover_filename)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_values.append(book_id)
    
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                update_query = f"""
                    UPDATE books 
                    SET {', '.join(update_fields)}
                    WHERE book_id = %s
                """
                cursor.execute(update_query, update_values)
                
                # Delete old cover image if new one was uploaded
                if cover_image and old_cover_filename:
                    delete_book_cover(old_cover_filename)
                
                cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
                updated_book = cursor.fetchone()
        
        # Convert cover filename to URL
        if updated_book["cover_url"]:
            updated_book["cover_url"] = get_cover_url(updated_book["cover_url"])
        
        logger.info(f"Book updated: {book_id}")
        return BookResponse(**updated_book)
    except Exception as e:
        logger.error(f"Failed to update book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update book"
        )

@app.delete("/books/{book_id}", tags=["Books"])
async def delete_book(
    book_id: str = Path(..., description="Book ID"),
    current_user: dict = Depends(get_current_user)
):
    """Delete a book"""
    # Check if book exists and belongs to user
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("""
                SELECT cover_url FROM books WHERE book_id = %s AND user_id = %s
            """, (book_id, current_user["user_id"]))
            book = cursor.fetchone()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found or you don't have permission to delete it"
        )
    
    try:
        # Delete book cover image if exists
        if book["cover_url"]:
            delete_book_cover(book["cover_url"])
        
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        
        logger.info(f"Book deleted: {book_id}")
        return {"message": "Book deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete book"
        )

# ============================================
# MARK/BOOKMARK ROUTES
# ============================================

@app.post("/books/{book_id}/mark", tags=["Marks"])
async def mark_book(
    book_id: str = Path(..., description="Book ID"),
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
    book_id: str = Path(..., description="Book ID"),
    current_user: dict = Depends(get_current_user)
):
    """Unmark a book"""
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

@app.delete("/books/{book_id}/mark", tags=["Marks"])
async def unmark_book(
    book_id: str = Path(..., description="Book ID"),
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
    book_id: str = Path(..., description="Book ID"),
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

# ============================================
# REVIEW ROUTES
# ============================================

@app.post("/books/{book_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED, tags=["Reviews"])
async def create_review(
    book_id: str = Path(..., description="Book ID"),
    review_data: ReviewCreate = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a review for a book"""
    # Check if book exists
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("SELECT book_id FROM books WHERE book_id = %s", (book_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
            
            # Check if user already reviewed this book
            cursor.execute("""
                SELECT id FROM reviews 
                WHERE user_id = %s AND book_id = %s
            """, (current_user["user_id"], book_id))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already reviewed this book"
                )
    
    # Validate rating
    if review_data.rating is not None and (review_data.rating < 0 or review_data.rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 0 and 5"
        )
    
    # Create review
    review_id = generate_id()
    
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("""
                    INSERT INTO reviews (id, user_id, book_id, rating, review_comment)
                    VALUES (%s, %s, %s, %s, %s)
                """, (review_id, current_user["user_id"], book_id, 
                      review_data.rating, review_data.review_comment))
                
                cursor.execute("""
                    SELECT * FROM reviews WHERE id = %s
                """, (review_id,))
                new_review = cursor.fetchone()
        
        logger.info(f"Review created: {review_id} for book {book_id}")
        return ReviewResponse(**new_review)
    except Exception as e:
        logger.error(f"Failed to create review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review"
        )

@app.get("/books/{book_id}/reviews", response_model=List[ReviewResponse], tags=["Reviews"])
async def get_book_reviews(
    book_id: str = Path(..., description="Book ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    sort_by: str = Query("created_at", description="Sort by: created_at, rating, updated_at"),
    order: str = Query("desc", description="Order: asc or desc")
):
    """Get reviews for a book"""
    # Validate sort parameters
    valid_sort_fields = ["created_at", "rating", "updated_at"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort field. Valid options: {', '.join(valid_sort_fields)}"
        )
    
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be 'asc' or 'desc'"
        )
    
    # Check if book exists
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("SELECT book_id FROM books WHERE book_id = %s", (book_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
            
            # Get reviews
            cursor.execute(f"""
                SELECT r.*, u.name as user_name 
                FROM reviews r
                JOIN users u ON r.user_id = u.user_id
                WHERE r.book_id = %s
                ORDER BY r.{sort_by} {order.upper()}
                LIMIT %s OFFSET %s
            """, (book_id, limit, offset))
            reviews = cursor.fetchall()
            
            # Get total count
            cursor.execute("""
                SELECT COUNT(*) as total FROM reviews WHERE book_id = %s
            """, (book_id,))
            total_result = cursor.fetchone()
            total = total_result["total"] if total_result else 0
    
    return JSONResponse({
        "items": [ReviewResponse(**review).model_dump(mode='json') for review in reviews],
        "total": total,
        "page": offset // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    })

@app.get("/users/me/reviews", response_model=List[ReviewResponse], tags=["Reviews"])
async def get_my_reviews(
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user)
):
    """Get current user's reviews"""
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("""
                    SELECT r.*, b.title as book_title 
                    FROM reviews r
                    JOIN books b ON r.book_id = b.book_id
                    WHERE r.user_id = %s
                    ORDER BY r.created_at DESC
                    LIMIT %s OFFSET %s
                """, (current_user["user_id"], limit, offset))
                reviews = cursor.fetchall()
        
        return [ReviewResponse(**review) for review in reviews]
    except Exception as e:
        logger.error(f"Failed to fetch user reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reviews"
        )

@app.put("/reviews/{review_id}", response_model=ReviewResponse, tags=["Reviews"])
async def update_review(
    review_id: str = Path(..., description="Review ID"),
    review_update: ReviewUpdate = None,
    current_user: dict = Depends(get_current_user)
):
    """Update a review"""
    # Check if review exists and belongs to user
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("""
                SELECT * FROM reviews WHERE id = %s AND user_id = %s
            """, (review_id, current_user["user_id"]))
            review = cursor.fetchone()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or you don't have permission to update it"
        )
    
    # Validate rating
    if review_update and review_update.rating is not None and (review_update.rating < 0 or review_update.rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 0 and 5"
        )
    
    update_fields = []
    update_values = []
    
    if review_update and review_update.rating is not None:
        update_fields.append("rating = %s")
        update_values.append(review_update.rating)
    
    if review_update and review_update.review_comment is not None:
        update_fields.append("review_comment = %s")
        update_values.append(review_update.review_comment)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_values.append(review_id)
    
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                update_query = f"""
                    UPDATE reviews 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """
                cursor.execute(update_query, update_values)
                
                cursor.execute("SELECT * FROM reviews WHERE id = %s", (review_id,))
                updated_review = cursor.fetchone()
        
        logger.info(f"Review updated: {review_id}")
        return ReviewResponse(**updated_review)
    except Exception as e:
        logger.error(f"Failed to update review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update review"
        )

@app.delete("/reviews/{review_id}", tags=["Reviews"])
async def delete_review(
    review_id: str = Path(..., description="Review ID"),
    current_user: dict = Depends(get_current_user)
):
    """Delete a review"""
    # Check if review exists and belongs to user
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("""
                SELECT id FROM reviews WHERE id = %s AND user_id = %s
            """, (review_id, current_user["user_id"]))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Review not found or you don't have permission to delete it"
                )
            
            cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
    
    logger.info(f"Review deleted: {review_id}")
    return {"message": "Review deleted successfully"}

@app.get("/books/{book_id}/reviews/summary", tags=["Reviews"])
async def get_book_reviews_summary(book_id: str = Path(..., description="Book ID")):
    """Get summary statistics for book reviews"""
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            # Get review statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_reviews,
                    AVG(rating) as average_rating,
                    MIN(rating) as min_rating,
                    MAX(rating) as max_rating,
                    SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) as positive_reviews,
                    SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) as negative_reviews
                FROM reviews 
                WHERE book_id = %s AND rating IS NOT NULL
            """, (book_id,))
            stats = cursor.fetchone()
            
            # Get rating distribution
            cursor.execute("""
                SELECT 
                    rating,
                    COUNT(*) as count
                FROM reviews 
                WHERE book_id = %s AND rating IS NOT NULL
                GROUP BY rating
                ORDER BY rating DESC
            """, (book_id,))
            distribution = cursor.fetchall()
    
    if not stats or stats["total_reviews"] == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews found for this book"
        )
    
    return {
        "total_reviews": stats["total_reviews"],
        "average_rating": float(stats["average_rating"]) if stats["average_rating"] else 0,
        "min_rating": float(stats["min_rating"]) if stats["min_rating"] else 0,
        "max_rating": float(stats["max_rating"]) if stats["max_rating"] else 0,
        "positive_reviews": stats["positive_reviews"],
        "negative_reviews": stats["negative_reviews"],
        "distribution": {str(item["rating"]): item["count"] for item in distribution}
    }

# ============================================
# READING SESSION ROUTES
# ============================================

@app.post("/books/{book_id}/reading-sessions", response_model=ReadingSessionResponse, status_code=status.HTTP_201_CREATED, tags=["Reading Sessions"])
async def create_reading_session(
    book_id: str = Path(..., description="Book ID"),
    session_data: ReadingSessionCreate = None,
    current_user: dict = Depends(get_current_user)
):
    """Start a new reading session"""
    # Check if book exists
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("SELECT book_id FROM books WHERE book_id = %s", (book_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
    
    # Validate session data
    if session_data.end_time and session_data.end_time < session_data.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Calculate duration if end_time is provided
    duration_min = None
    if session_data.end_time:
        duration = session_data.end_time - session_data.start_time
        duration_min = int(duration.total_seconds() / 60)
    
    # Create reading session
    session_id = generate_id()
    
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("""
                    INSERT INTO reading_sessions (id, user_id, book_id, start_time, end_time, duration_min)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (session_id, current_user["user_id"], book_id, 
                      session_data.start_time, session_data.end_time, duration_min))
                
                cursor.execute("SELECT * FROM reading_sessions WHERE id = %s", (session_id,))
                new_session = cursor.fetchone()
        
        logger.info(f"Reading session created: {session_id} for book {book_id}")
        return ReadingSessionResponse(**new_session)
    except Exception as e:
        logger.error(f"Failed to create reading session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reading session"
        )

@app.put("/reading-sessions/{session_id}", response_model=ReadingSessionResponse, tags=["Reading Sessions"])
async def update_reading_session(
    session_id: str = Path(..., description="Session ID"),
    end_time: datetime = Query(..., description="End time for the session"),
    current_user: dict = Depends(get_current_user)
):
    """End a reading session"""
    # Check if session exists and belongs to user
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("""
                SELECT * FROM reading_sessions 
                WHERE id = %s AND user_id = %s
            """, (session_id, current_user["user_id"]))
            session = cursor.fetchone()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading session not found or you don't have permission to update it"
        )
    
    # Check if session already ended
    if session["end_time"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reading session already ended"
        )
    
    # Calculate duration - handle timezone-aware/naive datetime comparison
    try:
        start_time = session["start_time"]
        # Make both datetimes naive for comparison
        if hasattr(end_time, 'tzinfo') and end_time.tzinfo is not None:
            end_time = end_time.replace(tzinfo=None)
        if hasattr(start_time, 'tzinfo') and start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)
        
        duration = end_time - start_time
        duration_min = max(0, int(duration.total_seconds() / 60))
    except Exception as e:
        logger.warning(f"Duration calculation error: {e}, defaulting to 0")
        duration_min = 0
    
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("""
                    UPDATE reading_sessions 
                    SET end_time = %s, duration_min = %s
                    WHERE id = %s
                """, (end_time, duration_min, session_id))
                
                cursor.execute("SELECT * FROM reading_sessions WHERE id = %s", (session_id,))
                updated_session = cursor.fetchone()
        
        logger.info(f"Reading session ended: {session_id}")
        return ReadingSessionResponse(**updated_session)
    except Exception as e:
        logger.error(f"Failed to update reading session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update reading session"
        )

@app.get("/users/me/reading-sessions", response_model=List[ReadingSessionResponse], tags=["Reading Sessions"])
async def get_my_reading_sessions(
    book_id: Optional[str] = Query(None, description="Filter by book ID"),
    date_from: Optional[date] = Query(None, description="Filter by start date"),
    date_to: Optional[date] = Query(None, description="Filter by end date"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user)
):
    """Get current user's reading sessions"""
    try:
        query = """
            SELECT rs.*, b.title as book_title 
            FROM reading_sessions rs
            JOIN books b ON rs.book_id = b.book_id
            WHERE rs.user_id = %s
        """
        params = [current_user["user_id"]]
        
        if book_id:
            query += " AND rs.book_id = %s"
            params.append(book_id)
        
        if date_from:
            query += " AND DATE(rs.start_time) >= %s"
            params.append(date_from)
        
        if date_to:
            query += " AND DATE(rs.start_time) <= %s"
            params.append(date_to)
        
        query += " ORDER BY rs.start_time DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute(query, params)
                sessions = cursor.fetchall()
        
        return [ReadingSessionResponse(**session) for session in sessions]
    except Exception as e:
        logger.error(f"Failed to fetch reading sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reading sessions"
        )

@app.get("/books/{book_id}/reading-sessions", tags=["Reading Sessions"])
async def get_book_reading_sessions(
    book_id: str = Path(..., description="Book ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get reading session statistics for a book"""
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            # Get total reading time for this book by current user
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(duration_min) as total_minutes,
                    AVG(duration_min) as average_minutes,
                    MIN(start_time) as first_read,
                    MAX(start_time) as last_read
                FROM reading_sessions 
                WHERE user_id = %s AND book_id = %s AND duration_min IS NOT NULL
            """, (current_user["user_id"], book_id))
            stats = cursor.fetchone()
            
            # Get recent sessions
            cursor.execute("""
                SELECT * FROM reading_sessions 
                WHERE user_id = %s AND book_id = %s
                ORDER BY start_time DESC
                LIMIT 10
            """, (current_user["user_id"], book_id))
            recent_sessions = cursor.fetchall()
    
    return {
        "total_sessions": stats["total_sessions"] or 0,
        "total_minutes": stats["total_minutes"] or 0,
        "average_minutes": float(stats["average_minutes"]) if stats["average_minutes"] else 0,
        "first_read": stats["first_read"],
        "last_read": stats["last_read"],
        "recent_sessions": [ReadingSessionResponse(**session) for session in recent_sessions]
    }

@app.get("/users/me/reading-stats", tags=["Reading Sessions"])
async def get_my_reading_stats(
    period: str = Query("week", description="Period: day, week, month, year"),
    current_user: dict = Depends(get_current_user)
):
    """Get reading statistics for current user"""
    # Calculate date range
    today = datetime.now().date()
    
    if period == "day":
        start_date = today
    elif period == "week":
        start_date = today - timedelta(days=today.weekday())
    elif period == "month":
        start_date = today.replace(day=1)
    elif period == "year":
        start_date = today.replace(month=1, day=1)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid period. Use: day, week, month, year"
        )
    
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                # Get total reading time
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_sessions,
                        SUM(duration_min) as total_minutes,
                        COUNT(DISTINCT book_id) as unique_books
                    FROM reading_sessions 
                    WHERE user_id = %s AND DATE(start_time) >= %s AND duration_min IS NOT NULL
                """, (current_user["user_id"], start_date))
                stats = cursor.fetchone()
                
                # Get daily reading for the period
                cursor.execute("""
                    SELECT 
                        DATE(start_time) as reading_date,
                        SUM(duration_min) as daily_minutes,
                        COUNT(*) as daily_sessions
                    FROM reading_sessions 
                    WHERE user_id = %s AND DATE(start_time) >= %s AND duration_min IS NOT NULL
                    GROUP BY DATE(start_time)
                    ORDER BY reading_date
                """, (current_user["user_id"], start_date))
                daily_stats = cursor.fetchall()
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "total_sessions": stats["total_sessions"] or 0,
            "total_minutes": stats["total_minutes"] or 0,
            "unique_books": stats["unique_books"] or 0,
            "daily_stats": daily_stats
        }
    except Exception as e:
        logger.error(f"Failed to fetch reading stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reading statistics"
        )

# ============================================
# FOLLOWER ROUTES
# ============================================

@app.post("/users/{user_id}/follow", tags=["Followers"])
async def follow_user(
    user_id: str = Path(..., description="User ID to follow"),
    current_user: dict = Depends(get_current_user)
):
    """Follow another user"""
    # Check if user exists
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Prevent self-follow
            if user_id == current_user["user_id"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot follow yourself"
                )
            
            # Check if already following
            cursor.execute("""
                SELECT * FROM followers 
                WHERE follower_id = %s AND followed_id = %s
            """, (current_user["user_id"], user_id))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Already following this user"
                )
            
            # Create follow relationship
            cursor.execute("""
                INSERT INTO followers (follower_id, followed_id)
                VALUES (%s, %s)
            """, (current_user["user_id"], user_id))
    
    logger.info(f"User {current_user['user_id']} started following {user_id}")
    return {"message": f"Now following user {user_id}"}

@app.delete("/users/{user_id}/follow", tags=["Followers"])
async def unfollow_user(
    user_id: str = Path(..., description="User ID to unfollow"),
    current_user: dict = Depends(get_current_user)
):
    """Unfollow a user"""
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("""
                DELETE FROM followers 
                WHERE follower_id = %s AND followed_id = %s
            """, (current_user["user_id"], user_id))
            
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Not following this user"
                )
    
    logger.info(f"User {current_user['user_id']} unfollowed {user_id}")
    return {"message": f"Unfollowed user {user_id}"}

@app.get("/users/me/following", tags=["Followers"])
async def get_users_i_follow(
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user)
):
    """Get users that current user is following"""
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("""
                    SELECT u.user_id, u.name, u.email, f.followed_at 
                    FROM followers f
                    JOIN users u ON f.followed_id = u.user_id
                    WHERE f.follower_id = %s
                    ORDER BY f.followed_at DESC
                    LIMIT %s OFFSET %s
                """, (current_user["user_id"], limit, offset))
                following = cursor.fetchall()
                
                # Get total count
                cursor.execute("""
                    SELECT COUNT(*) as total FROM followers WHERE follower_id = %s
                """, (current_user["user_id"],))
                total_result = cursor.fetchone()
                total = total_result["total"] if total_result else 0
        
        # Convert datetime to string for JSON serialization
        for user in following:
            if user.get("followed_at"):
                user["followed_at"] = user["followed_at"].isoformat()
        
        return {
            "following": following,
            "total": total,
            "page": offset // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except Exception as e:
        logger.error(f"Failed to fetch following list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch following list"
        )

@app.get("/users/me/followers", tags=["Followers"])
async def get_my_followers(
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user)
):
    """Get users who are following current user"""
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                cursor.execute("""
                    SELECT u.user_id, u.name, u.email, f.followed_at 
                    FROM followers f
                    JOIN users u ON f.follower_id = u.user_id
                    WHERE f.followed_id = %s
                    ORDER BY f.followed_at DESC
                    LIMIT %s OFFSET %s
                """, (current_user["user_id"], limit, offset))
                followers = cursor.fetchall()
                
                # Get total count
                cursor.execute("""
                    SELECT COUNT(*) as total FROM followers WHERE followed_id = %s
                """, (current_user["user_id"],))
                total_result = cursor.fetchone()
                total = total_result["total"] if total_result else 0
        
        # Convert datetime to string for JSON serialization
        for user in followers:
            if user.get("followed_at"):
                user["followed_at"] = user["followed_at"].isoformat()
        
        return {
            "followers": followers,
            "total": total,
            "page": offset // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except Exception as e:
        logger.error(f"Failed to fetch followers list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch followers list"
        )

@app.get("/users/{user_id}/follow-status", tags=["Followers"])
async def get_follow_status(
    user_id: str = Path(..., description="User ID to check"),
    current_user: dict = Depends(get_current_user)
):
    """Check follow relationship status between current user and another user"""
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            # Check if current user is following target user
            cursor.execute("""
                SELECT * FROM followers 
                WHERE follower_id = %s AND followed_id = %s
            """, (current_user["user_id"], user_id))
            is_following = cursor.fetchone() is not None
            
            # Check if target user is following current user
            cursor.execute("""
                SELECT * FROM followers 
                WHERE follower_id = %s AND followed_id = %s
            """, (user_id, current_user["user_id"]))
            is_followed_by = cursor.fetchone() is not None
    
    return {
        "is_following": is_following,
        "is_followed_by": is_followed_by,
        "relationship": "mutual" if is_following and is_followed_by else 
                       "following" if is_following else 
                       "followed_by" if is_followed_by else 
                       "none"
    }

@app.get("/users/me/following/activity", tags=["Followers"])
async def get_following_activity(
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user)
):
    """Get recent activity from users you follow"""
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                # Get books added by followed users
                cursor.execute("""
                    SELECT 
                        b.*,
                        u.name as user_name,
                        'book_added' as activity_type,
                        b.created_at as activity_time,
                        NULL as duration_min,
                        NULL as session_id
                    FROM books b
                    JOIN users u ON b.user_id = u.user_id
                    WHERE b.user_id IN (
                        SELECT followed_id FROM followers 
                        WHERE follower_id = %s
                    )
                    UNION ALL
                    -- Get reviews by followed users
                    SELECT 
                        b.*,
                        u.name as user_name,
                        'review_added' as activity_type,
                        r.created_at as activity_time,
                        NULL as duration_min,
                        NULL as session_id
                    FROM reviews r
                    JOIN books b ON r.book_id = b.book_id
                    JOIN users u ON r.user_id = u.user_id
                    WHERE r.user_id IN (
                        SELECT followed_id FROM followers 
                        WHERE follower_id = %s
                    )
                    UNION ALL
                    -- Get reading sessions by followed users
                    SELECT 
                        b.*,
                        u.name as user_name,
                        'reading_session' as activity_type,
                        rs.start_time as activity_time,
                        rs.duration_min,
                        rs.id as session_id
                    FROM reading_sessions rs
                    JOIN books b ON rs.book_id = b.book_id
                    JOIN users u ON rs.user_id = u.user_id
                    WHERE rs.user_id IN (
                        SELECT followed_id FROM followers 
                        WHERE follower_id = %s
                    )
                    ORDER BY activity_time DESC
                    LIMIT %s OFFSET %s
                """, (current_user["user_id"], current_user["user_id"], current_user["user_id"], limit, offset))
                activities = cursor.fetchall()
        
        # Convert cover filenames to URLs
        for activity in activities:
            if activity["cover_url"]:
                activity["cover_url"] = get_cover_url(activity["cover_url"])
        
        return activities
    except Exception as e:
        logger.error(f"Failed to fetch following activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch following activity"
        )

# ============================================
# ADMIN ROUTES (Optional - for book verification)
# ============================================

@app.patch("/admin/books/{book_id}/verify", tags=["Admin"])
async def verify_book(
    book_id: str = Path(..., description="Book ID"),
    verify: bool = Query(..., description="Verify or unverify the book"),
    # In production, add admin authentication here
    # admin_user: dict = Depends(get_admin_user)
):
    """Verify or unverify a book (Admin only)"""
    # Check if book exists
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            cursor.execute("SELECT book_id FROM books WHERE book_id = %s", (book_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
            
            cursor.execute("""
                UPDATE books 
                SET is_verified = %s
                WHERE book_id = %s
            """, (verify, book_id))
    
    action = "verified" if verify else "unverified"
    logger.info(f"Book {book_id} {action}")
    return {"message": f"Book {action} successfully"}

# ============================================
# MAIN APPLICATION ENTRY
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
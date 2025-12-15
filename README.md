# 📚 Book Streaming API

A RESTful API backend for a book streaming platform built with FastAPI and MySQL.

## Features

- **User Authentication** - Registration, login with streak tracking
- **Book Management** - CRUD operations with cover image uploads
- **Reviews & Ratings** - Rate and review books (0-5 scale)
- **Bookmarks** - Mark books for later reading
- **Reading Sessions** - Track reading activity
- **Social Features** - Follow other users

## Tech Stack

- **Framework:** FastAPI
- **Database:** MySQL
- **Validation:** Pydantic v2
- **Image Storage:** Local filesystem

## Quick Start

### Prerequisites

- Python 3.10+
- MySQL Server

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd Book-Streaming/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\Activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn mysql-connector-python pydantic pydantic-settings python-multipart
   ```

4. **Create MySQL database:**
   ```sql
   CREATE DATABASE `book-streaming`;
   ```

5. **Configure environment (optional):**
   
   Create a `.env` file in `backend/`:
   ```env
   DATABASE_HOST=127.0.0.1
   DATABASE_PORT=3306
   DATABASE_USER=root
   DATABASE_PASSWORD=your_password
   DATABASE_NAME=book-streaming
   ```

6. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once running, access the interactive docs at:

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/docs | Swagger UI |
| http://127.0.0.1:8000/redoc | ReDoc |
| http://127.0.0.1:8000/health | Health Check |

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Users
- `GET /users/me` - Get current user
- `PUT /users/me` - Update current user

### Books
- `GET /books` - List books (with filters)
- `POST /books` - Create book
- `GET /books/{id}` - Get book details
- `PUT /books/{id}` - Update book
- `DELETE /books/{id}` - Delete book

### Marks (Bookmarks)
- `POST /books/{id}/mark` - Mark book
- `DELETE /books/{id}/mark` - Unmark book
- `GET /users/me/marks` - Get marked books

### Reviews
- `GET /books/{id}/reviews` - Get book reviews
- `POST /books/{id}/reviews` - Create review
- `PUT /reviews/{id}` - Update review
- `DELETE /reviews/{id}` - Delete review

## Project Structure

```
backend/
├── main.py       # FastAPI app and routes
├── models.py     # Pydantic models
├── database.py   # MySQL connection
├── config.py     # App configuration
├── utils.py      # Utility functions
└── images/       # Uploaded covers
```

## License

MIT

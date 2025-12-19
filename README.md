# 📚 Book Streaming Platform

A full-stack book streaming platform featuring a **FastAPI** backend and a **Vanilla JS** frontend.

## ✨ Features

### Frontend (UI/UX)
- **Modern Dashboard** - Clean, responsive interface with skeleton loading states
- **Dark Mode** - Fully supported system-wide dark theme
- **Reading Streak Calendar** - GitHub-style heatmap of your reading activity
- **Book Management** - Add your own books (marked as unverified/community)
- **Immersive Reading** - Distraction-free reading timer and tracker
- **Social Hub** - Discover users, follow friends, and see their activity

### Backend (API)
- **User Authentication** - Registration, login with JWT tokens
- **Book CRUD** - Management with cover image uploads
- **Reviews & Ratings** - Rate and review books (0-5 scale)
- **Bookmarks** - Mark books for later reading
- **Reading Sessions** - Track reading duration and progress logic
- **Social Graph** - Follow/Unfollow system

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | FastAPI (Python 3.10+) |
| Database | MySQL 8.0 |
| Validation | Pydantic v2 |
| Testing | pytest + httpx |
| Containerization | Docker |

---

## 🚀 Quick Start
 
 ### Option 1: Docker (Full Stack)
 
 Start the entire platform (Frontend + Backend + DB) with one command:
 
 ```bash
 # Start the stack
 docker-compose up -d
 
 # View logs
 docker-compose logs -f
 ```
 
 - **Frontend:** http://localhost:3000 (Open this!)
 - **Backend API:** http://localhost:8000
 
 > **Note:** First startup takes 1-2 minutes while MySQL initializes.
 
 ---
 
 ### Option 2: Manual Setup
 
 #### Prerequisites
 - **Python 3.10+**
 - **MySQL 8.0+** running locally
 - **Web Browser** (Chrome/Firefox/Edge)
 
 #### Step 1: Backend Setup
 
 ```bash
 cd backend
 
 # Create & Activate venv
 python -m venv venv
 .\venv\Scripts\Activate  # Windows
 # source venv/bin/activate  # Linux/Mac
 
 # Install dependencies
 pip install -r requirements.txt
 ```
 
 #### Step 2: Configure Database
 
 1. Create MySQL database: `CREATE DATABASE book-streaming;`
 2. Copy `.env.example` to `.env`
 3. Update `.env` with your DB credentials.
 
 #### Step 3: Run the API
 
 ```bash
 # From backend directory
 uvicorn main:app --reload
 ```
 
 **API is running at:** http://127.0.0.1:8000
 
 #### Step 4: Run the Frontend
 
 You can simply open `frontend/index.html` in your browser.
 
 For a better experience (to avoid CORS issues with some local file restrictions), use a simple HTTP server:
 
 ```bash
 # From project root
 cd frontend
 python -m http.server 5500
 ```
 
 **Open:** http://localhost:5500

---

## 📖 API Documentation

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | **Swagger UI** - Interactive API docs |
| http://localhost:8000/redoc | **ReDoc** - Alternative documentation |
| http://localhost:8000/health | **Health Check** - Service status |

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register new user |
| `POST` | `/auth/login` | Login and get token |
| `GET` | `/users/me` | Get current user profile |
| `GET` | `/books` | List/search books |
| `POST` | `/books` | Create a book |
| `GET` | `/books/{id}` | Get book details |
| `POST` | `/books/{id}/mark` | Bookmark a book |
| `POST` | `/books/{id}/reviews` | Add a review |

---

## 🧪 Testing

The project includes comprehensive tests organized by type:

```
backend/tests/
├── conftest.py          # Shared fixtures
├── unit/                # Fast, isolated tests
│   ├── test_utils.py    # Utility function tests
│   └── test_models.py   # Pydantic model tests
├── integration/         # API endpoint tests
│   ├── test_auth.py     # Authentication tests
│   └── test_books.py    # Book CRUD tests
└── e2e/                 # Full user journey tests
    └── test_user_journey.py
```

### Running Tests

```bash
cd backend

# Install test dependencies (if not already)
pip install pytest pytest-asyncio httpx pytest-cov

# Run all tests
pytest -v

# Run only unit tests (fast)
pytest tests/unit -v

# Run only integration tests
pytest tests/integration -v

# Run only E2E tests
pytest tests/e2e -v

# Run with coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Test Markers

```bash
# Run tests by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e           # End-to-end tests only
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'config'"

**Problem:** Running uvicorn from wrong directory.

**Solution:** Run from the `backend/` folder:
```bash
cd backend
uvicorn main:app --reload
```

#### 2. "expected str, bytes or os.PathLike object, not ellipsis"

**Problem:** Import conflict between `fastapi.Path` and `pathlib.Path`.

**Solution:** This is already fixed in the codebase. If you see this error, make sure you have the latest code with the fix in `main.py` line 19-20 that re-imports FastAPI's Path.

#### 3. "Can't connect to MySQL server"

**Problem:** MySQL not running or wrong credentials.

**Solutions:**
- Ensure MySQL is running: `sudo systemctl start mysql`
- Check credentials in `.env` file
- If using Docker, wait 1-2 min for MySQL to initialize

#### 4. "email-validator is not installed"

**Solution:**
```bash
pip install email-validator
```

#### 5. Database tables not created

**Solution:** Tables are auto-created on startup. Check the logs for errors:
```bash
uvicorn main:app --reload --log-level debug
```

---

## 📁 Project Structure

```
Book-Streaming/
├── frontend/            # Vanilla JS Frontend
│   ├── index.html       # Landing page (Login/Register)
│   ├── dashboard.html   # User dashboard
│   ├── app.js           # API Service & Core logic
│   ├── styles.css       # Global styles & specific CSS files
│   └── ...              # Page-specific JS/HTML files
├── backend/
│   ├── main.py          # FastAPI app & routes
│   ├── models.py        # Pydantic models
│   ├── database.py      # MySQL connection
│   ├── config.py        # App configuration
│   ├── utils.py         # Utility functions
│   ├── images/          # Uploaded book covers
│   ├── tests/           # Test suite
│   └── pytest.ini       # pytest configuration
├── docker-compose.yml   # Docker orchestration
├── Dockerfile           # Backend Container build
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── README.md
```

---

## 🔐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_HOST` | `127.0.0.1` | MySQL host |
| `DATABASE_PORT` | `3306` | MySQL port |
| `DATABASE_USER` | `root` | MySQL username |
| `DATABASE_PASSWORD` | - | MySQL password |
| `DATABASE_NAME` | `book-streaming` | Database name |
| `SECRET_KEY` | - | JWT secret key |
| `MAX_FILE_SIZE` | `5242880` | Max upload size (5MB) |

---

## 📝 License

MIT

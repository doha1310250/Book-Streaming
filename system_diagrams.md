# 📚 Book Streaming - System Diagrams

Complete UML and system diagrams for the Book-Streaming application.

---

## 1. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    USERS {
        VARCHAR user_id PK
        VARCHAR email UK
        VARCHAR name
        VARCHAR password
        INT last_streak
        INT current_streak
        TIMESTAMP created_at
    }
    
    BOOKS {
        VARCHAR book_id PK
        VARCHAR user_id FK
        DATE publish_date
        VARCHAR author_name
        TINYINT is_verified
        VARCHAR title
        VARCHAR cover_url
        TIMESTAMP created_at
    }
    
    FOLLOWERS {
        VARCHAR follower_id PK,FK
        VARCHAR followed_id PK,FK
        TIMESTAMP followed_at
    }
    
    MARKS {
        VARCHAR user_id PK,FK
        VARCHAR book_id PK,FK
        TIMESTAMP marked_at
    }
    
    READING_SESSIONS {
        VARCHAR id PK
        VARCHAR user_id FK
        VARCHAR book_id FK
        DATETIME start_time
        DATETIME end_time
        INT duration_min
        TIMESTAMP created_at
    }
    
    REVIEWS {
        VARCHAR id PK
        VARCHAR user_id FK
        VARCHAR book_id FK
        DECIMAL rating
        TEXT review_comment
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    USERS ||--o{ BOOKS : "creates"
    USERS ||--o{ MARKS : "bookmarks"
    USERS ||--o{ REVIEWS : "writes"
    USERS ||--o{ READING_SESSIONS : "logs"
    USERS ||--o{ FOLLOWERS : "follower"
    USERS ||--o{ FOLLOWERS : "followed"
    BOOKS ||--o{ MARKS : "bookmarked_by"
    BOOKS ||--o{ REVIEWS : "has"
    BOOKS ||--o{ READING_SESSIONS : "tracked_in"
```

---

## 2. Class Diagram (Pydantic Models)

```mermaid
classDiagram
    class UserBase {
        +EmailStr email
        +str name
        +validate_email_format()
    }
    
    class UserCreate {
        +str password
        +validate_password_strength()
    }
    
    class UserLogin {
        +EmailStr email
        +str password
    }
    
    class UserUpdate {
        +Optional~str~ name
        +Optional~str~ password
    }
    
    class UserResponse {
        +str user_id
        +int last_streak
        +int current_streak
        +datetime created_at
    }
    
    class BookBase {
        +str title
        +str author_name
        +Optional~date~ publish_date
        +validate_title()
        +validate_author()
    }
    
    class BookCreate
    class BookUpdate {
        +Optional~str~ title
        +Optional~str~ author_name
        +Optional~date~ publish_date
    }
    
    class BookResponse {
        +str book_id
        +Optional~str~ user_id
        +bool is_verified
        +Optional~str~ cover_url
        +datetime created_at
    }
    
    class MarkedBookResponse {
        +datetime marked_at
    }
    
    class ReviewBase {
        +Optional~Decimal~ rating
        +Optional~str~ review_comment
    }
    
    class ReviewCreate
    class ReviewUpdate
    class ReviewResponse {
        +str id
        +str user_id
        +str book_id
        +datetime created_at
        +datetime updated_at
    }
    
    class ReadingSessionBase {
        +datetime start_time
        +Optional~datetime~ end_time
        +Optional~int~ duration_min
        +validate_times()
    }
    
    class ReadingSessionCreate
    class ReadingSessionResponse {
        +str id
        +str user_id
        +str book_id
        +datetime created_at
    }
    
    class Token {
        +str access_token
        +str token_type
        +UserResponse user
    }
    
    class FollowResponse {
        +str follower_id
        +str followed_id
        +datetime followed_at
    }
    
    class MarkResponse {
        +str user_id
        +str book_id
        +datetime marked_at
    }
    
    UserBase <|-- UserCreate
    UserBase <|-- UserResponse
    BookBase <|-- BookCreate
    BookBase <|-- BookResponse
    BookResponse <|-- MarkedBookResponse
    ReviewBase <|-- ReviewCreate
    ReviewBase <|-- ReviewUpdate
    ReviewBase <|-- ReviewResponse
    ReadingSessionBase <|-- ReadingSessionCreate
    ReadingSessionBase <|-- ReadingSessionResponse
```

---

## 3. Use Case Diagram

```mermaid
flowchart TB
    subgraph Actors
        User((User))
        Admin((Admin))
    end
    
    subgraph Authentication
        UC1[Register]
        UC2[Login]
        UC3[Logout]
    end
    
    subgraph Book_Management["Book Management"]
        UC4[Browse Books]
        UC5[Search Books]
        UC6[View Book Details]
        UC7[Add New Book]
        UC8[Update Book]
        UC9[Delete Book]
        UC10[Upload Cover Image]
    end
    
    subgraph Bookmarks
        UC11[Mark Book]
        UC12[Unmark Book]
        UC13[View Marked Books]
    end
    
    subgraph Reviews
        UC14[Write Review]
        UC15[View Reviews]
        UC16[Update Review]
        UC17[Delete Review]
    end
    
    subgraph Reading_Tracker["Reading Tracker"]
        UC18[Start Reading Session]
        UC19[End Reading Session]
        UC20[View Reading History]
        UC21[View Reading Stats]
        UC22[View Streak Calendar]
    end
    
    subgraph Social
        UC23[Follow User]
        UC24[Unfollow User]
        UC25[View Followers]
        UC26[View Following]
        UC27[Search Users]
        UC28[View User Profile]
        UC29[View Activity Feed]
    end
    
    subgraph Admin_Actions["Admin Actions"]
        UC30[Verify Book]
        UC31[Unverify Book]
    end
    
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8
    User --> UC9
    User --> UC10
    User --> UC11
    User --> UC12
    User --> UC13
    User --> UC14
    User --> UC15
    User --> UC16
    User --> UC17
    User --> UC18
    User --> UC19
    User --> UC20
    User --> UC21
    User --> UC22
    User --> UC23
    User --> UC24
    User --> UC25
    User --> UC26
    User --> UC27
    User --> UC28
    User --> UC29
    
    Admin --> UC30
    Admin --> UC31
```

---

## 4. Sequence Diagrams

### 4.1 User Registration & Login

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant API as FastAPI Backend
    participant DB as MySQL Database
    
    Note over User,DB: Registration Flow
    User->>Frontend: Fill registration form
    Frontend->>API: POST /auth/register
    API->>API: Validate email & password
    API->>DB: Check if email exists
    DB-->>API: Email available
    API->>API: Hash password
    API->>DB: INSERT INTO users
    DB-->>API: User created
    API-->>Frontend: 201 Created + Token
    Frontend->>Frontend: Store token in localStorage
    Frontend-->>User: Redirect to Dashboard
    
    Note over User,DB: Login Flow
    User->>Frontend: Enter credentials
    Frontend->>API: POST /auth/login
    API->>DB: SELECT user by email
    DB-->>API: User data
    API->>API: Verify password hash
    API->>API: Generate JWT token
    API-->>Frontend: 200 OK + Token + User
    Frontend->>Frontend: Store in localStorage
    Frontend-->>User: Redirect to Dashboard
```

### 4.2 Reading Session Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant API as FastAPI Backend
    participant DB as MySQL Database
    
    User->>Frontend: Click "Start Reading" on book
    Frontend->>API: POST /books/{id}/sessions
    Note right of Frontend: {start_time: now()}
    API->>API: Validate JWT token
    API->>DB: Verify book exists
    DB-->>API: Book found
    API->>DB: INSERT reading_session
    DB-->>API: Session created
    API-->>Frontend: 201 Created + session_id
    Frontend->>Frontend: Start timer display
    
    Note over User,DB: User reads...
    
    User->>Frontend: Click "Stop Reading"
    Frontend->>API: PUT /sessions/{session_id}
    Note right of Frontend: {end_time: now()}
    API->>API: Calculate duration_min
    API->>DB: UPDATE reading_session
    API->>DB: UPDATE user streak
    DB-->>API: Updated
    API-->>Frontend: 200 OK + duration
    Frontend-->>User: Show reading summary
```

### 4.3 Social Follow Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant API as FastAPI Backend
    participant DB as MySQL Database
    
    User->>Frontend: Search for users
    Frontend->>API: GET /users/search?query=name
    API->>DB: SELECT users WHERE name LIKE
    DB-->>API: User list
    API-->>Frontend: Users array
    Frontend-->>User: Display user cards
    
    User->>Frontend: Click "Follow" on user
    Frontend->>API: POST /users/{id}/follow
    API->>API: Validate not self-follow
    API->>DB: INSERT INTO followers
    DB-->>API: Follow created
    API-->>Frontend: 201 Created
    Frontend-->>User: Update button to "Unfollow"
    
    User->>Frontend: View activity feed
    Frontend->>API: GET /following/activity
    API->>DB: SELECT sessions JOIN followers
    DB-->>API: Activity data
    API-->>Frontend: Activity feed
    Frontend-->>User: Show followed users' activity
```

### 4.4 Book Review Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant API as FastAPI Backend
    participant DB as MySQL Database
    
    User->>Frontend: Open book modal
    Frontend->>API: GET /books/{id}
    API->>DB: SELECT book
    DB-->>API: Book details
    Frontend->>API: GET /books/{id}/reviews
    API->>DB: SELECT reviews JOIN users
    DB-->>API: Reviews with user names
    API-->>Frontend: Reviews list
    Frontend-->>User: Display book + reviews
    
    User->>Frontend: Submit review (rating + comment)
    Frontend->>API: POST /books/{id}/reviews
    API->>DB: Check existing review
    alt Already reviewed
        API-->>Frontend: 400 Already reviewed
    else New review
        API->>DB: INSERT INTO reviews
        DB-->>API: Review created
        API-->>Frontend: 201 Created
        Frontend-->>User: Show success + update list
    end
```

---

## 5. Deployment / Architecture Diagram

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        Browser["Web Browser"]
    end
    
    subgraph Docker["Docker Environment"]
        subgraph FrontendContainer["Frontend Container (Nginx)"]
            Nginx["Nginx :80"]
            StaticFiles["Static Files<br/>HTML/CSS/JS"]
        end
        
        subgraph BackendContainer["Backend Container (FastAPI)"]
            Uvicorn["Uvicorn :8000"]
            FastAPI["FastAPI App"]
            JWT["JWT Auth"]
            Pydantic["Pydantic Validation"]
        end
        
        subgraph DBContainer["Database Container (MySQL)"]
            MySQL["MySQL 8.0 :3306"]
            DBVolume[("mysql_data<br/>volume")]
        end
        
        subgraph Storage["Persistent Storage"]
            Images[("images/<br/>Book Covers")]
        end
    end
    
    Browser -->|":3000"| Nginx
    Nginx --> StaticFiles
    Nginx -->|"API Proxy"| Uvicorn
    Browser -->|":8000 (direct)"| Uvicorn
    Uvicorn --> FastAPI
    FastAPI --> JWT
    FastAPI --> Pydantic
    FastAPI --> MySQL
    FastAPI --> Images
    MySQL --> DBVolume
    
    style Browser fill:#e1f5fe
    style Nginx fill:#fff3e0
    style FastAPI fill:#e8f5e9
    style MySQL fill:#fce4ec
```

---

## 6. Activity Diagrams

### 6.1 User Dashboard Load

```mermaid
flowchart TD
    A([Page Load]) --> B{Token in localStorage?}
    B -->|No| C[Redirect to Login]
    B -->|Yes| D[Show Skeleton Loaders]
    D --> E[Parallel API Calls]
    
    E --> F[GET /users/me]
    E --> G[GET /books/stats]
    E --> H[GET /marks/me]
    E --> I[GET /sessions/stats]
    E --> J[GET /books]
    
    F --> K{All Loaded?}
    G --> K
    H --> K
    I --> K
    J --> K
    
    K -->|Yes| L[Render Dashboard]
    L --> M[Display User Info]
    L --> N[Display Book Stats]
    L --> O[Display Streak Calendar]
    L --> P[Display Book Grid]
    L --> Q([Dashboard Ready])
    
    K -->|Error| R{Auth Error?}
    R -->|Yes| C
    R -->|No| S[Show Error Toast]
    S --> T[Retry Option]
```

### 6.2 Add New Book

```mermaid
flowchart TD
    A([Click Add Book]) --> B[Open Modal Form]
    B --> C[Fill Title, Author, Date]
    C --> D{Upload Cover?}
    D -->|Yes| E[Select Image File]
    E --> F[Validate File Size < 5MB]
    F -->|Invalid| G[Show Error]
    G --> E
    F -->|Valid| H[Preview Image]
    D -->|No| I[Use Default Cover]
    H --> J[Click Submit]
    I --> J
    J --> K[Create FormData]
    K --> L[POST /books with multipart]
    L --> M{Response OK?}
    M -->|201| N[Close Modal]
    N --> O[Refresh Book List]
    O --> P[Show Success Toast]
    P --> Q([Book Added])
    M -->|Error| R[Show Validation Errors]
    R --> C
```

### 6.3 Reading Timer Session

```mermaid
flowchart TD
    A([Open Timer Page]) --> B{Active Session?}
    B -->|Yes| C[Resume Timer Display]
    B -->|No| D[Show Book Selection]
    D --> E[Select Book to Read]
    E --> F[Click Start]
    F --> G[POST /books/id/sessions]
    G --> H[Store session_id]
    H --> I[Start Timer UI]
    C --> I
    I --> J[Display Elapsed Time]
    J --> K{User Action?}
    K -->|Pause| L[Pause Timer Locally]
    L --> K
    K -->|Resume| J
    K -->|Stop| M[PUT /sessions/id end_time]
    M --> N[Calculate Duration]
    N --> O[Update Streak if needed]
    O --> P[Show Summary Modal]
    P --> Q{Read Another?}
    Q -->|Yes| D
    Q -->|No| R([Exit to Dashboard])
```

---

## 7. Component Diagram (Frontend)

```mermaid
flowchart TB
    subgraph Pages
        Landing["index.html<br/>Landing Page"]
        Dashboard["dashboard.html<br/>Dashboard"]
        Timer["timer.html<br/>Reading Timer"]
        Profile["profile.html<br/>User Profile"]
        Social["social.html<br/>Social Hub"]
        UserProfile["user-profile.html<br/>Public Profile"]
    end
    
    subgraph JavaScript
        AppJS["app.js<br/>APIService + Utils"]
        DashJS["dashboard.js"]
        TimerJS["timer.js"]
        ProfileJS["profile.js"]
        SocialJS["social.js"]
        UserProfJS["user-profile.js"]
        LoginJS["login.js"]
        LandingJS["landing.js"]
    end
    
    subgraph Styles
        GlobalCSS["styles.css<br/>Global Styles"]
        DashCSS["dashboard.css"]
        TimerCSS["timer.css"]
        ProfileCSS["profile.css"]
        SocialCSS["social.css"]
        UserProfCSS["user-profile.css"]
        LoginCSS["login.css"]
        LandingCSS["landing.css"]
    end
    
    subgraph SharedServices["Shared (app.js)"]
        API["APIService"]
        Auth["Auth Utils"]
        Theme["Theme Manager"]
        Toast["Toast Notifications"]
    end
    
    Landing --> LandingJS
    Landing --> LoginJS
    Dashboard --> DashJS
    Timer --> TimerJS
    Profile --> ProfileJS
    Social --> SocialJS
    UserProfile --> UserProfJS
    
    DashJS --> AppJS
    TimerJS --> AppJS
    ProfileJS --> AppJS
    SocialJS --> AppJS
    UserProfJS --> AppJS
    LoginJS --> AppJS
    
    AppJS --> API
    AppJS --> Auth
    AppJS --> Theme
    AppJS --> Toast
```

---

## 8. API Endpoints Summary Table

| Category | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| **Auth** | POST | `/auth/register` | Register new user |
| | POST | `/auth/login` | Login & get JWT token |
| **Users** | GET | `/users/me` | Current user info |
| | PATCH | `/users/me` | Update profile |
| | GET | `/users/{id}/profile` | View public profile |
| | GET | `/users/search` | Search users |
| **Books** | GET | `/books` | List/search books |
| | POST | `/books` | Create book (multipart) |
| | GET | `/books/{id}` | Book details |
| | PUT | `/books/{id}` | Update book |
| | DELETE | `/books/{id}` | Delete book |
| | GET | `/books/stats` | Total book count |
| **Marks** | POST | `/books/{id}/mark` | Bookmark book |
| | DELETE | `/books/{id}/mark` | Remove bookmark |
| | GET | `/marks/me` | User's bookmarks |
| | GET | `/books/{id}/marked` | Check if marked |
| **Reviews** | GET | `/books/{id}/reviews` | Book reviews |
| | POST | `/books/{id}/reviews` | Create review |
| | PUT | `/reviews/{id}` | Update review |
| | DELETE | `/reviews/{id}` | Delete review |
| | GET | `/reviews/me` | User's reviews |
| | GET | `/books/{id}/reviews/summary` | Rating stats |
| **Sessions** | POST | `/books/{id}/sessions` | Start session |
| | PUT | `/sessions/{id}` | End session |
| | GET | `/sessions/me` | User's sessions |
| | GET | `/sessions/stats` | Reading stats |
| **Social** | POST | `/users/{id}/follow` | Follow user |
| | DELETE | `/users/{id}/follow` | Unfollow user |
| | GET | `/following/me` | Users I follow |
| | GET | `/followers/me` | My followers |
| | GET | `/users/{id}/follow/status` | Follow status |
| | GET | `/following/activity` | Activity feed |
| **Admin** | PATCH | `/books/{id}/verify` | Verify book |
| **Health** | GET | `/health` | API health check |

---

> **Note**: All diagrams use Mermaid syntax. You can render them in:
> - GitHub/GitLab Markdown
> - VS Code with Mermaid extension
> - [Mermaid Live Editor](https://mermaid.live)
> - Draw.io (import Mermaid)

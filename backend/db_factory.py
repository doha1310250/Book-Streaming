"""
Database Factory & Seeder for Book Streaming Platform
Generates sample data for development and testing.

Usage:
    python db_factory.py              # Seed with default amounts
    python db_factory.py --users 20   # Custom user count
    python db_factory.py --clear      # Clear all data first
"""

import random
import argparse
from datetime import datetime, timedelta
from database import db, init_database
from utils import generate_id, hash_password

# ========================================
# Sample Data
# ========================================

FIRST_NAMES = [
    "Ahmed", "Mohamed", "Omar", "Yusuf", "Ali", "Hassan", "Ibrahim", "Khaled",
    "Sara", "Fatima", "Nour", "Layla", "Amira", "Mariam", "Hana", "Salma",
    "John", "Emma", "Michael", "Sarah", "David", "Emily", "James", "Olivia"
]

LAST_NAMES = [
    "Hassan", "Ali", "Mohamed", "Ahmed", "Ibrahim", "Khaled", "Mahmoud",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller"
]

BOOK_TITLES = [
    "The Art of Coding", "Clean Architecture", "Design Patterns",
    "Python Mastery", "JavaScript: The Good Parts", "Learning SQL",
    "The Pragmatic Programmer", "Code Complete", "Refactoring",
    "Domain-Driven Design", "Microservices Patterns", "System Design",
    "Algorithms Unlocked", "Data Structures Explained", "Web Development 101",
    "The Midnight Library", "Atomic Habits", "Deep Work", "Thinking Fast and Slow",
    "The Psychology of Money", "Sapiens", "Project Hail Mary", "Dune",
    "1984", "The Great Gatsby", "To Kill a Mockingbird", "Pride and Prejudice",
    "The Alchemist", "Harry Potter and the Philosopher's Stone", "The Hobbit",
    "The Catcher in the Rye", "Lord of the Flies", "Brave New World"
]

AUTHORS = [
    "Robert C. Martin", "Martin Fowler", "Kent Beck", "Eric Evans",
    "Douglas Crockford", "Erich Gamma", "Gang of Four", "Steve McConnell",
    "Andrew Hunt", "David Thomas", "Sam Newman", "Alex Xu",
    "Matt Haig", "James Clear", "Cal Newport", "Daniel Kahneman",
    "Morgan Housel", "Yuval Noah Harari", "Andy Weir", "Frank Herbert",
    "George Orwell", "F. Scott Fitzgerald", "Harper Lee", "Jane Austen",
    "Paulo Coelho", "J.K. Rowling", "J.R.R. Tolkien", "J.D. Salinger"
]

REVIEW_COMMENTS = [
    "Absolutely loved this book! A must-read for everyone.",
    "Great insights and practical advice. Highly recommended.",
    "The author explains complex concepts in a simple way.",
    "Changed my perspective on the topic. Excellent read!",
    "Good book but could be more concise in places.",
    "A classic that stands the test of time.",
    "Couldn't put it down! Finished it in one sitting.",
    "Solid technical content, very practical.",
    "Interesting ideas but the execution could be better.",
    "Perfect for beginners, well-structured content.",
    "One of the best books I've read this year.",
    "The examples are very helpful and easy to follow.",
    "A bit outdated but still has valuable lessons.",
    "Transformative book that everyone should read.",
    "Dense but rewarding. Worth the effort."
]


# ========================================
# Factory Functions
# ========================================

def create_user(cursor, connection):
    """Create a random user and return their data."""
    user_id = generate_id()
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    email = f"{first.lower()}.{last.lower()}.{random.randint(1, 999)}@example.com"
    password = hash_password("Password123!")
    
    created_at = datetime.now() - timedelta(days=random.randint(1, 365))
    current_streak = random.randint(0, 30)
    last_streak = max(current_streak, random.randint(0, 50))
    
    cursor.execute("""
        INSERT INTO users (user_id, email, name, password, current_streak, last_streak, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, email, name, password, current_streak, last_streak, created_at))
    
    return {
        "user_id": user_id,
        "email": email,
        "name": name,
        "password": "Password123!"
    }


def create_book(cursor, connection, user_id):
    """Create a random book and return its data."""
    book_id = generate_id()
    title = random.choice(BOOK_TITLES) + f" (Edition {random.randint(1, 5)})"
    author = random.choice(AUTHORS)
    
    # Random publish date in the last 10 years
    days_ago = random.randint(30, 3650)
    publish_date = (datetime.now() - timedelta(days=days_ago)).date()
    
    is_verified = random.choice([True, False, False])  # 33% chance verified
    created_at = datetime.now() - timedelta(days=random.randint(1, 180))
    
    cursor.execute("""
        INSERT INTO books (book_id, user_id, title, author_name, publish_date, is_verified, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (book_id, user_id, title, author, publish_date, is_verified, created_at))
    
    return {
        "book_id": book_id,
        "title": title,
        "author_name": author
    }


def create_review(cursor, connection, user_id, book_id):
    """Create a random review."""
    review_id = generate_id()
    rating = random.choice([3.0, 3.5, 4.0, 4.5, 5.0, 4.0, 4.5])  # Skew positive
    comment = random.choice(REVIEW_COMMENTS)
    
    created_at = datetime.now() - timedelta(days=random.randint(1, 90))
    
    cursor.execute("""
        INSERT INTO reviews (id, user_id, book_id, rating, review_comment, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (review_id, user_id, book_id, rating, comment, created_at))
    
    return {"id": review_id, "rating": rating}


def create_mark(cursor, connection, user_id, book_id):
    """Create a bookmark for a user on a book."""
    marked_at = datetime.now() - timedelta(days=random.randint(1, 60))
    
    try:
        cursor.execute("""
            INSERT INTO marks (user_id, book_id, marked_at)
            VALUES (%s, %s, %s)
        """, (user_id, book_id, marked_at))
        return True
    except:
        return False  # Duplicate mark


def create_follow(cursor, connection, follower_id, followed_id):
    """Create a follow relationship."""
    followed_at = datetime.now() - timedelta(days=random.randint(1, 90))
    
    try:
        cursor.execute("""
            INSERT INTO followers (follower_id, followed_id, followed_at)
            VALUES (%s, %s, %s)
        """, (follower_id, followed_id, followed_at))
        return True
    except:
        return False  # Duplicate follow


def create_reading_session(cursor, connection, user_id, book_id):
    """Create a reading session."""
    session_id = generate_id()
    
    # Random session in the last 30 days
    days_ago = random.randint(0, 30)
    start_time = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 12))
    duration_min = random.randint(10, 120)
    end_time = start_time + timedelta(minutes=duration_min)
    
    cursor.execute("""
        INSERT INTO reading_sessions (id, user_id, book_id, start_time, end_time, duration_min)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (session_id, user_id, book_id, start_time, end_time, duration_min))
    
    return {"id": session_id, "duration_min": duration_min}


# ========================================
# Seeder
# ========================================

def clear_database():
    """Clear all data from the database."""
    print("🗑️  Clearing all data...")
    
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            # Order matters due to foreign keys
            tables = ['reading_sessions', 'reviews', 'marks', 'followers', 'books', 'users']
            for table in tables:
                cursor.execute(f"DELETE FROM {table}")
                print(f"   Cleared {table}")
    
    print("✅ Database cleared!\n")


def seed_database(num_users=10, num_books=25, num_reviews=50, num_marks=40, 
                  num_follows=30, num_sessions=60):
    """Seed the database with sample data."""
    
    print("🌱 Starting database seeding...\n")
    
    # Initialize tables first
    init_database()
    
    users = []
    books = []
    
    with db.get_connection() as connection:
        with db.get_cursor(connection) as cursor:
            
            # Create Users
            print(f"👤 Creating {num_users} users...")
            for i in range(num_users):
                user = create_user(cursor, connection)
                users.append(user)
                if (i + 1) % 5 == 0:
                    print(f"   Created {i + 1} users")
            print(f"   ✅ Created {len(users)} users\n")
            
            # Create Books
            print(f"📚 Creating {num_books} books...")
            for i in range(num_books):
                user = random.choice(users)
                book = create_book(cursor, connection, user["user_id"])
                books.append(book)
                if (i + 1) % 10 == 0:
                    print(f"   Created {i + 1} books")
            print(f"   ✅ Created {len(books)} books\n")
            
            # Create Reviews
            print(f"⭐ Creating {num_reviews} reviews...")
            review_count = 0
            for _ in range(num_reviews):
                user = random.choice(users)
                book = random.choice(books)
                try:
                    create_review(cursor, connection, user["user_id"], book["book_id"])
                    review_count += 1
                except:
                    pass  # Skip duplicates
            print(f"   ✅ Created {review_count} reviews\n")
            
            # Create Marks
            print(f"🔖 Creating {num_marks} bookmarks...")
            mark_count = 0
            for _ in range(num_marks):
                user = random.choice(users)
                book = random.choice(books)
                if create_mark(cursor, connection, user["user_id"], book["book_id"]):
                    mark_count += 1
            print(f"   ✅ Created {mark_count} bookmarks\n")
            
            # Create Follows
            print(f"👥 Creating {num_follows} follow relationships...")
            follow_count = 0
            for _ in range(num_follows):
                follower = random.choice(users)
                followed = random.choice(users)
                if follower["user_id"] != followed["user_id"]:
                    if create_follow(cursor, connection, follower["user_id"], followed["user_id"]):
                        follow_count += 1
            print(f"   ✅ Created {follow_count} follows\n")
            
            # Create Reading Sessions
            print(f"📖 Creating {num_sessions} reading sessions...")
            session_count = 0
            for _ in range(num_sessions):
                user = random.choice(users)
                book = random.choice(books)
                create_reading_session(cursor, connection, user["user_id"], book["book_id"])
                session_count += 1
            print(f"   ✅ Created {session_count} reading sessions\n")
    
    # Print summary
    print("=" * 50)
    print("🎉 Database seeding complete!")
    print("=" * 50)
    print(f"\nCreated:")
    print(f"  • {len(users)} users")
    print(f"  • {len(books)} books")
    print(f"  • {review_count} reviews")
    print(f"  • {mark_count} bookmarks")
    print(f"  • {follow_count} follows")
    print(f"  • {session_count} reading sessions")
    
    # Print sample credentials
    print(f"\n📋 Sample login credentials:")
    for user in users[:3]:
        print(f"   Email: {user['email']}")
        print(f"   Password: {user['password']}\n")
    
    return users, books


# ========================================
# Main
# ========================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the Book Streaming database")
    parser.add_argument("--users", type=int, default=10, help="Number of users to create")
    parser.add_argument("--books", type=int, default=25, help="Number of books to create")
    parser.add_argument("--reviews", type=int, default=50, help="Number of reviews to create")
    parser.add_argument("--marks", type=int, default=40, help="Number of bookmarks to create")
    parser.add_argument("--follows", type=int, default=30, help="Number of follows to create")
    parser.add_argument("--sessions", type=int, default=60, help="Number of reading sessions")
    parser.add_argument("--clear", action="store_true", help="Clear all data before seeding")
    
    args = parser.parse_args()
    
    if args.clear:
        clear_database()
    
    seed_database(
        num_users=args.users,
        num_books=args.books,
        num_reviews=args.reviews,
        num_marks=args.marks,
        num_follows=args.follows,
        num_sessions=args.sessions
    )

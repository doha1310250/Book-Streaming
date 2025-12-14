# database.py
import mysql.connector
from mysql.connector import pooling, Error
from contextlib import contextmanager
from typing import Generator, Optional
import logging

from config import settings

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance: Optional['DatabaseConnection'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="book_pool",
                pool_size=10,
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                database=settings.DATABASE_NAME,
                autocommit=True,
                charset='utf8mb4',
                collation='utf8mb4_general_ci'
            )
            logger.info("Database connection pool created successfully")
        except Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator[mysql.connector.connection.MySQLConnection, None, None]:
        """Get a connection from the pool"""
        connection = None
        try:
            connection = self.pool.get_connection()
            yield connection
        except Error as e:
            logger.error(f"Error getting database connection: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @contextmanager
    def get_cursor(self, connection: mysql.connector.connection.MySQLConnection = None):
        """Get a cursor for database operations"""
        close_connection = False
        if connection is None:
            connection = self.pool.get_connection()
            close_connection = True
        
        cursor = connection.cursor(dictionary=True, buffered=True)
        try:
            yield cursor
            if not connection.in_transaction:
                connection.commit()
        except Error as e:
            if connection.in_transaction:
                connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
            if close_connection and connection.is_connected():
                connection.close()

# Global database instance
db = DatabaseConnection()

def init_database():
    """Initialize database tables if they don't exist"""
    try:
        with db.get_connection() as connection:
            with db.get_cursor(connection) as cursor:
                # Check if tables exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id VARCHAR(50) PRIMARY KEY,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        last_streak INT DEFAULT 0,
                        current_streak INT DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                        book_id VARCHAR(50) PRIMARY KEY,
                        user_id VARCHAR(50),
                        publish_date DATE,
                        author_name VARCHAR(100) NOT NULL,
                        is_verified TINYINT(1) DEFAULT 0,
                        title VARCHAR(255) NOT NULL,
                        cover_url VARCHAR(500),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS followers (
                        follower_id VARCHAR(50) NOT NULL,
                        followed_id VARCHAR(50) NOT NULL,
                        followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (follower_id, followed_id),
                        FOREIGN KEY (follower_id) REFERENCES users(user_id) ON DELETE CASCADE,
                        FOREIGN KEY (followed_id) REFERENCES users(user_id) ON DELETE CASCADE
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS marks (
                        user_id VARCHAR(50) NOT NULL,
                        book_id VARCHAR(50) NOT NULL,
                        marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (user_id, book_id),
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                        FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reading_sessions (
                        id VARCHAR(50) PRIMARY KEY,
                        user_id VARCHAR(50) NOT NULL,
                        book_id VARCHAR(50) NOT NULL,
                        start_time DATETIME NOT NULL,
                        end_time DATETIME,
                        duration_min INT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                        FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reviews (
                        id VARCHAR(50) PRIMARY KEY,
                        user_id VARCHAR(50) NOT NULL,
                        book_id VARCHAR(50) NOT NULL,
                        rating DECIMAL(3,1) CHECK (rating >= 0 AND rating <= 5),
                        review_comment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        UNIQUE (user_id, book_id),
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                        FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
                    )
                """)
                
                logger.info("Database tables initialized successfully")
    except Error as e:
        logger.error(f"Error initializing database: {e}")
        raise
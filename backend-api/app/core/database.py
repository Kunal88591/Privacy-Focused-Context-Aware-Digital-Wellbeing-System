"""
Database Configuration with Connection Pooling
Optimized database settings for production performance
"""

from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
import logging
import time

logger = logging.getLogger(__name__)

# Database URL (would be from environment in production)
DATABASE_URL = "postgresql://user:password@localhost:5432/wellbeing_db"

# Create engine with optimized pool settings
engine = create_engine(
    DATABASE_URL,
    # Connection pool settings for high performance
    poolclass=pool.QueuePool,
    pool_size=20,              # Number of persistent connections
    max_overflow=40,           # Additional connections when pool is full
    pool_timeout=30,           # Timeout for getting connection from pool
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Check connection health before using
    echo=False,                # Disable SQL query logging for performance
    # Performance optimizations
    connect_args={
        "connect_timeout": 10,
        "application_name": "wellbeing_api",
    }
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Don't expire objects after commit
)

# Base class for models
Base = declarative_base()


# Database query performance logging
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries"""
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution time"""
    total = time.time() - conn.info['query_start_time'].pop(-1)
    total_ms = total * 1000
    
    # Log slow queries (>100ms)
    if total_ms > 100:
        logger.warning(f"SLOW QUERY ({total_ms:.2f}ms): {statement[:100]}...")


# Dependency for getting database session
def get_db() -> Session:
    """
    Get database session with automatic cleanup
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database connection health check
def check_database_connection() -> bool:
    """Check if database connection is healthy"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# Get database statistics
def get_pool_stats():
    """Get connection pool statistics"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_connections": pool.size() + pool.overflow()
    }

"""
PostgreSQL database connection and health check.
Lazy initialization with SQLAlchemy (placeholder implementation).
"""
import time
from typing import Optional, Tuple

from backend.app.config import get_config
from backend.app.logging import db_logger

# Optional SQLAlchemy import - fail gracefully if not installed
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
    from sqlalchemy.exc import SQLAlchemyError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Engine = None  # type: ignore


class PostgresClient:
    """PostgreSQL client with lazy initialization and health checking"""
    
    def __init__(self):
        self._engine: Optional[Engine] = None
        self._config = get_config()
    
    def _initialize(self) -> None:
        """Initialize database engine if not already initialized"""
        if self._engine is not None:
            return
        
        if not SQLALCHEMY_AVAILABLE:
            db_logger.warning("SQLAlchemy not available - PostgreSQL features disabled")
            return
        
        db_url = self._config.DB_URL
        if not db_url:
            db_logger.warning("DB_URL not configured - PostgreSQL features disabled")
            return
        
        try:
            self._engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            db_logger.info("PostgreSQL engine initialized")
        except Exception as e:
            db_logger.error(f"Failed to initialize PostgreSQL engine: {e}")
            self._engine = None
    
    def is_available(self) -> bool:
        """Check if PostgreSQL client is configured and available"""
        return (
            SQLALCHEMY_AVAILABLE
            and self._config.DB_URL is not None
        )
    
    async def health_check(self) -> Tuple[bool, str, Optional[float]]:
        """
        Perform health check on PostgreSQL connection.
        
        Returns:
            Tuple of (is_healthy, message, response_time_ms)
        """
        if not self.is_available():
            return False, "PostgreSQL not configured or SQLAlchemy not available", None
        
        self._initialize()
        
        if self._engine is None:
            return False, "PostgreSQL engine initialization failed", None
        
        start_time = time.time()
        try:
            with self._engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            response_time_ms = (time.time() - start_time) * 1000
            return True, "PostgreSQL connection healthy", response_time_ms
        
        except SQLAlchemyError as e:
            response_time_ms = (time.time() - start_time) * 1000
            db_logger.error(f"PostgreSQL health check failed: {e}")
            return False, f"PostgreSQL error: {str(e)}", response_time_ms
        
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            db_logger.error(f"Unexpected error during PostgreSQL health check: {e}")
            return False, f"Unexpected error: {str(e)}", response_time_ms
    
    def get_engine(self) -> Optional[Engine]:
        """Get the SQLAlchemy engine (for advanced usage)"""
        if not self.is_available():
            return None
        self._initialize()
        return self._engine


# Global client instance
_postgres_client: Optional[PostgresClient] = None


def get_postgres_client() -> PostgresClient:
    """Get the global PostgreSQL client instance"""
    global _postgres_client
    if _postgres_client is None:
        _postgres_client = PostgresClient()
    return _postgres_client

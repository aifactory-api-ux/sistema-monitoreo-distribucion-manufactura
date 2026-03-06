import os
import logging
from typing import Generator, Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from .config import get_settings
from .models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self.settings = get_settings()
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._initialized = False
    
    @property
    def engine(self) -> Engine:
        """Get or create database engine"""
        if self._engine is None:
            self._create_engine()
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Get or create session factory"""
        if self._session_factory is None:
            self._create_session_factory()
        return self._session_factory
    
    def _create_engine(self) -> None:
        """Create database engine with appropriate configuration"""
        try:
            engine_kwargs = {
                "echo": self.settings.debug,
                "future": True,
            }
            
            if self.settings.is_sqlite:
                # SQLite-specific configuration
                engine_kwargs.update({
                    "poolclass": StaticPool,
                    "connect_args": {
                        "check_same_thread": False,
                        "timeout": 30,
                    },
                })
            else:
                # PostgreSQL/MySQL configuration
                engine_kwargs.update({
                    "pool_size": self.settings.db_pool_size,
                    "max_overflow": self.settings.db_max_overflow,
                    "pool_timeout": self.settings.db_pool_timeout,
                    "pool_recycle": self.settings.db_pool_recycle,
                    "pool_pre_ping": True,
                })
            
            self._engine = create_engine(
                self.settings.database_url,
                **engine_kwargs
            )
            
            # Enable SQLite foreign key constraints
            if self.settings.is_sqlite:
                @event.listens_for(self._engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA synchronous=NORMAL")
                    cursor.execute("PRAGMA cache_size=1000")
                    cursor.execute("PRAGMA temp_store=MEMORY")
                    cursor.close()
            
            logger.info(f"Database engine created: {self.settings.database_url}")
            
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    
    def _create_session_factory(self) -> None:
        """Create session factory"""
        try:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            logger.info("Database session factory created")
            
        except Exception as e:
            logger.error(f"Failed to create session factory: {e}")
            raise
    
    def create_tables(self) -> None:
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def drop_tables(self) -> None:
        """Drop all database tables"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
            
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    def check_connection(self) -> bool:
        """Check database connectivity"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
            
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    def get_session(self) -> Session:
        """Get a new database session"""
        try:
            return self.session_factory()
            
        except Exception as e:
            logger.error(f"Failed to create database session: {e}")
            raise
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations"""
        session = self.get_session()
        try:
            yield session
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
            
        finally:
            session.close()
    
    def initialize(self) -> None:
        """Initialize database connection and create tables if needed"""
        if self._initialized:
            return
        
        try:
            # Test connection
            if not self.check_connection():
                raise OperationalError("Cannot connect to database", None, None)
            
            # Create tables if they don't exist
            self.create_tables()
            
            self._initialized = True
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def close(self) -> None:
        """Close database connections"""
        try:
            if self._engine:
                self._engine.dispose()
                logger.info("Database connections closed")
                
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

# Global database manager instance
_db_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Get or create global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session"""
    db_manager = get_database_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

def init_database() -> None:
    """Initialize database - call this at application startup"""
    try:
        db_manager = get_database_manager()
        db_manager.initialize()
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise SystemExit(1)

def close_database() -> None:
    """Close database connections - call this at application shutdown"""
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None
        logger.info("Database connections closed")

def check_database_health() -> dict:
    """Check database health for health endpoint"""
    try:
        db_manager = get_database_manager()
        is_connected = db_manager.check_connection()
        
        return {
            "database_connected": is_connected,
            "database_url": db_manager.settings.database_url.split('@')[-1] if '@' in db_manager.settings.database_url else db_manager.settings.database_url,
            "database_type": "sqlite" if db_manager.settings.is_sqlite else "postgresql" if db_manager.settings.is_postgresql else "mysql"
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "database_connected": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Test database connection
    try:
        init_database()
        db_manager = get_database_manager()
        
        with db_manager.session_scope() as session:
            result = session.execute(text("SELECT 1 as test"))
            print(f"Database test successful: {result.fetchone()}")
        
        health = check_database_health()
        print(f"Database health: {health}")
        
    except Exception as e:
        print(f"Database test failed: {e}")
    
    finally:
        close_database()
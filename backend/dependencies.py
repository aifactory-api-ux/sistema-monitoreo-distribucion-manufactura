from sqlalchemy.orm import Session
from shared.database import get_db_session


def get_db():
    """FastAPI dependency to get a database session."""
    with get_db_session() as session:
        yield session

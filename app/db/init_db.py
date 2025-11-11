"""
Initialize database tables
"""
from app.db.database import engine, Base
from app.db.models import ScanResult, KnownScam, UserReport


def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()


from collections.abc import Generator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

from core.settings import settings

# Create engine with connection pooling
engine = create_engine(
    str(settings.sqlalchemy_database_url),
    poolclass=QueuePool,
    pool_pre_ping=True,
    pool_size=18,
    max_overflow=7,
    echo=settings.debug,  # Enable SQL echo in debug mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

Base = declarative_base(metadata=metadata)


def create_schema():
    """Create all database tables."""
    metadata.create_all(engine)


def create_session() -> Generator[Session, None, None]:
    """
    Database session generator for dependency injection.
    Ensures session is properly closed after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

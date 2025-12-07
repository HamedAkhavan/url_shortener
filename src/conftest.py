import logging

import pytest
from fastapi.testclient import TestClient
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text

from core.database import Base, SessionLocal, create_session
from core.settings import settings
from main import app

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.pool").setLevel(logging.ERROR)


TEST_DB_NAME = "test_db"
POSTGRES_HOST = "0.0.0.0"


@pytest.fixture(scope="module")
def engine():
    engine = create_engine(
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{POSTGRES_HOST}:{settings.postgres_port}/{settings.postgres_db}"
    )
    conn = engine.connect()
    conn.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
    conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))

    # Create an engine for the test database
    test_engine = create_engine(
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{POSTGRES_HOST}:{settings.postgres_port}/{TEST_DB_NAME}"
    )
    # Create the tables
    Base.metadata.create_all(test_engine)
    yield test_engine
    # Drop the tables after the tests are done
    test_connection = test_engine.connect()
    test_connection.execute(text("DROP TABLE IF EXISTS narrative_blockchain CASCADE"))
    test_connection.close()
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()
    conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
    conn.close()
    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """Creates a new database session for a test and rolls it back after the test."""
    connection = engine.connect()
    transaction = connection.begin()

    # Bind an individual Session to the connection
    session = SessionLocal(bind=connection)

    yield session

    # Rollback the transaction after the test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(session):
    def override_create_session():
        try:
            yield session
        finally:
            session.close()

    app.user_middleware = []
    app.middleware_stack = app.build_middleware_stack()
    app.dependency_overrides[create_session] = override_create_session
    client = TestClient(app)
    yield client
    del app.dependency_overrides[create_session]

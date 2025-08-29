"""
Test configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.security import get_password_hash
from app.database.models import User, UserRole, UserStatus

# Test database URL (in-memory SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_user(db):
    """Create admin user for testing"""
    user = User(
        email="admin@test.com",
        password_hash=get_password_hash("testpassword"),
        first_name="Test",
        last_name="Admin",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def doctor_user(db):
    """Create doctor user for testing"""
    user = User(
        email="doctor@test.com",
        password_hash=get_password_hash("testpassword"),
        first_name="Test",
        last_name="Doctor",
        role=UserRole.DOCTOR,
        status=UserStatus.ACTIVE,
        specialization="General Medicine"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, admin_user):
    """Get authentication headers for admin user"""
    response = client.post(
        "/api/v1/auth/login-json",
        json={"email": "admin@test.com", "password": "testpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

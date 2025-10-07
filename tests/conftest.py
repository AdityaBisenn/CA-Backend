# tests/conftest.py
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, Base
from app.tenant.models.firm import CAFirm
from app.tenant.models.user import User
from app.cdm.models.entity import Entity
from app.core.auth import create_access_token, get_password_hash, UserRole
from datetime import datetime, timedelta
import uuid

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a fresh database session for each test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_firm(db_session):
    """Create a sample CA firm for testing"""
    firm = CAFirm(
        firm_id=str(uuid.uuid4()),
        firm_name="Test CA Firm",
        firm_registration_no="TEST123",
        contact_email="test@cafirm.com",
        phone="1234567890",
        address="123 Test Street",
        city="Test City",
        state="Test State",
        pincode="12345",
        is_active=True
    )
    db_session.add(firm)
    db_session.commit()
    db_session.refresh(firm)
    return firm


@pytest.fixture
def second_firm(db_session):
    """Create a second CA firm for testing isolation"""
    firm = CAFirm(
        firm_id=str(uuid.uuid4()),
        firm_name="Second CA Firm",
        firm_registration_no="TEST456",
        contact_email="test2@cafirm.com",
        phone="0987654321",
        address="456 Second Street",
        city="Second City",
        state="Second State",
        country="Test Country",
        postal_code="54321",
        is_active=True
    )
    db_session.add(firm)
    db_session.commit()
    db_session.refresh(firm)
    return firm


@pytest.fixture
def trenor_admin_user(db_session):
    """Create a Trenor admin user"""
    user = User(
        user_id=str(uuid.uuid4()),
        name="Admin User",
        email="admin@trenor.com",
        role=UserRole.TRENOR_ADMIN,
        is_active=True,
        firm_id=None  # Trenor admins don't belong to a specific firm
    )
    user.password_hash = get_password_hash("admin123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def firm_admin_user(db_session, sample_firm):
    """Create a firm admin user"""
    user = User(
        user_id=str(uuid.uuid4()),
        name="Firm Admin",
        email="firmadmin@test.com",
        role=UserRole.CA_FIRM_ADMIN,
        is_active=True,
        firm_id=sample_firm.firm_id
    )
    user.password_hash = get_password_hash("firmadmin123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def staff_user(db_session, sample_firm):
    """Create a staff user"""
    user = User(
        user_id=str(uuid.uuid4()),
        name="Staff User",
        email="staff@test.com",
        role=UserRole.CA_STAFF,
        is_active=True,
        firm_id=sample_firm.firm_id
    )
    user.password_hash = get_password_hash("staff123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def viewer_user(db_session, sample_firm):
    """Create a viewer user"""
    user = User(
        user_id=str(uuid.uuid4()),
        name="Viewer User",
        email="viewer@test.com",
        role=UserRole.CA_VIEWER,
        is_active=True,
        firm_id=sample_firm.firm_id
    )
    user.password_hash = get_password_hash("viewer123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def client_user(db_session):
    """Create a client user"""
    user = User(
        user_id=str(uuid.uuid4()),
        name="Client User",
        email="client@test.com",
        role=UserRole.CLIENT_USER,
        is_active=True,
        firm_id=None  # Clients might not belong to a firm directly
    )
    user.password_hash = get_password_hash("client123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def trenor_admin_token(trenor_admin_user):
    """Create JWT token for Trenor admin"""
    return create_access_token(data={"sub": trenor_admin_user.user_id})


@pytest.fixture
def firm_admin_token(firm_admin_user):
    """Create JWT token for firm admin"""
    return create_access_token(data={"sub": firm_admin_user.user_id})


@pytest.fixture
def staff_token(staff_user):
    """Create JWT token for staff user"""
    return create_access_token(data={"sub": staff_user.user_id})


@pytest.fixture
def viewer_token(viewer_user):
    """Create JWT token for viewer user"""
    return create_access_token(data={"sub": viewer_user.user_id})


@pytest.fixture
def client_token(client_user):
    """Create JWT token for client user"""
    return create_access_token(data={"sub": client_user.user_id})


@pytest.fixture
def auth_headers_trenor_admin(trenor_admin_token):
    """Authorization headers for Trenor admin"""
    return {"Authorization": f"Bearer {trenor_admin_token}"}


@pytest.fixture
def auth_headers_firm_admin(firm_admin_token):
    """Authorization headers for firm admin"""
    return {"Authorization": f"Bearer {firm_admin_token}"}


@pytest.fixture
def auth_headers_staff(staff_token):
    """Authorization headers for staff user"""
    return {"Authorization": f"Bearer {staff_token}"}


@pytest.fixture
def auth_headers_viewer(viewer_token):
    """Authorization headers for viewer user"""
    return {"Authorization": f"Bearer {viewer_token}"}


@pytest.fixture
def auth_headers_client(client_token):
    """Authorization headers for client user"""
    return {"Authorization": f"Bearer {client_token}"}


@pytest.fixture
def sample_entity(db_session, sample_firm):
    """Create a sample entity for testing"""
    entity = Entity(
        company_id=str(uuid.uuid4()),
        company_name="Test Company",
        firm_id=sample_firm.firm_id,
        company_type="Private Limited",
        incorporation_date=datetime.now().date(),
        firm_registration_no="COMP123",
        pan="ABCDE1234F",
        tan="ABCD12345E",
        gstin="12ABCDE3456F1Z7",
        is_active=True
    )
    db_session.add(entity)
    db_session.commit()
    db_session.refresh(entity)
    return entity


@pytest.fixture
def invalid_token():
    """Create an invalid JWT token for testing"""
    return "invalid.jwt.token"


@pytest.fixture
def expired_token():
    """Create an expired JWT token for testing"""
    return create_access_token(
        data={"sub": "test_user"}, 
        expires_delta=timedelta(minutes=-1)  # Already expired
    )


def pytest_configure(config):
    """Configure pytest"""
    # Set environment variables for testing
    os.environ["TESTING"] = "1"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
import pytest

from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User


# -------------------------
# Fake database
# -------------------------

class FakeDB:
    def __init__(self):
        self.added_objects = []
        self.committed = False

    def add(self, obj):
        self.added_objects.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        obj.id = 1
        obj.created_at = datetime.utcnow()
        obj.updated_at = datetime.utcnow()


fake_user = User(
    id=123,
    email="test@example.com",
    password_hash="fake_hash",
    full_name="Test User",
)

# fake_db = FakeDB()


def override_get_current_user():
    return fake_user


@pytest.fixture
def fake_db():
    return FakeDB()


@pytest.fixture
def client(fake_db):
    def override_get_db():
        yield fake_db

    previous_overrides = app.dependency_overrides.copy()

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous_overrides)


# -------------------------
# Tests
# -------------------------

def test_create_job(client, fake_db):
    response = client.post(
        "/jobs",
        json={
            "title": "Software Engineer",
            "company": "Google",
            "location": "Mountain View, CA",
            "job_description": (
                "We are looking for a Python developer "
                "with FastAPI and PostgreSQL experience."
            ),
            "source_url": "https://example.com/jobs/123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["title"] == "Software Engineer"
    assert data["company"] == "Google"
    assert data["location"] == "Mountain View, CA"
    assert data["job_description"] == (
        "We are looking for a Python developer "
        "with FastAPI and PostgreSQL experience."
    )
    assert data["source_url"] == "https://example.com/jobs/123"

    assert fake_db.committed is True

    saved_job = fake_db.added_objects[-1]

    assert saved_job.user_id == 123
    assert saved_job.title == "Software Engineer"
    assert saved_job.company == "Google"

def test_create_job_without_optional_fields(client, fake_db):
    response = client.post(
        "/jobs",
        json={
            "title": "Backend Engineer",
            "company": "Amazon",
            "job_description": "Looking for a backend engineer.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Backend Engineer"
    assert data["company"] == "Amazon"
    assert data["location"] is None
    assert data["source_url"] is None

    saved_job = fake_db.added_objects[-1]

    assert saved_job.location is None
    assert saved_job.source_url is None

def test_create_job_with_empty_title_returns_422(client):
    response = client.post(
        "/jobs",
        json={
            "title": "   ",
            "company": "Google",
            "job_description": "Python developer required.",
        },
    )

    assert response.status_code == 422

def test_create_job_with_empty_company_returns_422(client):
    response = client.post(
        "/jobs",
        json={
            "title": "Software Engineer",
            "company": "   ",
            "job_description": "Python developer required.",
        },
    )

    assert response.status_code == 422

def test_create_job_with_empty_job_description_returns_422(client):
    response = client.post(
        "/jobs",
        json={
            "title": "Software Engineer",
            "company": "Google",
            "job_description": "   ",
        },
    )

    assert response.status_code == 422

def test_create_job_with_oversized_job_description_returns_422(client):
    response = client.post(
        "/jobs",
        json={
            "title": "Software Engineer",
            "company": "Google",
            "job_description": "A" * 50001,
        },
    )

    assert response.status_code == 422

def test_create_job_with_missing_required_fields_returns_422(client):
    response = client.post(
        "/jobs",
        json={
            "location": "Mumbai",
        },
    )

    assert response.status_code == 422
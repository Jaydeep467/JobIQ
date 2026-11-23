from datetime import datetime
from io import BytesIO

from fastapi.testclient import TestClient
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.main import app
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.resume import Resume
from app.api.routes import resumes as resume_routes
from app.services import resume_service


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

fake_db = FakeDB()


def override_get_current_user():
    return fake_user


def override_get_db():
    yield fake_db


app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# -------------------------
# Tests
# -------------------------

def test_upload_pdf_resume(monkeypatch, tmp_path):
    monkeypatch.setattr(
        resume_service,
        "RESUME_STORAGE_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        resume_routes,
        "extract_text_from_pdf",
        lambda file_path: "Extracted PDF resume text",
    )

    response = client.post(
        "/resumes/upload",
        files={
            "file": (
                "resume.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["filename"] == "resume.pdf"
    assert data["id"] == 1

    assert fake_db.committed is True

    saved_resume = fake_db.added_objects[-1]

    assert saved_resume.user_id == 123
    assert saved_resume.filename == "resume.pdf"
    assert saved_resume.extracted_text == "Extracted PDF resume text"


def test_upload_docx_resume(monkeypatch, tmp_path):
    monkeypatch.setattr(
        resume_service,
        "RESUME_STORAGE_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        resume_routes,
        "extract_text_from_docx",
        lambda file_path: "Extracted DOCX resume text",
        raising=False,
    )

    response = client.post(
        "/resumes/upload",
        files={
            "file": (
                "resume.docx",
                b"fake docx content",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["filename"] == "resume.docx"
    assert data["id"] == 1

    saved_resume = fake_db.added_objects[-1]

    assert saved_resume.user_id == 123
    assert saved_resume.filename == "resume.docx"
    assert saved_resume.extracted_text == "Extracted DOCX resume text"


def test_upload_unsupported_file_returns_400(monkeypatch, tmp_path):
    monkeypatch.setattr(
        resume_service,
        "RESUME_STORAGE_DIR",
        tmp_path,
    )

    response = client.post(
        "/resumes/upload",
        files={
            "file": (
                "resume.txt",
                b"some text",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF and DOCX files are supported"
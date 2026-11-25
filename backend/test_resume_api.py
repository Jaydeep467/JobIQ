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

def test_upload_resume_returns_parsed_data(monkeypatch, tmp_path):
    monkeypatch.setattr(
        resume_service,
        "RESUME_STORAGE_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        resume_routes,
        "extract_text_from_pdf",
        lambda file_path: "Raw resume text",
    )

    parsed_resume = {
        "summary": "Software Engineer",
        "skills": ["Python", "React"],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "contact": {
            "email": "test@example.com",
            "phone": None,
            "linkedin": None,
            "github": None,
        },
    }

    monkeypatch.setattr(
        resume_routes,
        "parse_resume",
        lambda text: parsed_resume,
        raising=False,
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
    assert data["parsed_data"] == parsed_resume
    
    saved_resume = fake_db.added_objects[-1]

    assert saved_resume.extracted_text == "Raw resume text"
    assert saved_resume.parsed_data == parsed_resume

def test_upload_resume_with_empty_extracted_text_returns_400(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        resume_service,
        "RESUME_STORAGE_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        resume_routes,
        "extract_text_from_pdf",
        lambda file_path: "",
    )

    response = client.post(
        "/resumes/upload",
        files={
            "file": (
                "empty_resume.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Resume text cannot be empty"

def test_match_resume_to_job(monkeypatch):
    parsed_resume = {
        "skills": ["Python", "FastAPI", "React"],
    }

    resume = Resume(
        id=1,
        user_id=123,
        filename="resume.pdf",
        file_path="fake/path/resume.pdf",
        extracted_text="Fake resume text",
        parsed_data=parsed_resume,
    )

    # Fake the database query
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return resume

    monkeypatch.setattr(
        fake_db,
        "query",
        lambda model: FakeQuery(),
        raising=False,
    )

    expected_match_result = {
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": ["AWS", "Docker"],
        "match_percentage": 50.0,
        "total_skills": 4,
        "matched_count": 2,
        "missing_count": 2,
    }

    # Mock the matching service
    monkeypatch.setattr(
        resume_routes,
        "match_resume_to_job",
        lambda parsed_data, job_description: expected_match_result,
        raising=False,
    )

    response = client.post(
        "/resumes/1/match",
        json={
            "job_description": (
                "We are looking for a Python and FastAPI developer "
                "with AWS and Docker experience."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["resume_id"] == 1
    assert data["matched_skills"] == ["Python", "FastAPI"]
    assert data["missing_skills"] == ["AWS", "Docker"]
    assert data["match_percentage"] == 50.0
    assert data["total_skills"] == 4
    assert data["matched_count"] == 2
    assert data["missing_count"] == 2

def test_match_resume_not_found(monkeypatch):
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

    monkeypatch.setattr(
        fake_db,
        "query",
        lambda model: FakeQuery(),
        raising=False,
    )

    response = client.post(
        "/resumes/999/match",
        json={
            "job_description": "Python developer with FastAPI experience",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume not found"

def test_match_resume_with_empty_job_description_returns_422():
    response = client.post(
        "/resumes/1/match",
        json={
            "job_description": "   ",
        },
    )

    assert response.status_code == 422

def test_match_resume_with_oversized_job_description_returns_422():
    response = client.post(
        "/resumes/1/match",
        json={
            "job_description": "A" * 50001,
        },
    )

    assert response.status_code == 422
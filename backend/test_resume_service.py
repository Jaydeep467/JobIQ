import pytest
from pathlib import Path
from fastapi import UploadFile
from io import BytesIO
from starlette.datastructures import Headers

from app.services.resume_service import save_resume_file


@pytest.mark.anyio
async def test_save_resume_file_accepts_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.resume_service.RESUME_STORAGE_DIR",
        tmp_path,
    )

    file = UploadFile(
        filename="resume.pdf",
        file=BytesIO(b"fake pdf content"),
        headers=Headers({"content-type": "application/pdf"}),
    )

    saved_path = await save_resume_file(file)

    assert saved_path.endswith(".pdf")
    assert Path(saved_path).exists()
    assert Path(saved_path).read_bytes() == b"fake pdf content"


@pytest.mark.anyio
async def test_save_resume_file_accepts_docx(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.resume_service.RESUME_STORAGE_DIR",
        tmp_path,
    )

    file = UploadFile(
        filename="resume.docx",
        file=BytesIO(b"fake docx content"),
        headers=Headers({
            "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }),
    )

    saved_path = await save_resume_file(file)

    assert saved_path.endswith(".docx")
    assert Path(saved_path).exists()
    assert Path(saved_path).read_bytes() == b"fake docx content"


@pytest.mark.anyio
async def test_save_resume_file_rejects_unsupported_extension(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.resume_service.RESUME_STORAGE_DIR",
        tmp_path,
    )

    file = UploadFile(
        filename="resume.txt",
        file=BytesIO(b"text content"),
        headers=Headers({"content-type": "text/plain"}),
    )

    with pytest.raises(
        ValueError,
        match="Only PDF and DOCX files are supported",
    ):
        await save_resume_file(file)


@pytest.mark.anyio
async def test_save_resume_file_rejects_mismatched_content_type(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.resume_service.RESUME_STORAGE_DIR",
        tmp_path,
    )

    file = UploadFile(
        filename="resume.pdf",
        file=BytesIO(b"fake pdf content"),
        headers=Headers({"content-type": "text/plain"}),
    )

    with pytest.raises(ValueError, match="Invalid file type"):
        await save_resume_file(file)


@pytest.mark.anyio
async def test_save_resume_file_rejects_empty_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.resume_service.RESUME_STORAGE_DIR",
        tmp_path,
    )

    file = UploadFile(
        filename="resume.pdf",
        file=BytesIO(b""),
        headers=Headers({"content-type": "application/pdf"}),
    )

    with pytest.raises(ValueError, match="The uploaded file is empty"):
        await save_resume_file(file)
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


RESUME_STORAGE_DIR = Path("storage/resumes")
ALLOWED_CONTENT_TYPE = "application/pdf"


async def save_resume_file(file: UploadFile) -> str:
    if file.content_type != ALLOWED_CONTENT_TYPE:
        raise ValueError("Only PDF files are supported")

    extension = Path(file.filename or "").suffix.lower()

    if extension != ".pdf":
        raise ValueError("Only PDF files are supported")

    stored_filename = f"{uuid4()}.pdf"
    file_path = RESUME_STORAGE_DIR / stored_filename

    RESUME_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    contents = await file.read()

    if not contents:
        raise ValueError("The uploaded file is empty")

    file_path.write_bytes(contents)

    return str(file_path)
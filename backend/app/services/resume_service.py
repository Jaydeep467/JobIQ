from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


RESUME_STORAGE_DIR = Path("storage/resumes")

ALLOWED_FILE_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


async def save_resume_file(file: UploadFile) -> str:
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_FILE_TYPES:
        raise ValueError("Only PDF and DOCX files are supported")

    expected_content_type = ALLOWED_FILE_TYPES[extension]

    if file.content_type != expected_content_type:
        raise ValueError("Invalid file type")

    stored_filename = f"{uuid4()}{extension}"
    file_path = RESUME_STORAGE_DIR / stored_filename

    RESUME_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    contents = await file.read()

    if not contents:
        raise ValueError("The uploaded file is empty")

    file_path.write_bytes(contents)

    return str(file_path)
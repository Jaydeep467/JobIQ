from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.resume import Resume
from app.models.user import User
from app.services.pdf_service import extract_text_from_pdf
from app.services.resume_service import save_resume_file
from pathlib import Path
from app.services.docx_service import extract_text_from_docx
from app.services.resume_parser import parse_resume
from app.schemas.job_match import JobMatchRequest
from app.services.job_matcher import match_resume_to_job

router = APIRouter(
    prefix="/resumes",
    tags=["resumes"],
)


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ):
    try:
        file_path = await save_resume_file(file)

        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            extracted_text = extract_text_from_pdf(file_path)

        elif extension == ".docx":
            extracted_text = extract_text_from_docx(file_path)

        else:
            raise ValueError("Unsupported resume file type")
        
        parsed_data = parse_resume(extracted_text)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    resume = Resume(
        user_id=current_user.id,
        filename=file.filename or "resume.pdf",
        file_path=file_path,
        extracted_text=extracted_text,
        parsed_data=parsed_data,
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "filename": resume.filename,
        "created_at": resume.created_at,
        "parsed_data": parsed_data,
    }


@router.get("/")
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )

    return [
        {
            "id": resume.id,
            "filename": resume.filename,
            "created_at": resume.created_at,
        }
        for resume in resumes
    ]


@router.get("/{resume_id}")
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    return {
        "id": resume.id,
        "filename": resume.filename,
        "extracted_text": resume.extracted_text,
        "created_at": resume.created_at,
        "updated_at": resume.updated_at,
    }

@router.post("/{resume_id}/match")
def match_resume(
    resume_id: int,
    request: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    match_result = match_resume_to_job(
        resume.parsed_data,
        request.job_description,
    )

    return {
        "resume_id": resume.id,
        **match_result,
    }

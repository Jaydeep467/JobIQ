from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.resume import Resume
from app.models.user import User
from app.services.resume_service import save_resume_file


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
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    resume = Resume(
        user_id=current_user.id,
        filename=file.filename or "resume.pdf",
        file_path=file_path,
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "filename": resume.filename,
        "created_at": resume.created_at,
    }
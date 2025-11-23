"""
API routes for resume management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import shutil
import hashlib

from ...database import get_db
from ...database.models import Resume
from ...schemas.resume import (
    ResumeResponse, ResumeUpdate, ResumeUploadResponse,
    ResumeSelectionRequest, ResumeSelectionResponse
)
from ...config import settings

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    db: Session = Depends(get_db)
):
    """List all resume templates"""
    resumes = db.query(Resume).order_by(Resume.is_master.desc(), Resume.times_used.desc()).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific resume by ID"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found"
        )
    return resume


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    name: str = Form(...),
    focus_areas: Optional[str] = Form(None),  # Comma-separated
    technologies: Optional[str] = Form(None),  # Comma-separated
    is_master: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Upload new resume template"""
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.doc']
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not supported. Allowed: {', '.join(allowed_extensions)}"
        )

    # Check file size (read first chunk to validate)
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit"
        )

    # Reset file pointer
    await file.seek(0)

    # Check resume count limit
    resume_count = db.query(Resume).count()
    if resume_count >= settings.MAX_RESUMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum number of resumes ({settings.MAX_RESUMES}) reached. Delete some resumes first."
        )

    # Generate unique filename
    file_hash = hashlib.md5(file_content).hexdigest()[:10]
    safe_filename = f"{name.replace(' ', '_')}_{file_hash}{file_extension}"
    file_path = settings.RESUMES_DIR / safe_filename

    # Save file
    try:
        with file_path.open("wb") as buffer:
            buffer.write(file_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Parse focus areas and technologies
    focus_areas_list = [fa.strip() for fa in focus_areas.split(",")] if focus_areas else []
    technologies_list = [tech.strip() for tech in technologies.split(",")] if technologies else []

    # Extract keywords from resume (simple implementation - can be enhanced)
    keywords = _extract_keywords_from_resume(file_path, technologies_list)

    # Create resume record
    resume = Resume(
        user_id=1,  # Default to single user
        name=name,
        file_path=str(file_path),
        file_format=file_extension[1:],  # Remove the dot
        file_size=len(file_content),
        is_master=is_master,
        focus_areas=focus_areas_list,
        keywords=keywords,
        technologies=technologies_list
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeUploadResponse(
        id=resume.id,
        name=resume.name,
        file_path=resume.file_path,
        file_format=resume.file_format,
        message="Resume uploaded successfully"
    )


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: int,
    update: ResumeUpdate,
    db: Session = Depends(get_db)
):
    """Update resume metadata"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found"
        )

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(resume, key, value)

    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Delete resume template"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found"
        )

    # Delete file
    file_path = Path(resume.file_path)
    if file_path.exists():
        file_path.unlink()

    # Delete record
    db.delete(resume)
    db.commit()
    return None


@router.post("/select", response_model=ResumeSelectionResponse)
async def select_best_resume(
    request: ResumeSelectionRequest,
    db: Session = Depends(get_db)
):
    """Auto-select best resume template for job description"""
    # Get all resumes
    resumes = db.query(Resume).all()

    if not resumes:
        return ResumeSelectionResponse(
            resume_id=None,
            resume_name=None,
            match_score=0,
            reasons=["No resumes available. Please upload a resume first."]
        )

    # Extract keywords from job description
    job_keywords = _extract_keywords(request.job_description.lower())

    # Score each resume
    best_resume = None
    best_score = 0
    best_reasons = []

    for resume in resumes:
        score = 0
        reasons = []

        # Match technologies
        if resume.technologies:
            resume_techs = [t.lower() for t in resume.technologies]
            matched_techs = [tech for tech in resume_techs if tech in job_keywords]
            if matched_techs:
                score += len(matched_techs) * 10
                reasons.append(f"Matches technologies: {', '.join(matched_techs)}")

        # Match focus areas
        if resume.focus_areas:
            resume_focus = [f.lower() for f in resume.focus_areas]
            matched_focus = [focus for focus in resume_focus if any(focus in keyword for keyword in job_keywords)]
            if matched_focus:
                score += len(matched_focus) * 20
                reasons.append(f"Matches focus areas: {', '.join(matched_focus)}")

        # Prefer master template if no clear winner (boost)
        if resume.is_master:
            score += 5
            reasons.append("Master template")

        # Prefer frequently used resumes
        if resume.times_used > 0:
            usage_bonus = min(10, resume.times_used // 5)
            score += usage_bonus
            if usage_bonus > 0:
                reasons.append(f"Used successfully {resume.times_used} times")

        # Prefer resumes with high success rate
        if resume.success_rate > 0:
            success_bonus = int(resume.success_rate * 0.1)
            score += success_bonus
            if success_bonus > 0:
                reasons.append(f"Success rate: {resume.success_rate:.1f}%")

        if score > best_score:
            best_score = score
            best_resume = resume
            best_reasons = reasons

    if not best_resume:
        # Fallback to first resume
        best_resume = resumes[0]
        best_reasons = ["Default selection"]

    return ResumeSelectionResponse(
        resume_id=best_resume.id,
        resume_name=best_resume.name,
        match_score=min(100, best_score),
        reasons=best_reasons if best_reasons else ["Selected as default"]
    )


@router.get("/download/{resume_id}")
async def download_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Download resume file"""
    from fastapi.responses import FileResponse

    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found"
        )

    file_path = Path(resume.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found on disk"
        )

    return FileResponse(
        path=file_path,
        filename=f"{resume.name}.{resume.file_format}",
        media_type="application/octet-stream"
    )


def _extract_keywords_from_resume(file_path: Path, technologies: List[str]) -> List[str]:
    """Extract keywords from resume file (simple implementation)"""
    # For now, just return the technologies
    # Can be enhanced with PDF/DOCX parsing
    return technologies


def _extract_keywords(text: str) -> set:
    """Extract relevant keywords from job description"""
    tech_keywords = {
        'java', 'python', 'javascript', 'typescript', 'c++', 'go', 'rust', 'c#',
        'react', 'angular', 'vue', 'node', 'spring', 'django', 'flask', 'express',
        'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'terraform', 'ansible',
        'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
        'kafka', 'rabbitmq', 'spark', 'hadoop', 'airflow',
        'machine learning', 'ai', 'deep learning', 'nlp', 'computer vision',
        'distributed systems', 'microservices', 'scalability', 'performance',
        'backend', 'frontend', 'fullstack', 'full stack', 'full-stack',
        'devops', 'sre', 'site reliability', 'infrastructure',
        'agile', 'scrum', 'ci/cd', 'jenkins', 'gitlab', 'github actions',
        'rest api', 'graphql', 'grpc', 'websocket',
        'linux', 'unix', 'bash', 'shell', 'sql'
    }

    found_keywords = set()
    text_lower = text.lower()

    for keyword in tech_keywords:
        if keyword in text_lower:
            found_keywords.add(keyword)

    return found_keywords

"""
Resume Routes
File upload, parsing, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import shutil

from ..database import get_db
from ..models.user import User
from ..models.resume import Resume, ParsingStatus
from ..models.candidate import Candidate, Education, Experience, Skill
from ..routes.auth import get_current_user
from ..config import settings
from ..utils.validators import validate_file_extension, validate_file_size, sanitize_filename
from ..utils.helpers import generate_unique_filename, get_file_path
from ..services.text_extraction import extract_text_from_file
from ..services.nlp_pipeline import NLPPipeline
from ..services.ml_parser import get_ml_parser
from ..services.scoring import get_scoring_engine

router = APIRouter()


# Pydantic models
class ResumeResponse(BaseModel):
    id: int
    file_name: str
    file_type: str
    file_size: Optional[int]
    uploaded_at: datetime
    parsing_status: ParsingStatus
    parsed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ParseResult(BaseModel):
    resume_id: int
    candidate_id: Optional[int]
    status: str
    message: str
    data: Optional[dict]


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a resume file"""
    
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_extensions)}"
        )
    
    # Read file to check size
    contents = await file.read()
    file_size = len(contents)
    
    if not validate_file_size(file_size):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    safe_filename = sanitize_filename(file.filename)
    unique_filename = generate_unique_filename(safe_filename)
    file_path = get_file_path(unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create database record
    file_ext = safe_filename.rsplit('.', 1)[-1].lower()
    resume = Resume(
        file_name=safe_filename,
        file_path=file_path,
        file_type=file_ext,
        file_size=file_size,
        uploaded_by=current_user.id,
        parsing_status=ParsingStatus.PENDING
    )
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return resume


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[ParsingStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all resumes with pagination"""
    
    query = db.query(Resume)
    
    if status_filter:
        query = query.filter(Resume.parsing_status == status_filter)
    
    resumes = query.order_by(Resume.uploaded_at.desc()).offset(skip).limit(limit).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resume by ID"""
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume


@router.post("/{resume_id}/parse", response_model=ParseResult)
async def parse_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Parse a resume and extract information"""
    
    # Get resume
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check if already parsed
    if resume.parsing_status == ParsingStatus.COMPLETED:
        candidate = db.query(Candidate).filter(Candidate.resume_id == resume_id).first()
        return ParseResult(
            resume_id=resume_id,
            candidate_id=candidate.id if candidate else None,
            status="already_parsed",
            message="Resume already parsed",
            data=None
        )
    
    # Update status to processing
    resume.parsing_status = ParsingStatus.PROCESSING
    db.commit()
    
    try:
        # Extract text
        extraction_result = extract_text_from_file(resume.file_path)
        
        if not extraction_result['success']:
            resume.parsing_status = ParsingStatus.FAILED
            resume.error_message = extraction_result.get('error', 'Unknown error')
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Text extraction failed: {extraction_result.get('error')}"
            )
        
        text = extraction_result['text']
        
        # NLP processing
        nlp = NLPPipeline()
        cleaned_text = nlp.preprocess_text(text)
        sections = nlp.detect_sections(cleaned_text)
        keywords = nlp.extract_keywords(cleaned_text)
        
        # ML parsing
        ml_parser = get_ml_parser()
        parsed_data = ml_parser.parse_resume(cleaned_text, sections)
        
        # Create candidate record
        personal_info = parsed_data.get('personal_info', {})
        candidate = Candidate(
            resume_id=resume_id,
            full_name=personal_info.get('name'),
            email=personal_info.get('email'),
            phone=personal_info.get('phone'),
            linkedin_url=personal_info.get('linkedin'),
            github_url=personal_info.get('github'),
            address=personal_info.get('location')
        )
        
        db.add(candidate)
        db.flush()  # Get candidate ID
        
        # Add skills
        for keyword in keywords:
            skill = Skill(
                candidate_id=candidate.id,
                skill_name=keyword['keyword'],
                skill_category=keyword['category']
            )
            db.add(skill)
        
        # Calculate total experience (simplified)
        candidate.total_experience_years = 0.0  # Will be calculated from experience entries
        
        # Update resume status
        resume.parsing_status = ParsingStatus.COMPLETED
        resume.parsed_at = datetime.utcnow()
        resume.error_message = None
        
        db.commit()
        db.refresh(candidate)
        
        # Calculate score
        scoring_engine = get_scoring_engine()
        score_result = scoring_engine.calculate_total_score(
            experience_years=candidate.total_experience_years,
            skills=[s.skill_name for s in candidate.skills],
            education=[],
            certifications=[],
            projects=[]
        )
        
        return ParseResult(
            resume_id=resume_id,
            candidate_id=candidate.id,
            status="success",
            message="Resume parsed successfully",
            data={
                "personal_info": personal_info,
                "skills_count": len(keywords),
                "score": score_result
            }
        )
        
    except Exception as e:
        resume.parsing_status = ParsingStatus.FAILED
        resume.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parsing failed: {str(e)}"
        )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resume"""
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete file
    try:
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
    except Exception as e:
        print(f"Failed to delete file: {e}")
    
    # Delete database record (cascade will delete candidate)
    db.delete(resume)
    db.commit()
    
    return None

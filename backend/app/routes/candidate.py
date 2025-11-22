"""
Candidate Routes
Candidate management, search, and export
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import csv
import io

from ..database import get_db
from ..models.user import User
from ..models.candidate import Candidate, Education, Experience, Skill, Certification, Project
from ..routes.auth import get_current_user

router = APIRouter()


# Pydantic models
class SkillResponse(BaseModel):
    id: int
    skill_name: str
    skill_category: Optional[str]
    proficiency_level: Optional[str]
    
    class Config:
        from_attributes = True


class CandidateResponse(BaseModel):
    id: int
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    total_experience_years: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class CandidateDetail(CandidateResponse):
    address: Optional[str]
    portfolio_url: Optional[str]
    summary: Optional[str]
    skills: List[SkillResponse]
    
    class Config:
        from_attributes = True


class CandidateUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    summary: Optional[str]


class SearchRequest(BaseModel):
    skills: Optional[List[str]] = None
    min_experience: Optional[float] = None
    max_experience: Optional[float] = None
    keyword: Optional[str] = None


@router.get("/", response_model=List[CandidateResponse])
async def list_candidates(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all candidates with pagination"""
    
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()
    return candidates


@router.get("/{candidate_id}", response_model=CandidateDetail)
async def get_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get candidate details by ID"""
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    update_data: CandidateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update candidate information"""
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Update fields
    if update_data.full_name is not None:
        candidate.full_name = update_data.full_name
    if update_data.email is not None:
        candidate.email = update_data.email
    if update_data.phone is not None:
        candidate.phone = update_data.phone
    if update_data.summary is not None:
        candidate.summary = update_data.summary
    
    candidate.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(candidate)
    
    return candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a candidate"""
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    db.delete(candidate)
    db.commit()
    
    return None


@router.post("/search", response_model=List[CandidateResponse])
async def search_candidates(
    search_params: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Advanced candidate search"""
    
    query = db.query(Candidate)
    
    # Filter by experience
    if search_params.min_experience is not None:
        query = query.filter(Candidate.total_experience_years >= search_params.min_experience)
    if search_params.max_experience is not None:
        query = query.filter(Candidate.total_experience_years <= search_params.max_experience)
    
    # Filter by skills
    if search_params.skills:
        # Join with skills table
        query = query.join(Skill).filter(
            Skill.skill_name.in_([s.lower() for s in search_params.skills])
        ).distinct()
    
    # Keyword search in name, email, summary
    if search_params.keyword:
        keyword = f"%{search_params.keyword}%"
        query = query.filter(
            (Candidate.full_name.ilike(keyword)) |
            (Candidate.email.ilike(keyword)) |
            (Candidate.summary.ilike(keyword))
        )
    
    candidates = query.all()
    return candidates


@router.get("/{candidate_id}/export")
async def export_candidate(
    candidate_id: int,
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export candidate data in JSON or CSV format"""
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Prepare data
    data = {
        "id": candidate.id,
        "full_name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "linkedin": candidate.linkedin_url,
        "github": candidate.github_url,
        "experience_years": candidate.total_experience_years,
        "skills": [s.skill_name for s in candidate.skills],
        "summary": candidate.summary
    }
    
    if format.lower() == "json":
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=candidate_{candidate_id}.json"}
        )
    
    elif format.lower() == "csv":
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["Field", "Value"])
        
        # Data
        for key, value in data.items():
            if isinstance(value, list):
                value = ", ".join(value)
            writer.writerow([key, value])
        
        csv_content = output.getvalue()
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=candidate_{candidate_id}.csv"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Use 'json' or 'csv'"
        )

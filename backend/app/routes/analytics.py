"""
Analytics Routes
Dashboard metrics and reporting
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User
from ..models.resume import Resume, ParsingStatus
from ..models.candidate import Candidate, Skill
from ..routes.auth import get_current_user

router = APIRouter()


# Pydantic models
class OverviewMetrics(BaseModel):
    total_resumes: int
    total_candidates: int
    parsed_resumes: int
    pending_resumes: int
    failed_resumes: int
    success_rate: float
    avg_experience_years: float


class SkillDistribution(BaseModel):
    skill_name: str
    count: int
    category: str


@router.get("/overview", response_model=OverviewMetrics)
async def get_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard overview metrics"""
    
    # Total resumes
    total_resumes = db.query(Resume).count()
    
    # Total candidates
    total_candidates = db.query(Candidate).count()
    
    # Resumes by status
    parsed_resumes = db.query(Resume).filter(Resume.parsing_status == ParsingStatus.COMPLETED).count()
    pending_resumes = db.query(Resume).filter(Resume.parsing_status == ParsingStatus.PENDING).count()
    failed_resumes = db.query(Resume).filter(Resume.parsing_status == ParsingStatus.FAILED).count()
    
    # Success rate
    success_rate = (parsed_resumes / total_resumes * 100) if total_resumes > 0 else 0.0
    
    # Average experience
    avg_exp_result = db.query(func.avg(Candidate.total_experience_years)).scalar()
    avg_experience = float(avg_exp_result) if avg_exp_result else 0.0
    
    return OverviewMetrics(
        total_resumes=total_resumes,
        total_candidates=total_candidates,
        parsed_resumes=parsed_resumes,
        pending_resumes=pending_resumes,
        failed_resumes=failed_resumes,
        success_rate=round(success_rate, 2),
        avg_experience_years=round(avg_experience, 1)
    )


@router.get("/skills-distribution", response_model=List[SkillDistribution])
async def get_skills_distribution(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top skills distribution"""
    
    # Query skills with counts
    skills_query = db.query(
        Skill.skill_name,
        Skill.skill_category,
        func.count(Skill.id).label('count')
    ).group_by(
        Skill.skill_name,
        Skill.skill_category
    ).order_by(
        func.count(Skill.id).desc()
    ).limit(limit).all()
    
    return [
        SkillDistribution(
            skill_name=skill[0],
            category=skill[1] or 'other',
            count=skill[2]
        )
        for skill in skills_query
    ]


@router.get("/trends")
async def get_trends(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get parsing trends over time"""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query resumes by date
    resumes_by_date = db.query(
        func.date(Resume.uploaded_at).label('date'),
        func.count(Resume.id).label('count')
    ).filter(
        Resume.uploaded_at >= start_date
    ).group_by(
        func.date(Resume.uploaded_at)
    ).order_by(
        func.date(Resume.uploaded_at)
    ).all()
    
    # Format results
    trends = [
        {
            "date": str(item[0]),
            "count": item[1]
        }
        for item in resumes_by_date
    ]
    
    return {
        "period_days": days,
        "start_date": str(start_date.date()),
        "end_date": str(end_date.date()),
        "data": trends
    }


@router.get("/experience-distribution")
async def get_experience_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get experience level distribution"""
    
    # Define experience ranges
    ranges = [
        ("0-2 years", 0, 2),
        ("2-5 years", 2, 5),
        ("5-10 years", 5, 10),
        ("10+ years", 10, 100)
    ]
    
    distribution = []
    
    for label, min_exp, max_exp in ranges:
        count = db.query(Candidate).filter(
            Candidate.total_experience_years >= min_exp,
            Candidate.total_experience_years < max_exp
        ).count()
        
        distribution.append({
            "range": label,
            "count": count
        })
    
    return {
        "distribution": distribution
    }

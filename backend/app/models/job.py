"""
Job Role and Matching Models
"""

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class JobRole(Base):
    """Job role/description model"""
    __tablename__ = "job_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    required_skills = Column(Text)  # Comma-separated or JSON
    preferred_skills = Column(Text)  # Comma-separated or JSON
    min_experience_years = Column(Float, default=0.0)
    max_experience_years = Column(Float, nullable=True)
    education_requirements = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    matches = relationship("JobMatch", back_populates="job_role", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JobRole {self.title}>"


class CandidateScore(Base):
    """Candidate scoring results"""
    __tablename__ = "candidate_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))
    job_role_id = Column(Integer, ForeignKey("job_roles.id"), nullable=True)
    
    # Scores (0-100)
    total_score = Column(Float, index=True)
    experience_score = Column(Float)
    skills_score = Column(Float)
    education_score = Column(Float)
    certification_score = Column(Float)
    project_score = Column(Float)
    
    # Grade
    grade = Column(String(5))  # A+, A, B, C, D
    
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    candidate = relationship("Candidate", back_populates="scores")
    
    def __repr__(self):
        return f"<CandidateScore {self.total_score} ({self.grade})>"


class JobMatch(Base):
    """Candidate-Job matching results"""
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))
    job_role_id = Column(Integer, ForeignKey("job_roles.id", ondelete="CASCADE"))
    
    match_percentage = Column(Float, index=True)
    missing_skills = Column(Text)  # Comma-separated
    matching_skills = Column(Text)  # Comma-separated
    recommendations = Column(Text)
    
    matched_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job_role = relationship("JobRole", back_populates="matches")
    
    def __repr__(self):
        return f"<JobMatch {self.match_percentage}%>"

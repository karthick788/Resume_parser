"""
Candidate Models - Extracted Information
"""

from sqlalchemy import Column, Integer, String, Text, Float, Date, Boolean, ForeignKey, DateTime, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Candidate(Base):
    """Candidate information extracted from resume"""
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), unique=True)
    
    # Personal Information
    full_name = Column(String(255), index=True)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    address = Column(Text)
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))
    
    # Summary
    summary = Column(Text)
    total_experience_years = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    resume = relationship("Resume", back_populates="candidate")
    education = relationship("Education", back_populates="candidate", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="candidate", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="candidate", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="candidate", cascade="all, delete-orphan")
    scores = relationship("CandidateScore", back_populates="candidate", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Candidate {self.full_name}>"


class Education(Base):
    """Education details"""
    __tablename__ = "education"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))
    
    degree = Column(String(255))
    field_of_study = Column(String(255))
    institution = Column(String(255))
    location = Column(String(255))
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    gpa = Column(Float, nullable=True)
    description = Column(Text)
    
    # Relationship
    candidate = relationship("Candidate", back_populates="education")
    
    def __repr__(self):
        return f"<Education {self.degree} at {self.institution}>"


class Experience(Base):
    """Work experience details"""
    __tablename__ = "experience"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))
    
    company_name = Column(String(255))
    designation = Column(String(255))
    location = Column(String(255))
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    technologies_used = Column(Text)  # Comma-separated or JSON
    
    # Relationship
    candidate = relationship("Candidate", back_populates="experience")
    
    def __repr__(self):
        return f"<Experience {self.designation} at {self.company_name}>"


class Skill(Base):
    """Skills extracted from resume"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))
    
    skill_name = Column(String(100), index=True)
    skill_category = Column(String(100))  # programming, database, cloud, etc.
    proficiency_level = Column(String(50))  # beginner, intermediate, expert
    years_of_experience = Column(Float, nullable=True)
    
    # Relationship
    candidate = relationship("Candidate", back_populates="skills")
    
    def __repr__(self):
        return f"<Skill {self.skill_name}>"


class Certification(Base):
    """Certifications and licenses"""
    __tablename__ = "certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))
    
    certification_name = Column(String(255))
    issuing_organization = Column(String(255))
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    credential_id = Column(String(255))
    credential_url = Column(String(500))
    
    # Relationship
    candidate = relationship("Candidate", back_populates="certifications")
    
    def __repr__(self):
        return f"<Certification {self.certification_name}>"


class Project(Base):
    """Projects mentioned in resume"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))
    
    project_name = Column(String(255))
    description = Column(Text)
    technologies_used = Column(Text)  # Comma-separated
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    project_url = Column(String(500))
    
    # Relationship
    candidate = relationship("Candidate", back_populates="projects")
    
    def __repr__(self):
        return f"<Project {self.project_name}>"

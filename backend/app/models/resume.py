"""
Resume Model - Uploaded Resume Files
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class ParsingStatus(str, enum.Enum):
    """Resume parsing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Resume(Base):
    """Resume file model"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, docx
    file_size = Column(Integer, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    parsing_status = Column(Enum(ParsingStatus), default=ParsingStatus.PENDING)
    parsed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String(500), nullable=True)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Resume {self.file_name}>"

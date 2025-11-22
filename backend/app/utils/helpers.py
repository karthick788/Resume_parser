"""
Helper Utilities
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from ..config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT access token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename with UUID prefix"""
    ext = original_filename.rsplit('.', 1)[-1] if '.' in original_filename else ''
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{ext}" if ext else unique_id


def get_file_path(filename: str) -> str:
    """Get full file path in upload directory"""
    return os.path.join(settings.upload_dir, filename)


def calculate_experience_years(start_date: Optional[datetime], end_date: Optional[datetime]) -> float:
    """Calculate years of experience from date range"""
    if not start_date:
        return 0.0
    
    if not end_date:
        end_date = datetime.now()
    
    delta = end_date - start_date
    years = delta.days / 365.25
    return round(years, 1)


def format_score(score: float) -> str:
    """Format score to 2 decimal places"""
    return f"{score:.2f}"


def get_grade(score: float) -> str:
    """Convert score to grade"""
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    else:
        return 'D'


def clean_text(text: str) -> str:
    """Basic text cleaning"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove null bytes
    text = text.replace('\x00', '')
    return text.strip()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length] + "..."

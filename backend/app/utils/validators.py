"""
Validation Utilities
"""

import os
from typing import Optional
from ..config import settings


def validate_file_extension(filename: str) -> bool:
    """Check if file extension is allowed"""
    if not filename:
        return False
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in settings.allowed_extensions


def validate_file_size(file_size: int) -> bool:
    """Check if file size is within limits"""
    return file_size <= settings.max_upload_size


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    if '.' in filename:
        return filename.rsplit('.', 1)[-1].lower()
    return ''


def is_pdf(filename: str) -> bool:
    """Check if file is PDF"""
    return get_file_extension(filename) == 'pdf'


def is_docx(filename: str) -> bool:
    """Check if file is DOCX"""
    ext = get_file_extension(filename)
    return ext in ['docx', 'doc']


def validate_email(email: str) -> bool:
    """Basic email validation"""
    if not email:
        return False
    return '@' in email and '.' in email.split('@')[-1]


def validate_phone(phone: str) -> bool:
    """Basic phone validation"""
    if not phone:
        return False
    digits = ''.join(filter(str.isdigit, phone))
    return 7 <= len(digits) <= 15


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal"""
    # Remove path components
    filename = os.path.basename(filename)
    # Remove potentially dangerous characters
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    return filename


def validate_url(url: str) -> bool:
    """Basic URL validation"""
    if not url:
        return False
    return url.startswith(('http://', 'https://'))

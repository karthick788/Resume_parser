"""
Regex Patterns for Information Extraction
"""

import re
from typing import List, Optional


# Email pattern
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Phone patterns (supports multiple formats)
PHONE_REGEX = r'(?:(?:\+|00)?(\d{1,3})[-.\s]?)?(?:\((\d{1,4})\)[-.\s]?)?(\d{1,4})[-.\s]?(\d{1,4})[-.\s]?(\d{1,9})'

# URL pattern
URL_REGEX = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'

# Date patterns
DATE_REGEX = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b'
DATE_RANGE_REGEX = r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\w+\s+\d{4})\s*[-–to]+\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\w+\s+\d{4}|Present|Current)'

# LinkedIn URL
LINKEDIN_REGEX = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'

# GitHub URL
GITHUB_REGEX = r'(?:https?://)?(?:www\.)?github\.com/[\w-]+'

# Degree patterns
DEGREE_PATTERNS = [
    r'\b(?:B\.?S\.?|Bachelor(?:\'s)?)\s+(?:of\s+)?(?:Science|Arts|Engineering|Technology|Business|Commerce)\b',
    r'\b(?:M\.?S\.?|Master(?:\'s)?)\s+(?:of\s+)?(?:Science|Arts|Engineering|Technology|Business|Commerce)\b',
    r'\b(?:Ph\.?D\.?|Doctorate)\b',
    r'\b(?:MBA|BBA|BCA|MCA|B\.?Tech|M\.?Tech)\b'
]


def extract_emails(text: str) -> List[str]:
    """Extract all email addresses from text"""
    emails = re.findall(EMAIL_REGEX, text, re.IGNORECASE)
    return list(set(emails))  # Remove duplicates


def extract_phones(text: str) -> List[str]:
    """Extract phone numbers from text"""
    phones = re.findall(PHONE_REGEX, text)
    # Clean and format phone numbers
    cleaned_phones = []
    for match in phones:
        if isinstance(match, tuple):
            phone = ''.join(filter(str.isdigit, ''.join(match)))
            if 7 <= len(phone) <= 15:  # Valid phone number length
                cleaned_phones.append(phone)
        elif isinstance(match, str):
            phone = ''.join(filter(str.isdigit, match))
            if 7 <= len(phone) <= 15:
                cleaned_phones.append(phone)
    return list(set(cleaned_phones))


def extract_urls(text: str) -> List[str]:
    """Extract all URLs from text"""
    urls = re.findall(URL_REGEX, text, re.IGNORECASE)
    return list(set(urls))


def extract_linkedin(text: str) -> Optional[str]:
    """Extract LinkedIn profile URL"""
    matches = re.findall(LINKEDIN_REGEX, text, re.IGNORECASE)
    return matches[0] if matches else None


def extract_github(text: str) -> Optional[str]:
    """Extract GitHub profile URL"""
    matches = re.findall(GITHUB_REGEX, text, re.IGNORECASE)
    return matches[0] if matches else None


def extract_dates(text: str) -> List[str]:
    """Extract dates from text"""
    dates = re.findall(DATE_REGEX, text, re.IGNORECASE)
    return dates


def extract_date_ranges(text: str) -> List[tuple]:
    """Extract date ranges (e.g., 'Jan 2020 - Dec 2022')"""
    ranges = re.findall(DATE_RANGE_REGEX, text, re.IGNORECASE)
    return ranges


def find_url_by_domain(urls: List[str], domain: str) -> Optional[str]:
    """Find URL containing specific domain"""
    for url in urls:
        if domain.lower() in url.lower():
            return url
    return None


def extract_degrees(text: str) -> List[str]:
    """Extract degree mentions from text"""
    degrees = []
    for pattern in DEGREE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        degrees.extend(matches)
    return list(set(degrees))

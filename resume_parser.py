import re
import os
import magic
import pdfplumber
from docx import Document
import spacy
from typing import Dict, List, Optional, Union
from pathlib import Path

class ResumeParser:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.skills_vocab = self._load_skills_vocab()
    
    def _load_skills_vocab(self) -> set:
        """Load a predefined set of common skills for matching."""
        # This is a basic list - you might want to expand this
        return {
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
            'html', 'css', 'react', 'angular', 'vue', 'django', 'flask', 'node.js', 'express',
            'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'docker', 'kubernetes',
            'git', 'jenkins', 'ci/cd', 'machine learning', 'deep learning', 'tensorflow',
            'pytorch', 'pandas', 'numpy', 'scikit-learn', 'data analysis', 'data science'
        }
    
    def extract_text(self, file_path: Union[str, Path]) -> str:
        """Extract text from PDF, DOCX, or TXT files."""
        file_path = Path(file_path)
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(str(file_path)).lower()
        
        if 'pdf' in file_type:
            return self._extract_from_pdf(file_path)
        elif 'word' in file_type or file_path.suffix.lower() == '.docx':
            return self._extract_from_docx(file_path)
        elif 'text' in file_type or file_path.suffix.lower() == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def _extract_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess the extracted text."""
        # Remove multiple spaces, newlines, and tabs
        text = ' '.join(text.split())
        # Convert to lowercase for consistent processing
        return text.lower()
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        return match.group() if match else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text."""
        # Match various phone number formats
        patterns = [
            r'\+?[\d\s-]{10,}',  # International numbers
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US/Canada numbers
            r'\b\d{5}[\s-]?\d{5}\b'  # Indian numbers
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return None
    
    def extract_links(self, text: str) -> List[str]:
        """Extract website links from text."""
        # Match URLs
        url_pattern = r'https?://[^\s\n\r\(\)\[\]\{\}]+\.\w{2,}(?:/[^\s\n\r\(\)\[\]\{\}]*)?'
        # Match GitHub usernames/links
        github_pattern = r'(?:github\.com/|@)[a-zA-Z0-9-]+'
        # Match LinkedIn profile links
        linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9-]+'
        
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        github = re.findall(github_pattern, text, re.IGNORECASE)
        linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
        
        return list(set(urls + github + linkedin))
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using predefined vocabulary."""
        tokens = set(text.lower().split())
        return list(tokens.intersection(self.skills_vocab))
    
    def extract_education(self, text: str) -> List[str]:
        """Extract education information."""
        # This is a simple implementation - you might want to enhance it
        education = []
        # Look for degree patterns
        degree_keywords = [
            'bachelor', 'bs', 'b\.?s\.?', 'b\.?a\.?', 'master', 'ms', 'm\.?s\.?',
            'ph\.?d', 'doctorate', 'mba', 'b\.?tech', 'm\.?tech', 'b\.?e\.?', 'b\.?sc'
        ]
        
        for keyword in degree_keywords:
            pattern = fr"\b{keyword}[^\n\r]+"
            matches = re.findall(pattern, text, re.IGNORECASE)
            education.extend(matches)
        
        return list(set(education))
    
    def extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience information."""
        # This is a basic implementation - consider using NER or more sophisticated parsing
        experience = []
        # Look for job title and company patterns
        pattern = r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})\s*-\s*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}|present)'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            experience.append({
                'duration': match.group(0),
                'details': text[match.end():match.end()+200].split('\n')[0]  # Get some context
            })
        
        return experience
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract the most likely name from the text."""
        # Process the text with spaCy
        doc = self.nlp(text)
        
        # Look for person names in the first few lines
        first_few_lines = '\n'.join(text.split('\n')[:10])
        doc = self.nlp(first_few_lines)
        
        # Find all person entities
        names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
        
        # Return the first name found, if any
        return names[0] if names else None
    
    def parse_resume(self, file_path: Union[str, Path]) -> Dict:
        """Main method to parse a resume file and extract structured information."""
        # Extract and preprocess text
        raw_text = self.extract_text(file_path)
        text = self.preprocess_text(raw_text)
        
        # Extract various components
        name = self.extract_name(raw_text)  # Use raw text for better name extraction
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        links = self.extract_links(text)
        skills = self.extract_skills(text)
        education = self.extract_education(text)
        experience = self.extract_experience(raw_text)  # Use raw text for better date parsing
        
        # Construct the result dictionary
        result = {
            'name': name,
            'email': email,
            'phone': phone,
            'skills': skills,
            'education': education,
            'experience': experience,
            'links': links,
            'raw_text': raw_text[:500] + '...' if len(raw_text) > 500 else raw_text  # Store first 500 chars for reference
        }
        
        return result

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python resume_parser.py <path_to_resume>")
        sys.exit(1)
    
    parser = ResumeParser()
    try:
        result = parser.parse_resume(sys.argv[1])
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error processing resume: {str(e)}", file=sys.stderr)
        sys.exit(1)

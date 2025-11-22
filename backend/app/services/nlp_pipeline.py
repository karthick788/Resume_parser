"""
NLP Pipeline
Text preprocessing, section detection, and keyword extraction
"""

import re
from typing import Dict, List, Set
from ..utils.helpers import clean_text


class NLPPipeline:
    """NLP processing pipeline for resume text"""
    
    # Common resume section headers
    SECTION_HEADERS = {
        'education': ['education', 'academic', 'qualification', 'degree'],
        'experience': ['experience', 'employment', 'work history', 'professional experience', 'career'],
        'skills': ['skills', 'technical skills', 'core competencies', 'expertise', 'technologies'],
        'projects': ['projects', 'portfolio', 'work samples'],
        'certifications': ['certifications', 'certificates', 'licenses', 'credentials'],
        'summary': ['summary', 'objective', 'profile', 'about'],
        'achievements': ['achievements', 'accomplishments', 'awards', 'honors']
    }
    
    # Comprehensive skill taxonomy
    SKILL_TAXONOMY = {
        'programming': [
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
            'go', 'rust', 'typescript', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash'
        ],
        'web': [
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django',
            'flask', 'fastapi', 'spring', 'asp.net', 'jquery', 'bootstrap', 'tailwind'
        ],
        'database': [
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite',
            'cassandra', 'dynamodb', 'elasticsearch', 'firebase'
        ],
        'cloud': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
            'ci/cd', 'devops', 'heroku', 'digitalocean'
        ],
        'data_science': [
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow',
            'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'tableau',
            'power bi', 'spark', 'hadoop'
        ],
        'mobile': [
            'android', 'ios', 'react native', 'flutter', 'xamarin', 'swift', 'kotlin'
        ],
        'tools': [
            'git', 'github', 'gitlab', 'jira', 'confluence', 'slack', 'vs code',
            'intellij', 'eclipse', 'postman', 'swagger'
        ]
    }
    
    def __init__(self):
        """Initialize NLP pipeline"""
        self.all_skills = self._flatten_skills()
    
    def _flatten_skills(self) -> Set[str]:
        """Flatten skill taxonomy into a set"""
        skills = set()
        for category_skills in self.SKILL_TAXONOMY.values():
            skills.update([s.lower() for s in category_skills])
        return skills
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Basic cleaning
        text = clean_text(text)
        
        # Remove page numbers
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
    
    def detect_sections(self, text: str) -> Dict[str, str]:
        """
        Detect and segment resume sections
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}
        lines = text.split('\n')
        current_section = 'header'
        current_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if line is a section header
            section_found = None
            for section_name, keywords in self.SECTION_HEADERS.items():
                for keyword in keywords:
                    if keyword in line_lower and len(line.split()) <= 5:
                        section_found = section_name
                        break
                if section_found:
                    break
            
            if section_found:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = section_found
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def extract_keywords(self, text: str, custom_keywords: List[str] = None) -> List[Dict[str, str]]:
        """
        Extract keywords and skills from text
        
        Args:
            text: Text to analyze
            custom_keywords: Additional keywords to search for
            
        Returns:
            List of found keywords with categories
        """
        text_lower = text.lower()
        found_keywords = []
        
        # Search for skills from taxonomy
        for category, skills in self.SKILL_TAXONOMY.items():
            for skill in skills:
                # Use word boundaries for exact matching
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_keywords.append({
                        'keyword': skill,
                        'category': category
                    })
        
        # Search for custom keywords
        if custom_keywords:
            for keyword in custom_keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_keywords.append({
                        'keyword': keyword,
                        'category': 'custom'
                    })
        
        return found_keywords
    
    def tokenize(self, text: str) -> List[str]:
        """
        Simple word tokenization
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return [t.strip() for t in tokens if t.strip()]
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text
        
        Args:
            text: Text to process
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def get_skill_category(self, skill: str) -> str:
        """
        Get category for a skill
        
        Args:
            skill: Skill name
            
        Returns:
            Category name or 'other'
        """
        skill_lower = skill.lower()
        for category, skills in self.SKILL_TAXONOMY.items():
            if skill_lower in [s.lower() for s in skills]:
                return category
        return 'other'

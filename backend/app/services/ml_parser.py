"""
ML Parser - Named Entity Recognition using spaCy
"""

import spacy
from typing import Dict, List, Optional
from ..config import settings
from ..utils.regex_patterns import (
    extract_emails, extract_phones, extract_linkedin,
    extract_github, extract_urls
)


class MLParser:
    """Machine Learning-based resume parser using spaCy NER"""
    
    def __init__(self):
        """Initialize ML parser with spaCy model"""
        self.nlp = None
        self.model_loaded = False
    
    def load_model(self):
        """Load spaCy model (lazy loading)"""
        if not self.model_loaded:
            try:
                self.nlp = spacy.load(settings.spacy_model)
                self.model_loaded = True
                print(f"✓ Loaded spaCy model: {settings.spacy_model}")
            except OSError:
                print(f"✗ Model '{settings.spacy_model}' not found. Using en_core_web_sm as fallback.")
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    self.model_loaded = True
                except OSError:
                    print("✗ No spaCy model found. Please install: python -m spacy download en_core_web_sm")
                    self.nlp = None
                    self.model_loaded = False
    
    def extract_entities(self, text: str) -> List[Dict[str, any]]:
        """
        Extract named entities from text
        
        Args:
            text: Text to process
            
        Returns:
            List of entities with labels and confidence
        """
        if not self.model_loaded:
            self.load_model()
        
        if not self.nlp:
            return []
        
        doc = self.nlp(text[:1000000])  # Limit text length for performance
        
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'confidence': self._calculate_confidence(ent)
            })
        
        return entities
    
    def _calculate_confidence(self, entity) -> float:
        """
        Calculate confidence score for entity
        
        Args:
            entity: spaCy entity
            
        Returns:
            Confidence score (0-1)
        """
        # For pre-trained models, we use a heuristic based on entity properties
        # In a custom trained model, this would come from the model itself
        
        # Longer entities tend to be more reliable
        length_score = min(len(entity.text) / 50, 1.0)
        
        # Certain entity types are more reliable
        type_confidence = {
            'PERSON': 0.85,
            'ORG': 0.80,
            'GPE': 0.75,
            'DATE': 0.90,
            'CARDINAL': 0.70,
            'MONEY': 0.85
        }
        type_score = type_confidence.get(entity.label_, 0.70)
        
        # Combine scores
        confidence = (length_score * 0.3 + type_score * 0.7)
        return round(confidence, 2)
    
    def parse_resume(self, text: str, sections: Dict[str, str] = None) -> Dict[str, any]:
        """
        Parse resume and extract structured information
        
        Args:
            text: Resume text
            sections: Pre-segmented sections (optional)
            
        Returns:
            Structured resume data
        """
        if not self.model_loaded:
            self.load_model()
        
        # Extract entities
        entities = self.extract_entities(text)
        
        # Extract using regex patterns
        emails = extract_emails(text)
        phones = extract_phones(text)
        linkedin = extract_linkedin(text)
        github = extract_github(text)
        urls = extract_urls(text)
        
        # Extract person name (first PERSON entity with high confidence)
        person_entities = [e for e in entities if e['label'] == 'PERSON' and e['confidence'] > 0.7]
        name = person_entities[0]['text'] if person_entities else None
        
        # Extract organizations (companies)
        organizations = [e['text'] for e in entities if e['label'] == 'ORG' and e['confidence'] > 0.6]
        
        # Extract locations
        locations = [e['text'] for e in entities if e['label'] in ['GPE', 'LOC'] and e['confidence'] > 0.6]
        
        # Extract dates
        dates = [e['text'] for e in entities if e['label'] == 'DATE']
        
        # Build structured data
        parsed_data = {
            'personal_info': {
                'name': name,
                'email': emails[0] if emails else None,
                'phone': phones[0] if phones else None,
                'linkedin': linkedin,
                'github': github,
                'location': locations[0] if locations else None
            },
            'organizations': list(set(organizations)),
            'locations': list(set(locations)),
            'dates': dates,
            'all_entities': entities,
            'urls': urls
        }
        
        # If sections provided, extract section-specific information
        if sections:
            parsed_data['sections'] = self._parse_sections(sections, entities)
        
        return parsed_data
    
    def _parse_sections(self, sections: Dict[str, str], entities: List[Dict]) -> Dict[str, any]:
        """
        Parse individual sections for specific information
        
        Args:
            sections: Section text dictionary
            entities: Extracted entities
            
        Returns:
            Parsed section data
        """
        section_data = {}
        
        # Parse education section
        if 'education' in sections:
            section_data['education'] = self._parse_education(sections['education'])
        
        # Parse experience section
        if 'experience' in sections:
            section_data['experience'] = self._parse_experience(sections['experience'])
        
        # Parse skills section
        if 'skills' in sections:
            section_data['skills'] = self._parse_skills(sections['skills'])
        
        return section_data
    
    def _parse_education(self, text: str) -> List[Dict[str, str]]:
        """Parse education section"""
        doc = self.nlp(text) if self.nlp else None
        if not doc:
            return []
        
        education_entries = []
        
        # Extract organizations (universities)
        orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
        dates = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
        
        # Simple heuristic: pair organizations with dates
        for i, org in enumerate(orgs):
            entry = {
                'institution': org,
                'date': dates[i] if i < len(dates) else None
            }
            education_entries.append(entry)
        
        return education_entries
    
    def _parse_experience(self, text: str) -> List[Dict[str, str]]:
        """Parse experience section"""
        doc = self.nlp(text) if self.nlp else None
        if not doc:
            return []
        
        experience_entries = []
        
        # Extract organizations (companies)
        orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
        dates = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
        
        for i, org in enumerate(orgs):
            entry = {
                'company': org,
                'date': dates[i] if i < len(dates) else None
            }
            experience_entries.append(entry)
        
        return experience_entries
    
    def _parse_skills(self, text: str) -> List[str]:
        """Parse skills section"""
        # Skills are better extracted using keyword matching (NLPPipeline)
        # This is a simple extraction
        skills = []
        lines = text.split('\n')
        for line in lines:
            # Split by common delimiters
            parts = line.replace(',', ' ').replace('|', ' ').replace(';', ' ').split()
            skills.extend([p.strip() for p in parts if p.strip()])
        
        return list(set(skills))


# Global instance (singleton pattern)
_ml_parser_instance = None


def get_ml_parser() -> MLParser:
    """Get or create ML parser instance"""
    global _ml_parser_instance
    if _ml_parser_instance is None:
        _ml_parser_instance = MLParser()
    return _ml_parser_instance

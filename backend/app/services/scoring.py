"""
Scoring Engine - Candidate Evaluation
"""

from typing import Dict, List, Optional
from ..utils.helpers import get_grade


class ScoringEngine:
    """Calculate candidate scores based on various criteria"""
    
    # Scoring weights
    WEIGHTS = {
        'experience': 0.30,
        'skills': 0.35,
        'education': 0.20,
        'certification': 0.10,
        'project': 0.05
    }
    
    # Education level scores
    EDUCATION_LEVELS = {
        'high school': 1,
        'diploma': 2,
        'bachelor': 3,
        'master': 4,
        'phd': 5,
        'doctorate': 5
    }
    
    def calculate_experience_score(
        self,
        total_years: float,
        required_years: float = 0,
        max_years: float = 10
    ) -> float:
        """
        Calculate experience score
        
        Args:
            total_years: Candidate's total experience
            required_years: Required experience for job
            max_years: Maximum years for full score
            
        Returns:
            Score (0-100)
        """
        if total_years >= max_years:
            return 100.0
        
        if required_years > 0:
            if total_years >= required_years:
                # Bonus for exceeding requirements
                excess = total_years - required_years
                base_score = 80.0
                bonus = min(20.0, (excess / required_years) * 20)
                return base_score + bonus
            else:
                # Penalty for not meeting requirements
                return (total_years / required_years) * 80.0
        else:
            # Linear scoring if no requirement
            return (total_years / max_years) * 100.0
    
    def calculate_skills_score(
        self,
        candidate_skills: List[str],
        required_skills: List[str] = None,
        preferred_skills: List[str] = None
    ) -> float:
        """
        Calculate skills match score
        
        Args:
            candidate_skills: List of candidate's skills
            required_skills: Required skills for job
            preferred_skills: Preferred skills for job
            
        Returns:
            Score (0-100)
        """
        if not candidate_skills:
            return 0.0
        
        # Normalize to lowercase for comparison
        candidate_set = set(s.lower().strip() for s in candidate_skills)
        
        if required_skills or preferred_skills:
            required_set = set(s.lower().strip() for s in (required_skills or []))
            preferred_set = set(s.lower().strip() for s in (preferred_skills or []))
            
            # Calculate matches
            required_match = len(candidate_set & required_set) / len(required_set) if required_set else 1.0
            preferred_match = len(candidate_set & preferred_set) / len(preferred_set) if preferred_set else 0.5
            
            # Weighted combination (required: 70%, preferred: 30%)
            score = (required_match * 0.7 + preferred_match * 0.3) * 100
            return min(100.0, score)
        else:
            # If no requirements, score based on skill count
            return min(100.0, len(candidate_set) * 5)
    
    def calculate_education_score(
        self,
        candidate_education: List[Dict],
        required_level: str = 'bachelor'
    ) -> float:
        """
        Calculate education score
        
        Args:
            candidate_education: List of education entries
            required_level: Required education level
            
        Returns:
            Score (0-100)
        """
        if not candidate_education:
            return 0.0
        
        # Find highest education level
        max_level = 0
        for edu in candidate_education:
            degree = edu.get('degree', '').lower()
            for level_name, level_value in self.EDUCATION_LEVELS.items():
                if level_name in degree:
                    max_level = max(max_level, level_value)
        
        # Get required level value
        required_value = self.EDUCATION_LEVELS.get(required_level.lower(), 3)
        
        if max_level >= required_value:
            # Meets or exceeds requirement
            return min(100.0, (max_level / required_value) * 100)
        else:
            # Below requirement
            return (max_level / required_value) * 80.0
    
    def calculate_certification_score(
        self,
        certifications: List[Dict],
        max_certs: int = 5
    ) -> float:
        """
        Calculate certification score
        
        Args:
            certifications: List of certifications
            max_certs: Maximum certifications for full score
            
        Returns:
            Score (0-100)
        """
        if not certifications:
            return 0.0
        
        cert_count = len(certifications)
        return min(100.0, (cert_count / max_certs) * 100)
    
    def calculate_project_score(
        self,
        projects: List[Dict],
        max_projects: int = 4
    ) -> float:
        """
        Calculate project score
        
        Args:
            projects: List of projects
            max_projects: Maximum projects for full score
            
        Returns:
            Score (0-100)
        """
        if not projects:
            return 0.0
        
        project_count = len(projects)
        return min(100.0, (project_count / max_projects) * 100)
    
    def calculate_total_score(
        self,
        experience_years: float = 0,
        skills: List[str] = None,
        education: List[Dict] = None,
        certifications: List[Dict] = None,
        projects: List[Dict] = None,
        job_requirements: Dict = None
    ) -> Dict[str, any]:
        """
        Calculate overall candidate score
        
        Args:
            experience_years: Total years of experience
            skills: List of skills
            education: List of education entries
            certifications: List of certifications
            projects: List of projects
            job_requirements: Job requirements (optional)
            
        Returns:
            Dictionary with total score and breakdown
        """
        # Extract job requirements if provided
        required_exp = job_requirements.get('min_experience_years', 0) if job_requirements else 0
        required_skills = job_requirements.get('required_skills', []) if job_requirements else []
        preferred_skills = job_requirements.get('preferred_skills', []) if job_requirements else []
        required_edu = job_requirements.get('education_level', 'bachelor') if job_requirements else 'bachelor'
        
        # Calculate individual scores
        exp_score = self.calculate_experience_score(experience_years, required_exp)
        skills_score = self.calculate_skills_score(skills or [], required_skills, preferred_skills)
        edu_score = self.calculate_education_score(education or [], required_edu)
        cert_score = self.calculate_certification_score(certifications or [])
        proj_score = self.calculate_project_score(projects or [])
        
        # Calculate weighted total
        total = (
            exp_score * self.WEIGHTS['experience'] +
            skills_score * self.WEIGHTS['skills'] +
            edu_score * self.WEIGHTS['education'] +
            cert_score * self.WEIGHTS['certification'] +
            proj_score * self.WEIGHTS['project']
        )
        
        return {
            'total_score': round(total, 2),
            'grade': get_grade(total),
            'breakdown': {
                'experience': round(exp_score, 2),
                'skills': round(skills_score, 2),
                'education': round(edu_score, 2),
                'certifications': round(cert_score, 2),
                'projects': round(proj_score, 2)
            },
            'weights': self.WEIGHTS
        }


# Global instance
_scoring_engine_instance = None


def get_scoring_engine() -> ScoringEngine:
    """Get or create scoring engine instance"""
    global _scoring_engine_instance
    if _scoring_engine_instance is None:
        _scoring_engine_instance = ScoringEngine()
    return _scoring_engine_instance

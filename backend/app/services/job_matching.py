"""
Job Matching Service
Match candidates to job descriptions
"""

from typing import Dict, List, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class JobMatcher:
    """Match candidates to job roles"""
    
    def __init__(self):
        """Initialize job matcher"""
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using TF-IDF
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            # Create TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except:
            return 0.0
    
    def calculate_skills_match(
        self,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str] = None
    ) -> Dict[str, any]:
        """
        Calculate skills match between candidate and job
        
        Args:
            candidate_skills: Candidate's skills
            required_skills: Job's required skills
            preferred_skills: Job's preferred skills
            
        Returns:
            Match details including percentage and gaps
        """
        # Normalize skills
        candidate_set = set(s.lower().strip() for s in candidate_skills)
        required_set = set(s.lower().strip() for s in required_skills)
        preferred_set = set(s.lower().strip() for s in (preferred_skills or []))
        
        # Find matches and gaps
        required_matches = candidate_set & required_set
        required_missing = required_set - candidate_set
        preferred_matches = candidate_set & preferred_set
        
        # Calculate match percentage
        total_required = len(required_set)
        total_preferred = len(preferred_set)
        
        if total_required > 0:
            required_match_pct = (len(required_matches) / total_required) * 100
        else:
            required_match_pct = 100.0
        
        if total_preferred > 0:
            preferred_match_pct = (len(preferred_matches) / total_preferred) * 100
        else:
            preferred_match_pct = 0.0
        
        # Overall match (70% required, 30% preferred)
        overall_match = (required_match_pct * 0.7 + preferred_match_pct * 0.3)
        
        return {
            'match_percentage': round(overall_match, 2),
            'required_match_percentage': round(required_match_pct, 2),
            'preferred_match_percentage': round(preferred_match_pct, 2),
            'matching_skills': list(required_matches | preferred_matches),
            'missing_required_skills': list(required_missing),
            'total_required': total_required,
            'total_preferred': total_preferred
        }
    
    def match_candidate_to_job(
        self,
        candidate: Dict,
        job: Dict
    ) -> Dict[str, any]:
        """
        Comprehensive candidate-job matching
        
        Args:
            candidate: Candidate data dictionary
            job: Job role data dictionary
            
        Returns:
            Match results with percentage and recommendations
        """
        # Extract candidate information
        candidate_skills = [s.get('skill_name', '') for s in candidate.get('skills', [])]
        candidate_exp = candidate.get('total_experience_years', 0)
        candidate_summary = candidate.get('summary', '')
        
        # Extract job requirements
        job_required_skills = job.get('required_skills', '').split(',') if isinstance(job.get('required_skills'), str) else job.get('required_skills', [])
        job_preferred_skills = job.get('preferred_skills', '').split(',') if isinstance(job.get('preferred_skills'), str) else job.get('preferred_skills', [])
        job_min_exp = job.get('min_experience_years', 0)
        job_description = job.get('description', '')
        
        # Clean skills lists
        job_required_skills = [s.strip() for s in job_required_skills if s.strip()]
        job_preferred_skills = [s.strip() for s in job_preferred_skills if s.strip()]
        
        # Calculate skills match
        skills_match = self.calculate_skills_match(
            candidate_skills,
            job_required_skills,
            job_preferred_skills
        )
        
        # Calculate experience match
        if candidate_exp >= job_min_exp:
            exp_match = min(100.0, (candidate_exp / max(job_min_exp, 1)) * 100)
        else:
            exp_match = (candidate_exp / max(job_min_exp, 1)) * 80
        
        # Calculate text similarity (if descriptions available)
        text_similarity = 0.0
        if candidate_summary and job_description:
            text_similarity = self.calculate_text_similarity(candidate_summary, job_description) * 100
        
        # Overall match (skills: 60%, experience: 30%, text similarity: 10%)
        overall_match = (
            skills_match['match_percentage'] * 0.60 +
            exp_match * 0.30 +
            text_similarity * 0.10
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            skills_match['missing_required_skills'],
            candidate_exp,
            job_min_exp
        )
        
        return {
            'match_percentage': round(overall_match, 2),
            'skills_match': skills_match,
            'experience_match': round(exp_match, 2),
            'text_similarity': round(text_similarity, 2),
            'recommendations': recommendations,
            'fit_level': self._get_fit_level(overall_match)
        }
    
    def _generate_recommendations(
        self,
        missing_skills: List[str],
        candidate_exp: float,
        required_exp: float
    ) -> List[str]:
        """Generate recommendations for candidate"""
        recommendations = []
        
        if missing_skills:
            recommendations.append(
                f"Consider learning: {', '.join(missing_skills[:5])}"
            )
        
        if candidate_exp < required_exp:
            gap = required_exp - candidate_exp
            recommendations.append(
                f"Gain {gap:.1f} more years of relevant experience"
            )
        
        if not recommendations:
            recommendations.append("Strong match! Consider applying.")
        
        return recommendations
    
    def _get_fit_level(self, match_percentage: float) -> str:
        """Get fit level based on match percentage"""
        if match_percentage >= 80:
            return "Excellent Fit"
        elif match_percentage >= 60:
            return "Good Fit"
        elif match_percentage >= 40:
            return "Moderate Fit"
        else:
            return "Low Fit"
    
    def rank_candidates(
        self,
        candidates: List[Dict],
        job: Dict
    ) -> List[Dict]:
        """
        Rank candidates for a job
        
        Args:
            candidates: List of candidate dictionaries
            job: Job role dictionary
            
        Returns:
            Sorted list of candidates with match scores
        """
        ranked = []
        
        for candidate in candidates:
            match_result = self.match_candidate_to_job(candidate, job)
            ranked.append({
                'candidate': candidate,
                'match_result': match_result
            })
        
        # Sort by match percentage (descending)
        ranked.sort(key=lambda x: x['match_result']['match_percentage'], reverse=True)
        
        return ranked


# Global instance
_job_matcher_instance = None


def get_job_matcher() -> JobMatcher:
    """Get or create job matcher instance"""
    global _job_matcher_instance
    if _job_matcher_instance is None:
        _job_matcher_instance = JobMatcher()
    return _job_matcher_instance

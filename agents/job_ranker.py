"""Job Ranker Agent Module.

Ranks job listings based on user preferences, fit scores, and advanced ranking strategies.

Author: Autonomous JobHunt System
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class JobRanker:
    """Ranks job postings by their relevance and desirability for the user profile."""
    
    def __init__(self, user_profile: Dict[str, Any]):
        """Initializes the JobRanker with user preferences and data.
        
        Args:
            user_profile: Dictionary containing user's skills, experience, and preferences
        """
        self.user_profile = user_profile
        logger.info('JobRanker initialized for user: %s', user_profile.get('name'))
    
    def rank_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranks jobs and returns them in sorted order by overall score.
        
        Args:
            jobs: List of job dictionaries to rank
        Returns:
            List sorted by descending score (most relevant first)
        """
        for job in jobs:
            job['rank_score'] = self._compute_score(job)
        ranked_jobs = sorted(jobs, key=lambda j: j['rank_score'], reverse=True)
        logger.info('Ranked %d jobs', len(jobs))
        return ranked_jobs
    
    def _compute_score(self, job: Dict[str, Any]) -> float:
        """Computes the relevance score for a job.
        (Future logic: Use LLM/embeddings for semantic and preference match.)
        """
        score = 0.0
        # Skill matching
        job_skills = set([s.lower() for s in job.get('skills', [])])
        user_skills = set([s.lower() for s in self.user_profile.get('skills', [])])
        skill_matches = len(job_skills & user_skills)
        score += skill_matches * 5.0
        # Preferred location
        preferred_locations = [loc.lower() for loc in self.user_profile.get('locations', [])]
        job_location = job.get('location', '').lower()
        if any(loc in job_location for loc in preferred_locations):
            score += 10.0
        # Salary boost
        min_salary = self.user_profile.get('min_salary', None)
        job_salary = job.get('salary', None)
        if min_salary and job_salary and job_salary >= min_salary:
            score += 7.5
        # Remote preference
        remote_pref = self.user_profile.get('remote_only', False)
        if remote_pref and (job.get('is_remote', False) or 'remote' in job_location):
            score += 8.0
        # Experience match
        exp_years = self.user_profile.get('experience_years', None)
        job_exp = job.get('experience_years', None)
        if job_exp and exp_years and job_exp <= exp_years:
            score += 3.0
        # TODO: Add LLM-driven match for requirements, soft skills, and interests
        # Suggested approach: Use sentence embeddings or similarity search
        return score
    
    def top_n(self, jobs: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
        """Returns the top N ranked jobs for quick access.
        
        Args:
            jobs: List of already-ranked job dicts
            n: Number of top jobs to return
        Returns:
            List of top jobs
        """
        ranked = self.rank_jobs(jobs)
        return ranked[:n]
    
    def print_ranked_jobs(self, jobs: List[Dict[str, Any]]):
        """Prints a table of ranked jobs for debugging/testing."""
        for idx, job in enumerate(jobs, 1):
            print(f'{idx}. {job.get("title"):<30} | {job.get("company"):<20} | Score: {job.get("rank_score"):.2f}')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Example user profile
    user_profile = {
        'name': 'Alex',
        'skills': ['Python', 'Machine Learning', 'TensorFlow'],
        'locations': ['Remote', 'San Francisco'],
        'min_salary': 100000,
        'remote_only': True,
        'experience_years': 5,
    }
    # Example jobs
    jobs = [
        {'title': 'ML Engineer', 'company': 'Tech Corp', 'location': 'Remote', 'skills': ['Python', 'Machine Learning'], 'salary': 120000, 'is_remote': True, 'experience_years': 3},
        {'title': 'Software Developer', 'company': 'StartUp Inc', 'location': 'New York', 'skills': ['Java', 'Spring'], 'salary': 90000, 'is_remote': False, 'experience_years': 2}
    ]
    ranker = JobRanker(user_profile)
    ranked_jobs = ranker.rank_jobs(jobs)
    ranker.print_ranked_jobs(ranked_jobs)

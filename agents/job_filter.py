"""Job Filter Agent Module.

This module provides intelligent filtering capabilities for job listings
based on user preferences, requirements, and criteria.

Author: Autonomous JobHunt System
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


@dataclass
class FilterCriteria:
    """Data class representing job filtering criteria."""
    
    required_skills: List[str] = None
    preferred_skills: List[str] = None
    locations: List[str] = None
    remote_only: bool = False
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    job_types: List[str] = None  # full-time, part-time, contract, etc.
    company_blacklist: List[str] = None
    company_whitelist: List[str] = None
    posted_within_days: Optional[int] = None
    keywords: List[str] = None
    exclude_keywords: List[str] = None


class JobFilter:
    """Main job filtering agent class.
    
    This class handles filtering of job listings based on various criteria
    including skills, location, salary, experience, and custom preferences.
    """
    
    def __init__(self, criteria: FilterCriteria):
        """Initialize the job filter with filtering criteria.
        
        Args:
            criteria: FilterCriteria object containing filter parameters
        """
        self.criteria = criteria
        self.filtered_count = 0
        self.total_processed = 0
        logger.info("JobFilter initialized with criteria: %s", criteria)
    
    def filter_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter a list of job postings based on criteria.
        
        Args:
            jobs: List of job dictionaries to filter
            
        Returns:
            List of job dictionaries that meet the filtering criteria
        """
        logger.info("Starting job filtering process for %d jobs", len(jobs))
        self.total_processed = len(jobs)
        
        filtered_jobs = []
        for job in jobs:
            if self._meets_criteria(job):
                filtered_jobs.append(job)
        
        self.filtered_count = len(filtered_jobs)
        logger.info("Filtered %d jobs from %d total", self.filtered_count, self.total_processed)
        
        return filtered_jobs
    
    def _meets_criteria(self, job: Dict[str, Any]) -> bool:
        """Check if a single job meets all filtering criteria.
        
        Args:
            job: Job dictionary to evaluate
            
        Returns:
            True if job meets all criteria, False otherwise
        """
        # Check required skills
        if not self._check_required_skills(job):
            return False
        
        # Check location preferences
        if not self._check_location(job):
            return False
        
        # Check salary range
        if not self._check_salary(job):
            return False
        
        # Check experience requirements
        if not self._check_experience(job):
            return False
        
        # Check job type
        if not self._check_job_type(job):
            return False
        
        # Check company filters
        if not self._check_company(job):
            return False
        
        # Check posting date
        if not self._check_posting_date(job):
            return False
        
        # Check keywords
        if not self._check_keywords(job):
            return False
        
        # TODO: Add LLM-based semantic matching for better skill/requirement alignment
        # This will use embeddings to match job descriptions with user preferences
        
        return True
    
    def _check_required_skills(self, job: Dict[str, Any]) -> bool:
        """Verify job has required skills.
        
        Args:
            job: Job dictionary
            
        Returns:
            True if all required skills are present or no requirements set
        """
        if not self.criteria.required_skills:
            return True
        
        job_skills = job.get('skills', []) or []
        job_description = job.get('description', '').lower()
        
        for required_skill in self.criteria.required_skills:
            skill_lower = required_skill.lower()
            # Check if skill is in skills list or description
            if skill_lower not in [s.lower() for s in job_skills] and skill_lower not in job_description:
                logger.debug("Job '%s' missing required skill: %s", job.get('title'), required_skill)
                return False
        
        return True
    
    def _check_location(self, job: Dict[str, Any]) -> bool:
        """Check if job location matches preferences.
        
        Args:
            job: Job dictionary
            
        Returns:
            True if location matches or no location preferences set
        """
        if self.criteria.remote_only:
            is_remote = job.get('is_remote', False) or 'remote' in job.get('location', '').lower()
            return is_remote
        
        if not self.criteria.locations:
            return True
        
        job_location = job.get('location', '').lower()
        for location in self.criteria.locations:
            if location.lower() in job_location:
                return True
        
        return False
    
    def _check_salary(self, job: Dict[str, Any]) -> bool:
        """Check if salary falls within acceptable range.
        
        Args:
            job: Job dictionary
            
        Returns:
            True if salary is acceptable or no salary requirements set
        """
        job_salary = job.get('salary')
        if job_salary is None:
            return True  # Don't filter out jobs without salary info
        
        if self.criteria.min_salary and job_salary < self.criteria.min_salary:
            return False
        
        if self.criteria.max_salary and job_salary > self.criteria.max_salary:
            return False
        
        return True
    
    def _check_experience(self, job: Dict[str, Any]) -> bool:
        """Check if experience requirements are acceptable.
        
        Args:
            job: Job dictionary
            
        Returns:
            True if experience level is acceptable
        """
        job_experience = job.get('experience_years')
        if job_experience is None:
            return True
        
        if self.criteria.experience_min and job_experience < self.criteria.experience_min:
            return False
        
        if self.criteria.experience_max and job_experience > self.criteria.experience_max:
            return False
        
        return True
    
    def _check_job_type(self, job: Dict[str, Any]) -> bool:
        """Check if job type matches preferences.
        
        Args:
            job: Job dictionary
            
        Returns:
            True if job type matches or no preferences set
        """
        if not self.criteria.job_types:
            return True
        
        job_type = job.get('job_type', '').lower()
        return any(jt.lower() in job_type for jt in self.criteria.job_types)
    
    def _check_company(self, job: Dict[str, Any]) -> bool:
        """Check company against whitelist/blacklist.
        
        Args:
            job: Job dictionary
            
        Returns:
            True if company is acceptable
        """
        company = job.get('company', '').lower()
        
        # Check blacklist first
        if self.criteria.company_blacklist:
            if any(blocked.lower() in company for blocked in self.criteria.company_blacklist):
                logger.debug("Job at '%s' filtered due to company blacklist", company)
                return False
        
        # Check whitelist
        if self.criteria.company_whitelist:
            if not any(allowed.lower() in company for allowed in self.criteria.company_whitelist):
                return False
        
        return True
    
    def _check_posting_date(self, job: Dict[str, Any]) -> bool:
        """Check if job was posted within acceptable timeframe.
        
        Args:
            job: Job dictionary
            
        Returns:
            True if posting date is acceptable
        """
        if not self.criteria.posted_within_days:
            return True
        
        posted_date = job.get('posted_date')
        if not posted_date:
            return True  # Don't filter if date not available
        
        if isinstance(posted_date, str):
            try:
                posted_date = datetime.fromisoformat(posted_date)
            except ValueError:
                return True
        
        cutoff_date = datetime.now() - timedelta(days=self.criteria.posted_within_days)
        return posted_date >= cutoff_date
    
    def _check_keywords(self, job: Dict[str, Any]) -> bool:
        """Check for required and excluded keywords.
        
        Args:
            job: Job dictionary
            
        Returns:
            True if keywords match criteria
        """
        description = job.get('description', '').lower()
        title = job.get('title', '').lower()
        combined_text = f"{title} {description}"
        
        # Check required keywords
        if self.criteria.keywords:
            if not any(keyword.lower() in combined_text for keyword in self.criteria.keywords):
                return False
        
        # Check excluded keywords
        if self.criteria.exclude_keywords:
            if any(keyword.lower() in combined_text for keyword in self.criteria.exclude_keywords):
                logger.debug("Job filtered due to excluded keyword")
                return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get filtering statistics.
        
        Returns:
            Dictionary containing filtering statistics
        """
        return {
            'total_processed': self.total_processed,
            'filtered_count': self.filtered_count,
            'filter_rate': self.filtered_count / self.total_processed if self.total_processed > 0 else 0
        }
    
    def apply_llm_filter(self, jobs: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply LLM-based intelligent filtering (future implementation).
        
        This method will use language models to perform semantic matching
        between job requirements and user qualifications.
        
        Args:
            jobs: List of jobs to filter
            user_profile: User profile with skills, experience, preferences
            
        Returns:
            Filtered list of jobs with match scores
        """
        # TODO: Implement LLM-based filtering
        # - Use embeddings to compute semantic similarity
        # - Score jobs based on profile match
        # - Consider soft skills and cultural fit
        # - Analyze job description sentiment and company reviews
        
        logger.warning("LLM filtering not yet implemented, returning original list")
        return jobs


def create_default_criteria(**kwargs) -> FilterCriteria:
    """Factory function to create FilterCriteria with sensible defaults.
    
    Args:
        **kwargs: Override specific criteria fields
        
    Returns:
        FilterCriteria instance
    """
    defaults = {
        'required_skills': [],
        'preferred_skills': [],
        'locations': [],
        'remote_only': False,
        'job_types': ['full-time'],
        'posted_within_days': 30,
    }
    defaults.update(kwargs)
    return FilterCriteria(**defaults)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    criteria = create_default_criteria(
        required_skills=['Python', 'Machine Learning'],
        locations=['San Francisco', 'Remote'],
        remote_only=True,
        min_salary=100000,
        posted_within_days=14
    )
    
    filter_agent = JobFilter(criteria)
    
    # Sample jobs for testing
    sample_jobs = [
        {
            'title': 'ML Engineer',
            'company': 'Tech Corp',
            'location': 'Remote',
            'skills': ['Python', 'Machine Learning', 'TensorFlow'],
            'salary': 120000,
            'is_remote': True,
            'posted_date': datetime.now() - timedelta(days=7)
        },
        {
            'title': 'Software Developer',
            'company': 'StartUp Inc',
            'location': 'New York',
            'skills': ['Java', 'Spring'],
            'salary': 90000,
            'is_remote': False,
            'posted_date': datetime.now() - timedelta(days=20)
        }
    ]
    
    filtered = filter_agent.filter_jobs(sample_jobs)
    print(f"Filtered {len(filtered)} jobs from {len(sample_jobs)} total")
    print(f"Statistics: {filter_agent.get_statistics()}")

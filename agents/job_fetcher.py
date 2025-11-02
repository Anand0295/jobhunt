"""Job Fetcher Agent
Fetches job listings from various sources using web scraping and APIs.
"""
import asyncio
from typing import List, Dict, Optional
import logging
import aiohttp
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class JobFetcherError(Exception):
    """Custom exception for job fetcher errors."""
    pass


class JobFetcher:
    """Fetches job listings from multiple sources."""
    
    def __init__(self, sources: Optional[List[str]] = None):
        """Initialize the job fetcher.
        
        Args:
            sources: List of job board sources to fetch from
        """
        self.sources = sources or ["linkedin", "indeed", "glassdoor"]
        self.jobs: List[Dict] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_jobs(self, keywords: str, location: str = "") -> List[Dict]:
        """Fetch jobs matching the given criteria.
        
        Args:
            keywords: Job search keywords
            location: Job location
            
        Returns:
            List of job dictionaries
        """
        logger.info(f"Fetching jobs for: {keywords} in {location}")
        
        if not self.session:
            async with self:
                return await self._fetch_all_sources(keywords, location)
        
        return await self._fetch_all_sources(keywords, location)
    
    async def _fetch_all_sources(self, keywords: str, location: str) -> List[Dict]:
        """Fetch jobs from all configured sources concurrently.
        
        Args:
            keywords: Job search keywords
            location: Job location
            
        Returns:
            Combined list of jobs from all sources
        """
        tasks = []
        for source in self.sources:
            if source == "linkedin":
                tasks.append(self._fetch_linkedin(keywords, location))
            elif source == "indeed":
                tasks.append(self._fetch_indeed(keywords, location))
            elif source == "glassdoor":
                tasks.append(self._fetch_glassdoor(keywords, location))
            else:
                logger.warning(f"Unknown source: {source}")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_jobs = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching from {self.sources[i]}: {result}")
            else:
                all_jobs.extend(result)
        
        self.jobs = all_jobs
        return all_jobs
    
    async def _fetch_linkedin(self, keywords: str, location: str) -> List[Dict]:
        """Fetch jobs from LinkedIn.
        
        Args:
            keywords: Job search keywords
            location: Job location
            
        Returns:
            List of job dictionaries from LinkedIn
        """
        try:
            # Sample API endpoint structure (actual implementation would need API keys)
            url = "https://api.linkedin.com/v2/jobs"
            params = {
                "keywords": keywords,
                "location": location,
                "count": 25
            }
            
            # Placeholder for actual API call
            # In production, this would use LinkedIn's official API with authentication
            jobs = await self._make_api_request(url, params, "linkedin")
            
            return [self.parse_job_listing(job) for job in jobs]
            
        except Exception as e:
            logger.error(f"LinkedIn fetch error: {e}")
            raise JobFetcherError(f"Failed to fetch from LinkedIn: {e}")
    
    async def _fetch_indeed(self, keywords: str, location: str) -> List[Dict]:
        """Fetch jobs from Indeed.
        
        Args:
            keywords: Job search keywords
            location: Job location
            
        Returns:
            List of job dictionaries from Indeed
        """
        try:
            # Sample API endpoint structure
            url = "https://api.indeed.com/ads/apisearch"
            params = {
                "q": keywords,
                "l": location,
                "limit": 25,
                "format": "json"
            }
            
            jobs = await self._make_api_request(url, params, "indeed")
            
            return [self.parse_job_listing(job) for job in jobs]
            
        except Exception as e:
            logger.error(f"Indeed fetch error: {e}")
            raise JobFetcherError(f"Failed to fetch from Indeed: {e}")
    
    async def _fetch_glassdoor(self, keywords: str, location: str) -> List[Dict]:
        """Fetch jobs from Glassdoor.
        
        Args:
            keywords: Job search keywords
            location: Job location
            
        Returns:
            List of job dictionaries from Glassdoor
        """
        try:
            # Sample API endpoint structure
            url = "https://api.glassdoor.com/api/api.htm"
            params = {
                "action": "jobs-prog",
                "q": keywords,
                "l": location,
                "pagesize": 25
            }
            
            jobs = await self._make_api_request(url, params, "glassdoor")
            
            return [self.parse_job_listing(job) for job in jobs]
            
        except Exception as e:
            logger.error(f"Glassdoor fetch error: {e}")
            raise JobFetcherError(f"Failed to fetch from Glassdoor: {e}")
    
    async def _make_api_request(self, url: str, params: Dict, source: str) -> List[Dict]:
        """Make an API request with error handling and retry logic.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            source: Source name for logging
            
        Returns:
            List of raw job data dictionaries
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if not self.session:
                    raise JobFetcherError("Session not initialized")
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully fetched from {source}")
                        # Return empty list as placeholder for demo
                        # In production, parse data based on source format
                        return self._extract_jobs_from_response(data, source)
                    elif response.status == 429:
                        logger.warning(f"Rate limited by {source}, retrying...")
                        await asyncio.sleep(retry_delay * (attempt + 1))
                    else:
                        logger.error(f"API error from {source}: {response.status}")
                        return []
                        
            except aiohttp.ClientError as e:
                logger.error(f"Network error fetching from {source}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    return []
            except Exception as e:
                logger.error(f"Unexpected error fetching from {source}: {e}")
                return []
        
        return []
    
    def _extract_jobs_from_response(self, data: Dict, source: str) -> List[Dict]:
        """Extract job listings from API response based on source format.
        
        Args:
            data: Raw API response data
            source: Source name to determine parsing strategy
            
        Returns:
            List of job dictionaries
        """
        # This is a placeholder implementation
        # In production, implement source-specific parsing
        if source == "linkedin":
            return data.get("elements", [])
        elif source == "indeed":
            return data.get("results", [])
        elif source == "glassdoor":
            return data.get("response", {}).get("jobListings", [])
        
        return []
    
    def parse_job_listing(self, raw_data: Dict) -> Dict:
        """Parse raw job listing data into standardized format.
        
        Args:
            raw_data: Raw job data from source
            
        Returns:
            Standardized job dictionary
        """
        return {
            "title": raw_data.get("title", ""),
            "company": raw_data.get("company", ""),
            "location": raw_data.get("location", ""),
            "description": raw_data.get("description", ""),
            "url": raw_data.get("url", ""),
            "posted_date": raw_data.get("posted_date", ""),
            "salary": raw_data.get("salary", ""),
            "job_type": raw_data.get("job_type", ""),
            "source": raw_data.get("source", "unknown"),
            "fetched_at": datetime.utcnow().isoformat()
        }
    
    def filter_jobs(self, filters: Dict) -> List[Dict]:
        """Filter jobs based on criteria.
        
        Args:
            filters: Dictionary of filter criteria (e.g., {"job_type": "Full-time"})
            
        Returns:
            Filtered list of jobs
        """
        filtered = self.jobs
        
        for key, value in filters.items():
            if value:
                filtered = [job for job in filtered if self._matches_filter(job, key, value)]
        
        logger.info(f"Filtered {len(filtered)} jobs from {len(self.jobs)} total")
        return filtered
    
    def _matches_filter(self, job: Dict, key: str, value: str) -> bool:
        """Check if a job matches a specific filter criterion.
        
        Args:
            job: Job dictionary
            key: Filter key
            value: Filter value
            
        Returns:
            True if job matches filter
        """
        job_value = job.get(key, "")
        if isinstance(job_value, str):
            return value.lower() in job_value.lower()
        return job_value == value
    
    def deduplicate_jobs(self) -> List[Dict]:
        """Remove duplicate job listings based on title, company, and location.
        
        Returns:
            Deduplicated list of jobs
        """
        seen = set()
        unique_jobs = []
        
        for job in self.jobs:
            key = (job.get("title", ""), job.get("company", ""), job.get("location", ""))
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        logger.info(f"Deduplicated {len(self.jobs)} jobs to {len(unique_jobs)}")
        self.jobs = unique_jobs
        return unique_jobs
    
    def get_job_stats(self) -> Dict:
        """Get statistics about fetched jobs.
        
        Returns:
            Dictionary with job statistics
        """
        return {
            "total_jobs": len(self.jobs),
            "sources": self._count_by_field("source"),
            "companies": self._count_by_field("company"),
            "locations": self._count_by_field("location"),
            "job_types": self._count_by_field("job_type")
        }
    
    def _count_by_field(self, field: str) -> Dict[str, int]:
        """Count occurrences of values in a specific field.
        
        Args:
            field: Field name to count
            
        Returns:
            Dictionary mapping values to counts
        """
        counts = {}
        for job in self.jobs:
            value = job.get(field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts


if __name__ == "__main__":
    # Example usage
    async def main():
        async with JobFetcher() as fetcher:
            jobs = await fetcher.fetch_jobs("Software Engineer", "San Francisco, CA")
            print(f"Found {len(jobs)} jobs")
            
            # Get statistics
            stats = fetcher.get_job_stats()
            print(f"Statistics: {stats}")
    
    asyncio.run(main())

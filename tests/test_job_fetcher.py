"""Tests for JobFetcher agent module.

Tests cover:
- Job fetching from multiple sources (LinkedIn, Indeed, Glassdoor)
- API integration and error handling
- Rate limiting and retry logic
- Data validation and parsing
- Edge cases and failure scenarios
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.job_fetcher import JobFetcher


class TestJobFetcherInitialization:
    """Test JobFetcher initialization and configuration."""
    
    def test_init_with_valid_config(self):
        """Test initialization with valid configuration."""
        fetcher = JobFetcher()
        assert fetcher is not None
        # Add assertions for config loading
    
    def test_init_with_missing_config(self):
        """Test initialization handles missing configuration gracefully."""
        # Test that missing config raises appropriate error or uses defaults
        pass
    
    def test_init_with_invalid_credentials(self):
        """Test initialization with invalid API credentials."""
        # Test that invalid credentials are handled properly
        pass


class TestJobFetching:
    """Test job fetching functionality."""
    
    @pytest.fixture
    def fetcher(self):
        """Create a JobFetcher instance for testing."""
        return JobFetcher()
    
    def test_fetch_jobs_with_valid_query(self, fetcher):
        """Test fetching jobs with valid search query."""
        query = "Python Developer"
        location = "San Francisco"
        # Mock API response
        with patch.object(fetcher, 'fetch_from_linkedin') as mock_fetch:
            mock_fetch.return_value = [
                {"title": "Python Developer", "company": "Tech Corp", "location": "SF"}
            ]
            jobs = fetcher.fetch_jobs(query, location)
            assert len(jobs) > 0
            assert jobs[0]["title"] == "Python Developer"
    
    def test_fetch_jobs_with_empty_query(self, fetcher):
        """Test fetching jobs with empty query string."""
        # Should handle empty query gracefully
        with pytest.raises(ValueError):
            fetcher.fetch_jobs("", "")
    
    def test_fetch_jobs_with_no_results(self, fetcher):
        """Test fetching jobs when no results are found."""
        query = "NonexistentJobTitle12345"
        with patch.object(fetcher, 'fetch_from_linkedin') as mock_fetch:
            mock_fetch.return_value = []
            jobs = fetcher.fetch_jobs(query, "Remote")
            assert jobs == []
    
    def test_fetch_jobs_with_multiple_sources(self, fetcher):
        """Test fetching jobs from multiple sources."""
        # Mock responses from LinkedIn, Indeed, and Glassdoor
        with patch.object(fetcher, 'fetch_from_linkedin') as mock_linkedin, \
             patch.object(fetcher, 'fetch_from_indeed') as mock_indeed, \
             patch.object(fetcher, 'fetch_from_glassdoor') as mock_glassdoor:
            
            mock_linkedin.return_value = [{"source": "LinkedIn", "title": "Job 1"}]
            mock_indeed.return_value = [{"source": "Indeed", "title": "Job 2"}]
            mock_glassdoor.return_value = [{"source": "Glassdoor", "title": "Job 3"}]
            
            jobs = fetcher.fetch_jobs("Developer", "NYC")
            assert len(jobs) >= 3


class TestAPIIntegration:
    """Test API integration with job boards."""
    
    @pytest.fixture
    def fetcher(self):
        return JobFetcher()
    
    def test_linkedin_api_success(self, fetcher):
        """Test successful LinkedIn API call."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"jobs": [{"id": 1, "title": "Developer"}]}
            mock_get.return_value = mock_response
            
            jobs = fetcher.fetch_from_linkedin("Python", "Remote")
            assert len(jobs) > 0
    
    def test_linkedin_api_rate_limit(self, fetcher):
        """Test handling of LinkedIn API rate limiting."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429  # Too Many Requests
            mock_get.return_value = mock_response
            
            # Should handle rate limiting gracefully (retry or backoff)
            jobs = fetcher.fetch_from_linkedin("Python", "Remote")
            assert isinstance(jobs, list)  # Should return empty list or retry
    
    def test_api_timeout(self, fetcher):
        """Test handling of API timeout."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = TimeoutError("Request timed out")
            
            # Should handle timeout gracefully
            jobs = fetcher.fetch_from_linkedin("Python", "Remote")
            assert jobs == []
    
    def test_api_network_error(self, fetcher):
        """Test handling of network errors."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = ConnectionError("Network error")
            
            jobs = fetcher.fetch_from_linkedin("Python", "Remote")
            assert jobs == []
    
    def test_api_invalid_response(self, fetcher):
        """Test handling of malformed API response."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response
            
            jobs = fetcher.fetch_from_linkedin("Python", "Remote")
            assert jobs == []


class TestDataValidation:
    """Test data validation and parsing."""
    
    @pytest.fixture
    def fetcher(self):
        return JobFetcher()
    
    def test_parse_valid_job_data(self, fetcher):
        """Test parsing of valid job data."""
        raw_job = {
            "title": "Python Developer",
            "company": "Tech Corp",
            "location": "San Francisco",
            "salary": "$120k-$150k",
            "description": "Great opportunity..."
        }
        parsed = fetcher.parse_job(raw_job)
        assert parsed["title"] == "Python Developer"
        assert "company" in parsed
    
    def test_parse_job_with_missing_fields(self, fetcher):
        """Test parsing job data with missing required fields."""
        raw_job = {"title": "Developer"}  # Missing company, location, etc.
        parsed = fetcher.parse_job(raw_job)
        # Should handle missing fields gracefully (fill with defaults or None)
        assert parsed is not None
    
    def test_parse_job_with_invalid_data_types(self, fetcher):
        """Test parsing job with invalid data types."""
        raw_job = {
            "title": 123,  # Should be string
            "company": None,
            "salary": "invalid"
        }
        # Should handle type errors gracefully
        parsed = fetcher.parse_job(raw_job)
        assert parsed is not None
    
    def test_deduplicate_jobs(self, fetcher):
        """Test deduplication of job listings."""
        jobs = [
            {"id": "1", "title": "Python Dev", "company": "Corp A"},
            {"id": "1", "title": "Python Dev", "company": "Corp A"},  # Duplicate
            {"id": "2", "title": "Java Dev", "company": "Corp B"}
        ]
        unique_jobs = fetcher.deduplicate_jobs(jobs)
        assert len(unique_jobs) == 2


class TestRateLimiting:
    """Test rate limiting and retry logic."""
    
    @pytest.fixture
    def fetcher(self):
        return JobFetcher()
    
    def test_rate_limit_enforcement(self, fetcher):
        """Test that rate limiting is enforced."""
        # Mock multiple rapid API calls
        with patch('time.sleep') as mock_sleep:
            for i in range(10):
                fetcher.fetch_from_linkedin("Python", "Remote")
            # Should have called sleep to enforce rate limiting
            assert mock_sleep.call_count > 0
    
    def test_exponential_backoff(self, fetcher):
        """Test exponential backoff on failures."""
        with patch('requests.get') as mock_get:
            # Simulate multiple failures then success
            mock_get.side_effect = [
                Mock(status_code=429),
                Mock(status_code=429),
                Mock(status_code=200, json=lambda: {"jobs": []})
            ]
            
            jobs = fetcher.fetch_from_linkedin("Python", "Remote")
            assert mock_get.call_count == 3  # Should retry


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def fetcher(self):
        return JobFetcher()
    
    def test_fetch_with_special_characters(self, fetcher):
        """Test fetching jobs with special characters in query."""
        query = "C++ Developer (Senior) @Company!"
        # Should handle special characters properly
        with patch.object(fetcher, 'fetch_from_linkedin') as mock_fetch:
            mock_fetch.return_value = []
            jobs = fetcher.fetch_jobs(query, "Remote")
            assert isinstance(jobs, list)
    
    def test_fetch_with_very_long_query(self, fetcher):
        """Test fetching jobs with extremely long query string."""
        query = "Developer " * 100  # Very long query
        # Should truncate or handle gracefully
        with pytest.raises(ValueError):
            fetcher.fetch_jobs(query, "Remote")
    
    def test_fetch_with_unicode_characters(self, fetcher):
        """Test fetching jobs with Unicode characters."""
        query = "开发人员"  # Chinese characters
        location = "北京"
        with patch.object(fetcher, 'fetch_from_linkedin') as mock_fetch:
            mock_fetch.return_value = []
            jobs = fetcher.fetch_jobs(query, location)
            assert isinstance(jobs, list)
    
    def test_concurrent_fetching(self, fetcher):
        """Test concurrent job fetching from multiple sources."""
        # Test thread safety and concurrent API calls
        import threading
        results = []
        
        def fetch_wrapper():
            jobs = fetcher.fetch_jobs("Developer", "Remote")
            results.append(jobs)
        
        threads = [threading.Thread(target=fetch_wrapper) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

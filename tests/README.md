# Testing and Coverage Setup

This directory contains comprehensive tests for the JobHunt application, covering all agent modules and their critical logic flows.

## Overview

The test suite is designed to ensure robustness and reliability across all job hunting automation components:

- **test_job_fetcher.py** - Tests for job scraping and API integration
- **test_job_filter.py** - Tests for job filtering logic based on criteria
- **test_job_ranker.py** - Tests for AI-powered job ranking algorithms
- **test_resume_tweaker.py** - Tests for resume customization and optimization
- **test_job_applier.py** - Tests for automated job application submission
- **test_status_tracker.py** - Tests for application tracking and status monitoring

## Setup

### Prerequisites

Install the required testing dependencies:

```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

### Running Tests

#### Run all tests:
```bash
pytest
```

#### Run tests with verbose output:
```bash
pytest -v
```

#### Run specific test file:
```bash
pytest tests/test_job_fetcher.py
```

#### Run tests matching a pattern:
```bash
pytest -k "test_fetch"
```

### Coverage

#### Generate coverage report:
```bash
pytest --cov=agents --cov-report=html
```

#### View coverage in terminal:
```bash
pytest --cov=agents --cov-report=term-missing
```

#### Coverage threshold (fail if below 80%):
```bash
pytest --cov=agents --cov-fail-under=80
```

## Test Structure

Each test module follows this structure:

1. **Unit Tests** - Test individual functions and methods
2. **Integration Tests** - Test component interactions
3. **Edge Case Tests** - Test boundary conditions and error handling
4. **Mock Tests** - Test with mocked external dependencies (APIs, databases, etc.)

## Test Conventions

- Test functions are named with `test_` prefix
- Use descriptive names: `test_fetch_jobs_with_valid_query()`
- Group related tests in classes: `TestJobFetcher`
- Use fixtures for common setup/teardown
- Mock external API calls and file I/O operations
- Test both success and failure scenarios

## Key Edge Cases Covered

### Job Fetcher
- Empty search results
- API rate limiting
- Network timeouts
- Invalid credentials
- Malformed job data

### Job Filter
- Empty job list
- Missing filter criteria
- Invalid filter values
- Multiple conflicting filters

### Job Ranker
- Empty job list
- Missing ranking criteria
- Tie-breaking scenarios
- Invalid score values

### Resume Tweaker
- Missing resume file
- Invalid resume format
- Missing job description
- Template parsing errors

### Job Applier
- Application submission failures
- Missing required fields
- File upload errors
- Authentication failures

### Status Tracker
- Duplicate applications
- Invalid status transitions
- Database connection errors
- Data persistence failures

## Continuous Integration

Tests are automatically run on:
- Every commit to main branch
- All pull requests
- Scheduled nightly builds

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain coverage above 80%
4. Add edge case tests
5. Update this README if needed

## Debugging Failed Tests

```bash
# Run with print statements visible
pytest -s

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)

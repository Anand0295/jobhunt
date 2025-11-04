import pytest
from agents.job_filter import JobFilter

@pytest.fixture
def sample_jobs():
    return [
        {'title': 'Python Developer', 'salary': 120000, 'skills': ['python', 'django'], 'description': 'Remote Python developer', 'type': 'Full-time', 'location': 'Remote'},
        {'title': 'Frontend Engineer', 'salary': 90000, 'skills': ['javascript', 'react'], 'description': 'Onsite frontend role', 'type': 'Part-time', 'location': 'San Francisco'},
        {'title': 'Data Scientist', 'salary': 150000, 'skills': ['python', 'machine learning'], 'description': 'AI, ML, Data', 'type': 'Full-time', 'location': 'New York'},
        {'title': 'Junior Developer', 'salary': 80000, 'skills': ['python'], 'description': 'Entry-level job', 'type': 'Internship', 'location': 'Remote'},
    ]

# Test filtering by salary
def test_filter_by_salary(sample_jobs):
    agent = JobFilter(salary_min=100000)
    filtered = agent.filter_jobs(sample_jobs)
    assert all(j['salary'] >= 100000 for j in filtered)
    assert any(j['title'] == 'Python Developer' for j in filtered)

# Test filtering by required skills
def test_required_skills(sample_jobs):
    agent = JobFilter(skills_required=['machine learning'])
    filtered = agent.filter_jobs(sample_jobs)
    assert any('machine learning' in j['skills'] for j in filtered)
    assert all('machine learning' in j['skills'] for j in filtered)

# Test exclude keywords
def test_exclude_keywords(sample_jobs):
    agent = JobFilter(exclude_keywords=['entry-level'])
    filtered = agent.filter_jobs(sample_jobs)
    assert all('entry-level' not in j['description'].lower() for j in filtered)

# Test filtering by job type
def test_job_type(sample_jobs):
    agent = JobFilter(job_type='Full-time')
    filtered = agent.filter_jobs(sample_jobs)
    assert all(j['type'] == 'Full-time' for j in filtered)

# Test filtering by location
def test_location(sample_jobs):
    agent = JobFilter(location='Remote')
    filtered = agent.filter_jobs(sample_jobs)
    assert all(j['location'] == 'Remote' for j in filtered)

# Edge case: No jobs meet criteria
def test_no_jobs_meet_criteria(sample_jobs):
    agent = JobFilter(skills_required=['java'])
    filtered = agent.filter_jobs(sample_jobs)
    assert filtered == []

# Edge case: Empty job list
def test_empty_job_list():
    agent = JobFilter(salary_min=50000)
    assert agent.filter_jobs([]) == []

# Edge case: Invalid input
@pytest.mark.parametrize('bad_jobs', [None, 'string', 123, {}])
def test_invalid_input(bad_jobs):
    agent = JobFilter()
    with pytest.raises(Exception):
        agent.filter_jobs(bad_jobs)

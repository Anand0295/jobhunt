import pytest
from agents.resume_tweaker import ResumeTweaker

class DummyLLM:
    def tweak_resume(self, resume, job_description):
        return "TWEAKED RESUME"

def test_nlp_keyword_injection():
    tweaker = ResumeTweaker()
    resume = "Experienced Python developer."
    job_description = "Python, Django, REST APIs"
    tweaked = tweaker.tweak(resume, job_description)
    assert "Python" in tweaked and "Django" in tweaked

@pytest.mark.parametrize("resume, job_description, expected_skills", [
    ("Expert in JS and React.", "JavaScript, React, Redux", ["JavaScript", "React", "Redux"]),
    ("Data engineer specializing in SQL.", "SQL, ETL", ["SQL", "ETL"]),
])
def test_tailoring_logic(resume, job_description, expected_skills):
    tweaker = ResumeTweaker()
    tweaked = tweaker.tweak(resume, job_description)
    for skill in expected_skills:
        assert skill in tweaked

def test_skills_experience_matching():
    tweaker = ResumeTweaker()
    resume = "Backend engineer."
    job_description = "Python, Flask, Docker, CI/CD"
    tweaked = tweaker.tweak(resume, job_description)
    assert all(skill in tweaked for skill in ["Python", "Flask", "Docker", "CI/CD"])

def test_future_llm_placeholder():
    tweaker = ResumeTweaker(llm=DummyLLM())
    resume = "Old resume"
    job_description = "AI, ML, NLP"
    tweaked = tweaker.tweak(resume, job_description)
    assert tweaked == "TWEAKED RESUME"

def test_missing_invalid_data():
    tweaker = ResumeTweaker()
    # Missing resume
    tweaked = tweaker.tweak("", "Python")
    assert tweaked is not None and isinstance(tweaked, str)
    # Missing job description
    tweaked = tweaker.tweak("Python dev", "")
    assert tweaked is not None and isinstance(tweaked, str)
    # Both empty
    tweaked = tweaker.tweak("", "")
    assert tweaked is not None and isinstance(tweaked, str)


def test_realistic_output_structure():
    tweaker = ResumeTweaker()
    resume = "Project manager at X Corp."
    job_description = "Project management, Agile, Jira, Scrum"
    tweaked = tweaker.tweak(resume, job_description)
    assert tweaked.startswith("Project manager") or "Project manager" in tweaked
    assert any(word in tweaked for word in ["Agile", "Jira", "Scrum"])
    # Output is string and not empty
    assert isinstance(tweaked, str) and len(tweaked) > 10

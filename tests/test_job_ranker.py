import pytest
from jobhunter.agents.job_ranker import JobRanker

class DummyJob:
    def __init__(self, title, score):
        self.title = title
        self.score = score

    def __repr__(self):
        return f"DummyJob({self.title},{self.score})"

@pytest.fixture
def example_jobs():
    return [
        DummyJob("Job A", 95),
        DummyJob("Job B", 90),
        DummyJob("Job C", 80),
        DummyJob("Job D", 60),
        DummyJob("Job E", 90)
    ]

@pytest.fixture
def ranker():
    return JobRanker()

# Typical ranking test
def test_ranking_by_score(ranker, example_jobs):
    ranked = ranker.rank(example_jobs)
    scores = [j.score for j in ranked]
    assert scores == sorted(scores, reverse=True)
    assert ranked[0].title == "Job A"
    assert "Job E" in [j.title for j in ranked]

# Tie-break handling
def test_tie_break_logic(ranker):
    jobs = [DummyJob("X", 50), DummyJob("Y", 50)]
    ranked = ranker.rank(jobs)
    titles = [j.title for j in ranked]
    assert set(titles) == {"X", "Y"}
    assert len(ranked) == 2

# Empty input
def test_empty_input(ranker):
    ranked = ranker.rank([])
    assert ranked == []

# Edge case: all identical scores
def test_all_equal_scores(ranker):
    jobs = [DummyJob(str(i), 42) for i in range(10)]
    ranked = ranker.rank(jobs)
    assert len(ranked) == 10
    assert set(j.score for j in ranked) == {42}

# Edge case: non-integer, mix types
def test_mixed_score_types(ranker):
    jobs = [DummyJob("Float", 99.9), DummyJob("Int", 100), DummyJob("Neg", -10)]
    ranked = ranker.rank(jobs)
    scores = [j.score for j in ranked]
    assert scores == sorted(scores, reverse=True)
    assert ranked[0].score == 100 or ranked[0].score == 99.9

# Edge case: single job
def test_single_job(ranker):
    jobs = [DummyJob("Solo", 77)]
    ranked = ranker.rank(jobs)
    assert ranked[0].title == "Solo"
    assert ranked[0].score == 77
    assert len(ranked) == 1

# Edge case: None score handling
def test_none_score_handling(ranker):
    jobs = [DummyJob("Present", 70), DummyJob("Missing", None)]
    ranked = ranker.rank(jobs)
    # Ensure None is ranked last or handled gracefully
    assert ranked[-1].title == "Missing" or ranked[-1].score is None

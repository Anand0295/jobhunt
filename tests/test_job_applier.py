import pytest
from jobhunt.job_applier import JobApplier, ApplicationError

class DummyJobSite:
    def __init__(self, method=None, fail=False):
        self.method = method or "easy_apply"
        self.fail = fail
        self.called = False
    def apply(self, job_info):
        self.called = True
        if self.fail:
            raise ApplicationError("Failed to apply")
        return {"status": "success", "method": self.method, "job": job_info}

def test_typical_automation_flow(monkeypatch):
    job_info = {"id": 123, "title": "Engineer"}
    called = {}
    def fake_apply(self, job_info_arg):
        called["ran"] = True
        assert job_info_arg == job_info
        return {"status": "success", "job": job_info_arg}
    monkeypatch.setattr(DummyJobSite, "apply", fake_apply)
    agent = JobApplier(site=DummyJobSite())
    result = agent.apply(job_info)
    assert called["ran"] is True
    assert result["status"] == "success"

@pytest.mark.parametrize(
    "method", ["easy_apply", "email", "redirect"])
def test_application_method_selection(method):
    site = DummyJobSite(method=method)
    agent = JobApplier(site=site)
    job_info = {"id": 1, "title": "Developer"}
    result = agent.apply(job_info, method=method)
    assert result["method"] == method
    assert site.called

def test_dry_run_mode(monkeypatch):
    agent = JobApplier(site=DummyJobSite())
    job_info = {"id": 20, "title": "Tester"}
    def fake_apply(self, job_info_arg):
        raise AssertionError("Should not run in dry-run mode")
    monkeypatch.setattr(DummyJobSite, "apply", fake_apply)
    result = agent.apply(job_info, dry_run=True)
    assert result["status"] == "dry_run"
    assert result["job"] == job_info

def test_error_handling():
    site = DummyJobSite(fail=True)
    agent = JobApplier(site=site)
    job_info = {"id": 99, "title": "QA"}
    with pytest.raises(ApplicationError):
        agent.apply(job_info)

def test_application_record_generation():
    site = DummyJobSite()
    agent = JobApplier(site=site)
    job_info = {"id": 42, "title": "Lead"}
    record = agent.apply(job_info)
    assert record["status"] == "success"
    assert record["job"] == job_info

@pytest.mark.parametrize("missing_field", ["id", "title"])
def test_missing_input_scenarios(missing_field):
    site = DummyJobSite()
    agent = JobApplier(site=site)
    job_info = {"id": 7, "title": "Analyst"}
    del job_info[missing_field]
    with pytest.raises((KeyError, ApplicationError)):
        agent.apply(job_info)

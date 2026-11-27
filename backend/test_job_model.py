from app.models.user import User
from app.models.job import Job

def test_job_model_stores_job_details():
    job = Job(
        user_id=123,
        title="Software Engineer",
        company="Google",
        location="Mountain View, CA",
        job_description="We are looking for a Python developer.",
        source_url="https://example.com/jobs/123",
    )

    assert job.user_id == 123
    assert job.title == "Software Engineer"
    assert job.company == "Google"
    assert job.location == "Mountain View, CA"
    assert job.job_description == "We are looking for a Python developer."
    assert job.source_url == "https://example.com/jobs/123"

def test_job_model_supports_optional_fields():
    job = Job(
        user_id=123,
        title="Backend Engineer",
        company="Amazon",
        job_description="Looking for a backend engineer.",
    )

    assert job.location is None
    assert job.source_url is None
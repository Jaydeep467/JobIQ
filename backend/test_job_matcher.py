from app.services.job_matcher import match_resume_to_job


def test_match_resume_to_job_returns_matched_and_missing_skills():
    resume_data = {
        "skills": ["Python", "React", "FastAPI", "Docker"],
    }

    job_description = """
    We are looking for a Software Engineer experienced in Python,
    FastAPI, AWS, Docker, and Kubernetes.
    """

    result = match_resume_to_job(
        resume_data=resume_data,
        job_description=job_description,
    )

    assert result["matched_skills"] == [
        "Python",
        "FastAPI",
        "Docker",
    ]

    assert result["missing_skills"] == [
        "AWS",
        "Kubernetes",
    ]

    assert result["match_percentage"] == 60.0

def test_match_resume_to_job_returns_zero_when_no_skills_detected():
    resume_data = {
        "skills": ["Python", "React"],
    }

    job_description = """
    We are looking for a motivated software engineer
    with strong communication and problem-solving skills.
    """

    result = match_resume_to_job(
        resume_data=resume_data,
        job_description=job_description,
    )

    assert result["matched_skills"] == []
    assert result["missing_skills"] == []
    assert result["match_percentage"] == 0.0


def test_match_resume_to_job_is_case_insensitive():
    resume_data = {
        "skills": ["python", "FASTAPI", "docker"],
    }

    job_description = """
    Required skills: Python, FastAPI, Docker.
    """

    result = match_resume_to_job(
        resume_data=resume_data,
        job_description=job_description,
    )

    assert result["matched_skills"] == [
        "Python",
        "FastAPI",
        "Docker",
    ]

    assert result["missing_skills"] == []
    assert result["match_percentage"] == 100.0


def test_match_resume_to_job_handles_missing_skills_key():
    resume_data = {}

    job_description = """
    Required skills: Python, AWS, Docker.
    """

    result = match_resume_to_job(
        resume_data=resume_data,
        job_description=job_description,
    )

    assert result["matched_skills"] == []
    assert result["missing_skills"] == [
        "Python",
        "AWS",
        "Docker",
    ]

    assert result["match_percentage"] == 0.0

def test_match_resume_to_job_supports_skill_aliases():
    resume_data = {
        "skills": ["JS", "Node", "Postgres", "K8s"],
    }

    job_description = """
    Required skills: JavaScript, Node.js,
    PostgreSQL, Kubernetes.
    """

    result = match_resume_to_job(
        resume_data=resume_data,
        job_description=job_description,
    )

    assert result["matched_skills"] == [
        "JavaScript",
        "Node.js",
        "PostgreSQL",
        "Kubernetes",
    ]

    assert result["missing_skills"] == []
    assert result["match_percentage"] == 100.0

def test_match_resume_to_job_supports_aliases_in_job_description():
    resume_data = {
        "skills": [
            "JavaScript",
            "Node.js",
            "PostgreSQL",
            "Kubernetes",
        ],
    }

    job_description = """
    Required skills: JS, Node, Postgres, K8s.
    """

    result = match_resume_to_job(
        resume_data=resume_data,
        job_description=job_description,
    )

    assert result["matched_skills"] == [
        "JavaScript",
        "Node.js",
        "PostgreSQL",
        "Kubernetes",
    ]

    assert result["missing_skills"] == []
    assert result["match_percentage"] == 100.0

def test_match_resume_to_job_does_not_duplicate_skills():
    resume_data = {
        "skills": ["JavaScript"],
    }

    job_description = """
    JavaScript is required.
    Experience with JS is preferred.
    Strong JavaScript skills are required.
    """

    result = match_resume_to_job(
        resume_data=resume_data,
        job_description=job_description,
    )

    assert result["matched_skills"] == ["JavaScript"]
    assert result["missing_skills"] == []
    assert result["match_percentage"] == 100.0

def test_match_resume_to_job_returns_skill_statistics():
    resume_data = {
        "skills": ["Python", "FastAPI", "Docker"],
    }

    job_description = """
    Required skills: Python, FastAPI, Docker, AWS, Kubernetes.
    """

    result = match_resume_to_job(
        resume_data=resume_data,
        job_description=job_description,
    )

    assert result["total_skills"] == 5
    assert result["matched_count"] == 3
    assert result["missing_count"] == 2
    assert result["match_percentage"] == 60.0
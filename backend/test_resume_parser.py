import pytest
from app.services.resume_parser import parse_resume, normalize_text


def test_normalize_text():
    text = "  Python   Developer \n\n React   Developer  "

    result = normalize_text(text)

    assert result == "Python Developer\n\nReact Developer"


def test_parse_resume_extracts_skills():
    resume_text = """
    SKILLS
    Python, Java, React, PostgreSQL, Docker, AWS
    """

    result = parse_resume(resume_text)

    skills = result["skills"]

    assert "Python" in skills
    assert "Java" in skills
    assert "React" in skills
    assert "PostgreSQL" in skills
    assert "Docker" in skills
    assert "AWS" in skills


def test_parse_resume_extracts_education():
    resume_text = """
    EDUCATION

    M.S. Computer Science
    Arizona State University
    GPA: 3.80 / 4.00
    Aug 2023 – May 2025

    B.E. Electronics & Computer Science
    Mumbai University
    GPA: 9.28 / 10.00
    Aug 2019 – May 2023
    """

    result = parse_resume(resume_text)

    education = result["education"]
    # print("\nEDUCATION PARSED:", education)

    assert len(education) >= 2
    assert "Arizona State University" in education[0]["university"]
    assert "Mumbai University" in education[1]["university"]


def test_parse_resume_extracts_experience():
    resume_text = """
    EXPERIENCE

    SKYFARER ACADEMY | Full Stack Software Engineer | San Diego, CA
    Apr 2025 – Present
    - Built REST APIs using Python and Django.
    - Improved API response times by 20%.

    MATROID | Software Developer (Contract)
    May 2024 – Jan 2025
    - Developed software features.
    """

    result = parse_resume(resume_text)

    experience = result["experience"]
    # print("\nEXPERIENCE PARSED:", experience)

    assert len(experience) >= 2
    assert "SKYFARER ACADEMY" in experience[0]["company"]
    assert "MATROID" in experience[1]["company"]




def test_parse_resume_handles_empty_text():
    with pytest.raises(ValueError, match="Resume text cannot be empty"):
        parse_resume("")


def test_parse_resume_handles_missing_sections():
    resume_text = """
    John Doe
    Software Engineer
    Experienced developer specializing in backend systems.
    """

    result = parse_resume(resume_text)

    assert isinstance(result, dict)
    assert result["education"] == []
    assert result["experience"] == []
    assert isinstance(result["skills"], list)

def test_parse_resume_extracts_projects():
    resume_text = """
    PROJECTS

    LLM INFERENCE PIPELINE — GPU-Accelerated Serving
    Python, PyTorch, CUDA, Flask
    Engineered a GPU-accelerated LLM serving pipeline.
    Reduced inference latency by 25%.

    SHOPFLOW — Full Stack E-Commerce Platform
    React, TypeScript, Node.js, PostgreSQL
    Built a full-stack e-commerce application.
    """

    result = parse_resume(resume_text)

    projects = result["projects"]

    assert isinstance(projects, list)
    assert len(projects) >= 2

    assert "LLM INFERENCE PIPELINE" in projects[0]["name"]
    assert "Python" in projects[0]["technologies"]

    assert "SHOPFLOW" in projects[1]["name"]
    assert "React" in projects[1]["technologies"]

def test_parse_resume_handles_project_without_technologies():
    resume_text = """
    PROJECTS

    PERSONAL PORTFOLIO — Web Application
    Designed and built a personal portfolio website.
    Added responsive layouts and animations.
    """

    result = parse_resume(resume_text)

    projects = result["projects"]

    assert len(projects) == 1
    assert projects[0]["name"] == "PERSONAL PORTFOLIO"
    assert projects[0]["technologies"] == []
    assert "personal portfolio website" in projects[0]["description"].lower()

def test_parse_resume_handles_empty_projects_section():
    resume_text = """
    PROJECTS

    EXPERIENCE

    Software Engineer | Company A
    Jan 2024 – Present
    Built software applications.
    """

    result = parse_resume(resume_text)

    assert result["projects"] == []
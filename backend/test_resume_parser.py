import pytest
from app.services.resume_parser import parse_resume, normalize_text, extract_sections

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

def test_parse_resume_extracts_project_with_pipe_separator():
    resume_text = """
    PROJECTS

    SHOPFLOW | Full Stack E-Commerce Platform
    React, TypeScript, Node.js, PostgreSQL
    Built a full-stack e-commerce application.
    """

    result = parse_resume(resume_text)

    projects = result["projects"]

    assert len(projects) == 1
    assert projects[0]["name"] == "SHOPFLOW"
    assert projects[0]["subtitle"] == "Full Stack E-Commerce Platform"
    assert "React" in projects[0]["technologies"]

def test_parse_resume_extracts_certifications():
    resume_text = """
    CERTIFICATIONS

    Data Scientist's Toolbox — Coursera
    Data Structures with Python — Coursera
    CS50 AI — Harvard
    """

    result = parse_resume(resume_text)

    certifications = result["certifications"]

    assert isinstance(certifications, list)
    assert len(certifications) == 3

    assert certifications[0]["name"] == "Data Scientist's Toolbox"
    assert certifications[0]["issuer"] == "Coursera"

    assert certifications[1]["name"] == "Data Structures with Python"
    assert certifications[1]["issuer"] == "Coursera"

    assert certifications[2]["name"] == "CS50 AI"
    assert certifications[2]["issuer"] == "Harvard"

def test_parse_resume_handles_certifications_without_issuer():
    resume_text = """
    CERTIFICATIONS

    CS50 AI
    Data Structures and Algorithms
    AWS Cloud Practitioner
    """

    result = parse_resume(resume_text)

    certifications = result["certifications"]

    assert len(certifications) == 3

    assert certifications[0]["name"] == "CS50 AI"
    assert certifications[0]["issuer"] == ""

    assert certifications[1]["name"] == "Data Structures and Algorithms"
    assert certifications[1]["issuer"] == ""

    assert certifications[2]["name"] == "AWS Cloud Practitioner"
    assert certifications[2]["issuer"] == ""

def test_parse_resume_handles_empty_certifications_section():
    resume_text = """
    CERTIFICATIONS

    PROJECTS

    SHOPFLOW — Full Stack E-Commerce Platform
    React, TypeScript
    Built an e-commerce application.
    """

    result = parse_resume(resume_text)

    assert result["certifications"] == []

def test_parse_resume_recognizes_professional_experience_heading():
    resume_text = """
    PROFESSIONAL EXPERIENCE

    Skyfarer Academy | Full Stack Software Engineer | San Diego, CA
    Apr 2025 – Present
    Built and maintained full-stack features.
    """

    result = parse_resume(resume_text)

    assert len(result["experience"]) == 1
    assert result["experience"][0]["company"] == "Skyfarer Academy"
    assert result["experience"][0]["title"] == "Full Stack Software Engineer"

def test_parse_resume_recognizes_work_experience_heading():
    resume_text = """
    WORK EXPERIENCE

    Skyfarer Academy | Full Stack Software Engineer | San Diego, CA
    Apr 2025 – Present
    Built and maintained full-stack features.
    """

    result = parse_resume(resume_text)

    assert len(result["experience"]) == 1
    assert result["experience"][0]["company"] == "Skyfarer Academy"
    assert result["experience"][0]["title"] == "Full Stack Software Engineer"

def test_parse_resume_recognizes_employment_heading():
    resume_text = """
    EMPLOYMENT

    Skyfarer Academy | Full Stack Software Engineer | San Diego, CA
    Apr 2025 – Present
    Built and maintained full-stack features.
    """

    result = parse_resume(resume_text)

    assert len(result["experience"]) == 1
    assert result["experience"][0]["company"] == "Skyfarer Academy"
    assert result["experience"][0]["title"] == "Full Stack Software Engineer"

def test_parse_resume_recognizes_core_competencies_heading():
    resume_text = """
    CORE COMPETENCIES

    Python, Java, React, SQL, Docker
    """

    result = parse_resume(resume_text)

    assert "Python" in result["skills"]
    assert "Java" in result["skills"]
    assert "React" in result["skills"]
    assert "SQL" in result["skills"]
    assert "Docker" in result["skills"]

def test_extract_sections_recognizes_core_competencies():
    text = """
    CORE COMPETENCIES

    Python, Java, React, SQL, Docker
    """

    sections = extract_sections(text)

    assert "skills" in sections
    assert "Python, Java, React, SQL, Docker" in sections["skills"]

def test_extract_sections_recognizes_career_summary():
    text = """
    CAREER SUMMARY

    Full Stack Software Engineer with experience in Python,
    React, Django, and AWS.
    """

    sections = extract_sections(text)

    assert "summary" in sections
    assert "Full Stack Software Engineer" in sections["summary"]

@pytest.mark.parametrize(
    "heading, expected_section",
    [
        ("ABOUT ME", "summary"),
        ("CAREER SUMMARY", "summary"),
        ("PERSONAL PROFILE", "summary"),
        ("PERSONAL SUMMARY", "summary"),
        ("EXECUTIVE SUMMARY", "summary"),

        ("CORE COMPETENCIES", "skills"),
        ("KEY SKILLS", "skills"),
        ("CORE SKILLS", "skills"),
        ("SKILL SET", "skills"),
        ("TECHNOLOGY STACK", "skills"),
        ("TOOLS & TECHNOLOGIES", "skills"),

        ("EDUCATIONAL BACKGROUND", "education"),
        ("ACADEMIC HISTORY", "education"),
        ("EDUCATION & TRAINING", "education"),
        ("QUALIFICATIONS", "education"),

        ("EMPLOYMENT", "experience"),
        ("EMPLOYMENT EXPERIENCE", "experience"),
        ("CAREER HISTORY", "experience"),
        ("RELEVANT EXPERIENCE", "experience"),
        ("PROFESSIONAL WORK EXPERIENCE", "experience"),

        ("SELECTED PROJECTS", "projects"),
        ("PROJECT WORK", "projects"),
        ("KEY PROJECTS", "projects"),
        ("PROJECT PORTFOLIO", "projects"),

        ("PROFESSIONAL CERTIFICATIONS", "certifications"),
        ("LICENSES & CERTIFICATIONS", "certifications"),
        ("CERTIFICATIONS & LICENSES", "certifications"),
    ],
)
def test_extract_sections_recognizes_common_heading_variations(
    heading, expected_section
):
    text = f"""
    {heading}

    Sample content for this section.
    """

    sections = extract_sections(text)

    assert expected_section in sections
    assert "Sample content for this section." in sections[expected_section]
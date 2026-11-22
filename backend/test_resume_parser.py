import pytest
# from app.services.resume_parser import parse_resume, normalize_text, extract_sections
from app.services.resume_parser import (
    parse_resume,
    normalize_text,
    extract_sections,
    extract_skills,
    extract_contact_info,
)

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

@pytest.mark.parametrize(
    "text, expected",
    [
        # Case-insensitive matching
        ("I use PYTHON and python.", ["Python"]),

        # Java should not accidentally match JavaScript
        ("I am a JavaScript developer.", ["JavaScript"]),
        ("I use Java and JavaScript.", ["Java", "JavaScript"]),

        # Duplicate skills should only appear once
        ("Python Python Python Python", ["Python"]),

        # Special characters
        ("I know C++ and C#.", ["C++", "C#"]),

        # Partial-word false positives
        ("I enjoy Reactively building interfaces.", []),

        # Multiple valid skills
        (
            "Python, React, PostgreSQL, and Docker are my tools.",
            ["Python", "PostgreSQL", "React", "Docker"],
        ),
    ],
)
def test_extract_skills_handles_edge_cases(text, expected):
    assert extract_skills(text) == expected

@pytest.mark.parametrize(
    "skill",
    [
        "HTML",
        "CSS",
        "Tailwind CSS",
        "Bootstrap",
        "Vue.js",
        "Angular",
        "Redux",
        "Express.js",
        "GraphQL",
        "Microservices",
        "WebSockets",
        "Microsoft Azure",
        "Google Cloud Platform",
        "CI/CD",
        "GitHub Actions",
        "Linux",
        "Bash",
        "Terraform",
        "SQLite",
        "DynamoDB",
        "Elasticsearch",
        "Apache Spark",
        "Airflow",
        "Data Engineering",
        "Data Analysis",
        "Generative AI",
        "Large Language Models",
        "RAG",
        "Computer Vision",
        "Hugging Face",
        "OpenAI API",
        "Data Structures",
        "Algorithms",
        "Object-Oriented Programming",
        "System Design",
        "Software Engineering",
        "Agile",
        "Scrum",
        "Jira",
        "Postman",
        "Figma",
        "Power BI",
        "Excel",
    ],
)
def test_extract_skills_recognizes_expanded_skill_keywords(skill):
    assert extract_skills(skill) == [skill]

def test_extract_skills_does_not_extract_css_from_tailwind_css():
    assert extract_skills("Tailwind CSS") == ["Tailwind CSS"]

def test_extract_skills_detects_standalone_css_with_tailwind():
    assert extract_skills("Tailwind CSS and CSS") == ["CSS", "Tailwind CSS"]

@pytest.mark.parametrize(
    "alias,expected_skill",
    [
        ("JS", "JavaScript"),
        ("javascript", "JavaScript"),
        ("TS", "TypeScript"),
        ("ML", "Machine Learning"),
        ("DL", "Deep Learning"),
        ("AI", "Artificial Intelligence"),
        ("GCP", "Google Cloud Platform"),
        ("K8s", "Kubernetes"),
        ("OOP", "Object-Oriented Programming"),
    ],
)
def test_extract_skills_recognizes_aliases(alias, expected_skill):
    assert expected_skill in extract_skills(alias)

def test_extract_skills_returns_canonical_name_for_alias():
    skills = extract_skills("JS, TS, ML, GCP, K8s")

    assert "JavaScript" in skills
    assert "TypeScript" in skills
    assert "Machine Learning" in skills
    assert "Google Cloud Platform" in skills
    assert "Kubernetes" in skills

    assert "JS" not in skills
    assert "TS" not in skills
    assert "ML" not in skills
    assert "GCP" not in skills
    assert "K8s" not in skills

def test_extract_skills_does_not_extract_js_from_vue_js():
    assert extract_skills("Vue.js") == ["Vue.js"]


def test_extract_skills_does_not_extract_js_from_express_js():
    assert extract_skills("Express.js") == ["Express.js"]


def test_extract_skills_does_not_extract_ai_from_generative_ai():
    assert extract_skills("Generative AI") == ["Generative AI"]


def test_extract_skills_extracts_alias_when_standalone():
    skills = extract_skills("Vue.js, JS, Express.js, AI")

    assert "Vue.js" in skills
    assert "JavaScript" in skills
    assert "Express.js" in skills
    assert "Artificial Intelligence" in skills
    assert "Generative AI" not in skills

def test_extract_contact_info_extracts_email():
    text = "Contact: jaydeep.patil@example.com"

    result = extract_contact_info(text)

    assert result["email"] == "jaydeep.patil@example.com"


def test_extract_contact_info_extracts_phone():
    text = "Phone: +1 (555) 123-4567"

    result = extract_contact_info(text)

    assert result["phone"] == "+1 (555) 123-4567"


def test_extract_contact_info_extracts_linkedin():
    text = "LinkedIn: https://www.linkedin.com/in/jaydeep-patil"

    result = extract_contact_info(text)

    assert result["linkedin"] == "https://www.linkedin.com/in/jaydeep-patil"


def test_extract_contact_info_extracts_github():
    text = "GitHub: https://github.com/Jaydeep467"

    result = extract_contact_info(text)

    assert result["github"] == "https://github.com/Jaydeep467"


def test_extract_contact_info_handles_missing_fields():
    text = "Experienced software engineer with Python skills."

    result = extract_contact_info(text)

    assert result == {
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
    }

def test_parse_resume_includes_contact_info():
    text = """
    Jaydeep Patil
    jaydeep.patil@example.com
    +1 (555) 123-4567
    https://linkedin.com/in/jaydeep-patil
    https://github.com/Jaydeep467

    SUMMARY
    Software Engineer with Python experience.

    SKILLS
    Python, JavaScript, React

    EDUCATION
    Arizona State University
    Master of Science in Computer Science
    """

    result = parse_resume(text)

    assert result["contact"] == {
        "email": "jaydeep.patil@example.com",
        "phone": "+1 (555) 123-4567",
        "linkedin": "https://linkedin.com/in/jaydeep-patil",
        "github": "https://github.com/Jaydeep467",
    }


def test_parse_resume_contact_info_handles_missing_fields():
    text = """
    SUMMARY
    Experienced software engineer.

    SKILLS
    Python, Java
    """

    result = parse_resume(text)

    assert result["contact"] == {
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
    }

def test_extract_contact_info_extracts_indian_phone():
    text = "Phone: +91 98765 43210"
    result = extract_contact_info(text)

    assert result["phone"] == "+91 98765 43210"


def test_extract_contact_info_extracts_linkedin_without_scheme():
    text = "linkedin.com/in/jaydeep-patil"
    result = extract_contact_info(text)

    assert result["linkedin"] == "linkedin.com/in/jaydeep-patil"


def test_extract_contact_info_extracts_github_without_scheme():
    text = "github.com/Jaydeep467"
    result = extract_contact_info(text)

    assert result["github"] == "github.com/Jaydeep467"

def test_extract_contact_info_removes_trailing_url_punctuation():
    text = """
    LinkedIn: linkedin.com/in/jaydeep-patil.
    GitHub: github.com/Jaydeep467,
    """

    result = extract_contact_info(text)

    assert result["linkedin"] == "linkedin.com/in/jaydeep-patil"
    assert result["github"] == "github.com/Jaydeep467"


def test_extract_contact_info_preserves_phone_format():
    text = "Phone: +91-98765-43210"

    result = extract_contact_info(text)

    assert result["phone"] == "+91-98765-43210"
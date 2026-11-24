import re


SKILL_CATALOG = [
    "Python",
    "FastAPI",
    "React",
    "JavaScript",
    "TypeScript",
    "Node.js",
    "AWS",
    "Docker",
    "Kubernetes",
    "PostgreSQL",
    "MongoDB",
    "SQL",
    "Java",
    "C++",
]

SKILL_ALIASES = {
    "js": "javascript",
    "node": "node.js",
    "nodejs": "node.js",
    "reactjs": "react",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "k8s": "kubernetes",
}

def extract_job_skills(job_description: str) -> list[str]:
    detected_skills = []

    for skill in SKILL_CATALOG:
        aliases = [
            alias
            for alias, canonical in SKILL_ALIASES.items()
            if canonical == skill.lower()
        ]

        search_terms = [skill, *aliases]

        matches = []

        for term in search_terms:
            pattern = rf"(?<!\w){re.escape(term)}(?!\w)"

            match = re.search(
                pattern,
                job_description,
                re.IGNORECASE,
            )

            if match:
                matches.append(match.start())

        if matches:
            detected_skills.append((skill, min(matches)))

    detected_skills.sort(key=lambda item: item[1])

    return [skill for skill, _ in detected_skills]


def match_resume_to_job(
    resume_data: dict,
    job_description: str,
) -> dict:
    resume_skills = resume_data.get("skills", [])

    normalized_resume_skills = {
        normalize_skill(skill)
        for skill in resume_skills
    }

    job_skills = extract_job_skills(job_description)

    matched_skills = []
    missing_skills = []

    for skill in job_skills:
        if normalize_skill(skill) in normalized_resume_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    match_percentage = (
        len(matched_skills) / len(job_skills) * 100
        if job_skills
        else 0.0
    )

    total_skills = len(job_skills)
    matched_count = len(matched_skills)
    missing_count = len(missing_skills)

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": round(match_percentage, 2),
        "total_skills": total_skills,
        "matched_count": matched_count,
        "missing_count": missing_count,
    }

def normalize_skill(skill: str) -> str:
    normalized = skill.strip().lower()

    return SKILL_ALIASES.get(normalized, normalized)

import re
from typing import Any


SKILL_KEYWORDS = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "C#",
    "SQL",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "React",
    "Next.js",
    "Node.js",
    "FastAPI",
    "Django",
    "Flask",
    "Spring Boot",
    "AWS",
    "Docker",
    "Kubernetes",
    "Git",
    "TensorFlow",
    "PyTorch",
    "Scikit-learn",
    "Pandas",
    "NumPy",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "REST APIs",
    "Redis",
    "Kafka",
]

SECTION_ALIASES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "career objective",
        "objective",
    ],
    "education": [
        "education",
        "academic background",
        "academic qualifications",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
    ],
    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "project experience",
    ],
    "skills": [
        "skills",
        "technical skills",
        "technologies",
        "technical expertise",
        "technical proficiencies",
    ],
    "certifications": [
        "certifications",
        "certifications & activities",
        "certifications and activities",
        "certificates",
        "activities",
        "awards and certifications",
    ],
}


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving section line breaks."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = [
        re.sub(r"[ \t]+", " ", line).strip()
        for line in text.split("\n")
    ]

    return "\n".join(lines).strip()


def extract_sections(text: str) -> dict[str, str]:
    """Extract common resume sections using heading-based boundaries."""
    lines = normalize_text(text).splitlines()
    aliases = {
        alias.casefold(): section
        for section, names in SECTION_ALIASES.items()
        for alias in names
    }

    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in lines:
        heading = line.strip().rstrip(":").strip()
        matched_section = aliases.get(heading.casefold())

        if matched_section:
            current_section = matched_section
            sections.setdefault(current_section, [])
            continue

        if current_section:
            sections[current_section].append(line)

    return {
        section: "\n".join(content).strip()
        for section, content in sections.items()
    }


def extract_skills(text: str) -> list[str]:
    """Find known technology and skill keywords in the supplied text."""
    normalized = normalize_text(text).casefold()
    found: list[str] = []

    for skill in SKILL_KEYWORDS:
        pattern = rf"(?<!\w){re.escape(skill.casefold())}(?!\w)"
        if re.search(pattern, normalized):
            found.append(skill)

    return found


def parse_education(education_text: str) -> list[dict[str, str | None]]:
    """Split education text into individual degree records."""
    if not education_text.strip():
        return []

    entries = re.split(
        r"(?m)(?=^(?:M\.?S\.?|B\.?E\.?|B\.?S\.?|M\.?S\.?C\.?|"
        r"B\.?S\.?C\.?|M\.?E\.?|M\.?TECH|B\.?TECH)\b)",
        education_text.strip(),
    )

    records = []

    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue

        degree_match = re.search(
            r"^(M\.?S\.?|B\.?E\.?|B\.?S\.?|M\.?S\.?C\.?|"
            r"B\.?S\.?C\.?|M\.?E\.?|M\.?TECH|B\.?TECH)"
            r"[^\n|]*",
            entry,
            re.IGNORECASE,
        )

        gpa_match = re.search(
            r"GPA:\s*([0-9.]+\s*/\s*[0-9.]+)",
            entry,
            re.IGNORECASE,
        )

        date_match = re.search(
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"\w*\s+\d{4})\s*[–-]\s*"
            r"((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"\w*\s+)?\d{4}|Present)",
            entry,
            re.IGNORECASE,
        )
        
        # university_match = re.search(
        #     r"\|\s*([^|\n]+?)\s*\|\s*GPA:",
        #     entry,
        #     re.IGNORECASE,
        # )
                # Extract university from either pipe-separated or multiline formats.
        university = None
        lines = [line.strip() for line in entry.splitlines() if line.strip()]

        for line in lines:
            # Format: Degree | University | GPA: ...
            if "|" in line:
                parts = [part.strip() for part in line.split("|")]

                for part in parts:
                    if (
                        part
                        and not re.search(r"\bGPA\b", part, re.IGNORECASE)
                        and not re.search(
                            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                            r"\w*\s+\d{4}\b",
                            part,
                            re.IGNORECASE,
                        )
                    ):
                        if part != degree_match.group(0).strip() if degree_match else True:
                            university = part
                            break

                if university:
                    break

            # Format: degree and university on separate lines.
            elif (
                degree_match
                and line != degree_match.group(0).strip()
                and not re.search(r"\bGPA\b", line, re.IGNORECASE)
                and not re.search(
                    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                    r"\w*\s+\d{4}\b",
                    line,
                    re.IGNORECASE,
                )
            ):
                university = line
                break

        records.append(
            {
                "degree": degree_match.group(0).strip()
                if degree_match else None,
                # "university": (
                #     university_match.group(1).strip()
                #     if university_match
                #     else None
                # ),
                "university": university,
                "gpa": gpa_match.group(1).strip()
                if gpa_match else None,
                "dates": date_match.group(0).strip()
                if date_match else None,
                "raw_text": entry,
            }
        )

    return records


# def parse_experience(experience_text: str) -> list[dict[str, str | None]]:
    """Extract basic work experience entries from resume text."""
    if not experience_text.strip():
        return []

    lines = normalize_text(experience_text).splitlines()
    entries = []
    current_entry = None

    # Identify lines that look like job headings containing date ranges.
    
    heading_pattern = re.compile(
        r"^(?P<company>.+?)\s*\|\s*"
        r"(?P<title>.+?)"
        r"(?:\s*\|\s*(?P<location>.+?))?"
        r"\s+(?P<dates>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\w*\s+\d{4}\s*[–-]\s*"
        r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\w*\s+\d{4}|Present))$",
        re.IGNORECASE,
    )

    for line in lines:
        match = heading_pattern.match(line.strip())

        if match:
            if current_entry:
                entries.append(current_entry)

            current_entry = {
                "company": match.group("company").strip(),
                "title": match.group("title").strip(),
                "location": (
                    match.group("location").strip()
                    if match.group("location")
                    else None
                ),
                "dates": match.group("dates").strip(),
                "achievements": [],
            }
        elif current_entry and line.strip():
            current_entry["achievements"].append(line.strip())

    if current_entry:
        entries.append(current_entry)

    for entry in entries:
        entry["achievements"] = "\n".join(entry["achievements"])

    return entries
def parse_experience(
    experience_text: str,
) -> list[dict[str, str | None]]:
    """Extract work experience entries from resume text."""

    if not experience_text.strip():
        return []

    lines = normalize_text(experience_text).splitlines()

    entries = []
    current_entry = None

    date_pattern = re.compile(
        r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\w*\s+\d{4})\s*[–-]\s*"
        r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\w*\s+\d{4}|\d{4}|Present)",
        re.IGNORECASE,
    )

    def parse_heading(heading: str, dates: str):
        parts = [part.strip() for part in heading.split("|")]

        if len(parts) < 2:
            return None

        company = parts[0]
        title = parts[1]
        location = parts[2] if len(parts) >= 3 else None

        return {
            "company": company,
            "title": title,
            "location": location,
            "dates": dates,
            "achievements": [],
        }

    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # Format 1:
        # Company | Title | Location
        # Apr 2025 – Present
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()

            if date_pattern.fullmatch(next_line):
                new_entry = parse_heading(line, next_line)

                if new_entry:
                    if current_entry:
                        entries.append(current_entry)

                    current_entry = new_entry
                    i += 2
                    continue

        # Format 2:
        # Company | Title | Location | Apr 2025 – Present
        date_match = date_pattern.search(line)

        if date_match:
            heading = line[:date_match.start()].strip().rstrip("|").strip()
            dates = date_match.group(0).strip()

            new_entry = parse_heading(heading, dates)

            if new_entry:
                if current_entry:
                    entries.append(current_entry)

                current_entry = new_entry
                i += 1
                continue

        # If we're already inside a job, treat remaining lines
        # as achievements until the next job heading.
        if current_entry:
            current_entry["achievements"].append(line)

        i += 1

    if current_entry:
        entries.append(current_entry)

    for entry in entries:
        entry["achievements"] = "\n".join(entry["achievements"])

    return entries

def parse_projects(projects_text: str) -> list[dict[str, str | list[str]]]:
    """Extract structured project information from resume text."""

    if not projects_text.strip():
        return []

    lines = normalize_text(projects_text).splitlines()

    projects = []
    current_project = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Detect project headings
        if "—" in line or "–" in line or "|" in line:
            if current_project:
                projects.append(current_project)

            parts = re.split(r"[—–|]", line, maxsplit=1)

            current_project = {
                "name": parts[0].strip(),
                "subtitle": parts[1].strip() if len(parts) > 1 else "",
                "technologies": [],
                "description": [],
            }

        elif current_project:
            # Detect technology stack
            if "," in line and len(line.split(",")) >= 2:
                current_project["technologies"] = [
                    tech.strip() for tech in line.split(",")
                ]

            else:
                current_project["description"].append(line)

    if current_project:
        projects.append(current_project)

    # Convert descriptions into strings
    for project in projects:
        project["description"] = "\n".join(project["description"])

    return projects

def parse_resume(text: str) -> dict[str, Any]:
    """Produce an initial structured representation of a resume."""
    if not text or not text.strip():
        raise ValueError("Resume text cannot be empty")

    normalized_text = normalize_text(text)
    sections = extract_sections(normalized_text)

    return {
        "summary": sections.get("summary", ""),
        "skills": extract_skills(normalized_text),
        "education": parse_education(
            sections.get("education", "")
        ),
        "experience": parse_experience(sections.get("experience", "")),
        "projects": parse_projects(sections.get("projects", "")),
        "certifications": sections.get("certifications", ""),
    }




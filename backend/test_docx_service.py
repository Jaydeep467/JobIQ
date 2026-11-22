from docx import Document
import pytest

from app.services.docx_service import extract_text_from_docx
from app.services.resume_parser import parse_resume


def create_test_docx(file_path, text):
    document = Document()

    for line in text.split("\n"):
        document.add_paragraph(line)

    document.save(file_path)


def test_extract_text_from_docx_extracts_text(tmp_path):
    docx_path = tmp_path / "resume.docx"

    create_test_docx(
        docx_path,
        "Jaydeep Patil\nSoftware Engineer\nPython Developer",
    )

    result = extract_text_from_docx(str(docx_path))

    assert "Jaydeep Patil" in result
    assert "Software Engineer" in result
    assert "Python Developer" in result


def test_extract_text_from_docx_handles_empty_document(tmp_path):
    docx_path = tmp_path / "empty.docx"

    document = Document()
    document.save(docx_path)

    result = extract_text_from_docx(str(docx_path))

    assert result == ""


def test_extract_text_from_docx_raises_for_missing_file(tmp_path):
    docx_path = tmp_path / "missing.docx"

    with pytest.raises(FileNotFoundError):
        extract_text_from_docx(str(docx_path))


def test_docx_text_can_be_parsed_into_structured_resume(tmp_path):
    resume_text = """Jaydeep Patil
jaydeep.patil@example.com
+91 98765 43210

SUMMARY
Software Engineer with experience building web applications.

SKILLS
Python, React, JavaScript, SQL

EDUCATION
Arizona State University
Master of Science in Computer Science
"""

    docx_path = tmp_path / "resume.docx"
    create_test_docx(docx_path, resume_text)

    extracted_text = extract_text_from_docx(str(docx_path))
    parsed_resume = parse_resume(extracted_text)

    assert parsed_resume["contact"]["email"] == "jaydeep.patil@example.com"
    assert parsed_resume["contact"]["phone"] == "+91 98765 43210"

    assert "Python" in parsed_resume["skills"]
    assert "React" in parsed_resume["skills"]

    assert parsed_resume["summary"]
    assert parsed_resume["education"]
import pymupdf
import pytest

from app.services.resume_parser import parse_resume
from app.services.pdf_service import extract_text_from_pdf


def create_test_pdf(file_path, text):
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    document.save(file_path)
    document.close()


def test_extract_text_from_pdf_extracts_text(tmp_path):
    pdf_path = tmp_path / "resume.pdf"
    create_test_pdf(pdf_path, "Jaydeep Patil Software Engineer")

    result = extract_text_from_pdf(str(pdf_path))

    assert "Jaydeep Patil" in result
    assert "Software Engineer" in result


def test_extract_text_from_pdf_handles_empty_pdf(tmp_path):
    pdf_path = tmp_path / "empty.pdf"

    document = pymupdf.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    result = extract_text_from_pdf(str(pdf_path))

    assert result == ""


def test_extract_text_from_pdf_raises_for_missing_file(tmp_path):
    pdf_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(str(pdf_path))

def test_pdf_text_can_be_parsed_into_structured_resume(tmp_path):
    resume_text = """
    Jaydeep Patil
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

    pdf_path = tmp_path / "resume.pdf"
    create_test_pdf(pdf_path, resume_text)

    extracted_text = extract_text_from_pdf(str(pdf_path))
    parsed_resume = parse_resume(extracted_text)

    assert parsed_resume["contact"]["email"] == "jaydeep.patil@example.com"
    assert parsed_resume["contact"]["phone"] == "+91 98765 43210"

    assert "Python" in parsed_resume["skills"]
    assert "React" in parsed_resume["skills"]

    assert parsed_resume["summary"]
    assert parsed_resume["education"]
from pathlib import Path

import pymupdf


def extract_text_from_pdf(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    document = pymupdf.open(path)

    try:
        pages = []

        for page in document:
            text = page.get_text()

            if text:
                pages.append(text.strip())

        return "\n\n".join(pages).strip()

    finally:
        document.close()
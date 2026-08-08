"""
Resume Parser
Supports PDF, DOCX and TXT
"""

import pdfplumber
from docx import Document


def parse_pdf(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


def parse_docx(file):
    doc = Document(file)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])


def parse_txt(file):
    return file.read().decode("utf-8")


def extract_resume_text(uploaded_file):
    """
    Detect file type automatically.
    """

    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return parse_pdf(uploaded_file)

    elif filename.endswith(".docx"):
        return parse_docx(uploaded_file)

    elif filename.endswith(".txt"):
        return parse_txt(uploaded_file)

    else:
        raise ValueError("Unsupported file type.")
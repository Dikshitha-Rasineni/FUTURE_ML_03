"""
Skill Extraction
"""

# ===============================
# Technical Skills Database
# ===============================

SKILLS = [
    "python",
    "java",
    "javascript",
    "html",
    "css",
    "sql",
    "mysql",
    "mongodb",
    "git",
    "github",
    "bootstrap",
    "react",
    "node",
    "express",
    "django",
    "flask",
    "aws",
    "docker",
    "kubernetes",
    "excel"
]

# ===============================
# Skill Extraction Function
# ===============================

def extract_skills(text):

    text = str(text).lower()

    detected_skills = []

    for skill in SKILLS:

        if skill in text:
            detected_skills.append(skill)

    return sorted(list(set(detected_skills)))
"""
ATS Engine
"""


def calculate_ats_score(
    similarity,
    skill_match,
    experience_match,
    education_match,
    completeness
):

    score = (

        similarity * 100 * 0.40

        +

        skill_match * 0.35

        +

        experience_match * 0.10

        +

        education_match * 0.05

        +

        completeness * 0.10

    )

    return round(score, 2)


def recommendation(score):

    if score >= 60:
        return "⭐ Strong Hire"

    elif score >= 50:
        return "✅ Hire"

    elif score >= 45:
        return "⚠️ Consider"

    else:
        return "❌ Reject"
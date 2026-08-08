from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model only once
embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def calculate_similarity(resume_text, job_description):
    """
    Calculate semantic similarity between
    one resume and one job description.
    """

    resume_embedding = embedding_model.encode(
        [resume_text],
        convert_to_numpy=True
    )

    job_embedding = embedding_model.encode(
        [job_description],
        convert_to_numpy=True
    )

    similarity = cosine_similarity(
        resume_embedding,
        job_embedding
    )[0][0]

    return round(float(similarity), 4)

def calculate_skill_match(resume_skills, job_skills):
    """
    Calculate skill match percentage between
    resume skills and job description skills.
    """

    resume_skills = set(skill.lower() for skill in resume_skills)
    job_skills = set(skill.lower() for skill in job_skills)

    if len(job_skills) == 0:
        return 0

    match = len(resume_skills.intersection(job_skills))

    return round((match / len(job_skills)) * 100, 2)
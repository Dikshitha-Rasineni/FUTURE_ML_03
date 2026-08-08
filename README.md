# AI Resume Screening System

An AI-powered resume screening and candidate evaluation system that helps recruiters analyze resumes against job descriptions using Natural Language Processing, semantic similarity, skill matching, and ATS-based scoring.

The system provides an interactive Streamlit dashboard where recruiters can upload resumes, enter a job description, analyze candidate suitability, and view screening analytics.

---

## Overview

Recruiters often need to review a large number of resumes for a single position. Manually comparing resumes with job requirements can be time-consuming and inconsistent.

This project automates key parts of the initial screening process by combining:

- Resume text extraction
- NLP-based preprocessing
- Skill extraction
- Semantic similarity
- Skill matching
- ATS score calculation
- Candidate recommendations
- Screening analytics

The goal is to provide a faster and more structured way to evaluate candidates while keeping the screening process transparent.

---

## Key Features

###  Resume Screening

- Upload resumes in **PDF, DOCX, or TXT** format
- Extract resume text automatically
- Clean and preprocess resume content
- Display original, cleaned, and NLP-processed text
- Detect relevant technical skills
- Compare resume skills with job requirements

### NLP & Semantic Matching

- Natural Language Processing using **spaCy**
- Resume preprocessing and normalization
- Skill extraction using predefined skill matching
- Semantic representation using **BGE embeddings**
- Cosine similarity between resume and job description

### ATS Scoring

The system combines multiple screening signals into an overall ATS score:

- Semantic Similarity
- Skill Match
- Experience Match
- Education Match
- Resume Completeness

The final score is used to generate a candidate recommendation.

### Candidate Recommendations

Candidates are categorized into:

| ATS Score | Recommendation |
|-----------|----------------|
| `60+` | ⭐ Strong Hire |
| `50–59.99` | ✅ Hire |
| `45–49.99` | ⚠️ Consider |
| `<45` | ❌ Reject |

### Analytics Dashboard

The analytics section provides insights into resumes analyzed during the current session, including:

- Number of resumes screened
- Average ATS score
- Average semantic similarity
- Average skill match
- Score trends
- Recommendation distribution
- Commonly detected skills
- Screening history

---

## Machine Learning Pipeline

The system follows an end-to-end resume screening pipeline:

```text
                 Resume
                    │
                    ▼
          ┌──────────────────┐
          │ Text Extraction  │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ NLP Preprocessing│
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Skill Extraction │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ BGE Embeddings   │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Cosine Similarity│
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Skill Matching   │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │   ATS Scoring    │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Recommendation   │
          └──────────────────┘

## Tech Stack
Programming & Application
Python
Streamlit
Natural Language Processing
spaCy
Sentence Transformers
Machine Learning
BGE-small-en-v1.5
Scikit-learn
Cosine Similarity
Data Processing
Pandas
NumPy
Visualization
Plotly
Development
Jupyter Notebook
Git & GitHub

📂 Project Structure
FUTURE_ML_03/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── backend/
│   ├── __init__.py
│   ├── ats_engine.py
│   ├── ml_pipeline.py
│   ├── parser.py
│   ├── preprocessing.py
│   └── skill_extractor.py
│
├── data/
│   ├── job_descriptions/
│   └── resumes/
│
├── models/
│
├── notebooks/
│   └── Resume_Screening_System.ipynb
│
└── screenshots/
    ├── dashboard.png
    ├── resume-screening.png
    ├── analytics.png
    └── about.png

Large datasets and generated model files are excluded from version control using .gitignore.

📸 Application Screenshots
🏠 Dashboard

The dashboard provides an overview of the AI-powered resume screening system, its capabilities, and the technologies used.
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/d673bcb2-e5db-4d81-9b70-54662f2c81a3" />

📄 Resume Screening

Recruiters can upload a resume and provide a job description. The system processes the resume and presents detected skills, required job skills, similarity, skill match, ATS score, and recommendation.
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/7d78edee-07f5-4d86-8bda-efeed0f490e9" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/f83c254a-d2e5-499b-9fa5-a8db09efdff7" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/72cd87ce-9ea4-4f2b-8a56-29d9331e6b84" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/8e066562-6c41-4fb4-a4ed-6d60bd2501f5" />


📊 Analytics

The analytics dashboard provides an overview of screening activity and candidate evaluation trends.
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/90e17612-cc33-4b4e-bdd6-34211876e8ed" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/4ba29477-92ba-47c3-a783-e305823b8bb7" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/19adb4fd-9de3-4cfa-8c24-c76a19b781dc" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/0af4809c-05e8-4bae-9ac7-d068b0bf961e" />

ℹ️ About

The About section explains the technology stack and overall methodology behind the system.
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/fa3a87aa-42e1-4a0f-992f-7e7e48e3c906" />


⚙️ How to Run Locally
1. Clone the repository
git clone https://github.com/Dikshitha-Rasineni/FUTURE_ML_03.git
2. Navigate to the project
cd FUTURE_ML_03
3. Create a virtual environment
macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
Windows
python -m venv .venv
.venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt
5. Run the Streamlit application
streamlit run app.py

The application will open in your browser at the local Streamlit address.

🔍 Example Screening Workflow

A typical screening process looks like:

1. Upload Resume
        ↓
2. Enter Job Description
        ↓
3. Extract Resume Text
        ↓
4. Preprocess Resume
        ↓
5. Extract Skills
        ↓
6. Generate Semantic Embeddings
        ↓
7. Calculate Similarity
        ↓
8. Calculate Skill Match
        ↓
9. Calculate ATS Score
        ↓
10. Generate Recommendation
📊 ATS Score Calculation

The ATS score combines the major screening signals into a single score:

ATS Score =
    40% Semantic Similarity
  + 35% Skill Match
  + 10% Experience Match
  +  5% Education Match
  + 10% Resume Completeness

This provides a structured scoring mechanism for comparing candidates against a particular job description.

🎯 Project Objective

The primary objective of this project is to develop an intelligent resume screening system that can:

Reduce the time required for initial resume screening
Identify relevant candidate skills
Compare resumes with job requirements
Provide semantic similarity between resumes and job descriptions
Generate a consistent ATS score
Assist recruiters in prioritizing candidates

The system is intended as a recruitment decision-support tool, rather than a replacement for human decision-making.

🔮 Future Improvements

Potential future enhancements include:

Multi-resume batch screening
Candidate ranking across multiple resumes
More advanced experience extraction
Improved education and experience matching
Resume-to-job explainability
Recruiter authentication
Persistent candidate databases
Exportable screening reports
Bias and fairness monitoring
Cloud deployment
Integration with applicant tracking systems
📌 Project Status

Current Status: Completed Prototype

The current system includes the core resume screening pipeline, Streamlit interface, ATS scoring, candidate recommendations, and analytics dashboard.

👩‍💻 Author

Dikshitha Rasineni

B.Tech — Computer Science & Engineering
Specialization in Artificial Intelligence & Machine Learning

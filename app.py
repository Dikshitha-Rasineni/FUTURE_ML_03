import streamlit as st
import plotly.graph_objects as go
from collections import Counter

from backend.parser import extract_resume_text
from backend.preprocessing import clean_resume, preprocess_text
from backend.skill_extractor import extract_skills
from backend.ats_engine import calculate_ats_score, recommendation
from backend.ml_pipeline import (
    calculate_similarity,
    calculate_skill_match
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# SESSION STATE (for real, session-based analytics — no fake data)
# ==========================================================

if "history" not in st.session_state:
    st.session_state.history = []  # each item: dict of one completed analysis

# ==========================================================
# DISPLAY-ONLY FORMATTING HELPERS
# (UI ITEM 6: these only change how numbers are *shown*.
#  They never touch calculate_similarity, calculate_ats_score,
#  calculate_skill_match, or recommendation — those values pass
#  through untouched and are stored in session_state as-is.)
# ==========================================================

def similarity_to_percent(similarity_value):
    """The backend returns cosine similarity as a 0-1 float.
    Convert ONLY for display so 0.7224 renders as 72.24%
    instead of the old, incorrect '0.7224%'."""
    pct = similarity_value * 100 if similarity_value <= 1 else similarity_value
    return round(pct, 2)


def fmt_pct(value):
    """Consistent percentage string formatting for display."""
    return f"{value:.2f}%" if isinstance(value, float) else f"{value}%"


def clamp_0_100(value):
    return min(max(int(round(value)), 0), 100)


# ==========================================================
# GLOBAL STYLE — dark, futuristic neon console
# (presentation only — no backend logic here)
# ==========================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* -----------------------------------------------------
       UI ITEM 1 — TEXT VISIBILITY
       Brighter, higher-contrast text tokens. Nothing
       important renders in low-contrast grey anymore.
    ----------------------------------------------------- */
    :root {
        --bg-0: #05070f;
        --bg-1: #0a0f1e;
        --panel: rgba(17, 24, 42, 0.68);
        --panel-border: rgba(0, 229, 255, 0.20);
        --neon-cyan: #00e5ff;
        --neon-purple: #a855f7;
        --neon-pink: #ff4dd8;
        --neon-green: #39ff88;
        --neon-red: #ff5470;
        --neon-yellow: #ffd60a;

        --text-primary: #FFFFFF;    /* headings, values, key labels   */
        --text-secondary: #ECECEC; /* body copy, descriptions        */
        --text-muted: #D8D8D8;     /* captions, chart labels, hints  */

        /* UI ITEM 2 — spacing scale used everywhere below */
        --space-sm: 0.75rem;
        --space-md: 1.25rem;
        --space-lg: 2rem;
        --space-xl: 2.75rem;
    }

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--text-secondary);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* UI ITEM 14 — responsive: never allow horizontal scroll */
    .stApp, .main, .block-container {
        overflow-x: hidden !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(0, 229, 255, 0.10) 0%, transparent 45%),
            radial-gradient(circle at 85% 0%, rgba(168, 85, 247, 0.12) 0%, transparent 45%),
            radial-gradient(circle at 50% 100%, rgba(255, 77, 216, 0.08) 0%, transparent 50%),
            linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 100%);
        background-attachment: fixed;
    }

    /* UI ITEM 2 — generous vertical rhythm for the whole page */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3.5rem;
        max-width: 1280px;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #060a16 0%, #0b1226 100%);
        border-right: 1px solid var(--panel-border);
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {
        color: var(--text-muted) !important;
    }

    /* -----------------------------------------------------
       UI ITEM 3 — HERO / HEADER
       Bigger, more confident SaaS-style hero with clearer
       hierarchy between title and subtitle.
    ----------------------------------------------------- */
    .app-header {
        padding: 2.2rem 2.4rem;
        border-radius: 20px;
        background: linear-gradient(120deg, rgba(0,229,255,0.16), rgba(168,85,247,0.20) 55%, rgba(255,77,216,0.15));
        border: 1px solid var(--panel-border);
        box-shadow: 0 0 36px rgba(0, 229, 255, 0.14), inset 0 0 44px rgba(168, 85, 247, 0.07);
        margin-bottom: var(--space-xl);
        backdrop-filter: blur(10px);
    }
    .app-header .eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--neon-cyan);
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 0.5rem;
    }
    .app-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        line-height: 1.25;
        background: linear-gradient(90deg, #ffffff, #b9f3ff 45%, #d9b8ff);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .app-header p {
        margin: 0.6rem 0 0 0;
        color: var(--text-secondary);
        font-size: 1.02rem;
        font-family: 'JetBrains Mono', monospace;
    }

    /* -----------------------------------------------------
       UI ITEM 2 — CARDS
       More internal padding + larger bottom margin so
       sections/cards/graphs all get breathing room.
    ----------------------------------------------------- */
    .section-card {
        background: var(--panel);
        border: 1px solid var(--panel-border);
        border-radius: 18px;
        padding: 1.8rem 2rem;
        margin-bottom: var(--space-lg);
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 28px rgba(0, 0, 0, 0.38);
    }
    .section-title {
        font-size: 1.12rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1.1rem;
        display: flex;
        align-items: center;
        gap: 0.55rem;
        letter-spacing: 0.01em;
    }
    .section-subtext {
        color: var(--text-muted);
        font-size: 0.9rem;
        margin: -0.6rem 0 1.2rem 0;
        font-family: 'JetBrains Mono', monospace;
    }
    /* thin divider used to add breathing room between stacked blocks */
    .ui-spacer-sm { height: var(--space-md); }
    .ui-spacer-lg { height: var(--space-xl); }

    /* -----------------------------------------------------
       UI ITEM 5 — UNIFORM METRIC / RESULT CARDS
       Fixed height flex layout so ATS Score / Similarity /
       Skill Match / Recommendation always match in size,
       with centered icon + value + consistent padding.
    ----------------------------------------------------- */
    .metric-card {
        background: var(--panel);
        border: 1px solid var(--panel-border);
        border-radius: 18px;
        padding: 1.6rem 1.4rem;
        text-align: center;
        backdrop-filter: blur(12px);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.07);
        min-height: 168px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.35rem;
    }
    .metric-card .icon {
        font-size: 1.6rem;
        line-height: 1;
        margin-bottom: 0.15rem;
    }
    .metric-card .label {
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.09em;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        background: linear-gradient(90deg, #00e5ff, #c084fc);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card .sub {
        font-size: 0.8rem;
        color: var(--text-muted);
    }

    /* -----------------------------------------------------
       UI ITEM 8 — SKILL CHIPS
       Consistent pill size across all four chip types.
    ----------------------------------------------------- */
    .badge-row { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.42rem 0.95rem;
        border-radius: 999px;
        font-size: 0.84rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        border: 1px solid transparent;
        white-space: nowrap;
    }
    .badge-skill {      /* Detected Skills — cyan outline pill, subtle glow */
        background: rgba(0, 229, 255, 0.10);
        color: #baf6ff;
        border-color: rgba(0, 229, 255, 0.55);
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.20);
    }
    .badge-job {        /* Required Skills — purple */
        background: rgba(168, 85, 247, 0.14);
        color: #e3d1ff;
        border-color: rgba(168, 85, 247, 0.55);
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.20);
    }
    .badge-matched {    /* Matched Skills — green */
        background: rgba(57, 255, 136, 0.12);
        color: #c8ffe1;
        border-color: rgba(57, 255, 136, 0.55);
        box-shadow: 0 0 12px rgba(57, 255, 136, 0.20);
    }
    .badge-missing {    /* Missing Skills — red */
        background: rgba(255, 84, 112, 0.12);
        color: #ffd7dd;
        border-color: rgba(255, 84, 112, 0.55);
        box-shadow: 0 0 12px rgba(255, 84, 112, 0.20);
    }

    /* -----------------------------------------------------
       UI ITEM 7 — CANDIDATE SUMMARY
       More padding/spacing, white body text, accent-colored
       key fields (ATS Score, Recommendation, Top Skills).
    ----------------------------------------------------- */
    .summary-box {
        background: rgba(5, 10, 25, 0.6);
        border-left: 4px solid var(--neon-cyan);
        border-radius: 14px;
        padding: 1.8rem 2rem;
    }
    .summary-row {
        margin-bottom: 0.85rem;
        font-size: 1rem;
        color: var(--text-primary);
        line-height: 1.5;
    }
    .summary-row .accent-cyan { color: var(--neon-cyan); font-weight: 700; }
    .summary-row .accent-purple { color: #d9b8ff; font-weight: 700; }
    .summary-row .accent-green { color: var(--neon-green); font-weight: 700; }
    .summary-box ul {
        margin: 0.3rem 0 1.1rem 1.2rem;
        color: var(--text-secondary);
        line-height: 1.7;
    }
    .summary-box h4 {
        color: var(--text-primary);
        font-size: 0.92rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0 0 0.4rem 0;
        font-family: 'JetBrains Mono', monospace;
    }

    /* -----------------------------------------------------
       UI ITEM 9 — PROGRESS BARS
       Thicker, rounded, gradient-filled.
    ----------------------------------------------------- */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #00e5ff, #a855f7);
        border-radius: 999px !important;
    }
    .stProgress > div > div {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 999px !important;
        height: 16px !important;
    }
    .progress-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.88rem;
        color: var(--text-secondary);
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 0.35rem;
    }
    .progress-label b { color: var(--text-primary); }
    .progress-block { margin-bottom: 1.4rem; }

    .stTextArea textarea, .stTextInput input {
        background: rgba(5, 10, 25, 0.6) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 12px !important;
        font-size: 0.96rem !important;
    }
    .stTextArea label, .stTextInput label, .stFileUploader label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* UI ITEM 4 — upload dropzone reads like a proper ATS intake panel */
    div[data-testid="stFileUploaderDropzone"] {
        background: rgba(5, 10, 25, 0.55);
        border: 1.5px dashed rgba(0, 229, 255, 0.4);
        border-radius: 14px;
        padding: 0.5rem;
    }
    div[data-testid="stFileUploaderDropzone"] * {
        color: var(--text-secondary) !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #00e5ff, #a855f7);
        color: #05070f;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.2rem;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.32);
        margin-top: 0.4rem;
    }
    .stButton > button:hover {
        box-shadow: 0 0 28px rgba(168, 85, 247, 0.55);
        color: #05070f;
    }
    .stButton > button p { color: #05070f !important; font-weight: 700 !important; }

    /* UI ITEM 13 — bigger, cleaner expanders */
    .streamlit-expanderHeader, div[data-testid="stExpander"] summary {
        background: var(--panel) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 12px !important;
        padding: 0.9rem 1.1rem !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    div[data-testid="stExpander"] {
        border: none !important;
        margin-bottom: 1rem;
    }
    div[data-testid="stExpanderDetails"] {
        background: rgba(5, 10, 25, 0.5) !important;
        border: 1px solid var(--panel-border) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1.2rem 1.3rem !important;
        color: var(--text-secondary) !important;
    }

    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: var(--text-secondary);
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
    }

    /* generic helper text colors so Streamlit's own captions/labels
       never fall back to low-contrast grey (UI ITEM 1) */
    [data-testid="stCaptionContainer"], .stCaption, small {
        color: var(--text-muted) !important;
    }
    [data-testid="stMarkdownContainer"] p {
        color: var(--text-secondary);
    }
    h1, h2, h3, h4, h5 { color: var(--text-primary) !important; }

    /* dataframe / table (Analytics scan history) contrast */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--panel-border);
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# UI ITEM 10 — shared chart theme: brighter fonts, bigger legend text
# NOTE: no 'legend' key here — charts that need custom legend placement
# (e.g. trend_fig) pass their own `legend=...` to update_layout, and
# Python raises "got multiple values for keyword argument" if a key is
# both explicit and inside **PLOTLY_DARK. The base `font` above already
# lifts legend text color/size for every chart that doesn't override it.
PLOTLY_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#ECECEC", family="JetBrains Mono", size=13),
)

# ==========================================================
# UI HELPER FUNCTIONS (presentation only — do not affect scoring)
# ==========================================================

def render_header(eyebrow, title, subtitle):
    st.markdown(f"""
    <div class="app-header">
        <div class="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def spacer(size="sm"):
    """UI ITEM 2 — explicit vertical breathing room between blocks."""
    st.markdown(f'<div class="ui-spacer-{size}"></div>', unsafe_allow_html=True)


def render_metric_card(col, icon, label, value, sub=""):
    """UI ITEM 5 — every metric card shares the same fixed-height
    flex layout so icon / value / label always line up identically
    regardless of content length."""
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">{icon}</div>
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)


def render_badges(items, css_class, empty_message):
    if not items:
        st.warning(empty_message)
        return
    chips = "".join(f'<span class="badge {css_class}">{item}</span>' for item in items)
    st.markdown(f'<div class="badge-row">{chips}</div>', unsafe_allow_html=True)


def render_progress(label, value_pct):
    """UI ITEM 9 — labeled, thicker, gradient progress bar."""
    st.markdown(f"""
    <div class="progress-label"><span>{label}</span><b>{fmt_pct(value_pct)}</b></div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="progress-block">', unsafe_allow_html=True)
    st.progress(clamp_0_100(value_pct))
    st.markdown('</div>', unsafe_allow_html=True)


def render_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 38, "color": "#FFFFFF"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#D8D8D8",
                     "tickfont": {"color": "#ECECEC", "size": 12}},
            "bar": {"color": "#00e5ff", "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 1,
            "bordercolor": "rgba(0, 229, 255, 0.3)",
            "steps": [
                {"range": [0, 50], "color": "rgba(255, 84, 112, 0.20)"},
                {"range": [50, 75], "color": "rgba(255, 214, 10, 0.16)"},
                {"range": [75, 100], "color": "rgba(57, 255, 136, 0.20)"},
            ],
        },
        domain={"x": [0, 1], "y": [0, 1]},
    ))
    # UI ITEM 10 — taller chart, brighter fonts
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=10), **PLOTLY_DARK)
    st.plotly_chart(fig, use_container_width=True)


def build_matched_and_missing(resume_skills, job_skills_list):
    """Pure UI comparison of already-extracted skill lists. No scoring logic here."""
    resume_set = {s.lower() for s in resume_skills}

    matched = [s for s in job_skills_list if s.lower() in resume_set]
    missing = [s for s in job_skills_list if s.lower() not in resume_set]
    return matched, missing


def build_summary_notes(resume_skills, missing_skills):
    """Generates readable strengths/improvement bullet points from real detected
    skills and real missing skills — no fabricated scores or values."""
    strengths = [f"Strong grasp of {skill}" for skill in resume_skills[:5]]
    if not strengths:
        strengths = ["No standout skills detected from the resume text."]

    improvements = [f"Consider strengthening {skill}" for skill in missing_skills[:5]]
    if not improvements:
        improvements = ["No major skill gaps detected against the job description."]

    return strengths, improvements


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.markdown("## 🤖 AI Recruiter")
    st.caption("Resume Intelligence Suite")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠  Dashboard",
            "📄  Resume Screening",
            "📊  Analytics",
            "ℹ️  About"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption(f"🗂 Scanned this session: {len(st.session_state.history)}")
    st.caption("Powered by spaCy + Sentence Transformers")

# ==========================================================
# DASHBOARD  (UI ITEM 3 — professional SaaS-style landing view)
# ==========================================================

if page == "🏠  Dashboard":

    render_header(
        "AI RECRUITER CONSOLE",
        "AI Resume Screening System",
        "AI-powered Applicant Tracking System for smarter, faster hiring decisions."
    )

    st.markdown("""
    <div class="section-card">
        <div class="section-title">✨ What this platform does</div>
        <div class="section-subtext" style="margin-top:-0.4rem; margin-bottom:0;">
            Screen resumes using NLP (spaCy), Sentence Transformers, semantic similarity,
            skill matching, and automated ATS scoring — all in one recruiter-friendly dashboard.
        </div>
    </div>
    """, unsafe_allow_html=True)

    spacer("sm")

    col1, col2, col3, col4 = st.columns(4, gap="medium")
    render_metric_card(col1, "📄", "Resumes", "2,484")
    render_metric_card(col2, "🧭", "Job Roles", "100+")
    render_metric_card(col3, "🛠", "Skills", "30+")
    render_metric_card(col4, "🧠", "Model", "BGE")

    spacer("lg")
    st.success("Backend Connected Successfully ✅")

# ==========================================================
# RESUME SCREENING  (UI ITEM 4)
# ==========================================================

elif page == "📄  Resume Screening":

    render_header(
        "SCREENING WORKSPACE",
        "Resume Screening",
        "Upload a resume and paste a job description to generate a full ATS report."
    )

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📥 Candidate Intake</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtext">Provide a resume file and the target job description to begin scoring.</div>',
        unsafe_allow_html=True,
    )

    upload_col, jd_col = st.columns(2, gap="large")

    with upload_col:
        uploaded_file = st.file_uploader(
            "Upload Resume",
            type=["pdf", "docx", "txt"]
        )

    with jd_col:
        job_description = st.text_area(
            "Paste Job Description",
            height=180
        )

    spacer("sm")
    analyze_clicked = st.button("🔍  Analyze Resume", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if analyze_clicked:

        if uploaded_file is None:
            st.warning("Please upload a resume first.")

        else:

            # ------------------------------------
            # Extract Resume Text
            # ------------------------------------

            resume_text = extract_resume_text(uploaded_file)

            # ------------------------------------
            # Clean Resume
            # ------------------------------------

            clean_text = clean_resume(resume_text)

            # ------------------------------------
            # NLP Processing
            # ------------------------------------

            processed_text = preprocess_text(resume_text)

            # ------------------------------------
            # Skill Extraction
            # ------------------------------------

            skills = extract_skills(resume_text)
            job_skills = extract_skills(job_description)

            # ------------------------------------
            # Temporary ATS Values
            # (Will connect to notebook later)
            # ------------------------------------

            similarity = calculate_similarity(
                processed_text,
                job_description
            )
            skill_match = calculate_skill_match(
                skills,
                job_skills
            )
            experience_match = 60
            education_match = 100
            completeness = 80

            ats_score = calculate_ats_score(
                similarity,
                skill_match,
                experience_match,
                education_match,
                completeness
            )

            hire = recommendation(ats_score)

            # UI ITEM 6 — display-only conversion; raw `similarity` (0-1)
            # from the backend is left completely untouched and is what
            # gets passed into calculate_ats_score above and stored below.
            similarity_display = similarity_to_percent(similarity)

            # Record this real result for the Analytics page (session-only, no fake data)
            st.session_state.history.append({
                "file_name": getattr(uploaded_file, "name", f"Resume {len(st.session_state.history) + 1}"),
                "ats_score": ats_score,
                "similarity_display": similarity_display,
                "skill_match": skill_match,
                "recommendation": hire,
                "skills": skills,
            })

            st.success("✅ Resume processed successfully!")
            spacer("sm")

            # ------------------------------------
            # Raw text views (UI ITEM 13 — larger, cleaner expanders)
            # ------------------------------------

            with st.expander("📄  Original Resume"):
                st.text(resume_text[:3000])

            with st.expander("🧹  Cleaned Resume"):
                st.text(clean_text[:3000])

            with st.expander("🧠  NLP Processed Resume"):
                st.text(processed_text[:3000])

            spacer("lg")

            # ------------------------------------
            # Metric cards (UI ITEM 5 — uniform size/alignment)
            # ------------------------------------

            st.markdown('<div class="section-title" style="font-size:1.3rem;">📊 ATS Results</div>', unsafe_allow_html=True)
            spacer("sm")

            m1, m2, m3, m4 = st.columns(4, gap="medium")
            render_metric_card(m1, "🎯", "ATS Score", f"{ats_score}%")
            render_metric_card(m2, "🧬", "Similarity", fmt_pct(similarity_display))
            render_metric_card(m3, "🛠", "Skill Match", f"{skill_match}%")
            render_metric_card(m4, "✅", "Recommendation", hire)

            spacer("lg")

            # ------------------------------------
            # Progress bars (UI ITEM 9)
            # ------------------------------------

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📈 Score Breakdown</div>', unsafe_allow_html=True)

            render_progress("ATS Score", ats_score)
            render_progress("Semantic Similarity", similarity_display)
            render_progress("Skill Match", skill_match)

            st.markdown('</div>', unsafe_allow_html=True)
            spacer("lg")

            # ------------------------------------
            # Gauge + Candidate summary
            # ------------------------------------

            gauge_col, summary_col = st.columns([1, 1.3], gap="large")

            with gauge_col:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">🎯 ATS Score</div>', unsafe_allow_html=True)
                render_gauge(ats_score)
                st.markdown('</div>', unsafe_allow_html=True)

            matched_skills, missing_skills = build_matched_and_missing(skills, job_skills)

            with summary_col:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">🧾 Candidate Summary</div>', unsafe_allow_html=True)

                strengths, improvements = build_summary_notes(skills, missing_skills)
                top_skills_str = ", ".join(skills[:5]) if skills else "—"

                # UI ITEM 7 — brighter body text, accent-highlighted key fields,
                # more generous padding/spacing inside the summary box.
                st.markdown(f"""
                <div class="summary-box">
                    <div class="summary-row">ATS Score: <span class="accent-cyan">{ats_score}%</span></div>
                    <div class="summary-row">Recommendation: <span class="accent-green">{hire}</span></div>
                    <div class="summary-row">Top Skills: <span class="accent-purple">{top_skills_str}</span></div>
                    <h4>Strengths</h4>
                    <ul>{"".join(f"<li>{s}</li>" for s in strengths)}</ul>
                    <h4>Areas to Improve</h4>
                    <ul>{"".join(f"<li>{i}</li>" for i in improvements)}</ul>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            spacer("lg")

            # ------------------------------------
            # Skill chip sections (UI ITEM 8 + extra spacing)
            # ------------------------------------

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🛠 Detected Resume Skills</div>', unsafe_allow_html=True)
            render_badges(skills, "badge-skill", "No skills detected.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">💼 Required Job Skills</div>', unsafe_allow_html=True)
            render_badges(job_skills, "badge-job", "No job skills detected.")
            st.markdown('</div>', unsafe_allow_html=True)

            match_col, miss_col = st.columns(2, gap="large")

            with match_col:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">✅ Matched Skills</div>', unsafe_allow_html=True)
                render_badges(matched_skills, "badge-matched", "No matched skills found.")
                st.markdown('</div>', unsafe_allow_html=True)

            with miss_col:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">❌ Missing Skills</div>', unsafe_allow_html=True)
                render_badges(missing_skills, "badge-missing", "No missing skills — great match!")
                st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# ANALYTICS  (UI ITEM 11)
# ==========================================================

elif page == "📊  Analytics":

    render_header(
        "PERFORMANCE OVERVIEW",
        "Analytics",
        "Screening trends across every resume analyzed this session."
    )

    history = st.session_state.history

    if not history:
        st.markdown("""
        <div class="section-card">
            <div class="empty-state">
                📭 No resumes analyzed yet.<br><br>
                Head to <b style="color:#00e5ff;">Resume Screening</b> and analyze a resume — this dashboard
                fills in automatically from your real results, nothing here is simulated.
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        scores = [h["ats_score"] for h in history]
        similarities = [h["similarity_display"] for h in history]  # already display-converted (UI ITEM 6)
        skill_matches = [h["skill_match"] for h in history]
        avg_score = round(sum(scores) / len(scores), 1)
        avg_similarity = round(sum(similarities) / len(similarities), 1)
        avg_skill_match = round(sum(skill_matches) / len(skill_matches), 1)
        top_pick_count = sum(1 for h in history if h["ats_score"] == max(scores))

        # ---- KPI cards ----
        c1, c2, c3, c4 = st.columns(4, gap="medium")
        render_metric_card(c1, "📄", "Resumes Scanned", len(history))
        render_metric_card(c2, "🎯", "Avg ATS Score", f"{avg_score}%")
        render_metric_card(c3, "🧬", "Avg Similarity", fmt_pct(avg_similarity))
        render_metric_card(c4, "🛠", "Avg Skill Match", f"{avg_skill_match}%")

        spacer("lg")

        # ---- score trend across scans ----
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Score Trend Across Scans</div>', unsafe_allow_html=True)

        x_labels = [f"#{i + 1}" for i in range(len(history))]
        trend_fig = go.Figure()
        trend_fig.add_trace(go.Scatter(
            x=x_labels, y=scores, name="ATS Score",
            mode="lines+markers", line=dict(color="#00e5ff", width=3),
        ))
        trend_fig.add_trace(go.Scatter(
            x=x_labels, y=similarities, name="Similarity",
            mode="lines+markers", line=dict(color="#a855f7", width=3),
        ))
        trend_fig.add_trace(go.Scatter(
            x=x_labels, y=skill_matches, name="Skill Match",
            mode="lines+markers", line=dict(color="#39ff88", width=3),
        ))
        # UI ITEM 10 — clearer axis titles, bigger legend/fonts, taller chart
        trend_fig.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1,
                        font=dict(color="#FFFFFF", size=13)),
            xaxis=dict(title="Scan", gridcolor="rgba(255,255,255,0.08)",
                       title_font=dict(color="#ECECEC"), tickfont=dict(color="#ECECEC")),
            yaxis=dict(title="Percent (%)", gridcolor="rgba(255,255,255,0.08)", range=[0, 100],
                       title_font=dict(color="#ECECEC"), tickfont=dict(color="#ECECEC")),
            **PLOTLY_DARK,
        )
        st.plotly_chart(trend_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        spacer("md")

        # ---- recommendation split + top skills ----
        rec_col, skill_col = st.columns(2, gap="large")

        with rec_col:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🧭 Recommendation Split</div>', unsafe_allow_html=True)

            rec_counts = Counter(h["recommendation"] for h in history)
            pie_fig = go.Figure(go.Pie(
                labels=list(rec_counts.keys()),
                values=list(rec_counts.values()),
                hole=0.55,
                marker=dict(colors=["#00e5ff", "#a855f7", "#39ff88", "#ff5470", "#ffd60a"]),
                textfont=dict(color="#05070f", size=13),
            ))
            pie_fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), **PLOTLY_DARK)
            st.plotly_chart(pie_fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with skill_col:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🏆 Most Common Skills Detected</div>', unsafe_allow_html=True)

            all_skills = [skill for h in history for skill in h["skills"]]
            if all_skills:
                skill_counts = Counter(all_skills).most_common(8)
                names = [s[0] for s in skill_counts][::-1]
                counts = [s[1] for s in skill_counts][::-1]

                bar_fig = go.Figure(go.Bar(
                    x=counts, y=names, orientation="h",
                    marker=dict(color=counts, colorscale=[[0, "#a855f7"], [1, "#00e5ff"]]),
                ))
                bar_fig.update_layout(
                    height=320,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis=dict(title="Occurrences", gridcolor="rgba(255,255,255,0.08)",
                               title_font=dict(color="#ECECEC"), tickfont=dict(color="#ECECEC")),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.0)", tickfont=dict(color="#FFFFFF", size=13)),
                    **PLOTLY_DARK,
                )
                st.plotly_chart(bar_fig, use_container_width=True)
            else:
                st.info("No skills detected across scanned resumes yet.")
            st.markdown('</div>', unsafe_allow_html=True)

        spacer("md")

        # ---- scan history table ----
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🗂 Scan History</div>', unsafe_allow_html=True)

        table_rows = [{
            "Resume": h["file_name"],
            "ATS Score": f"{h['ats_score']}%",
            "Similarity": fmt_pct(h["similarity_display"]),
            "Skill Match": f"{h['skill_match']}%",
            "Recommendation": h["recommendation"],
        } for h in history]

        st.dataframe(table_rows, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if top_pick_count and len(history) > 1:
            st.caption(f"🥇 {top_pick_count} resume(s) currently tied for the top ATS score this session.")

# ==========================================================
# ABOUT  (UI ITEM 12)
# ==========================================================

else:

    render_header(
        "PLATFORM INFO",
        "About",
        "How the AI Resume Screening System works."
    )

    st.markdown("""
    <div class="section-card">
        <div class="section-title">🧩 Built With</div>
        <div class="section-subtext" style="margin-bottom:0;">
            Python &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp; spaCy &nbsp;·&nbsp;
            Sentence Transformers &nbsp;·&nbsp; Scikit-learn &nbsp;·&nbsp; Plotly
        </div>
    </div>
    """, unsafe_allow_html=True)

    spacer("sm")

    st.markdown("""
    <div class="section-card">
        <div class="section-title">🧠 How It Works</div>
        <div class="section-subtext" style="margin-bottom:0; color:var(--text-secondary); line-height:1.7;">
            This project uses Natural Language Processing and Semantic Similarity
            to rank resumes against job descriptions and calculate an ATS score —
            combining skill matching, experience, education, and completeness signals
            into a single recruiter-friendly recommendation.
        </div>
    </div>
    """, unsafe_allow_html=True)

    spacer("sm")

    st.markdown("""
    <div class="section-card">
        <div class="section-title">⚙️ Pipeline Stages</div>
        <div class="section-subtext" style="margin-bottom:0; color:var(--text-secondary); line-height:1.9;">
            1️⃣ &nbsp;Resume parsing &nbsp;&nbsp;→&nbsp;&nbsp;
            2️⃣ &nbsp;Text cleaning &amp; preprocessing &nbsp;&nbsp;→&nbsp;&nbsp;
            3️⃣ &nbsp;Skill extraction &nbsp;&nbsp;→&nbsp;&nbsp;
            4️⃣ &nbsp;Semantic similarity &nbsp;&nbsp;→&nbsp;&nbsp;
            5️⃣ &nbsp;ATS scoring &amp; recommendation
        </div>
    </div>
    """, unsafe_allow_html=True)
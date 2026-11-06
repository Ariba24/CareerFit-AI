import os
import re
from typing import List

import fitz
import math
import streamlit as st
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


SKILLS = [
    # AI, software, and data
    "python", "java", "javascript", "typescript", "c++", "c#", "html", "css",
    "sql", "nosql", "machine learning", "artificial intelligence", "generative ai",
    "prompt engineering", "large language models", "natural language processing",
    "deep learning", "data annotation", "data labeling", "data analysis",
    "data engineering", "data visualization", "statistics", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "langchain", "streamlit",
    "power bi", "tableau", "excel", "api integration", "software testing",
    "quality assurance", "web development", "cloud computing", "cybersecurity",
    "database management", "git", "agile methodology",
    # Business, operations, and project work
    "project management", "program management", "operations management",
    "business analysis", "business development", "process improvement",
    "strategic planning", "stakeholder management", "vendor management",
    "inventory management", "supply chain management", "logistics",
    "documentation", "reporting", "research", "market research",
    "problem solving", "critical thinking", "decision making",
    # HR and recruitment
    "human resources", "recruitment", "talent acquisition", "interviewing",
    "employee engagement", "performance management", "payroll",
    "onboarding", "training and development", "hr operations",
    # Sales and marketing
    "sales", "lead generation", "customer relationship management",
    "account management", "negotiation", "salesforce", "digital marketing",
    "content marketing", "social media marketing", "search engine optimization",
    "search engine marketing", "email marketing", "brand management",
    "campaign management", "copywriting", "content creation",
    # Finance and administration
    "accounting", "bookkeeping", "financial analysis", "financial reporting",
    "budgeting", "forecasting", "auditing", "taxation", "invoicing",
    "accounts payable", "accounts receivable", "data entry",
    "administrative support", "calendar management", "record keeping",
    # Customer service and communication
    "customer service", "customer support", "client relationship management",
    "complaint resolution", "conflict resolution", "active listening",
    "communication", "written communication", "verbal communication",
    "presentation skills", "teamwork", "collaboration", "time management",
    "adaptability", "attention to detail", "multitasking",
    # Design and content
    "graphic design", "ui design", "ux design", "user research",
    "wireframing", "prototyping", "video editing", "creative writing",
    # General professional skills
    "leadership", "people management", "training", "teaching",
    "compliance", "risk management", "safety procedures",
]

SKILL_ALIASES = {
    "large language models": ["llm", "llms", "large language model"],
    "generative ai": ["gen ai", "generative artificial intelligence", "genai"],
    "machine learning": ["ml", "machine-learning"],
    "artificial intelligence": ["ai", "artificial-intelligence"],
    "data annotation": ["data annotator", "annotation"],
    "data labeling": ["data labelling", "labeling", "labelling"],
    "prompt engineering": ["prompt design", "prompting"],
    "data analysis": ["data analytics", "data analysing", "data handling"],
    "data visualization": ["data visualisation", "visualization", "visualisation"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "power bi": ["powerbi"],
    "problem solving": ["problem-solving", "troubleshooting"],
    "api integration": ["api integrations", "rest api", "rest apis"],
    "quality assurance": ["qa", "quality testing", "quality control"],
    "natural language processing": ["nlp"],
    "software testing": ["testing", "test cases", "test automation"],
    "database management": ["database administration", "db management"],
    "customer relationship management": ["crm"],
    "client relationship management": ["client management", "client servicing"],
    "human resources": ["hr", "human resource management", "human resources management"],
    "talent acquisition": ["talent sourcing", "candidate sourcing"],
    "recruitment": ["recruiting", "recruiter", "hiring", "candidate recruitment"],
    "sales": ["sales skills", "selling", "sales executive"],
    "employee engagement": ["staff engagement"],
    "training and development": ["learning and development", "l&d"],
    "hr operations": ["hr admin", "human resources operations"],
    "digital marketing": ["online marketing"],
    "search engine optimization": ["seo", "search engine optimisation"],
    "search engine marketing": ["sem"],
    "social media marketing": ["social media management"],
    "email marketing": ["e-mail marketing"],
    "brand management": ["brand marketing"],
    "campaign management": ["campaign planning"],
    "content creation": ["content development"],
    "financial analysis": ["finance analysis"],
    "financial reporting": ["finance reporting", "financial reports", "finance reports", "financial statements"],
    "accounts payable": ["ap"],
    "accounts receivable": ["ar"],
    "administrative support": ["admin support", "office administration"],
    "data entry": ["data input"],
    "customer service": ["customer care", "client service", "customer servicing"],
    "customer support": ["technical support", "customer assistance"],
    "complaint resolution": ["grievance handling", "complaint handling", "customer complaints", "resolved complaints"],
    "conflict resolution": ["conflict management"],
    "active listening": ["listening skills"],
    "communication": ["communication skills", "effective communication"],
    "written communication": ["written communications", "business writing"],
    "verbal communication": ["oral communication"],
    "presentation skills": ["presentation", "presentations"],
    "teamwork": ["team player", "team collaboration"],
    "collaboration": ["cross-functional collaboration", "cross functional teamwork"],
    "time management": ["time-management", "prioritization"],
    "attention to detail": ["detail oriented", "detail-oriented"],
    "critical thinking": ["logical reasoning", "analytical thinking"],
    "decision making": ["decision-making", "decision making skills"],
    "project management": ["project coordination", "project planning"],
    "program management": ["programme management"],
    "operations management": ["business operations", "operations"],
    "business analysis": ["business analyst", "requirements analysis"],
    "business development": ["bd", "business growth"],
    "process improvement": ["continuous improvement", "process optimization", "process optimisation"],
    "strategic planning": ["strategy development"],
    "stakeholder management": ["stakeholder engagement"],
    "vendor management": ["supplier management"],
    "inventory management": ["stock management"],
    "supply chain management": ["supply chain"],
    "market research": ["consumer research", "industry research"],
    "lead generation": ["prospecting", "generating leads", "generated leads", "lead sourcing"],
    "account management": ["key account management", "client account management", "managed client accounts", "managed accounts"],
    "negotiation": ["negotiation skills", "negotiated", "negotiating"],
    "accounting": ["financial accounting"],
    "bookkeeping": ["book keeping"],
    "budgeting": ["budget planning"],
    "forecasting": ["financial forecasting", "sales forecasting"],
    "auditing": ["audit"],
    "taxation": ["tax compliance", "tax preparation"],
    "record keeping": ["recordkeeping", "records management"],
    "graphic design": ["visual design"],
    "ui design": ["user interface design", "ui/ux"],
    "ux design": ["user experience design", "ui/ux"],
    "user research": ["usability research"],
    "wireframing": ["wireframes"],
    "prototyping": ["prototypes"],
    "leadership": ["team leadership"],
    "people management": ["team management"],
    "training": ["coaching", "facilitation"],
    "teaching": ["instruction", "classroom teaching"],
    "risk management": ["risk assessment"],
}



class ResumeAnalysisSummary(BaseModel):
    candidate_strengths: List[str] = Field(
        description="Evidence-based strengths relevant to the target job."
    )
    relevant_experience_and_projects: List[str] = Field(
        description="Relevant experience or projects explicitly supported by the resume."
    )
    skill_gaps: List[str] = Field(
        description="Important job requirements not clearly evidenced in the resume."
    )
    learning_actions: List[str] = Field(
        description="Practical learning actions prioritized for the target role."
    )
    resume_improvements: List[str] = Field(
        description="Specific, truthful changes that could improve the resume."
    )
    overall_assessment: str = Field(
        description="A short, balanced assessment without predicting hiring outcomes."
    )


class LearningModule(BaseModel):
    skill: str = Field(description="Skill to learn")
    priority: str = Field(
        description="High, Medium, or Low priority"
    )
    reason: str = Field(
        description="Why this skill matters for the target job"
    )
    topics: List[str] = Field(
        description="Topics arranged in learning order"
    )
    practice_task: str = Field(
        description="A practical exercise for this skill"
    )
    estimated_duration: str = Field(
        description="Estimated time needed to learn this module"
    )


class CareerRoadmap(BaseModel):
    target_role: str = Field(
        description="The job role this roadmap targets"
    )
    learning_modules: List[LearningModule] = Field(
        description="Prioritized modules arranged in learning order"
    )
    final_project: str = Field(
        description="A practical project combining the learned skills"
    )
    total_estimated_duration: str = Field(
        description="Estimated duration for the complete roadmap"
    )

@tool
def count_resume_words(resume_text: str) -> int:
    """Count the number of words in the extracted resume text."""
    return len(resume_text.split())


def contains_term(text: str, term: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)"
    return re.search(pattern, text.lower()) is not None


def skill_terms(skill: str) -> List[str]:
    return [skill] + SKILL_ALIASES.get(skill, [])


def match_skills(resume_text: str, job_description: str):
    """Return keyword score, supported requirements, matches, and absent keywords."""
    required_skills = [
        skill for skill in SKILLS
        if any(contains_term(job_description, term) for term in skill_terms(skill))
    ]
    matched_skills = [
        skill for skill in required_skills
        if any(contains_term(resume_text, term) for term in skill_terms(skill))
    ]
    missing_skills = [skill for skill in required_skills if skill not in matched_skills]

    if not required_skills:
        return None, required_skills, matched_skills, missing_skills

    score = round(len(matched_skills) / len(required_skills) * 100)
    return score, required_skills, matched_skills, missing_skills


def find_skill_evidence(resume_text: str, skills: List[str]):
    """Return up to two resume lines containing each matched skill."""
    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    evidence = {}
    for skill in skills:
        terms = skill_terms(skill)
        evidence[skill] = [
            line for line in lines
            if any(contains_term(line, term) for term in terms)
        ][:2]
    return evidence
def classify_skill_importance(job_description, required_skills):
    """Classify skills using explicit importance signals in the job description."""

    preferred_terms = [
        "preferred", "nice to have", "good to have",
        "desirable", "bonus", "additional advantage"
    ]

    essential_terms = [
        "required", "must have", "essential",
        "mandatory", "minimum qualifications",
        "basic qualifications", "requirements"
    ]

    essential_skills = []
    preferred_skills = []
    unspecified_skills = []

    section_type = None

    for line in job_description.splitlines():
        text = line.lower().strip()

        if not text:
            continue

        if any(term in text for term in preferred_terms):
            section_type = "preferred"

        elif any(term in text for term in essential_terms):
            section_type = "essential"

        for skill in required_skills:
            if not any(
                contains_term(line, term)
                for term in skill_terms(skill)
            ):
                continue

            if any(term in text for term in preferred_terms):
                category = "preferred"
            elif any(term in text for term in essential_terms):
                category = "essential"
            else:
                category = section_type

            if category == "essential":
                essential_skills.append(skill)
            elif category == "preferred":
                preferred_skills.append(skill)
            else:
                unspecified_skills.append(skill)

    return (
        list(dict.fromkeys(essential_skills)),
        list(dict.fromkeys(preferred_skills)),
        list(dict.fromkeys(unspecified_skills)),
    )

def get_ai_analysis(resume_text, job_description, matched_skills, missing_skills):
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
        except (KeyError, FileNotFoundError):
            pass

    if not api_key:
        return None, "Gemini API key not found. Check your local .env file."

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.2,
    )
    prompt = f"""
You are CareerFit AI, a careful resume analysis and career guidance assistant.
Analyze the resume against the target job.

RESUME:
{resume_text[:12000]}

JOB DESCRIPTION:
{job_description[:7000]}

KEYWORDS FOUND:
{", ".join(matched_skills) or "None detected"}

JOB KEYWORDS NOT FOUND IN RESUME:
{", ".join(missing_skills) or "None detected"}

Rules:
- Use only information supported by the resume.
- Never invent skills, qualifications, employment, projects, or achievements.
- A keyword not found does not prove that the candidate lacks the skill.
- Make learning actions specific and practical for this job.
- Keep each list concise, with no more than 3 items per section.
- Do not predict hiring outcomes or call this an official ATS score.
"""
    try:
               # Try structured Pydantic output first. Fall back to plain text if unsupported.
        try:
            structured_model = model.with_structured_output(ResumeAnalysisSummary)
            result = structured_model.invoke(prompt)

            if isinstance(result, ResumeAnalysisSummary):
                return result, None

            if isinstance(result, dict):
                return ResumeAnalysisSummary(**result), None

        except Exception as error:
            error_message = str(error)

            if (
                "RESOURCE_EXHAUSTED" in error_message
                or "429" in error_message
                or "quota" in error_message.lower()
            ):
                return None, "Gemini quota exceeded. Please try again later."

        response = model.invoke(prompt + """
Return plain text under 300 words with these headings:
1. Candidate Strengths
2. Relevant Experience and Projects
3. Important Skill Gaps
4. Practical Learning Recommendations
5. Resume Improvement Suggestions
6. Overall Assessment
""")
        return response.content, None
    except Exception as error:
        return None, f"Gemini analysis failed: {error}"
def generate_fallback_roadmap(
    job_description,
    missing_skills,
    study_hours_per_day=1
):
    learning_modules = []

    skill_resources = {
        "sql": {
            "topics": [
                "Database fundamentals",
                "SELECT, WHERE and ORDER BY",
                "GROUP BY and aggregate functions",
                "JOIN operations",
                "Subqueries and practical queries"
            ],
            "hours": 12,
            "task": "Analyze a sample business sales database using SQL."
        },
        "power bi": {
            "topics": [
                "Power BI interface",
                "Importing and cleaning data",
                "Data relationships",
                "Basic DAX measures",
                "Dashboard creation"
            ],
            "hours": 12,
            "task": "Build a business performance dashboard."
        },
        "excel": {
            "topics": [
                "Sorting and filtering",
                "Formulas and functions",
                "Pivot tables",
                "Charts and data analysis"
            ],
            "hours": 8,
            "task": "Analyze a business dataset using Excel."
        },
        "python": {
            "topics": [
                "Python fundamentals",
                "Variables and data structures",
                "Functions and loops",
                "Pandas basics",
                "Data analysis"
            ],
            "hours": 15,
            "task": "Analyze a dataset using Python and Pandas."
        }
    }

    total_hours = 0

    for skill in missing_skills:
        skill_key = skill.lower().strip()

        if skill_key in skill_resources:
            resource = skill_resources[skill_key]
        else:
            resource = {
                "topics": [
                    f"Introduction to {skill}",
                    f"Core concepts of {skill}",
                    f"Practical applications of {skill}",
                    f"Hands-on practice with {skill}"
                ],
                "hours": 6,
                "task": f"Complete a beginner-level practical exercise in {skill}."
            }

        hours = resource["hours"]
        total_hours += hours

        learning_modules.append(
            LearningModule(
                skill=skill,
                priority="High",
                reason=f"This skill was not detected in your resume and may be relevant to your target role.",
                topics=resource["topics"],
                practice_task=resource["task"],
                estimated_duration=f"{hours} learning hours"
            )
        )

    project_hours = 8
    total_hours += project_hours

    total_days = math.ceil(total_hours / study_hours_per_day)
    total_weeks = math.ceil(total_days / 7)

    return CareerRoadmap(
        target_role="Target role based on your job description",
        learning_modules=learning_modules,
        final_project="Build a practical project combining the missing skills relevant to your target job.",
        total_estimated_duration=(
            f"{total_weeks} weeks ({total_hours} learning hours)"
        )
    )
def generate_career_roadmap(
    job_description,
    matched_skills,
    missing_skills,
    study_hours_per_day=1
):
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return None, "Gemini API key not found. Check your .env file."

    if not missing_skills:
        return None, "No missing supported skills were detected."

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.2,
    )

    prompt = f"""
You are the CareerFit AI Career Guidance Agent.

Create a practical learning roadmap for this target job.

JOB DESCRIPTION:
{job_description[:7000]}

SKILLS ALREADY FOUND IN RESUME:
{", ".join(matched_skills) or "None detected"}

SKILLS NOT FOUND IN RESUME:
{", ".join(missing_skills)}

AVAILABLE STUDY TIME:
{study_hours_per_day} hour(s) per day.
Instructions:
1. Prioritize missing skills by importance to the target job.
2. Do not assume a missing keyword proves the candidate lacks that skill.
3. Arrange modules in a sensible learning order.
4. Break each skill into beginner-friendly topics.
5. Include one practical exercise per module.
6. Estimate the learning hours required for each module realistically.
7. Do not include unrelated skills.
8. Keep the roadmap suitable for a beginner.
9. The final project should combine relevant skills.
10. Return a structured response matching the CareerRoadmap schema.

DURATION RULES:
11. The candidate can study exactly {study_hours_per_day} hour(s) per day.
12. Estimate the total learning hours required for all modules and the final project.
13. Calculate the total duration using:
    total calendar weeks = total learning hours / (study hours per day * 7).
14. Round the result up to the next whole week.
15. The total duration must be consistent with the individual module durations.
16. More daily study hours must not produce a longer duration for the same learning workload.
17. Do not invent a longer timeline simply to make the roadmap look comprehensive.
18. State the total duration in weeks and the approximate daily study commitment.
"""

    try:
        structured_model = model.with_structured_output(CareerRoadmap)
        result = structured_model.invoke(prompt)
        return result, None
    except Exception as error:
       error_message = str(error)

    if (
        "RESOURCE_EXHAUSTED" in error_message
        or "429" in error_message
        or "quota" in error_message.lower()
    ):
        fallback_roadmap = generate_fallback_roadmap(
            job_description=job_description,
            missing_skills=missing_skills,
            study_hours_per_day=study_hours_per_day,
        )

        return fallback_roadmap, None

    return None, f"Roadmap generation failed: {error_message}"

def render_structured_analysis(result):
    sections = [
        ("Candidate Strengths", result.candidate_strengths),
        ("Relevant Experience and Projects", result.relevant_experience_and_projects),
        ("Important Skill Gaps", result.skill_gaps),
        ("Practical Learning Recommendations", result.learning_actions),
        ("Resume Improvement Suggestions", result.resume_improvements),
    ]
    for heading, items in sections:
        st.markdown(f"### {heading}")
        if items:
            for item in items[:3]:
                st.markdown(f"- {item}")
        else:
            st.write("No specific points identified.")
    st.markdown("### Overall Assessment")
    st.write(result.overall_assessment)


def analysis_to_text(result):
    if isinstance(result, ResumeAnalysisSummary):
        sections = [
            ("Candidate Strengths", result.candidate_strengths),
            ("Relevant Experience and Projects", result.relevant_experience_and_projects),
            ("Important Skill Gaps", result.skill_gaps),
            ("Practical Learning Recommendations", result.learning_actions),
            ("Resume Improvement Suggestions", result.resume_improvements),
        ]
        parts = []
        for heading, items in sections:
            parts.append(heading)
            parts.extend(f"- {item}" for item in items)
            parts.append("")
        parts.extend(["Overall Assessment", result.overall_assessment])
        return "\n".join(parts)
    return str(result)


st.set_page_config(
    page_title="CareerFit AI | Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp { background-color: #f5f7fb; }
.block-container { max-width: 1150px; padding-top: 2rem; padding-bottom: 3rem; }
.hero {
    background: linear-gradient(120deg, #101b35, #233e72);
    padding: 2rem 2.2rem; border-radius: 18px; margin-bottom: 1.5rem; color: white;
}
.hero h1 { color: white; font-size: 2.5rem; font-weight: 750; margin-bottom: 0.4rem; }
.hero p { color: #d6e1f5; font-size: 1rem; line-height: 1.6; margin-bottom: 0; }
.hero-tag {
    display: inline-block; background: rgba(255,255,255,0.12); color: #e6edff;
    padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.8rem; margin-bottom: 0.8rem;
}
h2, h3, .stMarkdown h2, .stMarkdown h3 { color: #172746 !important; }
.stCaption, [data-testid="stCaptionContainer"] { color: #52627a !important; }
.stFileUploader label, .stTextArea label { color: #172746 !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { background-color: white; border-radius: 14px; }
.stButton > button, .stDownloadButton > button {
    border-radius: 9px; min-height: 2.8rem; font-weight: 600; transition: 0.2s ease;
}
.stButton > button[kind="primary"] { background: #315ee7; border: 1px solid #315ee7; }
.stButton > button[kind="primary"]:hover { background: #244bc4; border-color: #244bc4; }
div[data-testid="stMetric"] {
    background: white; border: 1px solid #e3e9f3; padding: 1.1rem; border-radius: 12px;
}
div[data-testid="stFileUploader"], div[data-testid="stTextArea"] { border-radius: 10px; }
.app-footer { text-align: center; color: #718096; font-size: 0.82rem; padding: 1.8rem 0 0.5rem; }
@media (max-width: 640px) {
    .hero { padding: 1.4rem; }
    .hero h1 { font-size: 2rem; }
    .block-container { padding-top: 1rem; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-tag">✦ AI-POWERED CAREER TOOL</div>
    <h1>CareerFit AI</h1>
    <p>Resume Intelligence &amp; Career Guidance<br>
    Compare your resume with a job description, identify relevant skills and discover opportunities to improve.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## Let's analyze your resume")
st.caption("Upload your resume and provide the job description you want to target.")
input_col1, input_col2 = st.columns(2, gap="large")

with input_col1:
    with st.container(border=True):
        st.markdown("### 📄 Resume upload")
        st.caption("Upload your resume in PDF format.")
        resume_file = st.file_uploader(
            "Choose your resume", type=["pdf"],
            help="Upload a PDF containing selectable text.",
        )
        if resume_file is not None:
            st.success(f"Selected: {resume_file.name}")

with input_col2:
    with st.container(border=True):
        st.markdown("### 📋 Job description")
        st.caption("Paste the job requirements for your target role.")
        job_description = st.text_area(
            "Job Description", height=180,
            placeholder="Paste the complete job description here, including required skills and qualifications...",
            label_visibility="collapsed",
        )

analyze_clicked = st.button("✨  Analyze My Resume", type="primary", use_container_width=True)
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

if "roadmap_data" not in st.session_state:
    st.session_state.roadmap_data = None
if analyze_clicked or st.session_state.analysis_data is not None:
    if resume_file is None:
        st.warning("Please upload your resume as a PDF.")
    elif not job_description.strip():
        st.warning("Please paste a job description.")
    else:
        try:
            pdf_bytes = resume_file.getvalue()
            with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
                resume_text = "\n".join(page.get_text() for page in pdf).strip()

            if not resume_text:
                st.warning("No readable text found. This PDF may be scanned or image-based.")
            else:
                st.success("Resume text extracted successfully!")
                score, required_skills, matched_skills, missing_skills = match_skills(
                    resume_text, job_description
                )
                essential_skills, preferred_skills, unspecified_skills = classify_skill_importance(
                  job_description, required_skills
                )
                evidence = find_skill_evidence(resume_text, matched_skills)
                st.session_state.analysis_data = {
                "resume_text": resume_text,
                "job_description": job_description,
                "score": score,
                "required_skills": required_skills,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "essential_skills": essential_skills,
                "preferred_skills": preferred_skills,
                "unspecified_skills": unspecified_skills,
                "evidence": evidence,}
                st.session_state.roadmap_data = None

                try:
                    word_count = count_resume_words.invoke({"resume_text": resume_text})
                except Exception:
                    word_count = len(resume_text.split())

                st.markdown("---")
                st.markdown("## 📊 Resume–Job Match Analysis")
                st.caption("A keyword-based comparison of supported job skills against your resume.")
                score_col, info_col = st.columns([1, 2], gap="large")

                with score_col:
                    if score is None:
                        st.metric("Skill Match Score", "N/A")
                        st.caption("No supported skills were detected in this job description, so a meaningful score cannot be calculated.")
                    else:
                        st.metric(
                            "Skill Match Score", f"{score}%",
                            help="Matched supported keywords divided by supported job-description keywords. This is not an official ATS score.",
                        )
                        st.progress(score / 100)

                with info_col:
                    st.markdown("### What this score means")
                    if score is not None:
                        st.write(
                            f"Your resume contains **{len(matched_skills)}** of the "
                            f"**{len(required_skills)}** supported skills detected in the job description."
                        )
                    st.caption("The score only covers skills supported by this application's skill list. It does not predict recruiter decisions.")
                    st.markdown("### 📌 Skill Importance")

                st.caption(
                    "Skills are classified using explicit importance signals in the job description. "
                    "Unspecified means the employer has not clearly stated their importance."
                )

                importance_col1, importance_col2, importance_col3 = st.columns(3)

                with importance_col1:
                    st.markdown("**Essential**")
                    st.write(essential_skills if essential_skills else "None identified")

                with importance_col2:
                    st.markdown("**Preferred**")
                    st.write(preferred_skills if preferred_skills else "None identified")

                with importance_col3:
                    st.markdown("**Unspecified**")
                    st.write(unspecified_skills if unspecified_skills else "None identified")
                st.markdown("### 🎯 Skill Breakdown")
                col1, col2 = st.columns(2, gap="large")
                with col1:
                    with st.container(border=True):
                        st.markdown("#### ✅ Skills found")
                        st.caption(f"{len(matched_skills)} detected in your resume")
                        if matched_skills:
                            for skill in matched_skills:
                                st.markdown(f"✓ {skill.title()}")
                        else:
                            st.info("No matching skills detected.")

                with col2:
                    with st.container(border=True):
                        st.markdown("#### 🧩 Job keywords not found")
                        st.caption(f"{len(missing_skills)} not detected in your resume")
                        if missing_skills:
                            for skill in missing_skills:
                                st.markdown(f"• {skill.title()}")
                        else:
                            st.success("No missing supported keywords detected.")

                if missing_skills:
                    st.info("A keyword not found in the resume does not necessarily mean you lack that skill. It may be described differently or omitted.")

                if matched_skills:
                    with st.expander("🔎 See resume evidence for matched skills"):
                        for skill in matched_skills:
                            st.markdown(f"**{skill.title()}**")
                            lines = evidence.get(skill, [])
                            if lines:
                                for line in lines:
                                    st.markdown(f"- {line}")
                            else:
                                st.caption("No supporting line was found.")

                st.markdown("---")
                st.markdown("## 🤖 AI-Powered Career Guidance")
                st.caption("Feedback based on your resume, job description, and detected keyword gaps.")
                with st.container(border=True):
                    if "ai_result" in st.session_state.analysis_data:
                        ai_result = st.session_state.analysis_data["ai_result"]
                        ai_error = st.session_state.analysis_data["ai_error"]
                    else:
                        with st.spinner("Analyzing your resume with Gemini AI..."):
                            ai_result, ai_error = get_ai_analysis(
                                resume_text,
                                job_description,
                                matched_skills,
                                missing_skills,
                            )

                        st.session_state.analysis_data["ai_result"] = ai_result
                        st.session_state.analysis_data["ai_error"] = ai_error

                    if ai_error:
                        st.error(ai_error)
                        ai_text = ai_error
                    elif isinstance(ai_result, ResumeAnalysisSummary):
                        render_structured_analysis(ai_result)
                        ai_text = analysis_to_text(ai_result)
                    else:
                        ai_text = str(ai_result)
                        st.markdown(ai_text)

                st.markdown("---")
                st.markdown("## 🗺️ Your Personalized Career Roadmap")
                st.caption(
                    "Get an ordered learning plan based on the skills "
                    "not detected in your resume and your target job."
                )

                study_hours = st.selectbox(
                    "How much time can you study daily?",
                    options=[1, 2, 3, 4],
                    index=0,
                    format_func=lambda hours: f"{hours} hour(s) per day",
                    key="career_roadmap_study_hours",
                )

                if st.button(
                    "Generate My Career Roadmap",
                    type="primary",
                    use_container_width=True,
                ):
                    if not missing_skills:
                        st.info(
                            "No missing supported skills were detected. "
                            "Try another relevant job description."
                        )
                    else:
                        with st.spinner(
                            "Your Career Guidance Agent is building your roadmap..."
                        ):
                            roadmap, roadmap_error = generate_career_roadmap(
                                job_description=job_description,
                                matched_skills=matched_skills,
                                missing_skills=missing_skills,
                                study_hours_per_day=study_hours,
                            )

                        if roadmap_error:
                            st.error(roadmap_error)
                        else:
                            st.markdown(f"### Target role: {roadmap.target_role}")
                            st.write(
                                f"**Estimated total duration:** "
                                f"{roadmap.total_estimated_duration}"
                            )

                            roadmap_report = [
                                f"CAREERFIT AI - CAREER ROADMAP",
                                f"Target role: {roadmap.target_role}",
                                f"Total estimated duration: "
                                f"{roadmap.total_estimated_duration}",
                                "",
                            ]

                            for index, module in enumerate(
                                roadmap.learning_modules, start=1
                            ):
                                with st.expander(
                                    f"Step {index}: {module.skill} "
                                    f"({module.priority} priority)"
                                ):
                                    st.write(f"**Why learn it?** {module.reason}")
                                    st.write(
                                        f"**Estimated duration:** "
                                        f"{module.estimated_duration}"
                                    )
                                    st.write("**Topics to learn:**")
                                    for topic in module.topics:
                                        st.markdown(f"- {topic}")
                                    st.write(
                                        f"**Practice task:** {module.practice_task}"
                                    )

                                roadmap_report.extend([
                                    f"STEP {index}: {module.skill}",
                                    f"Priority: {module.priority}",
                                    f"Why: {module.reason}",
                                    f"Duration: {module.estimated_duration}",
                                    "Topics:",
                                    *[f"- {topic}" for topic in module.topics],
                                    f"Practice task: {module.practice_task}",
                                    "",
                                ])

                            st.markdown("### 🎯 Final Project")
                            st.write(roadmap.final_project)
                            roadmap_report.extend([
                                "FINAL PROJECT",
                                roadmap.final_project,
                            ])

                            st.download_button(
                                "Download Career Roadmap",
                                data="\n".join(roadmap_report),
                                file_name="careerfit_learning_roadmap.txt",
                                mime="text/plain",
                                use_container_width=True,
                            )

                st.markdown("### 📌 Resume overview")
                metric1, metric2 = st.columns(2)
                metric1.metric("Approximate resume word count", word_count)
                metric2.metric("Supported job keywords detected", len(required_skills))

                with st.expander("📄 View extracted resume text", expanded=False):
                    st.caption("This is the text extracted from your uploaded PDF.")
                    st.text_area("Review the text extracted from your PDF", value=resume_text, height=300)
                with st.expander("📋 View submitted job description", expanded=False):
                    st.write(job_description)

                evidence_text = "\n".join(
                    f"{skill.title()}:\n" + "\n".join(evidence.get(skill, []))
                    for skill in matched_skills
                ) or "No matched-skill evidence found."
                score_display = f"{score}%" if score is not None else "N/A"
                report = f"""CAREERFIT AI - RESUME ANALYSIS REPORT

SKILL MATCH SCORE: {score_display}
SCORING METHOD: Matched supported keywords / supported job-description keywords.
SUPPORTED JOB KEYWORDS: {", ".join(required_skills) or "None detected"}

MATCHED SKILLS:
{", ".join(matched_skills) or "None detected"}

JOB KEYWORDS NOT FOUND IN RESUME:
{", ".join(missing_skills) or "None detected"}

RESUME EVIDENCE:
{evidence_text}

APPROXIMATE RESUME WORD COUNT:
{word_count}

AI CAREER GUIDANCE:
{ai_text}

DISCLAIMER:
The score is based on predefined keyword matching. It is not an official ATS score
or a prediction of hiring outcomes. A keyword not found does not prove a candidate
lacks that skill.
"""
                st.markdown("---")
                st.markdown("## 📥 Your Analysis Report")
                st.caption("Save a text copy of your resume analysis and career recommendations.")
                st.download_button(
                    label="⬇️ Download Analysis Report", data=report,
                    file_name="careerfit_analysis.txt", mime="text/plain",
                    use_container_width=True,
                )

        except Exception as error:
            st.error(f"Could not analyze this PDF: {error}")
st.markdown("""
<div class="app-footer">CareerFit AI · Resume Analysis &amp; Career Guidance</div>
""", unsafe_allow_html=True)

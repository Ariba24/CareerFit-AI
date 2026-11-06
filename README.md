# 🚀 CareerFit AI
### Resume Intelligence & Career Guidance

**AI-Powered Career Tool**

CareerFit AI is an AI-powered resume analysis and career guidance application that compares resumes against job descriptions, evaluates skill alignment, identifies potential skill gaps, and generates personalized career learning recommendations.

## ✨ Key Features

- **Resume Upload:** Upload resumes in PDF format.
- **Resume Parsing:** Extract resume information using PyMuPDF.
- **ATS Matching Score:** Evaluate alignment between a resume and a job description.
- **Skill Analysis:** Identify matching skills and potential skill gaps.
- **AI-Powered Analysis:** Generate resume insights using Google Gemini.
- **Career Roadmap:** Generate structured learning recommendations using AI and Pydantic.
- **Downloadable Report:** Download the generated analysis report.

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- LangChain
- Pydantic
- PyMuPDF

## 📁 Project Structure

```text
CareerFit-AI/
│
├── app.py
├── test_gemini.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ Installation and Setup

**1. Clone the repository**

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

**2. Navigate to the project folder**

```bash
cd CareerFit-AI
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure your Gemini API key**

Create a `.env` file in the project directory:

```text
GOOGLE_API_KEY=your_api_key_here
```

**5. Run the application**

```bash
python -m streamlit run app.py
```

## 🔐 API Configuration

CareerFit AI uses the Google Gemini API for AI-powered resume analysis and career guidance.

Keep your API key private. Never upload your `.env` file or expose API credentials on GitHub.

## 🚀 Future Enhancements

- **UI/UX Improvements:** A more modern, visually engaging, and interactive application design.
- **Interactive Career Roadmap:** Improve roadmap visualization and user experience.
- **Enhanced Resume Evaluation:** Further improve skill matching accuracy and ATS score transparency.
- **Additional Resume Formats:** Extend support to more resume file formats.

---

*CareerFit AI | AI-Powered Resume Analysis & Career Guidance*
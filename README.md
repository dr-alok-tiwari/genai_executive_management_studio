# 🎓 GenAI Executive Management Studio

A production-ready, interactive Streamlit teaching portal for **Generative AI in Management Education** — built for executive classrooms, MDPs, FDPs, and professional development workshops.

**Developed by:** Dr. Alok Tiwari | Assistant Professor – Big Data Analytics | Goa Institute of Management, Goa  
**Portfolio:** https://dr-alok-tiwari.github.io/

---

## 🎯 Purpose

This portal gives management educators and facilitators a self-contained, zero-cost, no-API tool to teach Generative AI concepts to experienced working professionals. Every activity — prompt building, caselet simulation, document analysis, risk classification, quizzes — runs entirely locally with no external AI service required.

---

## ✨ Key Features

| Module | Description |
|--------|-------------|
| 🛠️ Prompt Builder Studio | Click-through R-C-T-O-F-E prompt construction with weak vs. strong comparison |
| 📌 Nudges Lab | 60+ selectable prompt nudges across management categories |
| 📄 Document Intelligence Lab | Upload PDF/DOCX/TXT/CSV; extract keywords, generate prompt templates locally |
| 🗂️ Executive Use Cases | 12 domain-specific use cases with sample prompts and risk guidance |
| 🔒 Responsible AI & Risk Classifier | Local rule-based risk classifier with mitigation recommendations |
| 📋 Caselet Simulator | 10 management caselets with role/decision-path selector and downloadable worksheets |
| ❓ Quiz & Reflection | 75+ questions (MCQ, True/False, Reflection) with difficulty and theme filters |
| 🗺 Capstone Workflow Studio | Multi-stage AI workflow designer with reflection prompts |
| ✅ Readiness Checklist | 16-item AI adoption readiness self-assessment |
| 📦 Resource Hub | Downloadable templates, checklists, and free tools guide |
| 🎓 Instructor Mode | Session flow, classroom controls, facilitation notes |

---

## 🚀 Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/dr-alok-tiwari/genai_executive_management.git
cd genai_executive_management

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

### Requirements
- Python 3.10, 3.11, or 3.12
- streamlit >= 1.33
- pypdf >= 4.0
- python-docx >= 1.1

---

## ☁️ Streamlit Community Cloud Deployment

1. Push this repository to GitHub (ensure `app.py`, `requirements.txt`, `assets/`, and `data/` are all committed)
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repository → set main file to `app.py`
4. Click **Deploy**

No secrets or API keys are required.

---

## 🗂️ Repository Structure

```
genai_executive_management/
├── app.py                      # Main application (17 pages)
├── requirements.txt
├── assets/
│   ├── style.css               # Production CSS
│   ├── logo.png
│   └── sidebar_logo.png
└── data/
    ├── nudges.csv              # 60+ prompt nudges
    ├── caselets.csv            # 10 management caselets
    ├── quiz_questions.csv      # 75+ quiz questions
    ├── prompt_library.csv      # Ready-to-use prompt collection
    ├── use_cases.csv           # Domain use cases
    ├── responsible_ai_rules.csv# Responsible AI principles
    ├── classroom_activities.csv# Structured classroom activities
    └── resource_templates.csv  # Downloadable templates
```

---

## 🏫 Classroom Usage Guide

1. **Before the session:** Run `streamlit run app.py` and open the app on the projector
2. **Enable Instructor View** in the sidebar to see facilitation notes throughout
3. **Enable Classroom Mode** for larger text and hidden quiz answers
4. **Suggested 6-session flow** is available on the Instructor Mode page
5. **Safety reminder:** Ask all participants to use only dummy or public data in any field

---

## 🔒 Data & Safety Policy

- No data is transmitted externally at any point
- All document processing is local (pypdf, python-docx)
- No API keys, no cloud database, no user accounts
- All built-in examples use synthetic, dummy, or publicly available content
- Do not enter confidential, personally identifiable, or operationally sensitive information

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: streamlit` | Run `pip install -r requirements.txt` |
| PDF upload fails | Ensure pypdf is installed: `pip install pypdf` |
| DOCX upload fails | Ensure python-docx is installed: `pip install python-docx` |
| CSS not loading | Confirm `assets/style.css` exists in the same directory as `app.py` |
| Data not loading | Confirm all CSV files are present in `data/` |

---

## ⚙️ Technical Notes

- No `lmodern` or `microtype` — not applicable (Streamlit, not LaTeX)
- No `__pycache__` should be committed to the repository
- All content is CSV-driven — edit data files to customise without touching app.py

---

## 📄 License & Copyright

© 2025–2026 Dr. Alok Tiwari · Goa Institute of Management  
For classroom and educational use. Not for commercial redistribution.

---

*Built with Streamlit · No external AI API · No paid service · No data transmission*

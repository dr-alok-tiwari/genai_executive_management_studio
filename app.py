"""
GenAI Executive Management Studio
Dr. Alok Tiwari | Goa Institute of Management
Production-ready Streamlit teaching portal — no external API required.
"""

import io, re, csv, hashlib
from pathlib import Path

import streamlit as st

try:
    import pypdf; HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False
try:
    from docx import Document as DocxDocument; HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# ─────────────────────────────────────────────────────────────────────────────
# Anchor all paths to the script's directory so the app runs correctly
# regardless of which directory Streamlit is launched from.
BASE_DIR = Path(__file__).resolve().parent

APP_TITLE    = "GenAI Executive Management Studio"
APP_SUBTITLE = "A Hands-On Learning Portal for Management Professionals"
FOOTER_TEXT  = "© 2025–2026 Dr. Alok Tiwari · Goa Institute of Management · For classroom use only"
DEVELOPER_URL = "https://dr-alok-tiwari.github.io/"

st.set_page_config(
    page_title=APP_TITLE, page_icon="🎓",
    layout="wide", initial_sidebar_state="expanded",
)

_CSS = BASE_DIR / "assets" / "style.css"
if _CSS.exists():
    st.markdown(f"<style>{_CSS.read_text()}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def load_csv(path):
    """Load CSV robustly — no caching, handles extra columns, None keys, list values."""
    p = Path(path)
    if not p.exists():
        alt = BASE_DIR / "data" / p.name
        if alt.exists():
            p = alt
        else:
            st.warning(f"⚠️ Data file not found: `{path}`")
            return []
    try:
        rows = []
        with open(p, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                clean = {}
                for k, v in row.items():
                    if k is None:          # skip phantom overflow columns
                        continue
                    if isinstance(v, list):
                        v = ", ".join(str(i) for i in v)
                    clean[k] = str(v).strip() if v is not None else ""
                rows.append(clean)
        return rows
    except Exception as e:
        st.error(f"Error reading `{Path(path).name}`: {e}")
        return []


def init_state():
    for k, v in {
        "instructor_view": False,
        "classroom_mode":  False,
        "saved_prompts":   [],
        "quiz_reveals":    {},
        "_nav_target":     None,
        "_ctr":            0,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _uid(label="x"):
    st.session_state["_ctr"] += 1
    return hashlib.md5(f"{label}{st.session_state['_ctr']}".encode()).hexdigest()[:6]


def save_prompt(text):
    if text and text not in st.session_state.saved_prompts:
        st.session_state.saved_prompts.append(text)
        st.toast("✅ Prompt saved!", icon="📋")


def prompt_box(prompt, label="Generated Prompt"):
    if not prompt:
        return
    uid = _uid(label)
    st.markdown(f'<div class="prompt-display">{prompt}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇ .txt", prompt, "prompt.txt", "text/plain", key=f"dtxt_{uid}", use_container_width=True)
    with c2:
        st.download_button("⬇ .md", f"## {label}\n\n{prompt}", "prompt.md", "text/markdown", key=f"dmd_{uid}", use_container_width=True)
    with c3:
        if st.button("💾 Save", key=f"sav_{uid}", use_container_width=True):
            save_prompt(prompt)


def ibox(note):
    if st.session_state.get("instructor_view"):
        st.markdown(f'<div class="instructor-note">🎓 <strong>Instructor:</strong> {note}</div>', unsafe_allow_html=True)


def footer():
    st.markdown(f'<div class="footer">{FOOTER_TEXT}</div>', unsafe_allow_html=True)


def empty_st(icon, msg):
    st.markdown(f'<div class="empty-state"><div style="font-size:2.5rem">{icon}</div>'
                f'<p style="color:var(--muted)">{msg}</p></div>', unsafe_allow_html=True)


def sel_blank(label, opts, **kw):
    return st.selectbox(label, ["— select —"] + list(opts), index=0, **kw)


def radio_blank(label, opts, **kw):
    return st.radio(label, opts, index=None, **kw)


# ─────────────────────────────────────────────────────────────────────────────
# INLINE DATA
# ─────────────────────────────────────────────────────────────────────────────

SCENARIO_PRESETS = [
    ("HR Planning",         "Senior HR manager reviewing workforce skill gaps"),
    ("Training Design",     "L&D coordinator designing a GenAI orientation module"),
    ("Operations",          "Operations manager mapping a slow approval workflow"),
    ("Finance & Reporting", "Finance officer preparing a quarterly performance brief"),
    ("Stakeholder Comms",   "Project lead drafting a status update for leadership"),
    ("Risk Management",     "Risk officer building a risk register for a new initiative"),
    ("Policy Review",       "Policy analyst summarising regulatory changes"),
    ("Healthcare Admin",    "Hospital administrator analysing patient wait-time data"),
    ("Knowledge Mgmt",      "Knowledge manager documenting institutional best practices"),
    ("Performance Mgmt",    "Department head preparing appraisal guidance notes"),
]

CONCEPTS = [
    {"title":"What is Generative AI?","icon":"🤖","color":"#1A3C6E",
     "body":"Generative AI refers to models that produce new content — text, tables, summaries, drafts — based on patterns learned from large datasets. Unlike search engines, they generate responses rather than retrieve documents.",
     "example":"Asking an AI to draft an executive brief from bullet points.",
     "risk":"Outputs can be fluent but factually incorrect (hallucination)."},
    {"title":"Prompt Engineering","icon":"🛠️","color":"#0D7A5F",
     "body":"A prompt is the instruction you give to an AI. Well-structured prompts with clear role, context, task, output format, and constraints produce dramatically more useful results.",
     "example":"R-C-T-O-F-E: Role · Context · Task · Output · Format · Evaluation.",
     "risk":"Vague prompts lead to generic, low-quality outputs."},
    {"title":"Hallucination Risk","icon":"⚠️","color":"#B45309",
     "body":"AI models sometimes generate confident-sounding content that is factually wrong. This is a structural limitation — verification by a human expert is always required.",
     "example":"AI cites a policy number that does not exist.",
     "risk":"High risk when AI output is used without fact-checking."},
    {"title":"Human-in-the-Loop","icon":"👤","color":"#6B21A8",
     "body":"Human-in-the-loop (HITL) means a qualified person reviews, validates, and approves AI-assisted outputs before they are acted upon. Accountability always stays with the human decision-maker.",
     "example":"A manager reviews and edits an AI-drafted performance note before sharing.",
     "risk":"Removing humans from the loop increases decision risk."},
    {"title":"Responsible AI","icon":"⚖️","color":"#0E7490",
     "body":"Responsible AI means using AI systems in ways that are fair, transparent, accountable, and safe. It includes data privacy, bias awareness, appropriate oversight, and ethical deployment.",
     "example":"Not uploading personally identifiable data to a public AI tool.",
     "risk":"Irresponsible use can cause privacy breaches or biased decisions."},
    {"title":"Free AI Tools for Professionals","icon":"🆓","color":"#065F46",
     "body":"Several capable, free AI tools are available: ChatGPT (free tier), Gemini, Copilot, NotebookLM, Perplexity, and Claude.ai. Each has different strengths. NotebookLM is excellent for document-grounded analysis.",
     "example":"Using NotebookLM to summarise a long policy document.",
     "risk":"Free tools may not meet organisational data-security standards."},
    {"title":"The R-C-T-O-F-E Framework","icon":"📐","color":"#7C3AED",
     "body":"A structured prompt contains six elements: Role (who the AI plays), Context (background), Task (what to do), Output (what to produce), Format (structure), Evaluation (quality criteria or constraints).",
     "example":"Role: Senior policy analyst. Context: Draft AI governance brief. Task: …",
     "risk":"Omitting elements reduces output relevance and reliability."},
]

CAPSTONE_PRESETS = [
    "Workforce reskilling plan for a digitising department",
    "AI adoption roadmap for a public-sector organisation",
    "Risk-assessed implementation plan for AI-assisted reporting",
    "Stakeholder communication plan for a process-change initiative",
    "Evaluation framework for AI tools in a training programme",
    "Knowledge management strategy using GenAI for document intelligence",
]

REFLECTION_PRESETS = [
    "What is one AI use case I could try in my own work this week?",
    "Where do I see the highest hallucination risk in my domain?",
    "Which task in my workflow could benefit most from prompt-assisted drafting?",
    "What data privacy rule should I apply before using any public AI tool?",
    "How would I explain responsible AI use to a colleague who is sceptical?",
    "What human oversight step would I add to an AI-assisted reporting workflow?",
]

WORKFLOWS = [
    ("Meeting Summarisation",         "meeting notes → key decisions → action points → owner table"),
    ("Executive Brief Drafting",       "raw data → structured brief → leadership-ready summary"),
    ("Risk Register Creation",         "scenario → risk items → likelihood/impact → mitigation"),
    ("Training Design",                "learning goals → module outline → activities → evaluation"),
    ("Policy Analysis",                "policy text → key clauses → implications → recommendations"),
    ("Stakeholder Communication",      "context → audience map → message draft → review checklist"),
    ("Process Improvement Note",       "current process → pain points → improvement options → proposal"),
    ("Decision Matrix",                "decision context → options → criteria → weighted scoring"),
    ("Performance Brief",              "KPI data → narrative summary → leadership highlights → actions"),
    ("Onboarding Material Drafting",   "role profile → key tasks → resource list → orientation schedule"),
    ("Feedback Analysis",              "raw feedback → theme clusters → sentiment → recommended actions"),
    ("Procurement Justification Note", "requirement → options → cost-benefit → recommended choice"),
    ("Incident Report Drafting",       "event → timeline → impact → lessons learned → corrective action"),
    ("Project Status Update",          "milestones → status → risks → next steps → escalation flag"),
]

DOCUMENT_SAMPLES = [
    ("Training Brochure (dummy)",
     "Module: AI for Managers\nDuration: 2 days\nObjectives: Build awareness, hands-on practice, responsible use.\nTopics: Generative AI basics, prompt engineering, responsible AI, use cases.\nTarget: Mid-to-senior managers."),
    ("Meeting Notes (dummy)",
     "Date: 15 Jan 2026\nAttendees: Project Lead, Finance Officer, HR Head\nAgenda: Budget review, Q2 planning, staffing update\nDecisions: Approve training budget. Review vendor bids by 30 Jan.\nAction Items: Finance to circulate revised budget. HR to send JD drafts."),
    ("Policy Excerpt (dummy)",
     "Section 4.2 — Data Handling\nAll personnel data must be stored on approved systems only. Sharing data with third-party platforms requires prior written approval from the Data Protection Officer. Violations are subject to disciplinary action."),
    ("Feedback Report (dummy)",
     "Session: GenAI Orientation Workshop\nParticipants: 24\nAvg Rating: 4.3/5\nThemes: Practical examples appreciated. More time needed for hands-on exercises. Request for sector-specific use cases."),
    ("Process Description (dummy)",
     "Current process: Approval requests submitted via email. Routed manually to HOD. Average turnaround: 7 days. Pain points: No tracking, frequent follow-ups, version confusion."),
    ("KPI Summary (dummy)",
     "Quarter: Q3 FY2025-26\nDept: Operations\nKPI 1: SLA compliance — Target 95%, Achieved 91%\nKPI 2: Training completion — Target 80%, Achieved 76%\nKPI 3: Budget utilisation — Target 90%, Achieved 88%"),
]

RISK_SCENARIOS = [
    ("Upload personnel records to ChatGPT for analysis", "High", "Uploading real personnel data to a public AI tool is a serious privacy violation."),
    ("Use AI to draft a summary of a public training brochure", "Low", "Summarising public material with dummy data poses minimal risk."),
    ("Let AI auto-approve a procurement decision", "High", "Removing human review from procurement decisions creates accountability risk."),
    ("Use AI to generate a meeting agenda from bullet points", "Low", "Drafting agendas from generic notes is a safe, low-stakes task."),
    ("Prompt AI to predict an employee's performance rating", "High", "Automated performance judgments introduce bias and legal risk."),
    ("Use AI to convert a policy document into a simplified summary", "Medium", "Useful but outputs must be verified; AI may misinterpret nuanced clauses."),
    ("Use AI to write a first draft of a stakeholder update", "Low", "Draft generation is safe as long as a human reviews before sending."),
    ("Feed internal financial data to a public AI chatbot", "High", "Confidential financial data must never be shared with public AI tools."),
    ("Use AI to suggest training activity ideas for a workshop", "Low", "Generating creative activity ideas from generic context is low risk."),
    ("Use AI to classify incoming feedback by theme", "Medium", "Classification is useful but AI labels may miss context; human review needed."),
]

USE_CASES = [
    {"id":"uc01","icon":"👥","domain":"HR & Workforce Planning","title":"Skill-Gap Analysis Brief",
     "management_problem":"How do I identify and communicate workforce skill gaps to leadership?",
     "how_ai_helps":"AI drafts a structured skill-gap brief from raw competency data.",
     "sample_prompt":"Act as a senior HR analyst. Given the following competency data: [paste data], identify the top 5 skill gaps, suggest development priorities, and produce a 500-word executive brief with a summary table. Use formal language.",
     "expected_output":"Executive brief with skill-gap table and development recommendations.",
     "risk_level":"Medium","limitation":"AI cannot verify data accuracy; HR team must validate all figures.",
     "human_oversight":"HR lead reviews all recommendations before sharing with leadership.",
     "discussion_question":"What data would you need before trusting this brief?"},
    {"id":"uc02","icon":"📚","domain":"Training & L&D","title":"Training Module Outline",
     "management_problem":"How do I quickly design a training module for a new initiative?",
     "how_ai_helps":"AI generates a structured module outline with objectives, topics, and activities.",
     "sample_prompt":"Act as an instructional designer. Design a one-day training module on [topic] for [audience]. Include: learning objectives, session outline (4 sessions), suggested activities, and evaluation method. Use a professional tone.",
     "expected_output":"Full module outline in structured format.",
     "risk_level":"Low","limitation":"Content must be reviewed for domain accuracy by subject-matter experts.",
     "human_oversight":"L&D lead verifies alignment with organisational training policy.",
     "discussion_question":"Which part of this outline would you most want to verify?"},
    {"id":"uc03","icon":"⚙️","domain":"Operations","title":"Process Improvement Note",
     "management_problem":"How do I document and propose improvements for a slow workflow?",
     "how_ai_helps":"AI converts workflow descriptions into a structured process-improvement proposal.",
     "sample_prompt":"Act as an operations analyst. Given this process description: [paste description], identify inefficiencies, suggest three improvement options, and draft a one-page proposal with a before/after comparison. Use clear headings.",
     "expected_output":"Process improvement proposal with before/after table.",
     "risk_level":"Low","limitation":"AI lacks operational context; proposals need ground-level review.",
     "human_oversight":"Operations manager validates feasibility before submission.",
     "discussion_question":"What operational detail would AI miss without context?"},
    {"id":"uc04","icon":"💰","domain":"Finance & Reporting","title":"Quarterly Performance Brief",
     "management_problem":"How do I turn raw KPI data into a leadership-ready narrative?",
     "how_ai_helps":"AI converts structured KPI data into a clear executive narrative.",
     "sample_prompt":"Act as a finance officer. Given these Q3 KPIs: [paste data], write a 400-word performance brief for senior leadership. Highlight achievements, flag concerns, and suggest one priority for Q4. Use formal language.",
     "expected_output":"Structured performance brief with narrative and recommendations.",
     "risk_level":"Medium","limitation":"AI cannot verify figure accuracy; all numbers must be checked before circulation.",
     "human_oversight":"Finance head reviews figures and approves before distribution.",
     "discussion_question":"How would you ensure the AI did not fabricate any KPI interpretation?"},
    {"id":"uc05","icon":"📣","domain":"Stakeholder Communication","title":"Status Update Draft",
     "management_problem":"How do I draft a clear, professional status update for diverse stakeholders?",
     "how_ai_helps":"AI adapts a core message for different stakeholder audiences.",
     "sample_prompt":"Act as a communications officer. Based on this project update: [paste update], draft two versions: one for senior leadership (concise, 150 words) and one for the working team (detailed, 300 words). Use professional tone.",
     "expected_output":"Two tailored communication drafts.",
     "risk_level":"Low","limitation":"Tone and sensitivity must be verified by the sending officer.",
     "human_oversight":"Project lead reviews before sending.",
     "discussion_question":"What gets lost when AI adapts a message for a different audience?"},
    {"id":"uc06","icon":"🏥","domain":"Healthcare Administration","title":"Patient Flow Summary",
     "management_problem":"How do I summarise patient wait-time data into an actionable report?",
     "how_ai_helps":"AI converts tabular data into a plain-language summary with recommendations.",
     "sample_prompt":"Act as a healthcare administrator. Given this patient flow data: [paste data], summarise key findings, identify two bottlenecks, and recommend operational adjustments. Keep the summary under 300 words.",
     "expected_output":"Patient flow summary with bottleneck identification and recommendations.",
     "risk_level":"Medium","limitation":"Clinical interpretation must involve qualified health professionals.",
     "human_oversight":"Medical administrator reviews before operational decisions are made.",
     "discussion_question":"What clinical data should never be processed by a public AI tool?"},
    {"id":"uc07","icon":"🏛️","domain":"Public Administration","title":"Policy Simplification Brief",
     "management_problem":"How do I make complex policy documents accessible to field staff?",
     "how_ai_helps":"AI extracts key provisions and converts them into a simplified brief.",
     "sample_prompt":"Act as a policy analyst. Given this policy excerpt: [paste text], identify the five most important provisions for field staff, explain each in plain language, and highlight compliance requirements. Use bullet points.",
     "expected_output":"Simplified policy brief with key provisions and compliance notes.",
     "risk_level":"Medium","limitation":"Legal interpretations must be verified by a qualified legal or policy team.",
     "human_oversight":"Policy officer reviews simplified text for accuracy before distribution.",
     "discussion_question":"What risks arise when policy language is simplified by AI?"},
    {"id":"uc08","icon":"📊","domain":"Performance Management","title":"Appraisal Feedback Draft",
     "management_problem":"How do I write constructive, consistent performance feedback?",
     "how_ai_helps":"AI generates a draft feedback note from structured performance observations.",
     "sample_prompt":"Act as a performance management advisor. Given these observations: [paste observations], draft constructive feedback (200 words) covering strengths, improvement areas, and one development suggestion. Use a professional, balanced tone. Do not use real names.",
     "expected_output":"Balanced performance feedback draft.",
     "risk_level":"Medium","limitation":"Feedback must be reviewed and personalised by the reporting manager.",
     "human_oversight":"Manager reviews and adapts before the appraisal conversation.",
     "discussion_question":"What ethical considerations apply to AI-assisted performance feedback?"},
    {"id":"uc09","icon":"🔍","domain":"Knowledge Management","title":"Lessons Learned Summary",
     "management_problem":"How do I capture and share institutional knowledge from completed projects?",
     "how_ai_helps":"AI synthesises project notes into a structured lessons-learned document.",
     "sample_prompt":"Act as a knowledge management officer. From these project notes: [paste notes], extract three key lessons, one best practice, and one risk to avoid in future projects. Format as a structured lessons-learned note.",
     "expected_output":"Structured lessons-learned document.",
     "risk_level":"Low","limitation":"Lessons must be validated by the project team before institutional use.",
     "human_oversight":"Project lead verifies accuracy and approves for knowledge repository.",
     "discussion_question":"How would you ensure AI-generated lessons capture tacit knowledge?"},
    {"id":"uc10","icon":"🗓️","domain":"Meeting Management","title":"Meeting Summary with Action Items",
     "management_problem":"How do I convert meeting notes into a clean action-oriented summary?",
     "how_ai_helps":"AI structures raw meeting notes into a summary with decisions and action owners.",
     "sample_prompt":"Act as an executive assistant. Convert these meeting notes: [paste notes] into a structured summary with: key decisions (bullet list), action items (table with owner and deadline), and one open question for follow-up. Use formal tone.",
     "expected_output":"Structured meeting summary with decisions table and action-item tracker.",
     "risk_level":"Low","limitation":"Owner assignments and deadlines must be confirmed by meeting participants.",
     "human_oversight":"Meeting chair reviews and circulates after verification.",
     "discussion_question":"What should you never include in a meeting summary shared via AI?"},
    {"id":"uc11","icon":"🚛","domain":"Logistics & Supply Chain","title":"Delay Root-Cause Brief",
     "management_problem":"How do I quickly diagnose and communicate a supply-chain delay?",
     "how_ai_helps":"AI analyses delay descriptions and structures a root-cause brief.",
     "sample_prompt":"Act as a logistics analyst. Given this delay report: [paste report], identify the most likely root causes, assess short-term impact, and recommend two mitigation actions. Format as a concise management brief.",
     "expected_output":"Root-cause brief with impact assessment and mitigation options.",
     "risk_level":"Low","limitation":"Logistics specifics must be validated by supply-chain officers.",
     "human_oversight":"Supply-chain manager reviews before sharing with procurement.",
     "discussion_question":"What contextual detail is hardest for AI to infer in logistics problems?"},
    {"id":"uc12","icon":"💬","domain":"Feedback Analysis","title":"Feedback Theme Clustering",
     "management_problem":"How do I identify patterns across large volumes of participant feedback?",
     "how_ai_helps":"AI clusters open-ended responses into themes and sentiment categories.",
     "sample_prompt":"Act as a data analyst. Given these 20 feedback responses: [paste responses], group them into 3–5 themes, indicate overall sentiment per theme, and suggest one action recommendation per theme. Format as a table.",
     "expected_output":"Themed feedback table with sentiment and action recommendations.",
     "risk_level":"Low","limitation":"AI theme labels may miss contextual nuance; human review recommended.",
     "human_oversight":"Programme coordinator validates themes before sharing report.",
     "discussion_question":"What types of feedback would be hard for AI to categorise accurately?"},
]

FREE_TOOLS_MD = """# Free AI Tools for Management Professionals

## 1. ChatGPT (chat.openai.com)
Best for: Drafting, summarising, brainstorming, prompt practice. Free tier available (GPT-4o with limits). Do not upload confidential data.

## 2. Google Gemini (gemini.google.com)
Best for: Document Q&A, multimodal tasks, Google Workspace integration. Free tier available. Review Google data usage policy.

## 3. Microsoft Copilot (copilot.microsoft.com)
Best for: Office integration, email drafting, web-grounded responses. Free tier available in Edge and Bing.

## 4. NotebookLM (notebooklm.google.com)
Best for: Source-grounded Q&A from uploaded documents. Excellent for policy documents and reports. Free tier available.

## 5. Claude.ai (claude.ai)
Best for: Long documents, structured analysis, detailed reasoning. Free tier available (Claude Sonnet).

## 6. Perplexity (perplexity.ai)
Best for: Research with real-time web citations. Always verify cited sources independently. Free tier available.

---
General guidance: Never upload confidential or personally identifiable data to any public AI tool. Label all AI-assisted outputs before sharing. Human review is always required before action.
"""

# ─────────────────────────────────────────────────────────────────────────────
# PAGES dict and navigation
# ─────────────────────────────────────────────────────────────────────────────

PAGES = {
    "🏠 Home":                     "home",
    "🗺️ Programme Roadmap":        "roadmap",
    "💡 Gen AI Concepts":           "concepts",
    "🗂️ Executive Use Cases":       "use_cases",
    "🛠️ Prompt Builder Studio":     "prompt_builder",
    "📌 Prewritten Nudges Lab":     "nudges",
    "📄 Document Intelligence Lab": "doc_lab",
    "🎯 Activity Studio":           "activity",
    "📚 Prompt Library":            "prompt_lib",
    "🔒 Responsible AI & Risk":     "responsible",
    "📋 Caselet Simulator":         "caselets",
    "🗺 Capstone Workflow Studio":   "capstone",
    "✅ Readiness Checklist":       "readiness",
    "❓ Quiz & Reflection":         "quiz",
    "📦 Resource Hub":              "resources",
    "🎓 Instructor Mode":           "instructor",
    "👤 About Developer":           "about",
}


def render_sidebar():
    with st.sidebar:
        logo = BASE_DIR / "assets" / "sidebar_logo.png"
        if logo.exists():
            st.image(str(logo), use_container_width=True)
        st.markdown(f"### {APP_TITLE}")
        st.markdown("---")
        st.session_state["instructor_view"] = st.toggle("🎓 Instructor View", value=st.session_state["instructor_view"])
        st.session_state["classroom_mode"]  = st.toggle("📽 Classroom Mode",  value=st.session_state["classroom_mode"])
        st.markdown("---")
        page_label = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
        sel = PAGES[page_label]
        if st.session_state.get("_nav_target"):
            sel = st.session_state["_nav_target"]
            st.session_state["_nav_target"] = None
        st.markdown("---")
        if st.session_state.saved_prompts:
            st.markdown(f"💾 **{len(st.session_state.saved_prompts)}** saved prompt(s)")
            all_saved = "\n\n---\n\n".join(st.session_state.saved_prompts)
            st.download_button("⬇ Export all", all_saved, "saved_prompts.txt", "text/plain", use_container_width=True)
        else:
            st.caption("No saved prompts yet.")
        st.markdown("---")
        st.markdown(f'<div style="font-size:.75rem;color:#aaa;text-align:center"><a href="{DEVELOPER_URL}" target="_blank" style="color:#aaa">Dr. Alok Tiwari</a> · GIM Goa</div>', unsafe_allow_html=True)
        return sel


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────────────────────────────────────

def page_home():
    st.markdown(f'<div class="hero-section"><div class="hero-title">🎓 {APP_TITLE}</div><div class="hero-subtitle">{APP_SUBTITLE}</div><div class="hero-meta">Facilitated by <strong>Dr. Alok Tiwari</strong> · Goa Institute of Management</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🚀 Quick Launch")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🛠️ Prompt Builder", use_container_width=True): st.session_state["_nav_target"]="prompt_builder"; st.rerun()
    with c2:
        if st.button("🗂️ Use Cases", use_container_width=True): st.session_state["_nav_target"]="use_cases"; st.rerun()
    with c3:
        if st.button("❓ Quiz", use_container_width=True): st.session_state["_nav_target"]="quiz"; st.rerun()
    with c4:
        if st.button("📋 Caselets", use_container_width=True): st.session_state["_nav_target"]="caselets"; st.rerun()
    st.markdown("---")
    st.markdown("### 📋 What This Portal Offers")
    cards = [
        ("🛠️","Prompt Builder","Build structured, professional prompts step by step."),
        ("📌","Nudges Lab","Pick prewritten nudges to instantly enhance any prompt."),
        ("📄","Document Lab","Upload and analyse documents safely — no data leaves your device."),
        ("🔒","Responsible AI","Classify AI risks and learn mitigation strategies."),
        ("📋","Caselet Simulator","Work through realistic management caselets."),
        ("❓","Quiz & Reflection","Test your understanding with 75+ curated questions."),
        ("📦","Resource Hub","Download templates, checklists, and guides."),
        ("🎓","Instructor Mode","Facilitate live sessions with classroom controls."),
    ]
    cols = st.columns(4)
    for i,(icon,title,desc) in enumerate(cards):
        with cols[i%4]:
            st.markdown(f'<div class="feature-card"><div style="font-size:2rem">{icon}</div><strong>{title}</strong><br><span style="font-size:.85rem;color:var(--muted)">{desc}</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="warning-box">⚠️ <strong>Safety Reminder:</strong> Use only synthetic, public, or approved classroom material in this portal. Do not enter confidential, personally identifiable, or operationally sensitive information in any field. All processing occurs locally — no data is transmitted externally.</div>', unsafe_allow_html=True)
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ROADMAP
# ─────────────────────────────────────────────────────────────────────────────

def page_roadmap():
    st.title("🗺️ Programme Roadmap")
    st.caption("A structured learning journey through Generative AI for management professionals.")
    stages = [
        ("Stage 1","Foundation",["What is Generative AI?","Key concepts and terminology","Free tools overview","Responsible use principles"],"#1A3C6E"),
        ("Stage 2","Prompt Engineering",["R-C-T-O-F-E framework","Weak vs. strong prompts","Prompt Builder hands-on","Nudges Lab"],"#0D7A5F"),
        ("Stage 3","Executive Use Cases",["HR, Finance, Operations, Communications","Document Intelligence Lab","Caselet Simulator","Domain-specific prompt practice"],"#F59E0B"),
        ("Stage 4","Responsible AI",["Risk classification","Human-in-the-loop","Data privacy rules","Governance frameworks"],"#7C3AED"),
        ("Stage 5","Capstone & Reflection",["Capstone Workflow Studio","Readiness Checklist","Quiz & Reflection","Personal action plan"],"#0E7490"),
    ]
    for stage,name,items,color in stages:
        with st.expander(f"**{stage}: {name}**"):
            st.markdown(f'<div style="border-left:4px solid {color};padding-left:1rem">'+"".join(f"<p>✅ {it}</p>" for it in items)+"</div>", unsafe_allow_html=True)
    ibox("Walk participants through each stage in sequence. Use the quick-launch buttons on the Home page to jump to any module.")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CONCEPTS
# ─────────────────────────────────────────────────────────────────────────────

def page_concepts():
    st.title("💡 Gen AI Concepts")
    st.caption("Core ideas every management professional should understand before using AI tools.")
    for c in CONCEPTS:
        with st.expander(f"{c['icon']}  {c['title']}"):
            st.markdown(f'<div style="border-left:4px solid {c["color"]};padding-left:1rem"><p>{c["body"]}</p><p>📌 <strong>Example:</strong> {c["example"]}</p><p>⚠️ <strong>Risk:</strong> {c["risk"]}</p></div>', unsafe_allow_html=True)
    ibox("Spend 5–7 min per concept. Ask participants for a real example from their own domain before revealing the built-in example.")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: EXECUTIVE USE CASES
# ─────────────────────────────────────────────────────────────────────────────

def page_use_cases():
    st.title("🗂️ Executive Use Cases")
    tab1,tab2 = st.tabs(["🗂️ Use Case Explorer","📊 Domain Overview"])
    with tab1:
        domains = sorted({uc["domain"] for uc in USE_CASES})
        chosen = sel_blank("Filter by domain", domains, key="uc_dom")
        items = USE_CASES if chosen=="— select —" else [u for u in USE_CASES if u["domain"]==chosen]
        for uc in items:
            rc = {"Low":"#065F46","Medium":"#92400E","High":"#991B1B"}.get(uc["risk_level"],"#374151")
            with st.expander(f"{uc['icon']}  **{uc['domain']}** — {uc['title']}"):
                ca,cb = st.columns([2,1])
                with ca:
                    st.markdown(f"**Problem:** {uc['management_problem']}")
                    st.markdown(f"**How GenAI helps:** {uc['how_ai_helps']}")
                    st.markdown("**Sample Prompt:**")
                    st.code(uc["sample_prompt"],language=None)
                with cb:
                    st.markdown(f"**Expected Output:** {uc['expected_output']}")
                    st.markdown(f'<span class="badge" style="background:{rc}">Risk: {uc["risk_level"]}</span>', unsafe_allow_html=True)
                    st.markdown(f"**Limitation:** {uc['limitation']}")
                    st.markdown(f"**Human Oversight:** {uc['human_oversight']}")
                st.info(f"💬 **Discussion:** {uc['discussion_question']}")
                prompt_box(uc["sample_prompt"],f"Use Case — {uc['title']}")
    with tab2:
        csv_ucs = load_csv(str(BASE_DIR / "data" / "use_cases.csv"))
        if csv_ucs:
            dom_list = sorted({r.get("domain","") for r in csv_ucs})
            for d in dom_list:
                n = len([r for r in csv_ucs if r.get("domain")==d])
                st.markdown(f"**{d}** — {n} use case{'s' if n>1 else ''}")
        else:
            empty_st("📂","No CSV data found.")
    ibox("Pick 2–3 use cases relevant to the participants' domain. Have them adapt the sample prompt for a real scenario from their work.")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PROMPT BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def page_prompt_builder():
    st.title("🛠️ Prompt Builder Studio")
    st.caption("Build professional, structured prompts using the R-C-T-O-F-E framework.")
    with st.expander("ℹ️ R-C-T-O-F-E Framework"):
        st.markdown("| Element | Meaning | Example |\n|---|---|---|\n| **R**ole | Who the AI acts as | Senior policy analyst |\n| **C**ontext | Background | Reviewing a public training brochure |\n| **T**ask | What to do | Summarise key learning objectives |\n| **O**utput | What to produce | A 200-word executive brief |\n| **F**ormat | Structure | Bullet points, table |\n| **E**valuation | Constraints | Formal tone, no jargon |")
    st.markdown("### 🎯 Quick Scenario")
    picked = sel_blank("Load a scenario preset",[s[0] for s in SCENARIO_PRESETS],key="pb_scen")
    sc_ctx = ""
    if picked!="— select —":
        sc_ctx = next(s[1] for s in SCENARIO_PRESETS if s[0]==picked)
        st.info(f"*{sc_ctx}*")
    st.markdown("### 🔧 Build Your Prompt")
    ROLES = ["Senior manager","Policy analyst","HR officer","Finance officer","Operations manager","Communications officer","Training coordinator","Risk officer","Healthcare administrator","Knowledge manager"]
    TASKS = ["Summarise the key points","Draft an executive brief","Create an action plan","Build a risk register","Generate a decision matrix","Design a training outline","Write a stakeholder update","Convert notes into meeting minutes","Analyse the feedback and cluster themes","Prepare a policy summary"]
    OUTPUTS = ["A structured 200-word summary","A bulleted action list","A table with columns","A one-page brief","A risk register with likelihood and impact","A decision matrix with scoring","An agenda with time slots","A numbered implementation plan"]
    FORMATS = ["Formal professional","Plain language","Bullet points","Table format","Executive narrative","Step-by-step numbered list"]
    TONES = ["Formal and concise","Analytical and precise","Balanced and objective","Simple and clear","Authoritative and direct"]
    CONSTRAINTS = ["Avoid jargon","No more than 300 words","Do not include personal names","Use only the provided data","Highlight uncertainties clearly","Flag areas needing human review","Include a disclaimer for AI-generated content"]
    c1,c2 = st.columns(2)
    with c1:
        role=sel_blank("Role (R)",ROLES,key="pb_role")
        task=sel_blank("Task (T)",TASKS,key="pb_task")
        fmt=sel_blank("Format (F)",FORMATS,key="pb_fmt")
    with c2:
        out=sel_blank("Output (O)",OUTPUTS,key="pb_out")
        tone=sel_blank("Tone",TONES,key="pb_tone")
        constr=sel_blank("Constraint (E)",CONSTRAINTS,key="pb_constr")
    ctx_text = st.text_area("Context / Background (C) — optional",value=sc_ctx,placeholder="Paste background info here…",height=90,key="pb_ctx")
    extra = st.text_area("Additional instructions — optional",placeholder="Any extra requirement…",height=60,key="pb_extra")
    st.markdown("---")
    if st.button("⚡ Generate Prompt",type="primary",use_container_width=True):
        parts=[]
        if role!="— select —": parts.append(f"Act as a {role.lower()}.")
        if ctx_text.strip(): parts.append(f"Context: {ctx_text.strip()}")
        if task!="— select —": parts.append(f"Task: {task}.")
        if out!="— select —": parts.append(f"Output: {out}.")
        if fmt!="— select —": parts.append(f"Format: {fmt}.")
        if tone!="— select —": parts.append(f"Tone: {tone}.")
        if constr!="— select —": parts.append(f"Constraint: {constr}.")
        if extra.strip(): parts.append(extra.strip())
        if len(parts)<2:
            st.warning("Select at least a role and a task to generate a prompt.")
        else:
            st.session_state["pb_gen"]=" ".join(parts)
            st.success("✅ Prompt generated!")
    gen=st.session_state.get("pb_gen","")
    if gen:
        st.markdown("### 📋 Your Prompt")
        prompt_box(gen,"Prompt Builder")
        st.markdown("---")
        st.markdown("### 🔀 Weak vs Strong Comparison")
        task_s=st.session_state.get("pb_task","— select —")
        weak=f"Write something about {task_s.lower()}." if task_s!="— select —" else "Write me a summary."
        cc1,cc2=st.columns(2)
        with cc1:
            st.markdown("**❌ Weak Prompt**")
            st.markdown(f'<div class="warning-box">{weak}</div>',unsafe_allow_html=True)
        with cc2:
            st.markdown("**✅ Strong Prompt**")
            st.markdown(f'<div class="success-box">{gen}</div>',unsafe_allow_html=True)
        st.markdown("**Why is the strong prompt better?** It specifies a role, provides context, defines the task precisely, states the expected output format, and includes quality constraints — reducing ambiguity and guiding the AI to a more reliable, professionally appropriate response.")
    if st.button("🔄 Reset",use_container_width=True):
        for k in ["pb_role","pb_task","pb_fmt","pb_out","pb_tone","pb_constr","pb_ctx","pb_extra","pb_gen","pb_scen"]:
            st.session_state.pop(k,None)
        st.rerun()
    ibox("Walk participants through each dropdown. Show the weak vs strong comparison on the projector. Ask: 'What element makes the biggest difference in your domain?'")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: NUDGES LAB
# ─────────────────────────────────────────────────────────────────────────────

def page_nudges():
    st.title("📌 Prewritten Nudges Lab")
    nudges=load_csv(str(BASE_DIR / "data" / "nudges.csv"))
    if not nudges:
        st.error(f"nudges.csv not found at: {BASE_DIR / 'data' / 'nudges.csv'}"); return
    cats=sorted({n["category"] for n in nudges})
    cat=sel_blank("Category",cats,key="ncat")
    filt=nudges if cat=="— select —" else [n for n in nudges if n["category"]==cat]
    sel_nudges=[]
    if cat!="— select —":
        cols=st.columns(2)
        for i,n in enumerate(filt):
            with cols[i%2]:
                if st.checkbox(f"**{n['nudge']}**\n_{n['when_to_use']}_",key=f"nc_{i}_{cat}"):
                    sel_nudges.append(n["nudge"])
    else:
        empty_st("📌","Select a category above to browse nudges.")
    base=st.text_area("Base text (optional):",placeholder="Your existing prompt or notes…",height=90,key="nbase")
    if sel_nudges:
        combined=(f"{base.strip()} "+" ".join(sel_nudges)).strip()
        st.markdown('<div class="nudge-chip-container">'+"".join(f'<span class="nudge-chip">{n}</span>' for n in sel_nudges)+"</div>",unsafe_allow_html=True)
        prompt_box(combined,"Nudge Combination")
    ibox("Demonstrate combining 2–3 nudges. Show how the same base prompt changes when different nudges are applied.")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DOCUMENT INTELLIGENCE LAB
# ─────────────────────────────────────────────────────────────────────────────

def _extract_text(up):
    name=up.name.lower()
    try:
        if name.endswith(".txt") or name.endswith(".csv"):
            return up.read().decode("utf-8",errors="ignore")
        if name.endswith(".pdf"):
            if not HAS_PYPDF: return "[pypdf not installed]"
            r=pypdf.PdfReader(io.BytesIO(up.read()))
            return "\n".join(p.extract_text() or "" for p in r.pages)
        if name.endswith(".docx"):
            if not HAS_DOCX: return "[python-docx not installed]"
            doc=DocxDocument(io.BytesIO(up.read()))
            return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        return f"[Error: {e}]"
    return "[Unsupported file type]"


def _keywords(text,n=10):
    stop={"that","this","with","from","have","been","will","each","they","their","when","also","more","than","should","which","would","about","into","were","some"}
    freq={}
    for w in re.findall(r'\b[A-Za-z]{4,}\b',text):
        wl=w.lower()
        if wl not in stop: freq[wl]=freq.get(wl,0)+1
    return [w for w,_ in sorted(freq.items(),key=lambda x:-x[1])[:n]]


def _summary(text,n=3):
    s=re.split(r'(?<=[.!?])\s+',text.strip())
    return " ".join(s[:n]) if s else text[:400]


def page_doc_lab():
    st.title("📄 Document Intelligence Lab")
    st.markdown('<div class="warning-box">⚠️ <strong>Safety:</strong> Upload only classroom-safe, synthetic, public, or approved material. Do not upload confidential, personal, or sensitive documents. All processing is local — no data leaves your device.</div>',unsafe_allow_html=True)
    sn=[s[0] for s in DOCUMENT_SAMPLES]
    chosen_s=sel_blank("Load a sample document",sn,key="ds")
    st_=DOCUMENT_SAMPLES
    s_text=""
    if chosen_s!="— select —":
        s_text=next(s[1] for s in st_ if s[0]==chosen_s)
        st.info(f"Loaded: *{chosen_s}*")
    up=st.file_uploader("Or upload PDF, DOCX, TXT, CSV",type=["pdf","docx","txt","csv"],key="dup")
    doc=""
    if up:
        doc=_extract_text(up)
        st.success(f"✅ {len(doc)} chars from **{up.name}**")
    elif s_text:
        doc=s_text
    if doc:
        with st.expander("📖 Extracted Text"):
            st.text(doc[:2000]+("…" if len(doc)>2000 else ""))
        kws=_keywords(doc)
        st.markdown("**Keywords:** "+"".join(f'<span class="badge">{k}</span> ' for k in kws),unsafe_allow_html=True)
        st.markdown("---")
        TMPL_TYPES=["Executive Brief","Action Points","Risk Checklist","Stakeholder Note","Discussion Questions","Meeting Agenda"]
        ttype=sel_blank("Template type",TMPL_TYPES,key="dtt")
        if ttype!="— select —":
            kw_str=", ".join(kws[:5]); summ=_summary(doc)
            TMPLS={
                "Executive Brief":f"Act as a senior analyst. Based on:\n\"{summ}\"\n\nWrite a 250-word executive brief: key messages, implications, one recommended action. Formal language. Themes: {kw_str}.",
                "Action Points":f"Act as a project coordinator. From:\n\"{summ}\"\n\nExtract 5 action points as a numbered list with action, responsible party, deadline category. Themes: {kw_str}.",
                "Risk Checklist":f"Act as a risk officer. Review:\n\"{summ}\"\n\nIdentify 5 risks/compliance concerns as a checklist: risk description, likelihood (L/M/H), mitigation. Themes: {kw_str}.",
                "Stakeholder Note":f"Act as a communications officer. Based on:\n\"{summ}\"\n\nDraft a 150-word stakeholder note: context, key message, one call to action. Themes: {kw_str}.",
                "Discussion Questions":f"Act as a facilitator. Based on:\n\"{summ}\"\n\nGenerate 5 discussion questions for an experienced management audience. Themes: {kw_str}.",
                "Meeting Agenda":f"Act as an executive assistant. Based on:\n\"{summ}\"\n\nDraft a 60-minute agenda: items, time allocations, desired outcomes. Themes: {kw_str}.",
            }
            prompt_box(TMPLS[ttype],f"Document Lab — {ttype}")
    else:
        empty_st("📄","Load a sample or upload a file above.")
    ibox("Use sample documents for live demonstration. Show how the same doc can generate different prompt types. Ask: which output needs the most human review?")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ACTIVITY STUDIO
# ─────────────────────────────────────────────────────────────────────────────

def page_activity():
    st.title("🎯 Activity Studio")
    _csv_path = BASE_DIR / "data" / "classroom_activities.csv"
    if st.session_state.get("instructor_view"):
        st.caption(f"📂 Looking for: `{_csv_path}` — exists: `{_csv_path.exists()}`")
    acts=load_csv(str(_csv_path))
    if not acts:
        st.error(f"Could not load `classroom_activities.csv`.")
        st.code(f"Expected path: {_csv_path}\nFile exists: {_csv_path.exists()}\n\ndata/ folder contents:\n" +
                "\n".join(str(f.name) for f in (BASE_DIR / "data").iterdir()) if (BASE_DIR / "data").exists() else "data/ folder not found")
        return
    titles=[a.get("title",f"Activity {i+1}") for i,a in enumerate(acts)]
    ch=sel_blank("Choose an activity",titles,key="act_ch")
    if ch=="— select —":
        empty_st("🎯","Select an activity above."); footer(); return
    act=next(a for a in acts if a.get("title")==ch)
    c1,c2,c3=st.columns(3)
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-value">⏱ {act.get("duration_minutes","—")} min</div><div class="metric-label">Duration</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-value">🎯 {act.get("activity_type","—")}</div><div class="metric-label">Type</div></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-value">👤 Individual</div><div class="metric-label">Mode</div></div>',unsafe_allow_html=True)
    st.markdown(f"**Objective:** {act.get('objective','—')}")
    st.markdown("---")
    with st.expander("📋 Instructions",expanded=True): st.markdown(act.get("instructions","—"))
    with st.expander("📝 Sample Input"): st.code(act.get("sample_input","—"),language=None)
    with st.expander("✅ Ideal Output"): st.markdown(act.get("ideal_output","—"))
    st.info(f"💬 **Debrief:** {act.get('debrief_question','—')}")
    if st.session_state.get("instructor_view"):
        st.markdown(f'<div class="instructor-note">🎓 <strong>Facilitation Note:</strong> {act.get("facilitation_note","—")}</div>',unsafe_allow_html=True)
    st.markdown("### ✍️ Participant Workspace")
    resp=st.text_area("Write your response here:",height=140,key=f"aresp_{ch}")
    if resp:
        st.download_button("⬇ Download Response",resp,f"activity_{ch[:20].replace(' ','_')}.txt",use_container_width=True)
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PROMPT LIBRARY
# ─────────────────────────────────────────────────────────────────────────────

def page_prompt_lib():
    st.title("📚 Prompt Library")
    prompts=load_csv(str(BASE_DIR / "data" / "prompt_library.csv"))
    if not prompts:
        st.warning(f"prompt_library.csv not found at: {BASE_DIR / 'data' / 'prompt_library.csv'}"); return
    cats=sorted({p.get("category","") for p in prompts})
    risks=sorted({p.get("risk_level","") for p in prompts})
    c1,c2=st.columns(2)
    with c1: cf=sel_blank("Category",cats,key="plcat")
    with c2: rf=sel_blank("Risk level",risks,key="plrisk")
    filt=prompts
    if cf!="— select —": filt=[p for p in filt if p.get("category")==cf]
    if rf!="— select —": filt=[p for p in filt if p.get("risk_level")==rf]
    if not filt:
        empty_st("📚","No prompts match the filters."); return
    for p in filt:
        rc={"Low":"#065F46","Medium":"#92400E","High":"#991B1B"}.get(p.get("risk_level",""),"#374151")
        with st.expander(f"📝  {p.get('title','—')}"):
            st.markdown(f"**Category:** {p.get('category','—')} | **Tool:** {p.get('tool','—')} | **Output:** {p.get('output_type','—')}")
            st.markdown(f'<span class="badge" style="background:{rc}">Risk: {p.get("risk_level","—")}</span>',unsafe_allow_html=True)
            st.code(p.get("prompt","—"),language=None)
            if p.get("warning"):
                st.markdown(f'<div class="warning-box">⚠️ {p["warning"]}</div>',unsafe_allow_html=True)
            prompt_box(p.get("prompt",""),f"Library — {p.get('title','')}")
    ibox("Ask participants to select one prompt, adapt it for their domain, and share the adaptation.")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: RESPONSIBLE AI
# ─────────────────────────────────────────────────────────────────────────────

def _classify(text):
    tl=text.lower()
    checks={
        "Privacy":            (["personal","confidential","private","sensitive","identity","personnel","medical","health record"],"High"),
        "Hallucination":      (["accurate","fact","verify","source","cite","statistics"],"Medium"),
        "Bias":               (["hire","promote","select","rank","score","screen","assess","evaluate"],"Medium"),
        "Overreliance":       (["automatically","without review","final decision","approve","sign off","authorise"],"High"),
        "Confidentiality":    (["classified","restricted","internal","not public","official use only"],"High"),
        "Decision Automation":(["automate","auto-approve","automatically decide","replace human","no oversight"],"High"),
        "Reputational":       (["publish","share externally","social media","press","release","public statement"],"Medium"),
    }
    lp={"Low":0,"Medium":1,"High":2}
    overall="Low"; details=[]
    for rn,(kws,lv) in checks.items():
        if any(k in tl for k in kws):
            details.append((rn,lv))
            if lp[lv]>lp[overall]: overall=lv
    return {"overall":overall,"details":details}


def page_responsible():
    st.title("🔒 Responsible AI & Risk Classifier")
    tab1,tab2,tab3=st.tabs(["📋 Core Principles","🔍 Risk Classifier","🏛️ Governance"])
    with tab1:
        rules=load_csv(str(BASE_DIR / "data" / "responsible_ai_rules.csv"))
        if rules:
            for r in rules:
                rc={"Low":"#065F46","Medium":"#92400E","High":"#991B1B"}.get(r.get("classification",""),"#374151")
                with st.expander(f"**{r.get('rule_title','—')}** — {r.get('category','')}"):
                    st.markdown(r.get("description","—"))
                    st.markdown(f"**Risk Indicators:** {r.get('risk_indicators','—')}")
                    st.markdown(f"**Mitigation:** {r.get('mitigation','—')}")
                    st.markdown(f"**Example:** {r.get('example_scenario','—')}")
                    st.markdown(f'<span class="badge" style="background:{rc}">{r.get("classification","—")}</span>',unsafe_allow_html=True)
        else:
            empty_st("📋","responsible_ai_rules.csv not found.")
    with tab2:
        st.markdown("### 🔍 Scenario Risk Classifier")
        preset_names=[r[0] for r in RISK_SCENARIOS]
        cp=sel_blank("Load a preset scenario",preset_names,key="rp")
        pt=cp if cp!="— select —" else ""
        inp=st.text_area("Describe the AI use scenario:",value=pt,height=90,key="rinp")
        if st.button("🔍 Classify Risk",type="primary",use_container_width=True):
            if not inp.strip():
                st.warning("Enter or select a scenario first.")
            else:
                res=_classify(inp)
                known=next((r for r in RISK_SCENARIOS if r[0].lower() in inp.lower()),None)
                if known: res["overall"]=known[1]; res["note"]=known[2]
                else: res["note"]=""
                cm={"Low":"#065F46","Medium":"#92400E","High":"#991B1B"}
                oc=cm.get(res["overall"],"#374151")
                st.markdown(f'<div style="background:{oc};color:white;padding:1rem;border-radius:.75rem;font-size:1.25rem;font-weight:700;text-align:center">Overall Risk: {res["overall"]}</div>',unsafe_allow_html=True)
                if res.get("note"): st.info(res["note"])
                if res["details"]:
                    st.markdown("**Detected risk dimensions:**")
                    for rn,rl in res["details"]:
                        st.markdown(f'<span class="badge" style="background:{cm.get(rl,"#374151")}">{rn}: {rl}</span> ',unsafe_allow_html=True)
                mits={"High":"Do not proceed without written approval. Apply data-minimisation, ensure human review, consult compliance officer.",
                      "Medium":"Proceed with caution. Review outputs before sharing, avoid uploading personal/restricted data, have a qualified person verify AI content.",
                      "Low":"Safe to proceed with standard good practice: review before use, disclose AI assistance, retain human accountability."}
                st.markdown(f'<div class="info-box">💡 <strong>Mitigation:</strong> {mits[res["overall"]]}</div>',unsafe_allow_html=True)
                st.info("💬 **Reflection:** What would responsible use of AI look like in this scenario?")
    with tab3:
        st.markdown("### 🏛️ AI Governance Framework")
        fw=[("Data Privacy","Use only approved, anonymised data. Never share personal or restricted data with public AI tools."),("Human Accountability","AI assists — humans decide. All AI outputs require qualified human review before action."),("Transparency","Disclose AI use when sharing outputs. Label AI-assisted documents clearly."),("Bias Awareness","Check AI outputs for unintentional bias, especially in HR, evaluation, and communication tasks."),("Proportionality","Match the AI tool to the risk level of the task. High-stakes decisions need higher oversight."),("Audit Trail","Keep records of AI-assisted work, inputs used, and decisions taken.")]
        for title,desc in fw:
            st.markdown(f'<div class="info-box"><strong>{title}:</strong> {desc}</div>',unsafe_allow_html=True)
    ibox("Run the classifier live with preset scenarios. Ask: 'Would you classify this differently?' Challenge the group to propose a safer version of any High-risk scenario.")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CASELET SIMULATOR
# ─────────────────────────────────────────────────────────────────────────────

def page_caselets():
    st.title("📋 Caselet Simulator")
    caselets=load_csv(str(BASE_DIR / "data" / "caselets.csv"))
    if not caselets:
        st.warning(f"caselets.csv not found at: {BASE_DIR / 'data' / 'caselets.csv'}"); return
    titles=[c.get("title",f"Caselet {i+1}") for i,c in enumerate(caselets)]
    ch=sel_blank("Choose a caselet",titles,key="cc")
    if ch=="— select —":
        empty_st("📋","Select a caselet above."); footer(); return
    cas=next(c for c in caselets if c.get("title")==ch)
    st.markdown(f"## {cas.get('title','—')}")
    st.markdown(f'<div class="info-box"><strong>Situation:</strong> {cas.get("situation","—")}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="warning-box"><strong>Dilemma:</strong> {cas.get("dilemma","—")}</div>',unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        roles=[r.strip() for r in cas.get("role_options","Manager").split(",") if r.strip()]
        crole=radio_blank("Select your role:",roles,key=f"cr_{ch}")
    with c2:
        paths=[p.strip() for p in cas.get("decision_paths","Option A,Option B").split(",") if p.strip()]
        cpath=radio_blank("Select a decision path:",paths,key=f"cp_{ch}")
    if crole and cpath:
        st.markdown("### 📋 Tasks"); st.markdown(cas.get("tasks","—"))
        st.markdown('<div class="warning-box">'+cas.get("risks","—")+"</div>",unsafe_allow_html=True)
        ptemplate=f"Act as a {crole}. Scenario: {cas.get('situation','')} Decision path: {cpath}. {cas.get('tasks','')} Provide a structured response suitable for executive review."
        st.markdown("### 🛠️ Suggested Prompt")
        prompt_box(ptemplate,f"Caselet — {cas.get('title','')}")
        resp=st.text_area("Draft your analysis:",height=140,key=f"cresp_{ch}")
        if resp:
            ws=f"Caselet: {cas.get('title','')}\nRole: {crole}\nPath: {cpath}\n\nSituation: {cas.get('situation','')}\nDilemma: {cas.get('dilemma','')}\n\nMy Response:\n{resp}\n\nDebrief:\n{cas.get('debrief','')}"
            st.download_button("⬇ Download Worksheet",ws,f"caselet_{ch[:20].replace(' ','_')}.txt",use_container_width=True)
        with st.expander("💬 Debrief Questions"): st.markdown(cas.get("debrief","—"))
        st.info(f"💬 **Expected AI Output:** {cas.get('expected_output','—')}")
    ibox("Give participants 8–10 min to read the situation and select a role/path. Bring 2–3 responses to the group. Use debrief questions to close.")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CAPSTONE
# ─────────────────────────────────────────────────────────────────────────────

def page_capstone():
    st.title("🗺 Capstone Workflow Studio")
    st.caption("Design a complete AI-enabled management workflow step by step.")
    st.markdown("### Step 1: Scenario")
    preset=sel_blank("Select a scenario",CAPSTONE_PRESETS,key="cap_p")
    custom=st.text_input("Or describe your own:",placeholder="Your scenario…",key="cap_c")
    scenario=custom.strip() if custom.strip() else (preset if preset!="— select —" else "")
    if not scenario:
        empty_st("🗺","Select or type a capstone scenario."); footer(); return
    st.markdown("### Step 2: Workflow Stages")
    chosen=st.multiselect("Select relevant workflow stages:",[w[0] for w in WORKFLOWS],key="cap_stages")
    if chosen:
        st.markdown("### Step 3: Workflow Overview")
        for s in chosen:
            d=next(w[1] for w in WORKFLOWS if w[0]==s)
            st.markdown(f'<div class="info-box"><strong>{s}:</strong> {d}</div>',unsafe_allow_html=True)
        fp=(f"Act as a management consultant. Design a complete AI-enabled workflow for: '{scenario}'. Stages:\n"
            +"\n".join(f"  {i+1}. {s}" for i,s in enumerate(chosen))
            +"\n\nFor each stage: describe the task, where GenAI assists, expected output, and human oversight required. Professional management tone.")
        st.markdown("### 🛠️ Capstone Prompt")
        prompt_box(fp,"Capstone Workflow")
    st.markdown("### Step 4: Reflection")
    rq=sel_blank("Reflection question",REFLECTION_PRESETS,key="cap_rq")
    if rq!="— select —":
        st.info(f"💬 {rq}")
        st.text_area("Your reflection:",height=90,key="cap_rt")
    ibox("Allow 15–20 minutes. Encourage participants to draw their workflow on paper first. Close with one group sharing their capstone prompt.")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: READINESS CHECKLIST
# ─────────────────────────────────────────────────────────────────────────────

def page_readiness():
    st.title("✅ AI Readiness Checklist")
    st.caption("Assess your organisation's readiness to adopt GenAI tools responsibly.")
    sections={
        "🔒 Data & Privacy":["We have identified which data categories are safe to use with AI tools.","We have a data classification policy that covers AI use.","Staff are aware of what should NOT be uploaded to public AI tools.","We have a process for anonymising data before AI processing."],
        "👥 People & Skills":["Managers understand what Generative AI can and cannot do.","At least one team member has hands-on prompt engineering experience.","We have a plan to train staff on responsible AI use.","Staff know who to consult if an AI use case seems risky."],
        "⚙️ Process & Governance":["We have (or are drafting) an AI acceptable use policy.","AI-assisted outputs are reviewed by a human before circulation.","We track which AI tools are being used for what purposes.","We have a process for raising concerns about AI use."],
        "📊 Performance & Oversight":["We evaluate AI outputs against defined quality criteria.","We have a mechanism to detect and correct AI errors.","Leadership is aware of GenAI use within the organisation.","We conduct periodic reviews of AI-assisted processes."],
    }
    total=sum(len(v) for v in sections.values()); checked=0
    for sec,items in sections.items():
        st.markdown(f"#### {sec}")
        for it in items:
            if st.checkbox(it,key=f"rl_{it[:30]}"): checked+=1
    score=int((checked/total)*100)
    color="#065F46" if score>=75 else "#92400E" if score>=40 else "#991B1B"
    st.markdown("---")
    st.markdown(f"### Readiness Score: **{score}%** ({checked}/{total})")
    msg="✅ Strong readiness — proceed with structured AI adoption." if score>=75 else "⚠️ Partial readiness — address gaps before broad deployment." if score>=40 else "🔴 Early stage — prioritise awareness and policy development first."
    st.markdown(f'<div style="background:{color};color:white;padding:.75rem 1rem;border-radius:.5rem;font-weight:600">{msg}</div>',unsafe_allow_html=True)
    txt=f"AI Readiness Checklist\nScore: {score}% ({checked}/{total})\n\n"+"\n".join(f"\n{s}\n"+"".join(f"  [ ] {it}\n" for it in items) for s,items in sections.items())
    st.download_button("⬇ Download Checklist",txt,"ai_readiness_checklist.txt","text/plain",use_container_width=True)
    ibox("Ask participants to complete individually, then compare in pairs. Discussion: 'Which gap is most urgent for your team?'")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: QUIZ
# ─────────────────────────────────────────────────────────────────────────────

def page_quiz():
    st.title("❓ Quiz & Reflection")
    qs=load_csv(str(BASE_DIR / "data" / "quiz_questions.csv"))
    if not qs:
        st.warning(f"quiz_questions.csv not found at: {BASE_DIR / 'data' / 'quiz_questions.csv'}"); return
    diffs=sorted({q.get("difficulty","") for q in qs})
    themes=sorted({q.get("theme","") for q in qs})
    c1,c2,c3=st.columns(3)
    with c1: df=sel_blank("Difficulty",diffs,key="qdf")
    with c2: tf=sel_blank("Theme",themes,key="qtf")
    with c3: mx=st.slider("Max questions",5,min(75,len(qs)),10,key="qmx")
    filt=qs
    if df!="— select —": filt=[q for q in filt if q.get("difficulty")==df]
    if tf!="— select —": filt=[q for q in filt if q.get("theme")==tf]
    filt=filt[:mx]
    if not filt:
        empty_st("❓","No questions match the filters."); return
    cm_mode=st.session_state.get("classroom_mode",False)
    if cm_mode:
        st.markdown('<div class="info-box">📽 <strong>Classroom Mode:</strong> Answers are hidden until the instructor reveals them.</div>',unsafe_allow_html=True)
    score_c=0; answered=0
    for i,q in enumerate(filt):
        dc={"Basic":"#065F46","Intermediate":"#92400E","Executive":"#1A3C6E"}.get(q.get("difficulty",""),"#374151")
        st.markdown(f'<div style="border-left:4px solid {dc};padding:.5rem 1rem;background:var(--surface);border-radius:.5rem;margin-bottom:.25rem"><span class="badge" style="background:{dc};font-size:.7rem">{q.get("difficulty","")}</span> <span style="font-size:.7rem;color:var(--muted)">🏷 {q.get("theme","")}</span><br><strong>Q{i+1}. {q.get("question","")}</strong></div>',unsafe_allow_html=True)
        qt=q.get("type","MCQ").strip()
        if qt in ("MCQ","ScenarioMCQ"):
            opts={k:v for k,v in {"A":q.get("option_a",""),"B":q.get("option_b",""),"C":q.get("option_c",""),"D":q.get("option_d","")}.items() if v}
            ca=radio_blank(f"Answer (Q{i+1}):",[f"{k}. {v}" for k,v in opts.items()],key=f"qa_{i}")
        elif qt=="TrueFalse":
            ca=radio_blank(f"True or False (Q{i+1}):",["True","False"],key=f"qa_{i}")
        else:
            ca=st.text_area(f"Your reflection (Q{i+1}):",height=70,key=f"qa_{i}")
        rk=f"rev_{i}"
        if not cm_mode:
            if st.button(f"👁 Reveal Answer (Q{i+1})",key=f"rb_{i}"):
                st.session_state["quiz_reveals"][rk]=True
        if st.session_state["quiz_reveals"].get(rk) and not cm_mode:
            correct=q.get("answer",""); expl=q.get("explanation","")
            st.markdown(f'<div class="success-box">✅ <strong>Answer: {correct}</strong><br>{expl}</div>',unsafe_allow_html=True)
            if ca and qt in ("MCQ","ScenarioMCQ","TrueFalse"):
                if (ca[0] if ca else "")==correct: score_c+=1
            answered+=1
        if cm_mode and st.session_state.get("instructor_view"):
            if st.button(f"🎓 Reveal to Class (Q{i+1})",key=f"clsrv_{i}"):
                st.session_state["quiz_reveals"][rk]=True
            if st.session_state["quiz_reveals"].get(rk):
                st.markdown(f'<div class="success-box">✅ Answer: {q.get("answer","")} — {q.get("explanation","")}</div>',unsafe_allow_html=True)
        st.markdown("---")
    if answered>0 and not cm_mode:
        pct=int((score_c/answered)*100)
        st.markdown(f"### 🏆 Score: {score_c}/{answered} ({pct}%)")
    ibox("Run 10 questions per round. Use classroom mode to hide answers and reveal them after group discussion.")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: RESOURCE HUB
# ─────────────────────────────────────────────────────────────────────────────

def page_resources():
    st.title("📦 Resource Hub")
    tab1,tab2,tab3=st.tabs(["📋 Templates","🆓 Free Tools Guide","⬇ Bulk Download"])
    with tab1:
        tmpls=load_csv(str(BASE_DIR / "data" / "resource_templates.csv"))
        if not tmpls:
            st.warning("resource_templates.csv not found.")
        else:
            for t in tmpls:
                with st.expander(f"📄  {t.get('title','—')} — {t.get('category','')}"):
                    st.markdown(t.get("description","—"))
                    c=t.get("content","")
                    if c:
                        st.download_button(f"⬇ Download",c,f"{t.get('title','template').replace(' ','_').lower()}.txt","text/plain",use_container_width=True)
    with tab2:
        st.markdown(FREE_TOOLS_MD)
        st.download_button("⬇ Download Guide",FREE_TOOLS_MD,"free_ai_tools_guide.md","text/markdown",use_container_width=True)
    with tab3:
        all_t=load_csv(str(BASE_DIR / "data" / "resource_templates.csv")) or []
        sep="\n\n"+"="*60+"\n\n"
        combined=sep.join(f"# {t.get('title','')}\n{t.get('description','')}\n\n{t.get('content','')}" for t in all_t)+sep+FREE_TOOLS_MD
        st.download_button("⬇ Download All Resources",combined,"genai_resources.txt","text/plain",use_container_width=True)
    ibox("Distribute the free tools guide at the start of the session. Have participants download the Responsible AI Checklist and Prompt Quality Rubric as take-home references.")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: INSTRUCTOR MODE
# ─────────────────────────────────────────────────────────────────────────────

def page_instructor():
    st.title("🎓 Instructor Mode")
    if not st.session_state.get("instructor_view"):
        st.info("Enable **Instructor View** in the sidebar to see all facilitation notes.")
    sessions=[
        ("Session 1 (45 min)","Foundation","Home → Roadmap → Concepts. Cover Stages 1–2. Run 5 quiz questions."),
        ("Session 2 (60 min)","Prompt Engineering","Prompt Builder → Nudges Lab. Hands-on: participants build 3 prompts each."),
        ("Session 3 (60 min)","Use Cases","Executive Use Cases → Document Lab. Activity: adapt a sample prompt."),
        ("Session 4 (45 min)","Responsible AI","Responsible AI → Risk Classifier. Live classification of 3 preset scenarios."),
        ("Session 5 (60 min)","Caselet & Capstone","Caselet Simulator (2 caselets) → Capstone Workflow. Debrief with group."),
        ("Session 6 (30 min)","Reflection & Close","Quiz (10 questions) → Readiness Checklist → Reflection. Download resources."),
    ]
    st.markdown("### 🗓️ Suggested Session Flow")
    for title,name,desc in sessions:
        with st.expander(f"**{title}: {name}**"): st.markdown(desc)
    st.markdown("---")
    st.markdown("### 🕹️ Classroom Controls")
    c1,c2=st.columns(2)
    with c1:
        if st.button("📽 Enable Classroom Mode",use_container_width=True): st.session_state["classroom_mode"]=True; st.success("Enabled.")
    with c2:
        if st.button("📽 Disable Classroom Mode",use_container_width=True): st.session_state["classroom_mode"]=False; st.success("Disabled.")
    st.markdown("---")
    st.markdown("### 💾 Saved Prompts")
    if st.session_state.saved_prompts:
        for i,p in enumerate(st.session_state.saved_prompts,1): st.markdown(f"**{i}.** {p}")
        if st.button("🗑 Clear All"): st.session_state.saved_prompts=[]; st.rerun()
    else:
        empty_st("💾","No prompts saved yet.")
    st.markdown("---")
    st.markdown("### 📋 Facilitation Reminders")
    for r in [
        "Always remind participants to use only synthetic or public data in the portal.",
        "In classroom mode, quiz answers are hidden until you reveal them manually.",
        "The Prompt Builder's 'weak vs strong' comparison works well on the projector.",
        "Caselet Simulator works best with 8–10 min individual time before group debrief.",
        "Risk Classifier presets make good 5-min discussion starters.",
        "Encourage participants to download Resource Hub materials as take-home references.",
    ]: st.markdown(f"✅ {r}")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ABOUT
# ─────────────────────────────────────────────────────────────────────────────

def page_about():
    st.title("👤 About the Developer")
    st.markdown(f'<div class="info-box"><h3>Dr. Alok Tiwari</h3><p><strong>Assistant Professor — Big Data Analytics</strong><br>Goa Institute of Management, Panaji, Goa, India</p><p>Dr. Tiwari holds a PhD in Biomedical Engineering from IIT (BHU), Varanasi, with doctoral research in medical imaging AI, transfer learning, and weakly supervised learning for clinical applications. His current work spans healthcare AI, MLOps, responsible AI governance, and management education technology.</p><p>This portal was developed to bring practical, classroom-safe, and interactive GenAI learning to management professionals — grounded in real use cases, responsible use principles, and hands-on prompt practice.</p><p>🌐 <a href="{DEVELOPER_URL}" target="_blank">{DEVELOPER_URL}</a></p></div>',unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1: st.markdown("**What it uses:**\n- Python + Streamlit\n- pypdf, python-docx\n- Rule-based local processing\n- CSV-driven content\n- Custom CSS")
    with c2: st.markdown("**What it does NOT use:**\n- No external AI API\n- No paid service\n- No user login\n- No cloud database\n- No data transmission")
    footer()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

PAGE_FN = {
    "home": page_home, "roadmap": page_roadmap, "concepts": page_concepts,
    "use_cases": page_use_cases, "prompt_builder": page_prompt_builder,
    "nudges": page_nudges, "doc_lab": page_doc_lab, "activity": page_activity,
    "prompt_lib": page_prompt_lib, "responsible": page_responsible,
    "caselets": page_caselets, "capstone": page_capstone,
    "readiness": page_readiness, "quiz": page_quiz,
    "resources": page_resources, "instructor": page_instructor, "about": page_about,
}


def main():
    init_state()
    sel = render_sidebar()
    if st.session_state.get("classroom_mode"):
        st.markdown("<style>body,.stMarkdown,.stText{font-size:1.15rem!important}h1{font-size:2.2rem!important}h2{font-size:1.7rem!important}</style>",unsafe_allow_html=True)
    fn = PAGE_FN.get(sel, page_home)
    fn()


if __name__ == "__main__":
    main()

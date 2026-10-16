import re
from io import BytesIO
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="ResumeIQ — ATS Studio", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

# ResumeIQ design system: editorial typography, deep ink surfaces, electric mint accents,
# clear information hierarchy, responsive cards, and reduced-motion support.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--ink:#080d16;--panel:#101927;--panel2:#141f30;--line:rgba(177,199,226,.13);--muted:#93a2b8;--text:#f2f6fc;--mint:#9dffd3;--blue:#87b8ff}
html,body,[class*="css"]{font-family:'Manrope',sans-serif}
.stApp{background:radial-gradient(ellipse at 80% 0%,rgba(47,105,145,.18),transparent 38%),radial-gradient(ellipse at 5% 30%,rgba(61,140,111,.10),transparent 32%),var(--ink);color:var(--text)}
[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"]{background:#0b121e;border-right:1px solid var(--line)}
[data-testid="stSidebar"] *{color:var(--text)}
.block-container{padding-top:2rem;padding-bottom:3rem;max-width:1450px}
.hero{border:1px solid var(--line);border-radius:26px;padding:30px 32px;background:linear-gradient(120deg,rgba(23,39,57,.94),rgba(13,24,37,.72));position:relative;overflow:hidden;margin-bottom:24px}
.hero:after{content:'';position:absolute;width:260px;height:260px;right:-85px;top:-120px;border-radius:50%;background:radial-gradient(circle,rgba(157,255,211,.20),rgba(135,184,255,.04) 60%,transparent 72%);pointer-events:none}
.eyebrow{font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:.16em;font-size:.72rem;color:var(--mint)}
.hero h1{font-size:clamp(2.1rem,4vw,3.5rem);line-height:1.04;letter-spacing:-.055em;margin:.7rem 0 .7rem;font-weight:800;color:#f5f8ff}
.hero p{max-width:720px;color:#aebbd0;font-size:1rem;line-height:1.7;margin:0}
.pill{display:inline-block;padding:6px 10px;border:1px solid rgba(157,255,211,.25);border-radius:999px;color:var(--mint);font-size:.76rem;background:rgba(157,255,211,.06);margin:0 6px 8px 0}
.section-kicker{font-family:'DM Mono',monospace;font-size:.72rem;letter-spacing:.13em;text-transform:uppercase;color:var(--mint);margin:1rem 0 .5rem}
.panel{background:linear-gradient(145deg,rgba(20,31,48,.94),rgba(13,22,35,.92));border:1px solid var(--line);border-radius:18px;padding:20px 22px;height:100%}
.panel h3{font-size:1rem;margin:0 0 8px;color:#f1f6ff}
.metric-label{font-size:.75rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
.metric-value{font-size:2.25rem;font-weight:800;letter-spacing:-.06em;color:#f4f7fc;line-height:1.3}
.metric-foot{font-size:.78rem;color:var(--muted);margin-top:4px}
.mini-label{font-family:'DM Mono',monospace;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.skill{display:inline-block;border-radius:8px;padding:7px 10px;font-size:.8rem;margin:4px 5px 3px 0;border:1px solid var(--line);background:rgba(255,255,255,.035);color:#dbe7f7}
.skill.good{border-color:rgba(157,255,211,.28);color:var(--mint);background:rgba(157,255,211,.07)}
.skill.miss{border-color:rgba(255,178,143,.26);color:#ffc09e;background:rgba(255,178,143,.06)}
div.stButton>button{border-radius:11px;border:1px solid rgba(157,255,211,.32);background:linear-gradient(110deg,#b2ffda,#8de9d3);color:#07150f;font-weight:800;min-height:2.8rem;transition:transform .18s ease,filter .18s ease}
div.stButton>button:hover{filter:brightness(1.05);transform:translateY(-1px)}
.stTextArea textarea,.stTextInput input,.stSelectbox div[data-baseweb="select"]{background:#0b1421!important;color:#eff6ff!important;border-color:var(--line)!important;border-radius:12px!important}
.stTabs [data-baseweb="tab-list"]{gap:8px}
.stTabs [data-baseweb="tab"]{background:#111c2b;border-radius:10px;padding:10px 16px}
.stTabs [aria-selected="true"]{background:#1c3341!important;color:var(--mint)!important}
div[data-testid="stFileUploader"]{border:1px dashed rgba(157,255,211,.3);border-radius:14px;padding:12px;background:rgba(157,255,211,.025)}
hr{border-color:var(--line)}
small,.muted{color:var(--muted)}
footer{visibility:hidden}
@media(max-width:700px){.block-container{padding:1rem}.hero{padding:22px}.hero h1{font-size:2.2rem}.metric-value{font-size:1.8rem}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
</style>
""", unsafe_allow_html=True)

STOPWORDS = set("""a an and are as at be been being by can could for from had has have he her hers him his how i if in into is it its may me more most my no not of on or our out over she should so than that the their them then there these they this those to too up us was we were what when where which who will with would you your experience experienced using use used strong excellent including etc""".split())
SKILL_BANK = [
    "python","java","javascript","typescript","sql","postgresql","mysql","mongodb","html","css","react","node.js","streamlit",
    "pandas","numpy","scikit-learn","machine learning","deep learning","llm","rag","langchain","openai","groq","api","rest api",
    "git","github","docker","aws","azure","gcp","linux","data analysis","data visualization","power bi","tableau","excel",
    "communication","leadership","problem solving","teamwork","project management","testing","pytest","fastapi","flask","django",
    "tensorflow","pytorch","nlp","computer vision","prompt engineering","generative ai","cloud computing","agile","ci/cd"
]
SECTION_PATTERNS = {
    "Contact details": [r"@[w.-]+.w+", r"(?:+?d[ds().-]{7,}d)"],
    "Summary / objective": [r"(summary|objective|profile|about me)"],
    "Education": [r"(education|academic|university|college|bachelor|b.?tech|degree)"],
    "Experience": [r"(experience|employment|internship|work history|professional experience)"],
    "Skills": [r"(skills|technical skills|competencies|technologies)"],
    "Projects": [r"(projects|personal projects|academic projects|portfolio)"],
    "Certifications": [r"(certifications|certificates|licenses)"],
}

def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()

def extract_pdf(uploaded_file):
    reader = PdfReader(BytesIO(uploaded_file.getvalue()))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

def tokens(text):
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", text.lower())) - STOPWORDS

def detect_skills(text):
    lowered = normalize(text)
    return sorted({skill for skill in SKILL_BANK if re.search(r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])", lowered)})

def section_results(text):
    lowered = text.lower()
    return {name: any(re.search(pattern, lowered) for pattern in patterns) for name, patterns in SECTION_PATTERNS.items()}

def score_resume(text, job_text=""):
    sections = section_results(text)
    section_score = round(sum(sections.values()) / len(sections) * 35)
    contact_score = 15 if sections["Contact details"] else 0
    skills = detect_skills(text)
    skill_score = min(25, round(len(skills) / 8 * 25))
    length_words = len(text.split())
    length_score = 10 if 250 <= length_words <= 1000 else (6 if 120 <= length_words <= 1400 else 2)
    bullet_score = 10 if re.search(r"(?m)^\s*[•●▪\-*]", text) else 4
    job_score = 0
    if job_text.strip():
        job_tokens = tokens(job_text)
        resume_tokens = tokens(text)
        job_score = round(20 * len(job_tokens & resume_tokens) / max(1, min(len(job_tokens), 40)))
    total = min(100, round(section_score + contact_score + skill_score + length_score + bullet_score))
    return {"total": total, "sections": sections, "skills": skills, "section_score": section_score, "contact_score": contact_score, "skill_score": skill_score, "length_score": length_score, "bullet_score": bullet_score, "job_score": job_score, "word_count": length_words}

def make_report(text, job_text, result, matched, missing, suggestions):
    lines = [
        "# ResumeIQ — Resume Review", "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "",
        f"## Estimated resume readiness: {result['total']}/100", "",
        "> This is a transparent heuristic review, not an official ATS score or hiring prediction.", "",
        f"- Word count: {result['word_count']}",
        f"- Detected skills: {', '.join(result['skills']) or 'None detected'}",
        f"- Job description keyword overlap: {len(matched)} matched; {len(missing)} not found",
        "", "## Section checks", ""
    ]
    lines.extend([f"- {'✓' if ok else '✗'} {name}" for name, ok in result["sections"].items()])
    lines += ["", "## Skills found in both resume and job description", "", ", ".join(matched) or "No overlap detected.", "", "## Job keywords to consider", "", ", ".join(missing) or "No obvious missing keywords from the detected skill list.", "", "## Suggested next steps", ""]
    lines.extend([f"- {s}" for s in suggestions])
    return "\n".join(lines)

with st.sidebar:
    st.markdown("### ◈ ResumeIQ")
    st.caption("CAREER TOOLKIT / 01")
    st.markdown("---")
    st.markdown("**Workspace**")
    page = st.radio("Navigate", ["ATS Studio", "How scoring works"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<span class="mini-label">PRIVACY FIRST</span>', unsafe_allow_html=True)
    st.caption("Your resume is processed in this app session. This demo does not save uploaded files to a database.")
    st.markdown("---")
    st.caption("Built for practical resume improvement. No API key required.")

if page == "How scoring works":
    st.markdown('<div class="hero"><div class="eyebrow">TRANSPARENT BY DESIGN</div><h1>Know what the score means.</h1><p>ResumeIQ uses visible, rule-based checks so you can understand and improve your resume without sending it to an external AI service.</p></div>', unsafe_allow_html=True)
    st.markdown("### Readiness score components")
    st.dataframe(pd.DataFrame([
        {"Check": "Resume sections", "Weight": "35 points", "What it checks": "Summary, education, experience, skills, projects, certifications, contact details"},
        {"Check": "Contact details", "Weight": "15 points", "What it checks": "Email and phone-like patterns"},
        {"Check": "Detected skills", "Weight": "25 points", "What it checks": "Known technical and transferable skills"},
        {"Check": "Resume length", "Weight": "10 points", "What it checks": "A broad word-count range"},
        {"Check": "Bullet structure", "Weight": "10 points", "What it checks": "Bullet-like formatting"},
    ]), hide_index=True, use_container_width=True)
    st.warning("This is not a real ATS parser. Different employers and applicant-tracking systems use different rules. Always review the actual job requirements.")
    st.stop()

st.markdown("""
<div class="hero">
  <div class="eyebrow">CAREER INTELLIGENCE / RESUME WORKSPACE</div>
  <h1>Your next opportunity<br>starts with clarity.</h1>
  <p>Audit your resume, compare it with a role, and turn missing keywords into a practical action plan. No paid API, no mystery score.</p>
  <div style="margin-top:18px"><span class="pill">PDF or pasted text</span><span class="pill">Role matching</span><span class="pill">Instant report</span><span class="pill">Private by design</span></div>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([0.92, 1.08], gap="large")
with left:
    st.markdown('<div class="section-kicker">01 / Your resume</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload resume PDF", type=["pdf"], help="Text-based PDFs work best. Scanned image PDFs may not contain extractable text.")
    resume_text = ""
    if uploaded:
        try:
            resume_text = extract_pdf(uploaded)
            if not resume_text:
                st.warning("No selectable text found. Try a text-based PDF or paste your resume below.")
        except Exception as exc:
            st.error(f"Could not read this PDF: {exc}")
    pasted = st.text_area("Or paste resume text", value="", height=245, placeholder="Paste your resume here — summary, skills, education, projects, experience...")
    if pasted.strip():
        resume_text = pasted.strip()
    use_sample = st.button("Load sample resume", use_container_width=True)
    if use_sample:
        st.session_state["sample_resume"] = """Pradeep Kumar Pullamsetty
pradeep@example.com | +91 98765 43210 | GitHub: github.com/pradeeppullamsetty

SUMMARY
Computer Science and Engineering student interested in Python, AI, and cloud computing. Enjoys building practical web applications and learning modern development tools.

EDUCATION
B.Tech Computer Science and Engineering
Expected graduation: 2027

TECHNICAL SKILLS
Python, SQL, Git, GitHub, Streamlit, HTML, CSS, data analysis, prompt engineering, generative AI

PROJECTS
AI Text Summarizer
- Built a Streamlit application to summarize text with a clean user interface.
- Added input validation and download-ready output.

LUMA Calculator
- Created a beginner-friendly calculator project to practice Python programming and interface design.

EXPERIENCE
Academic and self-directed project work

CERTIFICATIONS
Add relevant completed certifications here."""
        st.rerun()
    if "sample_resume" in st.session_state and not pasted.strip() and not uploaded:
        resume_text = st.session_state["sample_resume"]
        st.info("Sample resume loaded. Edit or replace it in the text area above to analyze your own resume.")
    st.markdown('<div class="section-kicker">02 / Target role</div>', unsafe_allow_html=True)
    job_title = st.text_input("Role title", placeholder="e.g. Junior Python Developer")
    job_text = st.text_area("Paste the job description", height=185, placeholder="Paste the responsibilities, qualifications, and skills from the job post...")
    analyze = st.button("Analyze resume  ↗", type="primary", use_container_width=True)

with right:
    st.markdown('<div class="section-kicker">YOUR ANALYSIS / PREVIEW</div>', unsafe_allow_html=True)
    if analyze:
        if len(resume_text.strip()) < 40:
            st.warning("Upload a PDF or paste at least a few lines of resume text first.")
        else:
            result = score_resume(resume_text, job_text)
            resume_skills = set(result["skills"])
            job_skills = set(detect_skills(job_text))
            matched = sorted(resume_skills & job_skills)
            missing = sorted(job_skills - resume_skills)
            if not job_text.strip():
                matched = []
                missing = []
            suggestions = []
            if not result["sections"]["Summary / objective"]: suggestions.append("Add a short summary tailored to the target role.")
            if not result["sections"]["Projects"]: suggestions.append("Add 2–3 projects with your contribution, tools, and measurable outcome.")
            if not result["sections"]["Experience"]: suggestions.append("Include internship, volunteering, freelance, or relevant academic experience where applicable.")
            if not result["sections"]["Skills"]: suggestions.append("Add a clearly labeled skills section with skills you can genuinely demonstrate.")
            if result["word_count"] < 250: suggestions.append("Add relevant detail to projects and experience; the resume may be too brief.")
            if result["word_count"] > 1000: suggestions.append("Consider tightening the resume and prioritizing role-relevant information.")
            if missing: suggestions.append("Review the missing job keywords and include only those that accurately reflect your skills.")
            if not suggestions: suggestions.append("Keep the content role-specific and quantify outcomes wherever you can do so truthfully.")
            st.session_state["analysis"] = {"result": result, "matched": matched, "missing": missing, "suggestions": suggestions, "resume_text": resume_text, "job_text": job_text, "job_title": job_title}
    data = st.session_state.get("analysis")
    if not data:
        st.markdown("""
        <div class="panel" style="min-height:310px;display:flex;flex-direction:column;justify-content:center">
          <div class="eyebrow">READY WHEN YOU ARE</div>
          <h3 style="font-size:1.7rem;margin-top:12px">Your career dashboard is waiting.</h3>
          <p style="color:#93a2b8;line-height:1.8">Add your resume and a job description, then run the analysis to reveal your readiness score, section checklist, skills overlap, and next best actions.</p>
          <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:16px"><span class="pill">01 · Scan</span><span class="pill">02 · Compare</span><span class="pill">03 · Improve</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        result = data["result"]
        score = result["total"]
        score_color = "#9dffd3" if score >= 75 else ("#87b8ff" if score >= 50 else "#ffc09e")
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"""<div class="panel"><div class="metric-label">Resume readiness</div><div class="metric-value" style="color:{score_color}">{score}<span style="font-size:1rem;color:#93a2b8"> / 100</span></div><div class="metric-foot">Rule-based estimate · not an ATS guarantee</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="panel"><div class="metric-label">Resume length</div><div class="metric-value">{result['word_count']:,}</div><div class="metric-foot">Words detected in your content</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        gauge = go.Figure(go.Indicator(mode="gauge+number", value=score, number={"suffix": "/100", "font": {"size": 28, "color": "#f2f6fc"}}, gauge={"axis": {"range": [0,100], "tickcolor": "#93a2b8"}, "bar": {"color": score_color}, "bgcolor": "rgba(255,255,255,.025)", "borderwidth": 0, "steps": [{"range":[0,50],"color":"rgba(255,192,158,.08)"},{"range":[50,75],"color":"rgba(135,184,255,.08)"},{"range":[75,100],"color":"rgba(157,255,211,.08)"}]}))
        gauge.update_layout(height=190, margin=dict(l=15,r=15,t=8,b=5), paper_bgcolor="rgba(0,0,0,0)", font_color="#f2f6fc")
        st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})
        if data["job_text"].strip():
            total_detected = len(set(detect_skills(data["job_text"])))
            overlap = round(len(data["matched"]) / max(1, total_detected) * 100)
            st.markdown(f'<div class="panel"><div class="metric-label">Detected skill overlap</div><div class="metric-value">{overlap}<span style="font-size:1rem;color:#93a2b8">%</span></div><div class="metric-foot">{len(data["matched"])} matching skills from {total_detected} detected in the job description</div></div>', unsafe_allow_html=True)
        else:
            st.info("Add a job description to see role-specific skill matching.")

st.markdown("---")
data = st.session_state.get("analysis")
if data:
    st.markdown('<div class="section-kicker">03 / Your improvement plan</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Section audit", "Skills match", "Action plan & report"])
    with tab1:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown('<div class="panel"><h3>Resume sections</h3><p class="muted">Detected from headings and common content patterns.</p>', unsafe_allow_html=True)
            for name, ok in data["result"]["sections"].items():
                symbol = "✓" if ok else "○"
                color = "#9dffd3" if ok else "#ffc09e"
                st.markdown(f'<div style="display:flex;justify-content:space-between;gap:10px;padding:10px 0;border-bottom:1px solid rgba(177,199,226,.09)"><span>{name}</span><span style="color:{color};font-weight:800">{symbol} {"Found" if ok else "Review"}</span></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            section_df = pd.DataFrame({"Section": list(data["result"]["sections"].keys()), "Status": [100 if x else 0 for x in data["result"]["sections"].values()]})
            fig = go.Figure(go.Bar(x=section_df["Status"], y=section_df["Section"], orientation="h", marker_color=["#9dffd3" if v else "#344255" for v in section_df["Status"]], text=["Found" if v else "Review" for v in section_df["Status"]], textposition="outside"))
            fig.update_layout(height=330, xaxis=dict(range=[0,120], visible=False), yaxis=dict(autorange="reversed", tickfont=dict(color="#cbd7e8")), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=8,r=48,t=15,b=5), showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with tab2:
        if not data["job_text"].strip():
            st.info("Paste a target job description above and click Analyze resume to unlock this view.")
        else:
            a, b = st.columns(2)
            with a:
                st.markdown('<div class="panel"><h3>Skills detected in both</h3><p class="muted">Evidence of alignment between your resume and the role.</p>', unsafe_allow_html=True)
                if data["matched"]:
                    st.markdown("".join(f'<span class="skill good">{s}</span>' for s in data["matched"]), unsafe_allow_html=True)
                else:
                    st.write("No matching skills from the built-in skill list were detected.")
                st.markdown("</div>", unsafe_allow_html=True)
            with b:
                st.markdown('<div class="panel"><h3>Skills to review</h3><p class="muted">Only add these if you actually have the skill or relevant experience.</p>', unsafe_allow_html=True)
                if data["missing"]:
                    st.markdown("".join(f'<span class="skill miss">{s}</span>' for s in data["missing"]), unsafe_allow_html=True)
                else:
                    st.write("No obvious missing skills from the built-in list.")
                st.markdown("</div>", unsafe_allow_html=True)
            st.caption("Keyword detection is dictionary-based and may miss synonyms, context, or skills not included in the built-in list.")
    with tab3:
        st.markdown('<div class="panel"><h3>Recommended next actions</h3><p class="muted">Prioritize truthful, specific improvements over keyword stuffing.</p>', unsafe_allow_html=True)
        for i, item in enumerate(data["suggestions"], start=1):
            st.markdown(f'<div style="display:flex;gap:12px;padding:11px 0;border-bottom:1px solid rgba(177,199,226,.09)"><span style="font-family:DM Mono;color:#9dffd3">0{i}</span><span>{item}</span></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        report = make_report(data["resume_text"], data["job_text"], data["result"], data["matched"], data["missing"], data["suggestions"])
        st.download_button("Download your review report (.md)", data=report, file_name="resumeiq-review.md", mime="text/markdown", use_container_width=True)
        st.caption("Report includes the score breakdown, detected sections, matching skills, missing keywords, and next steps.")

st.markdown('<div style="text-align:center;padding:24px 0;color:#718198;font-size:.78rem">RESUMEIQ · A PRACTICAL CAREER TOOL · YOUR DATA IS NOT STORED BY THIS DEMO</div>', unsafe_allow_html=True)

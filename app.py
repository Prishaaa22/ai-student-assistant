# app.py — Final production-ready Groq app (Pomodoro section removed)
import streamlit as st
from groq import Groq
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import time
from config import GROQ_API_KEY  # create config.py with GROQ_API_KEY = "gsk_..."

# ---------------------------
# Initialize Groq client
# ---------------------------
client = Groq(api_key=GROQ_API_KEY)

# ---------------------------
# Embedded college info (official + brochure)
# ---------------------------
COLLEGE_OFFICIAL = """
RNS First Grade College (RNSFGC) — Official Information
- Established: 2012.
- Founder: Industrialist-philanthropist Dr. R. N. Shetty.
- Status: Autonomous (recently converted to autonomous status).
- Accreditation: NAAC accredited with an 'A' grade.
- Educational focus: Value-driven education, experiential learning, skill development, discipline, and holistic student growth.
- Mission highlights: Maintain academic excellence with integrity; promote holistic personal development; bridge theory & practice via labs, projects, and industry-relevant curriculum; prepare students for careers with training and placements; nurture socially aware, value-based, culturally rooted individuals.
- Courses / Programs:
  • UG: Bachelor of Computer Applications (BCA), Bachelor of Commerce (B.Com), Bachelor of Business Administration (BBA)
  • PG: Master of Business Administration (MBA)
- Departments: Computer Applications (BCA), Commerce (B.Com), Management (BBA), MBA department.
- Facilities: Well-equipped computer labs & IT infrastructure, library & digital library, hostel accommodation, auditorium/seminar halls, sports & recreation facilities (outdoor & indoor), canteen/food court, ICT-enabled classrooms / smart classrooms, fitness & wellness facilities.
- Contact & Location:
  RNS First Grade College, Dr. Vishnuvardhan Road, Channasandra, RR Nagar, Bengaluru – 560098
  Phone: 080-28611110 / 9141095892
  Emails: enquiryrnsfgc@gmail.com, principal_rnsfgc@rnsgi.com, vp_rnsfgc@rnsgi.com, rnsfgccollege2012@gmail.com
"""

COLLEGE_BROCHURE = """
RNS First Grade College — Professional Brochure Summary
RNSFGC is a modern, autonomous institution committed to shaping well-rounded professionals through a blend of rigorous academics and practical exposure. The college emphasizes:
• Academic excellence and ethical conduct
• Industry-relevant training and hands-on learning
• Leadership, communication, and personal growth
Programs include BCA, B.Com, BBA at the undergraduate level and MBA at the postgraduate level. Campus life supports learning through advanced computer labs, a comprehensive library (digital + physical), sports and cultural activities, smart classrooms, auditoriums for seminars, and residential facilities for outstation students. RNSFGC prepares students for contemporary careers with placement-oriented programs, value-based education, and opportunities for experiential projects.
"""

SYSTEM_PROMPT = f"""
You are an AI assistant specialized for RNS First Grade College (RNSFGC), Bengaluru.
Use the official details and brochure below to answer student queries accurately.

--- OFFICIAL INFO (use this for factual answers) ---
{COLLEGE_OFFICIAL}

--- PROFESSIONAL BROCHURE SUMMARY (use for polished descriptions) ---
{COLLEGE_BROCHURE}

Guidelines:
- Always prefer factual accuracy using OFFICIAL INFO for facts (courses, contact, accreditation, departments, facilities, year, founder).
- For promotional or brochure-style responses use BROCHURE text.
- Keep answers concise, structured; use bullets/lists where helpful.
- If the answer is not present in the provided info, reply exactly: "I could not find this information in the college data I was given."
- Avoid inventing facts. Be professional and student-friendly.
"""

# ---------------------------
# Page config + CSS (dark premium)
# ---------------------------
st.set_page_config(page_title="AI Student Assistant", layout="wide", page_icon="🎓")

st.markdown(
    """
    <style>
    :root {
        --bg:#071024;
        --card:#071224;
        --muted:#9fb6d6;
        --accent:#68b8ff;
        --neon:#5df0d8;
    }
    body { background: linear-gradient(180deg,#071028 0%, #0b1220 100%); color: #e6eef8; }
    .title { font-size: 52px; font-weight: 900; text-align:center; color: var(--accent); margin-bottom: 6px; text-shadow:0 0 22px rgba(104,183,255,0.12); }
    .section { font-size:18px; font-weight:700; color:#cfe9ff; margin-top:12px; }
    .card { background: var(--card); padding:18px; border-radius:12px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); border:1px solid rgba(104,155,255,0.06); }
    .output { background:#071424; padding:14px; border-left:5px solid var(--accent); border-radius:8px; color:#dfeefe; }
    .small { font-size:13px; color:var(--muted); }
    .hint { color: #94a6bf; font-size:13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='title'>🎓 AI Student Assistant</div>", unsafe_allow_html=True)

# ---------------------------
# Groq wrapper
# ---------------------------
def groq_chat(messages, max_tokens: int = 400, temperature: float = 0.15, model: str = "llama-3.1-8b-instant"):
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[Groq error] {e}"

# ---------------------------
# PDF generator
# ---------------------------
def generate_pdf_bytes(title: str, content: str) -> BytesIO:
    buff = BytesIO()
    pdf = canvas.Canvas(buff, pagesize=letter)
    width, height = letter
    y = height - 60

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, title)
    y -= 30

    pdf.setFont("Helvetica", 11)
    for line in content.split("\n"):
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 11)
            y = height - 50
        pdf.drawString(50, y, line)
        y -= 16

    pdf.save()
    buff.seek(0)
    return buff

# ---------------------------
# Session state defaults
# ---------------------------
if "todo" not in st.session_state:
    st.session_state.todo = []

# ---------------------------
# Tabs layout
# ---------------------------
tab1, tab2, tab3 = st.tabs(["🤖 Chat Assistant", "📘 Grade Calculator", "📚 Productivity Dashboard"])

# ---------------------------
# TAB 1 — Chat Assistant
# ---------------------------
with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section'>🤖 Chat Assistant (Groq LLM)</div>", unsafe_allow_html=True)

    chat_q = st.text_input("Ask a question about RNSFGC, courses, facilities, contacts, or student life", key="chat_q_input")
    c1, c2 = st.columns([1, 1])

    with c1:
        if st.button("Ask Groq", key="ask_groq_btn"):
            if not chat_q.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Contacting Groq for an answer..."):
                    messages = [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": chat_q}
                    ]
                    ans = groq_chat(messages, max_tokens=450, temperature=0.12)
                    st.markdown(f"<div class='output'>{ans}</div>", unsafe_allow_html=True)

    with c2:
        if st.button("Clear Chat Input", key="clear_chat_btn"):
            st.session_state.chat_q_input = ""

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# TAB 2 — Grade Calculator
# ---------------------------
with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section'>📘 Grade Calculator</div>", unsafe_allow_html=True)

    num = st.number_input("How many subjects?", min_value=1, max_value=20, value=3, key="num_subs")
    subjects = []
    marks = []

    for i in range(num):
        col_a, col_b = st.columns([3, 1])
        with col_a:
            s = st.text_input(f"Subject {i+1} name", key=f"sub_name_{i}")
        with col_b:
            m = st.number_input(f"Marks {i+1}", min_value=0, max_value=100, key=f"sub_mark_{i}")

        subjects.append(s.strip())
        marks.append(m)

    if st.button("Calculate Grades", key="calc_grades_btn"):
        if any(s == "" for s in subjects):
            st.warning("Please fill all subject names.")
        else:
            total = sum(marks)
            possible = 100 * len(marks)
            percentage = (total / possible) * 100
            cgpa = percentage / 9.5

            if percentage >= 90:
                grade = "A+"
            elif percentage >= 80:
                grade = "A"
            elif percentage >= 70:
                grade = "B+"
            elif percentage >= 60:
                grade = "B"
            elif percentage >= 50:
                grade = "C"
            else:
                grade = "Fail"

            detail_html = "".join([f"<li><b>{subjects[i]}</b>: {marks[i]}</li>" for i in range(len(subjects))])

            st.markdown(f"<div class='output'><b>Subject-wise:</b><ul>{detail_html}</ul>"
                        f"<b>Total:</b> {total}/{possible}<br>"
                        f"<b>Percentage:</b> {percentage:.2f}%<br>"
                        f"<b>CGPA(Est):</b> {cgpa:.2f}<br>"
                        f"<b>Grade:</b> {grade}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# TAB 3 — Productivity Dashboard
# ---------------------------
with tab3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section'>📚 Student Productivity Dashboard</div>", unsafe_allow_html=True)

    # Notes / To-Do List
    st.subheader("📝 Notes / To-Do List")
    notes = st.text_area("Write your notes here...", height=180, key="notes_text")
    new_task = st.text_input("Add a To-Do item", key="new_task")

    t1, t2 = st.columns([1, 1])

    with t1:
        if st.button("Add Task", key="add_task_btn"):
            if new_task.strip():
                st.session_state.todo.append(new_task.strip())
                st.success("Task added.")
            else:
                st.warning("Please type a task.")

    with t2:
        if st.button("Clear Tasks", key="clear_tasks_btn"):
            st.session_state.todo = []
            st.info("Tasks cleared.")

    if st.session_state.todo:
        st.markdown("**Your To-Do:**")
        for idx, t in enumerate(st.session_state.todo, 1):
            st.markdown(f"{idx}. {t}")

    st.markdown("---")

    # Study Suggestions
    st.subheader("💡 Study Suggestions (Groq)")
    study_topic = st.text_input("Enter topic you'd like suggestions for", key="study_topic")

    s1, s2 = st.columns([1, 1])

    with s1:
        if st.button("Get AI Study Suggestions", key="ai_study_btn"):
            if not study_topic.strip():
                st.warning("Please enter a study topic.")
            else:
                with st.spinner("Generating study suggestions..."):
                    prompt = (
                        f"Create a focused study plan for a student on the topic: {study_topic}. "
                        "Include: (1) a 2-hour plan broken into Pomodoro cycles, (2) a 7-day weekly plan, "
                        "(3) memory & practice tips, and (4) one sample practice question."
                    )
                    suggestions = groq_chat([{"role": "system", "content": SYSTEM_PROMPT},
                                             {"role": "user", "content": prompt}], max_tokens=450)
                    st.markdown(f"<div class='output'>{suggestions}</div>", unsafe_allow_html=True)

    with s2:
        if st.button("Quick Tips (Local)", key="quick_tips_btn"):
            st.info("Use Pomodoro (25/5), active recall, spaced repetition, solve previous-year questions, teach back topics.")

    st.markdown("</div>", unsafe_allow_html=True)

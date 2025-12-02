import streamlit as st
from groq import Groq
from config import GROQ_API_KEY

# ============================================
# BEAUTIFUL CUSTOM PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="AI Student Assistant",
    layout="wide",
    page_icon="🎓",
)

# Custom CSS for WOW UI
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f0f7ff, #e8f0ff); }

.card {
    padding: 20px;
    border-radius: 15px;
    background: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-top: 10px;
}

.big-title {
    font-size: 40px;
    font-weight: 900;
    color: #002b5c;
}

.subtext {
    font-size: 17px;
    color: #003b74;
}

.answer-box {
    background: #ffffff;
    padding: 18px;
    border-left: 6px solid #3b82f6;
    border-radius: 12px;
    font-size: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.grade-box {
    background: #eaf3ff;
    padding: 18px;
    border-left: 6px solid #2563eb;
    border-radius: 12px;
    font-size: 17px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)


# ============================================
# FIXED FAQ DATA
# ============================================
faq_data = [
    {
        "question": "About the College",
        "answer": """
RNS First Grade College (RNSFGC) was established in 2012 by industrialist-philanthropist Dr. R. N. Shetty.  
It is an autonomous institution accredited by NAAC with an 'A' grade.  
The college focuses on value-driven education, experiential learning, skill development, discipline, and holistic growth.
"""
    },
    {
        "question": "Vision and Mission",
        "answer": """
• Uphold academic excellence with integrity.  
• Promote discipline, ethics, responsibility & holistic development.  
• Bridge theory and practice through labs, projects & industry learning.  
• Prepare students for careers via training & placements.  
"""
    },
    {
        "question": "Courses Offered",
        "answer": """
UG Programs: BCA, B.Com, BBA  
PG Program: MBA
"""
    },
    {
        "question": "Departments",
        "answer": """
• BCA  
• B.Com  
• BBA  
• MBA  
"""
    },
    {
        "question": "Facilities",
        "answer": """
• Computer labs  
• Library & Digital Library  
• Hostel  
• Auditorium  
• Sports (Indoor & Outdoor)  
• ICT-enabled classrooms  
• Canteen  
• Gym  
"""
    },
    {
        "question": "Contact Details",
        "answer": """
Address:
RNS First Grade College, Dr. Vishnuvardhan Road, RR Nagar, Bengaluru – 560098  

Phone: 080-28611110, 9141095892  

Emails:  
• enquiryrnsfgc@gmail.com  
• principal_rnsfgc@rnsgi.com  
• vp_rnsfgc@rnsgi.com  
• rnsfgccollege2012@gmail.com  
"""
    }
]

faq_text = "\n\n".join([f"Q: {i['question']}\nA: {i['answer']}" for i in faq_data])

# ============================================
# LLM ANSWERING LOGIC
# ============================================
client = Groq(api_key=GROQ_API_KEY)

def answer_faq(question):
    prompt = f"""
Answer ONLY from the FAQ below.
If information is missing, say: "I could not find this information."

FAQ:
{faq_text}

QUESTION:
{question}
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    return res.choices[0].message.content.strip()


# ============================================
# GRADE CALCULATOR
# ============================================
def calculate_multi_subject_grades(marks_dict):
    total = sum(marks_dict.values())
    percentage = total / len(marks_dict)
    cgpa = percentage / 9.5
    return total, percentage, round(cgpa, 2)


# ============================================
# MAIN UI
# ============================================
st.markdown('<p class="big-title">🎓 AI Student Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="subtext">Smart · Simple · Professional</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📘 College FAQ Assistant", "📊 Grade Calculator"])

# =================================================
# TAB 1 — FAQ Assistant
# =================================================
with tab1:

    st.subheader("Ask anything about RNSFGC")

    # Suggestions
    st.write("Quick questions:")

    col1, col2, col3 = st.columns(3)
    suggestion_buttons = ["About the College", "Facilities", "Courses Offered"]

    question = ""

    if col1.button(suggestion_buttons[0]):
        question = suggestion_buttons[0]
    if col2.button(suggestion_buttons[1]):
        question = suggestion_buttons[1]
    if col3.button(suggestion_buttons[2]):
        question = suggestion_buttons[2]

    # Text input (UNIQUE KEY added)
    user_input = st.text_input("Or Type your Question:", key="main_question_box")

    # Priority: suggestion → user input
    if user_input.strip():
        question = user_input

    if st.button("Get Answer", key="faq_button"):
        if question.strip() == "":
            st.warning("Please enter a question!")
        else:
            ans = answer_faq(question)
            st.markdown(f'<div class="answer-box">{ans}</div>', unsafe_allow_html=True)



# =================================================
# TAB 2 — Grade Calculator
# =================================================
with tab2:

    st.subheader("Enter Subject Marks")

    num_subjects = st.number_input("Number of subjects:", min_value=1, max_value=20, step=1, key="num_subjects")

    marks = {}
    for i in range(num_subjects):
        marks[f"Subject {i+1}"] = st.number_input(
            f"Marks for Subject {i+1}",
            min_value=0,
            max_value=100,
            step=1,
            key=f"sub_{i}"
        )

    if st.button("Calculate Result", key="calc_result"):
        total, percentage, cgpa = calculate_multi_subject_grades(marks)

        st.markdown(
            f"""
            <div class="grade-box">
            <h3>📊 Your Grade Summary</h3>
            <b>Total Marks:</b> {total}<br>
            <b>Percentage:</b> {percentage:.2f}%<br>
            <b>CGPA / SGPA:</b> {cgpa}
            </div>
            """,
            unsafe_allow_html=True
        )

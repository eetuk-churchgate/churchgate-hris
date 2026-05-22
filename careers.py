import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from utils.database import DatabaseManager

st.set_page_config(page_title="Careers - Churchgate Group", page_icon="🌐", layout="wide")

st.markdown("""
<style>
    .career-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 3rem 2rem;
        text-align: center;
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        border-bottom: 4px solid #CC0000;
    }
    .career-header h1 { font-size: 2.5rem; font-weight: 700; margin: 0; }
    .career-header p { font-size: 1.2rem; margin-top: 1rem; opacity: 0.9; }
    .job-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #CC0000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .job-card:hover { transform: translateX(5px); box-shadow: 0 8px 20px rgba(0,0,0,0.12); }
    .job-title { font-size: 1.3rem; font-weight: 700; color: #1a1a1a; }
    .stButton > button {
        background: #CC0000 !important; color: white !important;
        border: none !important; padding: 0.6rem 2rem !important;
        border-radius: 6px !important; font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="career-header">
    <h1>🚀 Build Your Career at Churchgate Group</h1>
    <p>Join a team of innovators shaping Africa's real estate future</p>
</div>
""", unsafe_allow_html=True)

query_params = st.query_params
selected_job = query_params.get('job', None)

db = DatabaseManager()

if selected_job:
    st.markdown(f"### 📝 Apply for Position: {selected_job}")
    
    with st.form("job_application", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            first_name = st.text_input("First Name *")
            last_name = st.text_input("Last Name *")
            email = st.text_input("Email *")
            phone = st.text_input("Phone Number *")
            linkedin = st.text_input("LinkedIn Profile URL")
        with c2:
            github = st.text_input("GitHub URL")
            portfolio = st.text_input("Portfolio URL")
            current_position = st.text_input("Current/Last Position")
            current_company = st.text_input("Current/Last Company")
            years_exp = st.number_input("Years of Experience", 0, 50, 0)
        
        cover_letter = st.text_area("Cover Letter (Optional)", height=100)
        resume = st.file_uploader("Upload CV/Resume *", type=['pdf', 'docx'])
        
        st.markdown("### Screening Questions")
        st.info("Please answer the following questions to help us evaluate your application.")
        q1 = st.text_area("1. Describe your most relevant experience for this role. *", height=80)
        q2 = st.text_area("2. What is your key achievement that relates to this position? *", height=80)
        q3 = st.text_area("3. Why do you want to join Churchgate Group? *", height=80)
        
        submitted = st.form_submit_button("📤 Submit Application", use_container_width=True)
        
        if submitted:
            if first_name and last_name and email and phone and resume and q1 and q2 and q3:
                try:
                    resume_text = ""
                    if resume:
                        if resume.type == "application/pdf":
                            import PyPDF2
                            pdf_reader = PyPDF2.PdfReader(resume)
                            for page in pdf_reader.pages:
                                resume_text += page.extract_text() + "\n"
                        elif "word" in resume.type or "docx" in resume.type:
                            import docx
                            doc = docx.Document(resume)
                            resume_text = "\n".join([p.text for p in doc.paragraphs])
                    
                    candidate_data = (
                        f"CAND-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        first_name, last_name, email, phone,
                        linkedin, current_position, current_company, years_exp,
                        "", "", "", f"Resume_{first_name}_{last_name}.pdf", resume_text[:5000],
                        None, "Career Portal", "New"
                    )
                    db.add_candidate(candidate_data)
                    st.success(f"✅ Thank you, {first_name}! Your application has been submitted successfully.")
                    st.balloons()
                    st.info("📧 You will receive a confirmation email shortly. Our team will review your application.")
                except Exception as e:
                    st.error(f"Submission error: {str(e)}")
            else:
                st.error("❌ Please fill all required fields marked with *")
else:
    st.markdown("### 📋 Open Positions")
    
    jobs = [
        {"ref": "JOB-20260522-001", "title": "Senior Network Engineer", "dept": "Technology Group", "location": "Abuja", "type": "Full-time"},
        {"ref": "JOB-20260522-002", "title": "AI Transformation Lead", "dept": "Technology Group", "location": "Abuja", "type": "Full-time"},
        {"ref": "JOB-20260522-003", "title": "Facility Manager", "dept": "Facility Management", "location": "Lagos", "type": "Full-time"},
    ]
    
    for job in jobs:
        st.markdown(f"""
        <div class="job-card">
            <div class="job-title">{job['title']}</div>
            <p>🏢 {job['dept']} | 📍 {job['location']} | 💼 {job['type']}</p>
            <small>Ref: {job['ref']}</small>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Apply for {job['title']}", key=f"apply_{job['ref']}"):
            st.query_params['job'] = job['ref']
            st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 2rem;">
    <p>© 2026 Churchgate Group | World Trade Center, Abuja</p>
    <p>📧 careers@churchgate.com</p>
</div>
""", unsafe_allow_html=True)
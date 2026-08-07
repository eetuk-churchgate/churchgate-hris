import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import random
import base64
import time
import os
import re

sys.path.append(str(Path(__file__).parent.parent))

# Fix secrets for Hugging Face
class HuggingFaceSecrets:
    def __getitem__(self, key):
        try:
            if hasattr(st, 'secrets') and hasattr(st.secrets, '_secrets'):
                if key in st.secrets._secrets:
                    return st.secrets._secrets[key]
        except:
            pass
        return os.environ.get(key)
    def get(self, key, default=None):
        try:
            val = self.__getitem__(key)
            return val if val is not None else default
        except:
            return default

if not hasattr(st, 'secrets') or not hasattr(st.secrets, '_secrets'):
    st.secrets = HuggingFaceSecrets()

from utils.database import DatabaseManager

# ============ SESSION STATE ============
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'submitted_tracking_id' not in st.session_state:
    st.session_state.submitted_tracking_id = ""
if 'submitted_name' not in st.session_state:
    st.session_state.submitted_name = ""
if 'submitted_email' not in st.session_state:
    st.session_state.submitted_email = ""
if 'submitted_position' not in st.session_state:
    st.session_state.submitted_position = ""

logo_path = Path(__file__).parent.parent / "churchgate-logo.jpeg"
if logo_path.exists():
    st.set_page_config(page_title="Careers - Churchgate Group", page_icon=str(logo_path), layout="wide", initial_sidebar_state="collapsed")
else:
    st.set_page_config(page_title="Careers - Churchgate Group", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

# Initialize database
db = DatabaseManager()

def get_logo_base64():
    for ext in ['.jpeg', '.jpg', '.png']:
        path = Path(__file__).parent.parent / f"churchgate-logo{ext}"
        if path.exists():
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()

dept_icons = {
    "Technology Group": "💻", "Facility Management": "🏗️", "Human Resources": "👥",
    "Accounts & Finance": "💰", "Sales & Marketing": "📈", "Procurement": "📦",
    "Security": "🔒", "Legal": "⚖️", "Operations": "⚙️", "Engineering": "🔧",
    "Central Stores": "🏪", "Project Development": "🏗️", "Trade Services": "🤝"
}

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background: linear-gradient(180deg, #faf9f6 0%, #f5f0e8 50%, #faf9f6 100%) !important; }}
    .career-hero {{ background: linear-gradient(135deg, #1a1a1a 0%, #2d2a1f 50%, #1a1a1a 100%); padding: 1rem 2rem; text-align: center; border-bottom: 3px solid #D4AF37; }}
    .career-hero h1 {{ font-size: 1.5rem; font-weight: 800; margin: 0; color: #F5E6CC; }}
    .stButton > button {{ background: #CC0000 !important; color: white !important; border: none !important; padding: 0.5rem 1.5rem !important; border-radius: 6px !important; font-weight: 600 !important; }}
    .stButton > button:hover {{ background: #D4AF37 !important; }}
    .job-card {{ background: white; padding: 0; border-radius: 8px; margin-bottom: 0.6rem; border-left: 4px solid #D4AF37; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }}
    .tag {{ display: inline-block; background: #faf8f2; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.7rem; margin-right: 0.3rem; color: #5c4a2a; border: 1px solid #e8dcc8; }}
    div[data-testid="stSidebarNav"] {{display: none !important;}}
    div[data-testid="stSidebar"] {{display: none !important;}}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_cached_jobs():
    try:
        import requests
        supabase_url = os.environ.get("SUPABASE_URL", "https://pobfydvkjzhkmhuqwmtf.supabase.co")
        supabase_key = os.environ.get("SUPABASE_KEY", "sb_publishable_iDYmuO5jfqmzydDPgNhL3w_b21rWMhm")
        headers = {"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"}
        url = f"{supabase_url}/rest/v1/job_requisitions?select=*&status=eq.Approved - Live"
        r = requests.get(url, headers=headers)
        return r.json() if r.status_code == 200 else []
    except:
        return []

query_params = st.query_params
selected_job = query_params.get('job', None)

# ============ APPLICATION FORM PAGE ============
if selected_job:
    job_details = None
    try:
        all_reqs = get_cached_jobs()
        for r in all_reqs:
            if r.get('status') == 'Approved - Live':
                req_id = r.get('req_id', '')
                job_ref = f"JOB-{req_id[-6:]}" if len(req_id) >= 6 else req_id
                if req_id == selected_job or job_ref == selected_job or f"JOB-{req_id}" == selected_job:
                    job_details = r
                    break
    except:
        pass
    
    position_name = job_details.get('title', selected_job).replace('**', '') if job_details else selected_job.replace('**', '')
    
    st.markdown(f"""<div class="career-hero"><h1>📝 Apply for {position_name}</h1><p>{job_details.get('department', '')} | {job_details.get('location', '')} | {job_details.get('job_type', '')}</p></div>""", unsafe_allow_html=True)
    
    if job_details:
        with st.expander("📋 View Full Job Description", expanded=True):
            jd_text = job_details.get("jd", "")
            st.markdown(f'<div style="line-height:1.6;font-size:0.85rem;">{jd_text.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    
    # Show success if already submitted for this job
    if st.session_state.form_submitted:
        st.balloons()
        st.markdown(f"""
        <div style="max-width:700px;margin:50px auto;text-align:center;">
            <div style="background:#f0fdf4;border:2px solid #38a169;border-radius:16px;padding:40px;">
                <h1 style="color:#38a169;">✅ Application Submitted!</h1>
                <p>Thank you, <strong>{st.session_state.submitted_name}</strong>!</p>
                <p><strong>Tracking ID:</strong> {st.session_state.submitted_tracking_id}</p>
                <p><strong>Position:</strong> {st.session_state.submitted_position}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Apply for Another Position"):
            st.session_state.form_submitted = False
            st.query_params.clear()
            st.rerun()
        st.stop()
    
    # APPLICATION FORM
    with st.form("job_application", clear_on_submit=False):
        st.markdown("### Personal Information")
        c1, c2 = st.columns(2)
        with c1:
            first_name = st.text_input("First Name *")
            last_name = st.text_input("Last Name *")
            email = st.text_input("Email *")
            phone = st.text_input("Phone Number *")
        with c2:
            linkedin = st.text_input("LinkedIn Profile URL")
            current_position = st.text_input("Current/Last Position")
            current_company = st.text_input("Current/Last Company")
            years_exp = st.selectbox("Years of Experience", ["0-1", "1-3", "3-5", "5-7", "7-10", "10+", "15+", "20+"])
        
        st.markdown("---")
        cover_letter = st.text_area("Cover Letter (Optional)", height=100)
        st.markdown("---")
        st.markdown("### 📎 Documents")
        resume = st.file_uploader("Upload CV/Resume *", type=['pdf', 'docx'])
        st.markdown("---")
        st.markdown("### Screening Questions")
        q1 = st.text_area("1. Describe your most relevant experience. *", height=80)
        q2 = st.text_area("2. What is your proudest achievement? *", height=80)
        q3 = st.text_area("3. Why do you want to join Churchgate Group? *", height=80)
        
        submitted = st.form_submit_button("📤 Submit Application", use_container_width=True, type="primary")
        
        if submitted:
            errors = []
            if not first_name: errors.append("First Name")
            if not last_name: errors.append("Last Name")
            if not email: errors.append("Email")
            if not phone: errors.append("Phone")
            if not resume: errors.append("CV/Resume")
            if not q1: errors.append("Question 1")
            if not q2: errors.append("Question 2")
            if not q3: errors.append("Question 3")
            
            if errors:
                st.error(f"❌ Missing: {', '.join(errors)}")
            else:
                with st.spinner("📤 Submitting..."):
                    try:
                        # Extract resume text
                        resume_text = ""
                        file_ext = "pdf"
                        try:
                            if resume.type == "application/pdf":
                                import PyPDF2
                                pdf_reader = PyPDF2.PdfReader(resume)
                                for page in pdf_reader.pages:
                                    text = page.extract_text()
                                    if text: resume_text += text + "\n"
                                file_ext = "pdf"
                            elif "word" in resume.type or "docx" in resume.type:
                                import docx
                                doc = docx.Document(resume)
                                resume_text = "\n".join([p.text for p in doc.paragraphs])
                                file_ext = "docx"
                        except:
                            resume_text = "[Could not extract text]"
                        
                        tracking_id = f"CG-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
                        
                        # Upload CV
                        cv_url = ""
                        try:
                            resume.seek(0)
                            cv_url = db.upload_file("cvs", f"{tracking_id}_{first_name}_{last_name}.{file_ext}", resume.read(), resume.type)
                        except:
                            pass
                        
                        # SAVE CANDIDATE
                        db._post("candidates", {
                            "candidate_ref": tracking_id,
                            "first_name": first_name,
                            "last_name": last_name,
                            "email": email,
                            "phone": phone,
                            "linkedin_url": linkedin,
                            "current_position": current_position,
                            "current_company": current_company if current_company else "",
                            "years_of_experience": float(years_exp.split("-")[0]) if years_exp else 0,
                            "location": "",
                            "education_level": "",
                            "skills": "",
                            "resume_filename": f"CV_{first_name}_{last_name}.{file_ext}",
                            "resume_text": resume_text[:10000] if resume_text else "",
                            "cv_url": cv_url if cv_url else "",
                            "other_docs": "",
                            "job_id": str(selected_job),
                            "source": "Career Portal",
                            "status": "New",
                            "ai_score": 0,
                            "ai_tier": "Pending"
                        })
                        
                        # SAVE APPLICATION
                        db._post("applications", {
                            "tracking_id": tracking_id,
                            "first_name": first_name,
                            "last_name": last_name,
                            "email": email,
                            "phone": phone,
                            "job_ref": str(selected_job),
                            "position_name": position_name,
                            "status": "Received",
                            "applied_date": datetime.now().strftime('%Y-%m-%d %H:%M')
                        })
                        
                        # SEND EMAIL
                        try:
                            from utils.email_service import EmailService
                            EmailService().send_email(email, f"Application Received - {position_name}", f"Dear {first_name},\n\nThank you for applying for {position_name}.\n\nTracking ID: {tracking_id}\n\nChurchgate Group HR")
                        except:
                            pass
                        
                        # SHOW SUCCESS
                        st.session_state.form_submitted = True
                        st.session_state.submitted_tracking_id = tracking_id
                        st.session_state.submitted_name = first_name
                        st.session_state.submitted_email = email
                        st.session_state.submitted_position = position_name
                        st.success(f"✅ Application Submitted! Tracking ID: {tracking_id}")
                        st.balloons()
                        st.stop()
                        
                    except Exception as e:
                        import traceback
                        st.error(f"❌ Failed: {str(e)}")
                        st.code(traceback.format_exc())

# ============ MAIN CAREERS PAGE ============
else:
    st.markdown(f"""<div class="career-hero"><h1>🚀 Build Your Career at Churchgate Group</h1><p>Join a team of innovators shaping Africa's real estate future.</p></div>""", unsafe_allow_html=True)
    
    jobs = []
    try:
        all_reqs = get_cached_jobs()
        for req in all_reqs:
            if req.get('status') == 'Approved - Live':
                jobs.append({"ref": f"JOB-{req.get('req_id', '')[-6:]}", "title": req.get('title', '').replace('**', ''), "dept": req.get('department', ''), "location": req.get('location', ''), "type": req.get('job_type', ''), "closing": req.get('closing', ''), "jd": req.get('jd', '')})
    except:
        pass
    
    try:
        emp_count = len(db.get_all_employees()) if not db.get_all_employees().empty else 200
    except:
        emp_count = 200
    
    st.markdown(f"""<div style="display:flex;justify-content:space-around;background:#1a1a1a;padding:0.3rem 1rem;border-bottom:2px solid #D4AF37;"><div style="text-align:center;"><div style="font-size:1rem;font-weight:800;color:#D4AF37;">{emp_count}+</div><div style="font-size:0.5rem;color:#c4b998;">TEAM</div></div><div style="text-align:center;"><div style="font-size:1rem;font-weight:800;color:#D4AF37;">3</div><div style="font-size:0.5rem;color:#c4b998;">REGIONS</div></div><div style="text-align:center;"><div style="font-size:1rem;font-weight:800;color:#D4AF37;">16</div><div style="font-size:0.5rem;color:#c4b998;">SUBSIDIARIES</div></div><div style="text-align:center;"><div style="font-size:1rem;font-weight:800;color:#D4AF37;">{len(jobs)}</div><div style="font-size:0.5rem;color:#c4b998;">OPENINGS</div></div><div style="text-align:center;"><div style="font-size:1rem;font-weight:800;color:#D4AF37;">50+</div><div style="font-size:0.5rem;color:#c4b998;">YEARS</div></div></div>""", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search_query = st.text_input("🔍 Search jobs", placeholder="Search by title, skill, department...", label_visibility="collapsed")
    with c2:
        dept_filter = st.selectbox("Department", ["All Departments", "Technology Group", "Facility Management", "Human Resources", "Accounts & Finance", "Sales & Marketing", "Procurement", "Security", "Legal", "Operations"], label_visibility="collapsed")
    with c3:
        type_filter = st.selectbox("Type", ["All Types", "Full-time", "Contract", "Part-time", "Intern"], label_visibility="collapsed")
    
    filtered_jobs = [j for j in jobs if (not search_query or search_query.lower() in j['title'].lower()) and (dept_filter == "All Departments" or j['dept'] == dept_filter) and (type_filter == "All Types" or j['type'] == type_filter)]
    
    st.markdown("---")
    
    if filtered_jobs:
        st.markdown(f"### 📋 {len(filtered_jobs)} Open Position{'s' if len(filtered_jobs) > 1 else ''}")
        for job in filtered_jobs:
            with st.expander(f"{dept_icons.get(job['dept'], '🏢')} {job['title']} — {job['dept']} | {job['location']}", expanded=False):
                st.markdown(f"""<span class="tag">💼 {job['type']}</span><span class="tag">📍 {job['location']}</span><span class="tag">🏢 {job['dept']}</span>""", unsafe_allow_html=True)
                st.markdown(f'<div style="line-height:1.6;font-size:0.85rem;">{job["jd"].replace(chr(10), "<br>")[:500]}...</div>', unsafe_allow_html=True)
                if st.button(f"📝 Apply Now", key=f"apply_{job['ref']}"):
                    st.query_params['job'] = job['ref']
                    st.rerun()
    else:
        st.info("No open positions matching your criteria.")
    
    st.markdown("---")
    st.markdown("## 🎁 Why Churchgate Group?")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div style="background:white;padding:0.8rem;border-radius:8px;text-align:center;border-bottom:2px solid #D4AF37;"><div style="font-size:1.5rem;">🏥</div><h4>Health Insurance</h4><p style="font-size:0.75rem;color:#666;">Comprehensive HMO coverage</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div style="background:white;padding:0.8rem;border-radius:8px;text-align:center;border-bottom:2px solid #D4AF37;"><div style="font-size:1.5rem;">💰</div><h4>Pension Plan</h4><p style="font-size:0.75rem;color:#666;">Secure retirement scheme</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div style="background:white;padding:0.8rem;border-radius:8px;text-align:center;border-bottom:2px solid #D4AF37;"><div style="font-size:1.5rem;">📚</div><h4>Learning</h4><p style="font-size:0.75rem;color:#666;">Training & certifications</p></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div style="background:white;padding:0.8rem;border-radius:8px;text-align:center;border-bottom:2px solid #D4AF37;"><div style="font-size:1.5rem;">🏖️</div><h4>Annual Leave</h4><p style="font-size:0.75rem;color:#666;">Paid time off</p></div>', unsafe_allow_html=True)

st.markdown("""<div style="background:#1a1a1a;color:#c4b998;padding:0.8rem;text-align:center;margin-top:1.5rem;border-top:2px solid #D4AF37;font-size:0.7rem;"><h3 style="color:#D4AF37;">Churchgate Group</h3><p>📧 careers@churchgate.com</p><p>© 2026 Churchgate Group. All rights reserved.</p></div>""", unsafe_allow_html=True)
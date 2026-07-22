import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import random
import base64
import time

sys.path.append(str(Path(__file__).parent.parent))

import os

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

logo_path = Path(__file__).parent.parent / "churchgate-logo.jpeg"
if logo_path.exists():
    st.set_page_config(page_title="Careers - Churchgate Group", page_icon=str(logo_path), layout="wide", initial_sidebar_state="collapsed")
else:
    st.set_page_config(page_title="Careers - Churchgate Group", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

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
    @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .animate-fade-in {{ animation: fadeIn 0.8s ease-out; }}
    .animate-fade-in-up {{ animation: fadeInUp 0.8s ease-out; }}
    .career-hero {{ background: linear-gradient(135deg, #1a1a1a 0%, #2d2a1f 50%, #1a1a1a 100%); padding: 1rem 2rem; text-align: center; border-bottom: 3px solid #D4AF37; }}
    .career-hero h1 {{ font-size: 1.5rem; font-weight: 800; margin: 0; color: #F5E6CC; }}
    .career-hero p {{ font-size: 0.8rem; margin-top: 0.3rem; color: #c4b998; max-width: 600px; margin-left: auto; margin-right: auto; }}
    .job-hero {{ background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 1rem 2rem; border-bottom: 3px solid #D4AF37; margin-bottom: 1rem; }}
    .job-hero h1 {{ color: #F5E6CC; font-size: 1.3rem; margin: 0; font-weight: 700; }}
    .job-hero p {{ color: #c4b998; margin: 0.2rem 0 0 0; font-size: 0.8rem; }}
    .search-bar {{ background: white; padding: 0.8rem 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin: -1.5rem 2rem 1rem 2rem; position: relative; z-index: 10; border: 1px solid #D4AF37; }}
    .job-card {{ background: white; padding: 0; border-radius: 8px; margin-bottom: 0.6rem; border-left: 4px solid #D4AF37; box-shadow: 0 1px 4px rgba(0,0,0,0.04); transition: all 0.3s ease; overflow: hidden; }}
    .job-card:hover {{ transform: translateX(4px); box-shadow: 0 4px 15px rgba(212,175,55,0.15); }}
    .tag {{ display: inline-block; background: #faf8f2; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.7rem; margin-right: 0.3rem; margin-top: 0.3rem; color: #5c4a2a; border: 1px solid #e8dcc8; }}
    .stButton > button {{ background: #CC0000 !important; color: white !important; border: none !important; padding: 0.5rem 1.5rem !important; border-radius: 6px !important; font-weight: 600 !important; font-size: 0.85rem !important; }}
    .stButton > button:hover {{ background: #D4AF37 !important; transform: translateY(-2px) !important; }}
    .benefit-card {{ background: white; padding: 0.8rem; border-radius: 8px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.04); border: 1px solid #e8dcc8; border-bottom: 2px solid #D4AF37; }}
    .benefit-card h4 {{ font-size: 0.8rem; margin: 0.2rem 0; }}
    .benefit-card p {{ font-size: 0.7rem !important; color: #888; }}
    .benefit-card:hover {{ transform: translateY(-3px); }}
    .benefit-icon {{ font-size: 1.5rem; margin-bottom: 0.2rem; }}
    .testimonial-card {{ background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); text-align: center; border: 1px solid #e8dcc8; border-top: 2px solid #D4AF37; }}
    .testimonial-card h4 {{ font-size: 0.8rem; }}
    .testimonial-card p {{ font-size: 0.75rem !important; color: #888; }}
    .social-proof {{ background: linear-gradient(135deg, #faf8f2, #f5f0e8); padding: 1rem; border-radius: 8px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.04); margin: 1rem 0; border: 1px solid #D4AF37; }}
    .social-proof h3 {{ font-size: 0.9rem; }}
    .social-proof p {{ font-size: 0.75rem !important; }}
    .footer {{ background: linear-gradient(135deg, #1a1a1a, #2d2a1f); color: #c4b998; padding: 0.8rem 1rem; text-align: center; margin-top: 1.5rem; border-top: 2px solid #D4AF37; font-size: 0.7rem; }}
    .footer h3 {{ color: #D4AF37; font-weight: 700; font-size: 0.8rem; margin-bottom: 0.2rem; }}
    .jd-content {{ line-height: 1.6; font-size: 0.85rem; color: #444; }}
    .jd-content strong {{ color: #1a1a1a; font-size: 1rem; }}
    .success-box {{ background: linear-gradient(135deg, #f0f8f0, #e8f5e9); padding: 1.5rem; border-radius: 10px; margin-top: 1rem; border: 2px solid #D4AF37; text-align: center; }}
    h2 {{ font-size: 1.1rem !important; }}
    h3 {{ font-size: 0.9rem !important; }}
    h4 {{ font-size: 0.8rem !important; }}
    div[data-testid="stSidebarNav"] {{display: none !important;}}
    div[data-testid="stSidebar"] {{display: none !important;}}
</style>
""", unsafe_allow_html=True)

db = DatabaseManager()
query_params = st.query_params
selected_job = query_params.get('job', None)

if selected_job:
    job_details = None
    try:
        all_reqs = db.get_all_job_requisitions()
        for r in all_reqs:
            if r.get('status') == 'Approved - Live':
                req_id = r.get('req_id', '')
                # Match by req_id OR old JOB format
                job_ref = f"JOB-{req_id[-6:]}" if len(req_id) >= 6 else req_id
                if req_id == selected_job or job_ref == selected_job or f"JOB-{req_id}" == selected_job:
                    job_details = r
                    break
    except:
        pass
    
    position_name = job_details.get('title', selected_job).replace('**', '') if job_details else selected_job.replace('**', '')
    position_name = position_name.replace('**', '')
    
    hero_html = f"""<div class="career-hero animate-fade-in">
        {f'<img src="data:image/png;base64,{logo_b64}" style="height: 50px; margin-bottom: 1rem; position: relative;" alt="Churchgate Group">' if logo_b64 else ''}
        <h1>📝 Apply for {position_name}</h1>
        <p>{job_details.get('department', '')} | {job_details.get('location', '')} | {job_details.get('job_type', '')}</p>
    </div>"""
    st.markdown(hero_html, unsafe_allow_html=True)
    
    if job_details:
        with st.expander("📋 View Full Job Description", expanded=True):
            jd_text = job_details.get("jd", "")
            import re
            section_headers = ['About the Role', 'What You Will Do', 'What Success Looks Like', 'What We Are Looking For', 'Preferred Background', 'Key Responsibilities', 'Requirements', 'Experience', 'Education', 'Skills & Competencies', 'Working Conditions', 'Why Join Churchgate', 'How to Apply', 'Job Summary', 'Job Details', 'About Company']
            for header in section_headers:
                jd_text = jd_text.replace(header, f'<br><br><strong style="font-size:1.15rem;color:#1a1a1a;border-bottom:2px solid #CC0000;padding-bottom:3px;">{header}</strong><br>')
            jd_text = jd_text.replace('• ', '<br>🔹 ').replace('● ', '<br>🔹 ')
            jd_text = re.sub(r'(?<=\n)- ', '<br>🔹 ', jd_text)
            jd_text = jd_text.replace('\n\n', '<br><br>').replace('\n', '<br>')
            st.markdown(f'<div class="jd-content animate-fade-in-up">{jd_text}</div>', unsafe_allow_html=True)
    
    st.markdown("<div class='form-container animate-slide-in'>", unsafe_allow_html=True)
    
    with st.form("job_application", clear_on_submit=True):
        st.markdown("### Personal Information")
        c1, c2 = st.columns(2)
        with c1:
            first_name = st.text_input("First Name *")
            last_name = st.text_input("Last Name *")
            email = st.text_input("Email *")
            phone = st.text_input("Phone Number *")
        with c2:
            linkedin = st.text_input("LinkedIn Profile URL")
            github = st.text_input("GitHub / Portfolio URL")
            current_position = st.text_input("Current/Last Position")
            years_exp = st.selectbox("Years of Experience", ["0-1", "1-3", "3-5", "5-7", "7-10", "10+", "15+", "20+"])
        
        st.markdown("---")
        cover_letter = st.text_area("Cover Letter (Optional)", height=120)
        st.markdown("---")
        resume = st.file_uploader("Upload CV/Resume *", type=['pdf', 'docx'])
        other_docs = st.file_uploader("Upload Other Documents (Optional)", type=['pdf', 'docx', 'jpg', 'png', 'jpeg'], accept_multiple_files=True)
        st.markdown("---")
        st.markdown("### Screening Questions")
        q1 = st.text_area("1. Describe your most relevant experience for this position. *", height=80)
        q2 = st.text_area("2. What is your proudest professional achievement? *", height=80)
        q3 = st.text_area("3. Why do you want to join Churchgate Group? *", height=80)
        st.markdown("*All fields marked with * are required.*")
        
        submitted = st.form_submit_button("📤 Submit Application", use_container_width=True)
        
        if submitted:
            if first_name and last_name and email and phone and resume and q1 and q2 and q3:
                try:
                    resume_text = ""
                    file_ext = "pdf"
                    if resume.type == "application/pdf":
                        import PyPDF2
                        pdf_reader = PyPDF2.PdfReader(resume)
                        for page in pdf_reader.pages:
                            resume_text += page.extract_text() + "\n"
                        file_ext = "pdf"
                    elif "word" in resume.type or "docx" in resume.type:
                        import docx
                        doc = docx.Document(resume)
                        resume_text = "\n".join([p.text for p in doc.paragraphs])
                        file_ext = "docx"
                    
                    tracking_id = f"CG-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
                    
                    # Upload original file to Supabase Storage
                    cv_url = ""
                    try:
                        resume.seek(0)
                        file_content = resume.read()
                        file_name = f"{tracking_id}_{first_name}_{last_name}.{file_ext}"
                        cv_url = db.upload_file("cvs", file_name, file_content, resume.type)
                        if cv_url:
                            st.success("✅ CV uploaded to storage!")
                    except Exception as e:
                        st.warning(f"Storage upload: {str(e)}")
                    
                    db._post("candidates", {
                        "candidate_ref": tracking_id, "first_name": first_name, "last_name": last_name,
                        "email": email, "phone": phone, "linkedin_url": linkedin,
                        "current_position": current_position, "current_company": "",
                        "years_of_experience": years_exp.replace("+","").split("-")[0] if "-" in years_exp else years_exp.replace("+",""),
                        "education_level": "", "skills": "", "location": "",
                        "resume_filename": f"CV_{first_name}_{last_name}.{file_ext}",
                        "resume_text": resume_text[:10000],
                        "cv_url": cv_url,
                        "other_docs": str(other_docs.name) if other_docs else "",
                        "job_id": selected_job,
                        "source": "Career Portal", "status": "New", "ai_score": 0, "ai_tier": "Pending"
                    })
                    
                    db._post("applications", {
                        "tracking_id": tracking_id, "first_name": first_name, "last_name": last_name,
                        "email": email, "phone": phone, "job_ref": selected_job,
                        "position_name": position_name, "status": "Received",
                        "applied_date": datetime.now().strftime('%Y-%m-%d %H:%M WAT')
                    })
                    
                    try:
                        from utils.email_service import EmailService
                        result, msg = EmailService().send_email(email, "Application Received - Churchgate Group",
                            f"Dear {first_name},\n\nThank you for applying for {position_name} at Churchgate Group.\n\nYour Tracking ID: {tracking_id}\n\nWe will review your application and get back to you.\n\nBest regards,\nChurchgate Group HR")
                        if result:
                            st.info(f"📧 Confirmation email sent to {email}")
                        else:
                            st.warning(f"Email not sent: {msg}")
                    except Exception as e:
                        st.warning(f"Email service: {str(e)}")
                    
                    st.success(f"✅ Thank you, {first_name}! Your application has been submitted.")
                    st.balloons()
                    
                    st.markdown(f"""
                    <div class="success-box animate-fade-in-up">
                        <h2 style="color: #38a169;">📋 Application Received!</h2>
                        <p style="font-size: 1.2rem;"><strong>Tracking ID:</strong> {tracking_id}</p>
                        <p style="font-size: 1.1rem;"><strong>Position:</strong> {position_name}</p>
                        <p>📧 Confirmation sent to <strong>{email}</strong></p>
                        <p>🔍 Check status anytime with your Tracking ID</p>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.error("❌ Please fill all required fields marked with *")
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    hero_html = f"""<div class="career-hero animate-fade-in">
        {f'<img src="data:image/png;base64,{logo_b64}" style="height: 60px; margin-bottom: 1.5rem; position: relative;" alt="Churchgate Group">' if logo_b64 else ''}
        <h1>🚀 Build Your Career at Churchgate Group</h1>
        <p>Join a team of innovators, leaders, and changemakers shaping Africa's real estate and infrastructure future.</p>
    </div>"""
    st.markdown(hero_html, unsafe_allow_html=True)
    
    # Load jobs for stats count
    jobs = []
    try:
        import requests
        supabase_url = os.environ.get("SUPABASE_URL", "https://pobfydvkjzhkmhuqwmtf.supabase.co")
        supabase_key = os.environ.get("SUPABASE_KEY", "sb_publishable_iDYmuO5jfqmzydDPgNhL3w_b21rWMhm")
        headers = {"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"}
        url = f"{supabase_url}/rest/v1/job_requisitions?select=*"
        r = requests.get(url, headers=headers)
        all_reqs = r.json() if r.status_code == 200 else []
        for req in all_reqs:
            if req.get('status') == 'Approved - Live':
                job_ref = f"JOB-{req.get('req_id', '')[-6:]}"
                jobs.append({"ref": job_ref, "title": req.get('title', '').replace('**', ''), "dept": req.get('department', ''), 
                            "location": req.get('location', ''), "type": req.get('job_type', ''), 
                            "closing": req.get('closing', ''), "jd": req.get('jd', '')})
    except:
        pass
    
    # Stats bar
    try:
        emp_count = len(db.get_all_employees()) if not db.get_all_employees().empty else 200
    except:
        emp_count = 200
    live_count = len(jobs)
    st.markdown(f"""<div style="display:flex;justify-content:space-around;background:#1a1a1a;padding:0.3rem 1rem;border-bottom:2px solid #D4AF37;"><div style="text-align:center;"><div style="font-size:1rem;font-weight:800;color:#D4AF37;">{emp_count}+</div><div style="font-size:0.5rem;color:#c4b998;">TEAM</div></div><div style="text-align:center;"><div style="font-size:1rem;font-weight:800;color:#D4AF37;">3</div><div style="font-size:0.5rem;color:#c4b998;">REGIONS</div></div><div style="text-align:center;"><div style="font-size:1rem;font-weight:800;color:#D4AF37;">16</div><div style="font-size:0.5rem;color:#c4b998;">SUBSIDIARIES</div></div><div style="text-align:center;"><div style="font-size:1rem;font-weight:800;color:#D4AF37;">{live_count}</div><div style="font-size:0.5rem;color:#c4b998;">OPENINGS</div></div><div style="text-align:center;"><div style="font-size:1rem;font-weight:800;color:#D4AF37;">50+</div><div style="font-size:0.5rem;color:#c4b998;">YEARS</div></div></div>""", unsafe_allow_html=True)
    
    # Search filters
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search_query = st.text_input("🔍 Search jobs", placeholder="Search by title, skill, department...", label_visibility="collapsed")
    with c2:
        dept_filter = st.selectbox("Department", ["All Departments", "Technology Group", "Facility Management", "Human Resources", "Accounts & Finance", "Sales & Marketing", "Procurement", "Security", "Legal", "Operations"], label_visibility="collapsed")
    with c3:
        type_filter = st.selectbox("Type", ["All Types", "Full-time", "Contract", "Part-time", "Intern"], label_visibility="collapsed")
    
    # Filter jobs
    filtered_jobs = []
    for job in jobs:
        if search_query and search_query.lower() not in job['title'].lower(): continue
        if dept_filter != "All Departments" and job['dept'] != dept_filter: continue
        if type_filter != "All Types" and job['type'] != type_filter: continue
        filtered_jobs.append(job)
    
    st.markdown("---")
    
    if filtered_jobs:
        st.markdown(f"### 📋 {len(filtered_jobs)} Open Position{'s' if len(filtered_jobs) > 1 else ''}")
        for job in filtered_jobs:
            try:
                closing_date = datetime.strptime(job['closing'], '%Y-%m-%d')
                days_left = (closing_date - datetime.now()).days
                days_text = f"⏰ {days_left} days remaining" if days_left > 0 else "🔴 Closing soon"
            except:
                days_text = ""
            
            dept_icon = dept_icons.get(job['dept'], "🏢")
            clean_title = job['title'].replace('**', '')
            with st.expander(f"{dept_icon} {clean_title} — {job['dept']} | {job['location']}", expanded=False):
                st.markdown(f"""<span class="tag">💼 {job['type']}</span><span class="tag">📍 {job['location']}</span><span class="tag">🏢 {job['dept']}</span><span class="tag">{days_text}</span>""", unsafe_allow_html=True)
                st.markdown("---")
                
                jd_text = job["jd"]
                import re
                section_headers = ['About the Role', 'What You Will Do', 'What Success Looks Like', 'What We Are Looking For', 'Preferred Background', 'Key Responsibilities', 'Requirements', 'Experience', 'Education', 'Skills & Competencies', 'Working Conditions', 'Why Join Churchgate', 'How to Apply', 'Job Summary', 'Job Details', 'About Company']
                for header in section_headers:
                    jd_text = jd_text.replace(header, f'<br><br><strong style="font-size:1.15rem;color:#1a1a1a;border-bottom:2px solid #CC0000;padding-bottom:3px;">{header}</strong><br>')
                jd_text = jd_text.replace('• ', '<br>🔹 ').replace('● ', '<br>🔹 ')
                jd_text = re.sub(r'(?<=\n)- ', '<br>🔹 ', jd_text)
                jd_text = jd_text.replace('\n\n', '<br><br>').replace('\n', '<br>')
                st.markdown(f'<div class="jd-content animate-fade-in">{jd_text}</div>', unsafe_allow_html=True)
                
                st.markdown(f"<small style='color:#888;'>📅 Closes: {job['closing']} | Ref: {job['ref']}</small>", unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button(f"📝 Apply Now - {job['title']}", key=f"apply_{job['ref']}"):
                        st.query_params['job'] = job['ref']
                        st.rerun()
                with c2:
                    share_url = f"https://churchgate-churchgate-hris.hf.space/Careers?job={job['ref']}"
                    st.markdown(f"""<div style="margin-top:0.5rem;"><a href="https://www.linkedin.com/sharing/share-offsite/?url={share_url}" target="_blank">🔗 LinkedIn</a> <a href="https://wa.me/?text=Job:{job['title']}%20at%20Churchgate%20Group%20{share_url}" target="_blank">💬 WhatsApp</a> <a href="https://twitter.com/intent/tweet?text=Job:{job['title']}%20at%20Churchgate%20Group&url={share_url}" target="_blank">🐦 Twitter</a></div>""", unsafe_allow_html=True)
    else:
        st.info("🎯 No open positions at the moment.")
    
    st.markdown("---")
    with st.expander("🔔 Get Job Alerts"):
        alert_email = st.text_input("Your email", placeholder="Enter email for job notifications", key="alert_email")
        if st.button("Subscribe to Job Alerts") and alert_email:
            try:
                db._post("job_alerts", {"email": alert_email, "created_at": datetime.now().strftime('%Y-%m-%d %H:%M')})
                st.success("✅ You'll be notified of new openings!")
            except:
                st.success("✅ Subscribed!")
    
    st.markdown("---")
    st.markdown("## 🎁 Why Choose Churchgate Group?")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="benefit-card animate-fade-in-up"><div class="benefit-icon">🏥</div><h4>Health Insurance</h4><p style="font-size:0.85rem;color:#666;">Comprehensive HMO coverage</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="benefit-card animate-fade-in-up"><div class="benefit-icon">💰</div><h4>Pension Plan</h4><p style="font-size:0.85rem;color:#666;">Secure retirement with contributory pension scheme</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="benefit-card animate-fade-in-up"><div class="benefit-icon">📚</div><h4>Learning & Development</h4><p style="font-size:0.85rem;color:#666;">Continuous training, certifications, and mentorship</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="benefit-card animate-fade-in-up"><div class="benefit-icon">🏖️</div><h4>Annual Leave</h4><p style="font-size:0.85rem;color:#666;">Generous paid time off to recharge and refresh</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 🌟 What Our Team Says")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="testimonial-card animate-slide-in"><h4>🎯 Career Growth</h4><p style="font-size:0.9rem;color:#666;">"Churchgate gave me the platform to grow from a junior engineer to leading major projects across Africa."</p><p style="color:#CC0000;font-weight:600;">— Senior Engineer, Technology Group</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="testimonial-card animate-slide-in"><h4>💡 Innovation</h4><p style="font-size:0.9rem;color:#666;">"The freedom to innovate and implement AI solutions has been the highlight of my career."</p><p style="color:#CC0000;font-weight:600;">— AI Transformation Lead</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="testimonial-card animate-slide-in"><h4>🤝 Culture</h4><p style="font-size:0.9rem;color:#666;">"The collaborative spirit here is unmatched. Every voice matters, every idea counts."</p><p style="color:#CC0000;font-weight:600;">— HR Business Partner</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f'<div class="social-proof"><h3>🏆 Recognized Excellence</h3><p style="color:#666;">EDGE Certified | Premier Accredited — Business & Member Services, Commercial Real Estate & Services, Trade Development by <a href="https://www.wtca.org" target="_blank" style="color: #CC0000; text-decoration: none;">WTCA</a></p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("🔍 Check Your Application Status"):
        tracking_input = st.text_input("Enter your Tracking ID", placeholder="e.g., CG-20260522-1234")
        if tracking_input:
            try:
                result = db.supabase.table("applications").select("*").eq("tracking_id", tracking_input).execute()
                apps = result.data if result.data else []
                if apps and len(apps) > 0:
                    app = apps[0]
                    st.success("✅ Application Found!")
                    st.markdown(f"**Status:** {app.get('status', 'Received')}")
                    st.markdown(f"**Position:** {app.get('position_name', app.get('job_ref', 'N/A'))}")
                    st.markdown(f"**Applied:** {app.get('applied_date', 'N/A')}")
                else:
                    st.warning("No application found with that Tracking ID.")
            except:
                st.info("Status check is being set up. Please check back soon.")

st.markdown("""
<div class="footer">
    <h3>Churchgate Group</h3>
    <p>Churchgate Towers, PC 30 Churchgate Street, Victoria Island, Lagos, Nigeria.</p>
    <p>📧 careers@churchgate.com</p>
    <p style="margin-top: 1rem; font-size: 0.85rem;">Churchgate Group is an equal opportunity employer. All employment decisions are based on merit, competence, and business needs.</p>
    <p style="font-size: 0.8rem;">© 2026 Churchgate Group. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
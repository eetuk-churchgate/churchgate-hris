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
@@ -37,33 +59,42 @@
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background: linear-gradient(180deg, #faf9f6 0%, #f5f0e8 50%, #faf9f6 100%) !important; }}
    @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .animate-fade-in {{ animation: fadeIn 0.8s ease-out; }}
    .animate-fade-in-up {{ animation: fadeInUp 0.8s ease-out; }}
    .career-hero {{ background: linear-gradient(135deg, #e8e8e8 0%, #d5d5d5 50%, #e0e0e0 100%); padding: 1.5rem 2rem; text-align: center; border-bottom: 3px solid #CC0000; position: relative; overflow: hidden; }}
    .career-hero h1 {{ font-size: 2rem; font-weight: 800; margin: 0; color: #1a1a1a; position: relative; }}
    .career-hero p {{ font-size: 0.95rem; margin-top: 0.5rem; color: #555; position: relative; max-width: 600px; margin-left: auto; margin-right: auto; }}
    .job-hero {{ background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 1.5rem 2rem; border-bottom: 3px solid #CC0000; margin-bottom: 1.5rem; }}
    .job-hero h1 {{ color: white; font-size: 1.6rem; margin: 0; font-weight: 700; }}
    .job-hero p {{ color: #ccc; margin: 0.3rem 0 0 0; font-size: 0.9rem; }}
    .search-bar {{ background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); margin: -2rem 2rem 2rem 2rem; position: relative; z-index: 10; }}
    .job-card {{ background: white; padding: 0; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #CC0000; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: all 0.3s ease; overflow: hidden; }}
    .job-card:hover {{ transform: translateX(6px); box-shadow: 0 6px 20px rgba(204,0,0,0.12); }}
    .tag {{ display: inline-block; background: #f5f5f5; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; margin-right: 0.5rem; margin-top: 0.5rem; color: #555; }}
    .info-card {{ background:white;padding:0.8rem;border-radius:8px;text-align:center;border:1px solid #e0e0e0; }}
    .stButton > button {{ background: #CC0000 !important; color: white !important; border: none !important; padding: 0.8rem 2.5rem !important; border-radius: 8px !important; font-weight: 600 !important; font-size: 1rem !important; }}
    .stButton > button:hover {{ background: #aa0000 !important; transform: translateY(-2px) !important; box-shadow: 0 5px 15px rgba(204,0,0,0.3) !important; }}
    .benefit-card {{ background: white; padding: 1.5rem; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: all 0.3s ease; border-bottom: 3px solid transparent; }}
    .benefit-card:hover {{ border-bottom-color: #CC0000; transform: translateY(-5px); }}
    .benefit-icon {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
    .testimonial-card {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: center; border-top: 3px solid #CC0000; }}
    .social-proof {{ background: white; padding: 2rem; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin: 2rem 0; }}
    .footer {{ background: linear-gradient(135deg, #e8e8e8 0%, #d5d5d5 100%); color: #555; padding: 1.5rem 2rem; text-align: center; margin-top: 2rem; border-top: 3px solid #CC0000; font-size: 0.85rem; }}
    .footer h3 {{ color: #CC0000; font-weight: 700; font-size: 1rem; margin-bottom: 0.3rem; }}
    .jd-content {{ line-height: 2; font-size: 0.95rem; color: #444; }}
    .jd-content strong {{ color: #1a1a1a; font-size: 1.1rem; }}
    .success-box {{ background: linear-gradient(135deg, #f0f8f0, #e8f5e9); padding: 2rem; border-radius: 12px; margin-top: 1rem; border: 2px solid #38a169; text-align: center; }}
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
@@ -230,39 +261,59 @@
    </div>"""
    st.markdown(hero_html, unsafe_allow_html=True)

    st.markdown("<div class='search-bar animate-fade-in-up'>", unsafe_allow_html=True)
    # Stats bar - RIGHT AFTER HERO, BEFORE SEARCH
    try:
        emp_count = len(db.get_all_employees()) if not db.get_all_employees().empty else 200
    except:
        emp_count = 200
    
    # Load jobs first to get live count
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
    st.markdown("</div>", unsafe_allow_html=True)

    jobs = []
    try:
        all_reqs = db.get_all_job_requisitions()
        for r in all_reqs:
            if r.get('status') == 'Approved - Live':
                job_ref = f"JOB-{r.get('req_id', '')[-6:]}"
                if search_query and search_query.lower() not in r.get('title', '').lower():
                    continue
                if dept_filter != "All Departments" and r.get('department', '') != dept_filter:
                    continue
                if type_filter != "All Types" and r.get('job_type', '') != type_filter:
                    continue
                jobs.append({"ref": job_ref, "title": r.get('title', '').replace('**', ''), "dept": r.get('department', ''), 
                            "location": r.get('location', ''), "type": r.get('job_type', ''), 
                            "closing": r.get('closing', ''), "jd": r.get('jd', '')})
    except:
        pass
    # Filter jobs based on search
    filtered_jobs = []
    for job in jobs:
        if search_query and search_query.lower() not in job['title'].lower():
            continue
        if dept_filter != "All Departments" and job['dept'] != dept_filter:
            continue
        if type_filter != "All Types" and job['type'] != type_filter:
            continue
        filtered_jobs.append(job)

    st.markdown("---")

    if jobs:
        st.markdown(f"### 📋 {len(jobs)} Open Position{'s' if len(jobs) > 1 else ''}")
        for job in jobs:
    if filtered_jobs:
        st.markdown(f"### 📋 {len(filtered_jobs)} Open Position{'s' if len(filtered_jobs) > 1 else ''}")
        for job in filtered_jobs:
            try:
                closing_date = datetime.strptime(job['closing'], '%Y-%m-%d')
                days_left = (closing_date - datetime.now()).days
@@ -271,95 +322,83 @@
                days_text = ""

            dept_icon = dept_icons.get(job['dept'], "🏢")
            
            clean_title = job['title'].replace('**', '')
            with st.expander(f"{dept_icon} {clean_title} — {job['dept']} | {job['location']}", expanded=False):
                st.markdown(f"""<span class="tag">💼 {job['type']}</span><span class="tag">📍 {job['location']}</span><span class="tag">🏢 {job['dept']}</span><span class="tag">{days_text}</span>""", unsafe_allow_html=True)
                st.markdown("---")

                jd_text = job["jd"]
                import re
                section_headers = ['About the Role', 'What You Will Do', 'What Success Looks Like', 'What We Are Looking For', 'Preferred Background', 'Key Responsibilities', 'Requirements', 'Experience', 'Education', 'Skills & Competencies', 'Working Conditions', 'Why Join Churchgate', 'How to Apply', 'Job Summary', 'Job Details', 'About Company']
                section_headers = ['About the Role', 'What You Will Do', 'Key Responsibilities', 'Requirements', 'Qualifications', 'Skills']
                for header in section_headers:
                    jd_text = jd_text.replace(header, f'<br><br><strong style="font-size:1.15rem;color:#1a1a1a;border-bottom:2px solid #CC0000;padding-bottom:3px;">{header}</strong><br>')
                jd_text = jd_text.replace('• ', '<br>🔹 ').replace('● ', '<br>🔹 ')
                    jd_text = jd_text.replace(header, f'<br><br><strong style="font-size:1rem;color:#1a1a1a;">{header}</strong><br>')
                jd_text = jd_text.replace('• ', '<br>🔹 ')
                jd_text = re.sub(r'(?<=\n)- ', '<br>🔹 ', jd_text)
                jd_text = jd_text.replace('\n\n', '<br><br>').replace('\n', '<br>')
                st.markdown(f'<div class="jd-content animate-fade-in">{jd_text}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="jd-content">{jd_text[:500]}...</div>', unsafe_allow_html=True)

                st.markdown(f"<small style='color: #888;'>📅 Closes: {job['closing']} | Ref: {job['ref']}</small>", unsafe_allow_html=True)
                st.markdown(f"<small style='color:#888;'>📅 Closes: {job['closing']} | Ref: {job['ref']}</small>", unsafe_allow_html=True)

                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button(f"📝 Apply Now - {job['title']}", key=f"apply_{job['ref']}"):
                    if st.button(f"📝 Apply Now", key=f"apply_{job['ref']}", type="primary"):
                        st.query_params['job'] = job['ref']
                        st.rerun()
                with c2:
                    share_url = f"https://churchgate-hris.streamlit.app/Careers?job={job['ref']}"
                    st.markdown(f"""<div style="margin-top: 0.5rem;"><a href="https://www.linkedin.com/sharing/share-offsite/?url={share_url}" target="_blank" class="share-btn">🔗 LinkedIn</a><a href="https://wa.me/?text=Job%20Opening:%20{job['title']}%20at%20Churchgate%20Group%20-%20Apply%20here:%20{share_url}" target="_blank" class="share-btn">💬 WhatsApp</a><a href="https://twitter.com/intent/tweet?text=Job%20Opening:%20{job['title']}%20at%20Churchgate%20Group&url={share_url}" target="_blank" class="share-btn">🐦 Twitter</a></div>""", unsafe_allow_html=True)
                    share_url = f"https://churchgate-churchgate-hris.hf.space/Careers?job={job['ref']}"
                    st.markdown(f"<small>Share: <a href='https://www.linkedin.com/sharing/share-offsite/?url={share_url}' target='_blank'>LinkedIn</a> | <a href='https://wa.me/?text=Job:{job['title']}%20at%20Churchgate%20Group%20{share_url}' target='_blank'>WhatsApp</a></small>", unsafe_allow_html=True)
    else:
        st.info("🎯 No open positions at the moment.")

    st.markdown("---")
    with st.expander("🔔 Get Job Alerts"):
        alert_email = st.text_input("Your email", placeholder="Enter email for job notifications", key="alert_email")
        if st.button("Subscribe to Job Alerts"):
            if alert_email:
                try:
                    db._post("job_alerts", {"email": alert_email, "created_at": datetime.now().strftime('%Y-%m-%d %H:%M')})
                    st.success("✅ You'll be notified of new openings!")
                except:
                    st.success("✅ Subscribed!")
        if st.button("Subscribe") and alert_email:
            try:
                db._post("job_alerts", {"email": alert_email, "created_at": datetime.now().strftime('%Y-%m-%d %H:%M')})
                st.success("✅ Subscribed!")
            except:
                st.success("✅ Subscribed!")

    st.markdown("---")
    st.markdown("## 🎁 Why Choose Churchgate Group?")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="benefit-card animate-fade-in-up"><div class="benefit-icon">🏥</div><h4>Health Insurance</h4><p style="font-size:0.85rem;color:#666;">Comprehensive HMO coverage</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="benefit-card"><div class="benefit-icon">🏥</div><h4>Health Insurance</h4><p style="font-size:0.8rem;color:#888;">Comprehensive HMO coverage</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="benefit-card animate-fade-in-up"><div class="benefit-icon">💰</div><h4>Pension Plan</h4><p style="font-size:0.85rem;color:#666;">Secure retirement with contributory pension scheme</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="benefit-card"><div class="benefit-icon">💰</div><h4>Pension Plan</h4><p style="font-size:0.8rem;color:#888;">Secure retirement</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="benefit-card animate-fade-in-up"><div class="benefit-icon">📚</div><h4>Learning & Development</h4><p style="font-size:0.85rem;color:#666;">Continuous training, certifications, and mentorship</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="benefit-card"><div class="benefit-icon">📚</div><h4>Learning</h4><p style="font-size:0.8rem;color:#888;">Training & mentorship</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="benefit-card animate-fade-in-up"><div class="benefit-icon">🏖️</div><h4>Annual Leave</h4><p style="font-size:0.85rem;color:#666;">Generous paid time off to recharge and refresh</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="benefit-card"><div class="benefit-icon">🏖️</div><h4>Annual Leave</h4><p style="font-size:0.8rem;color:#888;">Generous time off</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🌟 What Our Team Says")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="testimonial-card animate-slide-in"><h4>🎯 Career Growth</h4><p style="font-size:0.9rem;color:#666;">"Churchgate gave me the platform to grow from a junior engineer to leading major projects across Africa."</p><p style="color:#CC0000;font-weight:600;">— Senior Engineer, Technology Group</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="testimonial-card"><p style="font-size:0.8rem;color:#888;">"Churchgate gave me the platform to grow."</p><p style="color:#D4AF37;font-weight:600;">— Senior Engineer</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="testimonial-card animate-slide-in"><h4>💡 Innovation</h4><p style="font-size:0.9rem;color:#666;">"The freedom to innovate and implement AI solutions has been the highlight of my career."</p><p style="color:#CC0000;font-weight:600;">— AI Transformation Lead</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="testimonial-card"><p style="font-size:0.8rem;color:#888;">"Freedom to innovate with AI."</p><p style="color:#D4AF37;font-weight:600;">— AI Lead</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="testimonial-card animate-slide-in"><h4>🤝 Culture</h4><p style="font-size:0.9rem;color:#666;">"The collaborative spirit here is unmatched. Every voice matters, every idea counts."</p><p style="color:#CC0000;font-weight:600;">— HR Business Partner</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="testimonial-card"><p style="font-size:0.8rem;color:#888;">"Every voice matters here."</p><p style="color:#D4AF37;font-weight:600;">— HR Partner</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<div class="social-proof"><h3>🏆 Recognized Excellence</h3><p style="color:#666;">EDGE Certified | Premier Accredited — Business & Member Services, Commercial Real Estate & Services, Trade Development by <a href="https://www.wtca.org" target="_blank" style="color: #CC0000; text-decoration: none;">WTCA</a></p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="social-proof"><h3>🏆 Recognized Excellence</h3><p style="color:#888;">EDGE Certified | Premier Accredited by <a href="https://www.wtca.org" target="_blank" style="color:#D4AF37;">WTCA</a></p></div>', unsafe_allow_html=True)

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
                if result.data:
                    app = result.data[0]
                    st.success(f"Status: {app.get('status', 'Received')}")
            except:
                st.info("Status check is being set up. Please check back soon.")
                st.info("Check back soon.")

st.markdown("""
<div class="footer">
st.markdown("""<div class="footer">
    <h3>Churchgate Group</h3>
    <p>Churchgate Towers, PC 30 Churchgate Street, Victoria Island, Lagos, Nigeria.</p>
    <p>📧 careers@churchgate.com</p>
    <p style="margin-top: 1rem; font-size: 0.85rem;">Churchgate Group is an equal opportunity employer. All employment decisions are based on merit, competence, and business needs.</p>
    <p style="font-size: 0.8rem;">© 2026 Churchgate Group. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
    <p>Churchgate Towers, Victoria Island, Lagos. 📧 careers@churchgate.com</p>
    <p style="font-size:0.7rem;">Equal opportunity employer. © 2026 Churchgate Group.</p>
</div>""", unsafe_allow_html=True)

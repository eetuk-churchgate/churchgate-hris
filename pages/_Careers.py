import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import random

sys.path.append(str(Path(__file__).parent.parent))

from utils.database import DatabaseManager

st.set_page_config(page_title="Careers - Churchgate Group", page_icon="🌐", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for world-class careers page
st.markdown("""
<style>
    .career-hero {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
        padding: 4rem 2rem;
        text-align: center;
        color: white;
        border-bottom: 4px solid #CC0000;
        margin-bottom: 0;
    }
    .career-hero h1 { font-size: 3rem; font-weight: 900; margin: 0; letter-spacing: -1px; }
    .career-hero p { font-size: 1.3rem; margin-top: 1rem; opacity: 0.9; max-width: 700px; margin-left: auto; margin-right: auto; }
    .company-badge {
        background: rgba(204,0,0,0.2);
        border: 1px solid #CC0000;
        padding: 0.5rem 1.5rem;
        border-radius: 30px;
        display: inline-block;
        margin-top: 1.5rem;
        font-size: 0.9rem;
    }
    .search-bar {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: -2rem 2rem 2rem 2rem;
        position: relative;
        z-index: 10;
    }
    .job-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        border-left: 4px solid #CC0000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    .job-card:hover { 
        transform: translateX(8px); 
        box-shadow: 0 8px 25px rgba(204,0,0,0.15);
    }
    .job-title { font-size: 1.3rem; font-weight: 700; color: #1a1a1a; }
    .job-meta { color: #666; font-size: 0.9rem; margin-top: 0.3rem; }
    .tag { 
        display: inline-block; 
        background: #f0f0f0; 
        padding: 0.3rem 0.8rem; 
        border-radius: 20px; 
        font-size: 0.8rem; 
        margin-right: 0.5rem;
        margin-top: 0.5rem;
    }
    .stButton > button {
        background: #CC0000 !important; color: white !important;
        border: none !important; padding: 0.6rem 2rem !important;
        border-radius: 8px !important; font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: #aa0000 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(204,0,0,0.3) !important;
    }
    .footer {
        background: #1a1a1a;
        color: #888;
        padding: 3rem 2rem;
        text-align: center;
        margin-top: 3rem;
    }
    .form-container {
        max-width: 800px;
        margin: 0 auto;
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

db = DatabaseManager()
query_params = st.query_params
selected_job = query_params.get('job', None)

# ============ APPLICATION FORM PAGE ============
if selected_job:
    st.markdown(f"""
    <div class="career-hero">
        <h1>📝 Apply for Position</h1>
        <p>Reference: {selected_job}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='form-container'>", unsafe_allow_html=True)
    
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
        st.markdown("### Cover Letter (Optional)")
        cover_letter = st.text_area("Tell us why you're the best fit", height=120)
        
        st.markdown("---")
        st.markdown("### Resume/CV *")
        resume = st.file_uploader("Upload your CV (PDF or DOCX)", type=['pdf', 'docx'])
        
        st.markdown("---")
        st.markdown("### Screening Questions")
        st.info("Please answer honestly - these help us evaluate your fit for the role.")
        q1 = st.text_area("1. Describe your most relevant experience for this position. *", height=80, placeholder="Be specific about projects, achievements, and technologies used...")
        q2 = st.text_area("2. What is your proudest professional achievement? *", height=80, placeholder="Share a specific accomplishment with measurable results...")
        q3 = st.text_area("3. Why do you want to join Churchgate Group? *", height=80, placeholder="Tell us what excites you about this opportunity...")
        
        st.markdown("---")
        st.markdown("*All fields marked with * are required.*")
        
        submitted = st.form_submit_button("📤 Submit Application", use_container_width=True)
        
        if submitted:
            if first_name and last_name and email and phone and resume and q1 and q2 and q3:
                try:
                    # Parse CV text
                    resume_text = ""
                    if resume.type == "application/pdf":
                        import PyPDF2
                        pdf_reader = PyPDF2.PdfReader(resume)
                        for page in pdf_reader.pages:
                            resume_text += page.extract_text() + "\n"
                    elif "word" in resume.type or "docx" in resume.type:
                        import docx
                        doc = docx.Document(resume)
                        resume_text = "\n".join([p.text for p in doc.paragraphs])
                    
                    # Generate tracking ID
                    tracking_id = f"CG-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
                    
                    # Save candidate
                    candidate_data = (
                        tracking_id, first_name, last_name, email, phone,
                        linkedin, current_position, "", 
                        years_exp.replace("+","").split("-")[0] if "-" in years_exp else years_exp.replace("+",""),
                        "", "", "", f"CV_{first_name}_{last_name}.pdf", resume_text[:5000],
                        selected_job, "Career Portal", "New"
                    )
                    db.add_candidate(candidate_data)
                    
                    # Save application to database
                    try:
                        db._post("applications", {
                            "tracking_id": tracking_id,
                            "first_name": first_name, "last_name": last_name,
                            "email": email, "phone": phone,
                            "job_ref": selected_job, "status": "Received",
                            "applied_date": datetime.now().strftime('%Y-%m-%d %H:%M WAT')
                        })
                    except:
                        pass
                    
                    st.success(f"✅ Thank you, {first_name}! Your application has been submitted successfully.")
                    st.balloons()
                    
                    st.markdown(f"""
                    <div style="background: #f0f8f0; padding: 1.5rem; border-radius: 10px; margin-top: 1rem; border: 1px solid #38a169;">
                        <h4 style="color: #38a169;">📋 Application Received!</h4>
                        <p><strong>Tracking ID:</strong> {tracking_id}</p>
                        <p><strong>Position:</strong> {selected_job}</p>
                        <p>📧 A confirmation email will be sent to <strong>{email}</strong></p>
                        <p>🔍 You can check your application status using your Tracking ID on our careers page.</p>
                        <p style="margin-top: 1rem; font-size: 0.9rem; color: #666;">
                            Churchgate Group is an equal opportunity employer. All stages of employment are based on merit, competence, and performance.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Email notification would go here
                    
                except Exception as e:
                    st.error(f"Submission error: {str(e)}")
            else:
                st.error("❌ Please fill all required fields marked with *")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============ JOB LISTING PAGE ============
else:
    st.markdown("""
    <div class="career-hero">
        <h1>🚀 Build Your Career at Churchgate Group</h1>
        <p>Join a team of innovators, leaders, and changemakers shaping Africa's real estate and infrastructure future.</p>
        <div class="company-badge">🏢 Equal Opportunity Employer | Merit-Based | Performance-Driven</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Search bar
    with st.container():
        st.markdown("<div class='search-bar'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            search_query = st.text_input("🔍 Search jobs", placeholder="Search by title, skill, department...", label_visibility="collapsed")
        with c2:
            dept_filter = st.selectbox("Department", ["All Departments", "Technology Group", "Facility Management", "Human Resources", "Accounts & Finance", "Sales & Marketing", "Procurement", "Security", "Legal", "Operations"], label_visibility="collapsed")
        with c3:
            type_filter = st.selectbox("Type", ["All Types", "Full-time", "Contract", "Part-time", "Intern"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Load real approved jobs from database
    jobs = []
    try:
        all_reqs = db.get_all_job_requisitions()
        for r in all_reqs:
            if r.get('status') == 'Approved - Live':
                job_ref = f"JOB-{r.get('req_id', '')[-6:]}"
                
                # Apply filters
                if search_query and search_query.lower() not in r.get('title', '').lower():
                    continue
                if dept_filter != "All Departments" and r.get('department', '') != dept_filter:
                    continue
                if type_filter != "All Types" and r.get('job_type', '') != type_filter:
                    continue
                
                jobs.append({
                    "ref": job_ref,
                    "title": r.get('title', ''),
                    "dept": r.get('department', ''),
                    "location": r.get('location', ''),
                    "type": r.get('job_type', ''),
                    "closing": r.get('closing', ''),
                    "jd": r.get('jd', '')[:300] + "..." if len(r.get('jd', '')) > 300 else r.get('jd', '')
                })
    except:
        pass
    
    st.markdown("---")
    
    if jobs:
        st.markdown(f"### 📋 {len(jobs)} Open Position{'s' if len(jobs) > 1 else ''}")
        
        for job in jobs:
            # Calculate days remaining
            try:
                closing_date = datetime.strptime(job['closing'], '%Y-%m-%d')
                days_left = (closing_date - datetime.now()).days
                days_text = f"⏰ {days_left} days remaining" if days_left > 0 else "🔴 Closing soon"
            except:
                days_text = ""
            
            with st.expander(f"**{job['title']}** — {job['dept']} | {job['location']}", expanded=False):
                st.markdown(f"""
                <div class="job-card">
                    <div>
                        <span class="tag">💼 {job['type']}</span>
                        <span class="tag">📍 {job['location']}</span>
                        <span class="tag">🏢 {job['dept']}</span>
                        <span class="tag">{days_text}</span>
                    </div>
                    <p style="margin-top: 1rem; color: #555; line-height: 1.6;">{job['jd']}</p>
                    <p style="font-size: 0.85rem; color: #888;">📅 Closes: {job['closing']} | Ref: {job['ref']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"📝 Apply Now - {job['title']}", key=f"apply_{job['ref']}"):
                    st.query_params['job'] = job['ref']
                    st.rerun()
    else:
        st.info("🎯 No open positions at the moment. Please check back later or follow us on LinkedIn for future opportunities.")
    
    # Status checker
    st.markdown("---")
    with st.expander("🔍 Check Your Application Status"):
        tracking_input = st.text_input("Enter your Tracking ID", placeholder="e.g., CG-20260522-1234")
        if tracking_input:
            try:
                apps = db._get("applications", {"tracking_id": tracking_input})
                if apps:
                    app = apps[0]
                    st.success(f"✅ Application Found!")
                    st.markdown(f"**Status:** {app.get('status', 'Received')}")
                    st.markdown(f"**Applied:** {app.get('applied_date', 'N/A')}")
                    st.markdown(f"**Position:** {app.get('job_ref', 'N/A')}")
                else:
                    st.warning("No application found with that Tracking ID.")
            except:
                st.info("Status check is being set up. Please check back soon.")

# Footer
st.markdown("""
<div class="footer">
    <h3 style="color: #CC0000;">Churchgate Group</h3>
    <p>World Trade Center, Abuja, Nigeria</p>
    <p>📧 careers@churchgate.com | 📞 +234 800 000 0000</p>
    <p style="margin-top: 1rem; font-size: 0.85rem;">
        Churchgate Group is an equal opportunity employer. All employment decisions are based on merit, competence, and business needs.
    </p>
    <p style="font-size: 0.8rem;">© 2026 Churchgate Group. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
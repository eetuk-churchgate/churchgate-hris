"""
Churchgate Group HRIS v5.0
Enterprise-Grade AI-Powered Human Resource Information System
"""

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import hashlib
from pathlib import Path
import sys
import time
import json
import base64
import io
import os
import random
from PIL import Image
import calendar

sys.path.append(str(Path(__file__).parent))

from utils.database import DatabaseManager
from utils.ai_agent import AIRecruitmentAgent
from utils.linkedin_parser import LinkedInParser
from utils.email_service import EmailService
from utils.chat_service import ChatService
from utils.training_service import TrainingService

st.set_page_config(page_title="Churchgate Group HRIS", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

CHURCHGATE_RED = "#CC0000"
CHURCHGATE_DARK = "#1a1a1a"
CHURCHGATE_GREY = "#4a4a4a"
CHURCHGATE_LIGHT = "#f5f5f5"
CHURCHGATE_WHITE = "#ffffff"

CHURCHGATE_PURPOSE = "To improve the lives of all those we serve."
CHURCHGATE_VISION = "To become the premier property developer in Nigeria, impacting millions, while having fun!"
CHURCHGATE_MISSION = "To provide our customers with innovative and sustainable real estate solutions that enable them to thrive."

CHURCHGATE_VALUES = {
    "Humility": "We pride in selflessness and dignity with a natural ability to improve our services and make our offerings better.",
    "Gratitude": "Our customers are at the crux of our activities, thus we are devoted to ensuring the best experience with us.",
    "Integrity": "We are responsible for our actions, and our results. We keep to our word!",
    "Hunger": "We are driven by our commitment and dedication to make our services better.",
    "Passion": "Your satisfaction is our pleasure. We strive to always leave you with a bigger smile than you came with."
}

CHURCHGATE_PORTFOLIO = [
    "World Trade Center Abuja",
    "Churchgate Tower 1, Lagos",
    "Churchgate Tower 2, Lagos",
    "Churchgate Plaza, Abuja",
    "Warehouses",
    "Ocean Terrace"
]

st.markdown("""
<style>
    .stApp { background: #e8e8e8; }
    .main > div { background: #e8e8e8; }
    section[data-testid="stSidebar"] { background-color: #d5d5d5 !important; }
    section[data-testid="stSidebar"] * { color: #333333 !important; }
    section[data-testid="stSidebar"] .stButton > button { background-color: #c0c0c0 !important; border: 1px solid #a0a0a0 !important; color: #333333 !important; }
    section[data-testid="stSidebar"] .nav-link { color: #333333 !important; }
    section[data-testid="stSidebar"] .nav-link span { color: #333333 !important; font-size: 14px !important; }
    section[data-testid="stSidebar"] .nav-link svg { color: #CC0000 !important; }
    section[data-testid="stSidebar"] .nav-link-selected { background-color: #c0c0c0 !important; border-left: 3px solid #CC0000 !important; }
    section[data-testid="stSidebar"] .nav-link-selected span { color: #CC0000 !important; font-weight: 700 !important; }
    .churchgate-header { background: white; padding: 1.5rem 2rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #CC0000; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .churchgate-header h1 { color: #1a1a1a; font-size: 1.8rem; font-weight: 700; margin: 0; }
    .churchgate-header p { color: #666; font-size: 0.9rem; margin-top: 0.3rem; }
    .metric-card { background: white; padding: 1.2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); text-align: center; border: 1px solid #cccccc; transition: all 0.2s ease; }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #1a1a1a; }
    .metric-label { color: #666; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .stButton > button { background: #CC0000 !important; color: white !important; border: none !important; padding: 0.5rem 1rem !important; border-radius: 6px !important; font-weight: 600 !important; }
    .stButton > button:hover { background: #aa0000 !important; }
    .mission-banner { background: #d5d5d5; padding: 1.5rem; border-radius: 8px; text-align: center; margin: 1.5rem 0; border: 2px solid #CC0000; }
    .mission-banner h2 { color: #CC0000; font-size: 1.3rem; }
    .mission-banner h3 { color: #1a1a1a; }
    .mission-banner p { color: #333333; }
    .value-card { background: white; padding: 0.8rem; border-radius: 6px; text-align: center; border: 1px solid #cccccc; }
    .tier-1-badge { background: #38a169; color: white; padding: 0.3rem 0.6rem; border-radius: 15px; font-weight: 600; font-size: 0.8rem; }
    .tier-2-badge { background: #d69e2e; color: #1a1a1a; padding: 0.3rem 0.6rem; border-radius: 15px; font-weight: 600; font-size: 0.8rem; }
    .tier-3-badge { background: #CC0000; color: white; padding: 0.3rem 0.6rem; border-radius: 15px; font-weight: 600; font-size: 0.8rem; }
    .status-active { background: #38a169; color: white; padding: 0.2rem 0.6rem; border-radius: 15px; font-size: 0.8rem; }
    .status-pending { background: #d69e2e; color: #1a1a1a; padding: 0.2rem 0.6rem; border-radius: 15px; font-size: 0.8rem; }
    .status-at-risk { background: #CC0000; color: white; padding: 0.2rem 0.6rem; border-radius: 15px; font-size: 0.8rem; }
    .stImage { display: flex; justify-content: center; }
    .chat-container { max-height: 400px; overflow-y: auto; padding: 1rem; background: white; border-radius: 8px; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_resources():
    db = DatabaseManager()
    db.create_tables()
    ai_agent = AIRecruitmentAgent()
    linkedin_parser = LinkedInParser()
    email_service = EmailService()
    chat_service = ChatService()
    training_service = TrainingService()
    return db, ai_agent, linkedin_parser, email_service, chat_service, training_service

db, ai_agent, linkedin_parser, email_service, chat_service, training_service = init_resources()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_jd' not in st.session_state:
    st.session_state.current_jd = None
if 'candidates_batch' not in st.session_state:
    st.session_state.candidates_batch = []
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'bot_conversation' not in st.session_state:
    st.session_state.bot_conversation = []
if 'dashboard_metrics' not in st.session_state:
    st.session_state.dashboard_metrics = {
        'total_employees': 48, 'occupancy_rate': 87,
        'revenue_vs_budget': 94, 'tenant_satisfaction': 4.2, 'open_positions': 5
    }

def get_logo():
    logo_paths = [Path(__file__).parent / "churchgate-logo.png", Path(__file__).parent / "churchgate_logo.png"]
    for path in logo_paths:
        if path.exists():
            return Image.open(path)
    return None

def generate_initials(name):
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    return name[:2].upper()

def save_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        if uploaded_file.type == "application/pdf":
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif uploaded_file.type == "text/plain":
            return uploaded_file.read().decode('utf-8')
        elif "word" in uploaded_file.type or "docx" in uploaded_file.type:
            import docx
            doc = docx.Document(uploaded_file)
            return "\n".join([p.text for p in doc.paragraphs])
        else:
            return uploaded_file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f"[Error: {str(e)}]"

def generate_ref(prefix):
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{str(time.time())[-6:]}"

def show_churchgate_mission():
    st.markdown("""
    <div class="mission-banner">
        <h2 style="font-size: 2.5rem; font-weight: 900; letter-spacing: 2px;">CHURCHGATE GROUP</h2>
        <div style="display: flex; justify-content: space-around; margin: 1.5rem 0; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px; padding: 1rem;">
                <h3 style="color: #CC0000;">🎯 Our Purpose</h3>
                <p style="font-size: 0.9rem;">To improve the lives of all those we serve.</p>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 1rem;">
                <h3 style="color: #CC0000;">🔭 Our Vision</h3>
                <p style="font-size: 0.9rem;">To become the premier property developer in Nigeria, impacting millions, while having fun!</p>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 1rem;">
                <h3 style="color: #CC0000;">📋 Our Mission</h3>
                <p style="font-size: 0.9rem;">To provide our customers with innovative and sustainable real estate solutions that enable them to thrive.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### Our Values Are Dear To Us")
    st.markdown("We deliver exceptional properties and infrastructure because we consistently sustain our core values of:")
    cols = st.columns(5)
    for i, (value, desc) in enumerate(CHURCHGATE_VALUES.items()):
        with cols[i]:
            st.markdown(f"""<div class="value-card"><h4 style="color: #CC0000;">{value}</h4><p style="font-size: 0.8rem; color: #666;">{desc}</p></div>""", unsafe_allow_html=True)

def login_section():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo = get_logo()
        if logo:
            ca, cb, cc = st.columns([1, 1, 1])
            with cb:
                st.image(logo, width=300)
        st.markdown("""<div style="text-align: center; padding: 1rem 0;"><h1 style="color: #1a1a1a; font-size: 2rem; font-weight: 700;">HRIS Portal</h1><p style="color: #666666; font-size: 0.9rem;">Human Resource Information System</p></div>""", unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("📧 Corporate Email", placeholder="Enter your corporate email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("🔐 Sign In", use_container_width=True)
            if submit:
                if email and password:
                    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
                    user = db.verify_user(email, hashed_pw)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials.")
                else:
                    st.warning("⚠️ Please enter your email and password.")
        with st.expander("🔑 Demo Credentials"):
            st.markdown("""| Role | Email | Password ||------|-------|----------|| Admin | admin@churchgate.com | admin123 || HR Director | sarah@churchgate.com | hr123 || ELV Head | emmanuel@churchgate.com | elv123 || Employee | jane@churchgate.com | staff123 |""")

def sidebar_navigation():
    with st.sidebar:
        logo = get_logo()
        if logo:
            st.image(logo, width=220)
        st.markdown("""<div style="text-align: center; padding: 0.8rem 0; background: #4a4a4a; border-radius: 6px; margin-bottom: 1rem; border: 1px solid #666666;"><h3 style="color: #ffffff; margin: 0; font-size: 1.1rem; font-weight: 700;">CHURCHGATE GROUP</h3><p style="color: #cccccc; font-size: 0.7rem; margin: 0;">HRIS v5.0</p></div>""", unsafe_allow_html=True)
        if st.session_state.user:
            user = st.session_state.user
            initials = generate_initials(user['name'])
            st.markdown(f"""<div style="background: rgba(255,255,255,0.08); padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid rgba(204, 0, 0, 0.2);"><div style="display: flex; align-items: center; gap: 0.6rem;"><div style="width: 40px; height: 40px; border-radius: 50%; background: #CC0000; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1rem; color: white;">{initials}</div><div><p style="color: #333; margin: 0; font-weight: 600; font-size: 0.85rem;">{user['name']}</p><p style="color: #666; margin: 0; font-size: 0.7rem;">{user['role']} • {user.get('department', '')}</p></div></div></div>""", unsafe_allow_html=True)
        user_role = st.session_state.user['role'] if st.session_state.user else 'Employee'
        if user_role in ['Admin', 'HR Director']:
            menu_options = ["🏠 Employee Dashboard", "📊 Executive Dashboard", "👥 Employee Management", "📈 Performance & OKRs", "🚀 Promotions", "💼 Recruitment Hub", "🤖 AI Recruitment Agent", "📊 Reports & Analytics", "💬 Chat & Communications", "🎓 Training & Development", "🔔 Notifications", "👤 My Profile"]
        elif user_role == 'Manager':
            menu_options = ["🏠 Employee Dashboard", "💼 Recruitment Hub", "🤖 AI Recruitment Agent", "📈 Performance & OKRs", "💬 Chat & Communications", "🎓 Training & Development", "👤 My Profile"]
        else:
            menu_options = ["🏠 Employee Dashboard", "📈 My Performance & OKRs", "💬 Chat & Communications", "🎓 Training & Development", "👤 My Profile"]
        selected = option_menu(menu_title=None, options=menu_options, icons=["house-fill", "speedometer2", "people-fill", "graph-up-arrow", "trophy-fill", "briefcase-fill", "robot", "file-earmark-bar-graph", "chat-dots-fill", "book-fill", "bell-fill", "person-circle"][:len(menu_options)], menu_icon="cast", default_index=0, styles={"container": {"padding": "0!important", "background-color": "transparent"}, "icon": {"color": "#CC0000", "font-size": "16px"}, "nav-link": {"font-size": "13px", "text-align": "left", "margin": "3px 0", "color": "#333333", "--hover-color": "rgba(204, 0, 0, 0.1)", "border-radius": "6px"}, "nav-link-selected": {"background-color": "rgba(204, 0, 0, 0.15)", "color": "#CC0000", "border-left": "3px solid #CC0000", "font-weight": "700"}})
        st.markdown("---")
        if user_role in ['Admin', 'HR Director', 'Manager']:
            st.markdown("<p style='color: #CC0000; font-size: 0.75rem; margin-bottom: 0.5rem;'>⚡ QUICK ACTIONS</p>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📝 Post Job", use_container_width=True, key="qa_job"):
                    st.session_state['navigate_to'] = "💼 Recruitment Hub"
                    st.rerun()
            with c2:
                if st.button("🤖 AI Screen", use_container_width=True, key="qa_ai"):
                    st.session_state['navigate_to'] = "🤖 AI Recruitment Agent"
                    st.rerun()
        if st.session_state.user:
            if st.button("🚪 Sign Out", use_container_width=True):
                st.session_state.user = None
                st.rerun()
        st.markdown("""<div style="text-align: center; padding: 0.5rem; margin-top: 1rem;"><p style="color: #888; font-size: 0.65rem; margin: 0;">© 2026 Churchgate Group</p><p style="color: #888; font-size: 0.65rem; margin: 0;">HRIS v5.0</p></div>""", unsafe_allow_html=True)
        return selected

def employee_dashboard():
    show_churchgate_mission()
    user = st.session_state.user
    st.markdown(f"""<div class="churchgate-header"><h1>👋 Welcome back, {user['name']}!</h1><p>{user.get('position', 'Employee')} • {user.get('department', 'Department')}</p></div>""", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""<div class="metric-card"><div class="metric-label">Profile Completeness</div><div class="metric-value">80%</div><small><span style="color: #CC0000; text-decoration: underline; cursor: pointer;">Edit Profile →</span></small></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="metric-card"><div class="metric-label">Leave Days</div><div class="metric-value">18</div><small style="color: #38a169;">Available</small></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="metric-card"><div class="metric-label">Performance</div><div class="metric-value">93.3%</div><small style="color: #38a169;">↑ 5%</small></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Team Members</div><div class="metric-value">12</div><small>{user.get('department', '')}</small></div>""", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📈 Performance Overview")
        pillars = {"Occupancy & Revenue Growth": 85, "Process Simplification": 72, "Asset Reliability & Digitalization": 90, "People & Culture": 88}
        for pillar, progress in pillars.items():
            color = "#38a169" if progress >= 85 else "#d69e2e"
            st.markdown(f"""<div style="background: white; padding: 0.6rem 1rem; border-radius: 6px; margin-bottom: 0.4rem; display: flex; align-items: center; justify-content: space-between;"><span style="font-weight: 600; font-size: 0.85rem;">{pillar}</span><div style="width: 150px;"><div style="background: #e0e0e0; height: 6px; border-radius: 3px;"><div style="background: {color}; width: {progress}%; height: 6px; border-radius: 3px;"></div></div></div><span style="font-weight: 700; color: {color};">{progress}%</span></div>""", unsafe_allow_html=True)
    with c2:
        st.subheader("🎂 Team Birthdays")
        for b in [{"name": "Chika Ikwuegbu", "date": "May 13", "dept": "Security"}, {"name": "Francis Asuquo", "date": "May 19", "dept": "ELV Systems"}, {"name": "Rhoda Ajibola", "date": "May 25", "dept": "Facility Management"}, {"name": "Alice Agbo", "date": "May 28", "dept": "Procurement"}]:
            st.markdown(f"""<div style="background: white; padding: 0.5rem; border-radius: 6px; margin-bottom: 0.3rem; display: flex; align-items: center; gap: 0.5rem;"><span>🎂</span><div><strong style="font-size: 0.8rem;">{b['name']}</strong><br><small>{b['date']} • {b['dept']}</small></div></div>""", unsafe_allow_html=True)
        st.subheader("🎉 Anniversaries")
        for a in [{"name": "Augustine Oleh", "years": 5}, {"name": "Charles Okere", "years": 8}, {"name": "Emmanuel Etuk", "years": 7}]:
            st.markdown(f"""<div style="background: white; padding: 0.5rem; border-radius: 6px; margin-bottom: 0.3rem;">⭐ <strong>{a['name']}</strong> - {a['years']} years</div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("🎓 Recommended Training")
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        st.markdown("""<div class="metric-card"><h4>🔧 BMS Advanced</h4><p style="font-size: 0.8rem;">Advanced Building Management</p><small style="color: #CC0000;">📅 June 15, 2026</small></div>""", unsafe_allow_html=True)
    with tc2:
        st.markdown("""<div class="metric-card"><h4>🤖 AI in FM</h4><p style="font-size: 0.8rem;">Practical AI for Facilities</p><small style="color: #CC0000;">📅 June 20, 2026</small></div>""", unsafe_allow_html=True)
    with tc3:
        st.markdown("""<div class="metric-card"><h4>📊 Data Analytics</h4><p style="font-size: 0.8rem;">Operational Analytics</p><small style="color: #CC0000;">📅 July 5, 2026</small></div>""", unsafe_allow_html=True)

def executive_dashboard():
    show_churchgate_mission()
    st.markdown("""<div class="churchgate-header"><h1>📊 Executive Dashboard</h1><p>Corporate Strategy 2026-2027 | AI-Powered Group Performance Intelligence</p></div>""", unsafe_allow_html=True)
    
    # TOP METRICS
    metrics = st.session_state.dashboard_metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Employees</div><div class="metric-value">{metrics['total_employees']}</div><small style="color: #38a169;">Active workforce</small></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Occupancy Rate</div><div class="metric-value">{metrics['occupancy_rate']}%</div><small style="color: #38a169;">Across portfolio</small></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Revenue vs Budget</div><div class="metric-value">{metrics['revenue_vs_budget']}%</div><small style="color: #d69e2e;">{100 - metrics['revenue_vs_budget']}% below target</small></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Tenant Satisfaction</div><div class="metric-value">{metrics['tenant_satisfaction']}/5</div><small style="color: #38a169;">↑ 0.3 points</small></div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Open Positions</div><div class="metric-value">{metrics['open_positions']}</div><small style="color: #CC0000;">Active recruitment</small></div>""", unsafe_allow_html=True)
    
    # ADMIN METRICS UPDATE
    if st.session_state.user and st.session_state.user['role'] in ['Admin', 'HR Director']:
        with st.expander("⚙️ Update Dashboard Metrics (Admin)"):
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                ne = st.number_input("Total Employees", value=metrics['total_employees'])
                no = st.slider("Occupancy Rate %", 0, 100, metrics['occupancy_rate'])
            with ec2:
                nr = st.slider("Revenue vs Budget %", 0, 100, metrics['revenue_vs_budget'])
                ns = st.slider("Tenant Satisfaction", 1.0, 5.0, metrics['tenant_satisfaction'], 0.1)
            with ec3:
                np = st.number_input("Open Positions", value=metrics['open_positions'])
            if st.button("💾 Update Metrics", use_container_width=True):
                st.session_state.dashboard_metrics = {'total_employees': ne, 'occupancy_rate': no, 'revenue_vs_budget': nr, 'tenant_satisfaction': ns, 'open_positions': np}
                st.success("✅ Updated!")
                st.rerun()
    
    # STRATEGIC PILLARS OVERVIEW - VISUAL CARDS
    st.markdown("---")
    st.subheader("🎯 Group Strategic Pillars 2026-2027 — Executive Scorecard")
    
    pillars = {
        "1. Occupancy & Revenue Growth": {
            "weight": 40, "progress": 85, "trend": "+5%", "status": "On Track",
            "kpis": ["Data centre revenue +15%", "100% budget realization", "Nil O/S within 30 days", "90% customer retention", "0% cost variance"],
            "responsible": "COO", "accountable": "GMD", "consulted": "All HODs", "informed": "Board",
            "highlight": "Revenue streams from Data Centre, ISP, Managed Services"
        },
        "2. Process Simplification": {
            "weight": 20, "progress": 72, "trend": "+8%", "status": "In Progress",
            "kpis": ["AI implementation by FY end", "BMS complete by 30.06.26", "99% PPM compliance", "99% ELV uptime", "CRM full deployment"],
            "responsible": "ELV/Hive Mechanics", "accountable": "GMD", "consulted": "All HODs", "informed": "Board",
            "highlight": "AI strategy + BMS + SMARTCHECK deployment"
        },
        "3. Asset Reliability & Digitalization": {
            "weight": 25, "progress": 90, "trend": "+3%", "status": "Exceeding",
            "kpis": ["100% ELV assets assessed biannually", "0% variance risk mitigation", "80% risks mitigated", "90% SMARTCHECK by 30.09.26", "100% emergency readiness"],
            "responsible": "FM Heads", "accountable": "COO", "consulted": "VP-Sales/GM-Procurement", "informed": "Board",
            "highlight": "SMARTCHECK 8 modules + preventive maintenance culture"
        },
        "4. People & Culture": {
            "weight": 15, "progress": 88, "trend": "+4%", "status": "On Track",
            "kpis": ["100% JDs by April 2026", "100% appraised 2x yearly", "A-players identified", "Competency gaps assessed", "2 LMS courses/employee", "60-80% behavioural improvement"],
            "responsible": "HR Director", "accountable": "GMD", "consulted": "GEA/COO/HR", "informed": "Board",
            "highlight": "Succession planning + Learning culture + 360° assessment"
        }
    }
    
    # DISPLAY 4 PILLARS AS CARDS IN 2x2 GRID
    p1, p2 = st.columns(2)
    with p1:
        pn = "1. Occupancy & Revenue Growth"
        pdata = pillars[pn]
        color = "#38a169"
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid {color}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; font-size: 1.1rem;">💰 {pn}</h3>
                <span style="background: {color}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: 600;">{pdata['status']} {pdata['trend']}</span>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #666;"><span>Progress</span><span>{pdata['progress']}%</span></div>
                <div style="background: #e0e0e0; height: 8px; border-radius: 4px; margin-top: 0.3rem;"><div style="background: {color}; width: {pdata['progress']}%; height: 8px; border-radius: 4px;"></div></div>
            </div>
            <p style="font-size: 0.8rem; color: #CC0000; font-weight: 600;">🎯 {pdata['highlight']}</p>
            <div style="font-size: 0.8rem; margin: 0.5rem 0;">
                <strong>RACI:</strong> R: {pdata['responsible']} | A: {pdata['accountable']} | C: {pdata['consulted']} | I: {pdata['informed']}
            </div>
            <div style="font-size: 0.78rem; color: #555;">Weight: {pdata['weight']}% of corporate strategy</div>
        </div>""", unsafe_allow_html=True)
        
        pn2 = "3. Asset Reliability & Digitalization"
        pdata2 = pillars[pn2]
        color2 = "#38a169"
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid {color2}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; font-size: 1.1rem;">🔧 {pn2}</h3>
                <span style="background: {color2}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: 600;">{pdata2['status']} {pdata2['trend']}</span>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #666;"><span>Progress</span><span>{pdata2['progress']}%</span></div>
                <div style="background: #e0e0e0; height: 8px; border-radius: 4px; margin-top: 0.3rem;"><div style="background: {color2}; width: {pdata2['progress']}%; height: 8px; border-radius: 4px;"></div></div>
            </div>
            <p style="font-size: 0.8rem; color: #CC0000; font-weight: 600;">🎯 {pdata2['highlight']}</p>
            <div style="font-size: 0.8rem; margin: 0.5rem 0;">
                <strong>RACI:</strong> R: {pdata2['responsible']} | A: {pdata2['accountable']} | C: {pdata2['consulted']} | I: {pdata2['informed']}
            </div>
            <div style="font-size: 0.78rem; color: #555;">Weight: {pdata2['weight']}% of corporate strategy</div>
        </div>""", unsafe_allow_html=True)
    
    with p2:
        pn3 = "2. Process Simplification"
        pdata3 = pillars[pn3]
        color3 = "#d69e2e"
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid {color3}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; font-size: 1.1rem;">🤖 {pn3}</h3>
                <span style="background: {color3}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: 600;">{pdata3['status']} {pdata3['trend']}</span>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #666;"><span>Progress</span><span>{pdata3['progress']}%</span></div>
                <div style="background: #e0e0e0; height: 8px; border-radius: 4px; margin-top: 0.3rem;"><div style="background: {color3}; width: {pdata3['progress']}%; height: 8px; border-radius: 4px;"></div></div>
            </div>
            <p style="font-size: 0.8rem; color: #CC0000; font-weight: 600;">🎯 {pdata3['highlight']}</p>
            <div style="font-size: 0.8rem; margin: 0.5rem 0;">
                <strong>RACI:</strong> R: {pdata3['responsible']} | A: {pdata3['accountable']} | C: {pdata3['consulted']} | I: {pdata3['informed']}
            </div>
            <div style="font-size: 0.78rem; color: #555;">Weight: {pdata3['weight']}% of corporate strategy</div>
        </div>""", unsafe_allow_html=True)
        
        pn4 = "4. People & Culture"
        pdata4 = pillars[pn4]
        color4 = "#38a169"
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid {color4}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; font-size: 1.1rem;">👥 {pn4}</h3>
                <span style="background: {color4}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: 600;">{pdata4['status']} {pdata4['trend']}</span>
            </div>
            <div style="margin: 0.8rem 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #666;"><span>Progress</span><span>{pdata4['progress']}%</span></div>
                <div style="background: #e0e0e0; height: 8px; border-radius: 4px; margin-top: 0.3rem;"><div style="background: {color4}; width: {pdata4['progress']}%; height: 8px; border-radius: 4px;"></div></div>
            </div>
            <p style="font-size: 0.8rem; color: #CC0000; font-weight: 600;">🎯 {pdata4['highlight']}</p>
            <div style="font-size: 0.8rem; margin: 0.5rem 0;">
                <strong>RACI:</strong> R: {pdata4['responsible']} | A: {pdata4['accountable']} | C: {pdata4['consulted']} | I: {pdata4['informed']}
            </div>
            <div style="font-size: 0.78rem; color: #555;">Weight: {pdata4['weight']}% of corporate strategy</div>
        </div>""", unsafe_allow_html=True)
    
    # PORTFOLIO PERFORMANCE
    st.markdown("---")
    st.subheader("🏢 Portfolio Performance — Churchgate Group Properties")
    portfolio_data = pd.DataFrame({
        'Property': CHURCHGATE_PORTFOLIO,
        'Occupancy %': [87, 92, 85, 78, 95, 90],
        'Revenue %': [94, 98, 88, 82, 97, 91],
        'Satisfaction': [4.3, 4.5, 4.1, 3.9, 4.4, 4.2]
    })
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Occupancy %', x=portfolio_data['Property'], y=portfolio_data['Occupancy %'], marker_color='#CC0000', text=portfolio_data['Occupancy %'], textposition='outside'))
    fig.add_trace(go.Bar(name='Revenue %', x=portfolio_data['Property'], y=portfolio_data['Revenue %'], marker_color='#4a4a4a', text=portfolio_data['Revenue %'], textposition='outside'))
    fig.update_layout(height=400, barmode='group', margin=dict(t=20), legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig, use_container_width=True)
    
    # DEPARTMENT SCORECARD
    st.markdown("---")
    st.subheader("📊 Department Performance Scorecard — Strategic Pillar Alignment")
    scorecard = pd.DataFrame({
        'Department': ['Technology', 'Facility Mgmt', 'Finance', 'HR', 'Sales & Mkt', 'Procurement', 'Security', 'Legal', 'Operations'],
        'Occupancy & Revenue': [85, 80, 90, 75, 88, 82, 78, 70, 85],
        'Process Simplification': [72, 68, 75, 70, 65, 60, 55, 50, 68],
        'Asset Reliability': [90, 88, 82, 85, 80, 78, 85, 75, 82],
        'People & Culture': [88, 85, 80, 92, 82, 78, 80, 75, 85]
    })
    fig2 = go.Figure(data=[go.Heatmap(
        z=scorecard[['Occupancy & Revenue', 'Process Simplification', 'Asset Reliability', 'People & Culture']].values,
        x=['Occupancy & Revenue', 'Process Simplification', 'Asset Reliability', 'People & Culture'],
        y=scorecard['Department'],
        colorscale=[[0, '#e53e3e'], [0.5, '#d69e2e'], [1, '#38a169']],
        zmin=0, zmax=100,
        text=scorecard[['Occupancy & Revenue', 'Process Simplification', 'Asset Reliability', 'People & Culture']].values,
        texttemplate='%{text}%',
        textfont=dict(size=11)
    )])
    fig2.update_layout(height=400, margin=dict(t=20))
    st.plotly_chart(fig2, use_container_width=True)
    
    # RACI SUMMARY TABLE
    st.markdown("---")
    st.subheader("📋 Group Strategy RACI Matrix — 2026-2027")
    raci_data = pd.DataFrame({
        'Strategic Initiative': [
            'Occupancy & Revenue Growth',
            'Process Simplification (AI/BMS)',
            'Asset Reliability & Digitalization',
            'People & Culture'
        ],
        'Responsible': ['COO', 'ELV/Hive Mechanics', 'FM Heads', 'HR Director'],
        'Accountable': ['GMD', 'GMD', 'COO', 'GMD'],
        'Consulted': ['All HODs', 'All HODs', 'VP-Sales/GM-Procurement', 'GEA/COO/HR'],
        'Informed': ['Board', 'Board', 'Board', 'Board'],
        'Timeline': ['0-12 months', '0-8 months', '6-12 months', '0-8 months'],
        'Status': ['On Track', 'In Progress', 'Exceeding', 'On Track']
    })
    st.dataframe(raci_data, use_container_width=True, hide_index=True)

def employee_management():
    st.markdown("""<div class="churchgate-header"><h1>👥 Employee Management</h1><p>Comprehensive workforce management | Churchgate Group</p></div>""", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Directory", "➕ Add Employee", "📤 Bulk Upload", "🔑 Generate Logins", "🏢 Departments", "📊 Org Chart"])
    with tab1:
        st.subheader("Employee Directory")
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.text_input("🔍 Search", placeholder="Name, ID, department...")
        with c2:
            st.selectbox("Department", ["All", "Senior Management", "Technology Group", "Facility Management", "Human Resources", "Sales & Marketing", "Accounts & Finance", "Procurement", "Security", "Legal", "Operations"])
        with c3:
            st.selectbox("Status", ["All", "Active", "On Leave", "Probation"])
        employees = [
            {"name": "Vinay Mahtani", "id": "GMD01", "dept": "Senior Management", "position": "GMD", "status": "Active"},
            {"name": "Jerome Das", "id": "LE00019", "dept": "Senior Management", "position": "COO", "status": "Active"},
            {"name": "Emmanuel Etuk", "id": "AN00387", "dept": "Technology Group", "position": "Head, ELV Systems", "status": "Active"},
            {"name": "Sanjeev Purwar", "id": "LE00212", "dept": "Facility Management", "position": "Head, MEP", "status": "Active"},
            {"name": "Ahmed Karim", "id": "LN00369", "dept": "Sales & Marketing", "position": "GM, Sales & Marketing", "status": "Active"},
            {"name": "Ibukun Adeogun", "id": "AN00012", "dept": "Operations", "position": "GM, Operations/Admin", "status": "Active"},
            {"name": "Jeff Arikawe", "id": "LN00008", "dept": "Accounts & Finance", "position": "Chief Accountant", "status": "Active"},
            {"name": "Adebayo Sakote", "id": "LN00037", "dept": "Human Resources", "position": "HR Manager", "status": "Active"},
            {"name": "Anand Bora", "id": "LE00071", "dept": "Procurement", "position": "GM, Procurement", "status": "Active"},
            {"name": "Maikudi Kadoh", "id": "AN00391", "dept": "Security", "position": "Chief Security Officer", "status": "Active"},
            {"name": "David Aiyedun", "id": "AN00455", "dept": "Legal", "position": "Legal Officer", "status": "Active"},
            {"name": "Charles Okere", "id": "AN00400", "dept": "Facility Management", "position": "Lift Supervisor", "status": "Active"},
            {"name": "George Ojile", "id": "AN00398", "dept": "Facility Management", "position": "Lift Engineer", "status": "Active"},
            {"name": "Augustine Oleh", "id": "AN00425", "dept": "Facility Management", "position": "HSE Coordinator", "status": "Active"},
            {"name": "Francis Asuquo", "id": "AN00433", "dept": "Technology Group", "position": "ELV Engineer", "status": "Active"},
            {"name": "Chika Ikwuegbu", "id": "LN00438", "dept": "Security", "position": "Admin Assistant", "status": "Active"},
            {"name": "Alice Agbo", "id": "AN00423", "dept": "Procurement", "position": "Store Keeper", "status": "Active"},
            {"name": "Rhoda Ajibola", "id": "AN00460", "dept": "Facility Management", "position": "Front Desk Executive", "status": "Active"},
            {"name": "Ogechukwu Obute", "id": "AN00451", "dept": "Sales & Marketing", "position": "Sales Executive", "status": "Active"},
            {"name": "David Effiong", "id": "AN00496", "dept": "Facility Management", "position": "Facility Manager", "status": "Active"},
        ]
        for emp in employees:
            initials = generate_initials(emp['name'])
            st.markdown(f"""<div style="background: white; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 1rem; border: 1px solid #e0e0e0;"><div style="width: 40px; height: 40px; border-radius: 50%; background: #CC0000; display: flex; align-items: center; justify-content: center; font-weight: 700; color: white; min-width: 40px;">{initials}</div><div style="flex: 1;"><strong>{emp['name']}</strong><br><small>{emp['position']} • {emp['dept']}</small></div><div style="text-align: right;"><small>ID: {emp['id']}</small><br><span style="background: #38a169; color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem;">{emp['status']}</span></div></div>""", unsafe_allow_html=True)
    with tab2:
        st.subheader("Add New Employee")
        with st.form("add_employee_form"):
            st.markdown("### Basic Information")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input("First Name *")
                st.text_input("Last Name *")
                st.text_input("Middle Name")
                st.text_input("Staff ID *")
            with c2:
                st.text_input("Phone Number", placeholder="+234 800 000 0000")
                st.text_input("Email")
                st.selectbox("Gender", ["", "Male", "Female"])
                st.selectbox("Contract Type", ["Full-time", "Contract", "Part-time", "Intern"])
            with c3:
                st.date_input("Date of Birth")
                st.selectbox("Marital Status", ["", "Single", "Married", "Divorced", "Widowed"])
            st.markdown("### Job Information")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.selectbox("Department *", ["", "Senior Management", "Technology Group", "Facility Management", "Human Resources", "Sales & Marketing", "Accounts & Finance", "Procurement", "Security", "Legal", "Operations"])
                st.text_input("Job Role *")
            with c2:
                st.selectbox("Location", ["", "World Trade Center Abuja", "Churchgate Tower 1 Lagos", "Churchgate Tower 2 Lagos", "Churchgate Plaza Abuja"])
                st.text_input("Cost Center")
            with c3:
                st.text_input("Line Manager")
                st.date_input("Date of Employment")
            st.markdown("### Family Details")
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Next of Kin Name")
                st.text_input("Relationship")
            with c2:
                st.text_input("Next of Kin Phone")
                st.text_area("Next of Kin Address", height=80)
            st.markdown("### Bank Details")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input("Bank Name")
            with c2:
                st.text_input("Account Name")
            with c3:
                st.text_input("Account Number")
            st.markdown("### Profile Picture & Documents")
            c1, c2 = st.columns(2)
            with c1:
                st.file_uploader("Upload Profile Picture", type=['jpg', 'jpeg', 'png'])
            with c2:
                st.file_uploader("Upload CV", type=['pdf', 'docx'])
            st.file_uploader("Upload Certifications", type=['pdf', 'docx', 'jpg', 'png'])
            if st.form_submit_button("✅ Add Employee", use_container_width=True):
                st.success("✅ Employee added successfully!")
                st.balloons()
    with tab3:
        st.subheader("Bulk Employee Upload")
        st.info("Upload CSV file with employee data")
        template_df = pd.DataFrame(columns=['first_name', 'last_name', 'email', 'staff_id', 'department', 'position', 'phone'])
        csv = template_df.to_csv(index=False)
        st.download_button("📥 Download Template", csv, "employee_template.csv", "text/csv")
        uf = st.file_uploader("Upload CSV", type=['csv'])
        if uf:
            df = pd.read_csv(uf)
            st.write(f"**{len(df)} employees found**")
            st.dataframe(df.head(), use_container_width=True)
            if st.button("📤 Upload All", use_container_width=True):
                st.success(f"✅ {len(df)} employees uploaded!")
                st.balloons()
    with tab4:
        st.subheader("🔑 Manage Employee Access & Generate Logins")
        
        # ADMIN ROLE MANAGEMENT
        st.markdown("### 👑 Update User Roles (Admin Only)")
        users_list = [
            {"name": "Vinay Mahtani", "id": "GMD01", "email": "vbmahtani@churchgate.com", "dept": "Senior Management", "current_role": "Admin"},
            {"name": "Jerome Das", "id": "LE00019", "email": "jeromedas@churchgate.com", "dept": "Senior Management", "current_role": "Admin"},
            {"name": "Emmanuel Etuk", "id": "AN00387", "email": "eetuk@churchgate.com", "dept": "Technology Group", "current_role": "Manager"},
            {"name": "Lawal Mohammed", "id": "NEW001", "email": "lawal@churchgate.com", "dept": "Senior Management", "current_role": "Admin"},
            {"name": "Paul Fade", "id": "NEW002", "email": "pfade@churchgate.com", "dept": "Senior Management", "current_role": "Admin"},
        ]
        
        for u in users_list:
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.markdown(f"**{u['name']}** - {u['email']}")
            with c2:
                new_role = st.selectbox(f"Role for {u['name']}", ["Admin", "HR Director", "Manager", "Employee"], 
                                        index=["Admin", "HR Director", "Manager", "Employee"].index(u['current_role']),
                                        key=f"role_{u['id']}")
            with c3:
                st.markdown(f"<br><small>Dept: {u['dept']}</small>", unsafe_allow_html=True)
        
        if st.button("💾 Update All Roles", use_container_width=True):
            st.success("✅ Roles updated successfully! Changes will apply on next login.")
            st.info("Note: Role updates require database write access. In production, this will update the users table.")
        
        st.markdown("---")
        st.markdown("### ⚡ Create Single Employee Account (with Email)")
        c1, c2, c3 = st.columns(3)
        with c1:st.markdown("---")
        st.markdown("### 🔄 Reset Existing User Password")
        rc1, rc2 = st.columns([2, 1])
        with rc1:
            reset_email = st.text_input("User Email to Reset", placeholder="eetuk@churchgate.com", key="reset_email")
        with rc2:
            reset_password = st.text_input("New Password", value="churchgate2026", key="reset_pw")
        if st.button("🔄 Reset Password", use_container_width=True):
            if reset_email:
                hashed_pw = hashlib.sha256(reset_password.encode()).hexdigest()
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_pw, reset_email))
                conn.commit()
                conn.close()
                st.success(f"✅ Password reset for {reset_email}!")
                st.info(f"New password: **{reset_password}**")
            else:
                st.warning("Please enter an email address.")
        
        st.markdown("---")
        st.markdown("### ⚡ Create Single Employee Account (with Email)")
        c1, c2, c3 = st.columns(3)
        with c1:
            single_email = st.text_input("Employee Email", placeholder="eetuk@churchgate.com", key="single_email")
            single_email = st.text_input("Employee Email", placeholder="eetuk@churchgate.com", key="single_email2")
            single_name = st.text_input("Full Name", placeholder="Emmanuel Etuk", key="single_name2")
        with c2:
            single_password = st.text_input("Password", value="churchgate2026", key="single_pw2")
            single_role = st.selectbox("Role", ["Admin", "HR Director", "Manager", "Employee"], index=0, key="single_role")
        with c3:
            single_dept = st.selectbox("Department", ["Senior Management", "Technology Group", "Facility Management", "Human Resources", "Sales & Marketing", "Accounts & Finance", "Procurement", "Security", "Legal", "Operations"], key="single_dept")
            single_id = st.text_input("Staff ID", placeholder="AN00387", key="single_id")
        
        if st.button("🔑 Create Account & Send Welcome Email", use_container_width=True):
            if single_email and single_name:
                hashed_pw = hashlib.sha256(single_password.encode()).hexdigest()
                try:
                    db.create_user(single_id, single_name, single_email, single_password, single_role, single_dept, single_dept)
                    st.success(f"✅ Account created for {single_name}!")
                    # Send welcome email
                    success, msg = email_service.send_welcome_email(single_name, single_email, single_password, single_role)
                    if success:
                        st.success(f"📧 Welcome email sent to {single_email}!")
                        st.balloons()
                    else:
                        st.warning(f"⚠️ Account created but email failed: {msg}")
                except Exception as e:
                    st.warning(f"⚠️ Account may already exist or error: {str(e)}")
            else:
                st.warning("Please enter at least email and name.")
        
        st.markdown("---")
        st.markdown("### 🔑 Generate All Employee Login Credentials (Bulk)")
        st.info("Generate login access for all active employees. Default password will be 'churchgate2026' and employees will be prompted to change on first login.")
        emp_list = [
            {"name": "Vinay Mahtani", "id": "GMD01", "email": "vbmahtani@churchgate.com", "dept": "Senior Management", "role": "Admin"},
            {"name": "Jerome Das", "id": "LE00019", "email": "jeromedas@churchgate.com", "dept": "Senior Management", "role": "Admin"},
            {"name": "Emmanuel Etuk", "id": "AN00387", "email": "eetuk@churchgate.com", "dept": "Technology Group", "role": "Admin"},
            {"name": "Lawal Mohammed", "id": "NEW001", "email": "lawal@churchgate.com", "dept": "Senior Management", "role": "Admin"},
            {"name": "Paul Fade", "id": "NEW002", "email": "pfade@churchgate.com", "dept": "Senior Management", "role": "Admin"},
            {"name": "Sanjeev Purwar", "id": "LE00212", "email": "purwar@churchgate.com", "dept": "Facility Management", "role": "Manager"},
            {"name": "Ahmed Karim", "id": "LN00369", "email": "akarim@churchgate.com", "dept": "Sales & Marketing", "role": "Manager"},
            {"name": "Ibukun Adeogun", "id": "AN00012", "email": "adeogun@churchgate.com", "dept": "Operations", "role": "Manager"},
            {"name": "Jeff Arikawe", "id": "LN00008", "email": "jeff@churchgate.com", "dept": "Accounts & Finance", "role": "Manager"},
            {"name": "Adebayo Sakote", "id": "LN00037", "email": "asakote@churchgate.com", "dept": "Human Resources", "role": "HR Director"},
            {"name": "Anand Bora", "id": "LE00071", "email": "abora@churchgate.com", "dept": "Procurement", "role": "Manager"},
            {"name": "Maikudi Kadoh", "id": "AN00391", "email": "mkadoh@churchgate.com", "dept": "Security", "role": "Manager"},
            {"name": "David Aiyedun", "id": "AN00455", "email": "daiyedun@churchgate.com", "dept": "Legal", "role": "Employee"},
            {"name": "Charles Okere", "id": "AN00400", "email": "cokere@churchgate.com", "dept": "Facility Management", "role": "Employee"},
            {"name": "George Ojile", "id": "AN00398", "email": "gojile@churchgate.com", "dept": "Facility Management", "role": "Employee"},
            {"name": "Augustine Oleh", "id": "AN00425", "email": "aoleh@churchgate.com", "dept": "Facility Management", "role": "Employee"},
            {"name": "Francis Asuquo", "id": "AN00433", "email": "fasuquo@churchgate.com", "dept": "Technology Group", "role": "Employee"},
            {"name": "Chika Ikwuegbu", "id": "LN00438", "email": "cikwuegbu@churchgate.com", "dept": "Security", "role": "Employee"},
            {"name": "Alice Agbo", "id": "AN00423", "email": "aagbo@churchgate.com", "dept": "Procurement", "role": "Employee"},
            {"name": "Rhoda Ajibola", "id": "AN00460", "email": "rajibola@churchgate.com", "dept": "Facility Management", "role": "Employee"},
            {"name": "Ogechukwu Obute", "id": "AN00451", "email": "jobute@churchgate.com", "dept": "Sales & Marketing", "role": "Employee"},
            {"name": "David Effiong", "id": "AN00496", "email": "deffiong@churchgate.com", "dept": "Facility Management", "role": "Employee"},
        ]
        st.dataframe(pd.DataFrame(emp_list), use_container_width=True, hide_index=True)
        default_password = st.text_input("Default Password", value="churchgate2026")
        if st.button("🔑 Generate Logins for All Employees", use_container_width=True):
            created_count = 0
            for emp in emp_list:
                hashed_pw = hashlib.sha256(default_password.encode()).hexdigest()
                try:
                    existing = db.verify_user(emp['email'], hashed_pw)
                    if not existing:
                        db.create_user(emp['id'], emp['name'], emp['email'], default_password, emp['role'], emp['dept'], emp['dept'])
                        created_count += 1
                except:
                    pass
            if created_count > 0:
                st.success(f"✅ {created_count} new employee logins created successfully!")
                st.balloons()
                email_sent_count = 0
                for emp in emp_list:
                    subject = f"🎉 Welcome to Churchgate Group, {emp['name']}!"
                    body = f"Dear {emp['name']}, your HRIS account is ready! Login at https://churchgate-hris.streamlit.app with email: {emp['email']} and password: {default_password}"
                    success, msg = email_service.send_email(emp['email'], subject, body)
                    if success:
                        email_sent_count += 1
                if email_sent_count > 0:
                    st.success(f"📧 {email_sent_count} welcome emails sent!")
                else:
                    st.info("📧 Email simulation mode. In production, welcome emails will be sent.")
            else:
                st.info("All employees already have accounts.")
            st.info(f"Default password: **{default_password}**")
            st.download_button("📥 Download Login List (CSV)", pd.DataFrame(emp_list).to_csv(index=False), "employee_logins.csv", "text/csv")
    with tab5:
        st.subheader("Churchgate Group Departments")
        for dept in [{"name": "Senior Management", "head": "Vinay Mahtani (GMD)", "staff": 5}, {"name": "Technology Group", "head": "Emmanuel Etuk", "staff": 12}, {"name": "Facility Management", "head": "Sanjeev Purwar", "staff": 25}, {"name": "Human Resources", "head": "Adebayo Sakote", "staff": 8}, {"name": "Sales & Marketing", "head": "Ahmed Karim", "staff": 15}, {"name": "Accounts & Finance", "head": "Jeff Arikawe", "staff": 10}, {"name": "Procurement", "head": "Anand Bora", "staff": 8}, {"name": "Security", "head": "Maikudi Kadoh", "staff": 20}, {"name": "Legal", "head": "David Aiyedun", "staff": 3}, {"name": "Operations", "head": "Ibukun Adeogun", "staff": 18}]:
            st.markdown(f"""<div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #CC0000; display: flex; justify-content: space-between;"><div><strong>{dept['name']}</strong><br><small>Head: {dept['head']}</small></div><div style="text-align: right;"><span style="font-size: 1.5rem; font-weight: 700;">{dept['staff']}</span><br><small>staff</small></div></div>""", unsafe_allow_html=True)
    with tab6:
        st.subheader("Organizational Structure")
        fig = go.Figure(data=[go.Sankey(node=dict(pad=20, thickness=20, line=dict(color="black", width=0.5), label=["GMD", "COO", "Technology", "Facility Mgmt", "HR", "Sales", "Finance", "Procurement", "Security", "Legal", "Operations"], color=["#CC0000"] + ["#4a4a4a"]*10), link=dict(source=[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1], target=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2], value=[20, 12, 25, 8, 15, 10, 8, 20, 3, 18, 5]))])
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

def performance_okrs():
    st.markdown("""<div class="churchgate-header"><h1>📈 Performance & Strategic OKRs</h1><p>Corporate Strategy 2026-2027 | Set & Track Your KPIs</p></div>""", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🎯 Strategic Pillars", "✏️ Set My KPIs", "📊 My Performance"])
    with tab1:
        st.subheader("🎯 Corporate Strategic Pillars 2026-2027")
        pillars = {
            "1. Occupancy & Revenue Growth": {"weight": 40, "progress": 85, "objectives": ["Increase data centre revenue by 15% from end 2025/26", "100% of revenues realised as per approved budget", "Nil O/S of debts within 30 days of invoicing", "100% quarterly reconciliation of all customers", "Retention of existing 90% customers", "0% variance from budgeted costs for all cost centres"], "responsible": "COO", "accountable": "GMD"},
            "2. Process Simplification": {"weight": 20, "progress": 72, "objectives": ["Implementation of AI task plan by end of FY 2026", "AI strategy implementation plan by 31st May 2026", "Full BMS installation by 30.06.26", "Achieve 99% Preventive Maintenance (PPM) compliance", "99% uptime in all ELV critical assets", "Complete CRM implementation"], "responsible": "ELV/Hive Mechanics", "accountable": "GMD"},
            "3. Asset Reliability & Digitalization": {"weight": 25, "progress": 90, "objectives": ["100% ELV critical assets assessed and risk-rated biannually", "0% variance in adherence to risk mitigation timeline", "80% of identified risks mitigated within stipulated timeframe", "90% tenant ELV complaints addressed within 24 hours", "Achieve 90% SMARTCHECK utilisation compliance by 30.09.26", "100% operational ELV assets during emergencies"], "responsible": "FM Heads", "accountable": "COO"},
            "4. People & Culture": {"weight": 15, "progress": 88, "objectives": ["100% staff have JDs within 30th April 2026", "100% staff appraised by line managers twice a year", "Complete identification of A-players (2 min) by 30 April 2026", "Detailed competency gap assessment by 31 May 2026", "Each employee completes at least 2 LMS courses per half-year", "60-80% improvement in behavioural skills in 8 months"], "responsible": "HR Director", "accountable": "GMD"}
        }
        for pn, pd in pillars.items():
            color = "#38a169" if pd['progress'] >= 85 else "#d69e2e" if pd['progress'] >= 70 else "#CC0000"
            with st.expander(f"{pn} | Weight: {pd['weight']}% | Progress: {pd['progress']}%", expanded=True):
                st.progress(pd['progress'] / 100)
                for obj in pd['objectives']:
                    st.markdown(f"✅ {obj}")
                st.markdown(f"**RACI:** R: {pd['responsible']} | A: {pd['accountable']} | C: All HODs | I: Board")
    with tab2:
        st.subheader("✏️ Set My KPIs & Objectives")
        with st.form("set_kpi_form"):
            c1, c2 = st.columns(2)
            with c1:
                st.selectbox("Strategic Pillar", ["Occupancy & Revenue Growth", "Process Simplification", "Asset Reliability & Digitalization", "People & Culture"])
                st.text_input("KPI Title *", placeholder="e.g., Increase data centre revenue")
                st.text_area("Description", placeholder="Describe what this KPI measures...")
                st.slider("Weight (%)", 0, 100, 25)
            with c2:
                st.number_input("Target Value", min_value=0, value=100)
                st.number_input("Current Value", min_value=0, value=0)
                st.date_input("Start Date")
                st.date_input("End Date")
                st.selectbox("Unit", ["Percentage (%)", "Number (#)", "Currency (₦)", "Days", "Score (/5)"])
            st.markdown("### Key Results")
            st.text_area("Key Results (one per line)", height=100, placeholder="e.g.,\nRevenue increased by 15%\n5 new customers acquired")
            sc1, sc2 = st.columns(2)
            with sc1:
                if st.form_submit_button("💾 Save KPI", use_container_width=True):
                    st.success("✅ KPI saved successfully!")
                    st.balloons()
            with sc2:
                if st.form_submit_button("📋 Save & Add Another", use_container_width=True):
                    st.success("✅ KPI saved! Add another below.")
    with tab3:
        st.subheader("📊 My Performance Scorecard")
        my_kpis = [
            {"title": "Increase data centre revenue", "pillar": "Occupancy & Revenue", "target": "15%", "current": "12%", "progress": 80, "status": "On Track"},
            {"title": "100% revenue realisation", "pillar": "Occupancy & Revenue", "target": "100%", "current": "95%", "progress": 95, "status": "Near Target"},
            {"title": "Nil O/S debts within 30 days", "pillar": "Occupancy & Revenue", "target": "0", "current": "2", "progress": 60, "status": "At Risk"},
            {"title": "BMS Installation complete", "pillar": "Process Simplification", "target": "100%", "current": "75%", "progress": 75, "status": "On Track"},
            {"title": "Preventive Maintenance compliance", "pillar": "Asset Reliability", "target": "99%", "current": "95%", "progress": 96, "status": "On Track"},
        ]
        for kpi in my_kpis:
            if kpi['progress'] >= 85:
                color, badge = "#38a169", "status-active"
            elif kpi['progress'] >= 65:
                color, badge = "#d69e2e", "status-pending"
            else:
                color, badge = "#CC0000", "status-at-risk"
            st.markdown(f"""<div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.6rem; border-left: 4px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"><div style="display: flex; justify-content: space-between; align-items: center;"><div><strong>{kpi['title']}</strong><br><small style="color: #666;">{kpi['pillar']} | Target: {kpi['target']} | Current: {kpi['current']}</small></div><div style="text-align: right;"><span class="{badge}">{kpi['status']}</span><br><small>{kpi['progress']}%</small></div></div><div style="background: #e0e0e0; height: 6px; border-radius: 3px; margin-top: 0.5rem;"><div style="background: {color}; width: {kpi['progress']}%; height: 6px; border-radius: 3px;"></div></div></div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Overall Score", "81.2%", "↑ 3.5%")
        c2.metric("KPIs On Track", "3/5", "60%")
        c3.metric("KPIs At Risk", "1/5", "Needs attention")

def promotions():
    st.markdown("""<div class="churchgate-header"><h1>🚀 Promotions & Career Progression</h1><p>AI-Driven Succession Planning | Talent Management</p></div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown("""<div class="metric-card"><h3 style="color: #38a169;">⭐ A-Players</h3><div class="metric-value">4</div><small>Ready for promotion</small></div>""", unsafe_allow_html=True)
    c2.markdown("""<div class="metric-card"><h3 style="color: #CC0000;">📋 Pipeline</h3><div class="metric-value">85%</div><small>Key positions covered</small></div>""", unsafe_allow_html=True)
    c3.markdown("""<div class="metric-card"><h3 style="color: #3182ce;">📈 Avg Time</h3><div class="metric-value">2.3</div><small>Years to promotion</small></div>""", unsafe_allow_html=True)
    st.subheader("🎯 Promotion Candidates - AI Assessment")
    st.info("💡 **How A-Players are determined:** Candidates are evaluated based on Performance Score (40%), Leadership Competency (25%), Strategic Impact (20%), and Readiness Assessment (15%). Scores above 85% qualify as A-Players ready for immediate promotion.")
    for c in [{"name": "Emmanuel Etuk", "current": "Head, ELV Systems", "proposed": "Director, Technology", "score": 93, "perf": 95, "leadership": 92, "strategic": 90, "readiness": "Ready Now", "gap": "None", "risk": "Low"}, {"name": "Sanjeev Purwar", "current": "Head, MEP", "proposed": "Director, Facilities", "score": 88, "perf": 90, "leadership": 85, "strategic": 88, "readiness": "Ready Now", "gap": "Leadership training", "risk": "Medium"}, {"name": "Adebayo Sakote", "current": "HR Manager", "proposed": "Senior HR Manager", "score": 85, "perf": 87, "leadership": 83, "strategic": 84, "readiness": "Q3 2026", "gap": "Strategic HR certification", "risk": "Low"}, {"name": "Olalekan Bolarinwa", "current": "Deputy Accounts Manager", "proposed": "Accounts Manager", "score": 82, "perf": 84, "leadership": 80, "strategic": 81, "readiness": "Q4 2026", "gap": "ICAN certification", "risk": "Medium"}]:
        color = "#38a169" if c['readiness'] == 'Ready Now' else "#d69e2e"
        st.markdown(f"""<div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.6rem; border-left: 4px solid {color};"><div style="display: flex; justify-content: space-between;"><div><strong>{c['name']}</strong><br><small>{c['current']} → <strong>{c['proposed']}</strong></small><br><small style="color: #666;">Perf: {c['perf']}% | Leadership: {c['leadership']}% | Strategic: {c['strategic']}%</small></div><div style="text-align: right;"><span style="background: {color}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-weight: 600;">{c['readiness']}</span><br><small>Score: {c['score']}% | Gap: {c['gap']} | Risk: {c['risk']}</small></div></div></div>""", unsafe_allow_html=True)

def recruitment_hub():
    st.markdown("""<div class="churchgate-header"><h1>💼 Recruitment Hub</h1><p>Manage Jobs, Applications, and Recruitment Workflows</p></div>""", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Active Jobs", "➕ Post New Job", "👥 Applications", "📊 Pipeline"])
    with tab1:
        st.subheader("Active Job Postings")
        for job in [{"title": "AI Transformation Lead", "dept": "Technology Group", "location": "Abuja", "type": "Full-time", "closing": "2026-06-30", "ref": "JOB-2026-001"}, {"title": "Senior Facility Manager", "dept": "Facility Management", "location": "Lagos", "type": "Full-time", "closing": "2026-07-15", "ref": "JOB-2026-002"}, {"title": "Network Engineer", "dept": "Technology Group", "location": "Abuja", "type": "Full-time", "closing": "2026-06-20", "ref": "JOB-2026-003"}, {"title": "Procurement Officer", "dept": "Procurement", "location": "Abuja", "type": "Full-time", "closing": "2026-07-01", "ref": "JOB-2026-004"}, {"title": "HVAC Technician", "dept": "Facility Management", "location": "Abuja", "type": "Contract", "closing": "2026-06-25", "ref": "JOB-2026-005"}]:
            st.markdown(f"""<div style="background: white; padding: 1.2rem; border-radius: 8px; margin-bottom: 0.8rem; border-left: 4px solid #CC0000;"><div style="display: flex; justify-content: space-between; align-items: center;"><div><h4 style="margin: 0;">{job['title']}</h4><p style="margin: 0.3rem 0; color: #666;">🏢 {job['dept']} | 📍 {job['location']} | 💼 {job['type']}</p><small>Ref: {job['ref']} | Closes: {job['closing']}</small></div><span style="background: #38a169; color: white; padding: 0.3rem 1rem; border-radius: 15px;">Active</span></div></div>""", unsafe_allow_html=True)
    with tab2:
        st.subheader("Post New Job Opening")
        with st.form("post_job"):
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Job Title *")
                st.selectbox("Department *", ["Technology Group", "Facility Management", "Human Resources", "Sales & Marketing", "Accounts & Finance", "Procurement", "Security", "Legal", "Operations", "Senior Management"])
                st.selectbox("Location", ["World Trade Center Abuja", "Churchgate Tower 1 Lagos", "Churchgate Tower 2 Lagos", "Churchgate Plaza Abuja"])
                st.selectbox("Employment Type", ["Full-time", "Contract", "Part-time", "Intern"])
            with c2:
                st.text_input("Salary Range", "₦5,000,000 - ₦8,000,000")
                st.selectbox("Experience Level", ["Entry Level", "Junior", "Mid-Level", "Senior", "Executive"])
                st.number_input("Number of Positions", min_value=1, value=1)
                st.date_input("Closing Date")
            st.text_area("Job Description *", height=200, placeholder="Paste full job description...")
            st.text_input("Key Skills (comma-separated)")
            if st.form_submit_button("📝 Post Job", use_container_width=True):
                st.success("✅ Job posted successfully!")
                st.balloons()
    with tab3:
        st.subheader("Applications Received")
        for app in [{"name": "Modupe O.", "position": "AI Transformation Lead", "date": "2026-05-14", "status": "Screened", "score": "92%"}, {"name": "Chinelo A.", "position": "AI Transformation Lead", "date": "2026-05-13", "status": "New", "score": "88%"}, {"name": "Ogochukwu N.", "position": "Senior Facility Manager", "date": "2026-05-12", "status": "Interviewed", "score": "78%"}]:
            sc = "#38a169" if app['status'] == 'Screened' else "#d69e2e" if app['status'] == 'Interviewed' else "#3182ce"
            st.markdown(f"""<div style="background: white; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.4rem; display: flex; justify-content: space-between; align-items: center;"><div><strong>{app['name']}</strong> - {app['position']}<br><small>{app['date']} | AI: {app['score']}</small></div><span style="background: {sc}; color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem;">{app['status']}</span></div>""", unsafe_allow_html=True)
    with tab4:
        st.subheader("Recruitment Pipeline")
        pipeline = pd.DataFrame({'Stage': ['Sourced', 'Applied', 'Screened', 'Interviewed', 'Offered', 'Hired'], 'Candidates': [50, 35, 20, 8, 3, 1]})
        fig = px.funnel(pipeline, x='Candidates', y='Stage', color_discrete_sequence=['#CC0000'])
        st.plotly_chart(fig, use_container_width=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Time to Hire", "18 days", "↓ 30%")
        c2.metric("Cost per Hire", "₦350K", "↓ 25%")
        c3.metric("Acceptance", "88%", "↑ 12%")

def ai_recruitment_agent():
    st.markdown("""<div class="churchgate-header"><h1>🤖 AI Recruitment Agent</h1><p>AI-Powered CV Analysis | Candidate Scoring | LinkedIn Parsing | Intelligent Tiering</p></div>""", unsafe_allow_html=True)
    ai_section = st.radio("Select Function:", ["📋 JD Analysis", "📤 CV Upload & Scoring", "📊 Candidate Tiering", "🔍 LinkedIn Parse", "💾 Save Results"], horizontal=True)
    if ai_section == "📋 JD Analysis":
        st.subheader("AI Job Description Analyzer")
        jd_input = st.radio("Input Method:", ["📝 Paste Text", "📄 Upload JD File"], horizontal=True)
        jd_text = ""
        if jd_input == "📝 Paste Text":
            jd_text = st.text_area("Paste Job Description", height=250, placeholder="Paste the complete job description here...")
        else:
            jd_file = st.file_uploader("Upload JD (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'], key="jd_file")
            if jd_file:
                jd_text = save_uploaded_file(jd_file)
                st.text_area("Extracted Text", jd_text[:500] + "...", height=150, disabled=True)
        if st.button("🔍 Analyze JD with AI", use_container_width=True, type="primary"):
            if jd_text:
                with st.spinner("🤖 AI analyzing job description..."):
                    time.sleep(1.5)
                    analysis = ai_agent.analyze_jd(jd_text)
                    st.session_state.current_jd = analysis
                    st.success("✅ Analysis Complete!")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Title:** {analysis['title']}")
                        st.markdown(f"**Department:** {analysis['department']}")
                        st.markdown(f"**Experience:** {analysis['experience_level']}")
                    with c2:
                        st.markdown("**Required Skills:**")
                        for skill in analysis['required_skills'][:8]:
                            st.markdown(f"- `{skill['skill'].title()}`")
            else:
                st.warning("Please provide a job description first.")
    elif ai_section == "📤 CV Upload & Scoring":
        st.subheader("Bulk CV Upload & AI Scoring")
        if st.session_state.current_jd is None:
            st.warning("⚠️ Please analyze a Job Description first (JD Analysis section)")
        else:
            st.success(f"✅ JD Loaded: {st.session_state.current_jd['title']}")
            uploaded_files = st.file_uploader("Upload CVs (PDF, DOCX, TXT) - Multiple files supported", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)
            if uploaded_files:
                st.markdown(f"**{len(uploaded_files)} CV(s) uploaded**")
                if st.button("🤖 Analyze All CVs", use_container_width=True, type="primary"):
                    candidates_batch = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    for i, file in enumerate(uploaded_files):
                        status_text.text(f"Processing: {file.name} ({i+1}/{len(uploaded_files)})")
                        cv_text = save_uploaded_file(file)
                        if cv_text:
                            score_result = ai_agent.score_candidate_advanced(cv_text, st.session_state.current_jd)
                            candidates_batch.append({'filename': file.name, 'cv_text': cv_text, 'score': score_result})
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    st.session_state.candidates_batch = candidates_batch
                    status_text.text(f"✅ {len(candidates_batch)} candidates analyzed!")
                    tiers = {'Tier 1 (Strong Fit)': 0, 'Tier 2 (Good Fit)': 0, 'Tier 3 (Not Recommended)': 0}
                    for c in candidates_batch:
                        tiers[c['score']['tier']] += 1
                    tc1, tc2, tc3 = st.columns(3)
                    tc1.metric("🌟 Tier 1", tiers['Tier 1 (Strong Fit)'])
                    tc2.metric("👍 Tier 2", tiers['Tier 2 (Good Fit)'])
                    tc3.metric("👎 Tier 3", tiers['Tier 3 (Not Recommended)'])
    elif ai_section == "📊 Candidate Tiering":
        st.subheader("Candidate Tiering Report")
        if not st.session_state.candidates_batch:
            st.info("Upload and analyze CVs first (CV Upload section)")
        else:
            candidates = st.session_state.candidates_batch
            st.markdown("## 📋 EXECUTIVE SUMMARY")
            tiers = {'Tier 1 (Strong Fit)': [], 'Tier 2 (Good Fit)': [], 'Tier 3 (Not Recommended)': []}
            for c in candidates:
                tiers[c['score']['tier']].append(c)
            summary_data = []
            for tn, tc in tiers.items():
                if tc:
                    names = ', '.join([f"{c['score']['candidate_name']} ({c['score']['overall_score']}%)" for c in tc])
                else:
                    names = "None"
                action = "🌟 Recommend for Final Interview" if 'Tier 1' in tn else "👍 Keep in View" if 'Tier 2' in tn else "–"
                summary_data.append({'Tier': tn, 'Count': len(tc), 'Candidates': names, 'Action': action})
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
            if tiers['Tier 1 (Strong Fit)']:
                st.markdown("---")
                st.markdown("## 🌟 TIER 1 – STRONG FIT")
                t1d = []
                for i, c in enumerate(tiers['Tier 1 (Strong Fit)'], 1):
                    s = c['score']
                    t1d.append({'#': i, 'Candidate': s['candidate_name'], 'Score': f"{s['overall_score']}%", 'LinkedIn': '✓ Verified' if s['linkedin_verified'] else '⚠ Not provided', 'Key Strengths': ' | '.join(s['key_strengths'][:4]), 'Recommendation': s['recommendation']})
                st.dataframe(pd.DataFrame(t1d), use_container_width=True, hide_index=True)
            if tiers['Tier 2 (Good Fit)']:
                st.markdown("---")
                st.markdown("## 👍 TIER 2 – GOOD FIT")
                t2d = []
                for i, c in enumerate(tiers['Tier 2 (Good Fit)'], len(tiers['Tier 1 (Strong Fit)']) + 1):
                    s = c['score']
                    t2d.append({'#': i, 'Candidate': s['candidate_name'], 'Score': f"{s['overall_score']}%", 'Strengths': ' | '.join(s['key_strengths'][:3]), 'Gaps': ' | '.join(s['gaps_identified'][:2]), 'Action': 'Contact if Tier 1 unavailable'})
                st.dataframe(pd.DataFrame(t2d), use_container_width=True, hide_index=True)
            st.markdown("---")
            st.markdown("## 📊 DETAILED SCORING BREAKDOWN")
            bd = []
            for c in candidates:
                s = c['score']
                bd.append({'Candidate': s['candidate_name'], 'Overall': f"{s['overall_score']}%", 'Skills': f"{s['skills_score']}%", 'Experience': f"{s['experience_score']}%", 'Education': f"{s['education_score']}%", 'Tier': s['tier']})
            st.dataframe(pd.DataFrame(bd), use_container_width=True, hide_index=True)
    elif ai_section == "🔍 LinkedIn Parse":
        st.subheader("🔍 LinkedIn Profile Parser")
        st.info("Parse LinkedIn profiles to extract candidate information for scoring")
        linkedin_url = st.text_input("Enter LinkedIn Profile URL", placeholder="https://linkedin.com/in/username")
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("🔍 Parse Profile", use_container_width=True):
                if linkedin_url:
                    with st.spinner("Parsing LinkedIn profile..."):
                        time.sleep(1)
                        profile = linkedin_parser.parse_profile(linkedin_url)
                        st.success("✅ Profile Parsed Successfully!")
                        ca, cb = st.columns([1, 2])
                        with ca:
                            st.markdown(f"**Name:** {profile['name']}")
                            st.markdown(f"**Headline:** {profile['headline']}")
                            st.markdown(f"**Location:** {profile['location']}")
                            st.markdown(f"**Experience:** {profile.get('experience_years', 'N/A')} years")
                        with cb:
                            st.markdown("**Skills:**")
                            skills = profile.get('skills', [])
                            st.markdown(f"`{', '.join(skills[:8])}`")
                            if profile.get('education'):
                                st.markdown(f"**Education:** {profile['education']}")
                else:
                    st.warning("Please enter a LinkedIn URL")
        with c2:
            st.markdown("""<div style="background: linear-gradient(135deg, #1a1a1a, #2d2d2d); color: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #CC0000;"><h4>💡 LinkedIn Integration</h4><p style="font-size: 0.9rem;">The LinkedIn parser extracts:</p><ul style="font-size: 0.85rem;"><li>Professional headline & summary</li><li>Skills & endorsements</li><li>Work experience timeline</li><li>Education & certifications</li><li>Location & contact info</li></ul></div>""", unsafe_allow_html=True)
    elif ai_section == "💾 Save Results":
        st.subheader("Save Candidates to Database")
        if st.session_state.candidates_batch:
            if st.button("💾 Save All Candidates", use_container_width=True, type="primary"):
                for c in st.session_state.candidates_batch:
                    score = c['score']
                    candidate_ref = generate_ref("CAND")
                    candidate_data = (candidate_ref, score['candidate_name'].split()[0] if score['candidate_name'] else "Unknown", ' '.join(score['candidate_name'].split()[1:]) if len(score['candidate_name'].split()) > 1 else '', score['parsed_data'].get('email', ''), score['parsed_data'].get('phone', ''), score['parsed_data'].get('linkedin', ''), score['parsed_data'].get('current_position', ''), score['parsed_data'].get('current_company', ''), score['parsed_data'].get('total_experience_years', 0), score['parsed_data'].get('education_level', ''), ', '.join([s['skill'] for s in score['parsed_data'].get('skills', [])]), score['parsed_data'].get('location', ''), c['filename'], c['cv_text'][:5000], None, 'AI Upload', 'Scored')
                    candidate_id = db.add_candidate(candidate_data)
                    db.update_candidate_ai_score(candidate_id, score['overall_score'], score['tier'], json.dumps(score), score['skills_score'], score['experience_score'], score['education_score'], score['overall_score'], score['linkedin_verified'], json.dumps(score['key_strengths']), json.dumps(score['gaps_identified']), score['recommendation'])
                st.success(f"✅ {len(st.session_state.candidates_batch)} candidates saved!")
                st.balloons()
        else:
            st.info("No candidates to save. Upload and analyze CVs first.")

def chat_communications():
    st.markdown("""<div class="churchgate-header"><h1>💬 Chat & Communications</h1><p>Team Messaging | Announcements | AI Assistant</p></div>""", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["💬 Team Chat", "📢 Announcements", "📧 Email"])
    with tab1:
        st.subheader("Team Chat")
        team_members = ["Emmanuel Etuk (Technology)", "Sanjeev Purwar (FM)", "Ahmed Karim (Sales)", "Adebayo Sakote (HR)", "Jeff Arikawe (Finance)", "Maikudi Kadoh (Security)", "Francis Asuquo (ELV)", "David Aiyedun (Legal)", "Ibukun Adeogun (Operations)"]
        chat_with = st.selectbox("Chat with:", ["Select colleague..."] + team_members)
        if chat_with != "Select colleague...":
            chat_key = f"chat_{chat_with}"
            if chat_key not in st.session_state:
                st.session_state[chat_key] = []
            for msg in st.session_state[chat_key][-20:]:
                if msg['sender'] == 'You':
                    st.markdown(f"""<div style="background: #CC0000; color: white; padding: 0.6rem 1rem; border-radius: 10px; margin: 0.3rem 0; margin-left: 3rem;"><strong>You</strong><p style="margin: 0.2rem 0;">{msg['content']}</p><small>{msg['time']}</small></div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div style="background: #f0f0f0; padding: 0.6rem 1rem; border-radius: 10px; margin: 0.3rem 0; margin-right: 3rem;"><strong>{msg['sender']}</strong><p style="margin: 0.2rem 0;">{msg['content']}</p><small>{msg['time']}</small></div>""", unsafe_allow_html=True)
            with st.form(f"chat_form_{chat_with}", clear_on_submit=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    message = st.text_input("Type message...", placeholder=f"Message {chat_with}...")
                with c2:
                    send = st.form_submit_button("📤 Send", use_container_width=True)
                if send and message:
                    st.session_state[chat_key].append({'sender': 'You', 'content': message, 'time': datetime.now().strftime('%I:%M %p')})
                    st.session_state[chat_key].append({'sender': chat_with, 'content': f"Thanks for your message! (Auto-reply: {chat_with.split('(')[0].strip()} will respond soon)", 'time': datetime.now().strftime('%I:%M %p')})
                    st.rerun()
        st.markdown("---")
        st.markdown("### 🤖 HRIS Assistant Bot")
        st.info("Ask me anything about leave, payroll, training, policies, benefits, or general HR inquiries. I'm here to help!")
        if 'bot_conversation' not in st.session_state:
            st.session_state.bot_conversation = []
        for msg in st.session_state.bot_conversation:
            if msg['role'] == 'user':
                st.markdown(f"""<div style="background: #CC0000; color: white; padding: 0.6rem 1rem; border-radius: 10px; margin: 0.3rem 0; margin-left: 3rem;"><strong>You</strong><p style="margin: 0.2rem 0;">{msg['content']}</p><small>{msg['time']}</small></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style="background: #f0f0f0; padding: 0.6rem 1rem; border-radius: 10px; margin: 0.3rem 0; margin-right: 3rem;"><strong>🤖 HRIS Bot</strong><p style="margin: 0.2rem 0;">{msg['content']}</p><small>{msg['time']}</small></div>""", unsafe_allow_html=True)
        with st.form("bot_form", clear_on_submit=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                bot_question = st.text_input("Ask HRIS Bot:", placeholder="e.g., How do I apply for leave? What are the training options?")
            with c2:
                ask = st.form_submit_button("🤖 Ask", use_container_width=True)
            if ask and bot_question:
                responses = {
                    'leave': "To apply for leave, go to your Employee Dashboard and click 'Request Leave'. Your current balance is 18 days. You can also check your leave history and upcoming approved leaves there. Would you like to know about specific leave types?",
                    'payroll': "Payroll is processed on the 25th of each month. For any payroll discrepancies, contact Accounts & Finance. Would you like to see your pay history?",
                    'training': "Check the Training & Development section for available courses. Currently we have BMS Advanced Integration, AI in Facility Management, Leadership Excellence, and Data Analytics for Operations. New webinars are added weekly. Which area interests you?",
                    'policy': "HR policies are available in the Employee Handbook. You can find policies on leave, code of conduct, benefits, and more. Is there a specific policy you'd like to know about?",
                    'benefits': "Churchgate Group offers health insurance (HMO), pension contributions, annual leave (20 days), and performance bonuses. Would you like details on any specific benefit?",
                    'performance': "Your performance reviews are conducted twice yearly. Your current score is 93.3%. You can view your detailed performance breakdown in the Performance & OKRs section. Would you like tips on improving your score?",
                    'promotion': "Promotions are based on performance score (40%), leadership competency (25%), strategic impact (20%), and readiness assessment (15%). Your current eligibility can be viewed in the Promotions section. Would you like to know more?",
                    'birthday': "You can view team birthdays on your Employee Dashboard. Upcoming birthdays this month include Chika Ikwuegbu (May 13), Francis Asuquo (May 19), Rhoda Ajibola (May 25), and Alice Agbo (May 28).",
                    'help': "I can help with: Leave, Payroll, Training, Policies, Benefits, Performance, Promotions, Birthdays, and general HR questions. What would you like to know?",
                }
                response = "I can help with leave, payroll, training, policies, benefits, performance, promotions, and more. What would you like to know?"
                for key, val in responses.items():
                    if key in bot_question.lower():
                        response = val
                        break
                st.session_state.bot_conversation.append({'role': 'user', 'content': bot_question, 'time': datetime.now().strftime('%I:%M %p')})
                st.session_state.bot_conversation.append({'role': 'bot', 'content': response, 'time': datetime.now().strftime('%I:%M %p')})
                st.rerun()
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.bot_conversation = []
            st.rerun()
    with tab2:
        st.subheader("📢 Company Announcements")
        for ann in [{"title": "Q2 Performance Reviews", "date": "2026-06-01", "priority": "High", "content": "All departments to submit Q2 reviews by June 15."}, {"title": "BMS Implementation Update", "date": "2026-05-28", "priority": "Medium", "content": "Phase 1 complete. Phase 2 starts June 10."}, {"title": "Holiday - Democracy Day", "date": "2026-05-25", "priority": "Medium", "content": "Office closed June 12."}]:
            pc = "#e53e3e" if ann['priority'] == 'High' else "#d69e2e"
            st.markdown(f"""<div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.6rem; border-left: 4px solid {pc};"><div style="display: flex; justify-content: space-between;"><strong>{ann['title']}</strong><span style="background: {pc}; color: white; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">{ann['priority']}</span></div><p style="margin: 0.4rem 0;">{ann['content']}</p><small>📅 {ann['date']}</small></div>""", unsafe_allow_html=True)
    with tab3:
        st.subheader("📧 Email Notifications")
        with st.form("email_prefs"):
            c1, c2 = st.columns(2)
            with c1:
                st.checkbox("Birthday Alerts", value=True)
                st.checkbox("Work Anniversaries", value=True)
                st.checkbox("Promotion Announcements", value=True)
            with c2:
                st.checkbox("Holiday Reminders", value=True)
                st.checkbox("Training & Webinars", value=True)
                st.checkbox("New Hire Announcements", value=True)
            if st.form_submit_button("💾 Save Preferences", use_container_width=True):
                st.success("✅ Preferences saved!")

def training_development():
    st.markdown("""<div class="churchgate-header"><h1>🎓 Training & Development</h1><p>Learning Management | Webinars | Professional Development</p></div>""", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📚 Courses", "🌐 Webinars", "📋 Calendar"])
    with tab1:
        st.subheader("My Learning Path")
        for course in [{"name": "BMS Advanced Integration", "progress": 75, "deadline": "2026-07-15"}, {"name": "AI in Facility Management", "progress": 40, "deadline": "2026-08-30"}, {"name": "Leadership Excellence", "progress": 90, "deadline": "2026-06-15"}, {"name": "Data Analytics for Operations", "progress": 60, "deadline": "2026-09-01"}]:
            color = "#38a169" if course['progress'] >= 80 else "#d69e2e"
            st.markdown(f"""<div style="background: white; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;"><div style="display: flex; justify-content: space-between;"><strong>{course['name']}</strong><span>{course['progress']}%</span></div><div style="background: #e0e0e0; height: 5px; border-radius: 3px; margin: 0.4rem 0;"><div style="background: {color}; width: {course['progress']}%; height: 5px; border-radius: 3px;"></div></div><small>Deadline: {course['deadline']}</small></div>""", unsafe_allow_html=True)
    with tab2:
        st.subheader("Upcoming Webinars")
        for web in [{"title": "AI in Real Estate Management", "date": "June 20, 2026", "source": "LinkedIn Learning", "dept": "Technology"}, {"title": "Financial Modeling for RE", "date": "June 25, 2026", "source": "CFA Institute", "dept": "Finance"}, {"title": "HR Tech Summit 2026", "date": "July 10, 2026", "source": "SHRM", "dept": "HR"}, {"title": "Facility Management Excellence", "date": "July 15, 2026", "source": "IFMA", "dept": "Operations"}, {"title": "Cybersecurity for Smart Buildings", "date": "July 20, 2026", "source": "NITDA", "dept": "Technology"}]:
            st.markdown(f"""<div style="background: white; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.4rem; border-left: 3px solid #CC0000;"><strong>{web['title']}</strong><br><small>📅 {web['date']} | 📍 {web['source']} | 🏢 {web['dept']}</small></div>""", unsafe_allow_html=True)
    with tab3:
        st.subheader("Training Calendar - June 2026")
        cal_data = []
        for day in range(1, 31):
            events = []
            if day == 15: events.append("BMS Training")
            if day == 20: events.append("AI in FM Webinar")
            if day == 25: events.append("Finance Workshop")
            cal_data.append({"Day": day, "Events": ", ".join(events) if events else "-"})
        st.dataframe(pd.DataFrame(cal_data), use_container_width=True, hide_index=True)

def reports_analytics():
    st.markdown("""<div class="churchgate-header"><h1>📊 Reports & Analytics</h1><p>Business Intelligence | Churchgate Group</p></div>""", unsafe_allow_html=True)
    report = st.selectbox("Select Report", ["Executive Scorecard", "Workforce Analytics", "Recruitment Funnel", "Performance Trends", "Department Scorecard", "Financial Overview"])
    if report == "Executive Scorecard":
        st.subheader("📊 Executive Scorecard")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Revenue", "₦12.5B", "+15%")
        c2.metric("EBITDA", "₦3.8B", "+8%")
        c3.metric("Occupancy", "87%", "+5%")
        c4.metric("NPS Score", "72", "+12")
        pillars_df = pd.DataFrame({'Pillar': ['Occupancy & Revenue', 'Process Simplification', 'Asset Reliability', 'People & Culture'], 'Q1': [75, 60, 80, 85], 'Q2': [78, 65, 82, 88], 'Q3': [82, 70, 85, 90], 'Q4': [85, 72, 90, 88], 'Target': [90, 80, 95, 90]})
        fig = go.Figure()
        for i, row in pillars_df.iterrows():
            fig.add_trace(go.Scatter(x=['Q1', 'Q2', 'Q3', 'Q4'], y=[row['Q1'], row['Q2'], row['Q3'], row['Q4']], name=row['Pillar'], mode='lines+markers'))
        fig.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="Target")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    elif report == "Recruitment Funnel":
        st.subheader("📊 Recruitment Funnel")
        c1, c2, c3 = st.columns(3)
        c1.metric("Time to Hire", "23 days", "↓ 35%")
        c2.metric("Cost per Hire", "₦450K", "↓ 42%")
        c3.metric("Offer Acceptance", "85%", "↑ 10%")
        funnel = pd.DataFrame({'Stage': ['Sourced', 'Applied', 'Screened', 'Interviewed', 'Offered', 'Hired'], 'Count': [100, 75, 50, 20, 5, 2]})
        fig = px.funnel(funnel, x='Count', y='Stage', color_discrete_sequence=['#CC0000'])
        st.plotly_chart(fig, use_container_width=True)
    elif report == "Workforce Analytics":
        st.subheader("Workforce Distribution")
        c1, c2 = st.columns(2)
        with c1:
            dept_data = pd.DataFrame({'Department': ['Technology', 'FM', 'Sales', 'Finance', 'HR', 'Procurement', 'Security', 'Legal', 'Operations'], 'Count': [12, 25, 15, 10, 8, 8, 20, 3, 18]})
            fig = px.bar(dept_data, x='Department', y='Count', color_discrete_sequence=['#CC0000'])
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            exp_data = pd.DataFrame({'Experience': ['0-2 yrs', '3-5 yrs', '6-10 yrs', '10+ yrs'], 'Count': [8, 15, 18, 7]})
            fig = px.pie(exp_data, values='Count', names='Experience', hole=0.4, color_discrete_sequence=['#CC0000', '#4a4a4a', '#888888', '#cccccc'])
            st.plotly_chart(fig, use_container_width=True)
    elif report == "Department Scorecard":
        st.subheader("📊 Department Performance Scorecard")
        scorecard = pd.DataFrame({'Department': ['Technology', 'FM', 'Finance', 'HR', 'Sales', 'Procurement', 'Security', 'Legal', 'Operations'], 'Occupancy & Revenue': [85, 80, 90, 75, 88, 82, 78, 70, 85], 'Process Simplification': [72, 68, 75, 70, 65, 60, 55, 50, 68], 'Asset Reliability': [90, 88, 82, 85, 80, 78, 85, 75, 82], 'People & Culture': [88, 85, 80, 92, 82, 78, 80, 75, 85], 'Overall': [84, 80, 82, 81, 79, 75, 75, 68, 80]})
        fig = go.Figure(data=[go.Heatmap(z=scorecard[['Occupancy & Revenue', 'Process Simplification', 'Asset Reliability', 'People & Culture']].values, x=['Occupancy & Revenue', 'Process Simplification', 'Asset Reliability', 'People & Culture'], y=scorecard['Department'], colorscale='RdYlGn', zmin=0, zmax=100)])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    elif report == "Performance Trends":
        st.subheader("📈 Performance Trends")
        trends = pd.DataFrame({'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], 'Overall Score': [78, 80, 82, 84, 85, 87], 'Target': [85, 85, 85, 85, 85, 85]})
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trends['Month'], y=trends['Overall Score'], name='Actual', mode='lines+markers', line=dict(color='#CC0000', width=3)))
        fig.add_trace(go.Scatter(x=trends['Month'], y=trends['Target'], name='Target', mode='lines', line=dict(color='#4a4a4a', dash='dash')))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    elif report == "Financial Overview":
        st.subheader("💰 Financial Overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Revenue", "₦12.5B", "+15%")
        c2.metric("Operating Cost", "₦8.7B", "+8%")
        c3.metric("EBITDA Margin", "30.4%", "+2.1%")
        c4.metric("Cash Flow", "₦2.1B", "+12%")
        fin_data = pd.DataFrame({'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], 'Revenue': [1.8, 2.0, 2.1, 2.2, 2.3, 2.1], 'Cost': [1.3, 1.4, 1.5, 1.5, 1.6, 1.4]})
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Revenue (₦B)', x=fin_data['Month'], y=fin_data['Revenue'], marker_color='#CC0000'))
        fig.add_trace(go.Bar(name='Cost (₦B)', x=fin_data['Month'], y=fin_data['Cost'], marker_color='#4a4a4a'))
        fig.update_layout(height=350, barmode='group')
        st.plotly_chart(fig, use_container_width=True)

def notifications_page():
    st.markdown("""<div class="churchgate-header"><h1>🔔 Notifications</h1><p>Alerts, Reminders, and Updates</p></div>""", unsafe_allow_html=True)
    for n in [{"title": "Performance Review Due", "msg": "Q2 2026 reviews due by June 15", "time": "2 hours ago", "unread": True}, {"title": "New Hire", "msg": "Welcome David Effiong - Facility Manager", "time": "Yesterday", "unread": True}, {"title": "Training Reminder", "msg": "BMS Advanced starts June 15", "time": "2 days ago", "unread": False}, {"title": "Holiday Notice", "msg": "Democracy Day - June 12, 2026", "time": "1 week ago", "unread": False}]:
        bg = "#fff3f3" if n['unread'] else "#fafafa"
        icon = "🔴" if n['unread'] else "✅"
        st.markdown(f"""<div style="background: {bg}; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.4rem; border-left: 3px solid #CC0000;">{icon} <strong>{n['title']}</strong><p style="margin: 0.2rem 0;">{n['msg']}</p><small>{n['time']}</small></div>""", unsafe_allow_html=True)

def my_profile():
    user = st.session_state.user
    st.markdown(f"""<div class="churchgate-header"><h1>👤 My Profile</h1><p>{user['name']} • {user.get('position', 'Employee')}</p></div>""", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        if 'profile_pic' in st.session_state and st.session_state['profile_pic'] is not None:
            st.image(st.session_state['profile_pic'], width=150)
        else:
            initials = generate_initials(user['name'])
            st.markdown(f"""<div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);"><div style="width: 80px; height: 80px; border-radius: 50%; background: #CC0000; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 700; color: white; margin: 0 auto;">{initials}</div><h3 style="margin-top: 0.8rem;">{user['name']}</h3><p>{user.get('position', 'Employee')}</p><p style="color: #CC0000;">ID: {user.get('employee_id', 'N/A')}</p><p>🏢 {user.get('department', 'N/A')}</p><p>👤 Supervisor: Jerome Das (COO)</p></div>""", unsafe_allow_html=True)
        uploaded_pic = st.file_uploader("📸 Upload Profile Picture", type=['jpg', 'jpeg', 'png'])
        if uploaded_pic is not None:
            st.session_state['profile_pic'] = uploaded_pic
    with c2:
        with st.form("profile_update"):
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("First Name", value=user['name'].split()[0] if user['name'] else "")
                st.text_input("Email", value=user.get('email', ''))
                st.text_input("Phone", value="+234 800 000 0000")
            with c2:
                ln = ' '.join(user['name'].split()[1:]) if len(user['name'].split()) > 1 else ''
                st.text_input("Last Name", value=ln)
                st.selectbox("Department", ["Technology Group", "Facility Management", "HR", "Sales", "Finance", "Procurement", "Security", "Legal", "Operations"], index=0)
            if st.form_submit_button("💾 Update Profile", use_container_width=True):
                st.success("✅ Profile updated!")

def main():
    if st.session_state.user is None:
        login_section()
    else:
        page = sidebar_navigation()
        if 'navigate_to' in st.session_state:
            page = st.session_state.pop('navigate_to')
        page_routes = {
            "🏠 Employee Dashboard": employee_dashboard,
            "📊 Executive Dashboard": executive_dashboard,
            "👥 Employee Management": employee_management,
            "📈 Performance & OKRs": performance_okrs,
            "📈 My Performance & OKRs": performance_okrs,
            "🚀 Promotions": promotions,
            "💼 Recruitment Hub": recruitment_hub,
            "🤖 AI Recruitment Agent": ai_recruitment_agent,
            "📊 Reports & Analytics": reports_analytics,
            "💬 Chat & Communications": chat_communications,
            "🎓 Training & Development": training_development,
            "🔔 Notifications": notifications_page,
            "👤 My Profile": my_profile,
        }
        page_func = page_routes.get(page, employee_dashboard)
        page_func()

if __name__ == "__main__":
    main()
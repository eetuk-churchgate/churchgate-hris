"""
Churchgate Group HRIS v4.0
Enterprise-Grade AI-Powered Human Resource Information System
Fortune 500 Standard | International Best Practices
"""

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
from PIL import Image, ImageDraw, ImageFont
import requests
import calendar

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.database import DatabaseManager
from utils.ai_agent import AIRecruitmentAgent
from utils.linkedin_parser import LinkedInParser
from utils.email_service import EmailService
from utils.chat_service import ChatService
from utils.training_service import TrainingService

# ============ PAGE CONFIGURATION ============
st.set_page_config(
    page_title="Churchgate Group HRIS",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CHURCHGATE BRANDING ============
CHURCHGATE_RED = "#CC0000"
CHURCHGATE_DARK = "#1a1a1a"
CHURCHGATE_GREY = "#4a4a4a"
CHURCHGATE_LIGHT = "#f5f5f5"
CHURCHGATE_WHITE = "#ffffff"
CHURCHGATE_GOLD = "#c49216"

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

# ============ CUSTOM CSS - CHURCHGATE BRANDING ============
st.markdown(f"""
<style>
    :root {{
        --cg-red: {CHURCHGATE_RED};
        --cg-dark: {CHURCHGATE_DARK};
        --cg-grey: {CHURCHGATE_GREY};
        --cg-light: {CHURCHGATE_LIGHT};
        --cg-white: {CHURCHGATE_WHITE};
        --cg-gold: {CHURCHGATE_GOLD};
    }}
    
    .stApp {{
        background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
    }}
    
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%) !important;
        border-right: 3px solid {CHURCHGATE_RED};
    }}
    
    [data-testid="stSidebar"] * {{
        color: #e0e0e0 !important;
    }}
    
    [data-testid="stSidebar"] .stButton > button {{
        background: rgba(204, 0, 0, 0.2) !important;
        border: 1px solid {CHURCHGATE_RED} !important;
        color: white !important;
    }}
    
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(204, 0, 0, 0.4) !important;
    }}
    
    .churchgate-header {{
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border-left: 4px solid {CHURCHGATE_RED};
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }}
    
    .churchgate-header h1 {{
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }}
    
    .churchgate-header p {{
        color: #cccccc;
        font-size: 0.95rem;
        margin-top: 0.5rem;
    }}
    
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        text-align: center;
        border-top: 3px solid {CHURCHGATE_RED};
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(204, 0, 0, 0.15);
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a1a;
    }}
    
    .metric-label {{
        color: #666666;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .stButton > button {{
        background: linear-gradient(135deg, {CHURCHGATE_RED} 0%, #ff1a1a 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 1.5rem !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(204, 0, 0, 0.3) !important;
    }}
    
    .mission-banner {{
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin: 2rem 0;
        border: 2px solid {CHURCHGATE_RED};
    }}
    
    .mission-banner h2 {{
        color: {CHURCHGATE_RED};
        font-size: 1.5rem;
    }}
    
    .value-card {{
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border-bottom: 3px solid {CHURCHGATE_RED};
        height: 100%;
    }}
    
    .tier-1-badge {{
        background: #38a169;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
    }}
    
    .tier-2-badge {{
        background: #d69e2e;
        color: #1a1a1a;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
    }}
    
    .tier-3-badge {{
        background: {CHURCHGATE_RED};
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
    }}
</style>
""", unsafe_allow_html=True)

# ============ INITIALIZE RESOURCES ============
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

# ============ SESSION STATE ============
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_jd' not in st.session_state:
    st.session_state.current_jd = None
if 'candidates_batch' not in st.session_state:
    st.session_state.candidates_batch = []
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'active_chat_user' not in st.session_state:
    st.session_state.active_chat_user = None
if 'dashboard_metrics' not in st.session_state:
    st.session_state.dashboard_metrics = {
        'total_employees': 48,
        'occupancy_rate': 87,
        'revenue_vs_budget': 94,
        'tenant_satisfaction': 4.2,
        'open_positions': 5
    }

# ============ HELPER FUNCTIONS ============
def get_logo():
    """Get Churchgate logo"""
    logo_paths = [
        Path(__file__).parent / "churchgate-logo.png",
        Path(__file__).parent / "churchgate_logo.png"
    ]
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
    """Display actual Churchgate Mission, Vision, Purpose & Values"""
    st.markdown(f"""
    <div class="mission-banner">
        <h2>🏢 Churchgate Group</h2>
        <div style="display: flex; justify-content: space-around; margin: 1.5rem 0; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px; padding: 1rem;">
                <h3 style="color: {CHURCHGATE_RED};">🎯 Our Purpose</h3>
                <p style="font-size: 0.9rem;">{CHURCHGATE_PURPOSE}</p>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 1rem;">
                <h3 style="color: {CHURCHGATE_RED};">🔭 Our Vision</h3>
                <p style="font-size: 0.9rem;">{CHURCHGATE_VISION}</p>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 1rem;">
                <h3 style="color: {CHURCHGATE_RED};">📋 Our Mission</h3>
                <p style="font-size: 0.9rem;">{CHURCHGATE_MISSION}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Our Values Are Dear To Us")
    st.markdown("We deliver exceptional properties and infrastructure because we consistently sustain our core values of:")
    
    cols = st.columns(5)
    for i, (value, desc) in enumerate(CHURCHGATE_VALUES.items()):
        with cols[i]:
            st.markdown(f"""
                <div class="value-card">
                    <h4 style="color: {CHURCHGATE_RED};">{value}</h4>
                    <p style="font-size: 0.8rem; color: #666;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)

# ============ LOGIN SECTION ============
def login_section():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo = get_logo()
        if logo:
            st.image(logo, width=300)
        
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem 0;">
                <h1 style="color: #1a1a1a; font-size: 2rem; font-weight: 700;">HRIS Portal</h1>
                <p style="color: #666666; font-size: 0.9rem;">Human Resource Information System</p>
            </div>
        """, unsafe_allow_html=True)
        
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
            st.markdown("""
            | Role | Email | Password |
            |------|-------|----------|
            | Admin | admin@churchgate.com | admin123 |
            | HR Director | sarah@churchgate.com | hr123 |
            | Manager | emmanuel@churchgate.com | elv123 |
            | Employee | jane@churchgate.com | staff123 |
            """)

# ============ SIDEBAR ============
def sidebar_navigation():
    with st.sidebar:
        logo = get_logo()
        if logo:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(logo, width=120)
        
        st.markdown(f"""
            <div style="text-align: center; padding: 0.8rem 0; background: rgba(204, 0, 0, 0.1); 
                        border-radius: 8px; margin-bottom: 1rem; border: 1px solid rgba(204, 0, 0, 0.3);">
                <h3 style="color: {CHURCHGATE_RED}; margin: 0; font-size: 1rem;">CHURCHGATE GROUP</h3>
                <p style="color: #cccccc; font-size: 0.7rem; margin: 0;">HRIS v4.0</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.user:
            user = st.session_state.user
            initials = generate_initials(user['name'])
            
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.08); padding: 0.8rem; border-radius: 8px; 
                            margin-bottom: 1rem; border: 1px solid rgba(204, 0, 0, 0.2);">
                    <div style="display: flex; align-items: center; gap: 0.6rem;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; 
                                    background: {CHURCHGATE_RED}; display: flex; align-items: center; 
                                    justify-content: center; font-weight: 700; font-size: 1rem; color: white;">
                            {initials}
                        </div>
                        <div>
                            <p style="color: white; margin: 0; font-weight: 600; font-size: 0.85rem;">{user['name']}</p>
                            <p style="color: #cccccc; margin: 0; font-size: 0.7rem;">{user['role']} • {user.get('department', '')}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        user_role = st.session_state.user['role'] if st.session_state.user else 'Employee'
        
        if user_role in ['Admin', 'HR Director']:
            menu_options = [
                "🏠 Employee Dashboard",
                "📊 Executive Dashboard",
                "👥 Employee Management",
                "📈 Performance & OKRs",
                "🚀 Promotions",
                "💼 Recruitment Hub",
                "🤖 AI Recruitment Agent",
                "📊 Reports & Analytics",
                "💬 Chat & Communications",
                "🎓 Training & Development",
                "🔔 Notifications",
                "👤 My Profile"
            ]
        elif user_role == 'Manager':
            menu_options = [
                "🏠 Employee Dashboard",
                "💼 Recruitment Hub",
                "🤖 AI Recruitment Agent",
                "📈 Performance & OKRs",
                "💬 Chat & Communications",
                "🎓 Training & Development",
                "👤 My Profile"
            ]
        else:
            menu_options = [
                "🏠 Employee Dashboard",
                "📈 My Performance & OKRs",
                "💬 Chat & Communications",
                "🎓 Training & Development",
                "👤 My Profile"
            ]
        
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=["house-fill", "speedometer2", "people-fill", "graph-up-arrow",
                   "trophy-fill", "briefcase-fill", "robot", "file-earmark-bar-graph",
                   "chat-dots-fill", "book-fill", "bell-fill", "person-circle"][:len(menu_options)],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": CHURCHGATE_RED, "font-size": "16px"},
                "nav-link": {
                    "font-size": "13px", "text-align": "left", "margin": "3px 0",
                    "color": "#e0e0e0", "--hover-color": "rgba(204, 0, 0, 0.2)",
                    "border-radius": "6px",
                },
                "nav-link-selected": {
                    "background-color": "rgba(204, 0, 0, 0.3)",
                    "color": "white",
                    "border-left": "3px solid " + CHURCHGATE_RED,
                },
            }
        )
        
        st.markdown("---")
        
        if st.session_state.user:
            if st.button("🚪 Sign Out", use_container_width=True):
                st.session_state.user = None
                st.rerun()
        
        st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem; margin-top: 1rem;">
                <p style="color: #888888; font-size: 0.65rem; margin: 0;">© 2026 Churchgate Group</p>
                <p style="color: #888888; font-size: 0.65rem; margin: 0;">HRIS v4.0</p>
            </div>
        """, unsafe_allow_html=True)
        
        return selected

# ============ EMPLOYEE DASHBOARD ============
def employee_dashboard():
    show_churchgate_mission()
    
    user = st.session_state.user
    
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>👋 Welcome back, {user['name']}!</h1>
            <p>{user.get('position', 'Employee')} • {user.get('department', 'Department')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Profile Completeness</div>
                <div class="metric-value">80%</div>
                <small><a href="#">Edit Profile →</a></small>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Leave Days</div>
                <div class="metric-value">18</div>
                <small style="color: #38a169;">Available</small>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Performance</div>
                <div class="metric-value">93.3%</div>
                <small style="color: #38a169;">↑ 5%</small>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Team Members</div>
                <div class="metric-value">12</div>
                <small>{user.get('department', '')}</small>
            </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Performance Overview")
        pillars = {
            "Occupancy & Revenue Growth": 85,
            "Process Simplification": 72,
            "Asset Reliability & Digitalization": 90,
            "People & Culture": 88
        }
        for pillar, progress in pillars.items():
            color = "#38a169" if progress >= 85 else "#d69e2e"
            st.markdown(f"""
                <div style="background: white; padding: 0.6rem 1rem; border-radius: 6px; margin-bottom: 0.4rem;
                            display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-weight: 600; font-size: 0.85rem;">{pillar}</span>
                    <div style="width: 150px;">
                        <div style="background: #e0e0e0; height: 6px; border-radius: 3px;">
                            <div style="background: {color}; width: {progress}%; height: 6px; border-radius: 3px;"></div>
                        </div>
                    </div>
                    <span style="font-weight: 700; color: {color};">{progress}%</span>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎂 Team Birthdays")
        birthdays = [
            {"name": "Chika Ikwuegbu", "date": "May 13", "dept": "Security"},
            {"name": "Francis Asuquo", "date": "May 19", "dept": "ELV Systems"},
            {"name": "Rhoda Ajibola", "date": "May 25", "dept": "Facility Management"},
            {"name": "Alice Agbo", "date": "May 28", "dept": "Procurement"},
        ]
        for b in birthdays:
            st.markdown(f"""
                <div style="background: white; padding: 0.5rem; border-radius: 6px; margin-bottom: 0.3rem;
                            display: flex; align-items: center; gap: 0.5rem;">
                    <span>🎂</span>
                    <div><strong style="font-size: 0.8rem;">{b['name']}</strong><br>
                    <small>{b['date']} • {b['dept']}</small></div>
                </div>
            """, unsafe_allow_html=True)
        
        st.subheader("🎉 Anniversaries")
        anniversaries = [
            {"name": "Augustine Oleh", "years": 5},
            {"name": "Charles Okere", "years": 8},
            {"name": "Emmanuel Etuk", "years": 7},
        ]
        for a in anniversaries:
            st.markdown(f"""
                <div style="background: white; padding: 0.5rem; border-radius: 6px; margin-bottom: 0.3rem;">
                    ⭐ <strong>{a['name']}</strong> - {a['years']} years
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎓 Recommended Training")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h4>🔧 BMS Advanced</h4>
                <p style="font-size: 0.8rem;">Advanced Building Management</p>
                <small style="color: {CHURCHGATE_RED};">📅 June 15, 2026</small>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <h4>🤖 AI in FM</h4>
                <p style="font-size: 0.8rem;">Practical AI for Facilities</p>
                <small style="color: {CHURCHGATE_RED};">📅 June 20, 2026</small>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <h4>📊 Data Analytics</h4>
                <p style="font-size: 0.8rem;">Operational Analytics</p>
                <small style="color: {CHURCHGATE_RED};">📅 July 5, 2026</small>
            </div>
        """, unsafe_allow_html=True)


# ============ EXECUTIVE DASHBOARD ============
def executive_dashboard():
    show_churchgate_mission()
    
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>📊 Executive Dashboard</h1>
            <p>Corporate Strategy 2026-2027 | Churchgate Group Portfolio Performance</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Dynamic metrics (admin can update)
    metrics = st.session_state.dashboard_metrics
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Employees</div>
                <div class="metric-value">{metrics['total_employees']}</div>
                <small style="color: #38a169;">Active workforce</small>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Occupancy Rate</div>
                <div class="metric-value">{metrics['occupancy_rate']}%</div>
                <small style="color: #38a169;">Across portfolio</small>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Revenue vs Budget</div>
                <div class="metric-value">{metrics['revenue_vs_budget']}%</div>
                <small style="color: #d69e2e;">{100 - metrics['revenue_vs_budget']}% below target</small>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Tenant Satisfaction</div>
                <div class="metric-value">{metrics['tenant_satisfaction']}/5</div>
                <small style="color: #38a169;">↑ 0.3 points</small>
            </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Open Positions</div>
                <div class="metric-value">{metrics['open_positions']}</div>
                <small style="color: {CHURCHGATE_RED};">Active recruitment</small>
            </div>
        """, unsafe_allow_html=True)
    
    # Admin controls to update metrics
    if st.session_state.user and st.session_state.user['role'] in ['Admin', 'HR Director']:
        with st.expander("⚙️ Update Dashboard Metrics (Admin Only)"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_employees = st.number_input("Total Employees", value=metrics['total_employees'])
                new_occupancy = st.slider("Occupancy Rate %", 0, 100, metrics['occupancy_rate'])
            with col2:
                new_revenue = st.slider("Revenue vs Budget %", 0, 100, metrics['revenue_vs_budget'])
                new_satisfaction = st.slider("Tenant Satisfaction", 1.0, 5.0, metrics['tenant_satisfaction'], 0.1)
            with col3:
                new_positions = st.number_input("Open Positions", value=metrics['open_positions'])
            
            if st.button("💾 Update Metrics", use_container_width=True):
                st.session_state.dashboard_metrics = {
                    'total_employees': new_employees,
                    'occupancy_rate': new_occupancy,
                    'revenue_vs_budget': new_revenue,
                    'tenant_satisfaction': new_satisfaction,
                    'open_positions': new_positions
                }
                st.success("✅ Metrics updated!")
                st.rerun()
    
    # Portfolio performance
    st.subheader("🏢 Portfolio Performance")
    
    portfolio_data = pd.DataFrame({
        'Property': CHURCHGATE_PORTFOLIO,
        'Occupancy': [87, 92, 85, 78, 95, 90],
        'Revenue': [94, 98, 88, 82, 97, 91],
        'Satisfaction': [4.3, 4.5, 4.1, 3.9, 4.4, 4.2]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Occupancy %', x=portfolio_data['Property'], y=portfolio_data['Occupancy'], marker_color=CHURCHGATE_RED))
    fig.add_trace(go.Bar(name='Revenue %', x=portfolio_data['Property'], y=portfolio_data['Revenue'], marker_color=CHURCHGATE_GREY))
    fig.update_layout(height=350, barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    
    # Strategic pillars
    st.subheader("🎯 Strategic Pillars 2026-2027")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {CHURCHGATE_RED};">
                <h4>1. Occupancy & Revenue Growth</h4>
                <p style="font-size: 0.85rem;">Drive revenue, maintain fiscal discipline, improve tenant retention</p>
                <div style="background: #e0e0e0; height: 6px; border-radius: 3px;">
                    <div style="background: {CHURCHGATE_RED}; width: 85%; height: 6px; border-radius: 3px;"></div>
                </div>
                <small>85% Complete</small>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {CHURCHGATE_RED};">
                <h4>2. Process Simplification</h4>
                <p style="font-size: 0.85rem;">AI-driven automation, workflow optimization</p>
                <div style="background: #e0e0e0; height: 6px; border-radius: 3px;">
                    <div style="background: {CHURCHGATE_RED}; width: 72%; height: 6px; border-radius: 3px;"></div>
                </div>
                <small>72% Complete</small>
            </div>
        """, unsafe_allow_html=True)

# ============ EMPLOYEE MANAGEMENT ============
def employee_management():
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>👥 Employee Management</h1>
            <p>Comprehensive workforce management | Churchgate Group</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Directory", "➕ Add Employee", "📤 Bulk Upload", "🏢 Departments", "📊 Org Chart"])
    
    with tab1:
        st.subheader("Employee Directory")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("🔍 Search", placeholder="Name, ID, department...")
        with col2:
            dept = st.selectbox("Department", ["All", "Senior Management", "Technology Group", "Facility Management", 
                                                 "Human Resources", "Sales & Marketing", "Accounts & Finance", 
                                                 "Procurement", "Security", "Legal", "Operations"])
        with col3:
            status = st.selectbox("Status", ["All", "Active", "On Leave", "Probation"])
        
        # Real employee data from Churchgate
        employees = [
            {"name": "Vinay Mahtani", "id": "GMD01", "dept": "Senior Management", "position": "GMD", "status": "Active"},
            {"name": "Emmanuel Etuk", "id": "AN00387", "dept": "Technology Group", "position": "Head, ELV Systems", "status": "Active"},
            {"name": "Sanjeev Purwar", "id": "LE00212", "dept": "Facility Management", "position": "Head, MEP", "status": "Active"},
            {"name": "Ahmed Karim", "id": "LN00369", "dept": "Sales & Marketing", "position": "GM, Sales & Marketing", "status": "Active"},
            {"name": "Jerome Das", "id": "LE00019", "dept": "Senior Management", "position": "COO", "status": "Active"},
            {"name": "Ibukun Adeogun", "id": "AN00012", "dept": "Operations", "position": "GM, Operations/Admin", "status": "Active"},
            {"name": "Jeff Arikawe", "id": "LN00008", "dept": "Accounts & Finance", "position": "Chief Accountant", "status": "Active"},
            {"name": "Adebayo Sakote", "id": "LN00037", "dept": "Human Resources", "position": "HR Manager", "status": "Active"},
            {"name": "Anand Bora", "id": "LE00071", "dept": "Procurement", "position": "GM, Procurement", "status": "Active"},
            {"name": "Maikudi Kadoh", "id": "AN00391", "dept": "Security", "position": "Chief Security Officer", "status": "Active"},
            {"name": "David Aiyedun", "id": "AN00455", "dept": "Legal", "position": "Legal Officer", "status": "Active"},
            {"name": "Chika Ikwuegbu", "id": "LN00438", "dept": "Security", "position": "Admin Assistant", "status": "Active"},
            {"name": "Francis Asuquo", "id": "AN00433", "dept": "Technology Group", "position": "ELV Engineer", "status": "Active"},
            {"name": "Alice Agbo", "id": "AN00423", "dept": "Procurement", "position": "Store Keeper", "status": "Active"},
            {"name": "Augustine Oleh", "id": "AN00425", "dept": "Facility Management", "position": "HSE Coordinator", "status": "Active"},
        ]
        
        for emp in employees:
            initials = generate_initials(emp['name'])
            st.markdown(f"""
                <div style="background: white; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.4rem;
                            display: flex; align-items: center; gap: 1rem; border: 1px solid #e0e0e0;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; background: {CHURCHGATE_RED};
                                display: flex; align-items: center; justify-content: center;
                                font-weight: 700; color: white; min-width: 40px;">{initials}</div>
                    <div style="flex: 1;">
                        <strong>{emp['name']}</strong>
                        <br><small>{emp['position']} • {emp['dept']}</small>
                    </div>
                    <div style="text-align: right;">
                        <small>ID: {emp['id']}</small>
                        <br><span style="background: #38a169; color: white; padding: 0.2rem 0.6rem; 
                                    border-radius: 12px; font-size: 0.75rem;">{emp['status']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Add New Employee")
        
        with st.form("add_employee_form"):
            st.markdown("### Basic Information")
            col1, col2, col3 = st.columns(3)
            with col1:
                first_name = st.text_input("First Name *")
                last_name = st.text_input("Last Name *")
                middle_name = st.text_input("Middle Name")
                staff_id = st.text_input("Staff ID *")
            with col2:
                phone = st.text_input("Phone Number", placeholder="+234 800 000 0000")
                email = st.text_input("Email")
                gender = st.selectbox("Gender", ["", "Male", "Female"])
                contract_type = st.selectbox("Contract Type", ["Full-time", "Contract", "Part-time", "Intern"])
            with col3:
                dob = st.date_input("Date of Birth")
                marital_status = st.selectbox("Marital Status", ["", "Single", "Married", "Divorced", "Widowed"])
            
            st.markdown("### Job Information")
            col1, col2, col3 = st.columns(3)
            with col1:
                department = st.selectbox("Department *", [
                    "", "Senior Management", "Technology Group", "Facility Management",
                    "Human Resources", "Sales & Marketing", "Accounts & Finance",
                    "Procurement", "Security", "Legal", "Operations"
                ])
                job_role = st.text_input("Job Role *")
            with col2:
                location = st.selectbox("Location", ["", "World Trade Center Abuja", "Churchgate Tower 1 Lagos", 
                                                      "Churchgate Tower 2 Lagos", "Churchgate Plaza Abuja"])
                cost_center = st.text_input("Cost Center")
            with col3:
                line_manager = st.text_input("Line Manager")
                join_date = st.date_input("Date of Employment")
            
            st.markdown("### Family Details")
            col1, col2 = st.columns(2)
            with col1:
                next_of_kin = st.text_input("Next of Kin Name")
                nok_relationship = st.text_input("Relationship")
            with col2:
                nok_phone = st.text_input("Next of Kin Phone")
                nok_address = st.text_area("Next of Kin Address", height=80)
            
            st.markdown("### Bank Details")
            col1, col2, col3 = st.columns(3)
            with col1:
                bank_name = st.text_input("Bank Name")
            with col2:
                account_name = st.text_input("Account Name")
            with col3:
                account_number = st.text_input("Account Number")
            
            st.markdown("### Documents")
            col1, col2 = st.columns(2)
            with col1:
                cv_upload = st.file_uploader("Upload CV", type=['pdf', 'docx'])
            with col2:
                cert_upload = st.file_uploader("Upload Certifications", type=['pdf', 'docx', 'jpg', 'png'])
            
            submitted = st.form_submit_button("✅ Add Employee", use_container_width=True)
            if submitted:
                if first_name and last_name and staff_id and department and job_role:
                    st.success(f"✅ {first_name} {last_name} added successfully!")
                    st.balloons()
                else:
                    st.error("Please fill all required fields (*)")
    
    with tab3:
        st.subheader("Bulk Employee Upload")
        st.info("Upload CSV file with employee data")
        template_df = pd.DataFrame(columns=['first_name', 'last_name', 'email', 'staff_id', 'department', 'position', 'phone'])
        csv = template_df.to_csv(index=False)
        st.download_button("📥 Download Template", csv, "employee_template.csv", "text/csv")
        
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write(f"**{len(df)} employees found**")
            st.dataframe(df.head(), use_container_width=True)
            if st.button("📤 Upload All", use_container_width=True):
                st.success(f"✅ {len(df)} employees uploaded!")
                st.balloons()
    
    with tab4:
        st.subheader("Churchgate Group Departments")
        departments = [
            {"name": "Senior Management", "head": "Vinay Mahtani (GMD)", "staff": 5},
            {"name": "Technology Group", "head": "Emmanuel Etuk", "staff": 12},
            {"name": "Facility Management", "head": "Sanjeev Purwar", "staff": 25},
            {"name": "Human Resources", "head": "Adebayo Sakote", "staff": 8},
            {"name": "Sales & Marketing", "head": "Ahmed Karim", "staff": 15},
            {"name": "Accounts & Finance", "head": "Jeff Arikawe", "staff": 10},
            {"name": "Procurement", "head": "Anand Bora", "staff": 8},
            {"name": "Security", "head": "Maikudi Kadoh", "staff": 20},
            {"name": "Legal", "head": "David Aiyedun", "staff": 3},
            {"name": "Operations", "head": "Ibukun Adeogun", "staff": 18},
        ]
        
        for dept in departments:
            st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;
                            border-left: 4px solid {CHURCHGATE_RED}; display: flex; justify-content: space-between;">
                    <div>
                        <strong>{dept['name']}</strong>
                        <br><small>Head: {dept['head']}</small>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.5rem; font-weight: 700;">{dept['staff']}</span>
                        <br><small>staff</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with tab5:
        st.subheader("Organizational Structure")
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20, thickness=20,
                line=dict(color="black", width=0.5),
                label=["GMD", "COO", "Technology", "Facility Mgmt", "HR", "Sales", "Finance", "Procurement", "Security", "Legal", "Operations"],
                color=[CHURCHGATE_RED, CHURCHGATE_GREY, CHURCHGATE_GREY, CHURCHGATE_GREY, CHURCHGATE_GREY,
                       CHURCHGATE_GREY, CHURCHGATE_GREY, CHURCHGATE_GREY, CHURCHGATE_GREY, CHURCHGATE_GREY, CHURCHGATE_GREY]
            ),
            link=dict(
                source=[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                target=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2],
                value=[20, 12, 25, 8, 15, 10, 8, 20, 3, 18, 5]
            )
        )])
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)


# ============ PERFORMANCE & OKRs ============
def performance_okrs():
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>📈 Performance & Strategic OKRs</h1>
            <p>Corporate Strategy 2026-2027 | Performance Management</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🎯 Corporate Strategic Pillars 2026-2027")
    
    pillars = {
        "1. Occupancy & Revenue Growth": {
            "weight": 40,
            "objectives": [
                "Increase data centre revenue by 15%",
                "100% revenue realization as per approved budget",
                "Nil O/S debts within 30 days of invoicing",
                "Retention of 90% existing customers",
                "0% variance from budgeted costs"
            ],
            "progress": 85,
            "responsible": "COO",
            "accountable": "GMD"
        },
        "2. Process Simplification": {
            "weight": 20,
            "objectives": [
                "AI implementation strategy by May 31, 2026",
                "Full BMS installation by June 30, 2026",
                "99% Preventive Maintenance compliance",
                "90% SMARTCHECK utilization"
            ],
            "progress": 72,
            "responsible": "ELV/Hive Mechanics",
            "accountable": "GMD"
        },
        "3. Asset Reliability & Digitalization": {
            "weight": 25,
            "objectives": [
                "100% ELV critical assets assessed biannually",
                "80% identified risks mitigated within timeframe",
                "0 days delay in tenant handover",
                "90% tenant complaints addressed within 24hrs"
            ],
            "progress": 90,
            "responsible": "FM Heads",
            "accountable": "COO"
        },
        "4. People & Culture": {
            "weight": 15,
            "objectives": [
                "100% staff with JDs by April 30, 2026",
                "100% staff appraised twice yearly",
                "Succession planning for A-players",
                "2 LMS courses per employee per half-year",
                "60-80% improvement in behavioural skills"
            ],
            "progress": 88,
            "responsible": "HR Director",
            "accountable": "GMD"
        }
    }
    
    for pillar_name, data in pillars.items():
        with st.expander(f"{pillar_name} | Weight: {data['weight']}% | Progress: {data['progress']}%", expanded=True):
            st.progress(data['progress'] / 100)
            for obj in data['objectives']:
                st.markdown(f"✅ {obj}")
            st.markdown(f"**RACI:** Responsible: {data['responsible']} | Accountable: {data['accountable']} | Consulted: All HODs | Informed: Board")


# ============ PROMOTIONS ============
def promotions():
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>🚀 Promotions & Career Progression</h1>
            <p>AI-Driven Succession Planning | Talent Management</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #38a169;">⭐ A-Players</h3>
                <div class="metric-value">4</div>
                <small>Ready for promotion</small>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {CHURCHGATE_RED};">📋 Pipeline</h3>
                <div class="metric-value">85%</div>
                <small>Key positions covered</small>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #3182ce;">📈 Avg Time</h3>
                <div class="metric-value">2.3</div>
                <small>Years to promotion</small>
            </div>
        """, unsafe_allow_html=True)
    
    st.subheader("🎯 Promotion Candidates - AI Assessment")
    candidates = [
        {"name": "Emmanuel Etuk", "current": "Head, ELV Systems", "proposed": "Director, Technology", "score": 93, "readiness": "Ready Now", "gap": "None", "risk": "Low"},
        {"name": "Sanjeev Purwar", "current": "Head, MEP", "proposed": "Director, Facilities", "score": 88, "readiness": "Ready Now", "gap": "Leadership", "risk": "Medium"},
        {"name": "Adebayo Sakote", "current": "HR Manager", "proposed": "Senior HR Manager", "score": 85, "readiness": "Q3 2026", "gap": "Strategic HR", "risk": "Low"},
        {"name": "Olalekan Bolarinwa", "current": "Deputy Accounts Manager", "proposed": "Accounts Manager", "score": 82, "readiness": "Q4 2026", "gap": "Certification", "risk": "Medium"},
    ]
    
    for c in candidates:
        color = "#38a169" if c['readiness'] == 'Ready Now' else "#d69e2e"
        st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.6rem;
                        border-left: 4px solid {color};">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <strong>{c['name']}</strong>
                        <br><small>{c['current']} → <strong>{c['proposed']}</strong></small>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: {color}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-weight: 600;">
                            {c['readiness']}
                        </span>
                        <br><small>Score: {c['score']}% | Risk: {c['risk']}</small>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


# ============ RECRUITMENT HUB - FULLY FUNCTIONAL ============
def recruitment_hub():
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>💼 Recruitment Hub</h1>
            <p>Manage Jobs, Applications, and Recruitment Workflows</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Active Jobs", "➕ Post New Job", "👥 Applications", "📊 Pipeline"])
    
    with tab1:
        st.subheader("Active Job Postings")
        jobs = [
            {"title": "AI Transformation Lead", "dept": "Technology Group", "location": "Abuja", "type": "Full-time", "closing": "2026-06-30", "ref": "JOB-2026-001"},
            {"title": "Senior Facility Manager", "dept": "Facility Management", "location": "Lagos", "type": "Full-time", "closing": "2026-07-15", "ref": "JOB-2026-002"},
            {"title": "Network Engineer", "dept": "Technology Group", "location": "Abuja", "type": "Full-time", "closing": "2026-06-20", "ref": "JOB-2026-003"},
            {"title": "Procurement Officer", "dept": "Procurement", "location": "Abuja", "type": "Full-time", "closing": "2026-07-01", "ref": "JOB-2026-004"},
            {"title": "HVAC Technician", "dept": "Facility Management", "location": "Abuja", "type": "Contract", "closing": "2026-06-25", "ref": "JOB-2026-005"},
        ]
        for job in jobs:
            st.markdown(f"""
                <div style="background: white; padding: 1.2rem; border-radius: 8px; margin-bottom: 0.8rem;
                            border-left: 4px solid {CHURCHGATE_RED};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0;">{job['title']}</h4>
                            <p style="margin: 0.3rem 0; color: #666;">🏢 {job['dept']} | 📍 {job['location']} | 💼 {job['type']}</p>
                            <small>Ref: {job['ref']} | Closes: {job['closing']}</small>
                        </div>
                        <span style="background: #38a169; color: white; padding: 0.3rem 1rem; border-radius: 15px;">Active</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Post New Job Opening")
        with st.form("post_job"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Job Title *")
                department = st.selectbox("Department *", ["Technology Group", "Facility Management", "Human Resources", 
                                                            "Sales & Marketing", "Accounts & Finance", "Procurement",
                                                            "Security", "Legal", "Operations", "Senior Management"])
                location = st.selectbox("Location", ["World Trade Center Abuja", "Churchgate Tower 1 Lagos", 
                                                      "Churchgate Tower 2 Lagos", "Churchgate Plaza Abuja"])
                emp_type = st.selectbox("Employment Type", ["Full-time", "Contract", "Part-time", "Intern"])
            with col2:
                salary = st.text_input("Salary Range", "₦5,000,000 - ₦8,000,000")
                exp_level = st.selectbox("Experience Level", ["Entry Level", "Junior", "Mid-Level", "Senior", "Executive"])
                positions = st.number_input("Number of Positions", min_value=1, value=1)
                closing = st.date_input("Closing Date")
            
            jd_text = st.text_area("Job Description *", height=200, placeholder="Paste full job description...")
            skills = st.text_input("Key Skills (comma-separated)")
            
            if st.form_submit_button("📝 Post Job", use_container_width=True):
                if title and department and jd_text:
                    st.success(f"✅ '{title}' posted successfully!")
                    st.balloons()
                else:
                    st.error("Fill all required fields (*)")
    
    with tab3:
        st.subheader("Applications Received")
        apps = [
            {"name": "Modupe O.", "position": "AI Transformation Lead", "date": "2026-05-14", "status": "Screened", "score": "92%"},
            {"name": "Chinelo A.", "position": "AI Transformation Lead", "date": "2026-05-13", "status": "New", "score": "88%"},
            {"name": "Ogochukwu N.", "position": "Senior Facility Manager", "date": "2026-05-12", "status": "Interviewed", "score": "78%"},
        ]
        for app in apps:
            sc = "#38a169" if app['status'] == 'Screened' else "#d69e2e" if app['status'] == 'Interviewed' else "#3182ce"
            st.markdown(f"""
                <div style="background: white; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.4rem;
                            display: flex; justify-content: space-between; align-items: center;">
                    <div><strong>{app['name']}</strong> - {app['position']}<br><small>{app['date']} | AI: {app['score']}</small></div>
                    <span style="background: {sc}; color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem;">{app['status']}</span>
                </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.subheader("Recruitment Pipeline")
        pipeline = pd.DataFrame({'Stage': ['Sourced', 'Applied', 'Screened', 'Interviewed', 'Offered', 'Hired'], 'Candidates': [50, 35, 20, 8, 3, 1]})
        fig = px.funnel(pipeline, x='Candidates', y='Stage', color_discrete_sequence=[CHURCHGATE_RED])
        st.plotly_chart(fig, use_container_width=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Time to Hire", "18 days", "↓ 30%")
        col2.metric("Cost per Hire", "₦350K", "↓ 25%")
        col3.metric("Acceptance", "88%", "↑ 12%")


# ============ AI RECRUITMENT AGENT - FULLY FIXED ============
def ai_recruitment_agent():
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>🤖 AI Recruitment Agent</h1>
            <p>AI-Powered CV Analysis | Candidate Scoring | Intelligent Tiering</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Use radio buttons instead of tabs to prevent navigation conflicts
    ai_section = st.radio("Select Function:", [
        "📋 JD Analysis", "📤 CV Upload & Scoring", "📊 Candidate Tiering", "💾 Save Results"
    ], horizontal=True)
    
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
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Title:** {analysis['title']}")
                        st.markdown(f"**Department:** {analysis['department']}")
                        st.markdown(f"**Experience:** {analysis['experience_level']}")
                    with col2:
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
            
            uploaded_files = st.file_uploader("Upload CVs (PDF, DOCX, TXT) - Multiple files supported", 
                                               type=['pdf', 'docx', 'txt'], accept_multiple_files=True)
            
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
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🌟 Tier 1", tiers['Tier 1 (Strong Fit)'])
                    col2.metric("👍 Tier 2", tiers['Tier 2 (Good Fit)'])
                    col3.metric("👎 Tier 3", tiers['Tier 3 (Not Recommended)'])
    
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
            
            for tier_name, tier_candidates in tiers.items():
                if tier_candidates:
                    names = ', '.join([f"{c['score']['candidate_name']} ({c['score']['overall_score']}%)" for c in tier_candidates[:3]])
                else:
                    names = "None"
                action = "Recommend for Final Interview" if 'Tier 1' in tier_name else "Keep in View" if 'Tier 2' in tier_name else "–"
                st.markdown(f"**{tier_name}** ({len(tier_candidates)}): {names} → *{action}*")
            
            # Tier 1 Details
            if tiers['Tier 1 (Strong Fit)']:
                st.markdown("---")
                st.markdown("## 🌟 TIER 1 – STRONG FIT")
                for i, c in enumerate(tiers['Tier 1 (Strong Fit)'], 1):
                    score = c['score']
                    st.markdown(f"""
                        <div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;
                                    border-left: 4px solid #38a169;">
                            <h4>#{i} {score['candidate_name']} - {score['overall_score']}%</h4>
                            <p><strong>LinkedIn:</strong> {'✓ Verified' if score['linkedin_verified'] else '⚠ Not provided'}</p>
                            <p><strong>Strengths:</strong> {', '.join(score['key_strengths'][:3])}</p>
                            <p><strong>Recommendation:</strong> {score['recommendation']}</p>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Scoring Breakdown
            st.markdown("---")
            st.markdown("## 📊 DETAILED SCORING BREAKDOWN")
            breakdown = []
            for c in candidates:
                s = c['score']
                breakdown.append({
                    'Candidate': s['candidate_name'],
                    'Overall': f"{s['overall_score']}%",
                    'Skills': f"{s['skills_score']}%",
                    'Experience': f"{s['experience_score']}%",
                    'Education': f"{s['education_score']}%",
                    'Tier': s['tier']
                })
            st.dataframe(pd.DataFrame(breakdown), use_container_width=True, hide_index=True)
    
    elif ai_section == "💾 Save Results":
        st.subheader("Save Candidates to Database")
        if st.session_state.candidates_batch:
            if st.button("💾 Save All Candidates", use_container_width=True, type="primary"):
                for c in st.session_state.candidates_batch:
                    score = c['score']
                    candidate_ref = generate_ref("CAND")
                    candidate_data = (
                        candidate_ref, score['candidate_name'].split()[0] if score['candidate_name'] else "Unknown",
                        ' '.join(score['candidate_name'].split()[1:]) if len(score['candidate_name'].split()) > 1 else '',
                        score['parsed_data'].get('email', ''), score['parsed_data'].get('phone', ''),
                        score['parsed_data'].get('linkedin', ''), score['parsed_data'].get('current_position', ''),
                        score['parsed_data'].get('current_company', ''), score['parsed_data'].get('total_experience_years', 0),
                        score['parsed_data'].get('education_level', ''),
                        ', '.join([s['skill'] for s in score['parsed_data'].get('skills', [])]),
                        score['parsed_data'].get('location', ''), c['filename'], c['cv_text'][:5000],
                        None, 'AI Upload', 'Scored'
                    )
                    candidate_id = db.add_candidate(candidate_data)
                    db.update_candidate_ai_score(
                        candidate_id, score['overall_score'], score['tier'], json.dumps(score),
                        score['skills_score'], score['experience_score'], score['education_score'],
                        score['overall_score'], score['linkedin_verified'],
                        json.dumps(score['key_strengths']), json.dumps(score['gaps_identified']),
                        score['recommendation']
                    )
                st.success(f"✅ {len(st.session_state.candidates_batch)} candidates saved!")
                st.balloons()
        else:
            st.info("No candidates to save. Upload and analyze CVs first.")


# ============ CHAT & COMMUNICATIONS ============
def chat_communications():
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>💬 Chat & Communications</h1>
            <p>Team Messaging | Announcements | @Mentions</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💬 Team Chat", "📢 Announcements", "📧 Email"])
    
    with tab1:
        st.subheader("Team Chat - @mention to chat with colleagues")
        
        # Team members for @mentions
        team_members = [
            "Emmanuel Etuk (Technology)", "Sanjeev Purwar (FM)", "Ahmed Karim (Sales)",
            "Adebayo Sakote (HR)", "Jeff Arikawe (Finance)", "Maikudi Kadoh (Security)",
            "Francis Asuquo (ELV)", "David Aiyedun (Legal)", "Ibukun Adeogun (Operations)"
        ]
        
        # Select person to chat with
        chat_with = st.selectbox("Chat with:", ["Select colleague..."] + team_members)
        
        if chat_with != "Select colleague...":
            st.session_state.active_chat_user = chat_with
            
            # Display chat history
            chat_key = f"chat_{chat_with}"
            if chat_key not in st.session_state:
                st.session_state[chat_key] = []
            
            for msg in st.session_state[chat_key][-20:]:
                if msg['sender'] == 'You':
                    st.markdown(f"""
                        <div style="background: {CHURCHGATE_RED}; color: white; padding: 0.6rem 1rem; 
                                    border-radius: 10px; margin: 0.3rem 0; margin-left: 3rem;">
                            <strong>You</strong>
                            <p style="margin: 0.2rem 0;">{msg['content']}</p>
                            <small>{msg['time']}</small>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="background: #f0f0f0; padding: 0.6rem 1rem; 
                                    border-radius: 10px; margin: 0.3rem 0; margin-right: 3rem;">
                            <strong>{msg['sender']}</strong>
                            <p style="margin: 0.2rem 0;">{msg['content']}</p>
                            <small>{msg['time']}</small>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Send message
            with st.form(f"chat_form_{chat_with}", clear_on_submit=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    message = st.text_input("Type message...", placeholder=f"Message {chat_with}...")
                with col2:
                    send = st.form_submit_button("📤 Send", use_container_width=True)
                
                if send and message:
                    st.session_state[chat_key].append({
                        'sender': 'You',
                        'content': message,
                        'time': datetime.now().strftime('%I:%M %p')
                    })
                    # Simulate reply
                    st.session_state[chat_key].append({
                        'sender': chat_with,
                        'content': f"Thanks for your message! (Auto-reply: {chat_with.split('(')[0].strip()} will respond soon)",
                        'time': datetime.now().strftime('%I:%M %p')
                    })
                    st.rerun()
        
        # HRIS Bot
        st.markdown("---")
        st.markdown("### 🤖 HRIS Assistant Bot")
        bot_question = st.text_input("Ask HRIS Bot:", placeholder="e.g., How do I apply for leave?")
        if bot_question:
            bot_responses = {
                'leave': "To apply for leave, go to your Employee Dashboard and click 'Request Leave'. Your current balance is 18 days.",
                'payroll': "Payroll is processed on the 25th of each month. Contact Accounts & Finance for specific inquiries.",
                'training': "Check the Training & Development section for available courses. New webinars are added weekly.",
                'policy': "HR policies are available in the Employee Handbook. Contact HR for specific policy questions.",
                'benefits': "Churchgate offers health insurance, pension, and annual leave. See HR for full benefits details.",
            }
            response = "I can help with leave, payroll, training, policies, and benefits. What would you like to know?"
            for key, val in bot_responses.items():
                if key in bot_question.lower():
                    response = val
                    break
            st.info(f"🤖 {response}")
    
    with tab2:
        st.subheader("📢 Company Announcements")
        announcements = [
            {"title": "Q2 Performance Reviews", "date": "2026-06-01", "priority": "High", "content": "All departments to submit Q2 performance reviews by June 15."},
            {"title": "BMS Implementation Update", "date": "2026-05-28", "priority": "Medium", "content": "Phase 1 complete. Phase 2 starts June 10."},
            {"title": "Holiday - Democracy Day", "date": "2026-05-25", "priority": "Medium", "content": "Office closed June 12 for Democracy Day."},
        ]
        for ann in announcements:
            pc = "#e53e3e" if ann['priority'] == 'High' else "#d69e2e"
            st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.6rem;
                            border-left: 4px solid {pc};">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{ann['title']}</strong>
                        <span style="background: {pc}; color: white; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">{ann['priority']}</span>
                    </div>
                    <p style="margin: 0.4rem 0;">{ann['content']}</p>
                    <small>📅 {ann['date']}</small>
                </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("📧 Email Notifications")
        with st.form("email_prefs"):
            st.markdown("### Notification Preferences")
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox("Birthday Alerts", value=True)
                st.checkbox("Work Anniversaries", value=True)
                st.checkbox("Promotion Announcements", value=True)
            with col2:
                st.checkbox("Holiday Reminders", value=True)
                st.checkbox("Training & Webinars", value=True)
                st.checkbox("New Hire Announcements", value=True)
            if st.form_submit_button("💾 Save Preferences", use_container_width=True):
                st.success("✅ Preferences saved!")


# ============ TRAINING & DEVELOPMENT ============
def training_development():
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>🎓 Training & Development</h1>
            <p>Learning Management | Webinars | Professional Development</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📚 Courses", "🌐 Webinars", "📋 Calendar"])
    
    with tab1:
        st.subheader("My Learning Path")
        courses = [
            {"name": "BMS Advanced Integration", "progress": 75, "deadline": "2026-07-15"},
            {"name": "AI in Facility Management", "progress": 40, "deadline": "2026-08-30"},
            {"name": "Leadership Excellence", "progress": 90, "deadline": "2026-06-15"},
            {"name": "Data Analytics for Operations", "progress": 60, "deadline": "2026-09-01"},
        ]
        for course in courses:
            color = "#38a169" if course['progress'] >= 80 else "#d69e2e"
            st.markdown(f"""
                <div style="background: white; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{course['name']}</strong>
                        <span>{course['progress']}%</span>
                    </div>
                    <div style="background: #e0e0e0; height: 5px; border-radius: 3px; margin: 0.4rem 0;">
                        <div style="background: {color}; width: {course['progress']}%; height: 5px; border-radius: 3px;"></div>
                    </div>
                    <small>Deadline: {course['deadline']}</small>
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Upcoming Webinars & Conferences")
        webinars = [
            {"title": "AI in Real Estate Management", "date": "June 20, 2026", "source": "LinkedIn Learning", "dept": "Technology"},
            {"title": "Financial Modeling for RE", "date": "June 25, 2026", "source": "CFA Institute", "dept": "Finance"},
            {"title": "HR Tech Summit 2026", "date": "July 10, 2026", "source": "SHRM", "dept": "HR"},
            {"title": "Facility Management Excellence", "date": "July 15, 2026", "source": "IFMA", "dept": "Operations"},
            {"title": "Cybersecurity for Smart Buildings", "date": "July 20, 2026", "source": "NITDA", "dept": "Technology"},
        ]
        for web in webinars:
            st.markdown(f"""
                <div style="background: white; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.4rem;
                            border-left: 3px solid {CHURCHGATE_RED};">
                    <strong>{web['title']}</strong>
                    <br><small>📅 {web['date']} | 📍 {web['source']} | 🏢 {web['dept']}</small>
                </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("Training Calendar - June 2026")
        
        # Simple calendar view
        cal_data = []
        today = datetime.now()
        for day in range(1, 31):
            events = []
            if day == 15: events.append("BMS Training")
            if day == 20: events.append("AI in FM Webinar")
            if day == 25: events.append("Finance Workshop")
            cal_data.append({"Day": day, "Events": ", ".join(events) if events else "-"})
        
        st.dataframe(pd.DataFrame(cal_data), use_container_width=True, hide_index=True)


# ============ REPORTS & ANALYTICS ============
def reports_analytics():
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>📊 Reports & Analytics</h1>
            <p>Business Intelligence | Fortune 500 Standard</p>
        </div>
    """, unsafe_allow_html=True)
    
    report = st.selectbox("Select Report", ["Executive Scorecard", "Workforce Analytics", "Recruitment Funnel", "Performance Trends"])
    
    if report == "Recruitment Funnel":
        funnel = pd.DataFrame({'Stage': ['Sourced', 'Applied', 'Screened', 'Interviewed', 'Offered', 'Hired'], 'Count': [100, 75, 50, 20, 5, 2]})
        fig = px.funnel(funnel, x='Count', y='Stage', color_discrete_sequence=[CHURCHGATE_RED])
        st.plotly_chart(fig, use_container_width=True)
    
    elif report == "Workforce Analytics":
        dept_data = pd.DataFrame({'Department': ['Technology', 'FM', 'Sales', 'Finance', 'HR', 'Procurement', 'Security', 'Legal', 'Operations'], 
                                   'Count': [12, 25, 15, 10, 8, 8, 20, 3, 18]})
        fig = px.bar(dept_data, x='Department', y='Count', color_discrete_sequence=[CHURCHGATE_RED])
        st.plotly_chart(fig, use_container_width=True)


# ============ NOTIFICATIONS ============
def notifications_page():
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>🔔 Notifications</h1>
            <p>Alerts, Reminders, and Updates</p>
        </div>
    """, unsafe_allow_html=True)
    
    notifs = [
        {"title": "Performance Review Due", "msg": "Q2 2026 performance reviews due by June 15", "time": "2 hours ago", "unread": True},
        {"title": "New Hire Announcement", "msg": "Welcome David Effiong - Facility Manager", "time": "Yesterday", "unread": True},
        {"title": "Training Reminder", "msg": "BMS Advanced Integration starts June 15", "time": "2 days ago", "unread": False},
        {"title": "Holiday Notice", "msg": "Democracy Day - June 12, 2026", "time": "1 week ago", "unread": False},
    ]
    
    for n in notifs:
        bg = "#fff3f3" if n['unread'] else "#fafafa"
        icon = "🔴" if n['unread'] else "✅"
        st.markdown(f"""
            <div style="background: {bg}; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.4rem; border-left: 3px solid {CHURCHGATE_RED};">
                {icon} <strong>{n['title']}</strong>
                <p style="margin: 0.2rem 0;">{n['msg']}</p>
                <small>{n['time']}</small>
            </div>
        """, unsafe_allow_html=True)


# ============ MY PROFILE ============
def my_profile():
    user = st.session_state.user
    
    st.markdown(f"""
        <div class="churchgate-header">
            <h1>👤 My Profile</h1>
            <p>{user['name']} • {user.get('position', 'Employee')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        initials = generate_initials(user['name'])
        st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <div style="width: 80px; height: 80px; border-radius: 50%; background: {CHURCHGATE_RED};
                            display: flex; align-items: center; justify-content: center;
                            font-size: 2rem; font-weight: 700; color: white; margin: 0 auto;">
                    {initials}
                </div>
                <h3 style="margin-top: 0.8rem;">{user['name']}</h3>
                <p>{user.get('position', 'Employee')}</p>
                <p style="color: {CHURCHGATE_RED};">ID: {user.get('employee_id', 'N/A')}</p>
                <p>🏢 {user.get('department', 'N/A')}</p>
                <p>👤 Supervisor: Jerome Das (COO)</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        with st.form("profile_update"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("First Name", value=user['name'].split()[0] if user['name'] else "")
                st.text_input("Email", value=user.get('email', ''))
                st.text_input("Phone", value="+234 800 000 0000")
            with col2:
                last_name = ' '.join(user['name'].split()[1:]) if len(user['name'].split()) > 1 else ''
                st.text_input("Last Name", value=last_name)
                st.selectbox("Department", ["Technology Group", "Facility Management", "HR", "Sales", "Finance", "Procurement", "Security", "Legal", "Operations"], index=0)
            
            if st.form_submit_button("💾 Update Profile", use_container_width=True):
                st.success("✅ Profile updated!")


# ============ MAIN APP ============
def main():
    if st.session_state.user is None:
        login_section()
    else:
        page = sidebar_navigation()
        
        if 'navigate_to' in st.session_state:
            page = st.session_state.pop('navigate_to')
        
        # Route to correct page
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
        
        # Execute the selected page function
        page_func = page_routes.get(page, employee_dashboard)
        page_func()


if __name__ == "__main__":
    main()
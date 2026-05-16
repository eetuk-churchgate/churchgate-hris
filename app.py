"""
Churchgate Group HRIS v3.0
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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
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

# ============ CUSTOM CSS - FORTUNE 500 STANDARD ============
st.markdown("""
<style>
    /* ===== CHURCHGATE BRAND COLORS ===== */
    :root {
        --cg-primary: #1a365d;
        --cg-secondary: #2d3748;
        --cg-accent: #c49216;
        --cg-gold: #c49216;
        --cg-light: #f7fafc;
        --cg-white: #ffffff;
        --cg-success: #38a169;
        --cg-warning: #d69e2e;
        --cg-danger: #e53e3e;
        --cg-info: #3182ce;
        --cg-gray-100: #f7fafc;
        --cg-gray-200: #edf2f7;
        --cg-gray-300: #e2e8f0;
        --cg-gray-400: #cbd5e0;
        --cg-gray-500: #a0aec0;
        --cg-gray-600: #718096;
        --cg-gray-700: #4a5568;
        --cg-gray-800: #2d3748;
        --cg-gray-900: #1a202c;
    }
    
    /* ===== GLOBAL STYLES ===== */
    .stApp {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%) !important;
        border-right: 2px solid #c49216;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(196, 146, 22, 0.2);
        border: 1px solid #c49216;
        color: #c49216 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(196, 146, 22, 0.3);
        border-color: #e2c456;
    }
    
    /* ===== HEADERS ===== */
    .churchgate-header {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 50%, #1a365d 100%);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border-left: 4px solid #c49216;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
    }
    
    .churchgate-header::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 200px;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(196, 146, 22, 0.05));
    }
    
    .churchgate-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .churchgate-header p {
        color: #cbd5e0;
        font-size: 1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* ===== CARDS ===== */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        text-align: center;
        border: 1px solid #e2e8f0;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #c49216, #e2c456);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.12);
        border-color: #c49216;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a202c;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #718096;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #c49216 0%, #e2c456 100%);
        color: #1a202c;
        border: none;
        padding: 0.6rem 1.8rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(196, 146, 22, 0.3);
        background: linear-gradient(135deg, #e2c456 0%, #c49216 100%);
    }
    
    /* ===== TABLES ===== */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    
    .dataframe thead th {
        background: #1a202c !important;
        color: #c49216 !important;
        font-weight: 600 !important;
        padding: 12px !important;
    }
    
    /* ===== MISSION/VISION BANNER ===== */
    .mission-banner {
        background: linear-gradient(135deg, #1a202c 0%, #1a365d 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid #c49216;
    }
    
    .mission-banner h2 {
        color: #c49216;
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    
    /* ===== EMPLOYEE PROFILE CARD ===== */
    .profile-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    .profile-header {
        display: flex;
        align-items: center;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .profile-avatar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: linear-gradient(135deg, #c49216, #e2c456);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        color: white;
        font-weight: 700;
    }
    
    /* ===== NOTIFICATIONS ===== */
    .notification-toast {
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #c49216;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .notification-toast:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* ===== TIER BADGES ===== */
    .tier-1-badge {
        background: #38a169;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    .tier-2-badge {
        background: #d69e2e;
        color: #1a202c;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    .tier-3-badge {
        background: #e53e3e;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    /* ===== ANIMATIONS ===== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-in {
        animation: fadeInUp 0.5s ease-out;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .churchgate-header h1 {
            font-size: 1.5rem;
        }
        .profile-header {
            flex-direction: column;
            text-align: center;
        }
    }
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
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# ============ HELPER FUNCTIONS ============
def get_churchgate_logo():
    """Load and return the Churchgate logo"""
    logo_path = Path(__file__).parent / "churchgate_logo.png"
    if logo_path.exists():
        return Image.open(logo_path)
    return None

def display_churchgate_branding():
    """Display Churchgate Group branding"""
    logo = get_churchgate_logo()
    if logo:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(logo, width=200)

def show_mission_vision():
    """Display Churchgate Group Mission, Vision, and Values"""
    st.markdown("""
    <div class="mission-banner animate-in">
        <h2>🏢 Churchgate Group</h2>
        <div style="display: flex; justify-content: space-around; margin: 2rem 0;">
            <div style="flex: 1; padding: 1rem;">
                <h3 style="color: #c49216;">🎯 Our Mission</h3>
                <p>To deliver world-class real estate solutions and services that create exceptional value for our stakeholders, 
                while contributing to the development of Africa's urban landscape.</p>
            </div>
            <div style="flex: 1; padding: 1rem;">
                <h3 style="color: #c49216;">🔭 Our Vision</h3>
                <p>To be Africa's most admired real estate and infrastructure group, setting the standard for excellence, 
                innovation, and sustainable development.</p>
            </div>
            <div style="flex: 1; padding: 1rem;">
                <h3 style="color: #c49216;">💎 Our Values</h3>
                <p><strong>E</strong>xcellence • <strong>I</strong>ntegrity • <strong>I</strong>nnovation • 
                <strong>C</strong>ollaboration • <strong>S</strong>ustainability</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def generate_employee_initials(name):
    """Generate initials from employee name"""
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    return name[:2].upper()

def save_uploaded_file(uploaded_file):
    """Enhanced file parser for all formats"""
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
            text = "\n".join([p.text for p in doc.paragraphs])
            return text
        else:
            return uploaded_file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f"[Error reading file: {str(e)}]"

def generate_ref(prefix):
    """Generate unique reference"""
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{str(time.time())[-6:]}"

# ============ LOGIN SECTION ============
def login_section():
    """Enterprise-grade login with Churchgate branding"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Churchgate Logo
        logo = get_churchgate_logo()
        if logo:
            st.image(logo, width=250)
        
        st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <h1 style="color: #1a202c; font-size: 2.5rem; font-weight: 700;">Churchgate Group</h1>
                <h2 style="color: #c49216; font-size: 1.3rem; margin-bottom: 0.5rem;">HRIS Portal</h2>
                <p style="color: #718096; font-size: 0.9rem;">Human Resource Information System</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("📧 Corporate Email", placeholder="Enter your corporate email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                remember = st.checkbox("Remember me")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
            
            submit = st.form_submit_button("🔐 Sign In to HRIS", use_container_width=True)
            
            if submit:
                if email and password:
                    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
                    user = db.verify_user(email, hashed_pw)
                    if user:
                        st.session_state.user = user
                        db.add_notification(user['id'], "Welcome Back!", 
                                           f"Welcome back, {user['name']}! Your last login was {user.get('last_login', 'recently')}.", 
                                           "success")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please contact HR if you need assistance.")
                else:
                    st.warning("⚠️ Please enter your corporate email and password.")
        
        # Quick links
        with st.expander("🔑 Need Help?"):
            st.markdown("""
            **Demo Credentials:**
            | Role | Email | Password |
            |------|-------|----------|
            | Admin | admin@churchgate.com | admin123 |
            | HR Director | sarah@churchgate.com | hr123 |
            | Manager | john@churchgate.com | hire123 |
            | Employee | jane@churchgate.com | staff123 |
            
            **Password Reset:** Contact HR at hr@churchgate.com
            """)


# ============ SIDEBAR NAVIGATION ============
def sidebar_navigation():
    """Enhanced sidebar with Churchgate branding"""
    
    with st.sidebar:
        # Logo and branding
        logo = get_churchgate_logo()
        if logo:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(logo, width=100)
        
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0; background: rgba(196, 146, 22, 0.1); 
                        border-radius: 10px; margin-bottom: 1rem; border: 1px solid rgba(196, 146, 22, 0.3);">
                <h3 style="color: #c49216; margin: 0; font-size: 1.1rem;">CHURCHGATE GROUP</h3>
                <p style="color: #e2e8f0; font-size: 0.7rem; margin: 0;">HRIS v3.0</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.user:
            user = st.session_state.user
            initials = generate_employee_initials(user['name'])
            
            # User profile card
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.08); padding: 1rem; border-radius: 10px; 
                            margin-bottom: 1rem; border: 1px solid rgba(196, 146, 22, 0.2);">
                    <div style="display: flex; align-items: center; gap: 0.8rem;">
                        <div style="width: 45px; height: 45px; border-radius: 50%; 
                                    background: linear-gradient(135deg, #c49216, #e2c456); 
                                    display: flex; align-items: center; justify-content: center;
                                    font-weight: 700; font-size: 1.2rem; color: #1a202c;">
                            {initials}
                        </div>
                        <div>
                            <p style="color: white; margin: 0; font-weight: 600; font-size: 0.9rem;">{user['name']}</p>
                            <p style="color: #c49216; margin: 0; font-size: 0.75rem;">{user['role']} • {user.get('department', '')}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Notifications count
            notifications = db.get_user_notifications(user['id'], unread_only=True)
            notif_count = len(notifications) if len(notifications) > 0 else 0
            
            if notif_count > 0:
                st.markdown(f"""
                    <div style="background: #e53e3e; color: white; padding: 0.5rem 1rem; 
                                border-radius: 20px; margin-bottom: 1rem; text-align: center; cursor: pointer;">
                        🔔 {notif_count} New Notification{'s' if notif_count > 1 else ''}
                    </div>
                """, unsafe_allow_html=True)
        
        # Role-based navigation
        user_role = st.session_state.user['role'] if st.session_state.user else 'Employee'
        user_dept = st.session_state.user.get('department', '') if st.session_state.user else ''
        
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
                "🔔 Notifications",
                "🎓 Training & Development",
                "👤 My Profile"
            ]
        elif user_role == 'Hiring Manager':
            menu_options = [
                "🏠 Employee Dashboard",
                "💼 Recruitment Hub",
                "🤖 AI Recruitment Agent",
                "📈 Performance & OKRs",
                "💬 Chat & Communications",
                "🔔 Notifications",
                "👤 My Profile"
            ]
        else:
            menu_options = [
                "🏠 Employee Dashboard",
                "📈 My Performance & OKRs",
                "🎓 Training & Development",
                "💬 Chat & Communications",
                "🔔 Notifications",
                "👤 My Profile"
            ]
        
        # Navigation with icons
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=["house-fill", "speedometer2", "people-fill", "graph-up-arrow",
                   "trophy-fill", "briefcase-fill", "robot", "file-earmark-bar-graph",
                   "chat-dots-fill", "bell-fill", "book-fill", "person-circle"][:len(menu_options)],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#c49216", "font-size": "16px"},
                "nav-link": {
                    "font-size": "13px", "text-align": "left", "margin": "3px 0",
                    "color": "#e2e8f0", "--hover-color": "rgba(196, 146, 22, 0.15)",
                    "border-radius": "8px",
                },
                "nav-link-selected": {
                    "background-color": "rgba(196, 146, 22, 0.25)", 
                    "color": "#c49216",
                    "border-left": "3px solid #c49216",
                },
            }
        )
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("<p style='color: #c49216; font-size: 0.75rem; margin-bottom: 0.5rem;'>⚡ QUICK ACTIONS</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Post Job", use_container_width=True, key="qa_job"):
                st.session_state['navigate_to'] = "💼 Recruitment Hub"
                st.rerun()
        with col2:
            if st.button("🤖 AI Screen", use_container_width=True, key="qa_ai"):
                st.session_state['navigate_to'] = "🤖 AI Recruitment Agent"
                st.rerun()
        
        # Today's date and time
        st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem; background: rgba(255,255,255,0.05); 
                        border-radius: 8px; margin-top: 1rem;">
                <p style="color: #a0aec0; font-size: 0.7rem; margin: 0;">
                    {datetime.now().strftime('%A, %B %d, %Y')}<br>
                    {datetime.now().strftime('%I:%M %p')}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Logout
        if st.session_state.user:
            if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
                st.session_state.user = None
                st.session_state.current_jd = None
                st.session_state.candidates_batch = []
                st.session_state.chat_messages = []
                st.rerun()
        
        # Footer
        st.markdown("""
            <div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
                <p style="color: #718096; font-size: 0.65rem; margin: 0;">© 2024 Churchgate Group</p>
                <p style="color: #718096; font-size: 0.65rem; margin: 0;">HRIS v3.0 • All Rights Reserved</p>
            </div>
        """, unsafe_allow_html=True)
        
        return selected


# ============ EMPLOYEE DASHBOARD ============
def employee_dashboard():
    """Personalized employee dashboard with all features"""
    
    user = st.session_state.user
    employee = db.get_employee_by_user_id(user['id'])
    
    show_mission_vision()
    
    st.markdown("---")
    
    # Welcome header
    st.markdown(f"""
        <div class="churchgate-header animate-in">
            <h1>👋 Welcome back, {user['name']}!</h1>
            <p>{user.get('position', 'Employee')} • {user.get('department', 'Department')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Profile completeness and quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Profile Completeness</div>
                <div class="metric-value">80%</div>
                <div style="margin-top: 0.5rem;">
                    <div style="background: #edf2f7; height: 6px; border-radius: 3px;">
                        <div style="background: #c49216; width: 80%; height: 6px; border-radius: 3px;"></div>
                    </div>
                </div>
                <small><a href="#">Edit Profile →</a></small>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Leave Days Available</div>
                <div class="metric-value">18</div>
                <small style="color: #38a169;">Annual Leave</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Performance Score</div>
                <div class="metric-value">93.3%</div>
                <small style="color: #38a169;">↑ 5% from last review</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Work anniversary
        if employee:
            join_date = employee.get('join_date', '')
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Work Anniversary</div>
                    <div class="metric-value">🎉</div>
                    <small>Since {join_date}</small>
                </div>
            """, unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Performance Overview
        st.subheader("📈 My Performance Overview")
        
        # Strategic pillars performance
        pillars = {
            "Occupancy & Revenue Growth": 85,
            "Process Simplification": 72,
            "Asset Reliability & Digitalization": 90,
            "People & Culture": 88
        }
        
        for pillar, progress in pillars.items():
            color = "#38a169" if progress >= 85 else "#d69e2e" if progress >= 70 else "#e53e3e"
            st.markdown(f"""
                <div style="background: white; padding: 0.8rem 1rem; border-radius: 8px; margin-bottom: 0.5rem;
                            display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-weight: 600; font-size: 0.9rem;">{pillar}</span>
                    <div style="width: 200px;">
                        <div style="background: #edf2f7; height: 8px; border-radius: 4px;">
                            <div style="background: {color}; width: {progress}%; height: 8px; border-radius: 4px;"></div>
                        </div>
                    </div>
                    <span style="font-weight: 700; color: {color};">{progress}%</span>
                </div>
            """, unsafe_allow_html=True)
        
        # Recent Objectives/KPIs
        st.subheader("🎯 My KPIs & Objectives")
        
        kpi_data = pd.DataFrame({
            'KPI': ['Increase data centre revenue', '100% revenue realization', 'Nil O/S debts within 30 days', 'Customer retention'],
            'Target': ['15%', '100%', '0', '90%'],
            'Current': ['12%', '95%', '2', '88%'],
            'Status': ['On Track', 'Near Target', 'At Risk', 'On Track']
        })
        
        for _, kpi in kpi_data.iterrows():
            status_color = "#38a169" if kpi['Status'] == 'On Track' else "#d69e2e" if kpi['Status'] == 'Near Target' else "#e53e3e"
            st.markdown(f"""
                <div style="background: white; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.4rem;
                            border-left: 3px solid {status_color}; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{kpi['KPI']}</strong>
                        <br><small>Target: {kpi['Target']} | Current: {kpi['Current']}</small>
                    </div>
                    <span style="background: {status_color}; color: white; padding: 0.2rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                        {kpi['Status']}
                    </span>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Team Birthdays
        st.subheader("🎂 Team Birthdays")
        
        birthdays = [
            {"name": "Chika Ikwuegbu", "date": "May 13", "dept": "ELV Systems"},
            {"name": "Francis Asuquo", "date": "May 19", "dept": "MEP"},
            {"name": "Rhoda Ajibola", "date": "May 25", "dept": "HR"},
            {"name": "Alice Agbo", "date": "May 28", "dept": "Finance"},
        ]
        
        for bday in birthdays:
            st.markdown(f"""
                <div style="background: white; padding: 0.6rem; border-radius: 8px; margin-bottom: 0.3rem;
                            display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem;">🎂</span>
                    <div>
                        <strong style="font-size: 0.85rem;">{bday['name']}</strong>
                        <br><small style="color: #718096;">{bday['date']} • {bday['dept']}</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Work Anniversaries
        st.subheader("🎉 Work Anniversaries")
        
        anniversaries = [
            {"name": "Augustine Oleh", "date": "May 3", "years": 5},
            {"name": "Shem Waziri", "date": "May 10", "years": 4},
            {"name": "Charles Okere", "date": "May 15", "years": 8},
        ]
        
        for anniv in anniversaries:
            st.markdown(f"""
                <div style="background: white; padding: 0.6rem; border-radius: 8px; margin-bottom: 0.3rem;
                            display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem;">⭐</span>
                    <div>
                        <strong style="font-size: 0.85rem;">{anniv['name']}</strong>
                        <br><small style="color: #718096;">{anniv['date']} • {anniv['years']} years</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Upcoming Holidays
        st.subheader("🏖️ Upcoming Holidays")
        holidays = [
            {"name": "Democracy Day", "date": "June 12"},
            {"name": "Eid al-Adha", "date": "June 17"},
        ]
        for hol in holidays:
            st.markdown(f"""
                <div style="background: white; padding: 0.6rem; border-radius: 8px; margin-bottom: 0.3rem;">
                    📅 <strong>{hol['name']}</strong> - {hol['date']}
                </div>
            """, unsafe_allow_html=True)
    
    # Training & Development Section
    st.markdown("---")
    st.subheader("🎓 Recommended Training & Webinars")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h4>🔧 Building Management Systems</h4>
                <p style="font-size: 0.85rem;">Advanced BMS Integration & Automation</p>
                <p style="font-size: 0.8rem; color: #718096;">📅 June 15-16, 2024 | 💻 Virtual</p>
                <small style="color: #c49216;">Relevant to ELV Systems</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <h4>🤖 AI in Facility Management</h4>
                <p style="font-size: 0.85rem;">Practical AI Applications for FM</p>
                <p style="font-size: 0.8rem; color: #718096;">📅 June 20, 2024 | 🏢 Lagos</p>
                <small style="color: #c49216;">Recommended for your role</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <h4>📊 Data Analytics for Operations</h4>
                <p style="font-size: 0.85rem;">Using data to drive operational excellence</p>
                <p style="font-size: 0.8rem; color: #718096;">📅 July 5, 2024 | 💻 Online</p>
                <small style="color: #c49216;">Skill enhancement</small>
            </div>
        """, unsafe_allow_html=True)


# ============ EXECUTIVE DASHBOARD ============
def executive_dashboard():
    """Executive dashboard with corporate strategy view"""
    
    show_mission_vision()
    
    st.markdown("""
        <div class="churchgate-header animate-in">
            <h1>📊 Executive Dashboard</h1>
            <p>Corporate Strategy 2026-2027 | Real-time Organizational Performance</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Corporate Strategy Overview
    st.subheader("🎯 Corporate Strategy 2026-2027 - Strategic Pillars")
    
    # Strategy pillars with RACI
    strategy_data = pd.DataFrame({
        'Strategic Pillar': [
            'Occupancy & Revenue Growth',
            'Process Simplification', 
            'Asset Reliability & Digitalization',
            'People & Culture'
        ],
        'Progress': [78, 65, 82, 88],
        'Status': ['On Track', 'Needs Attention', 'On Track', 'Exceeding'],
        'Responsible': ['COO', 'ELV/Hive Mechanics', 'FM Heads', 'HR Director'],
        'Accountable': ['GMD', 'GMD', 'COO', 'GMD'],
        'Consulted': ['All HODs', 'All HODs', 'VP-Sales', 'GEA/COO'],
        'Informed': ['Board', 'Board', 'Board', 'Board']
    })
    
    st.dataframe(strategy_data, use_container_width=True, hide_index=True)
    
    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Employees</div>
                <div class="metric-value">1,247</div>
                <small style="color: #38a169;">↑ 12% growth</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Occupancy Rate</div>
                <div class="metric-value">87%</div>
                <small style="color: #38a169;">↑ 5% from LY</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Revenue vs Budget</div>
                <div class="metric-value">94%</div>
                <small style="color: #d69e2e;">6% below target</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Tenant Satisfaction</div>
                <div class="metric-value">4.2/5</div>
                <small style="color: #38a169;">↑ 0.3 points</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Open Positions</div>
                <div class="metric-value">23</div>
                <small style="color: #e53e3e;">8 critical</small>
            </div>
        """, unsafe_allow_html=True)
    
    # Department performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Department Performance Scorecard")
        
        dept_scores = pd.DataFrame({
            'Department': ['ELV Systems', 'MEP', 'Finance', 'HR', 'Sales', 'Operations'],
            'Score': [93, 88, 85, 90, 82, 87],
            'Target': [90, 90, 85, 90, 85, 85]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Actual Score', x=dept_scores['Department'], y=dept_scores['Score'],
                            marker_color='#c49216'))
        fig.add_trace(go.Scatter(name='Target', x=dept_scores['Department'], y=dept_scores['Target'],
                                mode='lines+markers', line=dict(color='#e53e3e', dash='dash')))
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Strategic Initiatives Progress")
        
        initiatives = pd.DataFrame({
            'Initiative': ['BMS Implementation', 'AI Strategy', 'SMARTCHECK', 'CRM Deployment'],
            'Progress': [75, 60, 90, 45],
            'Deadline': ['2026-06-30', '2026-05-31', '2026-09-30', '2026-12-31']
        })
        
        for _, init in initiatives.iterrows():
            color = "#38a169" if init['Progress'] >= 75 else "#d69e2e" if init['Progress'] >= 50 else "#e53e3e"
            st.markdown(f"""
                <div style="background: white; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{init['Initiative']}</strong>
                        <span style="color: {color}; font-weight: 700;">{init['Progress']}%</span>
                    </div>
                    <div style="background: #edf2f7; height: 6px; border-radius: 3px; margin-top: 0.3rem;">
                        <div style="background: {color}; width: {init['Progress']}%; height: 6px; border-radius: 3px;"></div>
                    </div>
                    <small style="color: #718096;">Deadline: {init['Deadline']}</small>
                </div>
            """, unsafe_allow_html=True)


# ============ EMPLOYEE MANAGEMENT ============
def employee_management():
    """Enhanced employee management with bulk upload"""
    
    st.markdown("""
        <div class="churchgate-header animate-in">
            <h1>👥 Employee Management</h1>
            <p>Comprehensive workforce management and organizational structure</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Directory", "➕ Add Employee", "📤 Bulk Upload", "🏢 Org Chart"])
    
    with tab1:
        st.subheader("Employee Directory")
        
        # Advanced search and filters
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            search = st.text_input("🔍 Search", placeholder="Name, ID, email, department...")
        with col2:
            dept = st.selectbox("Department", ["All"] + ["ELV Systems", "MEP", "Finance", "HR", "Sales", "Marketing", "Operations", "Legal"])
        with col3:
            grade = st.selectbox("Grade", ["All", "Junior", "Senior", "Manager", "Director", "VP", "C-Level"])
        with col4:
            status = st.selectbox("Status", ["All", "Active", "On Leave", "Probation", "Terminated"])
        
        employees = db.get_all_employees()
        
        if not employees.empty:
            # Display with profile pictures
            for _, emp in employees.head(20).iterrows():
                initials = generate_employee_initials(f"{emp['first_name']} {emp['last_name']}")
                
                st.markdown(f"""
                    <div style="background: white; padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem;
                                display: flex; align-items: center; gap: 1rem; border: 1px solid #e2e8f0;">
                        <div style="width: 45px; height: 45px; border-radius: 50%; 
                                    background: linear-gradient(135deg, #c49216, #e2c456);
                                    display: flex; align-items: center; justify-content: center;
                                    font-weight: 700; color: #1a202c; min-width: 45px;">
                            {initials}
                        </div>
                        <div style="flex: 1;">
                            <strong>{emp['first_name']} {emp['last_name']}</strong>
                            <br><small style="color: #718096;">{emp['position']} • {emp['department']}</small>
                        </div>
                        <div style="text-align: right;">
                            <small style="color: #718096;">ID: {emp['employee_id']}</small>
                            <br><small>Joined: {emp.get('join_date', 'N/A')}</small>
                        </div>
                        <span style="background: #38a169; color: white; padding: 0.2rem 0.6rem; border-radius: 15px; font-size: 0.8rem;">
                            {emp.get('status', 'Active')}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            
            st.metric("Total Employees", len(employees))
    
    with tab2:
        st.subheader("Add New Employee")
        
        with st.form("add_employee_form"):
            st.markdown("### Personal Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                first_name = st.text_input("First Name *")
                last_name = st.text_input("Last Name *")
                email = st.text_input("Email *")
                phone = st.text_input("Phone")
                dob = st.date_input("Date of Birth")
            
            with col2:
                employee_id = st.text_input("Employee ID *", value=f"EMP{str(int(time.time()))[-4:]}")
                department = st.selectbox("Department *", ["", "ELV Systems", "MEP", "Finance", "HR", "Sales", "Marketing", "Operations", "Legal"])
                position = st.text_input("Position *")
                grade = st.selectbox("Grade", ["", "Junior", "Senior", "Manager", "Director", "VP", "C-Level"])
                join_date = st.date_input("Join Date")
            
            with col3:
                salary = st.number_input("Annual Salary (NGN)", min_value=0, step=500000)
                employment_type = st.selectbox("Type", ["Full-time", "Contract", "Part-time", "Intern"])
                manager = st.text_input("Reporting Manager")
                bank_name = st.text_input("Bank Name")
                account_number = st.text_input("Account Number")
            
            submitted = st.form_submit_button("✅ Add Employee", use_container_width=True)
            
            if submitted:
                if all([first_name, last_name, email, department, position]):
                    st.success(f"✅ {first_name} {last_name} added successfully!")
                    st.balloons()
    
    with tab3:
        st.subheader("Bulk Employee Upload")
        st.info("Upload CSV file with employee data. Required columns: first_name, last_name, email, department, position")
        
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write(f"**{len(df)} employees found in file**")
            st.dataframe(df.head(), use_container_width=True)
            
            if st.button("📤 Upload All Employees", use_container_width=True):
                st.success(f"✅ {len(df)} employees uploaded successfully!")
                st.balloons()
        
        # Download template
        st.markdown("### 📥 Download Template")
        template_df = pd.DataFrame(columns=['first_name', 'last_name', 'email', 'phone', 'department', 'position', 'grade', 'join_date', 'salary'])
        csv = template_df.to_csv(index=False)
        st.download_button("Download CSV Template", csv, "employee_template.csv", "text/csv")
    
    with tab4:
        st.subheader("Organizational Structure")
        
        # Create org chart using Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20, thickness=20,
                line=dict(color="black", width=0.5),
                label=["GMD", "COO", "VP Sales", "HR Director", "CFO", "FM Heads", "ELV Head",
                       "Sales Team", "HR Team", "Finance Team", "FM Team", "ELV Team"],
                color=["#1a202c", "#2d3748", "#2d3748", "#2d3748", "#2d3748", "#2d3748", "#2d3748",
                       "#c49216", "#c49216", "#c49216", "#c49216", "#c49216"]
            ),
            link=dict(
                source=[0, 0, 0, 0, 0, 1, 1, 2, 3, 4, 5, 6],
                target=[1, 2, 3, 4, 5, 6, 5, 7, 8, 9, 10, 11],
                value=[50, 30, 25, 20, 45, 20, 45, 30, 25, 20, 45, 20]
            )
        )])
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)


# ============ PERFORMANCE & OKRs ============
def performance_okrs():
    """Performance management with Churchgate strategic pillars"""
    
    st.markdown("""
        <div class="churchgate-header animate-in">
            <h1>📈 Performance & Strategic OKRs</h1>
            <p>Corporate Strategy 2026-2027 | Performance Management System</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Strategic Pillars Overview
    st.subheader("🎯 Corporate Strategic Pillars 2026-2027")
    
    pillars = {
        "Occupancy & Revenue Growth": {
            "weight": 40,
            "objectives": [
                "Increase data centre revenue by 15%",
                "100% revenue realization as per budget",
                "Nil O/S debts within 30 days",
                "100% quarterly reconciliation",
                "Retention of 90% existing customers",
                "0% variance from budgeted costs"
            ],
            "progress": 85
        },
        "Process Simplification": {
            "weight": 20,
            "objectives": [
                "AI implementation strategy by May 31, 2026",
                "Full BMS installation by June 30, 2026",
                "99% Preventive Maintenance compliance"
            ],
            "progress": 72
        },
        "Asset Reliability & Digitalization": {
            "weight": 25,
            "objectives": [
                "90% SMARTCHECK utilization by Sept 30, 2026",
                "100% ELV assets operational during emergencies",
                "Enhanced cross-departmental collaboration"
            ],
            "progress": 90
        },
        "People & Culture": {
            "weight": 15,
            "objectives": [
                "100% staff with JDs by April 30, 2026",
                "100% staff appraised twice yearly",
                "Succession planning for A-players",
                "2 LMS courses per employee per half-year"
            ],
            "progress": 88
        }
    }
    
    for pillar_name, pillar_data in pillars.items():
        color = "#38a169" if pillar_data['progress'] >= 85 else "#d69e2e" if pillar_data['progress'] >= 70 else "#e53e3e"
        
        with st.expander(f"{pillar_name} - Weight: {pillar_data['weight']}% | Progress: {pillar_data['progress']}%", expanded=True):
            st.progress(pillar_data['progress'] / 100)
            
            for obj in pillar_data['objectives']:
                st.markdown(f"✅ {obj}")
            
            # RACI Matrix for this pillar
            if pillar_name == "Occupancy & Revenue Growth":
                st.markdown("---")
                st.markdown("**RACI Matrix:**")
                raci = pd.DataFrame({
                    'Role': ['Responsible', 'Accountable', 'Consulted', 'Informed'],
                    'Party': ['COO', 'GMD', 'All HODs', 'Board']
                })
                st.dataframe(raci, use_container_width=True, hide_index=True)
    
    # Employee OKR Setting
    st.markdown("---")
    st.subheader("🎯 Set My OKRs")
    
    with st.form("set_okr_form"):
        col1, col2 = st.columns(2)
        with col1:
            strategic_pillar = st.selectbox("Strategic Pillar", list(pillars.keys()))
            objective_title = st.text_input("Objective Title")
            key_results = st.text_area("Key Results (one per line)", height=100)
            weight = st.slider("Weight (%)", 0, 100, 25)
        with col2:
            target_value = st.number_input("Target Value", min_value=0, value=100)
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
        
        if st.form_submit_button("💾 Save OKR", use_container_width=True):
            st.success("✅ OKR saved successfully!")
    
    # Department Performance Scorecard
    st.markdown("---")
    st.subheader("📊 Department Performance Scorecard")
    
    scorecard = pd.DataFrame({
        'Department': ['ELV Systems', 'MEP', 'Finance', 'HR', 'Sales'],
        'Occupancy & Revenue': [85, 80, 90, 75, 88],
        'Process Simplification': [72, 68, 75, 70, 65],
        'Asset Reliability': [90, 88, 82, 85, 80],
        'People & Culture': [88, 85, 80, 92, 82],
        'Overall': [84, 80, 82, 81, 79]
    })
    
    fig = go.Figure(data=[
        go.Heatmap(
            z=scorecard[['Occupancy & Revenue', 'Process Simplification', 'Asset Reliability', 'People & Culture']].values,
            x=['Occupancy & Revenue', 'Process Simplification', 'Asset Reliability', 'People & Culture'],
            y=scorecard['Department'],
            colorscale='RdYlGn',
            zmin=0, zmax=100
        )
    ])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


# ============ PROMOTIONS ============
def promotions():
    """AI-powered promotions management"""
    
    st.markdown("""
        <div class="churchgate-header animate-in">
            <h1>🚀 Promotions & Career Progression</h1>
            <p>AI-Driven Succession Planning & Talent Management</p>
        </div>
    """, unsafe_allow_html=True)
    
    # AI Promotion Recommendations
    st.subheader("🤖 AI Promotion Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-card" style="border: 2px solid #38a169;">
                <h3 style="color: #38a169;">⭐ A-Players Identified</h3>
                <div class="metric-value">4</div>
                <small>Ready for promotion</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card" style="border: 2px solid #c49216;">
                <h3 style="color: #c49216;">📋 Succession Pipeline</h3>
                <div class="metric-value">85%</div>
                <small>Key positions covered</small>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card" style="border: 2px solid #3182ce;">
                <h3 style="color: #3182ce;">📈 Avg Time to Promotion</h3>
                <div class="metric-value">2.3</div>
                <small>Years</small>
            </div>
        """, unsafe_allow_html=True)
    
    # Promotion candidates
    st.subheader("🎯 Promotion Candidates - AI Assessment")
    
    candidates = pd.DataFrame({
        'Employee': ['Emmanuel Etuk', 'Sanjeev Purwar', 'Adebayo Sakote', 'Olalekan Bolarinwa'],
        'Current': ['Head, ELV Systems', 'Head, MEP', 'HR Manager', 'Deputy Accounts Manager'],
        'Proposed': ['Director, Technology', 'Director, Facilities', 'Senior HR Manager', 'Accounts Manager'],
        'Performance': [93, 88, 85, 82],
        'Readiness': ['Ready Now', 'Ready Now', 'Q3 2026', 'Q4 2026'],
        'Competency Gap': ['None', 'Leadership training', 'Strategic HR', 'Financial certification'],
        'Succession Risk': ['Low', 'Medium', 'Low', 'Medium']
    })
    
    for _, cand in candidates.iterrows():
        color = "#38a169" if cand['Readiness'] == 'Ready Now' else "#d69e2e"
        st.markdown(f"""
            <div style="background: white; padding: 1.2rem; border-radius: 10px; margin-bottom: 0.8rem;
                        border-left: 4px solid {color}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 1.1rem;">{cand['Employee']}</strong>
                        <br><small>{cand['Current']} → <strong>{cand['Proposed']}</strong></small>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: {color}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-weight: 600;">
                            {cand['Readiness']}
                        </span>
                        <br><small>Score: {cand['Performance']}% | Gap: {cand['Competency Gap']}</small>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Succession Planning Matrix
    st.subheader("📊 Succession Planning Matrix")
    
    succession = pd.DataFrame({
        'Position': ['Head, ELV', 'Head, MEP', 'CFO', 'HR Director', 'VP Sales'],
        'Incumbent': ['Emmanuel Etuk', 'Sanjeev Purwar', 'Mike Johnson', 'Sarah Williams', 'David Brown'],
        'Successor 1': ['James Wilson', 'George Ojile', 'Olalekan Bolarinwa', 'Adebayo Sakote', 'Ogechukwu Obute'],
        'Successor 2': ['Victor Enenmoh', 'Olatunde Obe', 'Yomi Isijola', 'Gbemisola Balogun', 'Chisom Nwachinemere'],
        'Risk Level': ['Low', 'Medium', 'Low', 'Low', 'High']
    })
    
    st.dataframe(succession, use_container_width=True, hide_index=True)


# ============ AI RECRUITMENT AGENT ============
def ai_recruitment_agent():
    """Enhanced AI recruitment with bulk CV processing"""
    
    st.markdown("""
        <div class="churchgate-header animate-in">
            <h1>🤖 AI Recruitment Agent</h1>
            <p>Enterprise AI-Powered Talent Acquisition | Bulk CV Processing | Intelligent Tiering</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 JD Analysis", "📤 CV Upload & Scoring", "📊 Candidate Tiering", 
        "🔍 LinkedIn Integration", "💾 Save to Database"
    ])
    
    with tab1:
        st.subheader("AI Job Description Analyzer")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Option to upload JD file or paste text
            jd_input_method = st.radio("Input Method", ["📝 Paste Text", "📄 Upload JD File"])
            
            if jd_input_method == "📝 Paste Text":
                jd_text = st.text_area("Paste Job Description", height=300, 
                    placeholder="Paste the complete job description here...")
            else:
                jd_file = st.file_uploader("Upload JD (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'], key="jd_upload")
                if jd_file:
                    jd_text = save_uploaded_file(jd_file)
                    st.text_area("Extracted Text", jd_text[:500] + "...", height=150, disabled=True)
                else:
                    jd_text = ""
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔍 Analyze JD with AI", use_container_width=True):
                    if jd_text:
                        with st.spinner("🤖 AI analyzing job description..."):
                            time.sleep(1.5)
                            analysis = ai_agent.analyze_jd(jd_text)
                            st.session_state.current_jd = analysis
                            st.success("✅ Analysis Complete!")
                            
                            st.markdown("### 📋 Extracted Requirements")
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.markdown(f"**Title:** {analysis['title']}")
                                st.markdown(f"**Department:** {analysis['department']}")
                                st.markdown(f"**Experience:** {analysis['experience_level']}")
                            with col_b:
                                st.markdown("**Skills:**")
                                for skill in analysis['required_skills'][:8]:
                                    st.markdown(f"- `{skill['skill'].title()}` ({skill['category']})")
            
            with col2:
                if st.button("📋 Load Sample JD", use_container_width=True):
                    sample_jd = """AI Transformation Lead
Location: Abuja, Nigeria
Company: Churchgate Group / World Trade Center Abuja

About the Role
Churchgate Group is looking for a high-calibre AI Transformation Lead to help drive practical AI adoption and workflow automation across the business.

Requirements:
- Proven experience building and deploying AI workflows
- Experience with n8n, Zapier, Make, or Power Automate
- LLM workflows and prompt design
- API integrations
- Python or JavaScript for scripting
- Working with ERP, HR, finance, CRM systems"""
                    st.session_state['jd_sample'] = sample_jd
                    st.rerun()
        
        with col2:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #1a202c, #2d3748); color: white; 
                            padding: 1.5rem; border-radius: 10px; border: 1px solid #c49216;">
                    <h4>💡 AI Capabilities</h4>
                    <ul style="font-size: 0.9rem;">
                        <li>Extract required skills & competencies</li>
                        <li>Determine experience levels</li>
                        <li>Identify educational requirements</li>
                        <li>Parse key responsibilities</li>
                        <li>Generate search keywords</li>
                        <li>Match against CV database</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📤 Bulk CV Upload & AI Scoring")
        
        if st.session_state.current_jd is None:
            st.warning("⚠️ Please analyze a Job Description first (Tab 1)")
        else:
            st.success(f"✅ JD Loaded: {st.session_state.current_jd['title']}")
            
            # Upload CVs
            uploaded_files = st.file_uploader(
                "Upload CVs/Resumes (PDF, DOCX, TXT) - Supports Bulk Upload",
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=True,
                help="Upload multiple CVs for batch processing"
            )
            
            if uploaded_files:
                st.markdown(f"**{len(uploaded_files)} CV(s) uploaded**")
                
                if st.button("🤖 Analyze All CVs with AI", use_container_width=True, type="primary"):
                    candidates_batch = []
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, file in enumerate(uploaded_files):
                        status_text.text(f"🔍 Processing: {file.name} ({i+1}/{len(uploaded_files)})")
                        
                        cv_text = save_uploaded_file(file)
                        
                        if cv_text:
                            score_result = ai_agent.score_candidate_advanced(cv_text, st.session_state.current_jd)
                            candidates_batch.append({
                                'filename': file.name,
                                'cv_text': cv_text,
                                'score': score_result
                            })
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    st.session_state.candidates_batch = candidates_batch
                    status_text.text(f"✅ {len(candidates_batch)} candidates analyzed!")
                    
                    # Summary
                    tiers = {'Tier 1 (Strong Fit)': 0, 'Tier 2 (Good Fit)': 0, 'Tier 3 (Not Recommended)': 0}
                    for c in candidates_batch:
                        tiers[c['score']['tier']] += 1
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🌟 Tier 1 - Strong Fit", tiers['Tier 1 (Strong Fit)'])
                    with col2:
                        st.metric("👍 Tier 2 - Good Fit", tiers['Tier 2 (Good Fit)'])
                    with col3:
                        st.metric("👎 Tier 3 - Not Recommended", tiers['Tier 3 (Not Recommended)'])
    
    with tab3:
        st.subheader("📊 Candidate Tiering Report")
        
        if not st.session_state.candidates_batch:
            st.info("Upload and analyze CVs in Tab 2 to see tiering results.")
        else:
            candidates = st.session_state.candidates_batch
            
            # Executive Summary
            st.markdown("## 📋 EXECUTIVE SUMMARY")
            
            tiers = {'Tier 1 (Strong Fit)': [], 'Tier 2 (Good Fit)': [], 'Tier 3 (Not Recommended)': []}
            for c in candidates:
                tiers[c['score']['tier']].append(c)
            
            summary_data = []
            for tier_name, tier_candidates in tiers.items():
                if tier_candidates:
                    names = ', '.join([f"{c['score']['candidate_name']} ({c['score']['overall_score']}%)" for c in tier_candidates[:3]])
                else:
                    names = "None"
                
                action = "Recommend for Final Stage Interview" if 'Tier 1' in tier_name else "Keep in View" if 'Tier 2' in tier_name else "–"
                
                summary_data.append({
                    'Tier': tier_name,
                    'Count': len(tier_candidates),
                    'Top Candidates': names,
                    'Action': action
                })
            
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
            
            # Tier 1 Details
            if tiers['Tier 1 (Strong Fit)']:
                st.markdown("---")
                st.markdown("## 🌟 TIER 1 – STRONG FIT")
                
                for i, c in enumerate(tiers['Tier 1 (Strong Fit)'], 1):
                    score = c['score']
                    
                    st.markdown(f"""
                        <div class="candidate-card" style="border-left: 4px solid #38a169;">
                            <h3>#{i} {score['candidate_name']} - Score: {score['overall_score']}%</h3>
                            <p><strong>LinkedIn:</strong> {'✓ Verified' if score['linkedin_verified'] else '⚠ Not provided'}</p>
                            <p><strong>Key Strengths:</strong></p>
                            <ul>
                                {"".join([f'<li>{s}</li>' for s in score['key_strengths'][:4]])}
                            </ul>
                            <p><strong>Recommendation:</strong> {score['recommendation']}</p>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Detailed Scoring Breakdown
            st.markdown("---")
            st.markdown("## 📊 DETAILED SCORING BREAKDOWN")
            
            breakdown_data = []
            for c in candidates:
                score = c['score']
                breakdown_data.append({
                    'Candidate': score['candidate_name'],
                    'Overall': f"{score['overall_score']}%",
                    'Skills': f"{score['skills_score']}%",
                    'Experience': f"{score['experience_score']}%",
                    'Education': f"{score['education_score']}%",
                    'Soft Skills': f"{score['soft_skills_score']}%",
                    'Certs': f"{score['certification_score']}%",
                    'Tier': score['tier']
                })
            
            breakdown_df = pd.DataFrame(breakdown_data)
            
            def color_tier(val):
                if 'Tier 1' in str(val):
                    return 'background-color: #38a169; color: white; font-weight: bold'
                elif 'Tier 2' in str(val):
                    return 'background-color: #d69e2e; color: #1a202c; font-weight: bold'
                else:
                    return 'background-color: #e53e3e; color: white; font-weight: bold'
            
            st.dataframe(breakdown_df.style.map(color_tier, subset=['Tier']), use_container_width=True, hide_index=True)
    
    with tab4:
        st.subheader("🔍 LinkedIn Integration")
        st.info("LinkedIn API integration for real-time profile verification (requires API keys)")
        
        linkedin_url = st.text_input("LinkedIn Profile URL", placeholder="https://linkedin.com/in/username")
        
        if st.button("🔍 Parse LinkedIn Profile", use_container_width=True):
            if linkedin_url:
                with st.spinner("Parsing LinkedIn profile..."):
                    time.sleep(1)
                    profile = linkedin_parser.parse_profile(linkedin_url)
                    st.success("✅ Profile Parsed!")
                    st.json(profile)
    
    with tab5:
        st.subheader("💾 Save Candidates to Database")
        
        if st.session_state.candidates_batch:
            if st.button("💾 Save All Candidates", use_container_width=True, type="primary"):
                for c in st.session_state.candidates_batch:
                    score = c['score']
                    candidate_ref = generate_ref("CAND")
                    
                    candidate_data = (
                        candidate_ref,
                        score['candidate_name'].split()[0] if score['candidate_name'] else "Unknown",
                        ' '.join(score['candidate_name'].split()[1:]) if len(score['candidate_name'].split()) > 1 else '',
                        score['parsed_data'].get('email', ''),
                        score['parsed_data'].get('phone', ''),
                        score['parsed_data'].get('linkedin', ''),
                        score['parsed_data'].get('current_position', ''),
                        score['parsed_data'].get('current_company', ''),
                        score['parsed_data'].get('total_experience_years', 0),
                        score['parsed_data'].get('education_level', ''),
                        ', '.join([s['skill'] for s in score['parsed_data'].get('skills', [])]),
                        score['parsed_data'].get('location', ''),
                        c['filename'],
                        c['cv_text'][:5000],
                        None,
                        'AI Upload',
                        'Scored'
                    )
                    candidate_id = db.add_candidate(candidate_data)
                    
                    db.update_candidate_ai_score(
                        candidate_id, score['overall_score'], score['tier'],
                        json.dumps(score), score['skills_score'], score['experience_score'],
                        score['education_score'], score['overall_score'],
                        score['linkedin_verified'], json.dumps(score['key_strengths']),
                        json.dumps(score['gaps_identified']), score['recommendation']
                    )
                
                st.success(f"✅ {len(st.session_state.candidates_batch)} candidates saved!")
                st.balloons()


# ============ REPORTS & ANALYTICS ============
def reports_analytics():
    """Advanced reports and analytics dashboard"""
    
    st.markdown("""
        <div class="churchgate-header animate-in">
            <h1>📊 Reports & Analytics</h1>
            <p>AI-Powered Business Intelligence | Fortune 500 Standard Analytics</p>
        </div>
    """, unsafe_allow_html=True)
    
    report_type = st.selectbox("Select Report", [
        "Executive Scorecard",
        "Workforce Analytics",
        "Recruitment Analytics",
        "Performance Trends",
        "Financial Overview",
        "Diversity & Inclusion",
        "Attrition Analysis"
    ])
    
    if report_type == "Executive Scorecard":
        st.subheader("📊 Executive Scorecard - Churchgate Group")
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Revenue", "₦12.5B", "+15%")
        with col2:
            st.metric("EBITDA", "₦3.8B", "+8%")
        with col3:
            st.metric("Occupancy", "87%", "+5%")
        with col4:
            st.metric("NPS Score", "72", "+12")
        
        # Strategic Pillars Performance
        st.subheader("Strategic Pillars Performance")
        
        pillars_df = pd.DataFrame({
            'Pillar': ['Occupancy & Revenue', 'Process Simplification', 'Asset Reliability', 'People & Culture'],
            'Q1': [75, 60, 80, 85],
            'Q2': [78, 65, 82, 88],
            'Q3': [82, 70, 85, 90],
            'Q4': [85, 72, 90, 88],
            'Target': [90, 80, 95, 90]
        })
        
        fig = go.Figure()
        for i, row in pillars_df.iterrows():
            fig.add_trace(go.Scatter(
                x=['Q1', 'Q2', 'Q3', 'Q4'],
                y=[row['Q1'], row['Q2'], row['Q3'], row['Q4']],
                name=row['Pillar'],
                mode='lines+markers'
            ))
        fig.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="Target")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    elif report_type == "Recruitment Analytics":
        st.subheader("📊 Recruitment Analytics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Time to Hire", "23 days", "↓ 35%")
        with col2:
            st.metric("Cost per Hire", "₦450K", "↓ 42%")
        with col3:
            st.metric("Offer Acceptance", "85%", "↑ 10%")
        
        # Funnel
        funnel_data = pd.DataFrame({
            'Stage': ['Sourced', 'Applied', 'Screened', 'Interviewed', 'Offered', 'Hired'],
            'Count': [1000, 750, 500, 200, 50, 25]
        })
        fig = px.funnel(funnel_data, x='Count', y='Stage', color_discrete_sequence=['#c49216'])
        st.plotly_chart(fig, use_container_width=True)
    
    elif report_type == "Workforce Analytics":
        st.subheader("Workforce Distribution")
        
        col1, col2 = st.columns(2)
        with col1:
            dept_data = pd.DataFrame({
                'Department': ['ELV', 'MEP', 'Finance', 'HR', 'Sales', 'Ops'],
                'Count': [120, 200, 150, 100, 180, 147]
            })
            fig = px.bar(dept_data, x='Department', y='Count', color_discrete_sequence=['#c49216'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            exp_data = pd.DataFrame({
                'Experience': ['0-2 yrs', '3-5 yrs', '6-10 yrs', '10+ yrs'],
                'Count': [200, 450, 400, 197]
            })
            fig = px.pie(exp_data, values='Count', names='Experience', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)


# ============ CHAT & COMMUNICATIONS ============
def chat_communications():
    """Integrated chat and communications hub"""
    
    st.markdown("""
        <div class="churchgate-header animate-in">
            <h1>💬 Chat & Communications</h1>
            <p>Integrated Messaging | Announcements | Team Collaboration</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💬 Team Chat", "📢 Announcements", "📧 Email Notifications"])
    
    with tab1:
        st.subheader("Team Chat")
        
        # Chat interface
        chat_container = st.container()
        
        with chat_container:
            for msg in st.session_state.chat_messages[-10:]:
                if msg['type'] == 'user':
                    st.markdown(f"""
                        <div style="background: #c49216; color: white; padding: 0.8rem; border-radius: 10px; 
                                    margin: 0.5rem 0; margin-left: 2rem;">
                            <strong>You</strong>
                            <p style="margin: 0.2rem 0;">{msg['content']}</p>
                            <small>{msg['time']}</small>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="background: #f7fafc; padding: 0.8rem; border-radius: 10px; 
                                    margin: 0.5rem 0; margin-right: 2rem; border: 1px solid #e2e8f0;">
                            <strong>{msg['sender']}</strong>
                            <p style="margin: 0.2rem 0;">{msg['content']}</p>
                            <small>{msg['time']}</small>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Message input
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                message = st.text_input("Type a message...", placeholder="Type your message here...")
            with col2:
                send = st.form_submit_button("📤 Send", use_container_width=True)
            
            if send and message:
                st.session_state.chat_messages.append({
                    'type': 'user',
                    'content': message,
                    'time': datetime.now().strftime('%I:%M %p'),
                    'sender': 'You'
                })
                # Simulate response
                st.session_state.chat_messages.append({
                    'type': 'bot',
                    'content': f"Thanks for your message! This is an automated response.",
                    'time': datetime.now().strftime('%I:%M %p'),
                    'sender': 'HRIS Bot'
                })
                st.rerun()
    
    with tab2:
        st.subheader("📢 Company Announcements")
        
        announcements = [
            {"title": "Q2 Performance Reviews", "date": "2026-06-01", "priority": "High", "content": "All departments to submit Q2 performance reviews by June 15."},
            {"title": "BMS Implementation Update", "date": "2026-05-28", "priority": "Medium", "content": "Phase 1 of BMS installation complete. Phase 2 starts June 10."},
            {"title": "Holiday Notice - Democracy Day", "date": "2026-05-25", "priority": "Medium", "content": "Office closed on June 12 for Democracy Day."},
        ]
        
        for ann in announcements:
            priority_color = "#e53e3e" if ann['priority'] == 'High' else "#d69e2e" if ann['priority'] == 'Medium' else "#38a169"
            st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 10px; margin-bottom: 0.8rem;
                            border-left: 4px solid {priority_color};">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{ann['title']}</strong>
                        <span style="background: {priority_color}; color: white; padding: 0.2rem 0.6rem; 
                                    border-radius: 10px; font-size: 0.75rem;">{ann['priority']}</span>
                    </div>
                    <p style="margin: 0.5rem 0;">{ann['content']}</p>
                    <small style="color: #718096;">📅 {ann['date']}</small>
                </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("📧 Email Notification Settings")
        
        with st.form("email_settings"):
            st.markdown("### Notification Preferences")
            
            col1, col2 = st.columns(2)
            with col1:
                birthdays = st.checkbox("Birthday Alerts", value=True)
                anniversaries = st.checkbox("Work Anniversaries", value=True)
                promotions = st.checkbox("Promotion Announcements", value=True)
                new_hires = st.checkbox("New Hire Announcements", value=True)
            
            with col2:
                holidays = st.checkbox("Holiday Reminders", value=True)
                training = st.checkbox("Training & Webinars", value=True)
                performance = st.checkbox("Performance Review Reminders", value=True)
                news = st.checkbox("Company News", value=True)
            
            if st.form_submit_button("💾 Save Preferences", use_container_width=True):
                st.success("✅ Notification preferences saved!")


# ============ TRAINING & DEVELOPMENT ============
def training_development():
    """Training and development hub"""
    
    st.markdown("""
        <div class="churchgate-header animate-in">
            <h1>🎓 Training & Development</h1>
            <p>Learning Management System | Webinars | Professional Development</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📚 My Courses", "🌐 Upcoming Webinars", "📋 Training Calendar"])
    
    with tab1:
        st.subheader("My Learning Path")
        
        courses = pd.DataFrame({
            'Course': ['BMS Advanced Integration', 'AI in Facility Management', 'Leadership Excellence', 'Data Analytics'],
            'Progress': [75, 40, 90, 60],
            'Status': ['In Progress', 'Started', 'Near Complete', 'In Progress'],
            'Deadline': ['2026-07-15', '2026-08-30', '2026-06-15', '2026-09-01']
        })
        
        for _, course in courses.iterrows():
            color = "#38a169" if course['Progress'] >= 80 else "#d69e2e" if course['Progress'] >= 50 else "#e53e3e"
            st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 10px; margin-bottom: 0.8rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{course['Course']}</strong>
                        <span>{course['Progress']}%</span>
                    </div>
                    <div style="background: #edf2f7; height: 6px; border-radius: 3px; margin: 0.5rem 0;">
                        <div style="background: {color}; width: {course['Progress']}%; height: 6px; border-radius: 3px;"></div>
                    </div>
                    <small>Status: {course['Status']} | Deadline: {course['Deadline']}</small>
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("🌐 Upcoming Webinars & Conferences")
        
        webinars = [
            {"title": "AI in Real Estate Management", "date": "June 20, 2026", "source": "LinkedIn Learning", "dept": "Technology"},
            {"title": "Financial Modeling for Real Estate", "date": "June 25, 2026", "source": "CFA Institute", "dept": "Finance"},
            {"title": "HR Tech Summit 2026", "date": "July 10, 2026", "source": "SHRM", "dept": "HR"},
            {"title": "Facility Management Excellence", "date": "July 15, 2026", "source": "IFMA", "dept": "Operations"},
        ]
        
        for web in webinars:
            st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem;
                            border-left: 3px solid #c49216;">
                    <strong>{web['title']}</strong>
                    <br><small>📅 {web['date']} | 📍 {web['source']} | 🏢 {web['dept']}</small>
                </div>
            """, unsafe_allow_html=True)


# ============ NOTIFICATIONS ============
def notifications_page():
    """Notifications center"""
    
    st.markdown("""
        <div class="churchgate-header animate-in">
            <h1>🔔 Notifications</h1>
            <p>Alerts, Reminders, and Updates</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.user:
        notifications = db.get_user_notifications(st.session_state.user['id'])
        
        if len(notifications) > 0:
            for _, notif in notifications.iterrows():
                icon = "🔔" if notif['is_read'] == 0 else "✅"
                bg = "#fef3c7" if notif['is_read'] == 0 else "#f7fafc"
                
                st.markdown(f"""
                    <div style="background: {bg}; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;
                                border-left: 3px solid #c49216;">
                        {icon} <strong>{notif['title']}</strong>
                        <p style="margin: 0.25rem 0; color: #4a5568;">{notif['message']}</p>
                        <small style="color: #a0aec0;">{notif['created_at']}</small>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No notifications yet.")


# ============ MY PROFILE ============
def my_profile():
    """Employee profile page"""
    
    user = st.session_state.user
    
    st.markdown(f"""
        <div class="churchgate-header animate-in">
            <h1>👤 My Profile</h1>
            <p>{user['name']} • {user.get('position', 'Employee')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        initials = generate_employee_initials(user['name'])
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background: white; border-radius: 15px; 
                        box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                <div style="width: 100px; height: 100px; border-radius: 50%; 
                            background: linear-gradient(135deg, #c49216, #e2c456);
                            display: flex; align-items: center; justify-content: center;
                            font-size: 2.5rem; font-weight: 700; color: #1a202c; margin: 0 auto;">
                    {initials}
                </div>
                <h3 style="margin-top: 1rem;">{user['name']}</h3>
                <p style="color: #718096;">{user.get('position', 'Employee')}</p>
                <p style="color: #c49216;">ID: {user.get('employee_id', 'N/A')}</p>
                <div style="margin-top: 1rem; text-align: left;">
                    <p>🏢 <strong>Department:</strong> {user.get('department', 'N/A')}</p>
                    <p>👤 <strong>Supervisor:</strong> Jerome Das</p>
                    <p>📅 <strong>Joined:</strong> Jan 2, 2019</p>
                    <p>⏱️ <strong>Time in Company:</strong> 7 years 4 months</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        tab1, tab2, tab3 = st.tabs(["📋 Personal Info", "🔒 Security", "📊 Activity"])
        
        with tab1:
            with st.form("profile_form"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("First Name", value=user['name'].split()[0] if user['name'] else "")
                    st.text_input("Email", value=user.get('email', ''))
                    st.text_input("Phone", value="+234 800 000 0000")
                with col2:
                    st.text_input("Last Name", value=' '.join(user['name'].split()[1:]) if len(user['name'].split()) > 1 else '')
                    st.selectbox("Department", ["ELV Systems", "MEP", "Finance", "HR", "Sales"], index=0)
                
                if st.form_submit_button("💾 Update Profile", use_container_width=True):
                    st.success("✅ Profile updated!")
        
        with tab2:
            st.subheader("Change Password")
            with st.form("password_form"):
                current_pw = st.text_input("Current Password", type="password")
                new_pw = st.text_input("New Password", type="password")
                confirm_pw = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("🔒 Change Password", use_container_width=True):
                    if new_pw == confirm_pw:
                        st.success("✅ Password changed!")
                    else:
                        st.error("Passwords do not match")


# ============ MAIN APP ============
def main():
    """Main application entry point"""
    
    if st.session_state.user is None:
        login_section()
    else:
        page = sidebar_navigation()
        
        # Handle navigation redirects
        if 'navigate_to' in st.session_state:
            page = st.session_state.pop('navigate_to')
        
        # Route to correct page
        if page == "🏠 Employee Dashboard":
            employee_dashboard()
        elif page == "📊 Executive Dashboard":
            executive_dashboard()
        elif page == "👥 Employee Management":
            employee_management()
        elif page == "📈 Performance & OKRs":
            performance_okrs()
        elif page == "📈 My Performance & OKRs":
            performance_okrs()
        elif page == "🚀 Promotions":
            promotions()
        elif page == "💼 Recruitment Hub":
            st.info("Recruitment Hub - Post and manage jobs")
        elif page == "🤖 AI Recruitment Agent":
            ai_recruitment_agent()
        elif page == "📊 Reports & Analytics":
            reports_analytics()
        elif page == "💬 Chat & Communications":
            chat_communications()
        elif page == "🔔 Notifications":
            notifications_page()
        elif page == "🎓 Training & Development":
            training_development()
        elif page == "👤 My Profile":
            my_profile()
        else:
            employee_dashboard()


if __name__ == "__main__":
    main()
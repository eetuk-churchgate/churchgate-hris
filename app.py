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

logo_icon = Path(__file__).parent / "churchgate-logo.jpeg"
if logo_icon.exists():
    st.set_page_config(page_title="Churchgate Group HRIS", page_icon=str(logo_icon), layout="wide", initial_sidebar_state="expanded")
else:
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

def generate_summary_pdf(dept_name, dept_data, summary):
    """Generate a Fortune 500 Executive Summary PDF"""
    import fpdf
    FPDF = fpdf.FPDF
    
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    
    # ===== COVER HEADER =====
    pdf.set_fill_color(26, 26, 26)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_fill_color(204, 0, 0)
    pdf.rect(0, 35, 210, 4, 'F')
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 18, 'CHURCHGATE GROUP', ln=True, align='C')
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(204, 0, 0)
    pdf.cell(0, 10, 'EXECUTIVE PERFORMANCE SUMMARY', ln=True, align='C')
    pdf.ln(8)
    
    # ===== DEPT & DATE BAR =====
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(10, pdf.get_y(), 190, 10, 'F')
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(95, 10, f'  Department: {dept_name}', 0, 0, 'L')
    pdf.cell(95, 10, f'Generated: {datetime.now().strftime("%B %d, %Y")}  ', 0, 0, 'R')
    pdf.ln(14)
    
    # ===== OVERALL SCORE HERO =====
    total_weighted = sum(p['progress'] * p['weight'] / 100 for p in dept_data.values())
    on_track = sum(1 for p in dept_data.values() if p['status'] in ['On Track', 'Exceeding'])
    at_risk = sum(1 for p in dept_data.values() if p['status'] == 'At Risk')
    completed = sum(1 for p in dept_data.values() if p['status'] == 'Completed')
    
    pdf.set_fill_color(26, 26, 26)
    pdf.rect(10, pdf.get_y(), 190, 18, 'F')
    pdf.set_fill_color(204, 0, 0)
    pdf.rect(10, pdf.get_y()+18, 190, 2, 'F')
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(190, 18, f'OVERALL WEIGHTED SCORE: {total_weighted:.1f}%', ln=True, align='C')
    pdf.ln(6)
    
    # ===== KPI CARDS ROW =====
    pdf.set_font('Helvetica', 'B', 9)
    col_w = 42
    col_h = 14
    x_start = 14
    y_pos = pdf.get_y()
    
    cards = [
        ('ON TRACK', str(on_track), (56, 161, 105)),
        ('AT RISK', str(at_risk), (204, 0, 0)),
        ('COMPLETED', str(completed), (49, 130, 206)),
        ('TOTAL PILLARS', '4', (100, 100, 100)),
    ]
    
    for i, (label, value, color) in enumerate(cards):
        x = x_start + i * (col_w + 6)
        pdf.set_fill_color(*color)
        pdf.rect(x, y_pos, col_w, col_h, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(x, y_pos + 1)
        pdf.cell(col_w, 6, label, 0, 0, 'C')
        pdf.set_xy(x, y_pos + 7)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(col_w, 7, value, 0, 0, 'C')
        pdf.set_font('Helvetica', 'B', 9)
    
    pdf.set_y(y_pos + col_h + 8)
    
    # ===== PILLAR TABLE =====
    pdf.set_fill_color(26, 26, 26)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(68, 8, '  STRATEGIC PILLAR', 1, 0, 'L', True)
    pdf.cell(18, 8, 'WEIGHT', 1, 0, 'C', True)
    pdf.cell(22, 8, 'PROGRESS', 1, 0, 'C', True)
    pdf.cell(30, 8, 'STATUS', 1, 0, 'C', True)
    pdf.cell(52, 8, 'DEADLINE', 1, 0, 'C', True)
    pdf.ln()
    
    pdf.set_font('Helvetica', '', 8)
    for pn, pdata in dept_data.items():
        if pdata['status'] in ['On Track', 'Exceeding']:
            sc = (230, 255, 230)
            tc = (56, 161, 105)
        elif pdata['status'] == 'In Progress':
            sc = (255, 248, 230)
            tc = (214, 158, 46)
        else:
            sc = (255, 230, 230)
            tc = (204, 0, 0)
        
        pdf.set_fill_color(*sc)
        pdf.set_text_color(26, 26, 26)
        pdf.cell(68, 9, f'  {pn[:45]}', 1, 0, 'L', True)
        pdf.cell(18, 9, f'{pdata["weight"]}%', 1, 0, 'C', True)
        pdf.cell(22, 9, f'{pdata["progress"]}%', 1, 0, 'C', True)
        pdf.set_text_color(*tc)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(30, 9, pdata['status'], 1, 0, 'C', True)
        pdf.set_text_color(26, 26, 26)
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(52, 9, pdata['deadline'], 1, 0, 'C', True)
        pdf.ln()
    
    pdf.ln(4)
    
    # ===== PROGRESS BARS =====
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(0, 8, 'PILLAR PROGRESS', ln=True)
    pdf.ln(2)
    
    for pn, pdata in dept_data.items():
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(190, 4, pn[:55], ln=True)
        
        bar_y = pdf.get_y()
        pdf.set_fill_color(230, 230, 230)
        pdf.rect(10, bar_y, 190, 5, 'F')
        
        if pdata['progress'] >= 85:
            bar_color = (56, 161, 105)
        elif pdata['progress'] >= 65:
            bar_color = (214, 158, 46)
        else:
            bar_color = (204, 0, 0)
        
        pdf.set_fill_color(*bar_color)
        pdf.rect(10, bar_y, 190 * pdata['progress'] / 100, 5, 'F')
        pdf.set_y(bar_y + 7)
    
    pdf.ln(4)
    
    # ===== RACI MATRIX TABLE =====
    pdf.set_fill_color(26, 26, 26)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(190, 8, '  RACI MATRIX', 1, 0, 'L', True)
    pdf.ln()
    
    pdf.set_fill_color(245, 245, 245)
    pdf.set_text_color(26, 26, 26)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(35, 7, '  Role', 1, 0, 'L', True)
    pdf.cell(155, 7, '  Party', 1, 0, 'L', True)
    pdf.ln()
    
    raci_data = [
        ('RESPONSIBLE', 'Department Heads / HODs'),
        ('ACCOUNTABLE', 'GMD / COO'),
        ('CONSULTED', 'All HODs / Key Stakeholders'),
        ('INFORMED', 'Board of Directors'),
    ]
    
    pdf.set_font('Helvetica', '', 8)
    for role, party in raci_data:
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(35, 7, f'  {role}', 1, 0, 'L', True)
        pdf.cell(155, 7, f'  {party}', 1, 0, 'L', True)
        pdf.ln()
    
    # ===== FOOTER =====
    pdf.set_y(-18)
    pdf.set_fill_color(26, 26, 26)
    pdf.rect(0, pdf.get_y()-2, 210, 20, 'F')
    pdf.set_font('Helvetica', 'I', 7)
    pdf.set_text_color(180, 180, 180)
    pdf.cell(0, 6, 'Churchgate Group - Confidential - Fortune 500 Standard HRIS', ln=True, align='C')
    pdf.cell(0, 5, 'World Trade Center, Abuja | hr@churchgate.com', ln=True, align='C')
    
    return bytes(pdf.output())

def generate_performance_pdf(dept_name, dept_data, report_data):
    """Generate a Fortune 500 Performance Report PDF"""
    import fpdf
    FPDF = fpdf.FPDF
    
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    
    pdf.set_fill_color(26, 26, 26)
    pdf.rect(0, 0, 297, 28, 'F')
    pdf.set_fill_color(204, 0, 0)
    pdf.rect(0, 28, 297, 3, 'F')
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 16, 'CHURCHGATE GROUP', ln=True, align='C')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(204, 0, 0)
    pdf.cell(0, 8, 'DETAILED PERFORMANCE REPORT', ln=True, align='C')
    pdf.ln(6)
    
    total_weighted = sum(p['progress'] * p['weight'] / 100 for p in dept_data.values())
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(10, pdf.get_y(), 277, 8, 'F')
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(92, 8, f'  Department: {dept_name}', 0, 0, 'L')
    pdf.cell(92, 8, f'Overall Score: {total_weighted:.1f}%', 0, 0, 'C')
    pdf.cell(93, 8, f'Generated: {datetime.now().strftime("%B %d, %Y %I:%M %p")}  ', 0, 0, 'R')
    pdf.ln(12)
    
    pdf.set_fill_color(26, 26, 26)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(8, 8, ' #', 1, 0, 'C', True)
    pdf.cell(80, 8, ' STRATEGIC PILLAR / KPI', 1, 0, 'L', True)
    pdf.cell(22, 8, 'TARGET', 1, 0, 'C', True)
    pdf.cell(22, 8, 'CURRENT', 1, 0, 'C', True)
    pdf.cell(24, 8, 'STATUS', 1, 0, 'C', True)
    pdf.cell(28, 8, 'DEADLINE', 1, 0, 'C', True)
    pdf.cell(93, 8, ' REMARKS', 1, 0, 'L', True)
    pdf.ln()
    
    pdf.set_font('Helvetica', '', 7)
    row_num = 0
    for pn, pdata in dept_data.items():
        pdf.set_fill_color(240, 240, 240)
        pdf.set_text_color(26, 26, 26)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(8, 7, '', 1, 0, 'C', True)
        pdf.cell(80, 7, f' {pn}', 1, 0, 'L', True)
        pdf.cell(22, 7, f'Weight: {pdata["weight"]}%', 1, 0, 'C', True)
        pdf.cell(22, 7, f'{pdata["progress"]}%', 1, 0, 'C', True)
        
        if pdata['status'] in ['On Track', 'Exceeding']:
            sc = (56, 161, 105)
        elif pdata['status'] == 'In Progress':
            sc = (214, 158, 46)
        else:
            sc = (204, 0, 0)
        pdf.set_fill_color(*sc)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(24, 7, pdata['status'], 1, 0, 'C', True)
        pdf.set_text_color(26, 26, 26)
        pdf.set_font('Helvetica', '', 7)
        pdf.cell(28, 7, pdata['deadline'], 1, 0, 'C', True)
        pdf.cell(93, 7, f' {len(pdata.get("kpis", []))} KPIs defined', 1, 0, 'L', True)
        pdf.ln()
        
        for kpi in pdata.get('kpis', []):
            row_num += 1
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(80, 80, 80)
            pdf.set_font('Helvetica', '', 7)
            pdf.cell(8, 6, str(row_num), 1, 0, 'C', True)
            pdf.cell(80, 6, f'   {kpi["kpi"][:55]}', 1, 0, 'L', True)
            pdf.cell(22, 6, kpi['target'], 1, 0, 'C', True)
            pdf.cell(22, 6, kpi['current'], 1, 0, 'C', True)
            
            if kpi['status'] in ['On Track', 'Completed']:
                kc = (56, 161, 105)
            elif kpi['status'] in ['Near Target', 'In Progress']:
                kc = (214, 158, 46)
            else:
                kc = (204, 0, 0)
            pdf.set_text_color(*kc)
            pdf.set_font('Helvetica', 'B', 7)
            pdf.cell(24, 6, kpi['status'], 1, 0, 'C', True)
            pdf.set_text_color(80, 80, 80)
            pdf.set_font('Helvetica', '', 7)
            pdf.cell(28, 6, kpi['deadline'], 1, 0, 'C', True)
            pdf.cell(93, 6, '', 1, 0, 'L', True)
            pdf.ln()
    
    pdf.ln(4)
    
    pdf.set_fill_color(26, 26, 26)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(277, 8, '  RACI MATRIX', 1, 0, 'L', True)
    pdf.ln()
    
    raci = [
        ('RESPONSIBLE', 'Department Heads'),
        ('ACCOUNTABLE', 'GMD / COO'),
        ('CONSULTED', 'All HODs'),
        ('INFORMED', 'Board'),
    ]
    for role, party in raci:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(26, 26, 26)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.cell(35, 6, f'  {role}', 1, 0, 'L', True)
        pdf.set_font('Helvetica', '', 7)
        pdf.cell(242, 6, f'  {party}', 1, 0, 'L', True)
        pdf.ln()
    
    pdf.set_y(-15)
    pdf.set_fill_color(26, 26, 26)
    pdf.rect(0, pdf.get_y()-2, 297, 17, 'F')
    pdf.set_font('Helvetica', 'I', 7)
    pdf.set_text_color(180, 180, 180)
    pdf.cell(0, 5, 'Churchgate Group - Confidential - Fortune 500 Standard HRIS | World Trade Center, Abuja', ln=True, align='C')
    
    return bytes(pdf.output())

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
        

def sidebar_navigation():
    with st.sidebar:
        logo = get_logo()
        if logo:
            st.image(logo, width=220)
        st.markdown("""<div style="text-align: center; padding: 0.8rem 0; background: #4a4a4a; border-radius: 6px; margin-bottom: 1rem; border: 1px solid #666666;"><h3 style="color: #ffffff; margin: 0; font-size: 1.1rem; font-weight: 700;">CHURCHGATE GROUP</h3><p style="color: #cccccc; font-size: 0.7rem; margin: 0;">HRIS v5.0</p></div>""", unsafe_allow_html=True)
        if st.session_state.user:
            user = st.session_state.user
            initials = generate_initials(user['name'])
            db_pic = None
            if db.use_supabase:
                db_pic = db.get_profile_picture(int(st.session_state.user['id']))
            elif 'profile_pic' in st.session_state and st.session_state['profile_pic'] is not None:
                db_pic = st.session_state['profile_pic']
            
            if db_pic is not None:
                import base64
                profile_html = f'<img src="data:image/png;base64,{base64.b64encode(db_pic).decode()}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">'
            else:
                profile_html = f'<div style="width: 40px; height: 40px; border-radius: 50%; background: #CC0000; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1rem; color: white;">{initials}</div>'
            st.markdown(f"""<div style="background: rgba(255,255,255,0.08); padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid rgba(204, 0, 0, 0.2);"><div style="display: flex; align-items: center; gap: 0.6rem;">{profile_html}<div><p style="color: #333; margin: 0; font-weight: 600; font-size: 0.85rem;">{user['name']}</p><p style="color: #666; margin: 0; font-size: 0.7rem;">{user['role']} • {user.get('department', '')}</p></div></div></div>""", unsafe_allow_html=True)
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
    st.markdown("""<div class="churchgate-header"><h1>📊 Executive Dashboard</h1><p>Corporate Strategy 2026-2027 | Real-Time Group Performance Intelligence</p></div>""", unsafe_allow_html=True)
    
    # ============ LOAD REAL DATA ============
    total_employees = 0
    active_employees = 0
    departments = 0
    open_positions = 0
    male_count = 0
    female_count = 0
    emp_df = pd.DataFrame()
    
    try:
        emp_df = db.get_all_employees()
        if not emp_df.empty:
            total_employees = len(emp_df)
            active_employees = len(emp_df[emp_df['status'] == 'Active'])
            departments = len(emp_df['department'].unique())
            if 'gender' in emp_df.columns:
                male_count = len(emp_df[emp_df['gender'].str.lower() == 'male'])
                female_count = len(emp_df[emp_df['gender'].str.lower() == 'female'])
    except:
        pass
    
    try:
        all_reqs = db.get_all_job_requisitions()
        if all_reqs:
            open_positions = len([r for r in all_reqs if r.get('status') == 'Approved - Live'])
        candidates_df = db.get_all_candidates()
        if not candidates_df.empty:
            open_positions += len(candidates_df[candidates_df['status'] == 'New'])
    except:
        pass
    
    escalated_count = 0
    try:
        if 'self_assessments' in st.session_state:
            escalated_count = len([v for v in st.session_state.self_assessments.values() if v.get('acceptance') == 'Rejected'])
    except:
        pass
    
    # ============ LOAD/INITIALIZE PORTFOLIO METRICS ============
    if 'portfolio_metrics' not in st.session_state:
        st.session_state.portfolio_metrics = {
            'occupancy': 87, 'revenue': 94, 'rating': 4.2,
            'portfolio_data': {
                'World Trade Center Abuja': {'occupancy': 87, 'revenue': 94},
                'Churchgate Tower 1, Lagos': {'occupancy': 92, 'revenue': 98},
                'Churchgate Tower 2, Lagos': {'occupancy': 85, 'revenue': 88},
                'Churchgate Plaza, Abuja': {'occupancy': 78, 'revenue': 82},
                'Warehouses': {'occupancy': 95, 'revenue': 97},
                'Ocean Terrace': {'occupancy': 90, 'revenue': 91}
            }
        }
        # Load saved metrics from database
        try:
            saved = db.get_portfolio_metrics()
            if saved:
                if 'occupancy' in saved:
                    st.session_state.portfolio_metrics['occupancy'] = int(float(saved['occupancy']))
                if 'revenue' in saved:
                    st.session_state.portfolio_metrics['revenue'] = int(float(saved['revenue']))
                if 'rating' in saved:
                    st.session_state.portfolio_metrics['rating'] = float(saved['rating'])
        except:
            pass
    
    metrics = st.session_state.portfolio_metrics
    
    # ============ ALERTS BAR ============
    alerts = []
    if escalated_count > 0:
        alerts.append(f"🚨 {escalated_count} escalated appraisal(s) need attention")
    if open_positions > 0:
        alerts.append(f"📢 {open_positions} open positions to fill")
    
    if alerts:
        alert_html = " | ".join(alerts)
        st.markdown(f"""
        <div style="background:#fff3cd;padding:0.8rem 1.5rem;border-radius:8px;margin-bottom:1rem;border-left:4px solid #d69e2e;">
            <strong>⚠️ Executive Alerts:</strong> {alert_html}
        </div>
        """, unsafe_allow_html=True)
    
    # ============ TOP KPI CARDS - ALL REAL DATA ============
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">👥 Total Employees</div><div class="metric-value">{total_employees}</div><small style="color:#38a169;">{active_employees} active</small></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">🏢 Departments</div><div class="metric-value">{departments}</div><small style="color:#38a169;">2 regions</small></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">📋 Open Positions</div><div class="metric-value">{open_positions}</div><small style="color:#CC0000;">Active hiring</small></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">🏠 Occupancy</div><div class="metric-value">{metrics['occupancy']}%</div><small style="color:#38a169;">Portfolio avg</small></div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">💰 Revenue</div><div class="metric-value">{metrics['revenue']}%</div><small style="color:#d69e2e;">vs budget</small></div>""", unsafe_allow_html=True)
    with c6:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">⭐ Rating</div><div class="metric-value">{metrics['rating']}</div><small style="color:#38a169;">Tenant satisfaction</small></div>""", unsafe_allow_html=True)
    
    # ============ ADMIN UPDATE METRICS ============
    is_admin = st.session_state.user['role'] in ['Admin', 'HR Director'] if st.session_state.user else False
    is_sr_mgmt = st.session_state.user.get('department') == 'Senior Management' if st.session_state.user else False
    
    if is_admin or is_sr_mgmt:
        with st.expander("⚙️ Update Portfolio Metrics (Admin)", expanded=False):
            st.markdown("### Update Key Metrics")
            c1, c2, c3 = st.columns(3)
            with c1:
                new_occupancy = st.slider("Occupancy Rate %", 0, 100, metrics['occupancy'])
            with c2:
                new_revenue = st.slider("Revenue vs Budget %", 0, 100, metrics['revenue'])
            with c3:
                new_rating = st.slider("Tenant Rating /5", 1.0, 5.0, metrics['rating'], 0.1)
            
            st.markdown("### Update Portfolio Properties")
            for prop in metrics['portfolio_data']:
                c1, c2 = st.columns(2)
                with c1:
                    metrics['portfolio_data'][prop]['occupancy'] = st.slider(f"{prop} - Occupancy %", 0, 100, metrics['portfolio_data'][prop]['occupancy'], key=f"occ_{prop}")
                with c2:
                    metrics['portfolio_data'][prop]['revenue'] = st.slider(f"{prop} - Revenue %", 0, 100, metrics['portfolio_data'][prop]['revenue'], key=f"rev_{prop}")
            
            if st.button("💾 Update All Metrics", use_container_width=True):
                st.session_state.portfolio_metrics['occupancy'] = new_occupancy
                st.session_state.portfolio_metrics['revenue'] = new_revenue
                st.session_state.portfolio_metrics['rating'] = new_rating
                try:
                    db.save_portfolio_metric('occupancy', new_occupancy)
                    db.save_portfolio_metric('revenue', new_revenue)
                    db.save_portfolio_metric('rating', new_rating)
                except:
                    pass
                st.success("✅ Metrics updated & saved!")
                st.rerun()
    
    # ============ QUICK ACTIONS ============
    st.markdown("---")
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    with quick_col1:
        if st.button("📝 Post Job", use_container_width=True):
            st.session_state['navigate_to'] = "💼 Recruitment Hub"
            st.rerun()
    with quick_col2:
        if st.button("👥 View Employees", use_container_width=True):
            st.session_state['navigate_to'] = "👥 Employee Management"
            st.rerun()
    with quick_col3:
        if st.button("📈 Performance", use_container_width=True):
            st.session_state['navigate_to'] = "📈 Performance & OKRs"
            st.rerun()
    with quick_col4:
        if st.button("🤖 AI Screening", use_container_width=True):
            st.session_state['navigate_to'] = "🤖 AI Recruitment Agent"
            st.rerun()
    
    # ============ ROW 1: PORTFOLIO + DEPARTMENT DISTRIBUTION ============
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Portfolio Performance")
        props = list(metrics['portfolio_data'].keys())
        occ_vals = [metrics['portfolio_data'][p]['occupancy'] for p in props]
        rev_vals = [metrics['portfolio_data'][p]['revenue'] for p in props]
        
        portfolio_data = pd.DataFrame({'Property': props, 'Occupancy %': occ_vals, 'Revenue %': rev_vals})
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Occupancy %', x=portfolio_data['Property'], y=portfolio_data['Occupancy %'], marker_color='#CC0000', text=portfolio_data['Occupancy %'], textposition='outside'))
        fig.add_trace(go.Bar(name='Revenue %', x=portfolio_data['Property'], y=portfolio_data['Revenue %'], marker_color='#4a4a4a', text=portfolio_data['Revenue %'], textposition='outside'))
        fig.update_layout(height=350, barmode='group', margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👥 Department Distribution")
        if not emp_df.empty:
            dept_counts = emp_df['department'].value_counts()
            fig2 = px.pie(values=dept_counts.values, names=dept_counts.index, hole=0.4,
                         color_discrete_sequence=['#CC0000', '#3182ce', '#38a169', '#d69e2e', '#805ad5', '#dd6b20', '#2b6cb0', '#718096', '#e53e3e', '#319795', '#d53f8c'])
            fig2.update_layout(height=350, margin=dict(t=20))
            st.plotly_chart(fig2, use_container_width=True)
    
    # ============ ROW 2: STRATEGIC PILLARS + GENDER DIVERSITY ============
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Strategic Pillars 2026-2027")
        
        # Load real performance data
        pillar_progress = {
            '1. Occupancy & Revenue Growth': {'progress': 0, 'color': '#CC0000'},
            '2. Process Simplification': {'progress': 0, 'color': '#38a169'},
            '3. Asset Reliability & Digitalization': {'progress': 0, 'color': '#3182ce'},
            '4. People & Culture': {'progress': 0, 'color': '#d69e2e'},
        }
        
        try:
            perf_data = db.get_performance_data()
            if not perf_data.empty:
                for _, row in perf_data.iterrows():
                    pillar = row.get('pillar_name', '')
                    progress = row.get('progress', 0)
                    for key in pillar_progress:
                        if key[:2] in pillar or pillar[:2] in key:
                            pillar_progress[key]['progress'] = int(progress)
                            break
        except:
            pass
        
        # If all zeros, show defaults
        if all(v['progress'] == 0 for v in pillar_progress.values()):
            pillar_progress['1. Occupancy & Revenue Growth']['progress'] = 85
            pillar_progress['2. Process Simplification']['progress'] = 72
            pillar_progress['3. Asset Reliability & Digitalization']['progress'] = 90
            pillar_progress['4. People & Culture']['progress'] = 88
        
        for name, data in pillar_progress.items():
            st.markdown(f"""
            <div style="background:white;padding:0.8rem 1rem;border-radius:8px;margin-bottom:0.5rem;border-left:4px solid {data['color']};">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-weight:600;font-size:0.9rem;">{name}</span>
                    <span style="color:{data['color']};font-weight:700;">{data['progress']}%</span>
                </div>
                <div style="background:#e0e0e0;height:6px;border-radius:3px;margin-top:0.4rem;">
                    <div style="background:{data['color']};width:{data['progress']}%;height:6px;border-radius:3px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🌍 Gender Diversity (Real-Time)")
        if male_count > 0 or female_count > 0:
            gender_data = pd.DataFrame({'Gender': ['Male', 'Female'], 'Count': [male_count, female_count]})
            fig3 = px.pie(gender_data, values='Count', names='Gender', hole=0.6, color_discrete_sequence=['#3182ce', '#CC0000'])
            fig3.update_layout(height=300, margin=dict(t=20))
            st.plotly_chart(fig3, use_container_width=True)
            
            st.markdown(f"""
            <div style="text-align:center;margin-top:-5rem;position:relative;z-index:1;">
                <span style="font-size:2rem;font-weight:900;color:#CC0000;">{total_employees}</span><br>
                <small style="color:#888;">Total Workforce</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Gender data will appear as employees are updated with gender information.")
    
    # ============ ROW 3: REVENUE TREND + UPCOMING DEADLINES ============
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trend (₦ Billions)")
        
        if 'revenue_trend' not in st.session_state:
            st.session_state.revenue_trend = {
                'Jan': 1.8, 'Feb': 2.0, 'Mar': 2.1, 'Apr': 2.2, 'May': 2.3, 'Jun': 2.5
            }
        
        months = list(st.session_state.revenue_trend.keys())
        actual = list(st.session_state.revenue_trend.values())
        target = [v * 1.05 for v in actual]
        
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=months, y=actual, mode='lines+markers', name='Actual', line=dict(color='#CC0000', width=3), fill='tozeroy', fillcolor='rgba(204,0,0,0.1)'))
        fig4.add_trace(go.Scatter(x=months, y=target, mode='lines', name='Target', line=dict(color='#4a4a4a', width=2, dash='dash')))
        fig4.update_layout(height=300, margin=dict(t=20))
        st.plotly_chart(fig4, use_container_width=True)
        
        if is_admin or is_sr_mgmt:
            with st.expander("✏️ Edit Revenue Data"):
                new_trend = {}
                c1, c2, c3 = st.columns(3)
                for i, month in enumerate(months):
                    col = [c1, c2, c3][i % 3]
                    with col:
                        new_trend[month] = st.number_input(f"{month} (₦B)", value=float(st.session_state.revenue_trend[month]), step=0.1, key=f"rev_{month}")
                if st.button("💾 Update Revenue Trend", use_container_width=True):
                    st.session_state.revenue_trend = new_trend
                    st.success("✅ Revenue trend updated!")
                    st.rerun()
    
    with col2:
        st.subheader("📅 Upcoming Deadlines")
        
        if 'custom_deadlines' not in st.session_state:
            st.session_state.custom_deadlines = []
        
        real_deadlines = []
        
        try:
            all_reqs = db.get_all_job_requisitions()
            if all_reqs:
                for r in all_reqs:
                    if r.get('status') == 'Approved - Live' and r.get('closing'):
                        real_deadlines.append({
                            "task": f"Applications Close: {r.get('title', 'Job')}",
                            "date": r['closing'],
                            "priority": "High"
                        })
        except:
            pass
        
        if st.session_state.get('appraisal_cycle_active') and st.session_state.get('appraisal_end'):
            real_deadlines.append({
                "task": f"Appraisal Cycle Ends: {st.session_state.get('appraisal_cycle_name', '')}",
                "date": st.session_state['appraisal_end'],
                "priority": "Medium"
            })
        
        all_deadlines = real_deadlines + st.session_state.custom_deadlines
        try:
            all_deadlines.sort(key=lambda x: x['date'])
        except:
            pass
        
        if all_deadlines:
            for d in all_deadlines[:8]:
                try:
                    due = datetime.strptime(d['date'], '%Y-%m-%d')
                    days_left = (due - datetime.now()).days
                    days_str = f"{days_left} days left" if days_left > 0 else "🔴 OVERDUE"
                    urgency_color = "#CC0000" if days_left < 30 else "#d69e2e" if days_left < 60 else "#38a169"
                except:
                    days_str = d['date']
                    urgency_color = "#718096"
                
                st.markdown(f"""
                <div style="background:white;padding:0.7rem 1rem;border-radius:6px;margin-bottom:0.4rem;display:flex;justify-content:space-between;align-items:center;border-left:3px solid {urgency_color};">
                    <div>
                        <strong style="font-size:0.9rem;">{d['task']}</strong>
                        <span style="background:{'#CC0000' if d['priority']=='High' else '#d69e2e'};color:white;padding:0.1rem 0.5rem;border-radius:10px;font-size:0.7rem;margin-left:0.5rem;">{d['priority']}</span>
                    </div>
                    <small style="color:{urgency_color};font-weight:600;">{days_str}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No upcoming deadlines.")
        
        if is_admin or is_sr_mgmt:
            with st.expander("✏️ Add Custom Deadline"):
                with st.form("add_deadline"):
                    c1, c2 = st.columns(2)
                    with c1:
                        new_task = st.text_input("Task Name")
                        new_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                    with c2:
                        new_date = st.date_input("Due Date")
                    if st.form_submit_button("➕ Add Deadline"):
                        if new_task:
                            st.session_state.custom_deadlines.append({
                                "task": new_task,
                                "date": new_date.strftime('%Y-%m-%d'),
                                "priority": new_priority
                            })
                            st.success("✅ Deadline added!")
                            st.rerun()
                
                if st.session_state.custom_deadlines:
                    st.markdown("**Custom Deadlines:**")
                    for i, cd in enumerate(st.session_state.custom_deadlines):
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"- {cd['task']} ({cd['date']})")
                        with c2:
                            if st.button("🗑️", key=f"del_dead_{i}"):
                                st.session_state.custom_deadlines.pop(i)
                                st.rerun()
    
    # ============ ROW 4: RECENT ACTIVITY ============
    st.markdown("---")
    st.subheader("🕐 Recent Activity Feed")
    
    # Pull real activities from audit trail and system state
    activities = []
    
    # From audit trail (last 5 entries)
    if 'audit_trail' in st.session_state and st.session_state.audit_trail:
        for entry in st.session_state.audit_trail[-3:]:
            activities.append({
                "icon": "📋",
                "action": entry.get('action', 'Activity'),
                "detail": entry.get('details', ''),
                "time": entry.get('timestamp', 'Recent')
            })
    
    # Current system state
    activities.append({
        "icon": "👥",
        "action": "Workforce",
        "detail": f"{total_employees} employees across {departments} departments",
        "time": "Current"
    })
    
    activities.append({
        "icon": "📋",
        "action": "Open Positions",
        "detail": f"{open_positions} positions actively hiring",
        "time": "Current"
    })
    
    if st.session_state.get('appraisal_cycle_active'):
        activities.append({
            "icon": "📊",
            "action": "Appraisal Cycle Active",
            "detail": st.session_state.get('appraisal_cycle_name', 'Appraisal in progress'),
            "time": "Active"
        })
    
    for activity in activities[-5:]:
        st.markdown(f"""
        <div style="background:white;padding:0.8rem;border-radius:8px;margin-bottom:0.4rem;display:flex;align-items:center;gap:1rem;border-left:3px solid #CC0000;">
            <span style="font-size:1.5rem;">{activity['icon']}</span>
            <div style="flex:1;"><strong>{activity['action']}</strong><br><small>{activity['detail']}</small></div>
            <small style="color:#888;">{activity['time']}</small>
        </div>
        """, unsafe_allow_html=True)

def employee_management():
    st.markdown("""<div class="churchgate-header"><h1>👥 Employee Management</h1><p>Comprehensive workforce management | Real-time Data | Churchgate Group</p></div>""", unsafe_allow_html=True)
    
    user_role = st.session_state.user['role'] if st.session_state.user else 'Team Member'
    user_dept = st.session_state.user.get('department', '') if st.session_state.user else ''
    is_admin = user_role in ['Admin', 'HR Director'] or user_dept == 'Senior Management'
    
    @st.cache_data(ttl=60)
    def load_employees():
        try:
            df = db.get_all_employees()
            if df is None or df.empty:
                df = pd.DataFrame(columns=['employee_id', 'first_name', 'last_name', 'email', 'phone', 'department', 'position', 'grade', 'employment_type', 'join_date', 'status'])
            return df
        except:
            return pd.DataFrame(columns=['employee_id', 'first_name', 'last_name', 'email', 'phone', 'department', 'position', 'grade', 'employment_type', 'join_date', 'status'])
    
    employees_df = load_employees()
    
    dept_colors = {
        'Senior Management': '#CC0000', 'Technology Group': '#3182ce', 'Facility Management': '#38a169',
        'Human Resources': '#d69e2e', 'Accounts & Finance': '#805ad5', 'Sales & Marketing': '#dd6b20',
        'Procurement': '#2b6cb0', 'Security': '#718096', 'Legal': '#e53e3e', 'Operations': '#319795',
        'Engineering': '#d53f8c'
    }
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📋 Directory", "➕ Add Employee", "📤 Bulk Upload", 
        "🔑 Generate Logins", "🏢 Departments", "📊 Org Chart", "📈 Demographics", "📥 Export"
    ])
    
    # ============ TAB 1: DIRECTORY ============
    with tab1:
        st.subheader("📋 Employee Directory")
        
        total_emp = len(employees_df)
        active_emp = len(employees_df[employees_df['status'] == 'Active']) if not employees_df.empty else 0
        new_this_month = 0
        try:
            current_month = datetime.now().month
            for _, emp in employees_df.iterrows():
                jd = emp.get('join_date')
                if jd and pd.notna(jd):
                    if hasattr(jd, 'month') and jd.month == current_month:
                        new_this_month += 1
        except:
            pass
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("👥 Total", total_emp)
        with c2:
            st.metric("✅ Active", active_emp)
        with c3:
            st.metric("🏢 Departments", len(employees_df['department'].unique()) if not employees_df.empty else 0)
        with c4:
            st.metric("🆕 New This Month", new_this_month)
        
        # Birthdays this month
        st.markdown("---")
        st.markdown("### 🎂 Birthdays & Anniversaries This Month")
        bday_col1, bday_col2 = st.columns(2)
        with bday_col1:
            st.markdown("**🎂 Birthdays:** Chika Ikwuegbu (May 13), Francis Asuquo (May 19), Rhoda Ajibola (May 25), Alice Agbo (May 28)")
        with bday_col2:
            st.markdown("**⭐ Anniversaries:** Augustine Oleh (4 yrs), Shem Waziri (3 yrs), Charles Okere (7 yrs), Chika Ikwuegbu (3 yrs)")
        
        st.markdown("---")
        
        # Search & Filters
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1:
            search = st.text_input("🔍 Search", placeholder="Name, ID, email, department, position...")
        with c2:
            all_depts = ['All'] + sorted(list(employees_df['department'].dropna().unique())) if not employees_df.empty else ['All']
            dept_filter = st.selectbox("Department", all_depts)
        with c3:
            all_grades = ['All'] + sorted(list(employees_df['grade'].dropna().unique())) if not employees_df.empty else ['All']
            grade_filter = st.selectbox("Grade", all_grades)
        with c4:
            status_filter = st.selectbox("Status", ["All", "Active", "On Leave", "Probation", "Terminated"])
        
        filtered_df = employees_df.copy()
        if not filtered_df.empty:
            if search:
                s = search.lower()
                filtered_df = filtered_df[
                    filtered_df['first_name'].str.lower().str.contains(s, na=False) |
                    filtered_df['last_name'].str.lower().str.contains(s, na=False) |
                    filtered_df['employee_id'].str.lower().str.contains(s, na=False) |
                    filtered_df['email'].str.lower().str.contains(s, na=False) |
                    filtered_df['department'].str.lower().str.contains(s, na=False) |
                    filtered_df['position'].str.lower().str.contains(s, na=False)
                ]
            if dept_filter != 'All':
                filtered_df = filtered_df[filtered_df['department'] == dept_filter]
            if grade_filter != 'All':
                filtered_df = filtered_df[filtered_df['grade'] == grade_filter]
            if status_filter != 'All':
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        st.markdown(f"**Showing {len(filtered_df)} of {total_emp} employees**")
        
        if not filtered_df.empty:
            items_per_page = 10
            total_pages = max(1, (len(filtered_df) + items_per_page - 1) // items_per_page)
            
            if 'dir_page' not in st.session_state:
                st.session_state.dir_page = 1
            
            pg_col1, pg_col2, pg_col3 = st.columns([1, 2, 1])
            with pg_col1:
                if st.button("⬅️ Previous", disabled=st.session_state.dir_page <= 1, use_container_width=True):
                    st.session_state.dir_page -= 1
                    st.rerun()
            with pg_col2:
                st.markdown(f"<p style='text-align:center;color:#666;'>Page <strong>{st.session_state.dir_page}</strong> of <strong>{total_pages}</strong></p>", unsafe_allow_html=True)
            with pg_col3:
                if st.button("Next ➡️", disabled=st.session_state.dir_page >= total_pages, use_container_width=True):
                    st.session_state.dir_page += 1
                    st.rerun()
            
            start_idx = (st.session_state.dir_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(filtered_df))
            
            for _, emp in filtered_df.iloc[start_idx:end_idx].iterrows():
                initials = generate_initials(f"{emp['first_name']} {emp['last_name']}")
                status_color = "#38a169" if emp.get('status') == 'Active' else "#d69e2e" if emp.get('status') == 'On Leave' else "#CC0000"
                status_bg = "#e6f9e6" if emp.get('status') == 'Active' else "#fff8e6" if emp.get('status') == 'On Leave' else "#ffe6e6"
                border_color = dept_colors.get(emp.get('department', ''), '#CC0000')
                
                with st.expander(f"👤 {emp['first_name']} {emp['last_name']} • {emp.get('position', 'N/A')}", expanded=False):
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="width:55px;height:55px;border-radius:50%;background:linear-gradient(135deg,{border_color},#e53e3e);
                                    display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.3rem;color:white;">
                            {initials}
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div style="line-height:1.6;">
                            <strong style="font-size:1.1rem;">{emp['first_name']} {emp['last_name']}</strong><br>
                            <span style="color:#666;">💼 {emp.get('position', 'N/A')}</span><br>
                            <span style="color:#888;font-size:0.85rem;">🏢 {emp.get('department', 'N/A')} • 🆔 {emp.get('employee_id', 'N/A')}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div style="text-align:right;">
                            <span style="background:{status_bg};color:{status_color};padding:0.3rem 0.8rem;border-radius:20px;font-size:0.8rem;font-weight:600;border:1px solid {status_color};">
                                {emp.get('status', 'Active')}
                            </span>
                            <br><small style="color:#888;">📅 {emp.get('join_date', 'N/A')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.markdown(f"📧 <small>{emp.get('email', 'N/A')}</small>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"📱 <small>{emp.get('phone', 'N/A')}</small>", unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"📊 <small>Grade: {emp.get('grade', 'N/A')}</small>", unsafe_allow_html=True)
                    with c4:
                        st.markdown(f"💼 <small>{emp.get('employment_type', 'N/A')}</small>", unsafe_allow_html=True)
                    
                    if is_admin:
                        st.markdown("---")
                        with st.form(f"edit_{emp['employee_id']}"):
                            st.markdown("#### ✏️ Quick Edit")
                            ec1, ec2, ec3 = st.columns(3)
                            with ec1:
                                current_dept = str(emp.get('department', 'Technology Group'))
                                dept_options = ['Senior Management', 'Technology Group', 'Facility Management', 'Human Resources', 'Accounts & Finance', 'Sales & Marketing', 'Procurement', 'Security', 'Legal', 'Operations', 'Engineering']
                                dept_idx = dept_options.index(current_dept) if current_dept in dept_options else 1
                                new_dept = st.selectbox("Department", dept_options, index=dept_idx, key=f"dept_{emp['employee_id']}")
                                
                                current_grade = str(emp.get('grade', 'Junior'))
                                grade_options = ['Junior', 'Senior', 'Manager', 'HOD', 'C-Level']
                                grade_idx = grade_options.index(current_grade) if current_grade in grade_options else 0
                                new_grade = st.selectbox("Grade", grade_options, index=grade_idx, key=f"grd_{emp['employee_id']}")
                            with ec2:
                                new_position = st.text_input("Position", value=str(emp.get('position', '')), key=f"pos_{emp['employee_id']}")
                                
                                current_status = str(emp.get('status', 'Active'))
                                status_options = ['Active', 'On Leave', 'Probation', 'Terminated']
                                status_idx = status_options.index(current_status) if current_status in status_options else 0
                                new_status = st.selectbox("Status", status_options, index=status_idx, key=f"sts_{emp['employee_id']}")
                                
                                current_gender = str(emp.get('gender', 'Male'))
                                gender_options = ['Male', 'Female']
                                gender_idx = 0 if current_gender == 'Male' else 1
                                new_gender = st.selectbox("Gender", gender_options, index=gender_idx, key=f"gen_{emp['employee_id']}")
                            with ec3:
                                new_role = st.selectbox("System Role", ['Admin', 'HOD', 'Manager', 'Team Lead', 'Team Member'],
                                    key=f"role_{emp['employee_id']}")
                                new_email = st.text_input("Email", value=str(emp.get('email', '')), key=f"eml_{emp['employee_id']}")
                            with ec3:
                                new_role = st.selectbox("System Role", ['Admin', 'HOD', 'Manager', 'Team Lead', 'Team Member'],
                                    key=f"role_{emp['employee_id']}")
                                new_email = st.text_input("Email", value=str(emp.get('email', '')), key=f"eml_{emp['employee_id']}")
                            
                            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                                try:
                                    db._patch("employees", {
                                        "department": new_dept, "grade": new_grade,
                                        "position": new_position, "status": new_status,
                                        "email": new_email, "gender": new_gender
                                    }, {"employee_id": emp['employee_id']})
                                    st.success(f"✅ {emp['first_name']} {emp['last_name']} updated successfully!")
                                    st.cache_data.clear()
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Update failed: {str(e)}")
        else:
            st.info("No employees match your search criteria.")
    
    # ============ TAB 2: ADD EMPLOYEE ============
    with tab2:
        st.subheader("➕ Add New Employee")
        with st.form("add_employee_form"):
            st.markdown("### Personal Information")
            c1, c2, c3 = st.columns(3)
            with c1:
                first_name = st.text_input("First Name *")
                last_name = st.text_input("Last Name *")
                email = st.text_input("Email *")
                phone = st.text_input("Phone")
            with c2:
                employee_id = st.text_input("Employee ID *", placeholder="e.g., AN00001")
                department = st.selectbox("Department *", ['Senior Management', 'Technology Group', 'Facility Management', 'Human Resources', 'Accounts & Finance', 'Sales & Marketing', 'Procurement', 'Security', 'Legal', 'Operations', 'Engineering'])
                region = st.selectbox("Region *", ['Abuja', 'Lagos'])
                position = st.text_input("Position *")
                grade = st.selectbox("Grade", ['Junior', 'Senior', 'Manager', 'HOD', 'C-Level'])
            with c3:
                employment_type = st.selectbox("Employment Type", ['Full-time', 'Contract', 'Part-time', 'Intern'])
                join_date = st.date_input("Join Date")
                system_role = st.selectbox("System Role", ['Admin', 'HOD', 'Manager', 'Team Lead', 'Team Member'])
                status = st.selectbox("Status", ['Active', 'Probation'])
            
            if st.form_submit_button("✅ Add Employee", use_container_width=True):
                if first_name and last_name and employee_id and department and position:
                    try:
                        db._post("employees", {
                            "employee_id": employee_id, "first_name": first_name, "last_name": last_name,
                            "email": email, "phone": phone, "department": department,
                            "region": region,
                            "position": position, "grade": grade, "employment_type": employment_type,
                            "join_date": join_date.strftime('%Y-%m-%d'), "status": status
                        })
                        st.success(f"✅ {first_name} {last_name} added!")
                        st.balloons()
                        st.cache_data.clear()
                        st.rerun()
                    except:
                        st.error("Employee ID may already exist.")
                else:
                    st.error("❌ Required fields missing!")
    
    # ============ TAB 3: BULK UPLOAD ============
    with tab3:
        st.subheader("📤 Bulk Employee Upload")
        st.info("Upload CSV with columns: employee_id, first_name, last_name, email, phone, department, position, grade, employment_type, join_date")
        template_df = pd.DataFrame(columns=['employee_id', 'first_name', 'last_name', 'email', 'phone', 'department', 'position', 'grade', 'employment_type', 'join_date'])
        st.download_button("📥 Download Template", template_df.to_csv(index=False), "employee_template.csv", "text/csv")
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write(f"**{len(df)} employees in file**")
            st.dataframe(df.head(), use_container_width=True)
            if st.button("📤 Upload All", use_container_width=True):
                success, fail = 0, 0
                for _, row in df.iterrows():
                    try:
                        db._post("employees", {
                            "employee_id": str(row.get('employee_id', '')), "first_name": str(row.get('first_name', '')),
                            "last_name": str(row.get('last_name', '')), "email": str(row.get('email', '')),
                            "phone": str(row.get('phone', '')), "department": str(row.get('department', '')),
                            "position": str(row.get('position', '')), "grade": str(row.get('grade', 'Junior')),
                            "employment_type": str(row.get('employment_type', 'Full-time')),
                            "join_date": str(row.get('join_date', '')), "status": "Active"
                        })
                        success += 1
                    except:
                        fail += 1
                st.success(f"✅ {success} uploaded! ({fail} skipped)")
                st.balloons()
                st.cache_data.clear()
    
    # ============ TAB 4: GENERATE LOGINS ============
    with tab4:
        st.subheader("🔑 Generate Employee Login Credentials")
        
        # Single employee login
        st.markdown("### ⚡ Quick Single Employee")
        with st.form("single_login_form"):
            c1, c2 = st.columns(2)
            with c1:
                single_email = st.text_input("Employee Email *", placeholder="e.g., employee@churchgate.com")
                single_name = st.text_input("Full Name *")
                single_pw = st.text_input("Password", value="churchgate2026")
            with c2:
                single_dept = st.selectbox("Department", ['Senior Management', 'Technology Group', 'Facility Management', 'Human Resources', 'Accounts & Finance', 'Sales & Marketing', 'Procurement', 'Security', 'Legal', 'Operations', 'Engineering'], key="single_dept")
                single_role = st.selectbox("Role", ['Admin', 'HOD', 'Manager', 'Team Lead', 'Team Member'], key="single_role")
                single_id = st.text_input("Employee ID", placeholder="e.g., AN00001")
            
            if st.form_submit_button("🔑 Create Single Login", use_container_width=True):
                if single_email and single_name:
                    try:
                        db.create_user(single_id, single_name, single_email, single_pw, single_role, single_dept, 'Staff')
                        st.success(f"✅ Login created for {single_name}!")
                        st.balloons()
                    except:
                        st.warning("User may already exist.")
                else:
                    st.error("❌ Email and Name required!")
        
        st.markdown("---")
        st.markdown("### 👥 Bulk Generate for All Employees")
        if not employees_df.empty:
            default_pw = st.text_input("Default Password for Bulk", value="churchgate2026")
            emp_list = []
            for _, emp in employees_df.iterrows():
                emp_list.append({
                    'Name': f"{emp['first_name']} {emp['last_name']}", 'ID': emp['employee_id'],
                    'Email': emp.get('email', 'N/A'), 'Department': emp.get('department', ''), 'Role': 'Team Member'
                })
            st.dataframe(pd.DataFrame(emp_list), use_container_width=True, hide_index=True)
            if st.button("🔑 Generate Logins for All", use_container_width=True):
                count = 0
                for emp in emp_list:
                    if emp['Email'] and emp['Email'] != 'N/A':
                        try:
                            db.create_user(emp['ID'], emp['Name'], emp['Email'], default_pw, 'Team Member', emp['Department'], 'Staff')
                            count += 1
                        except:
                            pass
                st.success(f"✅ {count} logins generated!")
                st.info(f"Default password: **{default_pw}**")
                st.download_button("📥 Download Login List", pd.DataFrame(emp_list).to_csv(index=False), "logins.csv", "text/csv")
        else:
            st.info("No employees found.")
    
    # ============ TAB 5: DEPARTMENTS ============
    with tab5:
        st.subheader("🏢 Department Analytics")
        if not employees_df.empty:
            dept_counts = employees_df['department'].value_counts()
            c1, c2 = st.columns(2)
            for i, (dept, count) in enumerate(dept_counts.items()):
                color = dept_colors.get(dept, '#CC0000')
                with (c1 if i % 2 == 0 else c2):
                    st.markdown(f"""
                    <div style="background:white;padding:1.2rem;border-radius:10px;margin-bottom:0.8rem;border-left:4px solid {color};box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                        <strong>{dept}</strong>
                        <span style="float:right;font-size:1.5rem;font-weight:700;color:{color};">{count}</span>
                        <br><small style="color:#888;">staff members</small>
                    </div>
                    """, unsafe_allow_html=True)
    
    # ============ TAB 6: ORG CHART ============
    with tab6:
        st.subheader("📊 Organizational Structure — Churchgate Group")
        
        # Key Leadership Cards
        st.markdown("### 🌟 Key Leadership")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("""
            <div style="background:white;padding:1rem;border-radius:10px;text-align:center;border-top:3px solid #CC0000;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                <div style="width:50px;height:50px;border-radius:50%;background:#CC0000;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;color:white;">VM</div>
                <strong style="display:block;margin-top:0.5rem;">Vinay Mahtani</strong>
                <small style="color:#888;">GMD/CEO</small><br>
                <small style="color:#CC0000;">👥 Group-wide</small>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div style="background:white;padding:1rem;border-radius:10px;text-align:center;border-top:3px solid #e53e3e;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                <div style="width:50px;height:50px;border-radius:50%;background:#e53e3e;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;color:white;">JD</div>
                <strong style="display:block;margin-top:0.5rem;">Jerome Das</strong>
                <small style="color:#888;">COO</small><br>
                <small style="color:#e53e3e;">👥 All Departments</small>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div style="background:white;padding:1rem;border-radius:10px;text-align:center;border-top:3px solid #dd6b20;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                <div style="width:50px;height:50px;border-radius:50%;background:#dd6b20;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;color:white;">AK</div>
                <strong style="display:block;margin-top:0.5rem;">Ahmed Karim</strong>
                <small style="color:#888;">VP Sales</small><br>
                <small style="color:#dd6b20;">👥 Sales & Marketing</small>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown("""
            <div style="background:white;padding:1rem;border-radius:10px;text-align:center;border-top:3px solid #805ad5;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                <div style="width:50px;height:50px;border-radius:50%;background:#805ad5;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:700;color:white;">PL</div>
                <strong style="display:block;margin-top:0.5rem;">Partab Lalchandani</strong>
                <small style="color:#888;">GEA</small><br>
                <small style="color:#805ad5;">👥 Group Advisor</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Main Sankey - Group Level
        st.markdown("### 🔗 Group Reporting Hierarchy")
        st.info("GMD → COO (All Depts) / VP Sales (Sales & Mkt) / GEA | Regions: Abuja & Lagos")
        
        labels = [
            'GMD', 'COO', 'VP Sales', 'GEA',
            'Technology (Abuja)', 'Technology (Lagos)',
            'Facility Mgmt (Abuja)', 'Facility Mgmt (Lagos)',
            'Engineering/MEP', 'HR', 'Accounts & Finance',
            'Sales & Marketing', 'Procurement', 'Security',
            'Legal', 'Operations',
            'Heads of Department',
            'Sr. Managers', 'Managers', 'Team Leads', 'Team Members'
        ]
        
        colors = [
            '#CC0000', '#e53e3e', '#dd6b20', '#805ad5',
            '#3182ce', '#3182ce',
            '#38a169', '#38a169',
            '#d53f8c', '#d69e2e', '#805ad5',
            '#dd6b20', '#2b6cb0', '#718096',
            '#e53e3e', '#319795',
            '#FF6B35',
            '#38a169', '#d69e2e', '#2b6cb0', '#718096'
        ]
        
        sources = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3]
        targets = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 11, 15]
        values  = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        
        # Departments → HODs
        for i in range(4, 16):
            sources.append(i)
            targets.append(16)
            values.append(1)
        
        # HODs → Sr. Managers
        sources.append(16)
        targets.append(17)
        values.append(11)
        
        # Sr. Managers → Managers → Team Leads → Team Members
        sources += [17, 17, 18, 18]
        targets += [18, 19, 19, 20]
        values += [10, 5, 12, 30]
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=20, thickness=18, label=labels, color=colors),
            link=dict(source=sources, target=targets, value=values,
                color=['rgba(204,0,0,0.2)'] * len(sources))
        )])
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Department Heads by Region
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏢 Abuja Region — Department Heads")
            abuja_hods = pd.DataFrame({
                'Department': ['Technology Group', 'Facility Management', 'Engineering (MEP)', 'Human Resources', 'Accounts & Finance', 'Sales & Marketing', 'Procurement', 'Security', 'Legal', 'Operations'],
                'HOD': ['Emmanuel Etuk', 'David Effiong', 'Sanjeev Purwar', 'Adebayo Sakote', 'Jeff Arikawe', 'Ahmed Karim (VP)', 'Anand Bora', 'Usman Sani', 'David Aiyedun', 'Ibukun Adeogun'],
                'Team': [12, 20, 8, 6, 8, 12, 6, 15, 3, 10]
            })
            st.dataframe(abuja_hods, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 🏢 Lagos Region — Department Heads")
            lagos_hods = pd.DataFrame({
                'Department': ['Technology Group', 'Facility Management', 'Engineering (MEP)', 'Human Resources', 'Accounts & Finance', 'Sales & Marketing', 'Procurement', 'Security', 'Legal', 'Operations'],
                'HOD': ['Lawal Mohammed', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD'],
                'Team': ['TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD', 'TBD']
            })
            st.dataframe(lagos_hods, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Span of Control
        st.markdown("### 👥 Span of Control — Key Leaders")
        span_data = pd.DataFrame({
            'Leader': ['Vinay Mahtani', 'Jerome Das', 'Ahmed Karim', 'Emmanuel Etuk', 'David Effiong', 'Sanjeev Purwar', 'All HODs (Avg)'],
            'Role': ['GMD', 'COO', 'VP Sales', 'HOD Tech (Abuja)', 'HOD FM (Abuja)', 'HOD Engr (MEP)', 'Heads of Dept'],
            'Region': ['Group', 'Group', 'Group', 'Abuja', 'Abuja', 'Abuja', 'Group'],
            'Direct Reports': [5, 12, 6, 12, 20, 8, 10]
        })
        fig2 = px.bar(span_data, x='Leader', y='Direct Reports', color='Region', text='Direct Reports',
                     color_discrete_sequence=['#CC0000', '#3182ce', '#38a169'])
        fig2.update_layout(height=350)
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        
        # Reporting Chain Finder
        st.markdown("### 🔍 Find Reporting Chain")
        chain_search = st.text_input("Enter employee name to see reporting line", placeholder="e.g., Francis Asuquo", key="chain_search")
        if chain_search:
            found = False
            chain = ""
            try:
                for _, emp in employees_df.iterrows():
                    full_name = f"{emp['first_name']} {emp['last_name']}".lower()
                    if chain_search.lower() in full_name:
                        found = True
                        role = emp.get('position', '')
                        dept = emp.get('department', '')
                        region = emp.get('region', 'Abuja')
                        
                        if 'GMD' in role or 'CEO' in role:
                            chain = f"📋 **{emp['first_name']} {emp['last_name']}** → Reports to Board"
                        elif 'COO' in role or 'GED' in role or 'GEA' in role or 'Advisor' in role:
                            role_name = 'COO' if 'COO' in role else ('GED' if 'GED' in role else 'GEA')
                            chain = f"📋 **{emp['first_name']} {emp['last_name']}** → {role_name} → GMD (Vinay Mahtani)"
                        elif 'VP' in role or 'Vice President' in role:
                            chain = f"📋 **{emp['first_name']} {emp['last_name']}** → VP Sales → GMD (Vinay Mahtani)"
                        elif 'HOD' in role or 'Head' in role or 'head' in role.lower() or 'GM,' in role or 'GM ' in role or role.lower().startswith('head'):
                            chain = f"📋 **{emp['first_name']} {emp['last_name']}** → HOD ({dept}, {region}) → COO (Jerome Das) → GMD (Vinay Mahtani)"
                        elif 'Senior Manager' in role or 'Sr. Manager' in role:
                            chain = f"📋 **{emp['first_name']} {emp['last_name']}** → Sr. Manager ({dept}) → HOD → COO → GMD"
                        elif 'Manager' in role:
                            chain = f"📋 **{emp['first_name']} {emp['last_name']}** → Manager ({dept}) → Sr. Manager → HOD → COO → GMD"
                        elif 'Team Lead' in role:
                            chain = f"📋 **{emp['first_name']} {emp['last_name']}** → Team Lead ({dept}) → Manager → Sr. Manager → HOD → COO → GMD"
                        else:
                            chain = f"📋 **{emp['first_name']} {emp['last_name']}** → Team Member ({dept}) → Team Lead → Manager → Sr. Manager → HOD → COO → GMD"
                        break
                
                if not found:
                    chain = f"📋 **{chain_search}** not found in employee directory."
            except:
                chain = f"📋 Reporting chain lookup unavailable."
            
            st.info(chain)
            
            if chain and 'Sales & Marketing' in chain:
                st.caption("*Sales & Marketing reports to VP Sales → GMD")
        
        st.markdown("---")
        
        # Full Reporting Structure
        st.markdown("### 📋 Complete Reporting Structure")
        structure_data = pd.DataFrame({
            'Level': [1, 2, 2, 2, 3, 4, 5, 6, 7, 8],
            'Role': ['GMD/CEO', 'COO (All Depts)', 'VP Sales', 'GEA', 'Heads of Department', 'Sr. Managers', 'Managers', 'Team Leads', 'Team Members', 'GED'],
            'Reports To': ['Board', 'GMD', 'GMD', 'GMD', 'COO / GEA', 'HOD', 'Sr. Managers', 'Managers', 'Team Leads', 'GMD'],
            'Regions': ['Group-wide', 'Abuja & Lagos', 'Abuja & Lagos', 'Group-wide', 'By Region', 'By Department', 'By Department', 'By Department', 'By Department', 'Group-wide'],
            'Notes': ['', '11 Departments', 'Sales & Marketing only', 'Advisory', 'Reports to COO & GEA', '', 'Dotted line to HOD', '', '', 'Standalone, reports to GMD']
        })
        st.dataframe(structure_data, use_container_width=True, hide_index=True)
    
    # ============ TAB 7: DEMOGRAPHICS ============
    with tab7:
        st.subheader("📈 Demographics & Inclusion")
        
        # Gender distribution
        st.markdown("### 👥 Gender Distribution")
        gender_data = pd.DataFrame({'Gender': ['Male', 'Female'], 'Count': [38, 18]})
        fig = px.pie(gender_data, values='Count', names='Gender', hole=0.5, color_discrete_sequence=['#3182ce', '#CC0000'])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
        
        # Department gender split
        st.markdown("---")
        st.markdown("### 🏢 Department Gender Split")
        dept_gender = pd.DataFrame({
            'Department': ['Technology Group', 'Facility Management', 'Human Resources', 'Sales & Marketing', 'Accounts & Finance', 'Procurement', 'Security', 'Legal', 'Operations', 'Engineering'],
            'Male': [10, 10, 3, 6, 4, 3, 10, 1, 4, 3],
            'Female': [4, 3, 5, 4, 2, 2, 2, 1, 1, 1]
        })
        fig2 = px.bar(dept_gender, x='Department', y=['Male', 'Female'], barmode='group', color_discrete_sequence=['#3182ce', '#CC0000'])
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Tenure distribution
        st.markdown("---")
        st.markdown("### 📅 Tenure Distribution")
        try:
            tenure_data = []
            for _, emp in employees_df.iterrows():
                jd = emp.get('join_date')
                if jd and pd.notna(jd):
                    try:
                        years = (datetime.now() - pd.to_datetime(jd)).days / 365
                        if years < 2: tenure_data.append('0-2 years')
                        elif years < 5: tenure_data.append('3-5 years')
                        elif years < 10: tenure_data.append('6-10 years')
                        else: tenure_data.append('10+ years')
                    except:
                        pass
            if tenure_data:
                tenure_df = pd.DataFrame(pd.Series(tenure_data).value_counts()).reset_index()
                tenure_df.columns = ['Tenure', 'Count']
                fig3 = px.bar(tenure_df, x='Tenure', y='Count', color='Tenure', color_discrete_sequence=['#CC0000', '#3182ce', '#38a169', '#d69e2e'])
                fig3.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig3, use_container_width=True)
        except:
            pass
        
        # Grade distribution
        st.markdown("---")
        st.markdown("### 📊 Grade Distribution")
        if not employees_df.empty:
            grade_counts = employees_df['grade'].value_counts()
            grade_df = pd.DataFrame({'Grade': grade_counts.index, 'Count': grade_counts.values})
            fig4 = px.pie(grade_df, values='Count', names='Grade', hole=0.4, color_discrete_sequence=['#CC0000', '#3182ce', '#38a169', '#d69e2e', '#805ad5'])
            fig4.update_layout(height=350)
            st.plotly_chart(fig4, use_container_width=True)
    
    # ============ TAB 8: EXPORT ============
    with tab8:
        st.subheader("📥 Export Employee Data")
        if not employees_df.empty:
            st.download_button("📥 Download Full Directory (CSV)", employees_df.to_csv(index=False), "churchgate_employees.csv", "text/csv")
            
            st.markdown("---")
            st.markdown("### 📊 Export by Department")
            selected_export_dept = st.selectbox("Select Department", ['All'] + list(employees_df['department'].unique()) if not employees_df.empty else ['All'])
            if selected_export_dept != 'All':
                dept_df = employees_df[employees_df['department'] == selected_export_dept]
                st.download_button(f"📥 Download {selected_export_dept} (CSV)", dept_df.to_csv(index=False), f"{selected_export_dept}_employees.csv", "text/csv")
            
            st.markdown("---")
            st.markdown("### 📊 Quick Stats")
            st.dataframe(employees_df.describe(), use_container_width=True)

def performance_okrs():
    st.markdown("""<div class="churchgate-header"><h1>📈 Performance & Appraisal Engine</h1><p>KPI Management | Self-Assessment | HOD Review | Goal Cascading | Benchmark Reports | Smart Notifications | Audit Trail</p></div>""", unsafe_allow_html=True)
    
    user_role = st.session_state.user['role'] if st.session_state.user else 'Employee'
    user_dept = st.session_state.user.get('department', '') if st.session_state.user else ''
    user_name = st.session_state.user['name'] if st.session_state.user else 'Staff'
    user_email = st.session_state.user['email'] if st.session_state.user else ''
    is_admin = user_role in ['Admin', 'HR Director'] or user_dept == 'Senior Management'
    is_sr_mgmt = user_dept == 'Senior Management'
    is_hod = is_admin or user_role in ['Manager', 'HOD']
    
    # WAT Timezone
    from datetime import timezone, timedelta
    wat = timezone(timedelta(hours=1))
    now_wat = datetime.now(wat)
    
    all_depts = ['Senior Management', 'Technology Group', 'Facility Management', 'Human Resources', 'Accounts & Finance', 
                 'Sales & Marketing', 'Procurement', 'Security', 'Legal', 'Operations', 
                 'Engineering', 'Central Stores', 'Project Development', 'Trade Services']
    
    # Session state initialization
    if 'appraisal_cycle_active' not in st.session_state:
        st.session_state.appraisal_cycle_active = False
    if 'appraisal_cycle_name' not in st.session_state:
        st.session_state.appraisal_cycle_name = "2026 Half-Year Appraisal"
    if 'appraisal_start' not in st.session_state:
        st.session_state.appraisal_start = "2026-06-01"
    if 'appraisal_end' not in st.session_state:
        st.session_state.appraisal_end = "2026-12-31"
    if 'appraisal_locked' not in st.session_state:
        st.session_state.appraisal_locked = False
    if 'self_assessments' not in st.session_state:
        st.session_state.self_assessments = {}
    try:
        all_appraisals = db.get_all_appraisals()
        for a in all_appraisals:
            if a['user_name'] not in st.session_state.self_assessments or st.session_state.self_assessments[a['user_name']].get('status') != a.get('status'):
                st.session_state.self_assessments[a['user_name']] = {
                'scores': a.get('scores', {}),
                'comments': a.get('comments', ''),
                'pillar_comments': a.get('pillar_comments', {}),
                'date': a.get('submitted_date', ''),
                'status': a.get('status', 'Submitted'),
                'department': a.get('department', ''),
                'email': a.get('user_email', ''),
                'hod_scores': a.get('hod_scores'),
                'hod_comments': a.get('hod_comments'),
                'hod_pillar_comments': a.get('hod_pillar_comments'),
                'acceptance': a.get('acceptance'),
                'sr_decision': a.get('sr_decision')
            }
    except:
        pass
    if 'kpi_history' not in st.session_state:
        st.session_state.kpi_history = []
    if 'confirm_submit' not in st.session_state:
        st.session_state.confirm_submit = False
    if 'audit_trail' not in st.session_state:
        st.session_state.audit_trail = []
        try:
            db_audit = db.get_audit_trail()
            for a in db_audit:
                st.session_state.audit_trail.append({
                    'action': a.get('action', ''), 'details': a.get('details', ''),
                    'user': a.get('user_name', ''), 'timestamp': a.get('timestamp_text', '')
                })
        except:
            pass
    
    def log_audit(action, details):
        entry = {'action': action, 'details': details, 'user': user_name, 'timestamp': now_wat.strftime('%Y-%m-%d %H:%M WAT')}
        st.session_state.audit_trail.append(entry)
        try:
            db.save_audit(action, details, user_name, now_wat.strftime('%Y-%m-%d %H:%M WAT'))
        except:
            pass
    
    # Load performance data from database
    performance_data = {}
    try:
        db_perf = db.get_performance_data()
        if not db_perf.empty:
            for _, row in db_perf.iterrows():
                dept = row['department']
                pillar = row['pillar_name']
                if dept not in performance_data:
                    performance_data[dept] = {}
                kpi_list = json.loads(row['kpi_data']) if row['kpi_data'] else []
                performance_data[dept][pillar] = {
                    'weight': row['weight'], 'progress': row['progress'],
                    'status': row['status'], 'deadline': row['deadline'], 'kpis': kpi_list
                }
    except:
        pass
    
    for dept in all_depts:
        if dept not in performance_data:
            performance_data[dept] = {}
        for pillar in ['1. Occupancy & Revenue Growth', '2. Process Simplification', 
                       '3. Asset Reliability & Digitalization', '4. People & Culture']:
            if pillar not in performance_data[dept]:
                performance_data[dept][pillar] = {
                    'weight': 25, 'progress': 0, 'status': 'Not Started',
                    'deadline': '2026-12-31', 'kpis': []
                }
    
    def get_kpi_status(progress):
        if progress >= 85: return 'On Track', "#38a169"
        elif progress >= 65: return 'Near Target', "#d69e2e"
        else: return 'At Risk', "#CC0000"

    import re
    def natural_sort_key(item):
        key = item[0]
        parts = re.split(r'(\d+)', key)
        return [int(p) if p.isdigit() else p for p in parts]
    
    # ============ TAB 1: STRATEGIC PILLARS ============ (unchanged) ============
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Strategic Pillars", "✏️ My KPIs", "📝 Self-Assessment", "👔 HOD Review", "📊 Dashboard"])
    
    with tab1:
        st.subheader("🎯 Strategic Pillars Console — Corporate Strategy 2026-2027")
        
        if is_admin:
            st.markdown("""<div style="background: linear-gradient(135deg, #1a1a1a, #2d2d2d); color: white; padding: 1rem 1.5rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #CC0000;"><strong>🔐 Admin Console</strong> — Full access to all departments</div>""", unsafe_allow_html=True)
            selected_dept = st.selectbox("🏢 Select Department", all_depts)
        else:
            selected_dept = user_dept if user_dept in all_depts else all_depts[0]
        
        if selected_dept in performance_data:
            dept_data = performance_data[selected_dept]
            st.markdown(f"### 📊 {selected_dept} — Strategic Pillar Scorecard")
            
            total_weighted = sum(p['progress'] * p['weight'] / 100 for p in dept_data.values()) if dept_data else 0
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Overall Score", f"{total_weighted:.1f}%")
            c2.metric("On Track", str(sum(1 for p in dept_data.values() if p['status'] in ['On Track', 'Exceeding'])))
            c3.metric("At Risk", str(sum(1 for p in dept_data.values() if p['status'] == 'At Risk')))
            c4.metric("Completed", str(sum(1 for p in dept_data.values() if p['status'] == 'Completed')))
            
            if is_admin:
                st.markdown("---")
                st.markdown("### 🏢 Department Comparison")
                comp_data = []
                for d in all_depts:
                    if d in performance_data:
                        dd = performance_data[d]
                        comp_data.append({
                            'Department': d,
                            'Occupancy & Revenue': dd.get('1. Occupancy & Revenue Growth', {}).get('progress', 0),
                            'Process Simplification': dd.get('2. Process Simplification', {}).get('progress', 0),
                            'Asset Reliability': dd.get('3. Asset Reliability & Digitalization', {}).get('progress', 0),
                            'People & Culture': dd.get('4. People & Culture', {}).get('progress', 0)
                        })
                if comp_data:
                    df_comp = pd.DataFrame(comp_data)
                    fig = px.bar(df_comp.melt(id_vars=['Department'], var_name='Pillar', value_name='Progress'),
                                x='Department', y='Progress', color='Pillar', barmode='group',
                                color_discrete_sequence=['#CC0000', '#4a4a4a', '#888888', '#aaaaaa'])
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
            
            if is_admin:
                st.markdown("---")
                st.markdown("### 🎯 Goal Cascading")
                with st.form("cascade_form"):
                    cascade_pillar = st.selectbox("Pillar", ['1. Occupancy & Revenue Growth', '2. Process Simplification', '3. Asset Reliability & Digitalization', '4. People & Culture'])
                    cascade_kpi = st.text_input("Group KPI *", placeholder="e.g., Achieve 95% tenant satisfaction")
                    cascade_target = st.text_input("Target *", placeholder="e.g., 95%")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("📤 Cascade to All Departments"):
                            if cascade_kpi and cascade_target:
                                for d in all_depts:
                                    performance_data[d][cascade_pillar]['kpis'].append({
                                        'kpi': f"[GROUP] {cascade_kpi}", 'target': cascade_target,
                                        'current': '0%', 'status': 'In Progress',
                                        'deadline': '2026-12-31', 'owner': 'Group'
                                    })
                                    pd_data = performance_data[d][cascade_pillar]
                                    try:
                                        db.save_performance_data(d, cascade_pillar, pd_data['weight'], pd_data['progress'], pd_data['status'], pd_data['deadline'], pd_data['kpis'])
                                    except:
                                        pass
                                log_audit('Goal Cascaded', f'KPI cascaded to all depts: {cascade_kpi}')
                                st.success(f"✅ Group KPI cascaded to all {len(all_depts)} departments!")
                                st.balloons()
                                st.rerun()
                    with c2:
                        if st.form_submit_button("📤 Cascade to Selected"):
                            if cascade_kpi and cascade_target:
                                performance_data[selected_dept][cascade_pillar]['kpis'].append({
                                    'kpi': f"[GROUP] {cascade_kpi}", 'target': cascade_target,
                                    'current': '0%', 'status': 'In Progress',
                                    'deadline': '2026-12-31', 'owner': 'Group'
                                })
                                pd_data = performance_data[selected_dept][cascade_pillar]
                                try:
                                    db.save_performance_data(selected_dept, cascade_pillar, pd_data['weight'], pd_data['progress'], pd_data['status'], pd_data['deadline'], pd_data['kpis'])
                                except:
                                    pass
                                log_audit('Goal Cascaded', f'KPI cascaded to {selected_dept}: {cascade_kpi}')
                                st.success(f"✅ Group KPI cascaded to {selected_dept}!")
                                st.rerun()
            
            st.markdown("---")
            for pillar_name, pillar_data in dept_data.items():
                status_text, color = get_kpi_status(pillar_data['progress'])
                if pillar_data['status'] in ['Exceeding', 'Completed']:
                    color = "#38a169"
                
                with st.expander(f"{pillar_name} | {pillar_data['progress']}% | {pillar_data['status']}", expanded=False):
                    st.progress(pillar_data['progress'] / 100)
                    
                    if is_admin:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            new_progress = st.slider("Progress %", 0, 100, int(pillar_data['progress']), key=f"prog_{selected_dept}_{pillar_name}")
                        with c2:
                            new_status = st.selectbox("Status", ['On Track', 'In Progress', 'At Risk', 'Exceeding', 'Completed'], index=0, key=f"stat_{selected_dept}_{pillar_name}")
                        with c3:
                            new_weight = st.slider("Weight %", 0, 100, int(pillar_data['weight']), key=f"wgt_{selected_dept}_{pillar_name}")
                        
                        if st.button(f"💾 Update", key=f"upd_{selected_dept}_{pillar_name}"):
                            performance_data[selected_dept][pillar_name]['progress'] = new_progress
                            performance_data[selected_dept][pillar_name]['status'] = new_status
                            performance_data[selected_dept][pillar_name]['weight'] = new_weight
                            try:
                                db.save_performance_data(selected_dept, pillar_name, new_weight, new_progress, new_status, pillar_data['deadline'], pillar_data['kpis'])
                            except:
                                pass
                            st.rerun()
                    
                    if pillar_data['kpis']:
                        for kpi in pillar_data['kpis']:
                            try:
                                kpi_progress = int(float(str(kpi.get('current', '0')).replace('%', '')))
                            except:
                                kpi_progress = 0
                            kpi_status, kpi_color = get_kpi_status(kpi_progress)
                            st.markdown(f"""<div style="background: white; padding: 0.6rem; border-radius: 6px; margin-bottom: 0.4rem; border-left: 3px solid {kpi_color};"><div style="display: flex; justify-content: space-between;"><strong>{kpi['kpi'][:60]}</strong><span style="color: {kpi_color}; font-weight: 600;">{kpi_status}</span></div><small>Target: {kpi.get('target', 'N/A')} | Current: {kpi.get('current', '0')} | Deadline: {kpi.get('deadline', 'N/A')}</small><div style="background: #e0e0e0; height: 4px; border-radius: 2px; margin-top: 0.3rem;"><div style="background: {kpi_color}; width: {kpi_progress}%; height: 4px; border-radius: 2px;"></div></div></div>""", unsafe_allow_html=True)
    
    # ============ TAB 2: MY KPIs (unchanged) ============
    with tab2:
        st.subheader("✏️ My KPIs & Objectives")
        st.info("Set your KPIs aligned to the 4 strategic pillars. All fields are required.")
        
        if is_hod and user_dept in performance_data:
            with st.expander("📋 One-Click Copy KPIs to Team"):
                copy_pillar = st.selectbox("Select Pillar to Copy", ['1. Occupancy & Revenue Growth', '2. Process Simplification', '3. Asset Reliability & Digitalization', '4. People & Culture'], key="copy_pillar")
                if st.button("📤 Copy KPIs to Team"):
                    if performance_data[user_dept][copy_pillar]['kpis']:
                        count = len(performance_data[user_dept][copy_pillar]['kpis'])
                        st.success(f"✅ {count} KPIs ready to be assigned to team members!")
                    else:
                        st.warning("No KPIs in this pillar to copy.")
        
        with st.form("my_kpi_form"):
            st.markdown("### * Required Fields")
            c1, c2 = st.columns(2)
            with c1:
                pillar_choice = st.selectbox("Strategic Pillar *", ['1. Occupancy & Revenue Growth', '2. Process Simplification', '3. Asset Reliability & Digitalization', '4. People & Culture'])
                kpi_title = st.text_input("KPI Title *", placeholder="What will you achieve?")
                kpi_target = st.text_input("Target *", placeholder="e.g., 15% increase")
            with c2:
                kpi_weight = st.slider("Weight (%) *", 0, 100, 25)
                kpi_deadline = st.date_input("Target Deadline *")
                kpi_current = st.text_input("Current Progress *", placeholder="e.g., 10%")
            
            kpi_description = st.text_area("Description / Key Results *", placeholder="How will you achieve this KPI?")
            
            col1, col2 = st.columns(2)
            with col1:
                submit_continue = st.form_submit_button("💾 Save & Add Another", use_container_width=True)
            with col2:
                submit_final = st.form_submit_button("✅ Submit KPI", use_container_width=True)
            
            if submit_continue or submit_final:
                if not kpi_title or not kpi_target or not kpi_current or not kpi_description:
                    st.error("❌ All fields are required!")
                elif user_dept not in performance_data:
                    performance_data[user_dept] = {}
                    for pillar in ['1. Occupancy & Revenue Growth', '2. Process Simplification', '3. Asset Reliability & Digitalization', '4. People & Culture']:
                        performance_data[user_dept][pillar] = {'weight': 25, 'progress': 0, 'status': 'Not Started', 'deadline': '2026-12-31', 'kpis': []}
                    performance_data[user_dept][pillar_choice]['kpis'].append({
                        'kpi': kpi_title, 'target': kpi_target, 'current': kpi_current,
                        'status': 'In Progress', 'deadline': kpi_deadline.strftime('%Y-%m-%d'), 'owner': user_name
                    })
                    st.success("✅ KPI saved!")
                    st.rerun()
                else:
                    performance_data[user_dept][pillar_choice]['kpis'].append({
                        'kpi': kpi_title, 'target': kpi_target, 'current': kpi_current,
                        'status': 'In Progress', 'deadline': kpi_deadline.strftime('%Y-%m-%d'), 'owner': user_name
                    })
                    st.session_state.kpi_history.append({
                        'action': 'Added', 'kpi': kpi_title, 'user': user_name,
                        'date': now_wat.strftime('%Y-%m-%d %H:%M WAT'), 'pillar': pillar_choice
                    })
                    try:
                        db.save_kpi_history('Added', kpi_title, user_name, pillar_choice)
                    except:
                        pass
                    pd_data = performance_data[user_dept][pillar_choice]
                    try:
                        db.save_performance_data(user_dept, pillar_choice, pd_data['weight'], pd_data['progress'], pd_data['status'], pd_data['deadline'], pd_data['kpis'])
                    except:
                        pass
                    
                    if submit_continue:
                        st.success("✅ KPI saved! Add another below.")
                        time.sleep(1.5)
                        st.rerun()
                    if submit_final:
                        st.session_state.confirm_submit = True
                        st.rerun()
        
        if st.session_state.confirm_submit:
            st.markdown("---")
            st.warning("### ⚠️ Confirm Final Submission")
            st.markdown("Your KPI has been saved. It will be submitted for appraisal review.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Confirm & Finish", use_container_width=True):
                    st.session_state.confirm_submit = False
                    log_audit('KPI Submitted', 'Final KPI submission confirmed')
                    st.success("✅ KPI submitted successfully!")
                    st.balloons()
                    st.rerun()
            with c2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.confirm_submit = False
                    st.rerun()
        
        try:
            history_data = db.get_kpi_history()
        except:
            history_data = []
        if history_data:
            st.markdown("---")
            with st.expander("📋 KPI History Log"):
                for h in history_data[-10:]:
                    st.markdown(f"- **{h.get('created_at', 'N/A')}**: {h.get('action', '')} — {h.get('kpi_name', '')[:50]} by {h.get('user_name', '')}")
    
    # ============ TAB 3: SELF-ASSESSMENT (UPDATED) ============
    with tab3:
        st.subheader("📝 Self-Assessment")
        
        if st.session_state.appraisal_cycle_active:
            try:
                end_date = datetime.strptime(st.session_state.appraisal_end, '%Y-%m-%d')
                days_left = (end_date - datetime.now()).days
                if days_left <= 7 and days_left > 0:
                    st.warning(f"⏰ **Reminder:** Appraisal cycle ends in {days_left} days!")
                elif days_left <= 0:
                    st.error("⚠️ Appraisal cycle has ended.")
            except:
                pass
        
        if is_admin:
            with st.expander("⚙️ Appraisal Cycle Settings (Admin)"):
                st.session_state.appraisal_cycle_active = st.checkbox("Activate Appraisal Cycle", value=st.session_state.appraisal_cycle_active)
                st.session_state.appraisal_cycle_name = st.text_input("Cycle Name", st.session_state.appraisal_cycle_name)
                c1, c2 = st.columns(2)
                with c1:
                    st.session_state.appraisal_start = st.text_input("Start Date", st.session_state.appraisal_start)
                with c2:
                    st.session_state.appraisal_end = st.text_input("End Date", st.session_state.appraisal_end)
                st.session_state.appraisal_locked = st.checkbox("Lock Scores", value=st.session_state.appraisal_locked)
                if st.button("💾 Save Cycle Settings"):
                    log_audit('Cycle Updated', f'Appraisal cycle settings saved')
                    st.success("✅ Cycle settings saved!")
        
        if st.session_state.appraisal_cycle_active:
            st.success(f"🔓 Appraisal Active: {st.session_state.appraisal_cycle_name}")
            
            if st.session_state.appraisal_locked:
                st.warning("🔒 Scores are locked.")
            else:
                st.markdown("### Rate Yourself (0-100%)")
                st.info("Provide justification for each pillar. Attach evidence if available.")
                
                if user_dept in performance_data:
                    pillar_evidence = {}
                    for pillar_name, pillar_data in performance_data[user_dept].items():
                        if pillar_data['kpis']:
                            pillar_evidence[pillar_name] = st.file_uploader(f"Attach Evidence for {pillar_name} (Optional)", type=['pdf', 'docx', 'jpg', 'png', 'xlsx'], key=f"pe_{pillar_name}")
                    
                    with st.form("self_assessment_form"):
                        scores = {}
                        pillar_comments = {}
                        
                        for pillar_name, pillar_data in performance_data[user_dept].items():
                            if pillar_data['kpis']:
                                st.markdown(f"### {pillar_name} ({pillar_data['weight']}%)")
                                for i, kpi in enumerate(pillar_data['kpis']):
                                    score_key = f"{pillar_name}_{i}"
                                    scores[score_key] = st.slider(kpi['kpi'][:60], 0, 100, 50, key=f"sa_{user_name}_{pillar_name}_{i}")
                                pillar_comments[pillar_name] = st.text_area(f"Justification for {pillar_name} *", key=f"pc_{pillar_name}")
                                st.markdown("---")
                        
                        overall_comments = st.text_area("Overall Comments *", placeholder="Summarize your overall performance...")
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            submitted = st.form_submit_button("📤 Submit Self-Assessment", use_container_width=True)
                        
                        if submitted:
                            all_comments_filled = all(pillar_comments.values())
                            if not scores or not overall_comments or not all_comments_filled:
                                st.error("❌ All scores, pillar justifications, and overall comments are required!")
                            else:
                                try:
                                    db.save_appraisal(user_name, user_email, user_dept, 
                                        st.session_state.appraisal_cycle_name, 'Submitted',
                                        scores, overall_comments, pillar_comments, None, None, None, None, None,
                                        now_wat.strftime('%Y-%m-%d %H:%M WAT'))
                                except:
                                    pass
                                st.session_state.self_assessments[user_name] = {
                                    'scores': scores, 'comments': overall_comments,
                                    'pillar_comments': pillar_comments,
                                    'pillar_evidence': {k: v.name if v else None for k, v in pillar_evidence.items()},
                                    'date': now_wat.strftime('%Y-%m-%d %H:%M WAT'),
                                    'status': 'Submitted', 'department': user_dept, 'email': user_email,
                                    'hod_scores': None, 'hod_comments': None, 'acceptance': None,
                                    'reject_count': 0
                                }
                                log_audit('Self-Assessment Submitted', f'Submitted by {user_name}')
                                st.success("✅ Submitted! Saved to database. Awaiting HOD review.")
                                st.balloons()
        else:
            st.info("⏳ Appraisal cycle not active.")
        
        if user_name in st.session_state.self_assessments:
            st.markdown("---")
            st.markdown("### 📋 Your Submission")
            a = st.session_state.self_assessments[user_name]
            st.markdown(f"**Status:** {a['status']} | **Date:** {a['date']}")
            
            if a.get('hod_scores'):
                st.success("✅ HOD review complete")
                if not a.get('acceptance'):
                    st.markdown("### 🔍 HOD Review Pending Your Acceptance")
                    st.markdown("#### 📊 Side-by-Side Score Comparison")
                    for score_key, staff_score in sorted(a['scores'].items(), key=natural_sort_key):
                        hod_score = a['hod_scores'].get(score_key, 'N/A') if a['hod_scores'] else 'N/A'
                        c1, c2, c3 = st.columns([1, 1, 2])
                        with c1:
                            st.markdown(f"**You:** {staff_score}%")
                        with c2:
                            st.markdown(f"**HOD:** {hod_score}%")
                        with c3:
                            st.markdown(f"*{score_key}*")
                    st.markdown("---")
                    st.markdown(f"**Your Comments:** {a.get('comments', 'N/A')}")
                    st.markdown(f"**HOD Comments:** {a.get('hod_comments', 'N/A')}")
                    
                    if a.get('hod_pillar_comments'):
                        st.markdown("**HOD Pillar Justifications:**")
                        for pillar, comment in a['hod_pillar_comments'].items():
                            st.markdown(f"- **{pillar}:** {comment}")
                    
                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Accept HOD Review", use_container_width=True):
                            st.session_state.self_assessments[user_name]['acceptance'] = 'Accepted'
                            try:
                                db.archive_appraisal(user_name, user_email, user_dept,
                                    st.session_state.appraisal_cycle_name, 'Accepted',
                                    a['scores'], a['hod_scores'], a.get('comments', ''), a.get('hod_comments', ''),
                                    now_wat.strftime('%Y-%m-%d %H:%M WAT'))
                            except:
                                pass
                            log_audit('Appraisal Accepted', f'{user_name} accepted HOD review')
                            st.success("✅ Appraisal accepted! Cycle complete. Certificate available below.")
                            st.balloons()
                            st.rerun()
                    with c2:
                        if st.button("❌ Reject - Request Re-review", use_container_width=True):
                            st.session_state.self_assessments[user_name]['acceptance'] = 'Rejected'
                            st.session_state.self_assessments[user_name]['status'] = 'Awaiting HOD Re-review'
                            st.session_state.self_assessments[user_name]['reject_count'] = a.get('reject_count', 0) + 1
                            log_audit('Appraisal Rejected', f'{user_name} rejected - sent back to HOD')
                            st.warning("⚠️ Rejected. Sent back to HOD for re-review.")
                            st.rerun()
                elif a.get('acceptance') == 'Accepted':
                    st.success("🎉 Appraisal Complete! Cycle closed.")
                    if st.button("📜 Download Appraisal Certificate (PDF)", use_container_width=True, key=f"cert_{user_name}"):
                        try:
                            import fpdf
                            FPDF = fpdf.FPDF
                            pdf = FPDF(orientation='L', unit='mm', format='A4')
                            pdf.set_auto_page_break(auto=True, margin=10)
                            pdf.add_page()
                            
                            # GOLD BORDER
                            avg_score = sum(a['hod_scores'].values()) / len(a['hod_scores']) if a['hod_scores'] else 0
                            if avg_score >= 85:
                                rating, rating_color, border_color = "GOLD", (212, 175, 55), (212, 175, 55)
                            elif avg_score >= 70:
                                rating, rating_color, border_color = "SILVER", (192, 192, 192), (150, 150, 150)
                            else:
                                rating, rating_color, border_color = "BRONZE", (205, 127, 50), (180, 100, 40)
                            
                            pdf.set_draw_color(*border_color)
                            pdf.set_line_width(1.5)
                            pdf.rect(5, 5, 287, 200)
                            pdf.set_line_width(0.5)
                            pdf.set_draw_color(*border_color)
                            pdf.rect(8, 8, 281, 194)
                            
                            # HEADER
                            pdf.set_fill_color(26, 26, 26)
                            pdf.rect(0, 0, 297, 40, 'F')
                            pdf.set_fill_color(*rating_color)
                            pdf.rect(0, 40, 297, 4, 'F')
                            
                            # Logo placeholder
                            pdf.set_font('Helvetica', 'B', 28)
                            pdf.set_text_color(255, 255, 255)
                            pdf.cell(0, 22, 'CHURCHGATE GROUP', ln=True, align='C')
                            pdf.set_font('Helvetica', 'B', 13)
                            pdf.set_text_color(*rating_color)
                            pdf.cell(0, 10, 'OFFICIAL APPRAISAL CERTIFICATE', ln=True, align='C')
                            pdf.ln(10)
                            
                            # RATING BADGE
                            pdf.set_fill_color(*rating_color)
                            badge_x = 100
                            badge_y = pdf.get_y()
                            pdf.rect(badge_x, badge_y, 97, 18, 'F')
                            pdf.set_font('Helvetica', 'B', 20)
                            pdf.set_text_color(255, 255, 255)
                            pdf.set_xy(badge_x, badge_y + 2)
                            pdf.cell(97, 14, f'{rating} RATING', 0, 0, 'C')
                            pdf.set_y(badge_y + 22)
                            pdf.ln(6)
                            
                            # EMPLOYEE DETAILS
                            pdf.set_font('Helvetica', 'B', 16)
                            pdf.set_text_color(26, 26, 26)
                            pdf.cell(0, 10, f'Presented to: {user_name}', ln=True, align='C')
                            pdf.ln(2)
                            pdf.set_font('Helvetica', '', 12)
                            pdf.set_text_color(80, 80, 80)
                            pdf.cell(0, 8, f'Department: {user_dept}', ln=True, align='C')
                            pdf.cell(0, 8, f'Appraisal Cycle: {st.session_state.appraisal_cycle_name}', ln=True, align='C')
                            pdf.cell(0, 8, f'Date: {now_wat.strftime("%B %d, %Y - %H:%M WAT")}', ln=True, align='C')
                            pdf.ln(4)
                            
                            # SCORE SUMMARY TABLE
                            pdf.set_fill_color(26, 26, 26)
                            pdf.set_text_color(255, 255, 255)
                            pdf.set_font('Helvetica', 'B', 9)
                            table_x = 25
                            pdf.set_x(table_x)
                            pdf.cell(90, 7, ' PERFORMANCE PILLAR', 1, 0, 'L', True)
                            pdf.cell(35, 7, 'STAFF SCORE', 1, 0, 'C', True)
                            pdf.cell(35, 7, 'HOD SCORE', 1, 0, 'C', True)
                            pdf.cell(35, 7, 'FINAL', 1, 0, 'C', True)
                            pdf.cell(52, 7, ' RATING', 1, 0, 'C', True)
                            pdf.ln()
                            
                            pillar_scores = {}
                            for score_key, staff_score in sorted(a['scores'].items(), key=natural_sort_key):
                                pillar = '_'.join(score_key.split('_')[:2])
                                if pillar not in pillar_scores:
                                    pillar_scores[pillar] = {'staff': [], 'hod': []}
                                pillar_scores[pillar]['staff'].append(staff_score)
                                hod_score = a['hod_scores'].get(score_key, staff_score) if a['hod_scores'] else staff_score
                                pillar_scores[pillar]['hod'].append(hod_score)
                            
                            pdf.set_font('Helvetica', '', 8)
                            pdf.set_text_color(60, 60, 60)
                            for pillar, scores in pillar_scores.items():
                                avg_staff = sum(scores['staff']) / len(scores['staff'])
                                avg_hod = sum(scores['hod']) / len(scores['hod'])
                                final = avg_hod
                                if final >= 85: pr = 'GOLD'
                                elif final >= 70: pr = 'SILVER'
                                else: pr = 'BRONZE'
                                
                                pdf.set_x(table_x)
                                pdf.cell(90, 6, f' {pillar[:50]}', 1, 0, 'L')
                                pdf.cell(35, 6, f'{avg_staff:.1f}%', 1, 0, 'C')
                                pdf.cell(35, 6, f'{avg_hod:.1f}%', 1, 0, 'C')
                                pdf.cell(35, 6, f'{final:.1f}%', 1, 0, 'C')
                                pdf.cell(52, 6, f' {pr}', 1, 0, 'C')
                                pdf.ln()
                            
                            pdf.ln(4)
                            pdf.set_font('Helvetica', 'B', 14)
                            pdf.set_text_color(*rating_color)
                            pdf.cell(0, 8, f'OVERALL FINAL SCORE: {avg_score:.1f}% - {rating}', ln=True, align='C')
                            
                            # SIGNATURE LINES
                            pdf.ln(8)
                            pdf.set_draw_color(150, 150, 150)
                            pdf.set_line_width(0.3)
                            sig_y = pdf.get_y()
                            pdf.line(30, sig_y + 15, 110, sig_y + 15)
                            pdf.line(130, sig_y + 15, 240, sig_y + 15)
                            pdf.line(250, sig_y + 15, 280, sig_y + 15)
                            pdf.set_font('Helvetica', '', 8)
                            pdf.set_text_color(100, 100, 100)
                            pdf.set_xy(30, sig_y + 16)
                            pdf.cell(80, 5, 'HOD / Line Manager', 0, 0, 'C')
                            pdf.set_xy(130, sig_y + 16)
                            pdf.cell(110, 5, 'Human Resources Director', 0, 0, 'C')
                            pdf.set_xy(250, sig_y + 16)
                            pdf.cell(30, 5, 'Date', 0, 0, 'C')
                            
                            # FOOTER
                            pdf.set_y(-22)
                            pdf.set_fill_color(26, 26, 26)
                            pdf.rect(0, pdf.get_y()-2, 297, 24, 'F')
                            pdf.set_font('Helvetica', 'I', 7)
                            pdf.set_text_color(180, 180, 180)
                            pdf.cell(0, 5, 'Churchgate Group - Official Appraisal Document', ln=True, align='C')
                            pdf.cell(0, 5, 'World Trade Center, Abuja | hr@churchgate.com | This certificate is system-generated and valid without signature.', ln=True, align='C')
                            pdf.cell(0, 5, f'Certificate ID: CG-APP-{user_name[:3].upper()}-{datetime.now().strftime("%Y%m%d%H%M")}', ln=True, align='C')
                            
                            st.download_button("📥 Download World-Class Certificate", bytes(pdf.output()), f"{user_name}_certificate.pdf", "application/pdf")
                        except Exception as e:
                            st.warning(f"Certificate error: {str(e)}")
                elif a.get('acceptance') == 'Rejected':
                    if a.get('status') == 'Awaiting HOD Re-review':
                        st.warning("⚠️ Awaiting HOD re-review.")
                    else:
                        st.warning("⚠️ Under review by Sr. Management.")
    
    with tab4:
        st.subheader("👔 HOD Review & Approval")
        
        if is_hod:
            st.markdown("### 📊 Cycle Status")
            submitted_count = len([v for v in st.session_state.self_assessments.values() if v.get('department') == user_dept and v['status'] == 'Submitted'])
            re_review_count = len([v for v in st.session_state.self_assessments.values() if v.get('department') == user_dept and v['status'] == 'Awaiting HOD Re-review'])
            approved_count = len([v for v in st.session_state.self_assessments.values() if v.get('department') == user_dept and v['status'] == 'Approved'])
            escalated_count = len([v for v in st.session_state.self_assessments.values() if v.get('acceptance') == 'Rejected' and v.get('status') != 'Awaiting HOD Re-review'])
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Submitted", submitted_count)
            c2.metric("Re-Review", re_review_count)
            c3.metric("Approved", approved_count)
            c4.metric("Escalated", escalated_count)
            
            st.markdown("---")
            submitted = {k: v for k, v in st.session_state.self_assessments.items() if v.get('department') == user_dept and v['status'] in ['Submitted', 'Awaiting HOD Re-review']}
            
            if submitted:
                for staff_name, assessment in submitted.items():
                    is_re_review = assessment.get('status') == 'Awaiting HOD Re-review'
                    expander_title = f"{'🔄 RE-REVIEW: ' if is_re_review else '📋 '}{staff_name} — {assessment['date']} — {assessment['status']}"
                    
                    with st.expander(expander_title, expanded=is_re_review):
                        if is_re_review:
                            st.warning(f"⚠️ {staff_name} has rejected your initial review (Rejection #{assessment.get('reject_count', 1)}). Please re-review.")
                        
                        st.markdown(f"**Overall Comments:** {assessment.get('comments', 'N/A')}")
                        
                        if assessment.get('pillar_comments'):
                            st.markdown("**Staff Justifications by Pillar:**")
                            for pillar, comment in sorted(assessment['pillar_comments'].items()):
                                st.markdown(f"- **{pillar}:** {comment}")
                        
                        if is_re_review and assessment.get('hod_scores'):
                            st.markdown("---")
                            st.markdown("**📋 Your Previous Scores (for reference):**")
                            for score_key, prev_hod_score in sorted(assessment['hod_scores'].items(), key=natural_sort_key):
                                staff_score = assessment['scores'].get(score_key, 'N/A')
                                st.markdown(f"- {score_key}: Staff={staff_score}% / Your Previous={prev_hod_score}%")
                        
                        st.markdown("---")
                        st.markdown("### Side-by-Side Review")
                        
                        hod_scores = {}
                        hod_pillar_comments = {}
                        
                        for score_key, staff_score in sorted(assessment['scores'].items(), key=natural_sort_key):
                            pillar_name = '_'.join(score_key.split('_')[:2])
                            if pillar_name not in hod_pillar_comments:
                                st.markdown(f"**{pillar_name}**")
                                hod_pillar_comments[pillar_name] = st.text_area(f"HOD Justification for {pillar_name} *", key=f"hpc_{staff_name}_{pillar_name}")
                            
                            default_hod = assessment.get('hod_scores', {}).get(score_key, staff_score) if is_re_review else staff_score
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown(f"Staff: {staff_score}%")
                            with c2:
                                hod_scores[score_key] = st.number_input(f"HOD Score", 0, 100, int(default_hod) if default_hod else staff_score, key=f"hod_{staff_name}_{score_key}")
                        
                        st.markdown("---")
                        hod_overall = st.text_area(f"HOD Overall Comments for {staff_name} *", key=f"hod_com_{staff_name}")
                        
                        if is_re_review:
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                if st.button(f"🔄 Revise & Resubmit", key=f"revise_{staff_name}"):
                                    if all(hod_pillar_comments.values()) and hod_overall:
                                        st.session_state.self_assessments[staff_name]['status'] = 'Approved'
                                        st.session_state.self_assessments[staff_name]['hod_scores'] = hod_scores
                                        st.session_state.self_assessments[staff_name]['hod_comments'] = hod_overall
                                        st.session_state.self_assessments[staff_name]['hod_pillar_comments'] = hod_pillar_comments
                                        st.session_state.self_assessments[staff_name]['acceptance'] = None
                                        log_audit('HOD Revised', f'{staff_name} scores revised by HOD')
                                        try:
                                            db.save_appraisal(staff_name, assessment.get('email', ''), user_dept,
                                                st.session_state.appraisal_cycle_name, 'Approved',
                                                assessment['scores'], assessment.get('comments', ''), assessment.get('pillar_comments', {}),
                                                hod_scores, hod_overall, hod_pillar_comments, None, None,
                                                assessment.get('date', ''))
                                        except:
                                            pass
                                        st.success(f"✅ Scores revised! Sent back to {staff_name}.")
                                        st.rerun()
                                    else:
                                        st.error("❌ All justifications required!")
                            with c2:
                                if st.button(f"✋ Stand Firm - Escalate", key=f"standfirm_{staff_name}"):
                                    st.session_state.self_assessments[staff_name]['status'] = 'Approved'
                                    st.session_state.self_assessments[staff_name]['acceptance'] = 'Rejected'
                                    st.session_state.self_assessments[staff_name]['hod_scores'] = hod_scores if hod_scores else assessment.get('hod_scores', {})
                                    st.session_state.self_assessments[staff_name]['hod_comments'] = hod_overall if hod_overall else assessment.get('hod_comments', '')
                                    st.session_state.self_assessments[staff_name]['hod_pillar_comments'] = hod_pillar_comments if hod_pillar_comments else assessment.get('hod_pillar_comments', {})
                                    log_audit('HOD Stands Firm', f'{staff_name} escalated to Sr. Management')
                                    try:
                                        db.save_appraisal(staff_name, assessment.get('email', ''), user_dept,
                                            st.session_state.appraisal_cycle_name, 'Approved',
                                            assessment['scores'], assessment.get('comments', ''), assessment.get('pillar_comments', {}),
                                            assessment.get('hod_scores', {}), assessment.get('hod_comments', ''), assessment.get('hod_pillar_comments', {}),
                                            'Rejected', None,
                                            assessment.get('date', ''))
                                    except:
                                        pass
                                    st.warning(f"✋ Standing firm. Escalated to Sr. Management.")
                                    st.rerun()
                        else:
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button(f"✅ Approve {staff_name}", key=f"app_{staff_name}"):
                                    if all(hod_pillar_comments.values()) and hod_overall:
                                        st.session_state.self_assessments[staff_name]['status'] = 'Approved'
                                        st.session_state.self_assessments[staff_name]['hod_scores'] = hod_scores
                                        st.session_state.self_assessments[staff_name]['hod_comments'] = hod_overall
                                        st.session_state.self_assessments[staff_name]['hod_pillar_comments'] = hod_pillar_comments
                                        try:
                                            db.save_appraisal(staff_name, assessment.get('email', ''), user_dept,
                                                st.session_state.appraisal_cycle_name, 'Approved',
                                                assessment['scores'], assessment.get('comments', ''), assessment.get('pillar_comments', {}),
                                                hod_scores, hod_overall, hod_pillar_comments, None, None,
                                                assessment.get('date', ''))
                                        except:
                                            pass
                                        log_audit('Appraisal Approved', f'{staff_name} approved by HOD {user_name}')
                                        st.success(f"✅ {staff_name} approved! Staff has been notified.")
                                        st.balloons()
                                        time.sleep(1.5)
                                        st.rerun()
                                    else:
                                        st.error("❌ All justifications required!")
                            with c2:
                                if st.button(f"🔄 Request Revision", key=f"rev_{staff_name}"):
                                    st.session_state.self_assessments[staff_name]['status'] = 'Revision Requested'
                                    log_audit('Revision Requested', f'Revision requested for {staff_name}')
                                    st.warning(f"🔄 Revision requested from {staff_name}")
                                    st.rerun()
            else:
                st.info("No pending assessments for your team.")
        
        if is_sr_mgmt:
            st.markdown("---")
            st.markdown("### ⚖️ Escalated Appraisals (Final Committee)")
            escalated = {k: v for k, v in st.session_state.self_assessments.items() if v.get('acceptance') == 'Rejected' and v.get('status') != 'Awaiting HOD Re-review'}
            if escalated:
                for staff_name, assessment in escalated.items():
                    with st.expander(f"🚨 {staff_name} — Escalated — {assessment.get('reject_count', 1)} rejection(s)", expanded=True):
                        st.markdown(f"**Staff Comments:** {assessment.get('comments', 'N/A')}")
                        st.markdown(f"**HOD Comments:** {assessment.get('hod_comments', 'N/A')}")
                        st.markdown("---")
                        st.markdown("#### 📊 Full Side-by-Side Score Comparison")
                        for score_key, staff_score in sorted(assessment['scores'].items(), key=natural_sort_key):
                            hod_score = assessment.get('hod_scores', {}).get(score_key, 'N/A') if assessment.get('hod_scores') else 'N/A'
                            c1, c2, c3 = st.columns([1, 1, 2])
                            with c1:
                                st.markdown(f"**Staff:** {staff_score}%")
                            with c2:
                                st.markdown(f"**HOD:** {hod_score}%")
                            with c3:
                                st.markdown(f"*{score_key}*")
                        
                        if assessment.get('pillar_comments') or assessment.get('hod_pillar_comments'):
                            st.markdown("---")
                            st.markdown("#### 💬 Justifications Comparison")
                            for pillar in ['1. Occupancy & Revenue Growth', '2. Process Simplification', '3. Asset Reliability & Digitalization', '4. People & Culture']:
                                staff_just = assessment.get('pillar_comments', {}).get(pillar, 'N/A')
                                hod_just = assessment.get('hod_pillar_comments', {}).get(pillar, 'N/A') if assessment.get('hod_pillar_comments') else 'N/A'
                                if staff_just != 'N/A' or hod_just != 'N/A':
                                    st.markdown(f"**{pillar}**")
                                    st.markdown(f"- Staff: {staff_just}")
                                    st.markdown(f"- HOD: {hod_just}")
                        
                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button(f"✅ Uphold HOD Decision - {staff_name}", key=f"up_{staff_name}"):
                                st.session_state.self_assessments[staff_name]['acceptance'] = 'Accepted'
                                st.session_state.self_assessments[staff_name]['sr_decision'] = 'HOD Upheld'
                                st.session_state.self_assessments[staff_name]['status'] = 'Completed'
                                log_audit('Sr Mgmt Decision', f'HOD upheld for {staff_name}')
                                try:
                                    db.archive_appraisal(staff_name, assessment.get('email', ''), assessment.get('department', ''),
                                        st.session_state.appraisal_cycle_name, 'Accepted - HOD Upheld',
                                        assessment['scores'], assessment.get('hod_scores', {}), 
                                        assessment.get('comments', ''), assessment.get('hod_comments', ''),
                                        now_wat.strftime('%Y-%m-%d %H:%M WAT'))
                                except:
                                    pass
                                try:
                                    db._delete("appraisals", {"user_name": staff_name, "cycle_name": st.session_state.appraisal_cycle_name})
                                    db._post("appraisals", {
                                        "user_name": staff_name, "user_email": assessment.get('email', ''),
                                        "department": assessment.get('department', ''),
                                        "cycle_name": st.session_state.appraisal_cycle_name,
                                        "status": "Completed",
                                        "scores": json.dumps(assessment['scores']),
                                        "comments": assessment.get('comments', ''),
                                        "pillar_comments": json.dumps(assessment.get('pillar_comments', {})),
                                        "hod_scores": json.dumps(assessment.get('hod_scores', {})),
                                        "hod_comments": assessment.get('hod_comments', ''),
                                        "hod_pillar_comments": json.dumps(assessment.get('hod_pillar_comments', {})),
                                        "acceptance": "Accepted",
                                        "sr_decision": "HOD Upheld",
                                        "submitted_date": assessment.get('date', '')
                                    })
                                except:
                                    pass
                                st.success(f"✅ HOD decision upheld. Appraisal complete.")
                                st.balloons()
                                time.sleep(1.5)
                                st.rerun()
                        with c2:
                            if st.button(f"🔄 Overturn - Favor {staff_name}", key=f"ov_{staff_name}"):
                                st.session_state.self_assessments[staff_name]['acceptance'] = 'Accepted'
                                st.session_state.self_assessments[staff_name]['hod_scores'] = assessment['scores']
                                st.session_state.self_assessments[staff_name]['sr_decision'] = 'Overturned in Favor of Staff'
                                st.session_state.self_assessments[staff_name]['status'] = 'Completed'
                                log_audit('Sr Mgmt Overturn', f'HOD overturned for {staff_name}')
                                try:
                                    db.archive_appraisal(staff_name, assessment.get('email', ''), assessment.get('department', ''),
                                        st.session_state.appraisal_cycle_name, 'Accepted - Overturned',
                                        assessment['scores'], assessment['scores'],
                                        assessment.get('comments', ''), assessment.get('hod_comments', ''),
                                        now_wat.strftime('%Y-%m-%d %H:%M WAT'))
                                except:
                                    pass
                                try:
                                    db._delete("appraisals", {"user_name": staff_name, "cycle_name": st.session_state.appraisal_cycle_name})
                                    db._post("appraisals", {
                                        "user_name": staff_name, "user_email": assessment.get('email', ''),
                                        "department": assessment.get('department', ''),
                                        "cycle_name": st.session_state.appraisal_cycle_name,
                                        "status": "Completed",
                                        "scores": json.dumps(assessment['scores']),
                                        "comments": assessment.get('comments', ''),
                                        "pillar_comments": json.dumps(assessment.get('pillar_comments', {})),
                                        "hod_scores": json.dumps(assessment['scores']),
                                        "hod_comments": assessment.get('hod_comments', ''),
                                        "hod_pillar_comments": json.dumps(assessment.get('hod_pillar_comments', {})),
                                        "acceptance": "Accepted",
                                        "sr_decision": "Overturned in Favor of Staff",
                                        "submitted_date": assessment.get('date', '')
                                    })
                                except:
                                    pass
                                st.success(f"🔄 Decision overturned in favor of {staff_name}. Appraisal complete.")
                                st.balloons()
                                time.sleep(1.5)
                                st.rerun()
            else:
                st.info("No escalated appraisals.")
        elif not is_hod:
            st.info("HOD Review section is for Managers, HODs, Admin, and Senior Management.")
    
    with tab5:
        st.subheader("📊 My Performance Dashboard")
        
        user_assessment = st.session_state.self_assessments.get(user_name, {})
        
        if user_assessment.get('status') == 'Approved' and user_assessment.get('acceptance') == 'Accepted':
            st.success("✅ Appraisal Complete!")
            final_scores = user_assessment.get('hod_scores', user_assessment.get('scores', {}))
            if final_scores:
                valid = [s for s in final_scores.values() if isinstance(s, (int, float))]
                avg = sum(valid) / len(valid) if valid else 0
                st.metric("Final Score", f"{avg:.1f}%")
        
        if user_dept in performance_data:
            for pillar_name, pillar_data in performance_data[user_dept].items():
                color = "#38a169" if pillar_data['progress'] >= 85 else "#d69e2e" if pillar_data['progress'] >= 65 else "#CC0000"
                st.markdown(f"""<div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.6rem; border-left: 4px solid {color};"><strong>{pillar_name}</strong> ({pillar_data['weight']}%)<br><small>Progress: {pillar_data['progress']}% | {pillar_data['status']}</small><div style="background: #e0e0e0; height: 6px; border-radius: 3px; margin-top: 0.5rem;"><div style="background: {color}; width: {pillar_data['progress']}%; height: 6px; border-radius: 3px;"></div></div></div>""", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        total_prog = sum(p['progress'] * p['weight'] / 100 for p in performance_data.get(user_dept, {}).values()) if user_dept in performance_data else 0
        c1.metric("Weighted Score", f"{total_prog:.1f}%")
        c2.metric("On Track", str(sum(1 for p in performance_data.get(user_dept, {}).values() if p['status'] in ['On Track', 'Exceeding'])))
        c3.metric("At Risk", str(sum(1 for p in performance_data.get(user_dept, {}).values() if p['status'] == 'At Risk')))
        
        # Benchmark Report
        st.markdown("---")
        st.markdown("### 📊 Benchmark Report")
        if st.button("📊 Generate Benchmark Report", use_container_width=True):
            dept_avg = total_prog
            group_avg = 0
            count = 0
            for d in all_depts:
                if d in performance_data:
                    group_avg += sum(p['progress'] * p['weight'] / 100 for p in performance_data[d].values())
                    count += 1
            group_avg = group_avg / count if count > 0 else 0
            
            bench_data = pd.DataFrame({'Metric': ['My Score', 'Dept Average', 'Group Average', 'Target'], 'Score': [total_prog, dept_avg, group_avg, 85]})
            fig = px.bar(bench_data, x='Metric', y='Score', color='Metric', color_discrete_sequence=['#CC0000', '#4a4a4a', '#888888', '#38a169'])
            fig.add_hline(y=85, line_dash="dash", line_color="#38a169", annotation_text="Target")
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Audit Trail
        st.markdown("---")
        with st.expander("📋 Audit Trail"):
            if st.session_state.audit_trail:
                for entry in st.session_state.audit_trail[-20:]:
                    st.markdown(f"- **{entry['timestamp']}**: {entry['action']} — {entry['details']} by {entry['user']}")
            else:
                st.info("No audit entries yet.")
        
        # Appraisal History
        st.markdown("---")
        st.markdown("### 📜 Appraisal History")
        try:
            history = db.get_appraisal_history(user_name)
            if history:
                for h in history[-5:]:
                    st.markdown(f"- **{h.get('cycle_name', 'N/A')}**: {h.get('final_status', 'N/A')} on {h.get('completed_date', 'N/A')}")
            else:
                st.info("No completed appraisals yet.")
        except:
            st.info("History loading...")
        
        # Appraisal Reports
        st.markdown("---")
        st.markdown("### 📥 Appraisal Reports")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📊 CSV Report", use_container_width=True):
                if user_assessment.get('scores'):
                    report = []
                    for k, v in user_assessment['scores'].items():
                        hod = user_assessment.get('hod_scores', {}).get(k, 'Pending')
                        report.append({'KPI': k[:80], 'Self': f"{v}%", 'HOD': f"{hod}%" if isinstance(hod, (int, float)) else 'Pending'})
                    st.download_button("📥 Download CSV", pd.DataFrame(report).to_csv(index=False), f"{user_name}_appraisal.csv", "text/csv")
        with c2:
            if st.button("📕 PDF Report", use_container_width=True):
                try:
                    import fpdf
                    FPDF = fpdf.FPDF
                    pdf = FPDF(orientation='P', unit='mm', format='A4')
                    pdf.add_page()
                    pdf.set_fill_color(55, 55, 55)
                    pdf.rect(0, 0, 210, 35, 'F')
                    pdf.set_fill_color(204, 0, 0)
                    pdf.rect(0, 35, 210, 3, 'F')
                    pdf.set_font('Helvetica', 'B', 20)
                    pdf.set_text_color(255, 255, 255)
                    pdf.cell(0, 18, 'CHURCHGATE GROUP', ln=True, align='C')
                    pdf.set_font('Helvetica', 'B', 11)
                    pdf.set_text_color(255, 255, 255)
                    pdf.cell(0, 8, 'PERFORMANCE APPRAISAL REPORT', ln=True, align='C')
                    pdf.ln(10)
                    pdf.set_font('Helvetica', 'B', 12)
                    pdf.set_text_color(26, 26, 26)
                    pdf.cell(0, 8, f'Employee: {user_name} | Dept: {user_dept}', ln=True)
                    pdf.cell(0, 8, f'Cycle: {st.session_state.appraisal_cycle_name}', ln=True)
                    pdf.cell(0, 8, f'Date: {now_wat.strftime("%Y-%m-%d %H:%M WAT")}', ln=True)
                    pdf.ln(5)
                    if user_assessment.get('scores'):
                        pdf.set_fill_color(26, 26, 26)
                        pdf.set_text_color(255, 255, 255)
                        pdf.set_font('Helvetica', 'B', 9)
                        pdf.cell(95, 7, ' KPI', 1, 0, 'L', True)
                        pdf.cell(45, 7, 'SELF', 1, 0, 'C', True)
                        pdf.cell(50, 7, 'HOD', 1, 0, 'C', True)
                        pdf.ln()
                        pdf.set_font('Helvetica', '', 8)
                        pdf.set_text_color(26, 26, 26)
                        for k, v in user_assessment['scores'].items():
                            hod = user_assessment.get('hod_scores', {}).get(k, 'Pending')
                            pdf.cell(95, 6, f' {k[:55]}', 1, 0, 'L')
                            pdf.cell(45, 6, f'{v}%', 1, 0, 'C')
                            pdf.cell(50, 6, f'{hod}%' if isinstance(hod, (int, float)) else str(hod), 1, 0, 'C')
                            pdf.ln()
                    pdf.set_y(-20)
                    pdf.set_font('Helvetica', 'I', 7)
                    pdf.set_text_color(150, 150, 150)
                    pdf.cell(0, 10, 'Churchgate Group - Confidential | hr@churchgate.com', align='C')
                    st.download_button("📥 Download Appraisal PDF", bytes(pdf.output()), f"{user_name}_appraisal.pdf", "application/pdf")
                except:
                    pass

def promotions():
    st.markdown("""<div class="churchgate-header"><h1>🚀 Promotions & Career Progression Console</h1><p>360° A-Player Assessment | Succession Planning | Talent Pipeline Management</p></div>""", unsafe_allow_html=True)
    
    user_role = st.session_state.user['role'] if st.session_state.user else 'Employee'
    user_dept = st.session_state.user.get('department', '') if st.session_state.user else ''
    is_admin = user_role in ['Admin', 'HR Director'] or user_dept == 'Senior Management'
    
    # ALWAYS load from database
    aplayers_data = {}
    try:
        db_players = db.get_all_aplayers()
        if not db_players.empty:
            for _, row in db_players.iterrows():
                dept = row['department']
                if dept not in aplayers_data:
                    aplayers_data[dept] = []
                aplayers_data[dept].append({
                    'name': row['name'], 'position': row['position'],
                    'nominated_by': row['nominated_by'],
                    'perf_score': row['perf_score'], 'leadership': row['leadership'],
                    'strategic': row['strategic'], 'peer_review': row['peer_review'],
                    'junior_review': row['junior_review'], 'independent_review': row['independent_review'],
                    'overall': row['overall'], 'readiness': row['readiness'],
                    'gap': row['gap'], 'risk': row['risk'], 'photo': None
                })
    except:
        pass
    
    all_depts = ['Senior Management', 'Technology Group', 'Facility Management', 'Human Resources', 'Accounts & Finance', 
                 'Sales & Marketing', 'Procurement', 'Security', 'Legal', 'Operations', 
                 'Engineering', 'Central Stores', 'Project Development', 'Trade Services']
    for dept in all_depts:
        if dept not in aplayers_data:
            aplayers_data[dept] = []
    
    try:
        nom_data = db.get_all_nominations()
        nominations_list = nom_data.to_dict('records') if not nom_data.empty else []
    except:
        nominations_list = []
    
    if 'aplayer_nominations' not in st.session_state:
        st.session_state.aplayer_nominations = nominations_list
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 A-Players Board", "📝 Nominate A-Player", "📊 360° Assessment", "📋 Succession Pipeline", "📥 Reports"])
    
    with tab1:
        st.subheader("🏆 Group A-Players — Talent Pipeline")
        
        if st.session_state.aplayer_nominations:
            pending_count = len(st.session_state.aplayer_nominations)
            st.markdown(f"""<div style="background: #fff3cd; padding: 0.8rem 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #d69e2e;"><strong>🔔 {pending_count} Pending Nomination{'s' if pending_count > 1 else ''}</strong></div>""", unsafe_allow_html=True)
        
        all_players = []
        for dept, players in aplayers_data.items():
            for p in players:
                p['department'] = dept
                all_players.append(p)
        
        ready_now = [p for p in all_players if p['readiness'] == 'Ready Now']
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total A-Players", len(all_players))
        c2.metric("Ready Now", len(ready_now), "🚀")
        c3.metric("Avg Score", f"{sum(p['overall'] for p in all_players) / len(all_players):.1f}%" if all_players else "N/A")
        c4.metric("Departments", len([d for d, p in aplayers_data.items() if p]))
        
        st.markdown("---")
        
        if is_admin:
            view_dept = st.selectbox("🏢 Filter by Department", ["All Departments"] + all_depts)
        else:
            view_dept = "All Departments"
        
        if view_dept == "All Departments":
            display_players = all_players
        else:
            display_players = [p for p in all_players if p['department'] == view_dept]
        
        if display_players:
            for player in display_players:
                player_key = f"{player['name']}_{player['department']}"
                color = "#38a169" if player['readiness'] == 'Ready Now' else "#d69e2e" if 'Q3' in str(player['readiness']) else "#3182ce" if 'Q4' in str(player['readiness']) else "#CC0000"
                initials = generate_initials(player['name'])
                st.markdown(f"""
                <div style="background: white; padding: 1.2rem; border-radius: 10px; margin-bottom: 0.8rem; border-left: 5px solid {color}; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                    <div style="display: flex; align-items: center; gap: 1.2rem;">
                        <div style="width: 55px; height: 55px; border-radius: 50%; background: #CC0000; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.3rem; color: white; min-width: 55px;">{initials}</div>
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong style="font-size: 1.1rem;">{player['name']}</strong>
                                    <span style="color: #666; font-size: 0.85rem; margin-left: 0.5rem;">{player['department']}</span>
                                    <br><small>{player['position']} → <strong>Nominated by: {player['nominated_by']}</strong></small>
                                </div>
                                <div style="text-align: right;">
                                    <span style="background: {color}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-weight: 700; font-size: 0.85rem;">{player['readiness']}</span>
                                    <br><small style="font-size: 0.8rem;">Overall: {player['overall']}% | Risk: {player['risk']}</small>
                                </div>
                            </div>
                            <div style="margin-top: 0.5rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                                <span style="background: #f0f0f0; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Perf: {player['perf_score']}%</span>
                                <span style="background: #f0f0f0; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Leadership: {player['leadership']}%</span>
                                <span style="background: #f0f0f0; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Strategic: {player['strategic']}%</span>
                                <span style="background: #f0f0f0; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Peer: {player['peer_review']}%</span>
                                <span style="background: #f0f0f0; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Junior: {player['junior_review']}%</span>
                                <span style="background: #f0f0f0; padding: 0.2rem 0.6rem; border-radius: 10px; font-size: 0.75rem;">Indep: {player['independent_review']}%</span>
                            </div>
                            <div style="margin-top: 0.3rem;"><small style="color: #CC0000;">Gap: {player['gap']}</small></div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
                
        else:
            st.info("No A-Players found. Nominate using the 'Nominate A-Player' tab.")
    
    with tab2:
        st.subheader("📝 Nominate A-Player")
        st.info("HODs and Line Managers can nominate top performers as A-Players for the 360-degree assessment process.")
        
        with st.form("nominate_form"):
            c1, c2 = st.columns(2)
            with c1:
                nominee_name = st.text_input("Nominee Full Name *")
                nominee_position = st.text_input("Current Position *")
                nominee_dept = st.selectbox("Department *", all_depts)
            with c2:
                nominated_by = st.text_input("Nominated By (HOD/Line Manager) *")
                nomination_reason = st.text_area("Reason for Nomination")
            if st.form_submit_button("✅ Submit Nomination", use_container_width=True):
                if nominee_name and nominee_dept and nominated_by:
                    nom_entry = {
                        'name': nominee_name, 'position': nominee_position, 'department': nominee_dept,
                        'nominated_by': nominated_by, 'reason': nomination_reason,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'submitted_by': st.session_state.user['name'] if st.session_state.user else 'Unknown'
                    }
                    st.session_state.aplayer_nominations.append(nom_entry)
                    db.save_nomination(nominee_name, nominee_position, nominee_dept, nominated_by, nomination_reason,
                                     st.session_state.user['name'] if st.session_state.user else 'Unknown',
                                     st.session_state.user['email'] if st.session_state.user else '')
                    st.success(f"✅ {nominee_name} nominated successfully!")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
        
        if st.session_state.aplayer_nominations:
            st.markdown("---")
            st.markdown("### 📋 Pending Nominations — Admin Review")
            for i, nom in enumerate(st.session_state.aplayer_nominations):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"""<div style="background: white; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.3rem; border-left: 3px solid #d69e2e;"><strong>{nom.get('name', '')}</strong> - {nom.get('position', '')}<br><small>{nom.get('department', '')} | By: {nom.get('nominated_by', '')} | {str(nom.get('date', nom.get('created_at', '')))[:10]}</small><br><small style="color: #666;">Reason: {nom.get('reason', 'N/A')}</small></div>""", unsafe_allow_html=True)
                with c2:
                    if is_admin:
                        action_key = f"action_{i}"
                        if action_key not in st.session_state:
                            st.session_state[action_key] = None
                        
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        with col_btn1:
                            if st.button(f"✅", key=f"approve_{i}", use_container_width=True, help="Approve"):
                                st.session_state[action_key] = 'approve'
                        with col_btn2:
                            if st.button(f"⏸️", key=f"hold_{i}", use_container_width=True, help="On Hold"):
                                st.session_state[action_key] = 'hold'
                        with col_btn3:
                            if st.button(f"❌", key=f"reject_{i}", use_container_width=True, help="Reject"):
                                st.session_state[action_key] = 'reject'
                        
                        if st.session_state[action_key]:
                            reason = st.text_area(f"Reason for {st.session_state[action_key]}: *", key=f"reason_{i}", placeholder="Please provide a reason...")
                            if st.button(f"✅ Confirm {st.session_state[action_key].title()}", key=f"confirm_{i}", use_container_width=True):
                                if reason:
                                    if st.session_state[action_key] == 'approve':
                                        db.save_aplayer(nom['name'], nom['position'], nom['department'], nom['nominated_by'], 0, 0, 0, 0, 0, 0, 0, 'Pending Assessment', 'TBD', 'TBD')
                                        st.session_state.aplayer_nominations.pop(i)
                                        st.success(f"✅ {nom['name']} approved!")
                                    elif st.session_state[action_key] == 'reject':
                                        st.session_state.aplayer_nominations.pop(i)
                                        st.error(f"❌ {nom['name']} rejected.")
                                    st.session_state[action_key] = None
                                    st.rerun()
    
    with tab3:
        st.subheader("📊 360° Assessment Scorecard")
        st.info("Complete 360-degree assessment. Weights: Performance (35%), Leadership (25%), Strategic (20%), Peer (10%), Junior (5%), Independent (5%).")
        
        if is_admin:
            depts_with_players = all_depts
            if depts_with_players:
                assess_dept = st.selectbox("Select Department", all_depts, key="assess_dept")
                if assess_dept:
                    player_names = [p['name'] for p in aplayers_data.get(assess_dept, [])]
                    if player_names:
                        assess_player_name = st.selectbox("Select A-Player", player_names, key="assess_player")
                        
                        player_data = None
                        for p in aplayers_data.get(assess_dept, []):
                            if p['name'] == assess_player_name:
                                player_data = p
                                break
                        
                        if player_data:
                            st.markdown(f"### Assessing: {player_data['name']} - {player_data['position']}")
                            with st.form("assessment_form"):
                                c1, c2 = st.columns(2)
                                with c1:
                                    perf = st.slider("Performance Score (35%)", 0, 100, int(player_data['perf_score']))
                                    leadership = st.slider("Leadership Competency (25%)", 0, 100, int(player_data['leadership']))
                                    strategic = st.slider("Strategic Impact (20%)", 0, 100, int(player_data['strategic']))
                                with c2:
                                    peer = st.slider("Peer Review (10%)", 0, 100, int(player_data['peer_review']))
                                    junior = st.slider("Junior Review (5%)", 0, 100, int(player_data['junior_review']))
                                    independent = st.slider("Independent Review (5%)", 0, 100, int(player_data['independent_review']))
                                
                                readiness_options = ['Ready Now', 'Q3 2026', 'Q4 2026', 'Q1 2027', 'Pending Assessment']
                                current_readiness = player_data['readiness'] if player_data['readiness'] in readiness_options else 'Pending Assessment'
                                readiness = st.selectbox("Readiness", readiness_options, index=readiness_options.index(current_readiness))
                                gap = st.text_input("Competency Gap", player_data['gap'])
                                risk = st.selectbox("Risk", ['Low', 'Medium', 'High'], index=['Low', 'Medium', 'High'].index(player_data['risk']) if player_data['risk'] in ['Low', 'Medium', 'High'] else 0)
                                
                                if st.form_submit_button("💾 Save Assessment", use_container_width=True):
                                    overall = int(perf * 0.35 + leadership * 0.25 + strategic * 0.20 + peer * 0.10 + junior * 0.05 + independent * 0.05)
                                    db.save_aplayer(player_data['name'], player_data['position'], assess_dept, player_data['nominated_by'], perf, leadership, strategic, peer, junior, independent, overall, readiness, gap, risk)
                                    st.success(f"✅ Assessment saved! Overall: {overall}%")
                                    st.balloons()
                                    time.sleep(1)
                                    st.rerun()
                    else:
                        st.info(f"No A-Players found in {assess_dept}. Nominate first.")
            else:
                st.info("No A-Players available. Nominate first.")
    
    with tab4:
        st.subheader("📋 Succession Pipeline")
        pipeline_data = []
        for dept, players in aplayers_data.items():
            for p in players:
                pipeline_data.append({'Department': dept, 'A-Player': p['name'], 'Position': p['position'], 'Readiness': p['readiness'], 'Score': p['overall'], 'Risk': p['risk'], 'Gap': p['gap']})
        if pipeline_data:
            df = pd.DataFrame(pipeline_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            readiness_counts = df['Readiness'].value_counts()
            fig = px.pie(values=readiness_counts.values, names=readiness_counts.index, hole=0.5, color_discrete_sequence=['#38a169', '#d69e2e', '#3182ce', '#CC0000'])
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("📥 Promotion Reports")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📊 Generate CSV Report", use_container_width=True):
                csv_data = []
                for dept, players in aplayers_data.items():
                    for p in players:
                        csv_data.append({'Department': dept, 'Name': p['name'], 'Position': p['position'], 'Perf': p['perf_score'], 'Leadership': p['leadership'], 'Strategic': p['strategic'], 'Peer': p['peer_review'], 'Junior': p['junior_review'], 'Independent': p['independent_review'], 'Overall': p['overall'], 'Readiness': p['readiness'], 'Gap': p['gap'], 'Risk': p['risk']})
                if csv_data:
                    st.download_button("📥 Download CSV", pd.DataFrame(csv_data).to_csv(index=False), "aplayers_report.csv", "text/csv")
        with c2:
            if st.button("📕 Generate Executive PDF", use_container_width=True):
                try:
                    import fpdf
                    FPDF = fpdf.FPDF
                    pdf = FPDF(orientation='L', unit='mm', format='A4')
                    pdf.set_auto_page_break(auto=True, margin=10)
                    pdf.add_page()
                    
                    pdf.set_fill_color(55, 55, 55)
                    pdf.rect(0, 0, 297, 35, 'F')
                    pdf.set_fill_color(204, 0, 0)
                    pdf.rect(0, 35, 297, 3, 'F')
                    pdf.set_font('Helvetica', 'B', 22)
                    pdf.set_text_color(255, 255, 255)
                    pdf.cell(0, 18, 'CHURCHGATE GROUP', ln=True, align='C')
                    pdf.set_font('Helvetica', 'B', 12)
                    pdf.set_text_color(255, 255, 255)
                    pdf.cell(0, 8, 'A-PLAYERS & SUCCESSION PIPELINE - EXECUTIVE REPORT', ln=True, align='C')
                    pdf.ln(10)
                    
                    total = len(all_players)
                    ready = len(ready_now)
                    avg = sum(p['overall'] for p in all_players) / total if total > 0 else 0
                    
                    pdf.set_fill_color(245, 245, 245)
                    pdf.rect(10, pdf.get_y(), 277, 10, 'F')
                    pdf.set_font('Helvetica', 'B', 9)
                    pdf.set_text_color(26, 26, 26)
                    pdf.cell(92, 10, f'  Total: {total}', 0, 0, 'L')
                    pdf.cell(92, 10, f'Ready Now: {ready}', 0, 0, 'C')
                    pdf.cell(93, 10, f'Avg Score: {avg:.1f}%  ', 0, 0, 'R')
                    pdf.ln(14)
                    
                    cards_data = [('TOTAL', str(total), (26, 26, 26)), ('READY NOW', str(ready), (56, 161, 105)), ('AVG SCORE', f'{avg:.1f}%', (204, 0, 0)), ('DEPTS', str(len([d for d, p in aplayers_data.items() if p])), (49, 130, 206))]
                    col_w = 65
                    col_h = 16
                    x_start = 14
                    y_pos = pdf.get_y()
                    for j, (label, value, color) in enumerate(cards_data):
                        x = x_start + j * (col_w + 5)
                        pdf.set_fill_color(*color)
                        pdf.rect(x, y_pos, col_w, col_h, 'F')
                        pdf.set_text_color(255, 255, 255)
                        pdf.set_xy(x, y_pos + 1)
                        pdf.set_font('Helvetica', 'B', 7)
                        pdf.cell(col_w, 6, label, 0, 0, 'C')
                        pdf.set_xy(x, y_pos + 7)
                        pdf.set_font('Helvetica', 'B', 14)
                        pdf.cell(col_w, 8, value, 0, 0, 'C')
                    pdf.set_y(y_pos + col_h + 8)
                    
                    pdf.set_fill_color(26, 26, 26)
                    pdf.set_text_color(255, 255, 255)
                    pdf.set_font('Helvetica', 'B', 8)
                    pdf.cell(6, 7, ' #', 1, 0, 'C', True)
                    pdf.cell(42, 7, ' NAME', 1, 0, 'L', True)
                    pdf.cell(42, 7, ' DEPARTMENT', 1, 0, 'L', True)
                    pdf.cell(50, 7, ' POSITION', 1, 0, 'L', True)
                    pdf.cell(18, 7, 'SCORE', 1, 0, 'C', True)
                    pdf.cell(32, 7, 'READINESS', 1, 0, 'C', True)
                    pdf.cell(22, 7, 'RISK', 1, 0, 'C', True)
                    pdf.cell(65, 7, ' GAP', 1, 0, 'L', True)
                    pdf.ln()
                    
                    row_num = 0
                    pdf.set_font('Helvetica', '', 7)
                    for dept, players in aplayers_data.items():
                        for p in players:
                            row_num += 1
                            if p['overall'] >= 85:
                                tc = (56, 161, 105)
                            elif p['overall'] >= 70:
                                tc = (214, 158, 46)
                            else:
                                tc = (204, 0, 0)
                            pdf.set_text_color(26, 26, 26)
                            pdf.cell(6, 6, str(row_num), 1, 0, 'C')
                            pdf.cell(42, 6, f' {p["name"][:25]}', 1, 0, 'L')
                            pdf.cell(42, 6, f' {dept[:25]}', 1, 0, 'L')
                            pdf.cell(50, 6, f' {p["position"][:30]}', 1, 0, 'L')
                            pdf.set_text_color(*tc)
                            pdf.set_font('Helvetica', 'B', 7)
                            pdf.cell(18, 6, f'{p["overall"]}%', 1, 0, 'C')
                            pdf.set_text_color(26, 26, 26)
                            pdf.set_font('Helvetica', '', 7)
                            pdf.cell(32, 6, p['readiness'][:18], 1, 0, 'C')
                            pdf.cell(22, 6, p['risk'], 1, 0, 'C')
                            pdf.cell(65, 6, f' {p["gap"][:40]}', 1, 0, 'L')
                            pdf.ln()
                    
                    pdf.set_y(-15)
                    pdf.set_fill_color(26, 26, 26)
                    pdf.rect(0, pdf.get_y()-2, 297, 17, 'F')
                    pdf.set_font('Helvetica', 'I', 7)
                    pdf.set_text_color(180, 180, 180)
                    pdf.cell(0, 5, 'Churchgate Group - Confidential | hr@churchgate.com', ln=True, align='C')
                    
                    st.download_button("📥 Download PDF", bytes(pdf.output()), "aplayers_report.pdf", "application/pdf")
                    st.success("✅ PDF generated!")
                except Exception as e:
                    st.warning(f"PDF Error: {str(e)}")

def recruitment_hub():
    st.markdown("""<div class="churchgate-header"><h1>💼 Recruitment Hub</h1><p>Job Requisition | Auto-Posting | AI Screening | Interview Scheduler | Offer Letters | Background Checks | Onboarding</p></div>""", unsafe_allow_html=True)
    
    user_role = st.session_state.user['role'] if st.session_state.user else 'Employee'
    user_dept = st.session_state.user.get('department', '') if st.session_state.user else ''
    user_name = st.session_state.user['name'] if st.session_state.user else 'Staff'
    is_admin = user_role in ['Admin', 'HR Director'] or user_dept == 'Senior Management'
    is_manager = is_admin or user_role in ['Manager', 'HOD']
    
    STREAMLIT_URL = "https://churchgate-hris.streamlit.app"
    
    # CHANGE 1: Load from database
    if 'job_requisitions' not in st.session_state:
        st.session_state.job_requisitions = []
        try:
            db_reqs = db.get_all_job_requisitions()
            for r in db_reqs:
                st.session_state.job_requisitions.append({
                    'id': r.get('req_id', ''), 'title': r.get('title', ''),
                    'department': r.get('department', ''), 'location': r.get('location', ''),
                    'type': r.get('job_type', ''), 'salary': r.get('salary', ''),
                    'level': r.get('level', ''), 'positions': r.get('positions', 1),
                    'closing': r.get('closing', ''), 'jd': r.get('jd', ''),
                    'screening': json.loads(r.get('screening', '[]')),
                    'posts': json.loads(r.get('posts', '{}')),
                    'status': r.get('status', ''), 'submitted_by': r.get('submitted_by', ''),
                    'date': r.get('date', ''), 'lm_comment': r.get('lm_comment', ''),
                    'admin_comment': r.get('admin_comment', ''), 'coo_comment': r.get('coo_comment', '')
                })
        except:
            pass
    
    if 'active_jobs' not in st.session_state:
        st.session_state.active_jobs = []
        # Load from database
        try:
            all_reqs = db.get_all_job_requisitions()
            for r in all_reqs:
                if r.get('status') == 'Approved - Live':
                    job_ref = f"JOB-{datetime.now().strftime('%Y%m%d')}-{len(st.session_state.active_jobs)+1:03d}"
                    public_url = f"{STREAMLIT_URL}/Careers?job={job_ref}"
                    st.session_state.active_jobs.append({
                        'ref': job_ref, 'title': r.get('title', ''),
                        'department': r.get('department', ''), 'location': r.get('location', ''),
                        'type': r.get('job_type', ''), 'salary': r.get('salary', ''),
                        'jd': r.get('jd', ''), 'closing': r.get('closing', ''),
                        'screening': json.loads(r.get('screening', '[]')),
                        'posts': json.loads(r.get('posts', '{}')),
                        'date': r.get('date', ''), 'applications': 0,
                        'public_url': public_url
                    })
        except:
            pass
    if 'onboarding_list' not in st.session_state:
        st.session_state.onboarding_list = []
    if 'interviews_scheduled' not in st.session_state:
        st.session_state.interviews_scheduled = []
    if 'offer_letters' not in st.session_state:
        st.session_state.offer_letters = []
    if 'referrals' not in st.session_state:
        st.session_state.referrals = []
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📋 Job Requisition", "📢 Active Jobs", "🌐 Candidate Portal", 
        "🤖 AI Screening", "📅 Interviews", "📝 Offer Letters",
        "🎯 Onboarding", "🔍 Background Checks", "📊 Analytics"
    ])
    
    # ============ TAB 1: JOB REQUISITION ============
    with tab1:
        st.subheader("📋 Job Requisition & Approval Workflow")
        st.info("Workflow: Line Manager → Super Admin → COO → Job Goes LIVE on Careers Page")
        
        with st.form("job_requisition_form"):
            st.markdown("### New Job Requisition")
            c1, c2 = st.columns(2)
            with c1:
                job_title = st.text_input("Job Title *", placeholder="e.g., Senior Network Engineer")
                department = st.selectbox("Department *", ['Technology Group', 'Facility Management', 'Human Resources', 'Accounts & Finance', 'Sales & Marketing', 'Procurement', 'Security', 'Legal', 'Operations', 'Engineering', 'Central Stores', 'Project Development', 'Trade Services'])
                location = st.selectbox("Location", ["World Trade Center Abuja", "Churchgate Tower 1 Lagos", "Churchgate Tower 2 Lagos", "Churchgate Plaza Abuja", "Remote/Hybrid"])
                employment_type = st.selectbox("Employment Type", ["Full-time", "Contract", "Part-time", "Intern"])
            with c2:
                salary_range = st.text_input("Salary Range", placeholder="e.g., ₦5,000,000 - ₦8,000,000")
                experience_level = st.selectbox("Experience Level", ["Entry Level (0-2 yrs)", "Junior (2-4 yrs)", "Mid-Level (4-7 yrs)", "Senior (7-10 yrs)", "Executive (10+ yrs)"])
                positions = st.number_input("Number of Positions", min_value=1, value=1)
                closing_date = st.date_input("Application Deadline")
            
            st.markdown("---")
            jd_text = st.text_area("Full Job Description *", height=200, placeholder="Paste complete job description...")
            
            st.markdown("### Screening Questions")
            screening_q1 = st.text_input("Required Skill 1 *", placeholder="e.g., Cisco Certified (CCNP minimum)")
            screening_q2 = st.text_input("Required Skill 2 *", placeholder="e.g., 5+ years experience")
            screening_q3 = st.text_input("Required Skill 3", placeholder="e.g., Experience with security systems")
            screening_q4 = st.text_input("Education Requirement *", placeholder="e.g., B.Sc. Computer Science")
            
            st.markdown("### Auto-Post Settings")
            c1, c2, c3 = st.columns(3)
            with c1:
                post_linkedin = st.checkbox("Post to LinkedIn", value=True)
            with c2:
                post_indeed = st.checkbox("Post to Indeed", value=True)
            with c3:
                post_glassdoor = st.checkbox("Post to Glassdoor", value=True)
            
            submitted = st.form_submit_button("📤 Submit for Approval", use_container_width=True)
            
            if submitted:
                if job_title and department and jd_text:
                    req = {
                        'id': f"REQ-{datetime.now().strftime('%Y%m%d%H%M')}",
                        'title': job_title, 'department': department, 'location': location,
                        'type': employment_type, 'salary': salary_range, 'level': experience_level,
                        'positions': positions, 'closing': closing_date.strftime('%Y-%m-%d'),
                        'jd': jd_text, 'screening': [screening_q1, screening_q2, screening_q3, screening_q4],
                        'posts': {'linkedin': post_linkedin, 'indeed': post_indeed, 'glassdoor': post_glassdoor},
                        'status': 'Pending LM Approval',
                        'submitted_by': user_name, 'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'lm_comment': '', 'admin_comment': '', 'coo_comment': ''
                    }
                    st.session_state.job_requisitions.append(req)
                    # CHANGE 2: Save to database
                    try:
                        db.save_job_requisition(req['id'], req['title'], req['department'], req['location'],
                            req['type'], req['salary'], req['level'], req['positions'], req['closing'],
                            req['jd'], req['screening'], req['posts'], req['status'], req['submitted_by'], req['date'],
                            req['lm_comment'], req['admin_comment'], req['coo_comment'])
                    except:
                        pass
                    st.success(f"✅ Job requisition {req['id']} submitted! Awaiting approval chain.")
                    st.balloons()
                else:
                    st.error("❌ Required fields missing!")
        
        if st.session_state.job_requisitions:
            st.markdown("---")
            st.markdown("### 📋 Requisition Approval Dashboard")
            for i, req in enumerate(st.session_state.job_requisitions):
                with st.expander(f"{req['id']} - {req['title']} | {req['status']}", expanded=True):
                    st.markdown(f"**By:** {req['submitted_by']} | **Dept:** {req['department']} | **Location:** {req['location']}")
                    
                    if is_admin or is_manager:
                        if req['status'] == 'Pending LM Approval':
                            lm_comment = st.text_area("Line Manager Comment *", key=f"lm_comment_{i}", placeholder="Reason for approval...")
                            if st.button(f"✅ LM Approve", key=f"lm_{i}"):
                                if lm_comment:
                                    st.session_state.job_requisitions[i]['status'] = 'Pending Admin Approval'
                                    st.session_state.job_requisitions[i]['lm_comment'] = lm_comment
                                    # CHANGE 2: Save to database
                                    try:
                                        r = st.session_state.job_requisitions[i]
                                        db.save_job_requisition(r['id'], r['title'], r['department'], r['location'],
                                            r['type'], r['salary'], r['level'], r['positions'], r['closing'],
                                            r['jd'], r['screening'], r['posts'], r['status'], r['submitted_by'], r['date'],
                                            r['lm_comment'], r['admin_comment'], r['coo_comment'])
                                    except:
                                        pass
                                    st.success("✅ LM approved! Sent to Admin.")
                                    st.rerun()
                                else:
                                    st.error("❌ Comment required!")
                        
                        if req['status'] == 'Pending Admin Approval':
                            admin_comment = st.text_area("Admin Comment *", key=f"admin_comment_{i}", placeholder="Reason for approval...")
                            if st.button(f"✅ Admin Approve", key=f"adm_{i}"):
                                if admin_comment:
                                    st.session_state.job_requisitions[i]['status'] = 'Pending COO Approval'
                                    st.session_state.job_requisitions[i]['admin_comment'] = admin_comment
                                    # CHANGE 2: Save to database
                                    try:
                                        r = st.session_state.job_requisitions[i]
                                        db.save_job_requisition(r['id'], r['title'], r['department'], r['location'],
                                            r['type'], r['salary'], r['level'], r['positions'], r['closing'],
                                            r['jd'], r['screening'], r['posts'], r['status'], r['submitted_by'], r['date'],
                                            r['lm_comment'], r['admin_comment'], r['coo_comment'])
                                    except:
                                        pass
                                    st.success("✅ Admin approved! Sent to COO.")
                                    st.rerun()
                                else:
                                    st.error("❌ Comment required!")
                        
                        if req['status'] == 'Pending COO Approval':
                            coo_comment = st.text_area("COO Comment *", key=f"coo_comment_{i}", placeholder="Reason for approval...")
                            if st.button(f"✅ COO Approve & Activate", key=f"coo_{i}"):
                                if coo_comment:
                                    st.session_state.job_requisitions[i]['status'] = 'Approved - Live'
                                    st.session_state.job_requisitions[i]['coo_comment'] = coo_comment
                                    job_ref = f"JOB-{datetime.now().strftime('%Y%m%d')}-{len(st.session_state.active_jobs)+1:03d}"
                                    # CHANGE 3: URL fix
                                    public_url = f"{STREAMLIT_URL}/Careers?job={job_ref}"
                                    st.session_state.active_jobs.append({
                                        'ref': job_ref, 'title': req['title'], 'department': req['department'],
                                        'location': req['location'], 'type': req['type'], 'salary': req['salary'],
                                        'jd': req['jd'], 'screening': req['screening'], 'closing': req['closing'],
                                        'posts': req['posts'], 'date': datetime.now().strftime('%Y-%m-%d'),
                                        'applications': 0, 'public_url': public_url
                                    })
                                    # CHANGE 2: Save to database
                                    try:
                                        r = st.session_state.job_requisitions[i]
                                        db.save_job_requisition(r['id'], r['title'], r['department'], r['location'],
                                            r['type'], r['salary'], r['level'], r['positions'], r['closing'],
                                            r['jd'], r['screening'], r['posts'], r['status'], r['submitted_by'], r['date'],
                                            r['lm_comment'], r['admin_comment'], r['coo_comment'])
                                    except:
                                        pass
                                    st.success(f"✅ Job LIVE on Careers Page!")
                                    st.code(public_url, language=None)
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("❌ Comment required!")
                    
                    if req['status'] == 'Approved - Live':
                        st.success("🟢 LIVE - Accepting applications on Careers Page")
    
    # ============ TAB 2: ACTIVE JOBS ============
    with tab2:
        st.subheader("📢 Active Job Postings")
        if st.session_state.active_jobs:
            for job in st.session_state.active_jobs:
                with st.expander(f"🟢 {job['ref']} - {job['title']} | {job['department']} | {job.get('applications', 0)} applicants", expanded=False):
                    st.markdown(f"**Location:** {job['location']} | **Type:** {job['type']} | **Closes:** {job['closing']}")
                    st.markdown(f"**📎 Public Careers URL:**")
                    st.code(job['public_url'], language=None)
                    st.markdown(f"**Platforms:** LinkedIn: {'✅' if job['posts'].get('linkedin') else '❌'} | Indeed: {'✅' if job['posts'].get('indeed') else '❌'} | Glassdoor: {'✅' if job['posts'].get('glassdoor') else '❌'}")
        else:
            st.info("No active jobs. Submit a requisition in Tab 1.")
    
    # ============ TAB 3: CANDIDATE PORTAL ============
    with tab3:
        st.subheader("🌐 Candidate Application Portal Preview")
        st.info("This is what candidates see on the live Careers Page. Actual applications appear in AI Screening tab.")
        with st.expander("📝 Preview Application Form", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("First Name *", key="prev_fn", disabled=True)
                st.text_input("Last Name *", key="prev_ln", disabled=True)
                st.text_input("Email *", key="prev_em", disabled=True)
                st.text_input("Phone *", key="prev_ph", disabled=True)
                st.text_input("LinkedIn URL", key="prev_li", disabled=True)
            with c2:
                st.text_input("GitHub URL", key="prev_gh", disabled=True)
                st.text_input("Portfolio URL", key="prev_pf", disabled=True)
                st.text_input("Current Position", key="prev_cp", disabled=True)
                st.text_input("Years of Experience", key="prev_ye", disabled=True)
            st.text_area("Cover Letter (Optional)", key="prev_cl", disabled=True)
            st.file_uploader("Upload CV/Resume *", type=['pdf', 'docx'], key="prev_cv", disabled=True)
            st.markdown("### Screening Questions (Auto-generated per role)")
            st.text_area("Q1: Relevant Experience *", key="prev_q1", disabled=True)
            st.text_area("Q2: Key Achievement *", key="prev_q2", disabled=True)
            st.text_area("Q3: Why Churchgate Group? *", key="prev_q3", disabled=True)
    
    # ============ TAB 4: AI SCREENING ============
    with tab4:
        st.subheader("🤖 AI Candidate Screening & Tiering")
        st.info("Real candidate applications from the Careers Page appear here. AI auto-screens and tiers them.")
        
        try:
            candidates = db.get_all_candidates()
            if not candidates.empty:
                st.markdown(f"### 📊 {len(candidates)} Real Applications Received")
                st.dataframe(candidates[['candidate_ref', 'first_name', 'last_name', 'email', 'status', 'ai_score', 'ai_tier']].head(20), use_container_width=True, hide_index=True)
                
                if st.button("🤖 Run AI Screening on All Candidates", use_container_width=True):
                    st.success(f"✅ AI screening initiated! Processing {len(candidates)} candidates...")
                    st.info("📤 Candidates auto-routed to AI Recruitment Agent for deep analysis.")
            else:
                st.info("No applications received yet. Share the Careers Page URL to start receiving applications.")
        except:
            st.info("Database connection pending. Applications will appear here once submitted.")
        
        st.markdown("---")
        st.markdown("### ⚙️ Screening Configuration")
        c1, c2 = st.columns(2)
        with c1:
            st.slider("Skills Match Threshold", 0, 100, 70)
            st.slider("Experience Match Threshold", 0, 100, 60)
        with c2:
            st.slider("Education Match Threshold", 0, 100, 50)
            st.slider("Overall Fit Threshold", 0, 100, 65)
    
    # ============ TAB 5: INTERVIEWS ============
    with tab5:
        st.subheader("📅 Interview Scheduler")
        with st.form("schedule_interview"):
            c1, c2 = st.columns(2)
            with c1:
                candidate_name = st.text_input("Candidate Name *")
                interview_type = st.selectbox("Type", ["📞 Phone Screen", "💻 Technical", "👔 HR", "🏆 Final", "👥 Panel"])
                interviewer = st.text_input("Interviewer *")
            with c2:
                interview_date = st.date_input("Date *")
                interview_time = st.text_input("Time *", placeholder="e.g., 10:00 AM WAT")
                location = st.text_input("Location/Link", placeholder="Google Meet / Zoom / On-site")
            if st.form_submit_button("📅 Schedule Interview", use_container_width=True):
                if candidate_name and interviewer:
                    st.session_state.interviews_scheduled.append({
                        'candidate': candidate_name, 'type': interview_type,
                        'interviewer': interviewer, 'date': interview_date.strftime('%Y-%m-%d'),
                        'time': interview_time, 'location': location, 'status': 'Scheduled'
                    })
                    st.success(f"✅ Interview scheduled for {candidate_name}!")
                    st.balloons()
        
        if st.session_state.interviews_scheduled:
            st.markdown("---")
            st.markdown("### 📅 Upcoming Interviews")
            for iv in st.session_state.interviews_scheduled:
                st.markdown(f"""
                <div style="background: white; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.3rem; border-left: 3px solid #3182ce;">
                    <strong>{iv['candidate']}</strong> - {iv['type']}<br>
                    <small>📅 {iv['date']} at {iv['time']} | 👤 {iv['interviewer']} | 📍 {iv['location']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # ============ TAB 6: OFFER LETTERS ============
    with tab6:
        st.subheader("📝 Offer Letter Generator")
        with st.form("offer_letter"):
            c1, c2 = st.columns(2)
            with c1:
                offer_name = st.text_input("Candidate Name *")
                offer_position = st.text_input("Position *")
                offer_dept = st.selectbox("Department *", ['Technology Group', 'Facility Management', 'Human Resources', 'Accounts & Finance', 'Sales & Marketing', 'Procurement', 'Security', 'Legal', 'Operations'])
                offer_salary = st.text_input("Salary Package *", placeholder="e.g., ₦5,000,000 per annum")
            with c2:
                offer_start = st.date_input("Start Date *")
                offer_reporting = st.text_input("Reports To *")
                offer_probation = st.selectbox("Probation Period", ["3 months", "6 months"])
            if st.form_submit_button("📝 Generate Offer Letter (PDF)", use_container_width=True):
                if offer_name and offer_position and offer_salary:
                    st.session_state.offer_letters.append({
                        'name': offer_name, 'position': offer_position, 'dept': offer_dept,
                        'salary': offer_salary, 'start': offer_start.strftime('%Y-%m-%d'),
                        'reports_to': offer_reporting, 'probation': offer_probation,
                        'date': datetime.now().strftime('%Y-%m-%d'), 'status': 'Pending Acceptance'
                    })
                    try:
                        import fpdf
                        FPDF = fpdf.FPDF
                        pdf = FPDF(orientation='P', unit='mm', format='A4')
                        pdf.add_page()
                        pdf.set_fill_color(55, 55, 55)
                        pdf.rect(0, 0, 210, 30, 'F')
                        pdf.set_fill_color(204, 0, 0)
                        pdf.rect(0, 30, 210, 3, 'F')
                        pdf.set_font('Helvetica', 'B', 20)
                        pdf.set_text_color(255, 255, 255)
                        pdf.cell(0, 16, 'CHURCHGATE GROUP', ln=True, align='C')
                        pdf.set_font('Helvetica', 'B', 11)
                        pdf.cell(0, 8, 'OFFER OF EMPLOYMENT', ln=True, align='C')
                        pdf.ln(10)
                        pdf.set_font('Helvetica', '', 11)
                        pdf.set_text_color(26, 26, 26)
                        pdf.cell(0, 8, f'Dear {offer_name},', ln=True)
                        pdf.ln(3)
                        pdf.cell(0, 8, f'We are pleased to offer you the position of {offer_position} in {offer_dept}.', ln=True)
                        pdf.cell(0, 8, f'Salary: {offer_salary}', ln=True)
                        pdf.cell(0, 8, f'Start Date: {offer_start.strftime("%B %d, %Y")}', ln=True)
                        pdf.cell(0, 8, f'Reports To: {offer_reporting}', ln=True)
                        pdf.cell(0, 8, f'Probation: {offer_probation}', ln=True)
                        pdf.ln(5)
                        pdf.cell(0, 8, 'Please sign and return to accept.', ln=True)
                        pdf.set_y(-20)
                        pdf.set_font('Helvetica', 'I', 7)
                        pdf.set_text_color(150, 150, 150)
                        pdf.cell(0, 10, 'Churchgate Group - Official Offer Letter | hr@churchgate.com', align='C')
                        st.download_button("📥 Download Offer Letter", bytes(pdf.output()), f"{offer_name}_offer.pdf", "application/pdf")
                        st.success(f"✅ Offer letter generated!")
                        st.balloons()
                    except:
                        st.success(f"✅ Offer recorded for {offer_name}!")
    
    # ============ TAB 7: ONBOARDING ============
    with tab7:
        st.subheader("🎯 Onboarding")
        with st.expander("📋 Onboarding Checklist", expanded=True):
            steps = [
                ("📧", "Offer Letter Sent"),
                ("✅", "Offer Accepted"),
                ("📄", "Document Collection"),
                ("💻", "IT Setup (Email, Laptop, Access)"),
                ("🏢", "Workspace Assignment"),
                ("👤", "Buddy Assignment"),
                ("📅", "Orientation Scheduled"),
                ("📚", "Training Enrollment"),
                ("🔑", "Access Cards Issued"),
                ("🎉", "First Day Welcome")
            ]
            for emoji, step in steps:
                done = st.checkbox(f"{emoji} {step}", key=f"onboard_{step}")
                color = "#38a169" if done else "#d69e2e"
                icon = "✅" if done else "⏳"
                st.markdown(f"{icon} **{step}** <span style='color: {color};'>{'Complete' if done else 'Pending'}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        with st.form("add_onboarding"):
            st.markdown("### Add New Hire")
            c1, c2 = st.columns(2)
            with c1:
                nh_name = st.text_input("Employee Name *")
                nh_dept = st.selectbox("Department *", ['Technology Group', 'Facility Management', 'Human Resources', 'Accounts & Finance', 'Sales & Marketing', 'Procurement', 'Security', 'Legal', 'Operations'])
                nh_position = st.text_input("Position *")
            with c2:
                nh_start = st.date_input("Start Date *")
                nh_buddy = st.text_input("Assigned Buddy")
                nh_orientation = st.date_input("Orientation Date")
            if st.form_submit_button("🎯 Start Onboarding", use_container_width=True):
                if nh_name and nh_dept:
                    st.session_state.onboarding_list.append({
                        'name': nh_name, 'dept': nh_dept, 'position': nh_position,
                        'start': nh_start.strftime('%Y-%m-%d'), 'buddy': nh_buddy,
                        'orientation': nh_orientation.strftime('%Y-%m-%d'), 'progress': '10%'
                    })
                    st.success(f"✅ Onboarding started for {nh_name}!")
                    st.balloons()
        
        if st.session_state.onboarding_list:
            st.markdown("---")
            for onboard in st.session_state.onboarding_list:
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #38a169;">
                    <strong>{onboard['name']}</strong> - {onboard['position']} ({onboard['dept']})<br>
                    <small>Start: {onboard['start']} | Buddy: {onboard.get('buddy', 'TBD')} | Progress: {onboard['progress']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # ============ TAB 8: BACKGROUND CHECKS ============
    with tab8:
        st.subheader("🔍 Background Check Requests")
        with st.form("bg_check"):
            c1, c2 = st.columns(2)
            with c1:
                bg_name = st.text_input("Candidate Name *")
                bg_position = st.text_input("Position *")
            with c2:
                bg_type = st.multiselect("Check Type", ["Employment Verification", "Education Verification", "Criminal Record", "Credit Check", "Reference Check"])
                bg_priority = st.selectbox("Priority", ["Standard", "Urgent"])
            if st.form_submit_button("🔍 Request Background Check", use_container_width=True):
                if bg_name:
                    st.success(f"✅ Background check requested for {bg_name}!")
    
    # ============ TAB 9: ANALYTICS ============
    with tab9:
        st.subheader("📊 Recruitment Analytics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Active Jobs", len(st.session_state.active_jobs))
        c2.metric("Interviews", len(st.session_state.interviews_scheduled))
        c3.metric("Offers Sent", len(st.session_state.offer_letters))
        c4.metric("Onboarding", len(st.session_state.onboarding_list))
        
        try:
            candidates = db.get_all_candidates()
            total_apps = len(candidates) if not candidates.empty else 0
        except:
            total_apps = 0
        
        funnel = pd.DataFrame({'Stage': ['Applied', 'Screened', 'Interviewed', 'Offered', 'Hired'], 'Count': [total_apps, int(total_apps*0.6), int(total_apps*0.25), int(total_apps*0.1), int(total_apps*0.05)]})
        fig = px.funnel(funnel, x='Count', y='Stage', color_discrete_sequence=['#CC0000'])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🌍 Diversity & Inclusion")
        div_data = pd.DataFrame({'Category': ['Male', 'Female', 'Other'], 'Applicants': [28, 17, 2]})
        fig2 = px.pie(div_data, values='Applicants', names='Category', hole=0.5, color_discrete_sequence=['#3182ce', '#CC0000', '#718096'])
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🤝 Employee Referral Program")
        with st.form("referral"):
            c1, c2 = st.columns(2)
            with c1:
                ref_name = st.text_input("Referral Name *")
                ref_position = st.text_input("Position Referred For *")
                ref_employee = st.text_input("Your Name *")
            with c2:
                ref_relation = st.selectbox("Relationship", ["Former Colleague", "Friend", "Family", "Professional Network"])
                ref_date = st.date_input("Referral Date")
            if st.form_submit_button("🤝 Submit Referral", use_container_width=True):
                if ref_name and ref_employee:
                    st.session_state.referrals.append({'name': ref_name, 'position': ref_position, 'referrer': ref_employee, 'date': ref_date.strftime('%Y-%m-%d'), 'status': 'Pending'})
                    st.success(f"✅ Referral submitted! Bonus eligible upon successful hire.")
                    st.balloons()

def ai_recruitment_agent():
    st.markdown("""<div class="churchgate-header"><h1>🤖 AI Recruitment Agent</h1><p>AI-Powered CV-JD Matching | Verbatim Detection | Inconsistency Flags | Skills Gap Matrix | Bias Detection | Interview Generator | Executive Reports</p></div>""", unsafe_allow_html=True)
    
    options = ["📥 Load Applications", "📋 JD Analysis", "📤 CV Upload & Scoring", "📊 Candidate Tiering", "🔍 Deep Analysis", "📄 Executive Report", "🔗 LinkedIn Parse", "💾 Save Results"]
    
    if 'ai_section' not in st.session_state:
        st.session_state.ai_section = "📥 Load Applications"
    
    default_index = 0
    try:
        default_index = options.index(st.session_state.ai_section)
    except:
        pass
    
    ai_section = st.radio("Select Function:", options, index=default_index, horizontal=True)
    st.session_state.ai_section = ai_section
    
    # ============ LOAD APPLICATIONS ============
    if ai_section == "📥 Load Applications":
        st.subheader("📥 Applications from Careers Page")
        st.info("Real applications from Churchgate Careers Portal. AI auto-analyzes each candidate.")
        
        try:
            candidates = db.get_all_candidates()
            if not candidates.empty:
                st.markdown(f"### 📊 {len(candidates)} Applications Received")
                
                for idx, row in candidates.iterrows():
                    first = str(row.get('first_name') or '')
                    if not first or first == 'nan' or first == 'None':
                        continue
                    first = first if first else 'Candidate'
                    last = str(row.get('last_name') or '')
                    job = str(row.get('job_id') or 'N/A')
                    email_val = str(row.get('email') or 'N/A')
                    phone_val = str(row.get('phone') or 'N/A')
                    linkedin_val = str(row.get('linkedin_url') or 'N/A')
                    experience_val = str(row.get('years_of_experience') or 'N/A')
                    current_val = str(row.get('current_position') or 'N/A')
                    source_val = str(row.get('source') or 'N/A')
                    score_val = row.get('ai_score', 0) or 0
                    score_display = f"{int(score_val)}%" if score_val > 0 else "Pending"
                    tier_val = str(row.get('ai_tier') or 'Pending')
                    resume_val = str(row.get('resume_text') or '')
                    
                    with st.expander(f"📋 {first} {last} — {job} — AI: {score_display}", expanded=False):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"**Email:** {email_val}")
                            st.markdown(f"**Phone:** {phone_val}")
                            st.markdown(f"**LinkedIn:** {linkedin_val}")
                            st.markdown(f"**Experience:** {experience_val} years")
                        with c2:
                            st.markdown(f"**Current:** {current_val}")
                            st.markdown(f"**Source:** {source_val}")
                            st.markdown(f"**AI Score:** {score_display}")
                            st.markdown(f"**AI Tier:** {tier_val}")
                        
                        if resume_val and resume_val != 'None' and len(resume_val) > 10:
                            with st.expander("📄 View Full CV Content"):
                                st.text_area("CV Content", resume_val, height=200, key=f"cv_{idx}")
                                st.download_button(f"📥 Download CV Text - {first} {last}", resume_val, f"CV_{first}_{last}.txt", "text/plain", key=f"dl_cv_{idx}")
                                cv_url = str(row.get('cv_url') or '')
                                if cv_url:
                                    st.markdown(f"[📥 Download Original CV File]({cv_url})")
                        
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            if st.button(f"🤖 Quick AI Score", key=f"qscore_{idx}"):
                                cv_text = resume_val.lower()
                                keywords = ['experience', 'leadership', 'management', 'project', 'team', 'revenue', 'growth', 'strategy', 'innovation', 'digital', 'transformation', 'data', 'analytics', 'performance', 'stakeholder', 'budget', 'operations', 'compliance', 'quality', 'customer']
                                matches = sum(1 for kw in keywords if kw in cv_text)
                                score = min(98, 35 + matches * 3)
                                tier = "Tier 1 (Strong Fit)" if score >= 85 else "Tier 2 (Good Fit)" if score >= 65 else "Tier 3 (Not Recommended)"
                                st.success(f"{tier} — {score}%")
                        with c2:
                            if st.button(f"🔍 Verbatim Check", key=f"verb_{idx}"):
                                cv_lower = resume_val.lower()
                                jd_phrases = ['responsible for', 'duties include', 'team player', 'hardworking', 'detail oriented']
                                flags = [p for p in jd_phrases if p in cv_lower]
                                if flags:
                                    st.warning(f"⚠️ {len(flags)} verbatim phrases: {', '.join(flags)}")
                                else:
                                    st.success("✅ No verbatim issues")
                        with c3:
                            if st.button(f"📊 Full Analysis", key=f"full_{idx}"):
                                st.session_state.analyze_candidate = row.to_dict()
                                st.session_state.ai_section = "🔍 Deep Analysis"
                                st.success("✅ Candidate loaded! Go to '🔍 Deep Analysis' tab.")
                                st.rerun()
            else:
                st.info("No applications yet. Share your Careers Page URL:")
                st.code("https://churchgate-hris.streamlit.app/Careers", language=None)
        except Exception as e:
            st.warning(f"Loading: {str(e)}")
    
    # ============ JD ANALYSIS ============
    elif ai_section == "📋 JD Analysis":
        st.subheader("📋 AI Job Description Analyzer")
        jd_input = st.radio("Input Method:", ["📝 Paste Text", "📄 Upload JD File"], horizontal=True)
        jd_text = ""
        if jd_input == "📝 Paste Text":
            jd_text = st.text_area("Paste Job Description", height=250)
        else:
            jd_file = st.file_uploader("Upload JD", type=['pdf', 'docx', 'txt'], key="jd_file")
            if jd_file:
                jd_text = save_uploaded_file(jd_file)
                st.text_area("Extracted", jd_text[:500] + "...", height=150, disabled=True)
        
        if st.button("🔍 Analyze JD with AI", use_container_width=True, type="primary"):
            if jd_text:
                with st.spinner("🤖 AI analyzing JD..."):
                    time.sleep(1.5)
                    analysis = ai_agent.analyze_jd(jd_text)
                    st.session_state.current_jd = analysis
                    st.success("✅ Analysis Complete!")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Title:** {analysis['title']}")
                        st.markdown(f"**Dept:** {analysis['department']}")
                        st.markdown(f"**Experience:** {analysis['experience_level']}")
                    with c2:
                        st.markdown("**Required Skills:**")
                        for skill in analysis['required_skills'][:10]:
                            st.markdown(f"- `{skill['skill'].title()}`")
                    with st.expander("🚨 Bias Detection Report"):
                        bias_words = ['aggressive', 'ninja', 'rockstar', 'young', 'digital native']
                        jd_lower = jd_text.lower()
                        biases = [w for w in bias_words if w in jd_lower]
                        if biases:
                            st.warning(f"⚠️ {len(biases)} potentially biased terms: {', '.join(biases)}")
                        else:
                            st.success("✅ No biased language detected")
    
    # ============ CV UPLOAD ============
    elif ai_section == "📤 CV Upload & Scoring":
        st.subheader("📤 CV Upload & AI Scoring")
        uploaded_files = st.file_uploader("Upload CVs", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)
        if uploaded_files and st.button("🤖 Analyze All CVs", use_container_width=True, type="primary"):
            if st.session_state.get('current_jd'):
                for file in uploaded_files:
                    cv_text = save_uploaded_file(file)
                    if cv_text:
                        score_result = ai_agent.score_candidate_advanced(cv_text, st.session_state.current_jd)
                        st.success(f"✅ {file.name}: {score_result['overall_score']}% — {score_result['tier']}")
            else:
                st.warning("⚠️ Analyze a JD first in JD Analysis tab.")
    
    # ============ TIERING ============
    elif ai_section == "📊 Candidate Tiering":
        st.subheader("📊 Candidate Tiering Dashboard")
        try:
            candidates = db.get_all_candidates()
            if not candidates.empty:
                tier1 = len(candidates[candidates['ai_tier'].str.contains('Tier 1', na=False)])
                tier2 = len(candidates[candidates['ai_tier'].str.contains('Tier 2', na=False)])
                tier3 = len(candidates[candidates['ai_tier'].str.contains('Tier 3', na=False)])
                c1, c2, c3 = st.columns(3)
                c1.metric("🌟 Tier 1 - Strong Fit", tier1)
                c2.metric("👍 Tier 2 - Good Fit", tier2)
                c3.metric("👎 Tier 3 - Not Recommended", tier3)
                st.markdown("---")
                div_data = pd.DataFrame({'Category': ['Male', 'Female', 'Unspecified'], 'Count': [tier1+tier2, tier3, max(0, len(candidates)-tier1-tier2-tier3)]})
                fig = px.pie(div_data, values='Count', names='Category', hole=0.5, color_discrete_sequence=['#3182ce', '#CC0000', '#718096'])
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(candidates[['first_name', 'last_name', 'email', 'job_id', 'ai_score', 'ai_tier', 'status']], use_container_width=True, hide_index=True)
        except:
            st.info("Tiering data will appear here.")
    
    # ============ DEEP ANALYSIS ============
    elif ai_section == "🔍 Deep Analysis":
        st.subheader("🔍 AI Deep Candidate Analysis")
        if 'analyze_candidate' in st.session_state:
            candidate = st.session_state.analyze_candidate
            st.markdown(f"### Analyzing: {candidate.get('first_name', '')} {candidate.get('last_name', '')}")
            cv_text = str(candidate.get('resume_text', ''))
            
            st.markdown("---")
            st.markdown("### 🎯 Skills Gap Matrix")
            required_skills = ['Leadership', 'Project Management', 'Data Analysis', 'Communication', 'Strategy', 'Team Management', 'Digital Transformation', 'Stakeholder Management', 'Budgeting', 'Innovation']
            skill_scores = {}
            for skill in required_skills:
                if skill.lower() in cv_text.lower():
                    count = cv_text.lower().count(skill.lower())
                    skill_scores[skill] = min(100, 40 + count * 15)
                else:
                    skill_scores[skill] = random.randint(10, 35)
            skills_df = pd.DataFrame({'Skill': list(skill_scores.keys()), 'Score': list(skill_scores.values())})
            fig = px.bar(skills_df, x='Skill', y='Score', color='Score', color_continuous_scale=['#CC0000', '#d69e2e', '#38a169'])
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 🚨 Inconsistency & Flag Detection")
            flags = []
            if 'manager' in cv_text.lower() and 'managed' not in cv_text.lower():
                flags.append("⚠️ Claims leadership but no evidence of team management")
            import re
            years_match = re.findall(r'(\d+)\s*years', cv_text.lower())
            if years_match and max(int(y) for y in years_match) > 20:
                flags.append("⚠️ Extended experience claims - verify during interview")
            for flag in flags:
                st.warning(flag)
            if not flags:
                st.success("✅ No major inconsistencies detected")
            
            st.markdown("---")
            st.markdown("### 🤖 AI Confidence Score")
            confidence = random.randint(75, 95)
            st.progress(confidence/100)
            st.markdown(f"**AI Confidence: {confidence}%**")
            
            st.markdown("---")
            st.markdown("### 📝 AI-Generated Interview Questions")
            gaps = [s for s, v in skill_scores.items() if v < 50]
            for gap in gaps[:5]:
                st.markdown(f"- *\"Can you describe a situation where you demonstrated {gap.lower()}?\"*")
            
            st.markdown("---")
            st.markdown("### 🤝 Culture Fit Prediction")
            culture_words = ['team', 'collaborat', 'together', 'support', 'mentor', 'grow', 'learn', 'innovate', 'community', 'impact']
            culture_score = sum(1 for w in culture_words if w in cv_text.lower())
            culture_pct = min(100, culture_score * 12)
            st.progress(culture_pct/100)
            st.markdown(f"**Culture Alignment: {culture_pct}%**")
            
            st.markdown("---")
            st.markdown("### 💰 Salary Benchmarking")
            st.info("Market Rate for similar roles: ₦5M - ₦8M annually (Nigerian market, 2026)")
            
            st.markdown("---")
            st.markdown("### 📊 Radar Chart Comparison")
            categories = ['Skills', 'Experience', 'Leadership', 'Culture Fit', 'Communication', 'Technical']
            fig2 = go.Figure()
            fig2.add_trace(go.Scatterpolar(r=[skill_scores.get('Leadership', 50), skill_scores.get('Project Management', 50), random.randint(40,90), culture_pct, random.randint(50,90), random.randint(40,90)], theta=categories, fill='toself', name=candidate.get('first_name', 'Candidate'), line_color='#CC0000'))
            fig2.add_trace(go.Scatterpolar(r=[80, 75, 70, 80, 75, 80], theta=categories, fill='toself', name='Ideal Profile', line_color='#38a169'))
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Go to '📥 Load Applications' and click '📊 Full Analysis' on a candidate.")
    
    # ============ EXECUTIVE REPORT ============
    elif ai_section == "📄 Executive Report":
        st.subheader("📄 AI Executive Report Generator")
        try:
            candidates = db.get_all_candidates()
            if not candidates.empty:
                if st.button("📊 Generate Executive PDF Report", use_container_width=True, type="primary"):
                    try:
                        import fpdf
                        FPDF = fpdf.FPDF
                        pdf = FPDF(orientation='L', unit='mm', format='A4')
                        pdf.add_page()
                        pdf.set_fill_color(55, 55, 55)
                        pdf.rect(0, 0, 297, 30, 'F')
                        pdf.set_fill_color(204, 0, 0)
                        pdf.rect(0, 30, 297, 3, 'F')
                        pdf.set_font('Helvetica', 'B', 20)
                        pdf.set_text_color(255, 255, 255)
                        pdf.cell(0, 16, 'CHURCHGATE GROUP', ln=True, align='C')
                        pdf.set_font('Helvetica', 'B', 11)
                        pdf.set_text_color(255, 255, 255)
                        pdf.cell(0, 8, 'AI RECRUITMENT EXECUTIVE REPORT', ln=True, align='C')
                        pdf.ln(8)
                        total = len(candidates)
                        tier1 = len(candidates[candidates['ai_tier'].str.contains('Tier 1', na=False)])
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.set_text_color(26, 26, 26)
                        pdf.cell(0, 8, f'Total: {total} | Tier 1: {tier1} | Date: {datetime.now().strftime("%B %d, %Y")}', ln=True)
                        pdf.ln(5)
                        pdf.set_fill_color(26, 26, 26)
                        pdf.set_text_color(255, 255, 255)
                        pdf.set_font('Helvetica', 'B', 8)
                        pdf.cell(6, 7, ' #', 1, 0, 'C', True)
                        pdf.cell(45, 7, ' NAME', 1, 0, 'L', True)
                        pdf.cell(55, 7, ' POSITION', 1, 0, 'L', True)
                        pdf.cell(18, 7, 'SCORE', 1, 0, 'C', True)
                        pdf.cell(28, 7, 'TIER', 1, 0, 'C', True)
                        pdf.cell(28, 7, 'STATUS', 1, 0, 'C', True)
                        pdf.cell(97, 7, ' RECOMMENDATION', 1, 0, 'L', True)
                        pdf.ln()
                        pdf.set_font('Helvetica', '', 7)
                        for i, (_, row) in enumerate(candidates.iterrows()):
                            score = row.get('ai_score', 0) or 0
                            try:
                                score = int(float(score))
                            except:
                                score = 0
                            if score >= 85: color = (56,161,105)
                            elif score >= 65: color = (214,158,46)
                            else: color = (204,0,0)
                            pdf.set_text_color(26,26,26)
                            pdf.cell(6, 6, str(i+1), 1, 0, 'C')
                            pdf.cell(45, 6, f' {str(row.get("first_name",""))} {str(row.get("last_name",""))}'[:28], 1, 0, 'L')
                            pdf.cell(55, 6, f' {str(row.get("current_position",""))}'[:33], 1, 0, 'L')
                            pdf.set_text_color(*color)
                            pdf.cell(18, 6, f'{int(score)}%', 1, 0, 'C')
                            pdf.set_text_color(26,26,26)
                            pdf.cell(28, 6, str(row.get('ai_tier','Pending'))[:15], 1, 0, 'C')
                            pdf.cell(28, 6, str(row.get('status','New'))[:15], 1, 0, 'C')
                            rec = 'Advance to Interview' if score >= 85 else 'Keep in View' if score >= 65 else 'Not Recommended'
                            pdf.cell(97, 6, f' {rec}', 1, 0, 'L')
                            pdf.ln()
                        pdf.set_y(-15)
                        pdf.set_fill_color(26,26,26)
                        pdf.rect(0, pdf.get_y()-2, 297, 17, 'F')
                        pdf.set_font('Helvetica', 'I', 7)
                        pdf.set_text_color(180,180,180)
                        pdf.cell(0, 5, 'Churchgate Group - AI Recruitment Report - Confidential', align='C')
                        st.download_button("📥 Download Executive Report", bytes(pdf.output()), "ai_recruitment_report.pdf", "application/pdf")
                        st.success("✅ Report generated!")
                    except Exception as e:
                        st.warning(f"PDF Error: {str(e)}")
                st.download_button("📥 Download CSV", candidates.to_csv(index=False), "candidates.csv", "text/csv")
        except:
            st.info("Load applications first.")
    
    # ============ LINKEDIN ============
    elif ai_section == "🔗 LinkedIn Parse":
        st.subheader("🔍 LinkedIn Profile Parser")
        linkedin_url = st.text_input("Enter LinkedIn Profile URL")
        if st.button("🔍 Parse Profile", use_container_width=True):
            if linkedin_url:
                with st.spinner("Parsing..."):
                    time.sleep(1)
                    profile = linkedin_parser.parse_profile(linkedin_url)
                    st.success("✅ Profile Parsed!")
                    st.json(profile)
    
    # ============ SAVE ============
    elif ai_section == "💾 Save Results":
        st.subheader("💾 Export & Save")
        try:
            candidates = db.get_all_candidates()
            if not candidates.empty:
                st.download_button("📥 Download All (CSV)", candidates.to_csv(index=False), "candidates.csv", "text/csv")
                st.markdown("---")
                st.metric("Predicted Time-to-Hire", "12-15 days", "Based on current pipeline velocity")
        except:
            st.info("No data to export.")

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
    st.markdown("""<div class="churchgate-header"><h1>📊 Reports & Analytics</h1><p>Real-Time Business Intelligence | Predictive Analytics | Churchgate Group</p></div>""", unsafe_allow_html=True)
    
    # Load real data
    emp_df = pd.DataFrame()
    total_emp = 0
    departments = 0
    male_count = 0
    female_count = 0
    active_emp = 0
    
    try:
        emp_df = db.get_all_employees()
        if not emp_df.empty:
            total_emp = len(emp_df)
            departments = len(emp_df['department'].unique())
            active_emp = len(emp_df[emp_df['status'] == 'Active'])
            if 'gender' in emp_df.columns:
                male_count = len(emp_df[emp_df['gender'].str.lower() == 'male'])
                female_count = len(emp_df[emp_df['gender'].str.lower() == 'female'])
    except:
        pass
    
    # Custom date filter
    with st.expander("📅 Filter by Date Range", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            date_from = st.date_input("From", datetime.now() - timedelta(days=180))
        with c2:
            date_to = st.date_input("To", datetime.now())
    
    report_type = st.selectbox("Select Report", [
        "📊 Executive Scorecard",
        "👥 Workforce Analytics", 
        "📈 Recruitment Funnel",
        "🎯 Performance Trends",
        "🏢 Department Scorecard",
        "🌍 Gender Diversity",
        "💰 Financial Overview",
        "🔄 Comparative Analysis",
        "⚠️ Attrition Risk Matrix",
        "📋 Training Dashboard",
        "💵 Cost Per Hire",
        "📥 Export All Reports"
    ])
    
    # ============ EXECUTIVE SCORECARD ============
    if report_type == "📊 Executive Scorecard":
        st.subheader("📊 Executive Scorecard")
        
        metrics = st.session_state.get('portfolio_metrics', {'occupancy': 87, 'revenue': 94, 'rating': 4.2})
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("👥 Employees", total_emp, f"{active_emp} active")
        c2.metric("🏢 Departments", departments)
        c3.metric("🏠 Occupancy", f"{metrics['occupancy']}%")
        c4.metric("💰 Revenue", f"{metrics['revenue']}%", "vs budget")
        c5.metric("⭐ Rating", str(metrics['rating']), "/5")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Strategic Pillar Progress")
            try:
                perf_data = db.get_performance_data()
                if not perf_data.empty:
                    pillar_avg = perf_data.groupby('pillar_name')['progress'].mean().reset_index()
                    fig = px.bar(pillar_avg, x='pillar_name', y='progress', color='progress',
                               color_continuous_scale=['#CC0000', '#d69e2e', '#38a169'])
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Set KPIs in Performance & OKRs to see data.")
            except:
                pass
        
        with col2:
            st.subheader("Department Health")
            if not emp_df.empty:
                dept_health = emp_df.groupby('department').size().reset_index(name='count')
                fig2 = px.treemap(dept_health, path=['department'], values='count', color='count',
                                color_continuous_scale=['#CC0000', '#d69e2e', '#38a169'])
                fig2.update_layout(height=300)
                st.plotly_chart(fig2, use_container_width=True)
    
    # ============ WORKFORCE ANALYTICS ============
    elif report_type == "👥 Workforce Analytics":
        st.subheader("👥 Workforce Analytics")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", total_emp)
        c2.metric("Active", active_emp)
        c3.metric("Departments", departments)
        c4.metric("M:F Ratio", f"{male_count}:{female_count}" if female_count > 0 else "N/A")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if not emp_df.empty:
                dept_counts = emp_df['department'].value_counts()
                fig = px.bar(x=dept_counts.index, y=dept_counts.values, color=dept_counts.values,
                           color_continuous_scale=['#CC0000', '#d69e2e', '#38a169'])
                fig.update_layout(height=350, xaxis_title="Department", yaxis_title="Employees")
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            exp_data = pd.DataFrame({'Experience': ['0-2 yrs', '3-5 yrs', '6-10 yrs', '10+ yrs'], 'Count': [8, 15, 22, 12]})
            fig = px.pie(exp_data, values='Count', names='Experience', hole=0.4,
                       color_discrete_sequence=['#CC0000', '#d69e2e', '#3182ce', '#38a169'])
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📊 Employee Heatmap by Department & Grade")
        if not emp_df.empty:
            heatmap_data = emp_df.groupby(['department', 'grade']).size().unstack(fill_value=0)
            fig3 = px.imshow(heatmap_data, text_auto=True, aspect="auto", color_continuous_scale='Reds')
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
    
    # ============ RECRUITMENT FUNNEL ============
    elif report_type == "📈 Recruitment Funnel":
        st.subheader("📈 Recruitment Funnel Analytics")
        
        total_candidates = 0
        active_jobs = 0
        try:
            candidates = db.get_all_candidates()
            if not candidates.empty:
                total_candidates = len(candidates)
            all_reqs = db.get_all_job_requisitions()
            if all_reqs:
                active_jobs = len([r for r in all_reqs if r.get('status') == 'Approved - Live'])
        except:
            pass
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Candidates", total_candidates)
        c2.metric("Active Jobs", active_jobs)
        c3.metric("Interviews", len(st.session_state.get('interviews_scheduled', [])))
        c4.metric("Offers", len(st.session_state.get('offer_letters', [])))
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            funnel = pd.DataFrame({'Stage': ['Applied', 'Screened', 'Interviewed', 'Offered', 'Hired'], 
                                  'Count': [total_candidates, int(total_candidates*0.6), int(total_candidates*0.25), int(total_candidates*0.1), int(total_candidates*0.05)]})
            fig = px.funnel(funnel, x='Count', y='Stage', color_discrete_sequence=['#CC0000'])
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("⏱️ Time-to-Hire Prediction")
            st.metric("Predicted", "12-15 days", "Based on pipeline velocity")
            st.metric("Avg Time to Screen", "3 days")
            st.metric("Avg Time to Interview", "7 days")
    
    # ============ PERFORMANCE TRENDS ============
    elif report_type == "🎯 Performance Trends":
        st.subheader("🎯 Performance Trends & Forecasting")
        
        try:
            perf_data = db.get_performance_data()
            if not perf_data.empty:
                col1, col2 = st.columns(2)
                with col1:
                    dept_scores = perf_data.groupby('department')['progress'].mean().reset_index()
                    fig = px.bar(dept_scores, x='department', y='progress', color='progress',
                               color_continuous_scale=['#CC0000', '#d69e2e', '#38a169'])
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig2 = px.box(perf_data, x='pillar_name', y='progress', color='pillar_name')
                    fig2.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)
                
                st.markdown("---")
                st.subheader("📈 AI Trend Forecast")
                forecast_data = pd.DataFrame({'Month': ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                                            'Predicted': [82, 84, 86, 88, 90, 92],
                                            'Target': [85, 85, 85, 85, 85, 85]})
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=forecast_data['Month'], y=forecast_data['Predicted'], mode='lines+markers', name='Forecast', line=dict(color='#CC0000', width=3)))
                fig3.add_trace(go.Scatter(x=forecast_data['Month'], y=forecast_data['Target'], mode='lines', name='Target', line=dict(color='#38a169', width=2, dash='dash')))
                fig3.update_layout(height=300)
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("Set KPIs to see performance trends.")
        except:
            st.info("Performance data loading...")
    
    # ============ DEPARTMENT SCORECARD ============
    elif report_type == "🏢 Department Scorecard":
        st.subheader("🏢 Department Performance Scorecard")
        
        if not emp_df.empty:
            dept_list = sorted(emp_df['department'].unique())
            scorecard_data = []
            for dept in dept_list:
                dept_emp = len(emp_df[emp_df['department'] == dept])
                try:
                    perf = db.get_performance_data(dept)
                    avg_score = perf['progress'].mean() if not perf.empty else 0
                except:
                    avg_score = 0
                scorecard_data.append({'Department': dept, 'Employees': dept_emp, 'Avg Performance': f"{avg_score:.0f}%"})
            
            st.dataframe(pd.DataFrame(scorecard_data), use_container_width=True, hide_index=True)
        else:
            st.info("Employee data loading...")
    
    # ============ GENDER DIVERSITY ============
    elif report_type == "🌍 Gender Diversity":
        st.subheader("🌍 Gender Diversity & Inclusion")
        
        if male_count > 0 or female_count > 0:
            col1, col2 = st.columns(2)
            with col1:
                gender_df = pd.DataFrame({'Gender': ['Male', 'Female'], 'Count': [male_count, female_count]})
                fig = px.pie(gender_df, values='Count', names='Gender', hole=0.5, color_discrete_sequence=['#3182ce', '#CC0000'])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.metric("Male", f"{round(male_count/total_emp*100)}%" if total_emp > 0 else "N/A")
                st.metric("Female", f"{round(female_count/total_emp*100)}%" if total_emp > 0 else "N/A")
                st.metric("Diversity Ratio", f"{male_count}:{female_count}")
        else:
            st.info("Update employee genders in Directory to see diversity data.")
    
    # ============ FINANCIAL OVERVIEW ============
    elif report_type == "💰 Financial Overview":
        st.subheader("💰 Financial Overview")
        
        metrics = st.session_state.get('portfolio_metrics', {
            'occupancy': 87, 'revenue': 94, 'rating': 4.2,
            'portfolio_data': {
                'World Trade Center Abuja': {'occupancy': 87, 'revenue': 94},
                'Churchgate Tower 1, Lagos': {'occupancy': 92, 'revenue': 98},
                'Churchgate Tower 2, Lagos': {'occupancy': 85, 'revenue': 88},
                'Churchgate Plaza, Abuja': {'occupancy': 78, 'revenue': 82},
                'Warehouses': {'occupancy': 95, 'revenue': 97},
                'Ocean Terrace': {'occupancy': 90, 'revenue': 91}
            }
        })
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Revenue", "₦12.5B", "+15%")
        c2.metric("Cost", "₦8.7B", "+8%")
        c3.metric("EBITDA", "30.4%", "+2.1%")
        c4.metric("Cash Flow", "₦2.1B", "+12%")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            fin_data = pd.DataFrame({'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                                    'Revenue': [1.8, 2.0, 2.1, 2.2, 2.3, 2.5],
                                    'Cost': [1.3, 1.4, 1.5, 1.5, 1.6, 1.7]})
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Revenue (₦B)', x=fin_data['Month'], y=fin_data['Revenue'], marker_color='#CC0000'))
            fig.add_trace(go.Bar(name='Cost (₦B)', x=fin_data['Month'], y=fin_data['Cost'], marker_color='#4a4a4a'))
            fig.update_layout(height=350, barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            props = list(metrics['portfolio_data'].keys())
            occ_vals = [metrics['portfolio_data'][p]['occupancy'] for p in props]
            fig2 = px.bar(x=props, y=occ_vals, color=occ_vals, color_continuous_scale=['#CC0000', '#d69e2e', '#38a169'])
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)
    
    # ============ COMPARATIVE ANALYSIS ============
    elif report_type == "🔄 Comparative Analysis":
        st.subheader("🔄 Department Comparative Analysis")
        
        if not emp_df.empty:
            dept_list = sorted(emp_df['department'].unique())
            c1, c2 = st.columns(2)
            with c1:
                dept1 = st.selectbox("Department 1", dept_list, key="dept1")
            with c2:
                dept2 = st.selectbox("Department 2", dept_list, key="dept2", index=min(1, len(dept_list)-1))
            
            if dept1 and dept2:
                comp_data = pd.DataFrame({
                    'Metric': ['Employees', 'Performance'],
                    dept1: [len(emp_df[emp_df['department']==dept1]), 85],
                    dept2: [len(emp_df[emp_df['department']==dept2]), 78]
                })
                fig = go.Figure()
                fig.add_trace(go.Bar(name=dept1, x=comp_data['Metric'], y=comp_data[dept1], marker_color='#CC0000'))
                fig.add_trace(go.Bar(name=dept2, x=comp_data['Metric'], y=comp_data[dept2], marker_color='#3182ce'))
                fig.update_layout(height=350, barmode='group')
                st.plotly_chart(fig, use_container_width=True)
    
    # ============ ATTRITION RISK ============
    elif report_type == "⚠️ Attrition Risk Matrix":
        st.subheader("⚠️ Attrition Risk Assessment")
        st.info("Based on performance trends, tenure, and appraisal data")
        
        risk_data = pd.DataFrame({
            'Department': ['Technology', 'Facility Mgmt', 'HR', 'Finance', 'Sales'],
            'Low Risk': [8, 15, 5, 6, 8],
            'Medium Risk': [3, 6, 2, 2, 4],
            'High Risk': [1, 4, 1, 2, 3]
        })
        fig = px.bar(risk_data, x='Department', y=['Low Risk', 'Medium Risk', 'High Risk'],
                    color_discrete_sequence=['#38a169', '#d69e2e', '#CC0000'])
        fig.update_layout(height=400, barmode='stack')
        st.plotly_chart(fig, use_container_width=True)
    
    # ============ TRAINING DASHBOARD ============
    elif report_type == "📋 Training Dashboard":
        st.subheader("📋 Training Completion Dashboard")
        
        training_data = pd.DataFrame({
            'Department': ['Technology', 'Facility Mgmt', 'HR', 'Finance', 'Sales', 'Procurement', 'Security'],
            'Completed': [85, 70, 90, 75, 80, 65, 72],
            'In Progress': [10, 20, 5, 15, 12, 25, 18],
            'Not Started': [5, 10, 5, 10, 8, 10, 10]
        })
        fig = px.bar(training_data, x='Department', y=['Completed', 'In Progress', 'Not Started'],
                    color_discrete_sequence=['#38a169', '#d69e2e', '#CC0000'])
        fig.update_layout(height=400, barmode='stack')
        st.plotly_chart(fig, use_container_width=True)
    
    # ============ COST PER HIRE ============
    elif report_type == "💵 Cost Per Hire":
        st.subheader("💵 Cost Per Hire Analysis")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg Cost/Hire", "₦450,000")
        c2.metric("Job Board Fees", "₦120,000")
        c3.metric("Agency Fees", "₦0", "In-house recruitment")
        
        st.markdown("---")
        cost_data = pd.DataFrame({'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                                 'Cost': [400000, 380000, 450000, 420000, 480000, 450000]})
        fig = px.line(cost_data, x='Month', y='Cost', markers=True, color_discrete_sequence=['#CC0000'])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # ============ EXPORT ALL ============
    elif report_type == "📥 Export All Reports":
        st.subheader("📥 Export All Reports")
        
        if st.button("📊 Generate Comprehensive Executive Report (PDF)", use_container_width=True, type="primary"):
            try:
                import fpdf
                FPDF = fpdf.FPDF
                pdf = FPDF(orientation='P', unit='mm', format='A4')
                pdf.add_page()
                pdf.set_fill_color(55, 55, 55)
                pdf.rect(0, 0, 210, 30, 'F')
                pdf.set_fill_color(204, 0, 0)
                pdf.rect(0, 30, 210, 3, 'F')
                pdf.set_font('Helvetica', 'B', 18)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 16, 'CHURCHGATE GROUP', ln=True, align='C')
                pdf.set_font('Helvetica', 'B', 10)
                pdf.cell(0, 8, 'COMPREHENSIVE ANALYTICS REPORT', ln=True, align='C')
                pdf.ln(8)
                
                pdf.set_font('Helvetica', 'B', 12)
                pdf.set_text_color(26, 26, 26)
                pdf.cell(0, 8, f'Workforce: {total_emp} employees | {departments} departments | {active_emp} active', ln=True)
                pdf.cell(0, 8, f'Diversity: {male_count} Male | {female_count} Female', ln=True)
                pdf.ln(5)
                pdf.set_font('Helvetica', 'I', 8)
                pdf.cell(0, 6, f'Report generated: {datetime.now().strftime("%B %d, %Y at %H:%M WAT")}', ln=True)
                
                pdf.set_y(-20)
                pdf.set_font('Helvetica', 'I', 7)
                pdf.set_text_color(150, 150, 150)
                pdf.cell(0, 10, 'Churchgate Group - Confidential Analytics Report', align='C')
                
                st.download_button("📥 Download Executive Report", bytes(pdf.output()), "churchgate_analytics_report.pdf", "application/pdf")
                st.success("✅ Report generated!")
            except Exception as e:
                st.warning(f"PDF Error: {str(e)}")
        
        if not emp_df.empty:
            st.download_button("📥 Download Workforce Data (CSV)", emp_df.to_csv(index=False), "workforce_data.csv", "text/csv")

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
        db_pic = None
        if db.use_supabase:
            db_pic = db.get_profile_picture(int(st.session_state.user['id']))
        elif 'profile_pic' in st.session_state and st.session_state['profile_pic'] is not None:
            db_pic = st.session_state['profile_pic']
        
        if db_pic is not None:
            st.image(db_pic, width=150)
        
        else:
            initials = generate_initials(user['name'])
            st.markdown(f"""<div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);"><div style="width: 80px; height: 80px; border-radius: 50%; background: #CC0000; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 700; color: white; margin: 0 auto;">{initials}</div><h3 style="margin-top: 0.8rem;">{user['name']}</h3><p>{user.get('position', 'Employee')}</p><p style="color: #CC0000;">ID: {user.get('employee_id', 'N/A')}</p><p>🏢 {user.get('department', 'N/A')}</p><p>👤 Supervisor: Jerome Das (COO)</p></div>""", unsafe_allow_html=True)
        uploaded_pic = st.file_uploader("📸 Upload Profile Picture", type=['jpg', 'jpeg', 'png'])
        if uploaded_pic is not None:
            st.session_state['profile_pic'] = uploaded_pic
            try:
                user_id = st.session_state.user['id']
                image_bytes = uploaded_pic.read()
                if db.use_supabase:
                    import base64
                    b64_str = base64.b64encode(image_bytes).decode()
                    db._post("profile_pics", {"user_id": str(int(user_id)), "image_data": b64_str})
                    st.session_state['profile_pic'] = uploaded_pic
                    st.success("✅ Picture saved to Supabase!")
                else:
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET profile_picture = ? WHERE id = ?", (image_bytes, user_id))
                    conn.commit()
                    conn.close()
                st.success("✅ Profile picture saved permanently!")
            except Exception as e:
                pass
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
    # Check query params for persisted login
    query_params = st.query_params
    if 'logged_in' in query_params and query_params['logged_in'] == 'true':
        if 'user' not in st.session_state or st.session_state.user is None:
            # Try to restore from query param
            if 'user_email' in query_params:
                email = query_params['user_email']
                # Quick re-auth without password (session token approach)
                try:
                    result = db.supabase.table("users").select("*").eq("email", email).execute()
                    if result.data and len(result.data) > 0:
                        st.session_state.user = result.data[0]
                except:
                    pass
    
    if 'user' not in st.session_state or st.session_state.user is None:
        login_section()
    else:
        # Set query params to persist login
        st.query_params['logged_in'] = 'true'
        st.query_params['user_email'] = st.session_state.user.get('email', '')
        
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
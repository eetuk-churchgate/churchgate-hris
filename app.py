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
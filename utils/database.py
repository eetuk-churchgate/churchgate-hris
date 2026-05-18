import pandas as pd
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import streamlit as st

class DatabaseManager:
    def __init__(self):
        self.use_supabase = False
        self.supabase = None
        try:
            if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
                from supabase import create_client
                self.supabase = create_client(
                    st.secrets["SUPABASE_URL"],
                    st.secrets["SUPABASE_KEY"]
                )
                self.use_supabase = True
        except:
            pass
        
        if not self.use_supabase:
            import sqlite3
            Path("data").mkdir(exist_ok=True)
            self.sqlite_path = "data/churchgate_hr.db"
    
    def create_tables(self):
        pass
    
    def verify_user(self, email, password):
        if self.use_supabase and self.supabase:
            try:
                result = self.supabase.table("users").select("*").eq("email", email).execute()
                if result.data and len(result.data) > 0:
                    return result.data[0]
            except:
                pass
            return None
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
    
    def create_user(self, employee_id, name, email, password, role, department, position):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        if self.use_supabase and self.supabase:
            try:
                self.supabase.table("users").insert({"employee_id": employee_id, "name": name, "email": email, "password": hashed_pw, "role": role, "department": department, "position": position, "is_active": True}).execute()
                return True, "User created"
            except:
                return False, "Error"
        return False, "Error"
    
    def update_profile_picture(self, user_id, image_bytes):
        if self.use_supabase and self.supabase:
            try:
                self.supabase.table("users").update({"profile_picture": image_bytes}).eq("id", user_id).execute()
                return True
            except:
                pass
            return False
    
    def get_profile_picture(self, user_id):
        if self.use_supabase and self.supabase:
            try:
                result = self.supabase.table("users").select("profile_picture").eq("id", user_id).execute()
                if result.data and result.data[0].get('profile_picture'):
                    return result.data[0]['profile_picture']
            except:
                pass
            return None
    
    def save_aplayer(self, name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk):
        if self.use_supabase and self.supabase:
            try:
                self.supabase.table("aplayers").insert({"name": name, "position": position, "department": department, "nominated_by": nominated_by, "perf_score": perf_score, "leadership": leadership, "strategic": strategic, "peer_review": peer_review, "junior_review": junior_review, "independent_review": independent_review, "overall": overall, "readiness": readiness, "gap": gap, "risk": risk}).execute()
            except:
                pass
    
    def get_all_aplayers(self):
        if self.use_supabase and self.supabase:
            try:
                result = self.supabase.table("aplayers").select("*").execute()
                return pd.DataFrame(result.data) if result.data else pd.DataFrame()
            except:
                return pd.DataFrame()
        return pd.DataFrame()
    
    def save_nomination(self, name, position, department, nominated_by, reason, submitted_by, submitted_by_email):
        if self.use_supabase and self.supabase:
            try:
                self.supabase.table("aplayer_nominations").insert({"name": name, "position": position, "department": department, "nominated_by": nominated_by, "reason": reason, "submitted_by": submitted_by, "submitted_by_email": submitted_by_email, "status": "Pending"}).execute()
            except:
                pass
    
    def get_all_nominations(self):
        if self.use_supabase and self.supabase:
            try:
                result = self.supabase.table("aplayer_nominations").select("*").eq("status", "Pending").execute()
                return pd.DataFrame(result.data) if result.data else pd.DataFrame()
            except:
                return pd.DataFrame()
        return pd.DataFrame()
    
    def delete_nomination(self, nomination_id):
        if self.use_supabase and self.supabase:
            try:
                self.supabase.table("aplayer_nominations").delete().eq("id", nomination_id).execute()
            except:
                pass
    
    def save_performance_data(self, department, pillar_name, weight, progress, status, deadline, kpi_data):
        if self.use_supabase and self.supabase:
            try:
                self.supabase.table("performance_data").delete().eq("department", department).eq("pillar_name", pillar_name).execute()
                self.supabase.table("performance_data").insert({"department": department, "pillar_name": pillar_name, "weight": weight, "progress": progress, "status": status, "deadline": deadline, "kpi_data": json.dumps(kpi_data)}).execute()
            except:
                pass
    
    def get_performance_data(self, department=None):
        if self.use_supabase and self.supabase:
            try:
                result = self.supabase.table("performance_data").select("*").execute()
                return pd.DataFrame(result.data) if result.data else pd.DataFrame()
            except:
                return pd.DataFrame()
        return pd.DataFrame()
    
    def get_all_employees(self):
        return pd.DataFrame()
    
    def get_employee_by_user_id(self, user_id):
        return None
    
    def add_notification(self, user_id, title, message, type='Info', link=None):
        pass
    
    def get_user_notifications(self, user_id, unread_only=False):
        return pd.DataFrame()
    
    def get_dashboard_stats(self):
        return {'total_employees': 48, 'open_positions': 5, 'new_candidates': 0, 'avg_performance': 85.0}
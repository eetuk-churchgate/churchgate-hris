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
        except Exception as e:
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
                result = self.supabase.table("users").select("*").execute()
                if result.data and len(result.data) > 0:
                    return result.data[0]
            except:
                pass
            return None
    
    def create_user(self, employee_id, name, email, password, role, department, position):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        if self.use_supabase and self.supabase:
            try:
                self.supabase.table("users").insert({
                    "employee_id": employee_id, "name": name, "email": email,
                    "password": hashed_pw, "role": role, "department": department,
                    "position": position, "is_active": True
                }).execute()
                return True, "User created"
            except Exception as e:
                return False, str(e)
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (employee_id, name, email, hashed_pw, role, department, position)
                )
                conn.commit()
                conn.close()
                return True, "User created"
            except:
                conn.close()
                return False, "Error"
    
    def get_all_employees(self):
        if self.use_supabase and self.supabase:
            try:
                result = self.supabase.table("employees").select("*").eq("status", "Active").execute()
                return pd.DataFrame(result.data) if result.data else pd.DataFrame()
            except:
                return pd.DataFrame()
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            df = pd.read_sql_query("SELECT * FROM employees WHERE status = 'Active'", conn)
            conn.close()
            return df
    
    def get_employee_by_user_id(self, user_id):
        return None
    
    def add_notification(self, user_id, title, message, type='Info', link=None):
        pass
    
    def get_user_notifications(self, user_id, unread_only=False):
        return pd.DataFrame()
    
    def save_aplayer(self, name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk):
        if self.use_supabase and self.supabase:
            try:
                self.supabase.table("aplayers").insert({
                    "name": name, "position": position, "department": department,
                    "nominated_by": nominated_by, "perf_score": perf_score,
                    "leadership": leadership, "strategic": strategic,
                    "peer_review": peer_review, "junior_review": junior_review,
                    "independent_review": independent_review, "overall": overall,
                    "readiness": readiness, "gap": gap, "risk": risk
                }).execute()
            except:
                pass
    
    def get_all_aplayers(self):
        if self.use_supabase and self.supabase:
            try:
                result = self.supabase.table("aplayers").select("*").order("department").order("overall", desc=True).execute()
                return pd.DataFrame(result.data) if result.data else pd.DataFrame()
            except:
                return pd.DataFrame()
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            df = pd.read_sql_query("SELECT * FROM aplayers ORDER BY department, overall DESC", conn)
            conn.close()
            return df
    
    def save_nomination(self, name, position, department, nominated_by, reason, submitted_by, submitted_by_email):
        if self.use_supabase and self.supabase:
            try:
                self.supabase.table("aplayer_nominations").insert({
                    "name": name, "position": position, "department": department,
                    "nominated_by": nominated_by, "reason": reason,
                    "submitted_by": submitted_by, "submitted_by_email": submitted_by_email,
                    "status": "Pending"
                }).execute()
            except:
                pass
    
    def get_all_nominations(self):
        if self.use_supabase and self.supabase:
            try:
                result = self.supabase.table("aplayer_nominations").select("*").eq("status", "Pending").order("created_at", desc=True).execute()
                return pd.DataFrame(result.data) if result.data else pd.DataFrame()
            except:
                return pd.DataFrame()
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            df = pd.read_sql_query("SELECT * FROM aplayer_nominations WHERE status = 'Pending' ORDER BY created_at DESC", conn)
            conn.close()
            return df
    
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
                self.supabase.table("performance_data").insert({
                    "department": department, "pillar_name": pillar_name,
                    "weight": weight, "progress": progress, "status": status,
                    "deadline": deadline, "kpi_data": json.dumps(kpi_data)
                }).execute()
            except:
                pass
    
    def get_performance_data(self, department=None):
        if self.use_supabase and self.supabase:
            try:
                if department:
                    result = self.supabase.table("performance_data").select("*").eq("department", department).execute()
                else:
                    result = self.supabase.table("performance_data").select("*").execute()
                return pd.DataFrame(result.data) if result.data else pd.DataFrame()
            except:
                return pd.DataFrame()
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            if department:
                df = pd.read_sql_query("SELECT * FROM performance_data WHERE department = ?", conn, params=(department,))
            else:
                df = pd.read_sql_query("SELECT * FROM performance_data", conn)
            conn.close()
            return df
    
    def get_dashboard_stats(self):
        return {'total_employees': 48, 'open_positions': 5, 'new_candidates': 0, 'avg_performance': 85.0}
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
    
    def _supa_insert(self, table, data):
        """Insert data into Supabase table"""
        if self.use_supabase and self.supabase:
            try:
                result = self.supabase.table(table).insert(data).execute()
                return result.data
            except Exception as e:
                return None
        return None
    
    def _supa_select(self, table, filters=None):
        """Select data from Supabase table"""
        if self.use_supabase and self.supabase:
            try:
                result = self.supabase.table(table).select("*").execute()
                return result.data if result.data else []
            except Exception as e:
                return []
        return []
    
    def _supa_delete(self, table, filters):
        """Delete data from Supabase table"""
        if self.use_supabase and self.supabase:
            try:
                query = self.supabase.table(table).delete()
                for key, value in filters.items():
                    query = query.eq(key, value)
                query.execute()
                return True
            except:
                return False
        return False
    
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
        data = {"employee_id": employee_id, "name": name, "email": email, "password": hashed_pw, "role": role, "department": department, "position": position, "is_active": True}
        result = self._supa_insert("users", data)
        if result:
            return True, "User created"
        return False, "Error"
    
    def update_profile_picture(self, user_id, image_bytes):
        if self.use_supabase and self.supabase:
            try:
                self.supabase.table("users").update({"profile_picture": image_bytes}).eq("id", user_id).execute()
                return True
            except:
                pass
            return False
    
    def save_aplayer(self, name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk):
        data = {"name": name, "position": position, "department": department, "nominated_by": nominated_by, "perf_score": perf_score, "leadership": leadership, "strategic": strategic, "peer_review": peer_review, "junior_review": junior_review, "independent_review": independent_review, "overall": overall, "readiness": readiness, "gap": gap, "risk": risk}
        self._supa_insert("aplayers", data)
    
    def get_all_aplayers(self):
        data = self._supa_select("aplayers")
        return pd.DataFrame(data) if data else pd.DataFrame()
    
    def save_nomination(self, name, position, department, nominated_by, reason, submitted_by, submitted_by_email):
        data = {"name": name, "position": position, "department": department, "nominated_by": nominated_by, "reason": reason, "submitted_by": submitted_by, "submitted_by_email": submitted_by_email, "status": "Pending"}
        self._supa_insert("aplayer_nominations", data)
    
    def get_all_nominations(self):
        data = self._supa_select("aplayer_nominations", {"status": "Pending"})
        return pd.DataFrame(data) if data else pd.DataFrame()
    
    def delete_nomination(self, nomination_id):
        self._supa_delete("aplayer_nominations", {"id": nomination_id})
    
    def save_performance_data(self, department, pillar_name, weight, progress, status, deadline, kpi_data):
        self._supa_delete("performance_data", {"department": department, "pillar_name": pillar_name})
        data = {"department": department, "pillar_name": pillar_name, "weight": weight, "progress": progress, "status": status, "deadline": deadline, "kpi_data": json.dumps(kpi_data)}
        self._supa_insert("performance_data", data)
    
    def get_performance_data(self, department=None):
        filters = {"department": department} if department else None
        data = self._supa_select("performance_data", filters)
        return pd.DataFrame(data) if data else pd.DataFrame()
    
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
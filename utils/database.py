import pandas as pd
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import streamlit as st
import requests

class DatabaseManager:
    def __init__(self):
        self.use_supabase = False
        try:
            self.supabase_url = st.secrets["SUPABASE_URL"]
            self.supabase_key = st.secrets["SUPABASE_KEY"]
            self.use_supabase = True
        except:
            import sqlite3
            Path("data").mkdir(exist_ok=True)
            self.sqlite_path = "data/churchgate_hr.db"
    
    def _supabase_query(self, method, endpoint, data=None):
        """Make REST API call to Supabase"""
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        url = f"{self.supabase_url}/rest/v1/{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201]:
            return response.json() if response.text else []
        return []
    
    def execute_query(self, query, params=None, fetch=False):
        if self.use_supabase:
            # For Supabase REST API - handle basic operations
            return []
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                if fetch:
                    rows = cursor.fetchall()
                    result = [dict(row) for row in rows]
                else:
                    conn.commit()
                    result = True
                return result
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
    
    def create_tables(self):
        # Tables are auto-created via Supabase dashboard or SQL editor
        pass
    
    def verify_user(self, email, password):
        if self.use_supabase:
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            # Get user by email first, then check password
            users = self._supabase_query("GET", f"users?email=eq.{email}&select=*")
            if users and len(users) > 0:
                user = users[0]
                if user.get('password') == hashed_pw:
                    return user
            return None
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ? AND is_active = 1", (email, password))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
    
    def create_user(self, employee_id, name, email, password, role, department, position):
        if self.use_supabase:
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            data = {
                "employee_id": employee_id, "name": name, "email": email,
                "password": hashed_pw, "role": role, "department": department,
                "position": position, "is_active": True
            }
            result = self._supabase_query("POST", "users", data)
            return True, "User created"
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
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
    
    def save_aplayer(self, name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk):
        if self.use_supabase:
            data = {
                "name": name, "position": position, "department": department,
                "nominated_by": nominated_by, "perf_score": perf_score,
                "leadership": leadership, "strategic": strategic,
                "peer_review": peer_review, "junior_review": junior_review,
                "independent_review": independent_review, "overall": overall,
                "readiness": readiness, "gap": gap, "risk": risk
            }
            self._supabase_query("POST", "aplayers", data)
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO aplayers (name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk)
            )
            conn.commit()
            conn.close()
    
    def get_all_aplayers(self):
        if self.use_supabase:
            data = self._supabase_query("GET", "aplayers?order=department,overall.desc")
            return pd.DataFrame(data) if data else pd.DataFrame()
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            df = pd.read_sql_query("SELECT * FROM aplayers ORDER BY department, overall DESC", conn)
            conn.close()
            return df
    
    def save_nomination(self, name, position, department, nominated_by, reason, submitted_by, submitted_by_email):
        if self.use_supabase:
            data = {
                "name": name, "position": position, "department": department,
                "nominated_by": nominated_by, "reason": reason,
                "submitted_by": submitted_by, "submitted_by_email": submitted_by_email,
                "status": "Pending"
            }
            self._supabase_query("POST", "aplayer_nominations", data)
    
    def get_all_nominations(self):
        if self.use_supabase:
            data = self._supabase_query("GET", "aplayer_nominations?status=eq.Pending&order=created_at.desc")
            return pd.DataFrame(data) if data else pd.DataFrame()
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            df = pd.read_sql_query("SELECT * FROM aplayer_nominations WHERE status = 'Pending' ORDER BY created_at DESC", conn)
            conn.close()
            return df
    
    def delete_nomination(self, nomination_id):
        if self.use_supabase:
            self._supabase_query("DELETE", f"aplayer_nominations?id=eq.{nomination_id}")
    
    def save_performance_data(self, department, pillar_name, weight, progress, status, deadline, kpi_data):
        if self.use_supabase:
            self._supabase_query("DELETE", f"performance_data?department=eq.{department}&pillar_name=eq.{pillar_name}")
            data = {
                "department": department, "pillar_name": pillar_name,
                "weight": weight, "progress": progress, "status": status,
                "deadline": deadline, "kpi_data": json.dumps(kpi_data)
            }
            self._supabase_query("POST", "performance_data", data)
    
    def get_performance_data(self, department=None):
        if self.use_supabase:
            if department:
                data = self._supabase_query("GET", f"performance_data?department=eq.{department}")
            else:
                data = self._supabase_query("GET", "performance_data")
            return pd.DataFrame(data) if data else pd.DataFrame()
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
    
    def get_all_employees(self):
        return pd.DataFrame()
    
    def get_employee_by_user_id(self, user_id):
        return None
    
    def get_user_notifications(self, user_id, unread_only=False):
        return pd.DataFrame()
    
    def add_notification(self, user_id, title, message, type='Info', link=None):
        pass
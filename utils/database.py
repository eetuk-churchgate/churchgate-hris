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
            self.url = st.secrets["SUPABASE_URL"]
            self.key = st.secrets["SUPABASE_KEY"]
            self.use_supabase = True
        except:
            import sqlite3
            Path("data").mkdir(exist_ok=True)
            self.sqlite_path = "data/churchgate_hr.db"
    
    def _headers(self):
        return {"apikey": self.key, "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
    
    def _get(self, table, filters=None):
        url = f"{self.url}/rest/v1/{table}?select=*"
        if filters:
            for k, v in filters.items():
                url += f"&{k}=eq.{v}"
        r = requests.get(url, headers=self._headers())
        return r.json() if r.status_code == 200 else []
    
    def _post(self, table, data):
        url = f"{self.url}/rest/v1/{table}"
        r = requests.post(url, headers=self._headers(), json=data)
        return r.status_code in [200, 201]
    
    def _patch(self, table, data, filters):
        url = f"{self.url}/rest/v1/{table}?"
        for k, v in filters.items():
            url += f"{k}=eq.{v}&"
        r = requests.patch(url, headers=self._headers(), json=data)
        return r.status_code in [200, 201]
    
    def _delete(self, table, filters):
        url = f"{self.url}/rest/v1/{table}?"
        for k, v in filters.items():
            url += f"{k}=eq.{v}&"
        r = requests.delete(url, headers=self._headers())
        return r.status_code in [200, 201]
    
    def create_tables(self):
        pass
    
    def verify_user(self, email, password):
        if self.use_supabase:
            data = self._get("users", {"email": email})
            if data and len(data) > 0:
                return data[0]
            return None
    
    def create_user(self, employee_id, name, email, password, role, department, position):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        self._post("users", {"employee_id": employee_id, "name": name, "email": email, "password": hashed_pw, "role": role, "department": department, "position": position, "is_active": True})
        return True, "Created"
    
    def update_profile_picture(self, user_id, image_bytes):
        import base64
        b64_str = base64.b64encode(image_bytes).decode('utf-8')
        self._post("profile_pics", {"user_id": str(user_id), "image_data": b64_str})
    
    def get_profile_picture(self, user_id):
        data = self._get("profile_pics", {"user_id": str(user_id)})
        if data and len(data) > 0:
            import base64
            return base64.b64decode(data[0]['image_data'])
        return None
    
    def save_aplayer(self, name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk):
        self._post("aplayers", {"name": name, "position": position, "department": department, "nominated_by": nominated_by, "perf_score": perf_score, "leadership": leadership, "strategic": strategic, "peer_review": peer_review, "junior_review": junior_review, "independent_review": independent_review, "overall": overall, "readiness": readiness, "gap": gap, "risk": risk})
    
    def get_all_aplayers(self):
        data = self._get("aplayers")
        return pd.DataFrame(data) if data else pd.DataFrame()
    
    def save_nomination(self, name, position, department, nominated_by, reason, submitted_by, submitted_by_email):
        self._post("aplayer_nominations", {"name": name, "position": position, "department": department, "nominated_by": nominated_by, "reason": reason, "submitted_by": submitted_by, "submitted_by_email": submitted_by_email, "status": "Pending"})
    
    def get_all_nominations(self):
        data = self._get("aplayer_nominations", {"status": "Pending"})
        return pd.DataFrame(data) if data else pd.DataFrame()
    
    def delete_nomination(self, nomination_id):
        self._delete("aplayer_nominations", {"id": nomination_id})
    
    def save_performance_data(self, department, pillar_name, weight, progress, status, deadline, kpi_data):
        self._delete("performance_data", {"department": department, "pillar_name": pillar_name})
        self._post("performance_data", {"department": department, "pillar_name": pillar_name, "weight": weight, "progress": progress, "status": status, "deadline": deadline, "kpi_data": json.dumps(kpi_data)})
    
    def get_performance_data(self, department=None):
        data = self._get("performance_data")
        return pd.DataFrame(data) if data else pd.DataFrame()
    
    def get_all_employees(self):
        return pd.DataFrame()
    
    def get_employee_by_user_id(self, user_id):
        return None
    
    def add_notification(self, user_id, title, message, type='Info', link=None):
        pass
    
    def get_user_notifications(self, user_id, unread_only=False):
        return pd.DataFrame()
    
    def save_kpi_history(self, action, kpi_name, user, pillar):
        self._post("kpi_history", {"action": action, "kpi_name": kpi_name, "user_name": user, "pillar": pillar, "created_at": datetime.now().strftime('%Y-%m-%d %H:%M')})
    
    def get_kpi_history(self):
        data = self._get("kpi_history")
        return data if data else []
    
    def get_dashboard_stats(self):
        return {'total_employees': 48, 'open_positions': 5, 'new_candidates': 0, 'avg_performance': 85.0}
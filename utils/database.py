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
        self.supabase = None
        try:
            self.url = st.secrets["SUPABASE_URL"]
            self.key = st.secrets["SUPABASE_KEY"]
            from supabase import create_client
            self.supabase = create_client(self.url, self.key)
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
        if r.status_code not in [200, 201]:
            st.error(f"Supabase POST Error [{r.status_code}]: {r.text[:200]}")
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
        import hashlib
        import bcrypt
        
        # Try Supabase client
        if self.use_supabase and self.supabase:
            try:
                result = self.supabase.table("users").select("*").eq("email", email).execute()
                if result.data and len(result.data) > 0:
                    stored_user = result.data[0]
                    stored_hash = stored_user.get('password_hash', '')
                    
                    # Try bcrypt first (new format)
                    if stored_hash.startswith('$2b$'):
                        try:
                            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                                return stored_user
                        except:
                            pass
                    
                    # Try SHA-256 (old format or default)
                    input_hash = hashlib.sha256(password.encode()).hexdigest()
                    if stored_hash == input_hash:
                        return stored_user
                    
                    # Fallback for churchgate2026 default
                    if password == 'churchgate2026' and stored_hash == 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f':
                        return stored_user
            except:
                pass
        
        # Fallback: REST API
        if self.use_supabase:
            data = self._get("users", {"email": email})
            if data and len(data) > 0:
                stored_user = data[0]
                stored_hash = stored_user.get('password_hash', '')
                
                if stored_hash.startswith('$2b$'):
                    try:
                        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                            return stored_user
                    except:
                        pass
                
                input_hash = hashlib.sha256(password.encode()).hexdigest()
                if stored_hash == input_hash:
                    return stored_user
                
                if password == 'churchgate2026' and stored_hash == 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f':
                    return stored_user
        
        return None
    
    def create_user(self, employee_id, name, email, password, role, department, position):
        try:
            import bcrypt
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        except:
            import hashlib
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        self._post("users", {"employee_id": employee_id, "name": name, "email": email, "password": hashed_pw, "role": role, "department": department, "position": position, "is_active": True})
        
        # Send welcome email
        try:
            from utils.email_service import EmailService
            EmailService().send_welcome_email(name, email)
        except:
            pass
        
        return True, "Created"
    
    def update_profile_picture(self, user_id, image_bytes):
        import base64
        b64_str = base64.b64encode(image_bytes).decode('utf-8')
        # Delete old picture first
        self._delete("profile_pics", {"user_id": str(user_id)})
        # Insert new picture
        self._post("profile_pics", {"user_id": str(user_id), "image_data": b64_str})
    
    def get_profile_picture(self, user_id):
        data = self._get("profile_pics", {"user_id": str(user_id)})
        if data and len(data) > 0:
            import base64
            # Return the LAST (most recent) picture
            return base64.b64decode(data[-1]['image_data'])
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
        if self.use_supabase:
            data = self._get("employees")
            if data:
                return pd.DataFrame(data)
            return pd.DataFrame()
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
    
    def save_appraisal(self, user_name, user_email, department, cycle_name, status, scores, comments, pillar_comments, hod_scores, hod_comments, hod_pillar_comments, acceptance, sr_decision, submitted_date):
        existing = self._get("appraisals", {"user_name": user_name, "cycle_name": cycle_name})
        if existing:
            self._delete("appraisals", {"user_name": user_name, "cycle_name": cycle_name})
        self._post("appraisals", {
            "user_name": user_name, "user_email": user_email, "department": department,
            "cycle_name": cycle_name, "status": status,
            "scores": json.dumps(scores) if scores else "{}",
            "comments": comments or "",
            "pillar_comments": json.dumps(pillar_comments) if pillar_comments else "{}",
            "hod_scores": json.dumps(hod_scores) if hod_scores else "{}",
            "hod_comments": hod_comments or "",
            "hod_pillar_comments": json.dumps(hod_pillar_comments) if hod_pillar_comments else "{}",
            "acceptance": acceptance or "",
            "sr_decision": sr_decision or "",
            "submitted_date": submitted_date or ""
        })
    
    def get_all_appraisals(self):
        data = self._get("appraisals")
        if data:
            for item in data:
                for key in ['scores', 'pillar_comments', 'hod_scores', 'hod_pillar_comments']:
                    try:
                        item[key] = json.loads(item[key]) if isinstance(item[key], str) else item[key]
                    except:
                        item[key] = {}
            return data
        return []
    
    def save_audit(self, action, details, user_name, timestamp_text):
        self._post("audit_trail", {
            "action": action, "details": details, "user_name": user_name, "timestamp_text": timestamp_text
        })
    
    def get_audit_trail(self):
        return self._get("audit_trail")

    def archive_appraisal(self, user_name, user_email, department, cycle_name, final_status, scores, hod_scores, comments, hod_comments, completed_date):
        self._post("appraisal_history", {
            "user_name": user_name, "user_email": user_email, "department": department,
            "cycle_name": cycle_name, "final_status": final_status,
            "scores": json.dumps(scores) if scores else "{}",
            "hod_scores": json.dumps(hod_scores) if hod_scores else "{}",
            "comments": comments or "",
            "hod_comments": hod_comments or "",
            "completed_date": completed_date or ""
        })
    
    def get_appraisal_history(self, user_name=None):
        if user_name:
            return self._get("appraisal_history", {"user_name": user_name})
        return self._get("appraisal_history")
    
    def send_status_email(self, to_email, subject, message):
        try:
            email_service.send_email(to_email, subject, message)
            return True
        except:
            return False

    def save_job_requisition(self, req_id, title, department, location, job_type, salary, level, positions, closing, jd, screening, posts, status, submitted_by, date, lm_comment, admin_comment, coo_comment):
        existing = self._get("job_requisitions", {"req_id": req_id})
        if existing:
            self._delete("job_requisitions", {"req_id": req_id})
        self._post("job_requisitions", {
            "req_id": req_id, "title": title, "department": department,
            "location": location, "job_type": job_type, "salary": salary,
            "level": level, "positions": positions, "closing": closing,
            "jd": jd, "screening": json.dumps(screening),
            "posts": json.dumps(posts), "status": status,
            "submitted_by": submitted_by, "date": date,
            "lm_comment": lm_comment, "admin_comment": admin_comment, "coo_comment": coo_comment
        })
    
    def get_all_job_requisitions(self):
        data = self._get("job_requisitions")
        return data if data else []

    def get_all_candidates(self):
        data = self._get("candidates")
        return pd.DataFrame(data) if data else pd.DataFrame()

    def add_candidate(self, candidate_data):
        self._post("candidates", {
            "candidate_ref": candidate_data[0], "first_name": candidate_data[1],
            "last_name": candidate_data[2], "email": candidate_data[3],
            "phone": candidate_data[4], "linkedin_url": candidate_data[5],
            "current_position": candidate_data[6], "current_company": candidate_data[7],
            "years_of_experience": candidate_data[8], "education_level": candidate_data[9],
            "skills": candidate_data[10], "location": candidate_data[11],
            "resume_filename": candidate_data[12], "resume_text": candidate_data[13],
            "job_id": candidate_data[14], "source": candidate_data[15], "status": candidate_data[16]
        })

    def upload_file(self, bucket, file_name, file_content, content_type="application/pdf"):
        if self.use_supabase and self.supabase:
            self.supabase.storage.from_(bucket).upload(file_name, file_content, {"content-type": content_type})
            return self.supabase.storage.from_(bucket).get_public_url(file_name)
        return ""

    def save_portfolio_metric(self, name, value):
        existing = self._get("portfolio_metrics", {"metric_name": name})
        if existing:
            self._patch("portfolio_metrics", {"metric_value": str(value)}, {"metric_name": name})
        else:
            self._post("portfolio_metrics", {"metric_name": name, "metric_value": str(value)})
    
    def get_portfolio_metrics(self):
        data = self._get("portfolio_metrics")
        if data:
            return {item['metric_name']: item['metric_value'] for item in data}
        return {}

    def get_dashboard_stats(self):
        return {'total_employees': 48, 'open_positions': 5, 'new_candidates': 0, 'avg_performance': 85.0}
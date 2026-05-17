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
            if "DB_HOST" in st.secrets:
                from supabase import create_client
                supabase_url = f"https://{st.secrets['DB_HOST'].replace('db.', '')}"
                # Get the project ref from host
                parts = st.secrets['DB_HOST'].split('.')
                project_ref = parts[0]
                supabase_url = f"https://{project_ref}.supabase.co"
                supabase_key = st.secrets.get("SUPABASE_KEY", "")
                if not supabase_key:
                    # Use anon key as fallback
                    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvYmZ5ZHZramZ6aGttaHVxd210ZiIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNzQ3NDk4NDAwLCJleHAiOjIwNjMwNzQ0MDB9.FhE0Z2dLW1JfX0dDRlFZY0p5dDhvVFRhYm0wQXRmWjA"
                self.supabase = create_client(supabase_url, supabase_key)
                self.use_supabase = True
        except Exception as e:
            pass
        
        if not self.use_supabase:
            import sqlite3
            Path("data").mkdir(exist_ok=True)
            self.sqlite_path = "data/churchgate_hr.db"
    
    def _get_pg_conn(self):
        import psycopg2
        conn_string = f"postgresql://{st.secrets['DB_USER']}:{st.secrets['DB_PASSWORD']}@{st.secrets['DB_HOST']}:{st.secrets['DB_PORT']}/{st.secrets['DB_NAME']}?sslmode=require&connect_timeout=10"
        return psycopg2.connect(conn_string)
    
    def execute_query(self, query, params=None, fetch=False):
        if self.use_supabase:
            try:
                import psycopg2
                conn = self._get_pg_conn()
                cursor = conn.cursor()
                
                if params:
                    query = query.replace('?', '%s')
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch:
                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        result = [dict(zip(columns, row)) for row in rows]
                    else:
                        result = []
                else:
                    conn.commit()
                    result = True
                
                cursor.close()
                conn.close()
                return result
            except Exception as e:
                try:
                    conn.rollback()
                except:
                    pass
                raise e
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
        queries = [
            '''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY, employee_id TEXT UNIQUE, name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL,
                department TEXT, position TEXT, is_active BOOLEAN DEFAULT TRUE,
                profile_picture BYTEA, last_login TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY, employee_id TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
                phone TEXT, department TEXT NOT NULL, position TEXT NOT NULL, grade TEXT,
                employment_type TEXT, join_date DATE, status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS aplayers (
                id SERIAL PRIMARY KEY, name TEXT NOT NULL, position TEXT,
                department TEXT NOT NULL, nominated_by TEXT, perf_score REAL DEFAULT 0,
                leadership REAL DEFAULT 0, strategic REAL DEFAULT 0, peer_review REAL DEFAULT 0,
                junior_review REAL DEFAULT 0, independent_review REAL DEFAULT 0, overall REAL DEFAULT 0,
                readiness TEXT DEFAULT 'Pending Assessment', gap TEXT DEFAULT 'TBD', risk TEXT DEFAULT 'TBD',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS aplayer_nominations (
                id SERIAL PRIMARY KEY, name TEXT NOT NULL, position TEXT,
                department TEXT NOT NULL, nominated_by TEXT, reason TEXT,
                submitted_by TEXT, submitted_by_email TEXT, status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS performance_data (
                id SERIAL PRIMARY KEY, department TEXT NOT NULL,
                pillar_name TEXT NOT NULL, weight REAL DEFAULT 0, progress REAL DEFAULT 0,
                status TEXT DEFAULT 'On Track', deadline TEXT, kpi_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL,
                title TEXT NOT NULL, message TEXT, type TEXT DEFAULT 'Info',
                is_read BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
        ]
        
        for query in queries:
            try:
                self.execute_query(query)
            except:
                pass
        
        # Insert default users
        try:
            result = self.execute_query("SELECT COUNT(*) as cnt FROM users WHERE email = 'admin@churchgate.com'", fetch=True)
            count = result[0]['cnt'] if result else 0
            if count == 0:
                admin_password = hashlib.sha256("admin123".encode()).hexdigest()
                self.execute_query(
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (%s, %s, %s, %s, %s, %s, %s)" if self.use_supabase else
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ('ADM001', 'Admin User', 'admin@churchgate.com', admin_password, 'Admin', 'Senior Management', 'System Administrator')
                )
                
                eetuk_password = hashlib.sha256("churchgate2026".encode()).hexdigest()
                self.execute_query(
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (%s, %s, %s, %s, %s, %s, %s)" if self.use_supabase else
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ('AN00387', 'Emmanuel Etuk', 'eetuk@churchgate.com', eetuk_password, 'Admin', 'Senior Management', 'Head, ELV Systems')
                )
                
                vinay_password = hashlib.sha256("churchgate2026".encode()).hexdigest()
                self.execute_query(
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (%s, %s, %s, %s, %s, %s, %s)" if self.use_supabase else
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ('GMD01', 'Vinay Mahtani', 'vbmahtani@churchgate.com', vinay_password, 'Admin', 'Senior Management', 'GMD')
                )
                
                jerome_password = hashlib.sha256("churchgate2026".encode()).hexdigest()
                self.execute_query(
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (%s, %s, %s, %s, %s, %s, %s)" if self.use_supabase else
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ('LE00019', 'Jerome Das', 'jeromedas@churchgate.com', jerome_password, 'Admin', 'Senior Management', 'COO')
                )
        except:
            pass
    
    def verify_user(self, email, password):
        result = self.execute_query(
            "SELECT * FROM users WHERE email = ? AND password = ? AND is_active = TRUE",
            (email, password), fetch=True
        )
        user = result[0] if result else None
        return user
    
    def create_user(self, employee_id, name, email, password, role, department, position):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.execute_query(
                "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (employee_id, name, email, hashed_pw, role, department, position)
            )
            return True, "User created successfully"
        except Exception as e:
            return False, str(e)
    
    def get_all_employees(self):
        return pd.DataFrame(self.execute_query("SELECT * FROM employees WHERE status = 'Active'", fetch=True) or [])
    
    def get_employee_by_user_id(self, user_id):
        result = self.execute_query("SELECT employee_id FROM users WHERE id = ?", (user_id,), fetch=True)
        if result and result[0].get('employee_id'):
            emp = self.execute_query("SELECT * FROM employees WHERE employee_id = ?", (result[0]['employee_id'],), fetch=True)
            return emp[0] if emp else None
        return None
    
    def add_notification(self, user_id, title, message, type='Info', link=None):
        try:
            self.execute_query(
                "INSERT INTO notifications (user_id, title, message, type, link) VALUES (?, ?, ?, ?, ?)",
                (user_id, title, message, type, link)
            )
        except:
            pass
    
    def get_user_notifications(self, user_id, unread_only=False):
        try:
            if unread_only:
                return pd.DataFrame(self.execute_query(
                    "SELECT * FROM notifications WHERE user_id = ? AND is_read = FALSE ORDER BY created_at DESC", (user_id,), fetch=True
                ) or [])
            return pd.DataFrame(self.execute_query(
                "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 20", (user_id,), fetch=True
            ) or [])
        except:
            return pd.DataFrame()
    
    # A-Player Methods
    def save_aplayer(self, name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk):
        self.execute_query(
            "INSERT INTO aplayers (name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk)
        )
    
    def get_all_aplayers(self):
        return pd.DataFrame(self.execute_query("SELECT * FROM aplayers ORDER BY department, overall DESC", fetch=True) or [])
    
    def save_nomination(self, name, position, department, nominated_by, reason, submitted_by, submitted_by_email):
        self.execute_query(
            "INSERT INTO aplayer_nominations (name, position, department, nominated_by, reason, submitted_by, submitted_by_email) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, position, department, nominated_by, reason, submitted_by, submitted_by_email)
        )
    
    def get_all_nominations(self):
        return pd.DataFrame(self.execute_query("SELECT * FROM aplayer_nominations WHERE status = 'Pending' ORDER BY created_at DESC", fetch=True) or [])
    
    def delete_nomination(self, nomination_id):
        self.execute_query("DELETE FROM aplayer_nominations WHERE id = ?", (nomination_id,))
    
    # Performance Methods
    def save_performance_data(self, department, pillar_name, weight, progress, status, deadline, kpi_data):
        self.execute_query("DELETE FROM performance_data WHERE department = ? AND pillar_name = ?", (department, pillar_name))
        self.execute_query(
            "INSERT INTO performance_data (department, pillar_name, weight, progress, status, deadline, kpi_data) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (department, pillar_name, weight, progress, status, deadline, json.dumps(kpi_data))
        )
    
    def get_performance_data(self, department=None):
        if department:
            return pd.DataFrame(self.execute_query("SELECT * FROM performance_data WHERE department = ?", (department,), fetch=True) or [])
        return pd.DataFrame(self.execute_query("SELECT * FROM performance_data", fetch=True) or [])
    
    def get_dashboard_stats(self):
        try:
            emp = self.execute_query("SELECT COUNT(*) as cnt FROM employees WHERE status = 'Active'", fetch=True)
            total_employees = emp[0]['cnt'] if emp else 0
            return {'total_employees': total_employees, 'open_positions': 5, 'new_candidates': 0, 'avg_performance': 85.0}
        except:
            return {'total_employees': 0, 'open_positions': 0, 'new_candidates': 0, 'avg_performance': 0}
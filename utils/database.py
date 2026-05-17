import pandas as pd
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import streamlit as st

class DatabaseManager:
    def __init__(self):
        self.db_url = st.secrets.get("DATABASE_URL", "")
        if not self.db_url:
            # Fallback to SQLite for local development
            self.use_postgres = False
            import sqlite3
            Path("data").mkdir(exist_ok=True)
            self.sqlite_path = "data/churchgate_hr.db"
        else:
            self.use_postgres = True
    
    def get_connection(self):
        if self.use_postgres:
            import psycopg2
            conn = psycopg2.connect(self.db_url)
            return conn
        else:
            import sqlite3
            conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
    
    def execute_query(self, query, params=None, fetch=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                # Convert ? to %s for PostgreSQL
                if self.use_postgres:
                    query = query.replace('?', '%s')
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                if self.use_postgres:
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    rows = cursor.fetchall()
                    result = [dict(zip(columns, row)) for row in rows]
                else:
                    rows = cursor.fetchall()
                    result = [dict(row) for row in rows]
                return result
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def create_tables(self):
        if self.use_postgres:
            self._create_postgres_tables()
        else:
            self._create_sqlite_tables()
    
    def _create_postgres_tables(self):
        queries = [
            '''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                employee_id TEXT UNIQUE,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT,
                position TEXT,
                manager_id INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                profile_picture BYTEA,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                employee_id TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                department TEXT NOT NULL,
                position TEXT NOT NULL,
                grade TEXT,
                employment_type TEXT,
                join_date DATE,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS departments (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                code TEXT UNIQUE,
                head_id INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS job_postings (
                id SERIAL PRIMARY KEY,
                job_reference TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                department TEXT NOT NULL,
                location TEXT,
                employment_type TEXT,
                salary_range TEXT,
                description TEXT,
                requirements TEXT,
                status TEXT DEFAULT 'Open',
                posted_by INTEGER,
                posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closing_date DATE
            )''',
            '''CREATE TABLE IF NOT EXISTS candidates (
                id SERIAL PRIMARY KEY,
                candidate_ref TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                linkedin_url TEXT,
                current_position TEXT,
                years_of_experience REAL,
                education_level TEXT,
                skills TEXT,
                location TEXT,
                resume_filename TEXT,
                resume_text TEXT,
                job_id INTEGER,
                ai_score REAL,
                ai_tier TEXT,
                status TEXT DEFAULT 'New',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS aplayers (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT,
                department TEXT NOT NULL,
                nominated_by TEXT,
                perf_score REAL DEFAULT 0,
                leadership REAL DEFAULT 0,
                strategic REAL DEFAULT 0,
                peer_review REAL DEFAULT 0,
                junior_review REAL DEFAULT 0,
                independent_review REAL DEFAULT 0,
                overall REAL DEFAULT 0,
                readiness TEXT DEFAULT 'Pending Assessment',
                gap TEXT DEFAULT 'TBD',
                risk TEXT DEFAULT 'TBD',
                approval_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS aplayer_nominations (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT,
                department TEXT NOT NULL,
                nominated_by TEXT,
                reason TEXT,
                submitted_by TEXT,
                submitted_by_email TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS performance_data (
                id SERIAL PRIMARY KEY,
                department TEXT NOT NULL,
                pillar_name TEXT NOT NULL,
                weight REAL DEFAULT 0,
                progress REAL DEFAULT 0,
                status TEXT DEFAULT 'On Track',
                deadline TEXT,
                kpi_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT,
                type TEXT DEFAULT 'Info',
                is_read BOOLEAN DEFAULT FALSE,
                link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
        ]
        
        for query in queries:
            try:
                self.execute_query(query)
            except:
                pass
        
        # Insert default data
        self._insert_default_data()
    
    def _create_sqlite_tables(self):
        import sqlite3
        conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, employee_id TEXT UNIQUE, name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL,
            department TEXT, position TEXT, manager_id INTEGER, is_active BOOLEAN DEFAULT 1,
            profile_picture BLOB, last_login TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT, employee_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
            phone TEXT, department TEXT NOT NULL, position TEXT NOT NULL, grade TEXT,
            employment_type TEXT, join_date DATE, status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS aplayers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, position TEXT,
            department TEXT NOT NULL, nominated_by TEXT, perf_score REAL DEFAULT 0,
            leadership REAL DEFAULT 0, strategic REAL DEFAULT 0, peer_review REAL DEFAULT 0,
            junior_review REAL DEFAULT 0, independent_review REAL DEFAULT 0, overall REAL DEFAULT 0,
            readiness TEXT DEFAULT 'Pending Assessment', gap TEXT DEFAULT 'TBD', risk TEXT DEFAULT 'TBD',
            approval_reason TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS aplayer_nominations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, position TEXT,
            department TEXT NOT NULL, nominated_by TEXT, reason TEXT, submitted_by TEXT,
            submitted_by_email TEXT, status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS performance_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT, department TEXT NOT NULL,
            pillar_name TEXT NOT NULL, weight REAL DEFAULT 0, progress REAL DEFAULT 0,
            status TEXT DEFAULT 'On Track', deadline TEXT, kpi_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            title TEXT NOT NULL, message TEXT, type TEXT DEFAULT 'Info',
            is_read BOOLEAN DEFAULT 0, link TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
        self._insert_default_data()
    
    def _insert_default_data(self):
        try:
            result = self.execute_query("SELECT COUNT(*) as cnt FROM users WHERE email = 'admin@churchgate.com'", fetch=True)
            if result and result[0]['cnt'] == 0:
                admin_password = hashlib.sha256("admin123".encode()).hexdigest()
                self.execute_query(
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ('ADM001', 'Admin User', 'admin@churchgate.com', admin_password, 'Admin', 'Senior Management', 'System Administrator')
                )
                
                hr_password = hashlib.sha256("hr123".encode()).hexdigest()
                self.execute_query(
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ('LN00037', 'Adebayo Sakote', 'asakote@churchgate.com', hr_password, 'HR Director', 'Human Resources', 'HR Manager')
                )
                
                eetuk_password = hashlib.sha256("churchgate2026".encode()).hexdigest()
                self.execute_query(
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ('AN00387', 'Emmanuel Etuk', 'eetuk@churchgate.com', eetuk_password, 'Admin', 'Senior Management', 'Head, ELV Systems')
                )
                
                vinay_password = hashlib.sha256("churchgate2026".encode()).hexdigest()
                self.execute_query(
                    "INSERT INTO users (employee_id, name, email, password, role, department, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ('GMD01', 'Vinay Mahtani', 'vbmahtani@churchgate.com', vinay_password, 'Admin', 'Senior Management', 'GMD')
                )
                
                jerome_password = hashlib.sha256("churchgate2026".encode()).hexdigest()
                self.execute_query(
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
        if user:
            self.execute_query("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user['id'],))
        return user
    
    def get_all_users(self):
        return pd.DataFrame(self.execute_query(
            "SELECT id, employee_id, name, email, role, department, position, is_active, last_login FROM users", fetch=True
        ))
    
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
        return pd.DataFrame(self.execute_query("SELECT * FROM employees WHERE status = 'Active'", fetch=True))
    
    def get_employee_by_id(self, employee_id):
        result = self.execute_query("SELECT * FROM employees WHERE id = ?", (employee_id,), fetch=True)
        return result[0] if result else None
    
    def get_employee_by_user_id(self, user_id):
        user_result = self.execute_query("SELECT employee_id FROM users WHERE id = ?", (user_id,), fetch=True)
        if user_result and user_result[0]['employee_id']:
            emp_result = self.execute_query("SELECT * FROM employees WHERE employee_id = ?", (user_result[0]['employee_id'],), fetch=True)
            return emp_result[0] if emp_result else None
        return None
    
    def add_employee(self, employee_data):
        self.execute_query(
            "INSERT INTO employees (employee_id, first_name, last_name, email, phone, department, position, grade, employment_type, join_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            employee_data
        )
    
    def create_job_posting(self, job_data):
        self.execute_query(
            "INSERT INTO job_postings (job_reference, title, department, location, employment_type, salary_range, description, requirements, posted_by, closing_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            job_data
        )
    
    def get_all_jobs(self, status=None):
        if status:
            return pd.DataFrame(self.execute_query("SELECT * FROM job_postings WHERE status = ?", (status,), fetch=True))
        return pd.DataFrame(self.execute_query("SELECT * FROM job_postings", fetch=True))
    
    def add_candidate(self, candidate_data):
        self.execute_query(
            "INSERT INTO candidates (candidate_ref, first_name, last_name, email, phone, linkedin_url, current_position, years_of_experience, education_level, skills, location, resume_filename, resume_text, job_id, source, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            candidate_data
        )
    
    def update_candidate_ai_score(self, candidate_id, ai_score, ai_tier, ai_analysis, skills_match, experience_match, education_match, overall_fit, linkedin_verified, key_strengths, gaps, recommendation):
        self.execute_query(
            "UPDATE candidates SET ai_score = ?, ai_tier = ?, ai_analysis = ?, skills_match_percent = ?, experience_match_percent = ?, education_match_percent = ?, overall_fit_percent = ?, linkedin_verified = ?, key_strengths = ?, gaps_identified = ?, interview_recommendation = ? WHERE id = ?",
            (ai_score, ai_tier, ai_analysis, skills_match, experience_match, education_match, overall_fit, linkedin_verified, key_strengths, gaps, recommendation, candidate_id)
        )
    
    def get_all_candidates(self):
        return pd.DataFrame(self.execute_query("SELECT * FROM candidates ORDER BY created_at DESC", fetch=True))
    
    def add_notification(self, user_id, title, message, type='Info', link=None):
        self.execute_query(
            "INSERT INTO notifications (user_id, title, message, type, link) VALUES (?, ?, ?, ?, ?)",
            (user_id, title, message, type, link)
        )
    
    def get_user_notifications(self, user_id, unread_only=False):
        if unread_only:
            return pd.DataFrame(self.execute_query(
                "SELECT * FROM notifications WHERE user_id = ? AND is_read = FALSE ORDER BY created_at DESC", (user_id,), fetch=True
            ))
        return pd.DataFrame(self.execute_query(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 20", (user_id,), fetch=True
        ))
    
    # A-Player Methods
    def save_aplayer(self, name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk):
        self.execute_query(
            "INSERT INTO aplayers (name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, position, department, nominated_by, perf_score, leadership, strategic, peer_review, junior_review, independent_review, overall, readiness, gap, risk)
        )
    
    def get_all_aplayers(self):
        return pd.DataFrame(self.execute_query("SELECT * FROM aplayers ORDER BY department, overall DESC", fetch=True))
    
    def save_nomination(self, name, position, department, nominated_by, reason, submitted_by, submitted_by_email):
        self.execute_query(
            "INSERT INTO aplayer_nominations (name, position, department, nominated_by, reason, submitted_by, submitted_by_email) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, position, department, nominated_by, reason, submitted_by, submitted_by_email)
        )
    
    def get_all_nominations(self):
        return pd.DataFrame(self.execute_query("SELECT * FROM aplayer_nominations WHERE status = 'Pending' ORDER BY created_at DESC", fetch=True))
    
    def delete_nomination(self, nomination_id):
        self.execute_query("DELETE FROM aplayer_nominations WHERE id = ?", (nomination_id,))
    
    # Performance Methods
    def save_performance_data(self, department, pillar_name, weight, progress, status, deadline, kpi_data):
        self.execute_query(
            "DELETE FROM performance_data WHERE department = ? AND pillar_name = ?",
            (department, pillar_name)
        )
        self.execute_query(
            "INSERT INTO performance_data (department, pillar_name, weight, progress, status, deadline, kpi_data) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (department, pillar_name, weight, progress, status, deadline, json.dumps(kpi_data))
        )
    
    def get_performance_data(self, department=None):
        if department:
            return pd.DataFrame(self.execute_query("SELECT * FROM performance_data WHERE department = ?", (department,), fetch=True))
        return pd.DataFrame(self.execute_query("SELECT * FROM performance_data", fetch=True))
    
    def get_dashboard_stats(self):
        result = self.execute_query("SELECT COUNT(*) as cnt FROM employees WHERE status = 'Active'", fetch=True)
        total_employees = result[0]['cnt'] if result else 0
        result2 = self.execute_query("SELECT COUNT(*) as cnt FROM job_postings WHERE status = 'Open'", fetch=True)
        open_positions = result2[0]['cnt'] if result2 else 0
        result3 = self.execute_query("SELECT COUNT(*) as cnt FROM candidates WHERE status = 'New'", fetch=True)
        new_candidates = result3[0]['cnt'] if result3 else 0
        
        return {
            'total_employees': total_employees,
            'open_positions': open_positions,
            'new_candidates': new_candidates,
            'avg_performance': 85.0
        }
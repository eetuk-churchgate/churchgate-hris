import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="data/churchgate_hr.db"):
        Path("data").mkdir(exist_ok=True)
        self.db_path = db_path
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT,
                position TEXT,
                manager_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                profile_picture BLOB,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                date_of_birth DATE,
                gender TEXT,
                marital_status TEXT,
                address TEXT,
                department TEXT NOT NULL,
                position TEXT NOT NULL,
                grade TEXT,
                salary_grade TEXT,
                employment_type TEXT,
                join_date DATE,
                confirmation_date DATE,
                manager_id INTEGER,
                emergency_contact_name TEXT,
                emergency_contact_phone TEXT,
                bank_name TEXT,
                account_number TEXT,
                pension_id TEXT,
                tax_id TEXT,
                status TEXT DEFAULT 'Active',
                profile_picture BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                code TEXT UNIQUE,
                head_id INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_postings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_reference TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                department TEXT NOT NULL,
                location TEXT,
                employment_type TEXT,
                salary_range TEXT,
                description TEXT,
                requirements TEXT,
                responsibilities TEXT,
                qualifications TEXT,
                experience_level TEXT,
                skills_required TEXT,
                number_of_positions INTEGER DEFAULT 1,
                status TEXT DEFAULT 'Open',
                posted_by INTEGER,
                posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closing_date DATE,
                is_remote BOOLEAN DEFAULT 0,
                career_page_visible BOOLEAN DEFAULT 1,
                FOREIGN KEY (posted_by) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_ref TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                linkedin_url TEXT,
                github_url TEXT,
                portfolio_url TEXT,
                current_position TEXT,
                current_company TEXT,
                years_of_experience REAL,
                education_level TEXT,
                education_details TEXT,
                skills TEXT,
                certifications TEXT,
                languages TEXT,
                location TEXT,
                expected_salary REAL,
                notice_period TEXT,
                resume_filename TEXT,
                resume_text TEXT,
                resume_file BLOB,
                cover_letter TEXT,
                source TEXT DEFAULT 'Direct',
                job_id INTEGER,
                ai_score REAL,
                ai_tier TEXT,
                ai_analysis TEXT,
                skills_match_percent REAL,
                experience_match_percent REAL,
                education_match_percent REAL,
                overall_fit_percent REAL,
                linkedin_verified BOOLEAN DEFAULT 0,
                key_strengths TEXT,
                gaps_identified TEXT,
                interview_recommendation TEXT,
                status TEXT DEFAULT 'New',
                stage TEXT DEFAULT 'Applied',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES job_postings(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                reviewer_id INTEGER NOT NULL,
                review_period TEXT NOT NULL,
                review_type TEXT DEFAULT 'Annual',
                overall_rating REAL,
                objectives_rating REAL,
                competencies_rating REAL,
                leadership_rating REAL,
                teamwork_rating REAL,
                communication_rating REAL,
                technical_skills_rating REAL,
                strengths TEXT,
                areas_for_improvement TEXT,
                employee_comments TEXT,
                reviewer_comments TEXT,
                goals_next_period TEXT,
                training_needs TEXT,
                promotion_readiness TEXT,
                status TEXT DEFAULT 'Draft',
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                FOREIGN KEY (reviewer_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS objectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                key_results TEXT,
                weight REAL DEFAULT 1.0,
                target_value REAL,
                current_value REAL DEFAULT 0,
                progress_percent REAL DEFAULT 0,
                start_date DATE,
                end_date DATE,
                status TEXT DEFAULT 'Not Started',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                from_position TEXT,
                to_position TEXT,
                from_grade TEXT,
                to_grade TEXT,
                from_salary REAL,
                to_salary REAL,
                salary_increase_percent REAL,
                effective_date DATE,
                reason TEXT,
                approved_by INTEGER,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                FOREIGN KEY (approved_by) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                interview_type TEXT,
                interviewer_id INTEGER,
                scheduled_date TIMESTAMP,
                duration_minutes INTEGER DEFAULT 60,
                location TEXT,
                meeting_link TEXT,
                status TEXT DEFAULT 'Scheduled',
                feedback TEXT,
                rating REAL,
                recommendation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id),
                FOREIGN KEY (job_id) REFERENCES job_postings(id),
                FOREIGN KEY (interviewer_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT,
                type TEXT DEFAULT 'Info',
                is_read BOOLEAN DEFAULT 0,
                link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                candidate_id INTEGER,
                document_type TEXT NOT NULL,
                document_name TEXT NOT NULL,
                file_data BLOB,
                file_path TEXT,
                uploaded_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                FOREIGN KEY (candidate_id) REFERENCES candidates(id),
                FOREIGN KEY (uploaded_by) REFERENCES users(id)
            )
        ''')
        
        departments = [
            ('Senior Management', 'SM', None, 'Senior Leadership'),
            ('Human Resources', 'HR', None, 'Human Resources Department'),
            ('Technology Group', 'TECH', None, 'ELV Systems & Technology'),
            ('Sales & Marketing', 'SALES', None, 'Sales & Business Development'),
            ('Accounts & Finance', 'FIN', None, 'Finance & Accounting'),
            ('Operations', 'OPS', None, 'Operations & Logistics'),
            ('Facility Management', 'FM', None, 'Facility Management'),
            ('Legal', 'LEGAL', None, 'Legal & Compliance'),
            ('Procurement', 'PROC', None, 'Procurement'),
            ('Security', 'SEC', None, 'Security'),
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO departments (name, code, head_id, description)
            VALUES (?, ?, ?, ?)
        ''', departments)
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@churchgate.com'")
        if cursor.fetchone()[0] == 0:
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (employee_id, name, email, password, role, department, position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('ADM001', 'Admin User', 'admin@churchgate.com', admin_password, 'Admin', 'Senior Management', 'System Administrator'))
            
            hr_password = hashlib.sha256("hr123".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (employee_id, name, email, password, role, department, position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('LN00037', 'Adebayo Sakote', 'asakote@churchgate.com', hr_password, 'HR Director', 'Human Resources', 'HR Manager'))
            
            eetuk_password = hashlib.sha256("churchgate2026".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (employee_id, name, email, password, role, department, position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('AN00387', 'Emmanuel Etuk', 'eetuk@churchgate.com', eetuk_password, 'Admin', 'Senior Management', 'Head, ELV Systems'))
            
            vinay_password = hashlib.sha256("churchgate2026".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (employee_id, name, email, password, role, department, position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('GMD01', 'Vinay Mahtani', 'vbmahtani@churchgate.com', vinay_password, 'Admin', 'Senior Management', 'GMD'))
            
            jerome_password = hashlib.sha256("churchgate2026".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (employee_id, name, email, password, role, department, position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('LE00019', 'Jerome Das', 'jeromedas@churchgate.com', jerome_password, 'Admin', 'Senior Management', 'COO'))
            
            sample_employees = [
                ('AN00387', 'Emmanuel', 'Etuk', 'eetuk@churchgate.com', '+234-09092922509', 'Senior Management', 'Head, ELV Systems', 'Manager', 'Full-time', '2019-01-02'),
                ('GMD01', 'Vinay', 'Mahtani', 'vbmahtani@churchgate.com', '+234-00070300000', 'Senior Management', 'GMD', 'C-Level', 'Full-time', '2018-08-29'),
                ('LE00019', 'Jerome', 'Das', 'jeromedas@churchgate.com', '', 'Senior Management', 'COO', 'C-Level', 'Full-time', '2015-01-01'),
                ('LE00212', 'Sanjeev', 'Purwar', 'purwar@churchgate.com', '+234-08033606471', 'Facility Management', 'Head, MEP', 'Manager', 'Full-time', '1997-07-11'),
                ('LN00369', 'Ahmed', 'Karim', 'akarim@churchgate.com', '+234-09027363561', 'Sales & Marketing', 'GM, Sales & Marketing', 'Manager', 'Full-time', '2021-04-19'),
                ('AN00012', 'Ibukun', 'Adeogun', 'adeogun@churchgate.com', '+234-08033012808', 'Operations', 'GM, Operations/Admin', 'Manager', 'Full-time', '1991-04-04'),
                ('LN00008', 'Jeff', 'Arikawe', 'jeff@churchgate.com', '+234-07036233478', 'Accounts & Finance', 'Chief Accountant', 'Manager', 'Full-time', '1991-06-09'),
                ('LN00037', 'Adebayo', 'Sakote', 'asakote@churchgate.com', '', 'Human Resources', 'HR Manager', 'Manager', 'Full-time', '2020-01-01'),
                ('LE00071', 'Anand', 'Bora', 'abora@churchgate.com', '', 'Procurement', 'GM, Procurement', 'Manager', 'Full-time', '2018-01-01'),
                ('AN00391', 'Maikudi', 'Kadoh', 'mkadoh@churchgate.com', '+234-08033162042', 'Security', 'Chief Security Officer', 'Manager', 'Full-time', '2017-12-05'),
                ('AN00455', 'David', 'Aiyedun', 'daiyedun@churchgate.com', '+234-08062114849', 'Legal', 'Legal Officer', 'Senior', 'Full-time', '2022-10-24'),
                ('AN00400', 'Charles', 'Okere', 'cokere@churchgate.com', '+234-08033618587', 'Facility Management', 'Lift Supervisor', 'Senior', 'Full-time', '2018-05-15'),
                ('AN00398', 'George', 'Ojile', 'gojile@churchgate.com', '+234-08035673006', 'Facility Management', 'Lift Engineer', 'Senior', 'Full-time', '2018-04-24'),
                ('AN00425', 'Augustine', 'Oleh', 'aoleh@churchgate.com', '+234-08062069622', 'Facility Management', 'HSE Coordinator', 'Senior', 'Full-time', '2021-05-03'),
                ('AN00433', 'Francis', 'Asuquo', 'fasuquo@churchgate.com', '+234-08136403113', 'Technology Group', 'ELV Engineer', 'Junior', 'Full-time', '2022-01-21'),
                ('LN00438', 'Chika', 'Ikwuegbu', 'cikwuegbu@churchgate.com', '+234-08026822643', 'Security', 'Admin Assistant', 'Junior', 'Full-time', '2022-05-21'),
                ('AN00423', 'Alice', 'Agbo', 'aagbo@churchgate.com', '+234-08066792728', 'Procurement', 'Store Keeper', 'Junior', 'Full-time', '2021-02-22'),
                ('AN00460', 'Rhoda', 'Ajibola', 'rajibola@churchgate.com', '+234-07080037934', 'Facility Management', 'Front Desk Executive', 'Junior', 'Full-time', '2023-02-02'),
                ('AN00451', 'Ogechukwu', 'Obute', 'jobute@churchgate.com', '+234-09082989886', 'Sales & Marketing', 'Sales Executive', 'Junior', 'Full-time', '2022-10-03'),
                ('AN00496', 'David', 'Effiong', 'deffiong@churchgate.com', '+234-08036451805', 'Facility Management', 'Facility Manager', 'Manager', 'Full-time', '2025-01-20'),
            ]
            cursor.executemany('''
                INSERT INTO employees (employee_id, first_name, last_name, email, phone, department, position, grade, employment_type, join_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_employees)
        
        conn.commit()
        conn.close()
    
    def verify_user(self, email, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ? AND is_active = 1", (email, password))
        row = cursor.fetchone()
        user = dict(row) if row else None
        if user:
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user['id'],))
            conn.commit()
        conn.close()
        return user
    
    def get_all_users(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT id, employee_id, name, email, role, department, position, is_active, last_login FROM users", conn)
        conn.close()
        return df
    
    def create_user(self, employee_id, name, email, password, role, department, position):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute('''
                INSERT INTO users (employee_id, name, email, password, role, department, position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, name, email, hashed_pw, role, department, position))
            conn.commit()
            return True, "User created successfully"
        except sqlite3.IntegrityError:
            return False, "Email or Employee ID already exists"
        finally:
            conn.close()
    
    def get_all_employees(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM employees WHERE status = 'Active'", conn)
        conn.close()
        return df
    
    def get_employee_by_id(self, employee_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
        row = cursor.fetchone()
        employee = dict(row) if row else None
        conn.close()
        return employee
    
    def get_employee_by_user_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT employee_id FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        if user_row and user_row['employee_id']:
            cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (user_row['employee_id'],))
            row = cursor.fetchone()
            employee = dict(row) if row else None
            conn.close()
            return employee
        conn.close()
        return None
    
    def add_employee(self, employee_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO employees (employee_id, first_name, last_name, email, phone, department, 
                                 position, grade, employment_type, join_date, manager_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', employee_data)
        conn.commit()
        conn.close()
    
    def create_job_posting(self, job_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO job_postings (job_reference, title, department, location, employment_type,
                                    salary_range, description, requirements, responsibilities,
                                    qualifications, experience_level, skills_required, posted_by, closing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', job_data)
        conn.commit()
        job_id = cursor.lastrowid
        conn.close()
        return job_id
    
    def get_all_jobs(self, status=None):
        conn = self.get_connection()
        if status:
            df = pd.read_sql_query("SELECT * FROM job_postings WHERE status = ?", conn, params=(status,))
        else:
            df = pd.read_sql_query("SELECT * FROM job_postings", conn)
        conn.close()
        return df
    
    def add_candidate(self, candidate_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO candidates (candidate_ref, first_name, last_name, email, phone, linkedin_url,
                                  current_position, current_company, years_of_experience, education_level,
                                  skills, location, resume_filename, resume_text, job_id, source, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', candidate_data)
        conn.commit()
        candidate_id = cursor.lastrowid
        conn.close()
        return candidate_id
    
    def update_candidate_ai_score(self, candidate_id, ai_score, ai_tier, ai_analysis, 
                                   skills_match, experience_match, education_match, overall_fit,
                                   linkedin_verified, key_strengths, gaps, recommendation):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE candidates SET 
                ai_score = ?, ai_tier = ?, ai_analysis = ?, 
                skills_match_percent = ?, experience_match_percent = ?, 
                education_match_percent = ?, overall_fit_percent = ?,
                linkedin_verified = ?, key_strengths = ?, gaps_identified = ?,
                interview_recommendation = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (ai_score, ai_tier, ai_analysis, skills_match, experience_match, 
              education_match, overall_fit, linkedin_verified, key_strengths, 
              gaps, recommendation, candidate_id))
        conn.commit()
        conn.close()
    
    def get_candidates_by_job(self, job_id):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM candidates WHERE job_id = ? ORDER BY ai_score DESC", conn, params=(job_id,))
        conn.close()
        return df
    
    def get_all_candidates(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM candidates ORDER BY created_at DESC", conn)
        conn.close()
        return df
    
    def add_objective(self, employee_id, title, description, key_results, target_value, start_date, end_date, weight=1.0):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO objectives (employee_id, title, description, key_results, weight, target_value, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (employee_id, title, description, key_results, weight, target_value, start_date, end_date))
        conn.commit()
        conn.close()
    
    def get_employee_objectives(self, employee_id):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM objectives WHERE employee_id = ?", conn, params=(employee_id,))
        conn.close()
        return df
    
    def add_notification(self, user_id, title, message, type='Info', link=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, link)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, title, message, type, link))
        conn.commit()
        conn.close()
    
    def get_user_notifications(self, user_id, unread_only=False):
        conn = self.get_connection()
        if unread_only:
            df = pd.read_sql_query("SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY created_at DESC", 
                                   conn, params=(user_id,))
        else:
            df = pd.read_sql_query("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 20", 
                                   conn, params=(user_id,))
        conn.close()
        return df
    
    def get_dashboard_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 'Active'")
        total_employees = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM job_postings WHERE status = 'Open'")
        open_positions = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM candidates WHERE status = 'New'")
        new_candidates = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(overall_rating) FROM performance_reviews")
        avg_performance = cursor.fetchone()[0] or 0
        conn.close()
        return {
            'total_employees': total_employees,
            'open_positions': open_positions,
            'new_candidates': new_candidates,
            'avg_performance': round(avg_performance, 1)
        }
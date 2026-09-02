"""
Auto Celebration Email Sender - Runs daily at 7:30 AM via Railway Cron
Churchgate Group HRIS
"""

import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import pandas as pd
from utils.database import DatabaseManager
from utils.email_service import EmailService

db = DatabaseManager()

def check_and_send_celebrations():
    """Check for birthdays/anniversaries and send emails to ALL employees"""
    today = datetime.now()
    print(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] Checking celebrations for {today.strftime('%A, %B %d, %Y')}...")
    
    try:
        employees = db.get_all_employees()
        if employees.empty:
            print("❌ No employees found in database")
            return
        
        birthday_names = []
        anniversary_names = []
        
        for _, emp in employees.iterrows():
            # Check birthdays
            dob = emp.get('date_of_birth')
            if dob and str(dob) != 'None' and str(dob) != 'nan':
                try:
                    dob_date = pd.to_datetime(dob)
                    if dob_date.month == today.month and dob_date.day == today.day:
                        emp_name = f"{emp['first_name']} {emp['last_name']}".strip()
                        dept = emp.get('department', '')
                        birthday_names.append(f"{emp_name} ({dept})")
                except:
                    pass
            
            # Check work anniversaries
            join_date = emp.get('join_date')
            if join_date and str(join_date) != 'None' and str(join_date) != 'nan':
                try:
                    jd = pd.to_datetime(join_date)
                    years = today.year - jd.year
                    if jd.month == today.month and jd.day == today.day and years > 0:
                        emp_name = f"{emp['first_name']} {emp['last_name']}".strip()
                        dept = emp.get('department', '')
                        anniversary_names.append(f"{emp_name} ({dept}) — {years} year{'s' if years > 1 else ''}")
                except:
                    pass
        
        if birthday_names or anniversary_names:
            print(f"🎉 Celebrations found!")
            print(f"   Birthdays: {len(birthday_names)}")
            print(f"   Anniversaries: {len(anniversary_names)}")
            
            # Build email subject
            if birthday_names and anniversary_names:
                subject = "🎉 Today's Celebrations at Churchgate Group!"
            elif birthday_names:
                subject = "🎂 Birthday Celebrations at Churchgate Group!"
            else:
                subject = "⭐ Work Anniversaries at Churchgate Group!"
            
            # Build email body
            body = "Dear Team,\n\n"
            body += "Today we celebrate our amazing colleagues:\n\n"
            
            if birthday_names:
                body += "🎂 BIRTHDAYS:\n"
                for name in birthday_names:
                    body += f"  • {name}\n"
                body += "\n"
            
            if anniversary_names:
                body += "⭐ WORK ANNIVERSARIES:\n"
                for name in anniversary_names:
                    body += f"  • {name}\n"
                body += "\n"
            
            body += "Please join us in wishing them a wonderful day!\n\n"
            body += "Warm regards,\n"
            body += "Churchgate Group HR"
            
            # Send to ALL employees
            email_service = EmailService()
            sent_count = 0
            failed_count = 0
            
            for _, emp in employees.iterrows():
                email_addr = emp.get('email', '')
                if email_addr and '@' in str(email_addr):
                    try:
                        email_service.send_email(email_addr, subject, body)
                        sent_count += 1
                    except Exception as e:
                        failed_count += 1
                        print(f"   ❌ Failed for {email_addr}: {str(e)}")
            
            print(f"✅ Celebration emails sent to {sent_count} employees")
            if failed_count > 0:
                print(f"   ⚠️ {failed_count} emails failed")
            
            # Log to database
            try:
                db._post("user_engagement", {
                    "user_name": "System",
                    "user_email": "system@churchgate.com",
                    "department": "HR",
                    "module": "Auto Celebrations",
                    "action": "celebration_emails_sent",
                    "timestamp": today.strftime('%Y-%m-%d %H:%M:%S'),
                    "session_id": "auto_cron",
                    "device": "server"
                })
            except:
                pass
            
        else:
            print("ℹ️ No celebrations today")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_and_send_celebrations()
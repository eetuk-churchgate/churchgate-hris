"""
Churchgate Group HRIS - Email Service
Enterprise Email Notification System (SendGrid API)
"""

import os
import streamlit as st
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent, PlainTextContent
from datetime import datetime

class EmailService:
    def __init__(self):
        # Get SendGrid API key - Railway environment first
        self.sendgrid_api_key = os.environ.get("SENDGRID_API_KEY", "")
        if not self.sendgrid_api_key:
            try:
                self.sendgrid_api_key = st.secrets.get("SENDGRID_API_KEY", "")
            except:
                pass
        
        # Sender details - Railway environment first
        self.sender_email = os.environ.get("SMTP_SENDER_EMAIL", os.environ.get("SMTP_EMAIL", ""))
        if not self.sender_email:
            try:
                self.sender_email = st.secrets.get("SMTP_EMAIL", "eetuk@churchgate.com")
            except:
                self.sender_email = "eetuk@churchgate.com"
        
        self.sender_name = "Churchgate Group HRIS"    
    def _create_html_email(self, subject, body_content):
        """Create professional HTML email with Churchgate gold branding"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #faf9f6; margin: 0; padding: 0; }}
                .email-container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid #e8dcc8; }}
                .email-header {{ background: linear-gradient(135deg, #1a1a1a 0%, #2d2a1f 100%); padding: 30px 20px; text-align: center; border-bottom: 3px solid #D4AF37; }}
                .email-header h1 {{ color: #F5E6CC; margin: 0; font-size: 24px; }}
                .email-header p {{ color: #D4AF37; margin: 8px 0 0 0; font-size: 14px; }}
                .email-body {{ padding: 30px 25px; color: #3d3020; background: #faf9f6; }}
                .email-body h2 {{ color: #1a1a1a; border-bottom: 2px solid #D4AF37; padding-bottom: 5px; display: inline-block; }}
                .btn {{ display: inline-block; background: linear-gradient(135deg, #CC0000, #aa0000); color: white; padding: 14px 35px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px; margin: 15px 0; }}
                .btn:hover {{ background: linear-gradient(135deg, #D4AF37, #C9A84C); }}
                .info-box {{ background: white; padding: 18px; border-radius: 8px; margin: 18px 0; border-left: 4px solid #D4AF37; border: 1px solid #e8dcc8; }}
                .email-footer {{ background: linear-gradient(135deg, #1a1a1a, #2d2a1f); padding: 15px; text-align: center; border-top: 2px solid #D4AF37; }}
                .email-footer p {{ color: #D4AF37; font-size: 11px; margin: 0; }}
                p {{ color: #5c4a2a; }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    <img src="https://raw.githubusercontent.com/eetuk-churchgate/churchgate-hris/main/churchgate_logo.png" alt="Churchgate Group" style="max-width: 180px; margin-bottom: 10px;">
                    <h1>Churchgate Group</h1>
                    <p>HRIS Portal</p>
                </div>
                <div class="email-body">
                    {body_content}
                </div>
                <div class="email-footer">
                    <p>© {datetime.now().year} Churchgate Group. All rights reserved | hris@churchgate.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def send_email(self, to_email, subject, body, template_type='general'):
        """Send email using SendGrid API"""
        try:
            if not self.sendgrid_api_key:
                print(f"⚠️ SENDGRID_API_KEY not set! Email to {to_email} not sent.")
                return False, "SENDGRID_API_KEY not configured"
            
            html_body = self._create_html_email(subject, body)
            
            message = Mail(
                from_email=From(self.sender_email, self.sender_name),
                to_emails=To(to_email),
                subject=Subject(subject),
                plain_text_content=PlainTextContent(body),
                html_content=HtmlContent(html_body)
            )
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            print(f"✅ Email sent to {to_email}: {subject} | Status: {response.status_code}")
            return True, f"Email sent to {to_email}"
            
        except Exception as e:
            print(f"❌ Email failed for {to_email}: {str(e)}")
            return False, str(e)
    
    def send_welcome_email(self, employee_name, employee_email, login_url="https://hris.churchgate.com"):
        subject = f"🎉 Welcome to Churchgate Group, {employee_name}!"
        body = f"""
        <h2>Dear {employee_name},</h2>
        <p style="font-size: 15px; line-height: 1.6;">Welcome aboard! Your <strong>Churchgate Group HRIS Portal</strong> account is now active.</p>
        <p style="font-size: 15px; line-height: 1.6;">This is your personal hub for everything HR — profile, performance, training, and team connection.</p>
        <div class="info-box">
            <p style="margin: 0;"><strong>🔗 Login Here:</strong><br><a href="{login_url}" style="color: #CC0000; font-size: 16px;">{login_url}</a></p>
            <p style="margin: 10px 0 0 0;"><strong>📧 Email:</strong> {employee_email}</p>
            <p style="margin: 5px 0 0 0; font-size: 12px; color: #CC0000;">🔒 For security, use the "Forgot Password" link on the login page to set your password.</p>
        </div>
        <a href="{login_url}" class="btn">🚀 Log In Now</a>
        <p style="margin-top: 20px; font-size: 13px; color: #888;">We're excited to have you on board! — Churchgate Group HR Team</p>
        """
        return self.send_email(employee_email, subject, body)

    def send_birthday_alert(self, employee_name, employee_email, birth_date):
        subject = f"🎂 Happy Birthday, {employee_name}!"
        body = f"""
        <h2>🎉 Happy Birthday, {employee_name}!</h2>
        <p>Wishing you a wonderful birthday filled with joy and celebration!</p>
        <p>From all of us at Churchgate Group, we appreciate your dedication and contributions.</p>
        """
        return self.send_email(employee_email, subject, body)

    def send_training_reminder(self, employee_name, employee_email, course_name, date):
        subject = f"📚 Training Reminder: {course_name}"
        body = f"""
        <h2>📚 Upcoming Training</h2>
        <div class="info-box">
            <p><strong>Course:</strong> {course_name}</p>
            <p><strong>Date:</strong> {date}</p>
        </div>
        <p>Dear {employee_name}, this is a reminder for your upcoming training session.</p>
        """
        return self.send_email(employee_email, subject, body)
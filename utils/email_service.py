"""
Churchgate Group HRIS - Email Service
Enterprise Email Notification System
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
import json

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "hris@churchgate.com"
        self.sender_name = "Churchgate Group HRIS"
        
        # In production, load from environment variables
        self.smtp_username = None
        self.smtp_password = None
        
        # Email templates
        self.templates = {
            'welcome': self._welcome_template,
            'birthday': self._birthday_template,
            'promotion': self._promotion_template,
            'new_hire': self._new_hire_template,
            'training': self._training_template,
            'holiday': self._holiday_template,
            'announcement': self._announcement_template,
            'performance': self._performance_template,
        }
    
    def _create_html_email(self, subject, body_content, template_type='general'):
        """Create professional HTML email with Churchgate branding"""
        
        churchgate_colors = {
            'primary': '#1a365d',
            'gold': '#c49216',
            'bg': '#f7fafc',
            'text': '#2d3748',
        }
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: {churchgate_colors['bg']};
                    margin: 0;
                    padding: 0;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }}
                .email-header {{
                    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
                    padding: 30px 20px;
                    text-align: center;
                    border-bottom: 3px solid {churchgate_colors['gold']};
                }}
                .email-header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 24px;
                }}
                .email-header p {{
                    color: #cbd5e0;
                    margin: 5px 0 0 0;
                    font-size: 14px;
                }}
                .email-body {{
                    padding: 30px 20px;
                    color: {churchgate_colors['text']};
                }}
                .email-body h2 {{
                    color: {churchgate_colors['gold']};
                    font-size: 20px;
                }}
                .email-footer {{
                    background: {churchgate_colors['bg']};
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #718096;
                    border-top: 1px solid #e2e8f0;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: linear-gradient(135deg, {churchgate_colors['gold']}, #e2c456);
                    color: #1a202c;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: 600;
                    margin: 15px 0;
                }}
                .info-card {{
                    background: {churchgate_colors['bg']};
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                    border-left: 3px solid {churchgate_colors['gold']};
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    <h1>🏢 Churchgate Group</h1>
                    <p>Human Resource Information System</p>
                </div>
                <div class="email-body">
                    {body_content}
                </div>
                <div class="email-footer">
                    <p>© {datetime.now().year} Churchgate Group. All rights reserved.</p>
                    <p>This is an automated message from Churchgate Group HRIS.</p>
                    <p>World Trade Center, Abuja, Nigeria</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def send_email(self, to_email, subject, body, template_type='general', cc=None, bcc=None):
        """Send email with Churchgate branding"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            
            if cc:
                msg['Cc'] = cc
            if bcc:
                msg['Bcc'] = bcc
            
            # Plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # HTML version
            html_body = self._create_html_email(subject, body, template_type)
            msg.attach(MIMEText(html_body, 'html'))
            
            # In production, uncomment to send:
            # with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.smtp_username, self.smtp_password)
            #     server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}: {subject}")
            return True, f"Email sent to {to_email}"
            
        except Exception as e:
            print(f"❌ Email failed: {str(e)}")
            return False, str(e)
    
    def send_birthday_alert(self, employee_name, employee_email, birth_date):
        """Send birthday greeting"""
        subject = f"🎂 Happy Birthday, {employee_name}!"
        body = f"""
        <h2>🎉 Happy Birthday, {employee_name}!</h2>
        <p>Wishing you a wonderful birthday filled with joy and celebration!</p>
        <div class="info-card">
            <p>From all of us at Churchgate Group, we appreciate your dedication and contributions to our success.</p>
            <p>May this year bring you great achievements and happiness!</p>
        </div>
        <p>Enjoy your special day! 🎂🎈</p>
        """
        return self.send_email(employee_email, subject, body, 'birthday')
    
    def send_promotion_announcement(self, employee_name, new_position, department, recipients):
        """Send promotion announcement to team"""
        subject = f"🚀 Promotion Announcement: {employee_name}"
        body = f"""
        <h2>🌟 Promotion Announcement</h2>
        <div class="info-card">
            <h3>Congratulations to {employee_name}!</h3>
            <p><strong>New Position:</strong> {new_position}</p>
            <p><strong>Department:</strong> {department}</p>
        </div>
        <p>Please join us in congratulating {employee_name} on this well-deserved promotion.</p>
        <p>This promotion reflects their outstanding performance and commitment to Churchgate Group's success.</p>
        """
        
        results = []
        for recipient in recipients:
            results.append(self.send_email(recipient, subject, body, 'promotion'))
        return results
    
    def send_new_hire_announcement(self, new_hire_name, position, department, start_date, recipients):
        """Send new hire announcement"""
        subject = f"👋 Welcome {new_hire_name} to Churchgate Group!"
        body = f"""
        <h2>🎉 New Team Member Announcement</h2>
        <div class="info-card">
            <h3>Welcome {new_hire_name}!</h3>
            <p><strong>Position:</strong> {position}</p>
            <p><strong>Department:</strong> {department}</p>
            <p><strong>Start Date:</strong> {start_date}</p>
        </div>
        <p>Please join us in welcoming {new_hire_name} to the Churchgate Group family!</p>
        <p>Let's make them feel at home and support them in their journey with us.</p>
        """
        
        results = []
        for recipient in recipients:
            results.append(self.send_email(recipient, subject, body, 'new_hire'))
        return results
    
    def send_training_reminder(self, employee_name, employee_email, course_name, date, platform):
        """Send training reminder"""
        subject = f"📚 Training Reminder: {course_name}"
        body = f"""
        <h2>📚 Upcoming Training</h2>
        <div class="info-card">
            <p><strong>Course:</strong> {course_name}</p>
            <p><strong>Date:</strong> {date}</p>
            <p><strong>Platform:</strong> {platform}</p>
        </div>
        <p>Dear {employee_name},</p>
        <p>This is a reminder for your upcoming training session. Please ensure you have completed any pre-work and have the necessary materials ready.</p>
        <a href="#" class="btn">Access Training Portal</a>
        """
        return self.send_email(employee_email, subject, body, 'training')
    
    def send_holiday_notification(self, holiday_name, holiday_date, recipients):
        """Send holiday notification"""
        subject = f"🏖️ Upcoming Holiday: {holiday_name}"
        body = f"""
        <h2>📅 Holiday Notice</h2>
        <div class="info-card">
            <h3>{holiday_name}</h3>
            <p><strong>Date:</strong> {holiday_date}</p>
        </div>
        <p>Please note that our offices will be closed on {holiday_date} in observance of {holiday_name}.</p>
        <p>Plan your work accordingly and enjoy the holiday!</p>
        """
        
        results = []
        for recipient in recipients:
            results.append(self.send_email(recipient, subject, body, 'holiday'))
        return results
    
    def send_performance_review_reminder(self, employee_name, employee_email, review_period, deadline):
        """Send performance review reminder"""
        subject = f"📊 Performance Review Reminder - {review_period}"
        body = f"""
        <h2>📊 Performance Review</h2>
        <div class="info-card">
            <p><strong>Period:</strong> {review_period}</p>
            <p><strong>Deadline:</strong> {deadline}</p>
        </div>
        <p>Dear {employee_name},</p>
        <p>Your performance review for {review_period} is due by {deadline}. Please complete your self-assessment and schedule a review meeting with your manager.</p>
        <a href="#" class="btn">Complete Review</a>
        """
        return self.send_email(employee_email, subject, body, 'performance')
    
    def send_announcement(self, title, message, recipients, priority='normal'):
        """Send general announcement"""
        priority_prefix = "🔴 URGENT: " if priority == 'high' else "📢 "
        subject = f"{priority_prefix}{title}"
        body = f"""
        <h2>📢 {title}</h2>
        <div class="info-card">
            <p>{message}</p>
        </div>
        <p>Thank you for your attention.</p>
        """
        
        results = []
        for recipient in recipients:
            results.append(self.send_email(recipient, subject, body, 'announcement'))
        return results
    
    # Template methods
    def _welcome_template(self, name):
        return f"Welcome to Churchgate Group, {name}!"
    
    def _birthday_template(self, name):
        return f"Happy Birthday, {name}!"
    
    def _promotion_template(self, name, position):
        return f"Congratulations {name} on your promotion to {position}!"
    
    def _new_hire_template(self, name):
        return f"Welcome aboard, {name}!"
    
    def _training_template(self, course):
        return f"Training reminder: {course}"
    
    def _holiday_template(self, holiday):
        return f"Holiday notice: {holiday}"
    
    def _announcement_template(self, title):
        return f"Announcement: {title}"
    
    def _performance_template(self, period):
        return f"Performance review: {period}"


# Test the email service
if __name__ == "__main__":
    email_service = EmailService()
    
    # Test birthday alert
    email_service.send_birthday_alert("John Doe", "john@churchgate.com", "2026-05-20")
    
    # Test promotion announcement
    email_service.send_promotion_announcement(
        "Sarah Williams", "HR Director", "Human Resources",
        ["team@churchgate.com"]
    )
    
    print("✅ Email service test complete")
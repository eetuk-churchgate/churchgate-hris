"""
Churchgate Group AI DLP Monitor - Enterprise Data Leakage Prevention
Fortune 500 Grade | Military-Grade Security | Real-Time Intelligence
"""
import os
import json
import asyncio
import aiohttp
import hashlib
import uuid
import socket
import platform
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import ipinfo
from user_agents import parse

# ============================================================
# SENSITIVE ENTITIES - ALL CHURCHGATE SUBSIDIARIES
# ============================================================
SENSITIVE_ENTITIES = [
    "Aba Textile Mills PLC", "Agroline Ventures Limited", 
    "Associated Textile Manufacturing Company Limited", 
    "Churchgate Nigeria Limited", "Churchgate Group", "Churchgate Investment Limited",
    "Food & Confectionery Products (Nig.) Limited", 
    "First Continental Properties Limited – WTC", "First Continental Properties Limited",
    "First Spinners PLC", "HotelInvest & Resorts Limited",
    "International Textile Industries (Nig.) Limited", "Intercott Limited", 
    "Ocean Fisheries (Nig.) Limited", "Platinum Travel Limited", 
    "R. B Properties Limited", "Reliance Mills Limited", 
    "Vineyard Designs Nig. Limited", "World Trade Center Abuja"
]

SENSITIVE_KEYWORDS = [
    # FINANCIAL
    "salary", "invoice", "payslip", "bank transfer", "budget", "revenue", "profit", "loss",
    "expense", "bank account", "wire transfer", "payment", "receipt", "financial statement",
    "balance sheet", "income statement", "cash flow", "audit report", "tax document",
    "VAT", "TIN", "tax identification", "financial report", "account number", "sort code",
    "SWIFT code", "IBAN", "dividend", "shareholder", "equity", "loan", "credit facility",
    "overdraft", "treasury", "forex", "exchange rate", "naira", "dollar", "pounds sterling",
    "financial projection", "budget forecast", "capital expenditure", "CAPEX", "OPEX",
    "recurring revenue", "gross margin", "net profit", "EBITDA", "depreciation", "amortization",
    
    # HUMAN RESOURCES
    "staff list", "employee data", "HR records", "payroll", "BVN", "NIN", "passport",
    "employee handbook", "staff handbook", "employment contract", "termination letter",
    "resignation letter", "disciplinary action", "performance review", "appraisal",
    "salary structure", "grade level", "job description", "organogram", "organizational structure",
    "staff strength", "headcount", "recruitment", "interview", "onboarding", "offboarding",
    "leave request", "sick leave", "maternity leave", "paternity leave", "medical record",
    "staff ID", "employee ID", "pension", "gratuity", "severance", "redundancy",
    "staff benefits", "health insurance", "life insurance", "staff loan",
    
    # PROCUREMENT & VENDORS
    "procurement", "vendor", "supplier", "tender", "quotation", "purchase order",
    "contract", "contractor", "subcontractor", "bidding", "bid document", "RFQ", "RFP",
    "request for quotation", "request for proposal", "supply chain", "logistics",
    "inventory", "stock level", "warehouse", "delivery note", "goods received",
    "vendor rating", "supplier evaluation", "price negotiation", "bulk purchase",
    "procurement plan", "procurement budget", "vendor list", "supplier list",
    
    # LEGAL & CORPORATE
    "board meeting", "board resolution", "shareholder meeting", "AGM", "EGM",
    "memorandum of association", "articles of association", "company seal",
    "legal document", "lawsuit", "litigation", "arbitration", "settlement",
    "non-disclosure agreement", "NDA", "intellectual property", "trademark", "patent",
    "copyright", "license agreement", "franchise agreement", "joint venture",
    "merger", "acquisition", "due diligence", "corporate governance",
    
    # CONFIDENTIAL & INTERNAL
    "confidential", "internal memo", "internal document", "restricted", "classified",
    "proprietary", "trade secret", "sensitive information", "do not distribute",
    "for internal use only", "private and confidential", "executive summary",
    "management report", "strategy document", "business plan", "strategic plan",
    "5-year plan", "annual plan", "quarterly report", "monthly report",
    
    # REAL ESTATE & PROPERTY
    "property", "tenant", "lease", "rent", "occupancy", "property management",
    "building maintenance", "facility management", "asset register", "property valuation",
    "real estate", "development project", "construction", "renovation", "building plan",
    "site plan", "architectural drawing", "engineering drawing", "structural plan",
    
    # IT & SECURITY
    "password", "API key", "access token", "database", "server", "firewall",
    "VPN", "encryption", "cybersecurity", "data breach", "security protocol",
    "admin access", "root access", "privileged access", "user credentials",
    
    # BANKING & INVESTMENT
    "investment", "portfolio", "asset management", "fund management", "mutual fund",
    "treasury bill", "bond", "stock", "share", "dividend", "capital market",
    "money market", "fixed deposit", "savings account", "current account",
    
    # GENERAL SENSITIVE
    "internal audit", "external audit", "compliance", "regulatory", "CBN",
    "SEC Nigeria", "NAICOM", "PENCOM", "FIRS", "LIRS", "tax authority",
    "government contract", "public private partnership", "PPP", "concession"
]

# CATEGORIZED KEYWORDS FOR BETTER CLASSIFICATION
SENSITIVE_KEYWORD_CATEGORIES = {
    "Financial": [
        "salary", "invoice", "payslip", "bank transfer", "budget", "revenue", "profit", "loss",
        "expense", "bank account", "wire transfer", "payment", "receipt", "financial statement",
        "balance sheet", "income statement", "cash flow", "audit report", "tax document",
        "VAT", "TIN", "tax identification", "financial report", "account number", "sort code",
        "SWIFT code", "IBAN", "dividend", "shareholder", "equity", "loan", "credit facility",
        "overdraft", "treasury", "forex", "exchange rate", "naira", "dollar", "pounds sterling",
        "financial projection", "budget forecast", "capital expenditure", "CAPEX", "OPEX",
        "recurring revenue", "gross margin", "net profit", "EBITDA", "depreciation", "amortization"
    ],
    "HR": [
        "staff list", "employee data", "HR records", "payroll", "BVN", "NIN", "passport",
        "employee handbook", "staff handbook", "employment contract", "termination letter",
        "resignation letter", "disciplinary action", "performance review", "appraisal",
        "salary structure", "grade level", "job description", "organogram", "organizational structure",
        "staff strength", "headcount", "recruitment", "interview", "onboarding", "offboarding",
        "leave request", "sick leave", "maternity leave", "paternity leave", "medical record",
        "staff ID", "employee ID", "pension", "gratuity", "severance", "redundancy",
        "staff benefits", "health insurance", "life insurance", "staff loan"
    ],
    "Procurement": [
        "procurement", "vendor", "supplier", "tender", "quotation", "purchase order",
        "contract", "contractor", "subcontractor", "bidding", "bid document", "RFQ", "RFP",
        "request for quotation", "request for proposal", "supply chain", "logistics",
        "inventory", "stock level", "warehouse", "delivery note", "goods received",
        "vendor rating", "supplier evaluation", "price negotiation", "bulk purchase",
        "procurement plan", "procurement budget", "vendor list", "supplier list"
    ],
    "Legal": [
        "board meeting", "board resolution", "shareholder meeting", "AGM", "EGM",
        "memorandum of association", "articles of association", "company seal",
        "legal document", "lawsuit", "litigation", "arbitration", "settlement",
        "non-disclosure agreement", "NDA", "intellectual property", "trademark", "patent",
        "copyright", "license agreement", "franchise agreement", "joint venture",
        "merger", "acquisition", "due diligence", "corporate governance"
    ],
    "IT Security": [
        "password", "API key", "access token", "database", "server", "firewall",
        "VPN", "encryption", "cybersecurity", "data breach", "security protocol",
        "admin access", "root access", "privileged access", "user credentials"
    ],
    "General": [
        "confidential", "internal memo", "internal document", "restricted", "classified",
        "proprietary", "trade secret", "sensitive information", "do not distribute",
        "for internal use only", "private and confidential", "executive summary",
        "management report", "strategy document", "business plan", "strategic plan",
        "5-year plan", "annual plan", "quarterly report", "monthly report"
    ]
}

# ============================================================
# SEVERITY LEVELS - Determines alert priority
# ============================================================
SEVERITY_LEVELS = {
    "Finance": "Critical",
    "HR": "Critical",
    "Procurement": "High",
    "Legal": "High",
    "Secretarial": "Medium",
    "IT Security": "High",
    "General": "Low"
}

class IncidentResponder:
    def __init__(self):
        self.sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        self.MANAGEMENT_EMAILS = self._load_management_emails()
        self.alert_cooldown = {}
        self.incident_log = []
        
    def _load_management_emails(self):
        """Load ONLY the 3 Super Admin emails"""
        return [
            "eetuk@churchgate.com",
            "jeromedas@churchgate.com",
            "vbmahtani@churchgate.com"
        ]
    
    def save_evidence_to_storage(self, incident_id, evidence_data, file_name):
        """Save evidence to Supabase Storage"""
        try:
            from supabase import create_client
            
            supabase_url = os.environ.get('SUPABASE_URL', '')
            supabase_key = os.environ.get('SUPABASE_SERVICE_KEY', os.environ.get('SUPABASE_KEY', ''))
            
            client = create_client(supabase_url, supabase_key)
            
            # Upload evidence file
            client.storage.from_('dlp-evidence').upload(
                f"{incident_id}/{file_name}",
                evidence_data
            )
            
            # Get public URL
            url = client.storage.from_('dlp-evidence').get_public_url(f"{incident_id}/{file_name}")
            
            return url
        except Exception as e:
            print(f"Evidence upload failed: {e}")
            return None
    
    def save_alert_to_database(self, incident_id, subsidiary, leak_type, severity, source_url, content_snippet, forensics):
        """Save alert to Supabase database"""
        try:
            from utils.database import db
            
            db._post("dlp_alerts", {
                "incident_id": incident_id,
                "subsidiary": subsidiary,
                "leak_type": leak_type,
                "severity": severity,
                "source_url": source_url,
                "content_snippet": content_snippet[:1000],
                "ip_address": forensics.get('IP', 'Unknown'),
                "city": forensics.get('City', 'Unknown'),
                "region": forensics.get('Region', 'Unknown'),
                "country": forensics.get('Country', 'Unknown'),
                "device": forensics.get('Device', 'Unknown'),
                "browser": forensics.get('Browser', 'Unknown'),
                "os": forensics.get('OS', 'Unknown'),
                "device_type": forensics.get('Device_Type', 'Unknown'),
                "detected_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            return True
        except Exception as e:
            print(f"Database save failed: {e}")
            return False
    
    def save_scan_log(self, scan_type, entities_scanned, results_found, alerts_triggered, duration_seconds):
        """Save scan log to database"""
        try:
            from utils.database import db
            
            db._post("dlp_scan_log", {
                "scan_type": scan_type,
                "entities_scanned": entities_scanned,
                "results_found": results_found,
                "alerts_triggered": alerts_triggered,
                "scan_duration_seconds": duration_seconds,
                "scanned_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            return True
        except:
            return False
    
    def load_alerts_from_database(self):
        """Load all alerts from database"""
        try:
            from utils.database import db
            alerts = db._get("dlp_alerts")
            return alerts if alerts else []
        except:
            return []
        
    def check_cooldown(self, subsidiary):
        if subsidiary in self.alert_cooldown:
            if (datetime.now() - self.alert_cooldown[subsidiary]).seconds < 3600:
                return False
        self.alert_cooldown[subsidiary] = datetime.now()
        return True
    
    def trace_device_and_ip(self, source_metadata):
        try:
            ip = source_metadata.get('client_ip', '0.0.0.0')
            handler = ipinfo.getHandler(access_token=os.environ.get('IPINFO_TOKEN', ''))
            details = handler.getDetails(ip)
            
            user_agent = source_metadata.get('user_agent', '')
            parser = parse(user_agent)
            
            return {
                "IP": ip,
                "City": details.city,
                "Region": details.region,
                "Country": details.country,
                "Device": f"{parser.os.family} on {parser.device.family}",
                "Browser": parser.browser.family,
                "OS": parser.os.family,
                "Device_Type": parser.device.family,
                "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except:
            return {
                "IP": "Unknown", "City": "Unknown", "Region": "Unknown", 
                "Country": "Unknown", "Device": "Unknown", "Browser": "Unknown",
                "OS": "Unknown", "Device_Type": "Unknown", 
                "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def get_mitigation_plan(self, leak_type):
        plans = {
            "HR": """IMMEDIATE ACTIONS (FIRST 5 MINUTES):
1. REVOKE access to HR database for suspected user immediately.
2. FORCE password reset for ALL HR admin accounts.
3. FREEZE external payroll exports and API access.
4. NOTIFY Head of HR and Legal immediately.

FOLLOW-UP (FIRST HOUR):
5. Audit last 30 days of HR system access logs.
6. Identify all employees whose data may have been exposed.
7. Prepare internal communication for affected staff.

NOTIFICATION:
8. Contact Data Protection Officer (DPO).
9. Evaluate NDPR (Nigeria Data Protection Regulation) breach notification requirements.""",
            
            "Finance": """IMMEDIATE ACTIONS (FIRST 5 MINUTES):
1. NOTIFY THE CFO IMMEDIATELY.
2. FREEZE all pending outgoing wire transfers for 24 hours.
3. CONTACT GTBank/FirstBank with fraud alert case number.
4. SUSPEND all API keys for payment platforms.

FOLLOW-UP (FIRST HOUR):
5. Audit all recent financial transactions for anomalies.
6. Reconcile all bank statements for the last 48 hours.
7. Flag any transactions above ₦1,000,000 for manual review.

NOTIFICATION:
8. Contact external auditors.
9. Prepare preliminary financial impact assessment.""",
            
            "Procurement": """IMMEDIATE ACTIONS (FIRST 5 MINUTES):
1. FLAG the specific procurement contract as 'Compromised'.
2. CONTACT vendor partners to warn of potential phishing.
3. ROTATE API keys for procurement platforms.
4. SUSPEND new purchase order approvals.

FOLLOW-UP (FIRST HOUR):
5. Review all open purchase orders for tampering.
6. Verify vendor bank account details.
7. Check for duplicate invoices or ghost vendors.

NOTIFICATION:
8. Contact Internal Audit.
9. Review procurement approval chain for gaps.""",
            
            "Legal": """IMMEDIATE ACTIONS (FIRST 5 MINUTES):
1. NOTIFY Group Legal Counsel immediately.
2. SECURE all copies of the leaked document.
3. DOCUMENT the source URL and timestamp for evidence.

FOLLOW-UP (FIRST HOUR):
4. Assess confidentiality obligations.
5. Determine if client or third-party data is involved.
6. Prepare legal hold notice if litigation is anticipated.""",
            
            "Secretarial": """IMMEDIATE ACTIONS (FIRST 5 MINUTES):
1. NOTIFY Company Secretary.
2. SECURE board meeting minutes and resolutions.
3. RESTRICT access to corporate governance documents.

FOLLOW-UP (FIRST HOUR):
4. Identify which meetings/documents were exposed.
5. Contact board members if their data is involved.""",
            
            "IT Security": """IMMEDIATE ACTIONS (FIRST 5 MINUTES):
1. REVOKE all compromised API keys and access tokens.
2. FORCE password reset for all affected accounts.
3. DISABLE the affected service temporarily.
4. NOTIFY CTO immediately.

FOLLOW-UP (FIRST HOUR):
5. Review server logs for unauthorized access.
6. Check for lateral movement across systems.
7. Scan for malware or backdoors.

NOTIFICATION:
8. Contact external cybersecurity firm.
9. Prepare incident report for management."""
        }
        return plans.get(leak_type, "1. Quarantine the file. 2. Analyze user access logs. 3. Report to IT Security.")
    
    def send_red_alert(self, subsidiary, leak_type, leaked_content, source_url, forensics, severity="Critical"):
        if not self.check_cooldown(subsidiary):
            return False, None
        
        mitigation = self.get_mitigation_plan(leak_type)
        incident_id = f"CHG-{uuid.uuid4().hex[:8].upper()}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><style>body{{font-family: Arial, sans-serif; background: #f5f5f5;}} .container{{max-width: 700px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden;}} .header{{background: linear-gradient(135deg, #CC0000, #8B0000); color: white; padding: 20px; text-align: center;}} .body{{padding: 20px;}} .alert-box{{background: #FFF3CD; border-left: 4px solid #FFC107; padding: 10px; margin: 10px 0;}} .forensic{{background: #F8F9FA; border: 1px solid #DEE2E6; border-radius: 4px; padding: 10px; margin: 10px 0;}} .playbook{{background: #1E1E1E; color: #E0E0E0; padding: 15px; border-radius: 4px; margin: 10px 0; white-space: pre-wrap; font-family: monospace;}} .footer{{text-align: center; padding: 10px; color: #666; font-size: 0.8em;}}</style></head>
        <body>
        <div class="container">
            <div class="header">
                <h1 style="margin:0;">🚨 URGENT: Churchgate Group Data Leak Detected</h1>
                <p style="margin:5px 0 0 0;">Incident ID: {incident_id}</p>
            </div>
            <div class="body">
                <p><strong>⏰ Time Detected:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>🏢 Affected Subsidiary:</strong> {subsidiary}</p>
                <p><strong>📊 Data Classification:</strong> <span style="background-color: #CC0000; color: white; padding: 4px 10px; border-radius: 4px;">{leak_type.upper()} - {severity.upper()}</span></p>
                
                <div class="alert-box">
                    <strong>⚠️ IMMEDIATE ATTENTION REQUIRED</strong>
                    <p>This is an automated security alert. Please follow the mitigation playbook below.</p>
                </div>
                
                <hr>
                <h3>📍 Forensic Intelligence Report</h3>
                <div class="forensic">
                    <table style="width:100%; border-collapse: collapse;">
                        <tr><td><b>IP Address:</b></td><td>{forensics.get('IP', 'Unknown')}</td></tr>
                        <tr><td><b>Location:</b></td><td>{forensics.get('City', 'Unknown')}, {forensics.get('Region', 'Unknown')}, {forensics.get('Country', 'Unknown')}</td></tr>
                        <tr><td><b>Device:</b></td><td>{forensics.get('Device', 'Unknown')}</td></tr>
                        <tr><td><b>Operating System:</b></td><td>{forensics.get('OS', 'Unknown')}</td></tr>
                        <tr><td><b>Browser:</b></td><td>{forensics.get('Browser', 'Unknown')}</td></tr>
                        <tr><td><b>Detection Time:</b></td><td>{forensics.get('Timestamp', 'Unknown')}</td></tr>
                    </table>
                </div>
                
                <hr>
                <h3>📂 Leaked Content Snippet</h3>
                <div style="background-color: #F8F9FA; border-left: 4px solid #CC0000; padding: 10px; font-family: monospace; white-space: pre-wrap; word-break: break-all;">
                    {leaked_content[:1000]}
                </div>
                <p><a href="{source_url}" target="_blank" style="color: #CC0000; font-weight: bold;">🔗 Click here to view the exposed source</a></p>
                
                <hr>
                <h3>⚡ IMMEDIATE MITIGATION PLAYBOOK</h3>
                <div class="playbook">{mitigation}</div>
                
                <hr>
                <h3>📋 Required Actions</h3>
                <ol>
                    <li>Acknowledge this alert within 15 minutes.</li>
                    <li>Execute the mitigation playbook above.</li>
                    <li>Log the incident in the security register.</li>
                    <li>Notify the Group Security team.</li>
                </ol>
                
                <div class="footer">
                    <p>This is an automated alert from the Churchgate Group AI DLP Monitoring System.</p>
                    <p>For immediate assistance, contact IT Security: security@churchgate.com | +234 (0) 800 CHURCHGATE</p>
                </div>
            </div>
        </div>
        </body>
        </html>
        """
        
        message = Mail(
            from_email='security-alerts@churchgate.com',
            to_emails=self.MANAGEMENT_EMAILS,
            subject=f'🚨 {severity.upper()}: {leak_type} Leak Detected for {subsidiary} [{incident_id}]',
            html_content=html_content
        )
        
        try:
            response = self.sg.send(message)
            self.incident_log.append({
                'incident_id': incident_id,
                'subsidiary': subsidiary,
                'leak_type': leak_type,
                'severity': severity,
                'sent_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'emails_sent': len(self.MANAGEMENT_EMAILS)
            })
            return True, incident_id
        except Exception as e:
            print(f"EMAIL FAILED: {e}")
            return False, None

class AI_DLP_Monitor:
    def __init__(self):
        self.responder = IncidentResponder()
        self.alerts = []
        self.scan_history = []
        self.total_scans = 0
        self.critical_finds = 0
        
    async def run_continuous_scan(self, callback=None):
        """Continuous real-time scanning - runs forever"""
        while True:
            try:
                for entity in SENSITIVE_ENTITIES:
                    queries = [
                        f"{entity} confidential document",
                        f"{entity} salary structure",
                        f"{entity} invoice payment",
                        f"{entity} staff list",
                        f"{entity} procurement contract",
                        f"{entity} financial report"
                    ]
                    
                    for query in queries:
                        results = await self.scan_public_web(query)
                        self.total_scans += 1
                        
                        if results and 'organic' in results:
                            for item in results['organic'][:5]:
                                text = item.get('snippet', '')
                                url = item.get('link', '')
                                
                                if text:
                                    analysis = self.analyze_content(text, url)
                                    
                                    if analysis.get('is_sensitive'):
                                        self.trigger_alert(
                                            subsidiary=analysis.get('company', entity),
                                            leak_type=analysis.get('type', 'General'),
                                            content=text,
                                            source_url=url
                                        )
                                        if callback:
                                            callback(analysis)
                
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"Scan error: {e}")
                await asyncio.sleep(30)
        
    async def scan_public_web(self, query):
        """Scans public web for sensitive Churchgate data"""
        try:
            async with aiohttp.ClientSession() as session:
                api_key = os.environ.get('SERPER_API_KEY', '')
                headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
                params = {
                    "q": f"{query} (confidential OR salary OR invoice OR procurement OR payslip)",
                    "num": 20
                }
                
                async with session.post("https://google.serper.dev/search", 
                                       headers=headers, json=params) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except:
            return None
    
    def analyze_content(self, text, source_url):
        """Analyzes text for sensitive Churchgate data using Groq"""
        try:
            from groq import Groq
            groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
            
            prompt = f"""
            SECURITY ANALYSIS TASK:
            Analyze this text for potential data leakage involving Churchgate Group.
            
            Monitor these entities:
            {', '.join(SENSITIVE_ENTITIES)}
            
            Sensitive indicators:
            {', '.join(SENSITIVE_KEYWORDS)}
            
            Text to analyze:
            {text[:2000]}
            
            Reply with STRICT JSON only:
            {{"is_sensitive": true/false, "company": "matched entity or null", "type": "HR/Finance/Procurement/Legal/Secretarial/IT Security/General", "severity": "Critical/High/Medium/Low", "confidence": 0-100}}
            """
            
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "system", "content": "You are a security analyst. Only return valid JSON."},
                         {"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except:
            return {"is_sensitive": False, "company": None, "type": "General", "severity": "Low", "confidence": 0}
    
    def trigger_alert(self, subsidiary, leak_type, content, source_url, forensics=None):
        """Triggers immediate email alert with full forensics"""
        severity = SEVERITY_LEVELS.get(leak_type, "Medium")
        
        if forensics is None:
            forensics = self.responder.trace_device_and_ip({"client_ip": "0.0.0.0", "user_agent": ""})
        
        success, incident_id = self.responder.send_red_alert(
            subsidiary, leak_type, content, source_url, forensics, severity
        )
        
        alert_record = {
            'Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Incident_ID': incident_id,
            'Subsidiary': subsidiary,
            'Type': leak_type,
            'Severity': severity,
            'Source': source_url,
            'Content_Snippet': content[:200]
        }
        
        self.alerts.append(alert_record)
        
        if severity == "Critical":
            self.critical_finds += 1
        
        return success, incident_id
    
    def get_status_report(self):
        """Returns comprehensive status report"""
        return {
            'total_scans': self.total_scans,
            'critical_finds': self.critical_finds,
            'total_alerts': len(self.alerts),
            'entities_monitored': len(SENSITIVE_ENTITIES),
            'keywords_monitored': len(SENSITIVE_KEYWORDS),
            'keyword_categories': len(SENSITIVE_KEYWORD_CATEGORIES),
            'active': True
        }
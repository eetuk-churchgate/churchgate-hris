"""
Churchgate Group AI DLP - 24/7 Background Monitoring Service
Runs independently of Streamlit | Military-Grade Continuous Scanning
"""
import os
import json
import asyncio
import aiohttp
import threading
import time
from datetime import datetime, timedelta
from utils.dlp_monitor import (
    SENSITIVE_ENTITIES, 
    SENSITIVE_KEYWORDS, 
    SENSITIVE_KEYWORD_CATEGORIES,
    SEVERITY_LEVELS,
    IncidentResponder, 
    AI_DLP_Monitor
)

class BackgroundMonitorService:
    """24/7 Continuous Background Monitoring Service"""
    
    def __init__(self):
        self.monitor = AI_DLP_Monitor()
        self.responder = IncidentResponder()
        self.is_running = False
        self.scan_thread = None
        self.alert_log = []
        self.last_scan_time = None
        self.scan_count = 0
        self.error_count = 0
        
    def start(self):
        """Start the background monitoring thread"""
        if self.is_running:
            return "Already running"
        
        self.is_running = True
        self.scan_thread = threading.Thread(target=self._run_scan_loop, daemon=True)
        self.scan_thread.start()
        return "Monitoring started"
    
    def stop(self):
        """Stop the background monitoring"""
        self.is_running = False
        return "Monitoring stopped"
    
    def _run_scan_loop(self):
        """Main 24/7 scanning loop"""
        while self.is_running:
            try:
                self._perform_full_scan()
                self.last_scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.scan_count += 1
                time.sleep(300)  # 5 minutes between full cycles
            except Exception as e:
                self.error_count += 1
                time.sleep(60)  # Wait 1 minute on error
    
    def _perform_full_scan(self):
        """Perform complete scan of all entities and keywords"""
        for entity in SENSITIVE_ENTITIES:
            for keyword_group in SENSITIVE_KEYWORD_CATEGORIES.values():
                for keyword in keyword_group[:10]:  # Top 10 keywords per category
                    query = f"{entity} {keyword}"
                    self._scan_and_analyze(query, entity)
    
    def _scan_and_analyze(self, query, entity):
        """Scan public web and analyze results"""
        try:
            # Use Serper API
            results = self._search_serper(query)
            
            if results and 'organic' in results:
                for item in results['organic'][:3]:
                    snippet = item.get('snippet', '')
                    url = item.get('link', '')
                    
                    if snippet:
                        analysis = self.monitor.analyze_content(snippet, url)
                        
                        if analysis.get('is_sensitive'):
                            self._trigger_immediate_alert(
                                entity, analysis, snippet, url
                            )
        except Exception as e:
            print(f"Scan error for {query}: {e}")
    
    def _search_serper(self, query):
        """Search using Serper API"""
        try:
            api_key = os.environ.get('SERPER_API_KEY', '')
            headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
            params = {
                "q": f"{query} (confidential OR salary OR invoice OR procurement)",
                "num": 10
            }
            
            import requests
            response = requests.post(
                "https://google.serper.dev/search",
                headers=headers,
                json=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def _trigger_immediate_alert(self, entity, analysis, content, url):
        """Trigger immediate email alert"""
        leak_type = analysis.get('type', 'General')
        severity = SEVERITY_LEVELS.get(leak_type, 'Medium')
        
        forensics = self.responder.trace_device_and_ip({
            'client_ip': '0.0.0.0',
            'user_agent': ''
        })
        
        success, incident_id = self.responder.send_red_alert(
            subsidiary=analysis.get('company', entity),
            leak_type=leak_type,
            leaked_content=content,
            source_url=url,
            forensics=forensics,
            severity=severity
        )
        
        if success:
            self.alert_log.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'incident_id': incident_id,
                'entity': analysis.get('company', entity),
                'type': leak_type,
                'severity': severity,
                'source': url
            })
    
    def get_status(self):
        """Get current monitoring status"""
        return {
            'is_running': self.is_running,
            'scan_count': self.scan_count,
            'error_count': self.error_count,
            'last_scan_time': self.last_scan_time,
            'total_alerts': len(self.alert_log),
            'alerts': self.alert_log[-20:]
        }

# Global singleton instance
background_monitor = BackgroundMonitorService()
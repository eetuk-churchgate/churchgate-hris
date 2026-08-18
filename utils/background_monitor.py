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

# ============================================================
# GLOBAL STATE - Thread-safe shared state
# ============================================================
SCAN_STATE = {
    'is_running': False,
    'scan_count': 0,
    'last_scan_time': None,
    'progress': 0,
    'current_entity': '',
    'current_category': '',
    'current_keyword': '',
    'entities_scanned': 0,
    'total_searches': 0,
    'searches_completed': 0,
    'alerts_found': 0,
    'alert_log': []
}

class BackgroundMonitorService:
    """24/7 Continuous Background Monitoring Service"""
    
    def __init__(self):
        global SCAN_STATE
        self.monitor = AI_DLP_Monitor()
        self.responder = IncidentResponder()
        self.scan_thread = None
        self.error_count = 0
        
        # Restore from global state
        self.is_running = SCAN_STATE['is_running']
        self.scan_count = SCAN_STATE['scan_count']
        self.last_scan_time = SCAN_STATE['last_scan_time']
        self.alert_log = SCAN_STATE['alert_log']
        self.current_progress = SCAN_STATE['progress']
        self.current_entity = SCAN_STATE['current_entity']
        self.current_category = SCAN_STATE['current_category']
        self.current_keyword = SCAN_STATE['current_keyword']
        self.entities_scanned = SCAN_STATE['entities_scanned']
        self.total_searches = SCAN_STATE['total_searches']
        self.searches_completed = SCAN_STATE['searches_completed']
        self.alerts_found_this_scan = SCAN_STATE['alerts_found']
        
    def _log_progress(self, message):
        """Print progress with timestamp"""
        print(f"[DLP {datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def start(self):
        """Start the background monitoring thread"""
        global SCAN_STATE
        
        if SCAN_STATE['is_running']:
            return "Already running"
        
        SCAN_STATE['is_running'] = True
        self.is_running = True
        
        self.scan_thread = threading.Thread(target=self._run_scan_loop, daemon=True)
        self.scan_thread.start()
        return "Monitoring started"
    
    def stop(self):
        """Stop the background monitoring"""
        global SCAN_STATE
        
        SCAN_STATE['is_running'] = False
        self.is_running = False
        
        return "Monitoring stopped"
    
    def _run_scan_loop(self):
        """Main 24/7 scanning loop"""
        global SCAN_STATE
        
        self._log_progress("========================================")
        self._log_progress("SCAN LOOP STARTED - 24/7 MONITORING ACTIVE")
        self._log_progress("========================================")
        
        while SCAN_STATE['is_running']:
            try:
                self._log_progress(f"PERFORMING SCAN #{SCAN_STATE['scan_count'] + 1}")
                
                self._perform_full_scan()
                
                SCAN_STATE['last_scan_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                SCAN_STATE['scan_count'] += 1
                SCAN_STATE['alert_log'] = self.alert_log
                SCAN_STATE['progress'] = 100
                
                # Update local state for dashboard
                self.last_scan_time = SCAN_STATE['last_scan_time']
                self.scan_count = SCAN_STATE['scan_count']
                
                self._log_progress(f"SCAN #{SCAN_STATE['scan_count']} COMPLETE")
                self._log_progress(f"TIME: {SCAN_STATE['last_scan_time']}")
                self._log_progress(f"ENTITIES SCANNED: {self.entities_scanned}")
                self._log_progress(f"TOTAL SEARCHES: {self.searches_completed}")
                self._log_progress(f"ALERTS FOUND: {self.alerts_found_this_scan}")
                self._log_progress(f"TOTAL ALERTS: {len(self.alert_log)}")
                self._log_progress("========================================")
                
                time.sleep(300)
            except Exception as e:
                self.error_count += 1
                self._log_progress(f"ERROR: {e}")
                time.sleep(60)
    
    def _perform_full_scan(self):
        """Perform complete scan with FULL progress tracking"""
        global SCAN_STATE
        
        self._log_progress("STARTING FULL SCAN...")
        
        total_entities = len(SENSITIVE_ENTITIES)
        total_categories = len(SENSITIVE_KEYWORD_CATEGORIES)
        keywords_per_category = 10
        self.total_searches = total_entities * total_categories * keywords_per_category
        self.searches_completed = 0
        self.alerts_found_this_scan = 0
        
        SCAN_STATE['total_searches'] = self.total_searches
        
        entity_index = 0
        for entity in SENSITIVE_ENTITIES:
            entity_index += 1
            self.entities_scanned = entity_index
            self.current_entity = entity
            
            entity_progress = (entity_index / total_entities) * 100
            self.current_progress = entity_progress
            
            SCAN_STATE['entities_scanned'] = entity_index
            SCAN_STATE['current_entity'] = entity
            SCAN_STATE['progress'] = entity_progress
            
            self._log_progress(f"[ENTITY {entity_index}/{total_entities}] ({entity_progress:.1f}%) SCANNING: {entity}")
            
            category_index = 0
            for category_name, keywords in SENSITIVE_KEYWORD_CATEGORIES.items():
                category_index += 1
                self.current_category = category_name
                SCAN_STATE['current_category'] = category_name
                
                keyword_index = 0
                for keyword in keywords[:10]:
                    keyword_index += 1
                    self.current_keyword = keyword
                    SCAN_STATE['current_keyword'] = keyword
                    
                    query = f"{entity} {keyword}"
                    result = self._scan_and_analyze(query, entity)
                    
                    self.searches_completed += 1
                    SCAN_STATE['searches_completed'] = self.searches_completed
                    
                    search_progress = (self.searches_completed / self.total_searches) * 100
                    self.current_progress = search_progress
                    SCAN_STATE['progress'] = search_progress
                    
                    if result:
                        self.alerts_found_this_scan += 1
                        SCAN_STATE['alerts_found'] = self.alerts_found_this_scan
                        self._log_progress(f"     🚨 ALERT! Sensitive data found for {entity}")
        
        self._log_progress("FULL SCAN COMPLETE!")
    
    def _scan_and_analyze(self, query, entity):
        """Scan public web and analyze results - returns True if alert triggered"""
        try:
            results = self._search_serper(query)
            
            if results and 'organic' in results:
                for item in results['organic'][:3]:
                    snippet = item.get('snippet', '')
                    url = item.get('link', '')
                    
                    if snippet:
                        analysis = self.monitor.analyze_content(snippet, url)
                        
                        if analysis.get('is_sensitive'):
                            self._trigger_immediate_alert(entity, analysis, snippet, url)
                            return True
            return False
        except Exception as e:
            self._log_progress(f"     ⚠️ Scan error: {e}")
            return False
    
    def _search_serper(self, query):
        """Search using DuckDuckGo PRIMARY + Serper FALLBACK"""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{query} confidential OR salary OR invoice OR procurement", max_results=10))
                if results:
                    return {'organic': results}
        except Exception as e:
            self._log_progress(f"     ⚠️ DuckDuckGo error: {e}")
        
        try:
            api_key = os.environ.get('SERPER_API_KEY', '')
            if api_key:
                headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
                params = {"q": f"{query} (confidential OR salary OR invoice OR procurement)", "num": 10}
                
                import requests
                response = requests.post("https://google.serper.dev/search", headers=headers, json=params, timeout=10)
                
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            self._log_progress(f"     ⚠️ Serper error: {e}")
        
        return None
    
    def _trigger_immediate_alert(self, entity, analysis, content, url):
        """Trigger immediate email alert"""
        global SCAN_STATE
        
        leak_type = analysis.get('type', 'General')
        severity = SEVERITY_LEVELS.get(leak_type, 'Medium')
        
        forensics = self.responder.trace_device_and_ip({'client_ip': '0.0.0.0', 'user_agent': ''})
        
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
            SCAN_STATE['alert_log'] = self.alert_log
    
    def get_status(self):
        """Get current monitoring status from GLOBAL STATE"""
        global SCAN_STATE
        
        return {
            'is_running': SCAN_STATE['is_running'],
            'scan_count': SCAN_STATE['scan_count'],
            'error_count': self.error_count,
            'last_scan_time': SCAN_STATE['last_scan_time'],
            'total_alerts': len(SCAN_STATE['alert_log']),
            'alerts': SCAN_STATE['alert_log'][-20:],
            'progress': SCAN_STATE['progress'],
            'current_entity': SCAN_STATE['current_entity'],
            'current_category': SCAN_STATE['current_category'],
            'current_keyword': SCAN_STATE['current_keyword'],
            'entities_scanned': SCAN_STATE['entities_scanned'],
            'total_searches': SCAN_STATE['total_searches'],
            'searches_completed': SCAN_STATE['searches_completed'],
            'alerts_found_this_scan': SCAN_STATE['alerts_found']
        }

# Global singleton instance
background_monitor = BackgroundMonitorService()
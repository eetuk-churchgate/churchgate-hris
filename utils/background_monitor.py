"""
Churchgate Group AI DLP - 24/7 Background Monitoring Service
Runs independently of Streamlit | Military-Grade Continuous Scanning
Fortune 500 Grade | Real-Time Progress Tracking | Command Center Ready
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
        self.current_progress = 0
        self.current_entity = ""
        self.current_category = ""
        self.current_keyword = ""
        self.entities_scanned = 0
        self.total_searches = 0
        self.searches_completed = 0
        self.alerts_found_this_scan = 0
        
        # Restore from session state if exists
        try:
            import streamlit as st
            if 'dlp_monitor_running' in st.session_state:
                self.is_running = st.session_state.dlp_monitor_running
            if 'dlp_scan_count' in st.session_state:
                self.scan_count = st.session_state.dlp_scan_count
            if 'dlp_last_scan' in st.session_state:
                self.last_scan_time = st.session_state.dlp_last_scan
            if 'dlp_alert_log' in st.session_state:
                self.alert_log = st.session_state.dlp_alert_log
            if 'dlp_progress' in st.session_state:
                self.current_progress = st.session_state.dlp_progress
        except:
            pass
        
    def start(self):
        """Start the background monitoring thread"""
        import streamlit as st
        
        if self.is_running:
            return "Already running"
        
        self.is_running = True
        st.session_state.dlp_monitor_running = True
        st.session_state.dlp_scan_count = self.scan_count
        st.session_state.dlp_last_scan = self.last_scan_time
        st.session_state.dlp_alert_log = self.alert_log
        st.session_state.dlp_progress = 0
        
        self.scan_thread = threading.Thread(target=self._run_scan_loop, daemon=True)
        self.scan_thread.start()
        return "Monitoring started"
    
    def stop(self):
        """Stop the background monitoring"""
        import streamlit as st
        
        self.is_running = False
        st.session_state.dlp_monitor_running = False
        
        return "Monitoring stopped"
    
    def _log_progress(self, message):
        """Print progress with timestamp"""
        print(f"[DLP {datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def _run_scan_loop(self):
        """Main 24/7 scanning loop"""
        import streamlit as st
        
        self._log_progress("========================================")
        self._log_progress("SCAN LOOP STARTED - 24/7 MONITORING ACTIVE")
        self._log_progress("========================================")
        
        while self.is_running:
            try:
                self._log_progress(f"PERFORMING SCAN #{self.scan_count + 1}")
                self._log_progress("----------------------------------------")
                
                self._perform_full_scan()
                
                self.last_scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.scan_count += 1
                
                self._log_progress("----------------------------------------")
                self._log_progress(f"SCAN #{self.scan_count} COMPLETE")
                self._log_progress(f"TIME: {self.last_scan_time}")
                self._log_progress(f"ENTITIES SCANNED: {self.entities_scanned}")
                self._log_progress(f"TOTAL SEARCHES: {self.searches_completed}")
                self._log_progress(f"ALERTS FOUND: {self.alerts_found_this_scan}")
                self._log_progress(f"TOTAL ALERTS: {len(self.alert_log)}")
                self._log_progress("========================================")
                
                # Save to session state
                st.session_state.dlp_scan_count = self.scan_count
                st.session_state.dlp_last_scan = self.last_scan_time
                st.session_state.dlp_alert_log = self.alert_log
                st.session_state.dlp_progress = 100
                st.session_state.dlp_entities_scanned = self.entities_scanned
                st.session_state.dlp_searches_completed = self.searches_completed
                
                time.sleep(300)
            except Exception as e:
                self.error_count += 1
                self._log_progress(f"ERROR: {e}")
                st.session_state.dlp_error_count = self.error_count
                time.sleep(60)
    
    def _perform_full_scan(self):
        """Perform complete scan with FULL progress tracking"""
        import streamlit as st
        
        self._log_progress("STARTING FULL SCAN...")
        self._log_progress(f"TOTAL ENTITIES: {len(SENSITIVE_ENTITIES)}")
        self._log_progress(f"TOTAL CATEGORIES: {len(SENSITIVE_KEYWORD_CATEGORIES)}")
        
        # Calculate total searches
        total_entities = len(SENSITIVE_ENTITIES)
        total_categories = len(SENSITIVE_KEYWORD_CATEGORIES)
        keywords_per_category = 10
        self.total_searches = total_entities * total_categories * keywords_per_category
        self.searches_completed = 0
        self.alerts_found_this_scan = 0
        
        self._log_progress(f"TOTAL SEARCHES TO PERFORM: {self.total_searches}")
        self._log_progress("========================================")
        
        entity_index = 0
        for entity in SENSITIVE_ENTITIES:
            entity_index += 1
            self.entities_scanned = entity_index
            self.current_entity = entity
            
            # Calculate entity progress
            entity_progress = (entity_index / total_entities) * 100
            self.current_progress = entity_progress
            
            self._log_progress(f"[ENTITY {entity_index}/{total_entities}] ({entity_progress:.1f}%) SCANNING: {entity}")
            
            # Save progress to session state
            st.session_state.dlp_progress = entity_progress
            st.session_state.dlp_current_entity = entity
            
            category_index = 0
            for category_name, keywords in SENSITIVE_KEYWORD_CATEGORIES.items():
                category_index += 1
                self.current_category = category_name
                
                self._log_progress(f"  └─ CATEGORY {category_index}/{total_categories}: {category_name}")
                
                keyword_index = 0
                for keyword in keywords[:10]:
                    keyword_index += 1
                    self.current_keyword = keyword
                    
                    query = f"{entity} {keyword}"
                    
                    self._log_progress(f"     └─ [{keyword_index}/10] Searching: \"{keyword}\"")
                    
                    result = self._scan_and_analyze(query, entity)
                    
                    self.searches_completed += 1
                    
                    # Update progress
                    search_progress = (self.searches_completed / self.total_searches) * 100
                    self.current_progress = search_progress
                    
                    # Save to session state every 10 searches
                    if self.searches_completed % 10 == 0:
                        st.session_state.dlp_progress = search_progress
                        st.session_state.dlp_searches_completed = self.searches_completed
                    
                    if result:
                        self.alerts_found_this_scan += 1
                        self._log_progress(f"     🚨 ALERT! Sensitive data found for {entity}")
        
        self._log_progress("========================================")
        self._log_progress(f"FULL SCAN COMPLETE!")
        self._log_progress(f"ENTITIES: {entity_index}/{total_entities}")
        self._log_progress(f"SEARCHES: {self.searches_completed}/{self.total_searches}")
        self._log_progress(f"ALERTS: {self.alerts_found_this_scan}")
        self._log_progress("========================================")
    
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
            self._log_progress(f"     ⚠️ Scan error for \"{query}\": {e}")
            return False
    
    def _search_serper(self, query):
        """Search using DuckDuckGo PRIMARY + Serper FALLBACK"""
        # PRIMARY: DuckDuckGo (FREE - unlimited)
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{query} confidential OR salary OR invoice OR procurement", max_results=10))
                if results:
                    return {'organic': results}
        except Exception as e:
            self._log_progress(f"     ⚠️ DuckDuckGo error: {e}")
        
        # FALLBACK: Serper (if DuckDuckGo fails)
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
            alert_record = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'incident_id': incident_id,
                'entity': analysis.get('company', entity),
                'type': leak_type,
                'severity': severity,
                'source': url
            }
            self.alert_log.append(alert_record)
            
            self._log_progress(f"🚨 ALERT EMAIL SENT! Incident: {incident_id}")
            
            try:
                import streamlit as st
                st.session_state.dlp_alert_log = self.alert_log
            except:
                pass
    
    def get_status(self):
        """Get current monitoring status with progress"""
        return {
            'is_running': self.is_running,
            'scan_count': self.scan_count,
            'error_count': self.error_count,
            'last_scan_time': self.last_scan_time,
            'total_alerts': len(self.alert_log),
            'alerts': self.alert_log[-20:],
            'progress': self.current_progress,
            'current_entity': self.current_entity,
            'current_category': self.current_category,
            'current_keyword': self.current_keyword,
            'entities_scanned': self.entities_scanned,
            'total_searches': self.total_searches,
            'searches_completed': self.searches_completed,
            'alerts_found_this_scan': self.alerts_found_this_scan
        }

# Global singleton instance
background_monitor = BackgroundMonitorService()
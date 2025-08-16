#!/usr/bin/env python3
"""
Connection Manager for handling connection resilience and retry logic
Implements exponential backoff and graceful error handling
"""

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests library not available. Install with: pip install requests")

import time
import subprocess
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

class ConnectionManager:
    """Manages connection resilience and automatic recovery"""
    
    def __init__(self, base_delay: float = 1.0, max_delay: float = 10.0):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.logger = logging.getLogger(__name__)
        
    def check_connection_with_retry(self, url: str, max_retries: int = 3, timeout: int = 5) -> bool:
        """
        Check connection with exponential backoff retry logic
        
        Args:
            url: URL to check
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=timeout)
                if response.status_code == 200:
                    self.logger.info(f"Connection successful to {url}")
                    return True
                else:
                    self.logger.warning(f"HTTP {response.status_code} from {url}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:  # Don't sleep on last attempt
                    # Exponential backoff with jitter
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    time.sleep(delay)
                    
        self.logger.error(f"All connection attempts failed for {url}")
        return False
    
    def wait_for_streamlit_ready(self, port: int = 8501, max_wait: int = 60) -> bool:
        """
        Wait for Streamlit to be ready to accept connections
        
        Args:
            port: Port number to check
            max_wait: Maximum time to wait in seconds
            
        Returns:
            True if Streamlit becomes ready, False if timeout
        """
        url = f"http://localhost:{port}"
        start_time = time.time()
        
        self.logger.info(f"Waiting for Streamlit to be ready at {url}")
        
        while time.time() - start_time < max_wait:
            if self.check_connection_with_retry(url, max_retries=1):
                self.logger.info("Streamlit is ready")
                return True
                
            time.sleep(2)  # Check every 2 seconds
            
        self.logger.error(f"Streamlit not ready after {max_wait} seconds")
        return False
    
    def restart_streamlit(self, app_file: str, port: int = 8501) -> subprocess.Popen:
        """
        Restart Streamlit with proper error handling
        
        Args:
            app_file: Path to the Streamlit app file
            port: Port to run on
            
        Returns:
            Subprocess.Popen object for the new process
            
        Raises:
            RuntimeError: If restart fails
        """
        try:
            # Build command
            cmd = ['streamlit', 'run', app_file, '--server.port', str(port)]
            
            self.logger.info(f"Starting Streamlit: {' '.join(cmd)}")
            
            # Start process with proper handling
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(app_file).parent
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if process started successfully
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise RuntimeError(f"Streamlit failed to start: {stderr}")
                
            return process
            
        except Exception as e:
            self.logger.error(f"Error restarting Streamlit: {e}")
            raise RuntimeError(f"Failed to restart Streamlit: {e}")
    
    def get_connection_error_message(self, error_type: str) -> str:
        """
        Get user-friendly error message with actionable steps
        
        Args:
            error_type: Type of error (timeout, refused, etc.)
            
        Returns:
            User-friendly error message
        """
        messages = {
            'timeout': """
🔄 Connection Timeout
The application is taking longer than expected to start.

Try these steps:
1. Wait a few more seconds and refresh your browser
2. Check if Streamlit is still starting in your terminal
3. Restart the application if needed: streamlit run AcquisitionAnalyst.py
            """.strip(),
            
            'refused': """
🚫 Connection Refused
The application is not running or not accessible.

Try these steps:
1. Restart the application: streamlit run AcquisitionAnalyst.py
2. Check if another application is using port 8501
3. Try a different port: streamlit run AcquisitionAnalyst.py --server.port 8502
            """.strip(),
            
            'general': """
❌ Connection Error
There was a problem connecting to the application.

Try these steps:
1. Restart the application in your terminal
2. Check your internet connection
3. Make sure no firewall is blocking the connection
4. Try opening http://localhost:8501 directly in your browser
            """.strip()
        }
        
        return messages.get(error_type, messages['general'])
    
    def diagnose_connection_issue(self, port: int = 8501) -> Dict[str, Any]:
        """
        Diagnose connection issues and provide recommendations
        
        Args:
            port: Port to diagnose
            
        Returns:
            Diagnosis dict with issue details and recommendations
        """
        diagnosis = {
            'port': port,
            'url': f"http://localhost:{port}",
            'issues': [],
            'recommendations': []
        }
        
        # Check if port is listening
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                
                if result == 0:
                    diagnosis['port_listening'] = True
                    # Try HTTP request
                    if not self.check_connection_with_retry(diagnosis['url'], max_retries=1):
                        diagnosis['issues'].append('Port listening but HTTP request failed')
                        diagnosis['recommendations'].append('Streamlit may be starting up - wait 30 seconds')
                else:
                    diagnosis['port_listening'] = False
                    diagnosis['issues'].append('Nothing listening on port')
                    diagnosis['recommendations'].append('Start Streamlit application')
                    
        except Exception as e:
            diagnosis['issues'].append(f'Port check failed: {e}')
            diagnosis['recommendations'].append('Check network configuration')
        
        # Check for Streamlit process
        from session_manager import SessionManager
        session_mgr = SessionManager()
        if session_mgr.detect_streamlit_process():
            diagnosis['streamlit_process_found'] = True
        else:
            diagnosis['streamlit_process_found'] = False
            diagnosis['issues'].append('No Streamlit process detected')
            diagnosis['recommendations'].append('Start Streamlit: streamlit run AcquisitionAnalyst.py')
            
        return diagnosis
    
    def auto_recover(self, app_file: str, port: int = 8501) -> Dict[str, Any]:
        """
        Attempt automatic recovery from connection issues
        
        Args:
            app_file: Path to Streamlit app file
            port: Port to use
            
        Returns:
            Recovery result dict
        """
        recovery_result = {
            'success': False,
            'actions_taken': [],
            'final_status': {},
            'user_message': ''
        }
        
        try:
            # Diagnose the issue first
            diagnosis = self.diagnose_connection_issue(port)
            recovery_result['initial_diagnosis'] = diagnosis
            
            # Try to fix common issues
            if not diagnosis.get('streamlit_process_found', False):
                self.logger.info("No Streamlit process found, attempting restart")
                recovery_result['actions_taken'].append('restarted_streamlit')
                
                process = self.restart_streamlit(app_file, port)
                
                # Wait for it to be ready
                if self.wait_for_streamlit_ready(port, max_wait=30):
                    recovery_result['success'] = True
                    recovery_result['user_message'] = f"✅ Successfully restarted application on port {port}"
                else:
                    recovery_result['user_message'] = "⚠️ Restarted but not yet ready - please wait and refresh"
                    
            elif diagnosis.get('port_listening', False):
                # Port is listening, might just be starting up
                self.logger.info("Port listening, waiting for HTTP ready")
                recovery_result['actions_taken'].append('waited_for_ready')
                
                if self.wait_for_streamlit_ready(port, max_wait=20):
                    recovery_result['success'] = True
                    recovery_result['user_message'] = f"✅ Application is now ready on port {port}"
                else:
                    recovery_result['user_message'] = "⚠️ Application still not responding - try manual restart"
                    
            # Final status check
            recovery_result['final_status'] = self.diagnose_connection_issue(port)
            
        except Exception as e:
            self.logger.error(f"Auto-recovery failed: {e}")
            recovery_result['user_message'] = f"❌ Auto-recovery failed: {e}"
            recovery_result['actions_taken'].append('recovery_failed')
            
        return recovery_result
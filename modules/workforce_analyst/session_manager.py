#!/usr/bin/env python3
"""
Session Manager for handling existing Streamlit processes
Implements graceful session management and port handling
"""

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil library not available. Install with: pip install psutil")

import socket
import signal
import time
import logging
from typing import Optional, Dict, Any

class SessionManager:
    """Manages Streamlit session lifecycle and port allocation"""
    
    def __init__(self, default_port: int = 8501):
        self.default_port = default_port
        self.logger = logging.getLogger(__name__)
        
    def detect_streamlit_process(self) -> Optional[Dict[str, Any]]:
        """
        Detect if a Streamlit process is already running
        
        Returns:
            Dict with process info if found, None otherwise
        """
        try:
            for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = process.info
                    if proc_info['name'] and 'python' in proc_info['name'].lower():
                        cmdline = proc_info.get('cmdline', [])
                        if cmdline and any('streamlit' in arg.lower() for arg in cmdline):
                            return {
                                'pid': proc_info['pid'],
                                'cmdline': cmdline,
                                'process': process
                            }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Error detecting Streamlit process: {e}")
            
        return None
    
    def shutdown_existing_session(self, pid: int, timeout: int = 10) -> bool:
        """
        Gracefully shutdown existing Streamlit session
        
        Args:
            pid: Process ID to shutdown
            timeout: Maximum time to wait for shutdown
            
        Returns:
            True if successfully shutdown, False otherwise
        """
        try:
            process = psutil.Process(pid)
            
            # Try graceful shutdown first
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=timeout)
                self.logger.info(f"Successfully terminated Streamlit process {pid}")
                return True
            except psutil.TimeoutExpired:
                # Force kill if graceful shutdown failed
                self.logger.warning(f"Graceful shutdown timed out, force killing process {pid}")
                process.kill()
                process.wait(timeout=5)
                return True
                
        except psutil.NoSuchProcess:
            # Process already gone
            return True
        except Exception as e:
            self.logger.error(f"Error shutting down process {pid}: {e}")
            return False
    
    def is_port_available(self, port: int) -> bool:
        """
        Check if a port is available for use
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0  # 0 means connection successful (port busy)
        except Exception:
            return True  # Assume available if we can't check
    
    def find_available_port(self, start_port: int = 8501, max_attempts: int = 10) -> int:
        """
        Find an available port starting from start_port
        
        Args:
            start_port: Starting port number
            max_attempts: Maximum number of ports to try
            
        Returns:
            Available port number
            
        Raises:
            RuntimeError: If no available port found
        """
        for port in range(start_port, start_port + max_attempts):
            if self.is_port_available(port):
                return port
                
        raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_attempts}")
    
    def cleanup_and_prepare(self) -> Dict[str, Any]:
        """
        Cleanup existing sessions and prepare for new launch
        
        Returns:
            Configuration dict with port and status info
        """
        config = {
            'port': self.default_port,
            'existing_session_found': False,
            'cleanup_successful': True,
            'warnings': []
        }
        
        # Check for existing Streamlit process
        existing_process = self.detect_streamlit_process()
        
        if existing_process:
            config['existing_session_found'] = True
            self.logger.info(f"Found existing Streamlit process: {existing_process['pid']}")
            
            # Try to shutdown existing session
            if not self.shutdown_existing_session(existing_process['pid']):
                config['cleanup_successful'] = False
                config['warnings'].append("Could not shutdown existing Streamlit session")
                
                # Find alternative port if cleanup failed
                try:
                    alt_port = self.find_available_port(self.default_port + 1)
                    config['port'] = alt_port
                    config['warnings'].append(f"Using alternative port {alt_port}")
                except RuntimeError as e:
                    config['warnings'].append(str(e))
                    
        # Final port availability check
        if not self.is_port_available(config['port']):
            try:
                config['port'] = self.find_available_port(config['port'] + 1)
            except RuntimeError:
                config['cleanup_successful'] = False
                config['warnings'].append("No available ports found")
        
        return config
    
    def get_session_status(self) -> Dict[str, Any]:
        """
        Get current session status information
        
        Returns:
            Dict with detailed session status
        """
        existing_process = self.detect_streamlit_process()
        
        status = {
            'streamlit_running': existing_process is not None,
            'default_port_available': self.is_port_available(self.default_port),
            'recommended_action': 'ready'
        }
        
        if existing_process:
            status['existing_process'] = {
                'pid': existing_process['pid'],
                'cmdline': existing_process['cmdline']
            }
            status['recommended_action'] = 'cleanup_required'
        elif not status['default_port_available']:
            status['recommended_action'] = 'port_conflict'
            
        return status
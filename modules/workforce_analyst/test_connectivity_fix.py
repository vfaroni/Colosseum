#!/usr/bin/env python3
"""
Test suite for connectivity fix following TDD principles from CLAUDE.md

Tests for:
1. Session Management - Handle existing Streamlit processes
2. Connection Resilience - Recover from connection timeouts  
3. Google Auth Persistence - Remember credentials between sessions
4. User Experience - Clear error handling and recovery
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import psutil
import os
import json
import time
from pathlib import Path
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestSessionManagement(unittest.TestCase):
    """Test proper handling of existing Streamlit sessions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_port = 8501
        self.backup_port = 8502
        
    @patch('psutil.process_iter')
    def test_detect_existing_streamlit_process(self, mock_process_iter):
        """Test detection of running Streamlit process"""
        # Mock a running Streamlit process
        mock_process = Mock()
        mock_process.info = {'pid': 12345, 'name': 'streamlit', 'cmdline': ['streamlit', 'run', 'app.py']}
        mock_process_iter.return_value = [mock_process]
        
        from session_manager import SessionManager
        manager = SessionManager()
        
        result = manager.detect_streamlit_process()
        self.assertIsNotNone(result)
        self.assertEqual(result['pid'], 12345)
        
    @patch('psutil.process_iter')  
    def test_no_existing_streamlit_process(self, mock_process_iter):
        """Test when no Streamlit process is running"""
        mock_process_iter.return_value = []
        
        from session_manager import SessionManager
        manager = SessionManager()
        
        result = manager.detect_streamlit_process()
        self.assertIsNone(result)
        
    @patch('subprocess.run')
    def test_graceful_shutdown_existing_session(self, mock_subprocess):
        """Test graceful shutdown of existing Streamlit session"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        from session_manager import SessionManager
        manager = SessionManager()
        
        result = manager.shutdown_existing_session(12345)
        self.assertTrue(result)
        mock_subprocess.assert_called()
        
    def test_port_availability_check(self):
        """Test checking if port is available"""
        from session_manager import SessionManager
        manager = SessionManager()
        
        # Test with likely available port
        available = manager.is_port_available(9000)
        self.assertIsInstance(available, bool)
        
    @patch('socket.socket')
    def test_find_alternative_port(self, mock_socket):
        """Test finding alternative port when default is busy"""
        # Mock port 8501 as busy, 8502 as available
        mock_socket_instance = Mock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.side_effect = [0, 1]  # 8501 busy, 8502 free
        
        from session_manager import SessionManager
        manager = SessionManager()
        
        port = manager.find_available_port(8501, max_attempts=2)
        self.assertEqual(port, 8502)

class TestConnectionResilience(unittest.TestCase):
    """Test recovery from connection timeouts and network issues"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.max_retries = 3
        self.retry_delay = 1
        
    @patch('time.sleep')
    @patch('requests.get')
    def test_connection_retry_logic(self, mock_get, mock_sleep):
        """Test exponential backoff retry logic"""
        # First two calls fail, third succeeds
        mock_get.side_effect = [
            Exception("Connection timeout"),
            Exception("Connection timeout"), 
            Mock(status_code=200)
        ]
        
        from connection_manager import ConnectionManager
        manager = ConnectionManager()
        
        result = manager.check_connection_with_retry("http://localhost:8501")
        self.assertTrue(result)
        self.assertEqual(mock_get.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        
    @patch('requests.get')
    def test_connection_failure_after_max_retries(self, mock_get):
        """Test failure after maximum retry attempts"""
        mock_get.side_effect = Exception("Connection timeout")
        
        from connection_manager import ConnectionManager
        manager = ConnectionManager()
        
        result = manager.check_connection_with_retry("http://localhost:8501", max_retries=2)
        self.assertFalse(result)
        self.assertEqual(mock_get.call_count, 2)
        
    def test_error_message_clarity(self):
        """Test that error messages provide clear actionable steps"""
        from connection_manager import ConnectionManager
        manager = ConnectionManager()
        
        error_msg = manager.get_connection_error_message("timeout")
        self.assertIn("restart", error_msg.lower())
        self.assertIn("terminal", error_msg.lower())
        
    @patch('subprocess.Popen')
    def test_automatic_restart_on_failure(self, mock_popen):
        """Test automatic restart when connection fails"""
        mock_process = Mock()
        mock_process.poll.return_value = None  # Still running
        mock_popen.return_value = mock_process
        
        from connection_manager import ConnectionManager
        manager = ConnectionManager()
        
        result = manager.restart_streamlit("AcquisitionAnalyst.py")
        self.assertTrue(result)
        mock_popen.assert_called()

class TestGoogleAuthPersistence(unittest.TestCase):
    """Test persistent Google authentication between sessions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_creds_file = "/tmp/test_google_creds.json"
        self.test_token_file = "/tmp/test_google_token.json"
        
    def tearDown(self):
        """Clean up test files"""
        for file_path in [self.test_creds_file, self.test_token_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
                
    def test_save_credentials_to_file(self):
        """Test saving Google credentials to persistent storage"""
        from google_auth_manager import GoogleAuthManager
        manager = GoogleAuthManager(creds_file=self.test_creds_file)
        
        test_creds = {"access_token": "test_token", "refresh_token": "refresh_token"}
        
        result = manager.save_credentials(test_creds)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_creds_file))
        
    def test_load_saved_credentials(self):
        """Test loading previously saved credentials"""
        # Create test credentials file
        test_creds = {"access_token": "test_token", "refresh_token": "refresh_token"}
        with open(self.test_creds_file, 'w') as f:
            json.dump(test_creds, f)
            
        from google_auth_manager import GoogleAuthManager
        manager = GoogleAuthManager(creds_file=self.test_creds_file)
        
        loaded_creds = manager.load_credentials()
        self.assertIsNotNone(loaded_creds)
        self.assertEqual(loaded_creds["access_token"], "test_token")
        
    def test_credentials_not_found(self):
        """Test handling when no saved credentials exist"""
        from google_auth_manager import GoogleAuthManager
        manager = GoogleAuthManager(creds_file="/nonexistent/path.json")
        
        loaded_creds = manager.load_credentials()
        self.assertIsNone(loaded_creds)
        
    @patch('google.auth.transport.requests.Request')
    def test_credential_refresh(self, mock_request):
        """Test automatic refresh of expired credentials"""
        from google_auth_manager import GoogleAuthManager
        manager = GoogleAuthManager()
        
        # Mock expired credentials
        mock_creds = Mock()
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token"
        mock_creds.refresh = Mock()
        
        result = manager.refresh_credentials(mock_creds)
        mock_creds.refresh.assert_called_once()
        
    def test_first_time_auth_instructions(self):
        """Test clear instructions for first-time authentication"""
        from google_auth_manager import GoogleAuthManager
        manager = GoogleAuthManager()
        
        instructions = manager.get_first_time_auth_instructions()
        self.assertIn("browser", instructions.lower())
        self.assertIn("authenticate", instructions.lower())
        self.assertIn("google", instructions.lower())

class TestUserExperience(unittest.TestCase):
    """Test user experience improvements and error handling"""
    
    def test_clear_startup_instructions(self):
        """Test that startup provides clear instructions"""
        from app_launcher import AppLauncher
        launcher = AppLauncher()
        
        instructions = launcher.get_startup_instructions()
        self.assertIn("http://localhost", instructions)
        self.assertIn("browser", instructions.lower())
        
    def test_progress_indicators(self):
        """Test progress indicators during long operations"""
        from app_launcher import AppLauncher
        launcher = AppLauncher()
        
        # Mock progress callback
        progress_calls = []
        def progress_callback(message):
            progress_calls.append(message)
            
        launcher.launch_with_progress(progress_callback)
        self.assertGreater(len(progress_calls), 0)
        
    def test_error_recovery_suggestions(self):
        """Test that errors provide actionable recovery suggestions"""
        from app_launcher import AppLauncher
        launcher = AppLauncher()
        
        suggestions = launcher.get_error_recovery_suggestions("connection_timeout")
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
    def test_one_click_launch_experience(self):
        """Test simplified one-click launch experience"""
        from app_launcher import AppLauncher
        launcher = AppLauncher()
        
        # Should handle all setup automatically
        config = launcher.prepare_launch_config()
        self.assertIn("port", config)
        self.assertIn("auto_restart", config)
        self.assertIn("auth_ready", config)

class TestIntegration(unittest.TestCase):
    """Integration tests for complete connectivity fix"""
    
    @patch('subprocess.Popen')
    @patch('time.sleep')
    def test_end_to_end_launch_scenario(self, mock_sleep, mock_popen):
        """Test complete launch scenario with all fixes"""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        from app_launcher import AppLauncher
        launcher = AppLauncher()
        
        # Should handle: session detection, port management, auth, and launch
        result = launcher.launch_application("AcquisitionAnalyst.py")
        self.assertTrue(result)
        
    def test_graceful_degradation_no_google_auth(self):
        """Test app works without Google auth for basic functions"""
        from app_launcher import AppLauncher
        launcher = AppLauncher()
        
        # Should still allow basic functionality without Google Sheets
        config = launcher.prepare_launch_config(require_google_auth=False)
        self.assertTrue(config.get("basic_mode", False))

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
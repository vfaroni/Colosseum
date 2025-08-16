#!/usr/bin/env python3
"""
Application Launcher with connectivity fixes
Provides one-click launch experience with automatic error recovery
"""

import subprocess
import time
import logging
import webbrowser
from typing import Dict, Any, Callable, Optional, List
from pathlib import Path

from session_manager import SessionManager
from connection_manager import ConnectionManager
from google_auth_manager import GoogleAuthManager

class AppLauncher:
    """Main application launcher with connectivity fixes"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.connection_manager = ConnectionManager()
        self.auth_manager = GoogleAuthManager()
        self.logger = logging.getLogger(__name__)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get_startup_instructions(self) -> str:
        """
        Get clear startup instructions for users
        
        Returns:
            Formatted instructions string
        """
        return """
🚀 AcqUnderwriter Launch Instructions

The application will start automatically. Once ready:
1. Your browser will open to: http://localhost:8501
2. If browser doesn't open, click the link manually
3. Wait for the application to fully load (may take 30-60 seconds)

During startup:
• Session cleanup (if needed)
• Port allocation 
• Google authentication check
• Application initialization

Status updates will appear below...
        """.strip()
    
    def prepare_launch_config(self, require_google_auth: bool = True) -> Dict[str, Any]:
        """
        Prepare launch configuration with all necessary checks
        
        Args:
            require_google_auth: Whether Google auth is required
            
        Returns:
            Launch configuration dict
        """
        config = {
            'app_file': 'AcquisitionAnalyst.py',
            'auto_restart': True,
            'open_browser': True,
            'basic_mode': False
        }
        
        # Session management
        session_config = self.session_manager.cleanup_and_prepare()
        config.update(session_config)
        
        # Authentication status
        auth_status = self.auth_manager.get_auth_status()
        config['auth_ready'] = auth_status['authenticated']
        config['auth_status'] = auth_status
        
        # If Google auth not available, run in basic mode
        if require_google_auth and not auth_status['authenticated']:
            if not auth_status['client_secrets_available']:
                config['basic_mode'] = True
                config['warnings'] = config.get('warnings', [])
                config['warnings'].append("Running in basic mode - Google Sheets disabled")
        
        return config
    
    def launch_with_progress(self, progress_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """
        Launch application with progress updates
        
        Args:
            progress_callback: Function to call with progress updates
            
        Returns:
            Launch result dict
        """
        def update_progress(message: str):
            self.logger.info(message)
            if progress_callback:
                progress_callback(message)
        
        result = {
            'success': False,
            'port': 8501,
            'url': '',
            'process': None,
            'warnings': [],
            'instructions': ''
        }
        
        try:
            update_progress("🔧 Preparing launch configuration...")
            config = self.prepare_launch_config()
            result.update(config)
            
            update_progress(f"🧹 Session cleanup {'completed' if config['cleanup_successful'] else 'had issues'}")
            
            if config['warnings']:
                for warning in config['warnings']:
                    update_progress(f"⚠️ {warning}")
            
            update_progress(f"🌐 Using port {config['port']}")
            
            # Check Google authentication
            if config['auth_ready']:
                update_progress("✅ Google authentication ready")
            elif config['basic_mode']:
                update_progress("🔧 Running in basic mode (no Google Sheets)")
            else:
                update_progress("🔐 Google authentication will be required")
            
            # Launch Streamlit
            update_progress("🚀 Starting Streamlit application...")
            process = self.connection_manager.restart_streamlit(
                config['app_file'], 
                config['port']
            )
            result['process'] = process
            
            # Wait for ready
            update_progress("⏳ Waiting for application to be ready...")
            if self.connection_manager.wait_for_streamlit_ready(config['port'], max_wait=45):
                result['success'] = True
                result['url'] = f"http://localhost:{config['port']}"
                update_progress(f"✅ Application ready at {result['url']}")
                
                # Open browser
                if config.get('open_browser', True):
                    update_progress("🌐 Opening browser...")
                    webbrowser.open(result['url'])
                    
            else:
                update_progress("⚠️ Application started but not yet responding")
                result['url'] = f"http://localhost:{config['port']}"
                result['warnings'].append("Application may still be loading - try refreshing browser")
            
            # Final instructions
            result['instructions'] = self.get_post_launch_instructions(result)
            update_progress("🎉 Launch completed!")
            
        except Exception as e:
            update_progress(f"❌ Launch failed: {e}")
            result['error'] = str(e)
            result['instructions'] = self.get_error_recovery_suggestions("launch_failed")
            
        return result
    
    def launch_application(self, app_file: str = "AcquisitionAnalyst.py") -> bool:
        """
        Simple launch method for testing
        
        Args:
            app_file: Path to Streamlit app file
            
        Returns:
            True if launch successful, False otherwise
        """
        try:
            config = self.prepare_launch_config()
            process = self.connection_manager.restart_streamlit(app_file, config['port'])
            
            # Wait for ready with shorter timeout for testing
            return self.connection_manager.wait_for_streamlit_ready(config['port'], max_wait=20)
            
        except Exception as e:
            self.logger.error(f"Launch failed: {e}")
            return False
    
    def get_post_launch_instructions(self, launch_result: Dict[str, Any]) -> str:
        """
        Get post-launch instructions based on launch result
        
        Args:
            launch_result: Result from launch operation
            
        Returns:
            Formatted instructions string
        """
        if launch_result['success']:
            instructions = f"""
✅ AcqUnderwriter is Ready!

🌐 Access your application at: {launch_result['url']}

📋 What you can do:
• Select deals from your Dropbox folder
• Extract property data using AI
• Review and edit extracted information
• Export to Google Sheets for analysis
            """
            
            if launch_result.get('basic_mode'):
                instructions += "\n\n🔧 Basic Mode: Google Sheets export disabled"
            elif not launch_result.get('auth_ready'):
                instructions += "\n\n🔐 First use: You'll need to authenticate with Google"
                
        else:
            instructions = f"""
⚠️ Application Started with Issues

🌐 Try accessing: {launch_result['url']}

If not working:
1. Wait 30-60 seconds for full startup
2. Refresh your browser
3. Check terminal for error messages
4. Try restarting: streamlit run AcquisitionAnalyst.py
            """
            
        if launch_result.get('warnings'):
            instructions += "\n\n⚠️ Warnings:\n"
            for warning in launch_result['warnings']:
                instructions += f"• {warning}\n"
                
        return instructions.strip()
    
    def get_error_recovery_suggestions(self, error_type: str) -> List[str]:
        """
        Get error recovery suggestions based on error type
        
        Args:
            error_type: Type of error encountered
            
        Returns:
            List of recovery suggestions
        """
        suggestions = {
            'connection_timeout': [
                "Wait 30-60 seconds and refresh browser",
                "Check if Streamlit is still starting in terminal", 
                "Restart: streamlit run AcquisitionAnalyst.py",
                "Try alternative port: streamlit run AcquisitionAnalyst.py --server.port 8502"
            ],
            'port_busy': [
                "Stop existing Streamlit processes",
                "Use alternative port: --server.port 8502",
                "Restart your terminal session"
            ],
            'launch_failed': [
                "Check Python and Streamlit installation",
                "Verify AcquisitionAnalyst.py exists",
                "Check terminal for detailed error messages",
                "Try: pip install -r requirements.txt"
            ],
            'auth_failed': [
                "Set up Google client secrets file",
                "Check internet connection",
                "Clear saved credentials and re-authenticate",
                "Verify Google APIs are enabled"
            ]
        }
        
        return suggestions.get(error_type, [
            "Check error messages in terminal",
            "Restart the application",
            "Contact support if issue persists"
        ])
    
    def auto_recover_and_launch(self, app_file: str = "AcquisitionAnalyst.py") -> Dict[str, Any]:
        """
        Attempt automatic recovery and launch
        
        Args:
            app_file: Path to Streamlit app file
            
        Returns:
            Recovery and launch result
        """
        result = {
            'recovery_attempted': True,
            'recovery_successful': False,
            'launch_successful': False,
            'final_url': '',
            'user_message': ''
        }
        
        try:
            # Get initial port
            config = self.prepare_launch_config()
            port = config['port']
            
            # Attempt recovery
            recovery = self.connection_manager.auto_recover(app_file, port)
            result['recovery_successful'] = recovery['success']
            
            if recovery['success']:
                result['launch_successful'] = True
                result['final_url'] = f"http://localhost:{port}"
                result['user_message'] = recovery['user_message']
            else:
                result['user_message'] = recovery['user_message']
                
        except Exception as e:
            result['user_message'] = f"Auto-recovery failed: {e}"
            
        return result

# Convenience function for simple usage
def launch_acq_underwriter(progress_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
    """
    Convenience function to launch AcqUnderwriter with all fixes
    
    Args:
        progress_callback: Optional callback for progress updates
        
    Returns:
        Launch result dict
    """
    launcher = AppLauncher()
    return launcher.launch_with_progress(progress_callback)

if __name__ == "__main__":
    # Command line usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch AcqUnderwriter with connectivity fixes")
    parser.add_argument("--port", type=int, default=8501, help="Port to use")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")
    parser.add_argument("--basic-mode", action="store_true", help="Skip Google auth")
    
    args = parser.parse_args()
    
    def print_progress(message):
        print(message)
    
    launcher = AppLauncher()
    result = launcher.launch_with_progress(print_progress)
    
    if result['success']:
        print(f"\n✅ Success! Application available at: {result['url']}")
    else:
        print(f"\n❌ Launch had issues. Try: {result['url']}")
        
    if result.get('instructions'):
        print(f"\n{result['instructions']}")
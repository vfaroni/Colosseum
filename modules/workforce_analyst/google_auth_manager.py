#!/usr/bin/env python3
"""
Google Authentication Manager for persistent credential handling
Implements secure credential storage and automatic refresh
"""

import json
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import pickle

# Import Google auth modules with error handling
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    print("Warning: Google auth libraries not available. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2")

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

class GoogleAuthManager:
    """Manages Google OAuth credentials with persistence"""
    
    # Gmail and Sheets scopes
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self, creds_file: Optional[str] = None, token_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Set default file paths
        self.creds_file = creds_file or os.path.expanduser('~/.acq_underwriter/google_creds.json')
        self.token_file = token_file or os.path.expanduser('~/.acq_underwriter/google_token.pickle')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.creds_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
        
    def save_credentials(self, creds_data: Dict[str, Any]) -> bool:
        """
        Save Google credentials to persistent storage
        
        Args:
            creds_data: Credentials data to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.creds_file, 'w') as f:
                json.dump(creds_data, f, indent=2)
            
            # Set secure permissions
            os.chmod(self.creds_file, 0o600)
            
            self.logger.info(f"Credentials saved to {self.creds_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving credentials: {e}")
            return False
    
    def load_credentials(self) -> Optional[Dict[str, Any]]:
        """
        Load saved Google credentials
        
        Returns:
            Credentials dict if found, None otherwise
        """
        try:
            if os.path.exists(self.creds_file):
                with open(self.creds_file, 'r') as f:
                    creds_data = json.load(f)
                self.logger.info("Credentials loaded from file")
                return creds_data
            else:
                self.logger.info("No saved credentials file found")
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading credentials: {e}")
            return None
    
    def save_token(self, creds: Credentials) -> bool:
        """
        Save Google OAuth token for reuse
        
        Args:
            creds: Google OAuth credentials object
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.token_file, 'wb') as f:
                pickle.dump(creds, f)
            
            # Set secure permissions
            os.chmod(self.token_file, 0o600)
            
            self.logger.info(f"Token saved to {self.token_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving token: {e}")
            return False
    
    def load_token(self) -> Optional[Credentials]:
        """
        Load saved Google OAuth token
        
        Returns:
            Credentials object if found and valid, None otherwise
        """
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as f:
                    creds = pickle.load(f)
                    
                # Check if credentials are valid
                if creds and creds.valid:
                    self.logger.info("Valid token loaded from file")
                    return creds
                elif creds and creds.expired and creds.refresh_token:
                    self.logger.info("Token expired but has refresh token")
                    return creds
                else:
                    self.logger.warning("Token invalid or expired without refresh")
                    return None
            else:
                self.logger.info("No saved token file found")
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading token: {e}")
            return None
    
    def refresh_credentials(self, creds: Credentials) -> bool:
        """
        Refresh expired Google credentials
        
        Args:
            creds: Expired credentials to refresh
            
        Returns:
            True if refresh successful, False otherwise
        """
        try:
            if creds.expired and creds.refresh_token:
                # Create request with extended timeout for Google servers
                request = Request(timeout=300)  # 5 minute timeout
                creds.refresh(request)
                
                # Save refreshed token
                self.save_token(creds)
                
                self.logger.info("Credentials refreshed successfully")
                return True
            else:
                self.logger.warning("Cannot refresh credentials - no refresh token")
                return False
                
        except Exception as e:
            self.logger.error(f"Error refreshing credentials: {e}")
            return False
    
    def get_authenticated_credentials(self, force_reauth: bool = False) -> Optional[Credentials]:
        """
        Get authenticated Google credentials, handling refresh automatically
        
        Args:
            force_reauth: Force new authentication even if token exists
            
        Returns:
            Valid credentials object or None if authentication failed
        """
        if not force_reauth:
            # Try to load existing token
            creds = self.load_token()
            
            if creds:
                if creds.valid:
                    return creds
                elif creds.expired and creds.refresh_token:
                    if self.refresh_credentials(creds):
                        return creds
        
        # Need new authentication
        return self.authenticate_new()
    
    def authenticate_new(self) -> Optional[Credentials]:
        """
        Perform new Google authentication flow
        
        Returns:
            New credentials object or None if failed
        """
        try:
            # Check if we have client secrets
            client_secrets = self.get_client_secrets()
            if not client_secrets:
                self.logger.error("No Google client secrets found")
                return None
            
            # Create flow
            flow = InstalledAppFlow.from_client_config(client_secrets, self.SCOPES)
            
            # Run local server flow
            creds = flow.run_local_server(port=0)
            
            # Save the credentials
            self.save_token(creds)
            
            self.logger.info("New authentication completed successfully")
            return creds
            
        except Exception as e:
            self.logger.error(f"Error in new authentication: {e}")
            return None
    
    def get_client_secrets(self) -> Optional[Dict[str, Any]]:
        """
        Get Google client secrets from various sources
        
        Returns:
            Client secrets dict or None if not found
        """
        # Try Streamlit secrets first
        try:
            if hasattr(st, 'secrets') and 'google' in st.secrets:
                return dict(st.secrets['google'])
        except Exception:
            pass
        
        # Try environment variable
        secrets_json = os.getenv('GOOGLE_CLIENT_SECRETS')
        if secrets_json:
            try:
                return json.loads(secrets_json)
            except json.JSONDecodeError:
                self.logger.error("Invalid JSON in GOOGLE_CLIENT_SECRETS")
        
        # Try local file
        secrets_file = os.path.expanduser('~/.acq_underwriter/client_secrets.json')
        if os.path.exists(secrets_file):
            try:
                with open(secrets_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error reading client secrets file: {e}")
        
        return None
    
    def get_first_time_auth_instructions(self) -> str:
        """
        Get instructions for first-time authentication setup
        
        Returns:
            Formatted instructions string
        """
        return """
🔐 First-Time Google Authentication Setup

To use Google Sheets integration, you need to authenticate once:

1. **Get Google Credentials:**
   - Go to: https://console.cloud.google.com/
   - Create a new project or select existing
   - Enable Google Sheets API and Google Drive API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the JSON file

2. **Save Credentials:**
   - Save the downloaded JSON as: ~/.acq_underwriter/client_secrets.json
   - Or add to Streamlit secrets.toml under [google] section

3. **Authenticate:**
   - Click "Authenticate Google" button below
   - Complete OAuth flow in your browser
   - Credentials will be saved for future use

4. **Future Use:**
   - Authentication happens automatically
   - Credentials refresh automatically when needed
   - Re-authentication only needed if you revoke access

Need help? Check the setup guide or contact support.
        """.strip()
    
    def get_auth_status(self) -> Dict[str, Any]:
        """
        Get current authentication status
        
        Returns:
            Status dict with authentication details
        """
        status = {
            'authenticated': False,
            'token_exists': os.path.exists(self.token_file),
            'credentials_exist': os.path.exists(self.creds_file),
            'client_secrets_available': self.get_client_secrets() is not None,
            'needs_setup': False,
            'message': ''
        }
        
        # Check if we have valid credentials
        creds = self.load_token()
        if creds and creds.valid:
            status['authenticated'] = True
            status['message'] = '✅ Google authentication is active'
        elif creds and creds.expired and creds.refresh_token:
            # Try to refresh
            if self.refresh_credentials(creds):
                status['authenticated'] = True
                status['message'] = '✅ Google authentication refreshed'
            else:
                status['message'] = '⚠️ Authentication expired - need to re-authenticate'
        elif not status['client_secrets_available']:
            status['needs_setup'] = True
            status['message'] = '🔧 Setup required - need Google client secrets'
        else:
            status['message'] = '🔐 Authentication required - click to authenticate'
            
        return status
    
    def clear_saved_credentials(self) -> bool:
        """
        Clear all saved credentials (for troubleshooting)
        
        Returns:
            True if cleared successfully
        """
        try:
            files_removed = []
            
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
                files_removed.append('token')
                
            if os.path.exists(self.creds_file):
                os.remove(self.creds_file)
                files_removed.append('credentials')
            
            self.logger.info(f"Cleared saved auth files: {files_removed}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing credentials: {e}")
            return False
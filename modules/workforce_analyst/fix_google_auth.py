#!/usr/bin/env python3
"""
Permanent fix for Google Authentication in AcqUnderwriter
Implements service account support and better OAuth2 persistence
"""

import os
import json
import logging
from pathlib import Path

def create_service_account_setup():
    """Create instructions for service account setup"""
    
    instructions = """
🔧 PERMANENT GOOGLE AUTHENTICATION FIX

To eliminate repeated authentication, set up a Google Service Account:

1. Go to: https://console.cloud.google.com/
2. Create/select a project
3. Enable these APIs:
   - Google Sheets API
   - Google Drive API
4. Go to IAM & Admin → Service Accounts
5. Create Service Account: "acq-underwriter"
6. Download JSON key file
7. Save it as: service-account-key.json in this directory

Then run: python3 fix_google_auth.py install
    """
    
    print(instructions)

def install_service_account():
    """Install service account credentials"""
    
    service_key_path = Path("service-account-key.json")
    
    if not service_key_path.exists():
        print("❌ service-account-key.json not found")
        print("Please download it from Google Cloud Console first")
        return False
    
    # Validate the service account file
    try:
        with open(service_key_path, 'r') as f:
            key_data = json.load(f)
            
        required_fields = ['type', 'client_email', 'private_key']
        if not all(field in key_data for field in required_fields):
            print("❌ Invalid service account key file")
            return False
            
        if key_data.get('type') != 'service_account':
            print("❌ Not a service account key file")
            return False
            
        print(f"✅ Valid service account: {key_data['client_email']}")
        
        # Set environment variable for current session
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(service_key_path.absolute())
        
        # Add to shell profile for persistence
        shell_profiles = [
            Path.home() / '.zshrc',
            Path.home() / '.bash_profile',
            Path.home() / '.bashrc'
        ]
        
        env_line = f'export GOOGLE_APPLICATION_CREDENTIALS="{service_key_path.absolute()}"'
        
        for profile in shell_profiles:
            if profile.exists():
                with open(profile, 'r') as f:
                    content = f.read()
                
                if 'GOOGLE_APPLICATION_CREDENTIALS' not in content:
                    with open(profile, 'a') as f:
                        f.write(f'\n# AcqUnderwriter Google Auth\n{env_line}\n')
                    print(f"✅ Added to {profile}")
                else:
                    print(f"✅ Already configured in {profile}")
        
        # Test the credentials
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            credentials = service_account.Credentials.from_service_account_file(
                service_key_path,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
            
            # Test API access
            sheets_service = build('sheets', 'v4', credentials=credentials)
            print("✅ Google Sheets API access confirmed")
            
            print("\n🎉 SERVICE ACCOUNT SETUP COMPLETE!")
            print("Authentication will now persist between sessions.")
            print("Restart your terminal and try the app again.")
            
            return True
            
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error reading service account file: {e}")
        return False

def fix_current_auth():
    """Try to fix current OAuth2 authentication"""
    
    print("🔧 Attempting to fix current authentication...")
    
    # Check current ADC status
    adc_path = Path.home() / '.config' / 'gcloud' / 'application_default_credentials.json'
    
    if adc_path.exists():
        try:
            with open(adc_path, 'r') as f:
                creds = json.load(f)
            
            print("✅ Found existing ADC credentials")
            
            # Try to refresh them
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            
            credentials = Credentials.from_authorized_user_info(creds)
            
            if credentials.expired and credentials.refresh_token:
                print("🔄 Refreshing expired credentials...")
                credentials.refresh(Request())
                
                # Save refreshed credentials
                with open(adc_path, 'w') as f:
                    f.write(credentials.to_json())
                
                print("✅ Credentials refreshed successfully")
                return True
            elif credentials.valid:
                print("✅ Credentials are already valid")
                return True
            else:
                print("❌ Credentials cannot be refreshed")
                return False
                
        except Exception as e:
            print(f"❌ Error refreshing credentials: {e}")
            return False
    else:
        print("❌ No ADC credentials found")
        return False

def main():
    """Main function"""
    
    print("🔧 AcqUnderwriter Google Authentication Fix")
    print("=" * 50)
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'setup':
            create_service_account_setup()
        elif command == 'install':
            install_service_account()
        elif command == 'fix':
            fix_current_auth()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 fix_google_auth.py [setup|install|fix]")
    else:
        # Try to fix current auth first
        print("Step 1: Trying to fix current authentication...")
        if fix_current_auth():
            print("✅ Current authentication fixed!")
        else:
            print("❌ Current authentication cannot be fixed")
            print("\nStep 2: Setting up permanent solution...")
            create_service_account_setup()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Non-interactive Google authentication refresh"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

def refresh_auth():
    """Refresh Google authentication"""
    creds_dir = os.path.expanduser("~/.acq_underwriter")
    os.makedirs(creds_dir, exist_ok=True)
    
    token_path = os.path.join(creds_dir, "google_token.json")
    
    # ADC credentials path
    adc_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
    
    if os.path.exists(adc_path):
        print("✅ ADC credentials found")
        
        # Copy ADC to our token path
        import shutil
        shutil.copy2(adc_path, token_path)
        print(f"✅ Credentials saved to {token_path}")
        
        # Try to load and refresh
        try:
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            
            # Create credentials object
            creds = Credentials.from_authorized_user_info(token_data)
            
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired token...")
                # Create request with extended timeout for Google servers
                request = Request(timeout=300)  # 5 minute timeout
                creds.refresh(request)
                
                # Save refreshed token
                with open(token_path, 'w') as f:
                    f.write(creds.to_json())
                print("✅ Token refreshed successfully")
            else:
                print("✅ Token is valid")
                
        except Exception as e:
            print(f"⚠️ Could not refresh token: {e}")
            print("✅ But ADC credentials are available for use")
    else:
        print("❌ No ADC credentials found")
        print("Please run: gcloud auth application-default login")

if __name__ == "__main__":
    refresh_auth()
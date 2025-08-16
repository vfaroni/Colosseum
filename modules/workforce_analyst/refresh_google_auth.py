#!/usr/bin/env python3
"""
Script to refresh Google authentication interactively
"""

import subprocess
import sys
import webbrowser
import time

def refresh_google_auth():
    """Refresh Google Application Default Credentials"""
    
    print("🔐 Google Authentication Refresh")
    print("=" * 40)
    print()
    
    print("The Google authentication needs to be refreshed.")
    print("This will open a browser window for you to sign in.")
    print()
    
    response = input("Ready to proceed? (y/n): ").strip().lower()
    if response != 'y':
        print("Authentication cancelled.")
        return False
    
    print()
    print("🌐 Starting authentication process...")
    print("A browser window will open shortly...")
    
    try:
        # Run the gcloud auth command
        result = subprocess.run([
            'gcloud', 'auth', 'application-default', 'login'
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Authentication completed successfully!")
            
            # Test the authentication
            print("🧪 Testing authentication...")
            test_result = subprocess.run([
                'gcloud', 'auth', 'application-default', 'print-access-token'
            ], capture_output=True, text=True)
            
            if test_result.returncode == 0:
                print("✅ Authentication test successful!")
                return True
            else:
                print("⚠️ Authentication completed but test failed.")
                print("You may need to try again.")
                return False
        else:
            print("❌ Authentication failed.")
            return False
            
    except FileNotFoundError:
        print("❌ Google Cloud CLI (gcloud) not found.")
        print("Please install it from: https://cloud.google.com/sdk/docs/install")
        return False
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return False

def main():
    success = refresh_google_auth()
    
    if success:
        print()
        print("🎉 Google authentication is now ready!")
        print("You can now use Google Sheets features in AcqUnderwriter.")
        print()
        print("Try the ADC authentication button in the app again.")
    else:
        print()
        print("❌ Authentication was not completed.")
        print("Please try running this script again or contact support.")

if __name__ == "__main__":
    main()
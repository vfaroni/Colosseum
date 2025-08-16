#!/usr/bin/env python3
"""Verify batch processing setup"""

import os
import sys

def main():
    print("Verifying batch processing setup...")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    
    # Check if we can import the module
    try:
        from email_deal_filter_oauth_improved import EmailDealFilterOAuth
        print("✓ Successfully imported EmailDealFilterOAuth")
        
        # Create instance
        filter_tool = EmailDealFilterOAuth()
        print("✓ Successfully created filter instance")
        
        # Check authentication
        print("Checking Gmail authentication...")
        service = filter_tool.authenticate_gmail()
        if service:
            print("✓ Gmail authentication successful")
            print("\nReady to run batch processing!")
            print("The script will process ALL emails in Deal Announcements folder")
            print("in batches of 50 and delete emails that don't meet criteria.")
        else:
            print("✗ Gmail authentication failed")
            
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()
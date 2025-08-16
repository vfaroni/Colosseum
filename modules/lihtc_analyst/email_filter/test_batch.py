#!/usr/bin/env python3
"""Test batch processing functionality"""

from email_deal_filter_oauth_improved import EmailDealFilterOAuth

def main():
    print("Testing batch processing functionality...")
    filter_tool = EmailDealFilterOAuth()
    
    # Test with small batch size in dry run mode
    filter_tool.process_emails(dry_run=True, batch_size=10)

if __name__ == "__main__":
    main()
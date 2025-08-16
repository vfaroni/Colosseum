#!/usr/bin/env python3
"""Run email deletion with batch processing - REAL DELETION MODE"""

from email_deal_filter_oauth_improved import EmailDealFilterOAuth

def main():
    print("🚨 REAL DELETION MODE - This will actually delete emails!")
    print("Processing ALL emails in Deal Announcements folder...")
    print("=" * 80)
    
    filter_tool = EmailDealFilterOAuth()
    
    # Run in deletion mode (not dry run) with batch processing
    filter_tool.process_emails(dry_run=False, batch_size=50)
    
    print("\n" + "=" * 80)
    print("Email deletion process complete!")

if __name__ == "__main__":
    main()
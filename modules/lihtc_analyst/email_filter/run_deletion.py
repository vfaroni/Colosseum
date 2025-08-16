#!/usr/bin/env python3
"""Script to run email deletion without interactive prompts"""

from email_deal_filter_oauth_improved import EmailDealFilterOAuth

def main():
    filter_tool = EmailDealFilterOAuth()
    
    # Run in deletion mode (not dry run)
    print("Running email filter in DELETION mode with detailed output...")
    print("=" * 80)
    filter_tool.process_emails(dry_run=False)

if __name__ == "__main__":
    main()
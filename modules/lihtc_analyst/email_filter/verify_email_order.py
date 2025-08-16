#!/usr/bin/env python3

import json
from datetime import datetime
import email.utils
from email_deal_filter_oauth_improved import EmailDealFilterOAuth

class EmailOrderVerifier:
    def __init__(self):
        self.filter_instance = EmailDealFilterOAuth()
    
    def parse_email_date(self, date_string):
        """Parse email date string to datetime object"""
        try:
            # Gmail API date format can vary, try multiple formats
            if date_string:
                # Use email.utils which handles RFC 2822 format
                parsed = email.utils.parsedate_tz(date_string)
                if parsed:
                    return datetime.fromtimestamp(email.utils.mktime_tz(parsed))
        except:
            pass
        return None
    
    def get_email_details_with_dates(self, service, count=15):
        """Get first N emails with detailed timestamp information"""
        print(f"Retrieving first {count} emails from Deal Announcements folder...")
        
        # Get folder ID
        folder_id = self.filter_instance.get_folder_id(service, "Deal Announcements")
        if not folder_id:
            print("Error: Deal Announcements folder not found")
            return []
        
        # Query for emails
        query = 'in:"INBOX/Deal Announcements"'
        
        try:
            # Get message list (API order)
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=count
            ).execute()
            
            messages = results.get('messages', [])
            if not messages:
                print("No messages found")
                return []
            
            print(f"Found {len(messages)} messages, retrieving details...")
            
            email_details = []
            
            for idx, message in enumerate(messages, 1):
                try:
                    # Get full message details
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()
                    
                    # Extract headers
                    headers = msg['payload'].get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                    date_header = next((h['value'] for h in headers if h['name'] == 'Date'), None)
                    
                    # Parse date
                    parsed_date = self.parse_email_date(date_header)
                    
                    # Get internal date from Gmail API (milliseconds since epoch)
                    internal_date_ms = int(msg.get('internalDate', 0))
                    internal_date = datetime.fromtimestamp(internal_date_ms / 1000) if internal_date_ms else None
                    
                    # Extract sender name (before email address)
                    sender_name = sender.split('<')[0].strip() if '<' in sender else sender
                    
                    email_info = {
                        'api_position': idx,
                        'message_id': message['id'],
                        'subject': subject,
                        'sender': sender_name,
                        'sender_full': sender,
                        'date_header': date_header,
                        'parsed_date': parsed_date,
                        'internal_date': internal_date,
                        'internal_date_ms': internal_date_ms
                    }
                    
                    email_details.append(email_info)
                    print(f"  {idx:2d}. {subject[:60]}...")
                    
                except Exception as e:
                    print(f"Error processing message {idx}: {e}")
                    continue
            
            return email_details
            
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return []
    
    def display_email_comparison(self, emails):
        """Display emails with multiple sorting options for comparison"""
        if not emails:
            print("No emails to display")
            return
        
        print("\n" + "="*100)
        print("EMAIL ORDER VERIFICATION - Compare with your Gmail visual interface")
        print("="*100)
        
        # Show API order (current script behavior)
        print(f"\n📧 CURRENT API ORDER (what script sees):")
        print("-" * 100)
        for email in emails:
            date_str = email['parsed_date'].strftime('%Y-%m-%d %H:%M:%S') if email['parsed_date'] else 'No date'
            print(f"{email['api_position']:2d}. {email['subject'][:70]:<70} | {date_str}")
            print(f"    From: {email['sender'][:50]}")
            print()
        
        # Show sorted by parsed date (newest first)
        print(f"\n📧 SORTED BY DATE (newest first) - This should match Gmail visual order:")
        print("-" * 100)
        emails_by_date = sorted([e for e in emails if e['parsed_date']], 
                               key=lambda x: x['parsed_date'], reverse=True)
        
        for idx, email in enumerate(emails_by_date, 1):
            date_str = email['parsed_date'].strftime('%Y-%m-%d %H:%M:%S') if email['parsed_date'] else 'No date'
            api_pos = email['api_position']
            print(f"{idx:2d}. {email['subject'][:70]:<70} | {date_str} (was #{api_pos})")
            print(f"    From: {email['sender'][:50]}")
            print()
        
        # Show sorted by internal date
        print(f"\n📧 SORTED BY INTERNAL DATE (Gmail's internal timestamp):")
        print("-" * 100)
        emails_by_internal = sorted([e for e in emails if e['internal_date']], 
                                   key=lambda x: x['internal_date'], reverse=True)
        
        for idx, email in enumerate(emails_by_internal, 1):
            date_str = email['internal_date'].strftime('%Y-%m-%d %H:%M:%S') if email['internal_date'] else 'No date'
            api_pos = email['api_position']
            print(f"{idx:2d}. {email['subject'][:70]:<70} | {date_str} (was #{api_pos})")
            print(f"    From: {email['sender'][:50]}")
            print()
    
    def analyze_order_differences(self, emails):
        """Analyze differences between different ordering methods"""
        if len(emails) < 2:
            return
        
        print("\n" + "="*100)
        print("ORDER DIFFERENCE ANALYSIS")
        print("="*100)
        
        # Create different ordered lists
        api_order = emails
        date_order = sorted([e for e in emails if e['parsed_date']], 
                           key=lambda x: x['parsed_date'], reverse=True)
        internal_order = sorted([e for e in emails if e['internal_date']], 
                               key=lambda x: x['internal_date'], reverse=True)
        
        # Compare API vs Date order
        print("\n🔍 DIFFERENCES: API Order vs Date Order")
        print("-" * 60)
        mismatched = 0
        for i in range(min(len(api_order), len(date_order))):
            if api_order[i]['message_id'] != date_order[i]['message_id']:
                mismatched += 1
                print(f"Position {i+1}:")
                print(f"  API:  {api_order[i]['subject'][:50]}")
                print(f"  Date: {date_order[i]['subject'][:50]}")
                print()
        
        if mismatched == 0:
            print("✅ API order matches date order perfectly!")
        else:
            print(f"❌ Found {mismatched} position differences")
        
        # Show recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 60)
        if mismatched > 0:
            print("• Email script should sort by date to match Gmail visual interface")
            print("• Implement client-side sorting after API retrieval")
            print("• Use 'parsed_date' from email headers for consistent ordering")
        else:
            print("• Current API ordering matches date ordering")
            print("• Issue may be threading, caching, or timing-related")
    
    def run_verification(self, count=15):
        """Run complete order verification process"""
        print("Starting Email Order Verification...")
        print("This will help diagnose API vs visual interface ordering differences")
        print()
        
        # Authenticate
        service = self.filter_instance.authenticate_gmail()
        if not service:
            print("❌ Failed to authenticate with Gmail")
            return
        
        print("✅ Gmail authentication successful")
        
        # Get email details
        emails = self.get_email_details_with_dates(service, count)
        if not emails:
            print("❌ No emails retrieved")
            return
        
        # Display comparisons
        self.display_email_comparison(emails)
        
        # Analyze differences
        self.analyze_order_differences(emails)
        
        print(f"\n" + "="*100)
        print("NEXT STEPS:")
        print("="*100)
        print("1. Compare the 'SORTED BY DATE' section above with your Gmail visual interface")
        print("2. If they match, the fix is to implement date sorting in the batch script")
        print("3. If they don't match, we need to investigate Gmail's threading/grouping logic")
        print("4. Note any emails that appear in different positions")
        print()

def main():
    """Main function to run email order verification"""
    verifier = EmailOrderVerifier()
    
    # Run verification with first 15 emails
    verifier.run_verification(15)

if __name__ == "__main__":
    main()
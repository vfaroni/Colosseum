#!/usr/bin/env python3

import subprocess
import sys
import time
import argparse
import email.utils
from datetime import datetime
from email_deal_filter_oauth_improved import EmailDealFilterOAuth

def parse_email_date(date_string):
    """Parse email date string to datetime object"""
    try:
        if date_string:
            parsed = email.utils.parsedate_tz(date_string)
            if parsed:
                return datetime.fromtimestamp(email.utils.mktime_tz(parsed))
    except:
        pass
    return None

def run_batch_filtering(verify_mode=False):
    """Run email filtering in batches of 50 with user permission"""
    
    print("=" * 80)
    print("BATCH EMAIL FILTERING - 50 EMAILS AT A TIME")
    print("=" * 80)
    
    filter_instance = EmailDealFilterOAuth()
    
    # Authenticate
    service = filter_instance.authenticate_gmail()
    if not service:
        print("Failed to authenticate with Gmail")
        return
    
    # Get folder ID
    folder_id = filter_instance.get_folder_id(service, "Deal Announcements")
    if not folder_id:
        print(f"Folder 'Deal Announcements' not found")
        return
    
    batch_number = 1
    continue_processing = True
    next_page_token = None
    query = 'in:"INBOX/Deal Announcements"'
    
    # If in verify mode, just show first batch for verification
    if verify_mode:
        print("🔍 VERIFICATION MODE - Showing first 15 emails for comparison")
        print("Compare this with your Gmail visual interface to confirm alignment")
        print("=" * 80)
    
    while continue_processing:
        print(f"\n{'=' * 80}")
        print(f"PROCESSING BATCH {batch_number} (50 EMAILS)")
        print(f"{'=' * 80}")
        
        # Get emails - adjust count for verify mode
        max_results = 15 if verify_mode else 50
        
        if next_page_token:
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results,
                pageToken=next_page_token
            ).execute()
        else:
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
        
        messages = results.get('messages', [])
        next_page_token = results.get('nextPageToken')
        
        if not messages:
            print("\nNo more emails to process!")
            break
        
        print(f"\nFound {len(messages)} emails to analyze...")
        
        # Get message details and sort by date (newest first)
        messages_with_dates = []
        for message in messages:
            try:
                # Get basic message details for sorting
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload'].get('headers', [])
                date_header = next((h['value'] for h in headers if h['name'] == 'Date'), None)
                parsed_date = parse_email_date(date_header)
                
                messages_with_dates.append({
                    'message': message,
                    'msg_details': msg,
                    'date': parsed_date or datetime.min  # Use minimum date if parsing fails
                })
            except Exception as e:
                print(f"Warning: Error getting date for message {message['id']}: {e}")
                # Keep message but with minimum date so it goes to end
                messages_with_dates.append({
                    'message': message,
                    'msg_details': None,
                    'date': datetime.min
                })
        
        # Sort by date (newest first)
        messages_with_dates.sort(key=lambda x: x['date'], reverse=True)
        
        print(f"Sorted {len(messages_with_dates)} emails by date (newest first)")
        
        # Analyze emails
        emails_to_delete = []
        emails_to_keep = []
        
        # Store email details with timestamps for verification
        email_details = []
        
        for idx, msg_data in enumerate(messages_with_dates, 1):
            try:
                message = msg_data['message']
                msg = msg_data['msg_details']
                parsed_date = msg_data['date']
                
                # If we don't have message details (due to error), try to get them now
                if msg is None:
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()
                
                # Get email details from headers
                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date_header = next((h['value'] for h in headers if h['name'] == 'Date'), None)
                
                # Use the already parsed date
                if parsed_date == datetime.min:
                    parsed_date = parse_email_date(date_header)  # Try to parse again
                
                # Extract sender name (before email address)
                sender_name = sender.split('<')[0].strip() if '<' in sender else sender
                
                if not verify_mode:
                    print(f"Analyzing {idx}/{len(messages_with_dates)}: {subject[:60]}...", end='\r')
                else:
                    # In verify mode, show email details immediately
                    date_str = parsed_date.strftime('%Y-%m-%d %H:%M:%S') if parsed_date and parsed_date != datetime.min else 'No date'
                    print(f"{idx:2d}. {subject[:70]:<70} | {date_str}")
                    print(f"    From: {sender_name[:60]}")
                    print()
                
                # Store email details for verification
                email_details.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender_name,
                    'date': parsed_date,
                    'date_str': parsed_date.strftime('%Y-%m-%d %H:%M:%S') if parsed_date and parsed_date != datetime.min else 'No date'
                })
                
                # Skip analysis if in verify mode
                if verify_mode:
                    continue
                
                # First, analyze subject line
                subject_analysis = filter_instance.extract_from_subject(subject)
                
                # Determine if email should be deleted based on same logic as main script
                should_delete = False
                reason = ""
                
                # Check for non-deal keywords first
                if subject_analysis.get('is_non_deal', False):
                    should_delete = True
                    reason = "Non-deal email"
                # Quick decision: if we can definitively decide based on subject alone
                elif subject_analysis['location_state'] and subject_analysis['number_of_units'] is not None:
                    # Convert state abbreviations to full names for comparison
                    state_name = subject_analysis['location_state']
                    if state_name == "CA":
                        state_name = "California"
                    elif state_name == "AZ":
                        state_name = "Arizona"
                    elif state_name == "NM":
                        state_name = "New Mexico"
                    
                    if state_name not in filter_instance.target_states:
                        should_delete = True
                        reason = f"Wrong state: {state_name}"
                    elif subject_analysis['number_of_units'] < filter_instance.minimum_units:
                        should_delete = True
                        reason = f"Too few units: {subject_analysis['number_of_units']}"
                    else:
                        reason = f"{state_name}, {subject_analysis['number_of_units']} units"
                # If it's a land opportunity in target state, keep it
                elif subject_analysis['is_land_opportunity'] and subject_analysis['location_state']:
                    # Convert state abbreviations to full names for comparison
                    state_name = subject_analysis['location_state']
                    if state_name == "CA":
                        state_name = "California"
                    elif state_name == "AZ":
                        state_name = "Arizona"
                    elif state_name == "NM":
                        state_name = "New Mexico"
                    
                    if state_name in filter_instance.target_states:
                        reason = f"Land opportunity in {state_name}"
                    else:
                        should_delete = True
                        reason = f"Wrong state: {state_name}"
                # If it's clearly in a wrong state, delete it
                elif subject_analysis['location_state']:
                    # Convert state abbreviations to full names for comparison
                    state_name = subject_analysis['location_state']
                    if state_name == "CA":
                        state_name = "California"
                    elif state_name == "AZ":
                        state_name = "Arizona"
                    elif state_name == "NM":
                        state_name = "New Mexico"
                    
                    if state_name not in filter_instance.target_states:
                        should_delete = True
                        reason = f"Wrong state: {state_name}"
                else:
                    # Need to analyze body - get email text
                    email_text = filter_instance.get_email_text(msg['payload'])
                    
                    if not email_text.strip():
                        # No text content, keep for safety
                        reason = "No text content - kept for review"
                    else:
                        # Analyze with Ollama
                        analysis = filter_instance.analyze_email_with_ollama(email_text, subject_analysis)
                        
                        # Apply deletion logic
                        if analysis.get('is_non_deal', False):
                            should_delete = True
                            reason = "Non-deal email"
                        elif analysis['location_state']:
                            # Convert state abbreviations to full names for comparison
                            state_name = analysis['location_state']
                            if state_name == "CA":
                                state_name = "California"
                            elif state_name == "AZ":
                                state_name = "Arizona"
                            elif state_name == "NM":
                                state_name = "New Mexico"
                            
                            if state_name not in filter_instance.target_states:
                                should_delete = True
                                reason = f"Wrong state: {state_name}"
                            elif analysis['number_of_units'] is not None and analysis['number_of_units'] < filter_instance.minimum_units and not analysis['is_land_opportunity']:
                                should_delete = True
                                reason = f"Too few units: {analysis['number_of_units']}"
                            elif analysis['number_of_units'] and analysis['number_of_units'] >= filter_instance.minimum_units:
                                reason = f"{state_name}, {analysis['number_of_units']} units"
                            else:
                                reason = f"{state_name} - kept for review"
                        else:
                            reason = "Could not determine - kept for review"
                
                email_info = {
                    'id': message['id'],
                    'subject': subject,
                    'reason': reason,
                    'sender': sender_name,
                    'date': parsed_date,
                    'date_str': parsed_date.strftime('%Y-%m-%d %H:%M:%S') if parsed_date and parsed_date != datetime.min else 'No date'
                }
                
                if should_delete:
                    emails_to_delete.append(email_info)
                else:
                    emails_to_keep.append(email_info)
                    
            except Exception as e:
                print(f"\nError processing email: {e}")
                # Keep email if error
                emails_to_keep.append({
                    'id': message['id'],
                    'subject': subject if 'subject' in locals() else 'Unknown',
                    'reason': f"Error: {str(e)}",
                    'sender': sender_name if 'sender_name' in locals() else 'Unknown',
                    'date': None,
                    'date_str': 'No date'
                })
        
        # If in verify mode, exit after showing emails
        if verify_mode:
            print(f"\n🔍 VERIFICATION COMPLETE - Displayed {len(email_details)} emails")
            print("=" * 80)
            print("Next steps:")
            print("1. Compare the emails above with your Gmail visual interface")
            print("2. If they match, the ordering is correct")
            print("3. If not, note which emails are missing or in different positions")
            print("4. Run without --verify to process emails for filtering")
            return
        
        # Clear the progress line
        print(" " * 80, end='\r')
        
        # Show results
        print(f"\n{'=' * 80}")
        print(f"BATCH {batch_number} ANALYSIS COMPLETE")
        print(f"{'=' * 80}")
        print(f"Total emails in batch: {len(messages)}")
        print(f"Emails to DELETE: {len(emails_to_delete)}")
        print(f"Emails to KEEP: {len(emails_to_keep)}")
        
        # Show ALL emails in the batch
        print(f"\n{'=' * 80}")
        print("EMAILS TO BE DELETED:")
        print(f"{'=' * 80}")
        if emails_to_delete:
            for i, email in enumerate(emails_to_delete, 1):
                print(f"{i:3d}. {email['subject']}")
                print(f"     Reason: {email['reason']}")
        else:
            print("     (None)")
        
        print(f"\n{'=' * 80}")
        print("EMAILS TO BE KEPT:")
        print(f"{'=' * 80}")
        if emails_to_keep:
            for i, email in enumerate(emails_to_keep, 1):
                print(f"{i:3d}. {email['subject']}")
                print(f"     Reason: {email['reason']}")
        else:
            print("     (None)")
        
        if emails_to_delete:
            print(f"\n{'=' * 80}")
            print("OPTIONS:")
            print("1. Type 'DELETE' to delete all listed emails")
            print("2. Type 'KEEP' followed by numbers to keep specific emails (e.g., 'KEEP 3,5,12')")
            print("3. Type 'SKIP' to skip this batch and continue to next")
            print("4. Type 'QUIT' to stop processing")
            print(f"{'=' * 80}")
            
            while True:
                choice = input("\nYour choice: ").strip().upper()
                
                if choice == 'DELETE':
                    # Delete all emails
                    print("\nDeleting emails...")
                    deleted_count = 0
                    for email in emails_to_delete:
                        try:
                            service.users().messages().trash(
                                userId='me',
                                id=email['id']
                            ).execute()
                            deleted_count += 1
                            print(f"✓ Deleted: {email['subject'][:60]}...")
                        except Exception as e:
                            print(f"✗ Error deleting {email['subject'][:40]}: {e}")
                    print(f"\n✓ Successfully deleted {deleted_count} emails")
                    break
                    
                elif choice.startswith('KEEP'):
                    # Parse which emails to keep
                    try:
                        keep_nums = [int(x.strip()) for x in choice.replace('KEEP', '').split(',') if x.strip()]
                        
                        # Remove kept emails from deletion list
                        kept_emails = []
                        for num in keep_nums:
                            if 1 <= num <= len(emails_to_delete):
                                kept_email = emails_to_delete[num-1]
                                kept_emails.append(kept_email)
                                print(f"✓ KEEPING #{num}: {kept_email['subject'][:60]}...")
                        
                        # Remove kept emails from deletion list
                        for kept in kept_emails:
                            emails_to_delete.remove(kept)
                        
                        if emails_to_delete:
                            confirm = input(f"\nConfirm deletion of {len(emails_to_delete)} emails? (y/n): ").strip().lower()
                            if confirm == 'y':
                                print("\nDeleting emails...")
                                deleted_count = 0
                                for email in emails_to_delete:
                                    try:
                                        service.users().messages().delete(
                                            userId='me',
                                            id=email['id']
                                        ).execute()
                                        deleted_count += 1
                                        print(f"✓ Deleted: {email['subject'][:60]}...")
                                    except Exception as e:
                                        print(f"✗ Error deleting {email['subject'][:40]}: {e}")
                                print(f"\n✓ Successfully deleted {deleted_count} emails")
                        break
                    except:
                        print("Invalid format. Use 'KEEP 3,5,12' format")
                        
                elif choice == 'SKIP':
                    print("Skipping this batch...")
                    break
                    
                elif choice == 'QUIT':
                    print("Stopping batch processing...")
                    continue_processing = False
                    break
                    
                else:
                    print("Invalid choice. Please try again.")
        
        else:
            print("\nNo emails to delete in this batch!")
        
        if continue_processing and 'choice' in locals() and choice != 'QUIT':
            # Check if there are more emails
            if next_page_token:
                batch_number += 1
                # Automatically continue to next batch
                print(f"\n{'=' * 80}")
                print(f"Moving to batch {batch_number}...")
            else:
                print("\nNo more emails to process!")
                continue_processing = False
    
    print(f"\n{'=' * 80}")
    print("BATCH PROCESSING COMPLETE")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    # Add parent directory to path to import the main script
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Email Deal Filter - Batch Processing')
    parser.add_argument('--verify', action='store_true', 
                       help='Verification mode: show first 15 emails to compare with Gmail interface')
    args = parser.parse_args()
    
    run_batch_filtering(verify_mode=args.verify)
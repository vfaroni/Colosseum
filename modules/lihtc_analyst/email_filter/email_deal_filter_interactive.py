import base64
import email
import json
import requests
import logging
import pickle
import os
from email.header import decode_header
from datetime import datetime
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/vitorfaroni/Documents/Automation/Email Deal Filter/filter_log.txt'),
        logging.StreamHandler()
    ]
)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class EmailDealFilterInteractive:
    def __init__(self):
        self.email_address = "vitor@synergycdc.org"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.target_states = ["California", "Arizona", "New Mexico"]
        self.minimum_units = 50
        self.credentials_file = '/Users/vitorfaroni/Documents/Automation/Email Deal Filter/credentials.json'
        self.token_file = '/Users/vitorfaroni/Documents/Automation/Email Deal Filter/token.pickle'
        
    def authenticate_gmail(self):
        """Authenticate with Gmail using OAuth2"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logging.error(f"Credentials file not found: {self.credentials_file}")
                    logging.error("Please download credentials.json from Google Cloud Console")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            service = build('gmail', 'v1', credentials=creds)
            logging.info(f"Successfully authenticated with Gmail API")
            return service
        except Exception as e:
            logging.error(f"Failed to build Gmail service: {e}")
            return None
    
    def analyze_email_with_ollama(self, email_text):
        """Use Ollama Llama 3.1 to analyze email content"""
        prompt = f"""Analyze the following real estate deal email and extract ONLY the following information in JSON format:
1. location_state (full state name where the property is located)
2. number_of_units (total number of units as an integer)

Return ONLY a JSON object with these two fields. If you cannot determine either value, use null.

Email content:
{email_text}"""
        
        payload = {
            "model": "llama3.1",
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            analysis_text = result.get('response', '{}')
            
            # Parse the JSON response
            try:
                analysis = json.loads(analysis_text)
                return analysis
            except json.JSONDecodeError:
                # Try to extract JSON from response if it's wrapped in text
                json_match = re.search(r'\{[^}]+\}', analysis_text)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    logging.warning(f"Could not parse Ollama response: {analysis_text}")
                    return {"location_state": None, "number_of_units": None}
                    
        except Exception as e:
            logging.error(f"Error calling Ollama: {e}")
            return {"location_state": None, "number_of_units": None}
    
    def should_delete_email(self, analysis):
        """Determine if email should be deleted based on criteria"""
        location_state = analysis.get('location_state')
        number_of_units = analysis.get('number_of_units')
        
        delete_reasons = []
        
        # Check location (only delete if we can confirm it's NOT in target states)
        if location_state and location_state not in self.target_states:
            delete_reasons.append(f"Location is {location_state}, not in CA, AZ, or NM")
        
        # Check unit count (only delete if we can confirm it's less than minimum)
        if number_of_units is not None and number_of_units < self.minimum_units:
            delete_reasons.append(f"Only {number_of_units} units, less than {self.minimum_units} minimum")
        
        # If we couldn't determine location or units, don't delete (fail-safe)
        if location_state is None and number_of_units is None:
            return False, "Could not analyze email content"
        
        should_delete = len(delete_reasons) > 0
        return should_delete, "; ".join(delete_reasons)
    
    def get_email_text(self, payload):
        """Extract text content from Gmail API message payload"""
        text = ""
        
        def extract_text_from_part(part):
            """Recursively extract text from message parts"""
            nonlocal text
            
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_text_from_part(subpart)
            else:
                mime_type = part.get('mimeType', '')
                if mime_type == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        text += decoded
                elif mime_type == 'text/html' and not text:
                    data = part['body'].get('data', '')
                    if data:
                        decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        # Basic HTML stripping
                        text += re.sub('<[^<]+?>', '', decoded)
        
        extract_text_from_part(payload)
        return text
    
    def display_email_batch(self, emails, batch_num, total_batches):
        """Display a batch of emails and get user selection"""
        print(f"\n{'='*80}")
        print(f"BATCH {batch_num} of {total_batches} - EMAILS RECOMMENDED FOR DELETION")
        print(f"{'='*80}")
        
        for i, email in enumerate(emails, 1):
            print(f"\n{i:2d}. Subject: {email['subject'][:70]}...")
            print(f"    From: {email['sender'][:60]}")
            print(f"    Date: {email['date']}")
            print(f"    Location: {email.get('location_state', 'Unknown')}")
            print(f"    Units: {email.get('number_of_units', 'Unknown')}")
            print(f"    Reason: {email['reason']}")
        
        print(f"\n{'='*80}")
        print("SELECTION OPTIONS:")
        print("- Enter numbers to KEEP (e.g., '1,3,5' or '1-5,8,10')")
        print("- Enter 'all' to KEEP all emails in this batch")
        print("- Enter 'none' to DELETE all emails in this batch")
        print("- Enter 'quit' to stop processing")
        
        while True:
            selection = input(f"\nWhich emails do you want to KEEP from batch {batch_num}? ").strip().lower()
            
            if selection == 'quit':
                return 'quit', []
            elif selection == 'all':
                return 'keep', list(range(len(emails)))
            elif selection == 'none':
                return 'delete', []
            else:
                try:
                    # Parse the selection
                    keep_indices = []
                    parts = selection.split(',')
                    
                    for part in parts:
                        part = part.strip()
                        if '-' in part:
                            # Range like "1-5"
                            start, end = map(int, part.split('-'))
                            keep_indices.extend(range(start-1, end))  # Convert to 0-based
                        else:
                            # Single number
                            keep_indices.append(int(part) - 1)  # Convert to 0-based
                    
                    # Validate indices
                    valid_indices = [i for i in keep_indices if 0 <= i < len(emails)]
                    if len(valid_indices) != len(keep_indices):
                        print("Some numbers were out of range. Please try again.")
                        continue
                    
                    return 'partial', valid_indices
                    
                except ValueError:
                    print("Invalid input. Please enter numbers, ranges, 'all', 'none', or 'quit'.")
                    continue
    
    def process_emails(self, batch_size=50):
        """Main function to process emails in Deal Announcements folder"""
        service = self.authenticate_gmail()
        if not service:
            return
        
        try:
            # Search for emails in the Deal Announcements folder
            query = 'in:"INBOX/Deal Announcements"'
            results = service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            logging.info(f"Found {len(messages)} emails in Deal Announcements folder")
            
            if not messages:
                logging.info("No emails found in Deal Announcements folder")
                return
            
            print(f"Found {len(messages)} emails in Deal Announcements folder")
            print("Analyzing emails with Llama 3.1...")
            
            # Analyze all emails first
            all_emails = []
            for i, message in enumerate(messages, 1):
                try:
                    print(f"Analyzing email {i}/{len(messages)}...", end='\r')
                    
                    # Get full message
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()
                    
                    # Get email details from headers
                    headers = msg['payload'].get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                    date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
                    
                    # Extract email text
                    email_text = self.get_email_text(msg['payload'])
                    
                    if not email_text.strip():
                        # Keep emails with no text content
                        continue
                    
                    # Analyze with Ollama
                    analysis = self.analyze_email_with_ollama(email_text)
                    
                    # Determine if should delete
                    should_delete, reason = self.should_delete_email(analysis)
                    
                    if should_delete:
                        email_info = {
                            'id': message['id'],
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'location_state': analysis.get('location_state'),
                            'number_of_units': analysis.get('number_of_units'),
                            'reason': reason
                        }
                        all_emails.append(email_info)
                        
                except Exception as e:
                    logging.error(f"Error processing email {message['id']}: {e}")
                    continue
            
            print(f"\nAnalysis complete! Found {len(all_emails)} emails recommended for deletion.")
            
            if not all_emails:
                print("No emails meet the deletion criteria.")
                return
            
            # Process emails in batches
            emails_to_actually_delete = []
            batch_num = 1
            total_batches = (len(all_emails) + batch_size - 1) // batch_size
            
            for i in range(0, len(all_emails), batch_size):
                batch = all_emails[i:i + batch_size]
                
                action, keep_indices = self.display_email_batch(batch, batch_num, total_batches)
                
                if action == 'quit':
                    print("Processing stopped by user.")
                    break
                elif action == 'keep':
                    print(f"Keeping all {len(batch)} emails from batch {batch_num}")
                elif action == 'delete':
                    emails_to_actually_delete.extend(batch)
                    print(f"Will delete all {len(batch)} emails from batch {batch_num}")
                elif action == 'partial':
                    # Add emails NOT in keep_indices to deletion list
                    for j, email in enumerate(batch):
                        if j not in keep_indices:
                            emails_to_actually_delete.append(email)
                    
                    kept_count = len(keep_indices)
                    delete_count = len(batch) - kept_count
                    print(f"Will keep {kept_count} and delete {delete_count} emails from batch {batch_num}")
                
                batch_num += 1
            
            # Final confirmation and deletion
            if emails_to_actually_delete:
                print(f"\n{'='*80}")
                print(f"FINAL SUMMARY")
                print(f"{'='*80}")
                print(f"Total emails analyzed: {len(messages)}")
                print(f"Emails recommended for deletion: {len(all_emails)}")
                print(f"Emails you chose to DELETE: {len(emails_to_actually_delete)}")
                print(f"Emails you chose to KEEP: {len(all_emails) - len(emails_to_actually_delete)}")
                
                final_confirm = input(f"\nProceed to DELETE {len(emails_to_actually_delete)} emails? Type 'DELETE' to confirm: ")
                
                if final_confirm == 'DELETE':
                    print("Deleting emails...")
                    for i, email in enumerate(emails_to_actually_delete, 1):
                        try:
                            service.users().messages().trash(userId='me', id=email['id']).execute()
                            print(f"Deleted {i}/{len(emails_to_actually_delete)}: {email['subject'][:50]}...")
                            logging.info(f"DELETED: {email['subject']}")
                        except Exception as e:
                            logging.error(f"Error deleting email {email['id']}: {e}")
                    
                    print(f"\nSuccessfully moved {len(emails_to_actually_delete)} emails to trash!")
                else:
                    print("Deletion cancelled by user.")
            else:
                print("No emails selected for deletion.")
            
        except Exception as e:
            logging.error(f"Error processing emails: {e}")

def main():
    filter_tool = EmailDealFilterInteractive()
    
    print("Email Deal Filter - Interactive Mode")
    print("This will analyze all emails and let you choose which ones to delete.")
    
    confirm = input("Do you want to continue? (y/n): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("Operation cancelled")
        return
    
    filter_tool.process_emails(batch_size=50)

if __name__ == "__main__":
    main()
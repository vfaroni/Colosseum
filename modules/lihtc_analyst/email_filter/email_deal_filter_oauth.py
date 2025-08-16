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

class EmailDealFilterOAuth:
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
            logging.info("Could not determine location or unit count - keeping email for manual review")
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
    
    def get_folder_id(self, service, folder_name):
        """Get the folder ID for 'Deal Announcements' folder"""
        try:
            # List all labels to find the folder
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Look for the Deal Announcements folder
            for label in labels:
                if 'Deal Announcements' in label['name']:
                    logging.info(f"Found folder: {label['name']} (ID: {label['id']})")
                    return label['id']
            
            # If not found, list all labels for debugging
            logging.error("Deal Announcements folder not found. Available labels:")
            for label in labels:
                logging.info(f"  - {label['name']} (ID: {label['id']})")
            
            return None
            
        except Exception as e:
            logging.error(f"Error getting folder ID: {e}")
            return None
    
    def process_emails(self, dry_run=True):
        """Main function to process emails in Deal Announcements folder"""
        service = self.authenticate_gmail()
        if not service:
            return
        
        try:
            # Get the folder ID for Deal Announcements
            folder_id = self.get_folder_id(service, "Deal Announcements")
            if not folder_id:
                logging.error("Could not find Deal Announcements folder")
                return
            
            # Search for emails in the Deal Announcements folder
            # Use the folder name directly as Gmail API doesn't work well with nested label IDs
            query = 'in:"INBOX/Deal Announcements"'
            results = service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            logging.info(f"Found {len(messages)} emails in Deal Announcements folder")
            
            if not messages:
                logging.info("No emails found in Deal Announcements folder")
                return
            
            # Store emails to delete for review
            emails_to_delete = []
            emails_to_keep = []
            
            # First pass: analyze all emails
            for message in messages:
                try:
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
                        logging.warning(f"No text content found in email: {subject}")
                        emails_to_keep.append({
                            'id': message['id'],
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'reason': 'No text content to analyze'
                        })
                        continue
                    
                    # Analyze with Ollama
                    logging.info(f"Analyzing email: {subject[:50]}...")
                    analysis = self.analyze_email_with_ollama(email_text)
                    
                    # Determine if should delete
                    should_delete, reason = self.should_delete_email(analysis)
                    
                    email_info = {
                        'id': message['id'],
                        'subject': subject,
                        'sender': sender,
                        'date': date,
                        'location_state': analysis.get('location_state'),
                        'number_of_units': analysis.get('number_of_units'),
                        'reason': reason
                    }
                    
                    if should_delete:
                        emails_to_delete.append(email_info)
                    else:
                        emails_to_keep.append(email_info)
                        
                except Exception as e:
                    logging.error(f"Error processing email {message['id']}: {e}")
                    emails_to_keep.append({
                        'id': message['id'],
                        'subject': 'Error reading email',
                        'sender': 'Unknown',
                        'date': 'Unknown',
                        'reason': f'Error: {e}'
                    })
            
            # Display summary
            print(f"\n=== EMAIL ANALYSIS SUMMARY ===")
            print(f"Total emails found: {len(messages)}")
            print(f"Emails to DELETE: {len(emails_to_delete)}")
            print(f"Emails to KEEP: {len(emails_to_keep)}")
            
            # Show emails to be deleted
            if emails_to_delete:
                print(f"\n=== EMAILS TO BE DELETED ({len(emails_to_delete)}) ===")
                for i, email in enumerate(emails_to_delete, 1):
                    print(f"{i}. Subject: {email['subject'][:60]}...")
                    print(f"   From: {email['sender']}")
                    print(f"   Date: {email['date']}")
                    print(f"   Location: {email.get('location_state', 'Unknown')}")
                    print(f"   Units: {email.get('number_of_units', 'Unknown')}")
                    print(f"   Reason: {email['reason']}")
                    print("")
            
            # Show emails to be kept (first 5 for brevity)
            if emails_to_keep:
                print(f"\n=== EMAILS TO BE KEPT (showing first 5 of {len(emails_to_keep)}) ===")
                for i, email in enumerate(emails_to_keep[:5], 1):
                    print(f"{i}. Subject: {email['subject'][:60]}...")
                    print(f"   Location: {email.get('location_state', 'Unknown')}")
                    print(f"   Units: {email.get('number_of_units', 'Unknown')}")
                    print("")
            
            # If not dry run, confirm deletion
            if not dry_run and emails_to_delete:
                confirm = input(f"\nProceed to delete {len(emails_to_delete)} emails? Type 'DELETE' to confirm: ")
                if confirm != 'DELETE':
                    print("Deletion cancelled")
                    return
                
                # Actually delete the emails
                for email in emails_to_delete:
                    service.users().messages().trash(userId='me', id=email['id']).execute()
                    logging.info(f"DELETED: {email['subject']}")
                
                print(f"Successfully moved {len(emails_to_delete)} emails to trash")
            
            elif dry_run:
                print(f"\n[DRY RUN] Would delete {len(emails_to_delete)} emails")
            
            logging.info(f"Processing complete. To delete: {len(emails_to_delete)}, To keep: {len(emails_to_keep)}")
            
        except Exception as e:
            logging.error(f"Error processing emails: {e}")

def main():
    filter_tool = EmailDealFilterOAuth()
    
    # Ask if this is a dry run
    dry_run_input = input("Run in dry-run mode? (y/n): ").lower().strip()
    dry_run = dry_run_input in ['y', 'yes', '']
    
    if dry_run:
        print("Running in DRY RUN mode - no emails will be deleted")
    else:
        confirm = input("Are you sure you want to DELETE emails? Type 'DELETE' to confirm: ")
        if confirm != 'DELETE':
            print("Operation cancelled")
            return
    
    filter_tool.process_emails(dry_run=dry_run)

if __name__ == "__main__":
    main()
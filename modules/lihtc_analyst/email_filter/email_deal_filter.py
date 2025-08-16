import imaplib
import email
import json
import requests
import logging
from email.header import decode_header
from datetime import datetime
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/vitorfaroni/Documents/Automation/Email Deal Filter/filter_log.txt'),
        logging.StreamHandler()
    ]
)

class EmailDealFilter:
    def __init__(self):
        self.email_address = "vitor@synergycdc.org"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.target_states = ["California", "Arizona", "New Mexico"]
        self.minimum_units = 50
        
    def connect_to_email(self, password):
        """Connect to email account via IMAP"""
        try:
            # Connect to Gmail IMAP server
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.email_address, password)
            logging.info(f"Successfully connected to {self.email_address}")
            return mail
        except Exception as e:
            logging.error(f"Failed to connect to email: {e}")
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
    
    def get_email_text(self, msg):
        """Extract text content from email message"""
        text = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True)
                    if body:
                        text += body.decode('utf-8', errors='ignore')
                elif content_type == "text/html" and "attachment" not in content_disposition and not text:
                    body = part.get_payload(decode=True)
                    if body:
                        # Basic HTML stripping
                        html_text = body.decode('utf-8', errors='ignore')
                        text += re.sub('<[^<]+?>', '', html_text)
        else:
            body = msg.get_payload(decode=True)
            if body:
                text = body.decode('utf-8', errors='ignore')
        
        return text
    
    def process_emails(self, password, dry_run=True):
        """Main function to process emails in Deal Announcements folder"""
        mail = self.connect_to_email(password)
        if not mail:
            return
        
        try:
            # Select the Deal Announcements folder
            status, folders = mail.list()
            logging.info("Available folders:")
            for folder in folders:
                logging.info(folder.decode())
            
            # Try to select the Deal Announcements folder
            folder_name = '"INBOX/Deal Announcements"'
            status, messages = mail.select(folder_name)
            
            if status != 'OK':
                logging.error(f"Could not select folder {folder_name}")
                return
            
            # Get all email IDs
            status, email_ids = mail.search(None, 'ALL')
            email_id_list = email_ids[0].split()
            
            logging.info(f"Found {len(email_id_list)} emails in {folder_name}")
            
            # Store emails to delete for review
            emails_to_delete = []
            emails_to_keep = []
            
            # First pass: analyze all emails
            for email_id in email_id_list:
                try:
                    # Fetch email
                    status, email_data = mail.fetch(email_id, '(RFC822)')
                    email_message = email.message_from_bytes(email_data[0][1])
                    
                    # Get email details
                    subject = decode_header(email_message["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()
                    
                    sender = email_message["From"]
                    date = email_message["Date"]
                    
                    # Extract email text
                    email_text = self.get_email_text(email_message)
                    
                    if not email_text.strip():
                        logging.warning(f"No text content found in email: {subject}")
                        emails_to_keep.append({
                            'id': email_id,
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
                        'id': email_id,
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
                    logging.error(f"Error processing email {email_id}: {e}")
                    emails_to_keep.append({
                        'id': email_id,
                        'subject': 'Error reading email',
                        'sender': 'Unknown',
                        'date': 'Unknown',
                        'reason': f'Error: {e}'
                    })
            
            # Display summary
            print(f"\n=== EMAIL ANALYSIS SUMMARY ===")
            print(f"Total emails found: {len(email_id_list)}")
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
                    mail.store(email['id'], '+FLAGS', '\\Deleted')
                    logging.info(f"DELETED: {email['subject']}")
                
                # Expunge deleted emails
                mail.expunge()
                print(f"Successfully deleted {len(emails_to_delete)} emails")
            
            elif dry_run:
                print(f"\n[DRY RUN] Would delete {len(emails_to_delete)} emails")
            
            logging.info(f"Processing complete. To delete: {len(emails_to_delete)}, To keep: {len(emails_to_keep)}")
            
        except Exception as e:
            logging.error(f"Error processing emails: {e}")
        finally:
            mail.close()
            mail.logout()

def main():
    filter_tool = EmailDealFilter()
    
    # Get password securely
    import getpass
    password = getpass.getpass(f"Enter password for {filter_tool.email_address}: ")
    
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
    
    filter_tool.process_emails(password, dry_run=dry_run)

if __name__ == "__main__":
    main()
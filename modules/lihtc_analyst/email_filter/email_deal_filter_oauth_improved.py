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
from bs4 import BeautifulSoup
from urllib.parse import urlparse

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

# Gmail API scopes - mail.google.com scope required for deletion
SCOPES = ['https://mail.google.com/']

class EmailDealFilterOAuth:
    def __init__(self):
        self.email_address = "vitor@synergycdc.org"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.target_states = ["California", "Arizona", "New Mexico"]
        self.target_states_abbrev = ["CA", "AZ", "NM"]
        self.minimum_units = 50
        self.credentials_file = '/Users/vitorfaroni/Documents/Automation/Email Deal Filter/credentials.json'
        self.token_file = '/Users/vitorfaroni/Documents/Automation/Email Deal Filter/token.pickle'
        
        # Simple cache for subject analysis to avoid re-analyzing similar subjects
        self.subject_cache = {}
        
        # Common state abbreviations and city mappings
        self.state_abbrev_map = {
            "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
            "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
            "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
            "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
            "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
            "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
            "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
            "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
            "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
            "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
            "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
            "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
            "WI": "Wisconsin", "WY": "Wyoming"
        }
        
        # Common keywords indicating land/development opportunities
        self.land_keywords = [
            "development site", "land opportunity", "developable land", "entitled land",
            "zoned for", "du/ac", "units per acre", "density", "future development",
            "ground-up", "build-to-suit", "raw land", "vacant land", "assemblage"
        ]
        
        # Keywords indicating non-deal emails (should be deleted)
        self.non_deal_keywords = [
            "homebuyer workshop", "workshop", "seminar", "webinar", "conference",
            "training", "educational", "news", "enews", "newsletter", "update",
            "statement", "invoice", "payment",
            "marketing", "advertisement", "promotion", "survey", "feedback",
            "just closed", "recently financed", "recent closing", "recently closed",
            "just financed", "recent financing", "closing announcement", "deal closed",
            "transaction closed", "financing completed", "loan closed",
            # NEW: "Just sold" and related sale completion keywords
            "just sold", "recently sold", "sale completed", "transaction completed"
        ]
        
        # Common city to state mappings
        self.city_state_map = {
            # Texas cities
            "houston": "Texas", "austin": "Texas", "dallas": "Texas", "san antonio": "Texas",
            "fort worth": "Texas", "el paso": "Texas", "arlington": "Texas", "plano": "Texas",
            # California cities (all with 30,000+ population)
            "los angeles": "California", "san diego": "California", "san jose": "California",
            "san francisco": "California", "fresno": "California", "sacramento": "California",
            "long beach": "California", "oakland": "California", "bakersfield": "California",
            "anaheim": "California", "stockton": "California", "riverside": "California",
            "santa ana": "California", "irvine": "California", "chula vista": "California",
            "fremont": "California", "san bernardino": "California", "modesto": "California",
            "fontana": "California", "oxnard": "California", "moreno valley": "California",
            "glendale": "California", "huntington beach": "California", "santa clarita": "California",
            "garden grove": "California", "santa rosa": "California", "oceanside": "California",
            "rancho cucamonga": "California", "ontario": "California", "lancaster": "California",
            "elk grove": "California", "palmdale": "California", "corona": "California",
            "salinas": "California", "pomona": "California", "escondido": "California",
            "torrance": "California", "hayward": "California", "pasadena": "California",
            "orange": "California", "fullerton": "California", "thousand oaks": "California",
            "visalia": "California", "simi valley": "California", "concord": "California",
            "roseville": "California", "santa clara": "California", "vallejo": "California",
            "victorville": "California", "el monte": "California", "berkeley": "California",
            "downey": "California", "costa mesa": "California", "carlsbad": "California",
            "fairfield": "California", "richmond": "California", "ventura": "California",
            "temecula": "California", "antioch": "California", "murrieta": "California",
            "burbank": "California", "daly city": "California", "san mateo": "California",
            "clovis": "California", "jurupa valley": "California", "compton": "California",
            "rialto": "California", "vista": "California", "south gate": "California",
            "mission viejo": "California", "carson": "California", "santa monica": "California",
            "westminster": "California", "redding": "California", "santa barbara": "California",
            "chico": "California", "newport beach": "California", "san leandro": "California",
            "san marcos": "California", "citrus heights": "California", "hawthorne": "California",
            "alhambra": "California", "tracy": "California", "livermore": "California",
            "buena park": "California", "lakewood": "California", "merced": "California",
            "hemet": "California", "chino": "California", "menifee": "California",
            "lake forest": "California", "napa": "California", "redwood city": "California",
            "bellflower": "California", "indio": "California", "tustin": "California",
            "baldwin park": "California", "chino hills": "California", "mountain view": "California",
            "alameda": "California", "upland": "California", "folsom": "California",
            "san ramon": "California", "pleasanton": "California", "lynwood": "California",
            "union city": "California", "apple valley": "California", "redlands": "California",
            "turlock": "California", "perris": "California", "manteca": "California",
            "milpitas": "California", "redondo beach": "California", "davis": "California",
            "camarillo": "California", "yuba city": "California", "rancho cordova": "California",
            "palo alto": "California", "yorba linda": "California", "walnut creek": "California",
            "south san francisco": "California", "san clemente": "California", "pittsburg": "California",
            "laguna niguel": "California", "pico rivera": "California", "montebello": "California",
            "lodi": "California", "glendale": "California", "porterville": "California",
            "norwalk": "California", "san luis obispo": "California", "el cajon": "California",
            "danville": "California", "encinitas": "California", "rohnert park": "California",
            "national city": "California", "huntington park": "California", "la mesa": "California",
            "brentwood": "California", "fountain valley": "California", "arcadia": "California",
            "diamond bar": "California", "woodland": "California", "santee": "California",
            "lake elsinore": "California", "cathedral city": "California", "palm desert": "California",
            "west covina": "California", "aliso viejo": "California", "la habra": "California",
            "glendora": "California", "cerritos": "California", "san rafael": "California",
            "palm springs": "California", "petaluma": "California", "covina": "California",
            "azusa": "California", "la puente": "California", "rancho santa margarita": "California",
            "cypress": "California", "dublin": "California", "lincoln": "California",
            "colton": "California", "culver city": "California", "rosemead": "California",
            # Additional cities mentioned in emails
            "rocklin": "California", "carmichael": "California", "encino": "California",
            "placerville": "California", "coachella": "California", "hollywood": "California",
            "beverly hills": "California", "west hollywood": "California",
            "van nuys": "California", "silver lake": "California", "valley village": "California",
            # Arizona cities
            "phoenix": "Arizona", "tucson": "Arizona", "scottsdale": "Arizona",
            "mesa": "Arizona", "chandler": "Arizona", "glendale": "Arizona",
            "tempe": "Arizona", "gilbert": "Arizona", "peoria": "Arizona",
            "bullhead city": "Arizona", "flagstaff": "Arizona", "yuma": "Arizona",
            # New Mexico cities
            "albuquerque": "New Mexico", "santa fe": "New Mexico", "las cruces": "New Mexico",
            "rio rancho": "New Mexico", "roswell": "New Mexico",
            # Other states
            "des moines": "Iowa", "worcester": "Massachusetts", "boston": "Massachusetts",
            "richmond": "Virginia", "arlington heights": "Illinois", "chicago": "Illinois",
            "denver": "Colorado", "colorado springs": "Colorado", "covington": "Kentucky"
        }
        
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
    
    def extract_from_subject(self, subject):
        """Extract location and unit count directly from subject line"""
        # Check cache first
        if subject in self.subject_cache:
            return self.subject_cache[subject]
        
        location_state = None
        number_of_units = None
        is_land_opportunity = False
        is_non_deal = False
        
        # Check for non-deal keywords first (workshops, newsletters, etc.)
        subject_lower = subject.lower()
        for keyword in self.non_deal_keywords:
            if keyword in subject_lower:
                is_non_deal = True
                break
        
        # Check for land/development keywords
        for keyword in self.land_keywords:
            if keyword in subject_lower:
                is_land_opportunity = True
                break
        
        # Extract state from subject
        # First check for known city names
        for city, state in self.city_state_map.items():
            if city in subject_lower:
                location_state = state
                break
        
        # If no city match, check for full state names
        if not location_state:
            for abbrev, full_name in self.state_abbrev_map.items():
                if re.search(rf'\b{full_name}\b', subject, re.IGNORECASE):
                    location_state = full_name
                    break
        
        # If still no match, check for state abbreviations more carefully
        if not location_state:
            for abbrev, full_name in self.state_abbrev_map.items():
                # Match state abbreviations more carefully:
                # - After comma (e.g., "Phoenix, AZ")
                # - At end of string
                # - Before dash or hyphen
                patterns = [
                    rf',\s*{abbrev}\b',  # After comma
                    rf'\b{abbrev}$',   # At end of string  
                    rf'\b{abbrev}\s*[-–—]',  # Before dash
                    rf'\bin\s+{abbrev}\b',  # After "in"
                    rf'\s+{abbrev}\s+(?:with|near)',  # Before "with" or "near"
                ]
                for pattern in patterns:
                    if re.search(pattern, subject, re.IGNORECASE):
                        location_state = full_name
                        break
                if location_state:
                    break
        
        # Extract unit count from subject
        # Look for patterns like "6-Unit", "10 units", "150-unit", etc.
        unit_patterns = [
            r'(\d+)\s*-?\s*[Uu]nits?\b',
            r'(\d+)\s*[Uu]nit\b',
            r'(\d+)\s*[Aa]partments?\b',
            r'(\d+)\s*[Dd]oors?\b',
            r'(\d+)\s*[Bb]eds?\b',
            r'(\d+)\s*[Rr]esidential\s*[Uu]nits?\b'
        ]
        
        for pattern in unit_patterns:
            match = re.search(pattern, subject)
            if match:
                number_of_units = int(match.group(1))
                break
        
        # Check for property types that indicate specific unit counts
        property_type_units = {
            'duplex': 2,
            'triplex': 3,
            'fourplex': 4,
            'quadplex': 4,
            '4-plex': 4,
            '4plex': 4
        }
        
        if not number_of_units:
            for prop_type, units in property_type_units.items():
                if prop_type in subject_lower:
                    number_of_units = units
                    break
        
        # Don't count density (DU/Ac) as unit count for land opportunities
        if is_land_opportunity and re.search(r'(\d+)\s*DU/Ac', subject, re.IGNORECASE):
            number_of_units = None  # This is density, not actual unit count
        
        result = {
            'location_state': location_state,
            'number_of_units': number_of_units,
            'is_land_opportunity': is_land_opportunity,
            'is_non_deal': is_non_deal
        }
        
        # Cache the result
        self.subject_cache[subject] = result
        return result
    
    def analyze_email_with_ollama(self, email_text, subject_analysis):
        """Use Ollama Llama 3.1 to analyze email content - only when subject analysis is insufficient"""
        # Skip Ollama if we have sufficient info from subject OR if it's clearly a land opportunity
        if (subject_analysis['location_state'] and subject_analysis['number_of_units'] is not None) or \
           (subject_analysis['is_land_opportunity'] and subject_analysis['location_state']):
            return subject_analysis
        
        # Quick text-based analysis before using Ollama
        email_lower = email_text.lower()
        
        # Try to find state in email body if not found in subject
        if not subject_analysis['location_state']:
            for city, state in self.city_state_map.items():
                if city in email_lower:
                    subject_analysis['location_state'] = state
                    break
        
        # Try to find unit count in email body if not found in subject
        if subject_analysis['number_of_units'] is None:
            unit_patterns = [
                r'(\d+)\s*[-\s]*units?\b',
                r'(\d+)\s*[-\s]*unit\b',
                r'(\d+)\s*apartments?\b',
                r'(\d+)\s*doors?\b'
            ]
            for pattern in unit_patterns:
                match = re.search(pattern, email_lower)
                if match:
                    subject_analysis['number_of_units'] = int(match.group(1))
                    break
        
        # If we now have sufficient info, return it
        if subject_analysis['location_state'] and subject_analysis['number_of_units'] is not None:
            return subject_analysis
        
        # Only use Ollama as last resort for unclear cases
        prompt = f"""Extract location_state and number_of_units from this email. Return JSON only:
{email_text[:1000]}"""  # Limit text length for speed
        
        payload = {
            "model": "llama3.1",
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
                "num_predict": 100  # Limit response length
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=30)  # Reduced timeout
            response.raise_for_status()
            
            result = response.json()
            analysis_text = result.get('response', '{}')
            
            try:
                analysis = json.loads(analysis_text)
                return {
                    'location_state': analysis.get('location_state') or subject_analysis['location_state'],
                    'number_of_units': analysis.get('number_of_units') if analysis.get('number_of_units') is not None else subject_analysis['number_of_units'],
                    'is_land_opportunity': analysis.get('is_land_opportunity', subject_analysis['is_land_opportunity']),
                    'is_non_deal': subject_analysis.get('is_non_deal', False)
                }
            except json.JSONDecodeError:
                json_match = re.search(r'\{[^}]+\}', analysis_text)
                if json_match:
                    parsed = json.loads(json_match.group())
                    return {
                        'location_state': parsed.get('location_state') or subject_analysis['location_state'],
                        'number_of_units': parsed.get('number_of_units') if parsed.get('number_of_units') is not None else subject_analysis['number_of_units'],
                        'is_land_opportunity': parsed.get('is_land_opportunity', subject_analysis['is_land_opportunity']),
                        'is_non_deal': subject_analysis.get('is_non_deal', False)
                    }
                else:
                    return subject_analysis
                    
        except Exception as e:
            logging.warning(f"Ollama failed, using subject analysis: {e}")
            return subject_analysis
    
    def should_delete_email(self, analysis):
        """Determine if email should be deleted based on criteria"""
        location_state = analysis.get('location_state')
        number_of_units = analysis.get('number_of_units')
        is_land_opportunity = analysis.get('is_land_opportunity', False)
        is_non_deal = analysis.get('is_non_deal', False)
        
        delete_reasons = []
        
        # Check if it's a non-deal email (workshops, newsletters, etc.) - DELETE these
        if is_non_deal:
            delete_reasons.append("Non-deal email (workshop, newsletter, etc.)")
        
        # Check location (only delete if we can confirm it's NOT in target states)
        # Handle both full state names and abbreviations
        if location_state:
            # Convert abbreviations to full names for comparison
            if location_state == "CA":
                location_state = "California"
            elif location_state == "AZ":
                location_state = "Arizona"
            elif location_state == "NM":
                location_state = "New Mexico"
            
            if location_state not in self.target_states:
                delete_reasons.append(f"Location is {location_state}, not in CA, AZ, or NM")
        
        # Check unit count (only delete if we can confirm it's less than minimum)
        # Don't apply unit count criteria to land opportunities
        if not is_land_opportunity and number_of_units is not None and number_of_units < self.minimum_units:
            delete_reasons.append(f"Only {number_of_units} units, less than {self.minimum_units} minimum")
        
        # If we couldn't determine location or units AND it's not a non-deal email, don't delete (fail-safe)
        if not is_non_deal and location_state is None and number_of_units is None:
            logging.info("Could not determine location or unit count - keeping email for manual review")
            return False, "Could not analyze email content"
        
        should_delete = len(delete_reasons) > 0
        return should_delete, "; ".join(delete_reasons) if delete_reasons else "Meets criteria"
    
    def get_email_text(self, payload):
        """Extract text content from Gmail API message payload - optimized for speed"""
        text = ""
        html_content = ""
        
        def extract_content_from_part(part):
            """Recursively extract text and HTML from message parts"""
            nonlocal text, html_content
            
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_content_from_part(subpart)
            else:
                mime_type = part.get('mimeType', '')
                data = part['body'].get('data', '')
                
                if data:
                    try:
                        decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        
                        if mime_type == 'text/plain':
                            text += decoded
                        elif mime_type == 'text/html':
                            html_content += decoded
                    except:
                        # Skip if decoding fails
                        pass
        
        extract_content_from_part(payload)
        
        # If we have plain text, use it (faster)
        if text.strip():
            return text
        
        # Only parse HTML if no plain text available
        if html_content:
            try:
                # Fast HTML stripping using regex (much faster than BeautifulSoup)
                text = re.sub(r'<[^>]+>', ' ', html_content)
                text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                return text.strip()
            except:
                # Fallback to BeautifulSoup only if regex fails
                try:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    return soup.get_text(separator=' ', strip=True)
                except:
                    return ""
        
        return ""
    
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
    
    def process_emails(self, dry_run=True, batch_size=50):
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
            query = 'in:"INBOX/Deal Announcements"'
            
            # Get all emails in batches
            all_emails_to_delete = []
            all_emails_to_keep = []
            next_page_token = None
            batch_number = 1
            total_processed = 0
            total_deleted = 0
            
            while True:
                # Get batch of emails
                if next_page_token:
                    results = service.users().messages().list(
                        userId='me', 
                        q=query, 
                        maxResults=batch_size,
                        pageToken=next_page_token
                    ).execute()
                else:
                    results = service.users().messages().list(
                        userId='me', 
                        q=query, 
                        maxResults=batch_size
                    ).execute()
                
                messages = results.get('messages', [])
                next_page_token = results.get('nextPageToken')
                
                if not messages:
                    break
                
                print(f"\n=== PROCESSING BATCH {batch_number} ({len(messages)} emails) ===")
                logging.info(f"Processing batch {batch_number}: {len(messages)} emails")
                
                # Store emails to delete for review
                emails_to_delete = []
                emails_to_keep = []
            
                # Process emails in this batch
                for i, message in enumerate(messages):
                    try:
                        # Get full message
                        msg = service.users().messages().get(userId='me', id=message['id']).execute()
                        
                        # Get email details from headers
                        headers = msg['payload'].get('headers', [])
                        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
                        
                        logging.info(f"Processing {total_processed + i + 1}: {subject[:50]}...")
                        
                        # First, analyze subject line
                        subject_analysis = self.extract_from_subject(subject)
                        
                        # Quick decision: if we can definitively delete based on subject alone, do it
                        if subject_analysis['location_state'] and subject_analysis['number_of_units'] is not None:
                            analysis = subject_analysis
                            analysis_source = 'subject'
                            logging.info(f"Got sufficient info from subject: State={analysis['location_state']}, Units={analysis['number_of_units']}")
                        # If it's a land opportunity in target state, keep it
                        elif subject_analysis['is_land_opportunity'] and subject_analysis['location_state'] and subject_analysis['location_state'] in self.target_states:
                            analysis = subject_analysis
                            analysis_source = 'subject'
                            logging.info(f"Land opportunity in target state: {subject_analysis['location_state']}")
                        # If it's clearly in a wrong state, delete it
                        elif subject_analysis['location_state'] and subject_analysis['location_state'] not in self.target_states:
                            analysis = subject_analysis
                            analysis_source = 'subject'
                            logging.info(f"Wrong state from subject: {subject_analysis['location_state']}")
                        else:
                            # Only analyze body if subject analysis is insufficient
                            email_text = self.get_email_text(msg['payload'])
                            
                            if not email_text.strip():
                                logging.warning(f"No text content found in email: {subject}")
                                analysis = subject_analysis  # Use what we got from subject
                                analysis_source = 'subject'
                            else:
                                # Analyze with Ollama/regex, passing subject analysis as context
                                analysis = self.analyze_email_with_ollama(email_text, subject_analysis)
                                analysis_source = 'body'
                        
                        # Determine if should delete
                        should_delete, reason = self.should_delete_email(analysis)
                        
                        email_info = {
                            'id': message['id'],
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'location_state': analysis.get('location_state'),
                            'number_of_units': analysis.get('number_of_units'),
                            'is_land_opportunity': analysis.get('is_land_opportunity', False),
                            'is_non_deal': analysis.get('is_non_deal', False),
                            'reason': reason,
                            'analysis_source': analysis_source
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
                            'reason': f'Error: {e}',
                            'analysis_source': 'error'
                        })
                
                # Add batch results to overall results
                all_emails_to_delete.extend(emails_to_delete)
                all_emails_to_keep.extend(emails_to_keep)
                total_processed += len(messages)
                
                # Show batch summary
                print(f"Batch {batch_number} complete: {len(emails_to_delete)} to delete, {len(emails_to_keep)} to keep")
                
                # If not dry run and we have emails to delete in this batch, confirm deletion
                if not dry_run and emails_to_delete:
                    batch_deleted = self.confirm_and_delete_batch(
                        service, emails_to_delete, batch_number, total_processed
                    )
                    total_deleted += batch_deleted
                
                # Move to next batch
                batch_number += 1
                
                # If no more pages, break
                if not next_page_token:
                    break
            
            # Display final summary
            print(f"\n=== FINAL SUMMARY ===")
            print(f"Total emails processed: {total_processed}")
            if not dry_run:
                print(f"Total emails DELETED: {total_deleted}")
            else:
                print(f"Total emails to DELETE: {len(all_emails_to_delete)}")
            print(f"Total emails to KEEP: {len(all_emails_to_keep)}")
            
            # In dry run mode, show what would be deleted
            if dry_run and all_emails_to_delete:
                print(f"\n=== DRY RUN: EMAILS THAT WOULD BE DELETED ({len(all_emails_to_delete)}) ===")
                for i, email in enumerate(all_emails_to_delete, 1):
                    subject = email['subject']
                    print(f"{i}. {subject}")
            
            logging.info(f"Processing complete. To delete: {len(all_emails_to_delete)}, To keep: {len(all_emails_to_keep)}")
            
        except Exception as e:
            logging.error(f"Error processing emails: {e}")
    
    def confirm_and_delete_batch(self, service, emails_to_delete, batch_number, total_processed):
        """Confirm and delete emails for a single batch"""
        print(f"\n{'='*80}")
        print(f"BATCH {batch_number} DELETION CONFIRMATION")
        print(f"{'='*80}")
        print(f"Ready to delete {len(emails_to_delete)} emails from this batch.")
        print(f"\nREVIEW: Here are the emails that will be deleted:")
        print(f"{'='*80}")
        
        # Show numbered list for easy reference
        for i, email in enumerate(emails_to_delete, 1):
            subject = email['subject']
            if len(subject) > 100:
                subject = subject[:97] + "..."
            print(f"{i:3d}. {subject}")
        
        print(f"\n{'='*80}")
        print(f"OPTIONS:")
        print(f"1. Type 'DELETE' to delete all {len(emails_to_delete)} emails in this batch")
        print(f"2. Type 'KEEP' followed by numbers to keep specific emails (e.g., 'KEEP 3,5,12')")
        print(f"3. Type 'CANCEL' to skip this batch")
        print(f"4. Type 'STOP' to stop processing entirely")
        print(f"{'='*80}")
        
        user_input = input(f"\nYour choice: ").strip()
        
        if user_input.upper() == 'DELETE':
            # Delete all emails in batch
            emails_to_actually_delete = emails_to_delete
            print(f"\nProceeding to delete all {len(emails_to_actually_delete)} emails...")
            
        elif user_input.upper().startswith('KEEP'):
            # Parse which emails to keep
            try:
                keep_part = user_input[4:].strip()  # Remove 'KEEP' prefix
                if keep_part:
                    keep_numbers = [int(x.strip()) for x in keep_part.split(',')]
                    # Remove emails to keep from deletion list
                    emails_to_actually_delete = []
                    kept_emails = []
                    
                    for i, email in enumerate(emails_to_delete, 1):
                        if i in keep_numbers:
                            kept_emails.append(email)
                            print(f"✓ KEEPING #{i}: {email['subject']}")
                        else:
                            emails_to_actually_delete.append(email)
                    
                    print(f"\nKept {len(kept_emails)} emails, will delete {len(emails_to_actually_delete)} emails")
                    
                    if emails_to_actually_delete:
                        confirm = input(f"\nConfirm deletion of {len(emails_to_actually_delete)} emails? (y/n): ")
                        if confirm.lower() not in ['y', 'yes']:
                            print("Batch deletion cancelled")
                            return 0
                    else:
                        print("No emails to delete after keeping selected ones")
                        return 0
                else:
                    print("No numbers specified after KEEP. Skipping this batch.")
                    return 0
            except ValueError:
                print("Invalid format. Please use 'KEEP 1,2,3' format. Skipping this batch.")
                return 0
                
        elif user_input.upper() == 'CANCEL':
            print("Skipping this batch")
            return 0
        elif user_input.upper() == 'STOP':
            print("Stopping email processing")
            raise KeyboardInterrupt()
        else:
            print("Invalid option. Skipping this batch.")
            return 0
        
        # Actually delete the emails
        deleted_count = 0
        print("\n=== DELETING EMAILS ===")
        for i, email in enumerate(emails_to_actually_delete, 1):
            try:
                service.users().messages().trash(userId='me', id=email['id']).execute()
                logging.info(f"DELETED: {email['subject']}")
                deleted_count += 1
                print(f"✓ DELETED #{i}: {email['subject']}")
                
            except Exception as e:
                logging.error(f"Failed to delete {email['subject']}: {e}")
                print(f"✗ FAILED #{i}: {email['subject']}")
        
        print(f"\n=== BATCH {batch_number} DELETION COMPLETE ===")
        print(f"Successfully moved {deleted_count} emails to trash")
        return deleted_count

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
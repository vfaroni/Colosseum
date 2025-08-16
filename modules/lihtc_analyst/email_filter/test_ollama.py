import json
import requests
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class OllamaEmailTester:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.target_states = ["California", "Arizona", "New Mexico"]
        self.minimum_units = 50
        
        # Sample email data for testing
        self.sample_emails = [
            {
                "subject": "New Deal Alert: 120 Units in Phoenix, AZ - Prime Location",
                "from": "deals@realestate.com",
                "content": """
                Investment Opportunity Alert
                
                Property: Sunset Gardens Apartments
                Location: Phoenix, Arizona
                Units: 120 residential units
                Price: $15,000,000
                
                This property features modern amenities and is located in a growing area of Phoenix.
                Contact us for more details.
                """
            },
            {
                "subject": "Small Property Deal - 25 Units in Sacramento",
                "from": "properties@invest.com", 
                "content": """
                Quick Sale Opportunity
                
                Property: Oak Street Apartments
                Location: Sacramento, California
                Total Units: 25
                Asking Price: $3,500,000
                
                Well-maintained property in established neighborhood.
                """
            },
            {
                "subject": "Luxury Development - 200 Units in Dallas, Texas",
                "from": "luxury@developments.com",
                "content": """
                Premium Investment Opportunity
                
                Development: Dallas Heights
                Location: Dallas, Texas
                Units: 200 luxury apartments
                Price: $45,000,000
                
                State-of-the-art amenities, prime Dallas location.
                Expected completion Q2 2024.
                """
            },
            {
                "subject": "Value-Add Opportunity: 75 Units in Los Angeles",
                "from": "valueadd@realty.com",
                "content": """
                Value-Add Investment
                
                Property: Westside Manor
                Location: Los Angeles, California  
                Unit Count: 75 apartments
                Purchase Price: $22,000,000
                
                Excellent opportunity for repositioning in growing LA market.
                """
            },
            {
                "subject": "New Mexico Opportunity - 30 Units in Albuquerque",
                "from": "southwest@properties.com",
                "content": """
                Southwest Investment
                
                Property: Desert View Apartments
                Location: Albuquerque, New Mexico
                Number of Units: 30
                Price: $4,200,000
                
                Growing market with strong rental demand.
                """
            }
        ]
    
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
            print(f"Calling Ollama API at {self.ollama_url}...")
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            analysis_text = result.get('response', '{}')
            
            print(f"Raw Ollama response: {analysis_text}")
            
            # Parse the JSON response
            try:
                analysis = json.loads(analysis_text)
                return analysis
            except json.JSONDecodeError:
                # Try to extract JSON from response if it's wrapped in text
                import re
                json_match = re.search(r'\{[^}]+\}', analysis_text)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    print(f"Could not parse Ollama response: {analysis_text}")
                    return {"location_state": None, "number_of_units": None}
                    
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to Ollama. Make sure Ollama is running with 'ollama run llama3.1'")
            return {"location_state": None, "number_of_units": None}
        except Exception as e:
            print(f"Error calling Ollama: {e}")
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
    
    def test_analysis(self):
        """Test Ollama analysis on sample emails"""
        print("=== TESTING OLLAMA EMAIL ANALYSIS ===\n")
        
        emails_to_delete = []
        emails_to_keep = []
        
        for i, email in enumerate(self.sample_emails, 1):
            print(f"--- Testing Email {i} ---")
            print(f"Subject: {email['subject']}")
            print(f"From: {email['from']}")
            print(f"Content Preview: {email['content'][:100]}...")
            print()
            
            # Analyze with Ollama
            analysis = self.analyze_email_with_ollama(email['content'])
            print(f"Analysis Result: {analysis}")
            
            # Determine if should delete
            should_delete, reason = self.should_delete_email(analysis)
            
            email_info = {
                'subject': email['subject'],
                'from': email['from'],
                'location_state': analysis.get('location_state'),
                'number_of_units': analysis.get('number_of_units'),
                'reason': reason
            }
            
            if should_delete:
                emails_to_delete.append(email_info)
                print(f"✗ WOULD DELETE: {reason}")
            else:
                emails_to_keep.append(email_info)
                print(f"✓ WOULD KEEP: {reason}")
            
            print("-" * 50)
            print()
        
        # Display summary
        print(f"\n=== TEST RESULTS SUMMARY ===")
        print(f"Total emails tested: {len(self.sample_emails)}")
        print(f"Emails to DELETE: {len(emails_to_delete)}")
        print(f"Emails to KEEP: {len(emails_to_keep)}")
        
        # Show emails to be deleted
        if emails_to_delete:
            print(f"\n=== EMAILS TO BE DELETED ({len(emails_to_delete)}) ===")
            for i, email in enumerate(emails_to_delete, 1):
                print(f"{i}. Subject: {email['subject']}")
                print(f"   Location: {email.get('location_state', 'Unknown')}")
                print(f"   Units: {email.get('number_of_units', 'Unknown')}")
                print(f"   Reason: {email['reason']}")
                print("")
        
        # Show emails to be kept
        if emails_to_keep:
            print(f"\n=== EMAILS TO BE KEPT ({len(emails_to_keep)}) ===")
            for i, email in enumerate(emails_to_keep, 1):
                print(f"{i}. Subject: {email['subject']}")
                print(f"   Location: {email.get('location_state', 'Unknown')}")
                print(f"   Units: {email.get('number_of_units', 'Unknown')}")
                print(f"   Reason: {email['reason']}")
                print("")

def main():
    tester = OllamaEmailTester()
    
    # Check if Ollama is running
    try:
        test_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if test_response.status_code == 200:
            print("✓ Ollama is running")
            models = test_response.json().get('models', [])
            llama_models = [m for m in models if 'llama3.1' in m.get('name', '')]
            if llama_models:
                print(f"✓ Llama 3.1 model found: {llama_models[0]['name']}")
            else:
                print("⚠ Llama 3.1 model not found. Run 'ollama pull llama3.1' first")
                return
        else:
            print("✗ Ollama is not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Ollama is not running. Start it with 'ollama run llama3.1'")
        return
    
    # Run the test
    tester.test_analysis()

if __name__ == "__main__":
    main()
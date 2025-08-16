#!/usr/bin/env python3
"""
Email Webhook Processor for Zapier Integration
Receives email data from Zapier webhook and processes with Claude Code
"""

import json
import os
import requests
import subprocess
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify
from pathlib import Path

app = Flask(__name__)

# Configuration
CLICKUP_API_TOKEN = os.getenv('CLICKUP_API_TOKEN')  # Set this in your environment
CLICKUP_LIST_ID = os.getenv('CLICKUP_LIST_ID')      # Your ClickUp list ID for email tasks
EMAIL_LOG_PATH = Path(__file__).parent / "email_logs"
EMAIL_LOG_PATH.mkdir(exist_ok=True)

class EmailProcessor:
    def __init__(self):
        self.clickup_headers = {
            'Authorization': f'Bearer {CLICKUP_API_TOKEN}',
            'Content-Type': 'application/json'
        }
    
    def analyze_email_with_claude(self, email_data):
        """Use Claude Code to analyze email importance and extract action items"""
        prompt = f"""
        Analyze this email for LIHTC business importance and follow-up needs:

        SENDER: {email_data.get('sender', 'Unknown')}
        SUBJECT: {email_data.get('subject', 'No Subject')}
        BODY: {email_data.get('body', 'No Body')[:2000]}  # Limit body length
        DATE: {email_data.get('date', 'Unknown')}

        Context: This is from Bill Rice's Synergy CDC email focused on LIHTC/affordable housing development, 
        CTCAC applications, and real estate analysis.

        Please analyze and respond with JSON format:
        {{
            "priority": "urgent|high|medium|low",
            "category": "ctcac_deadline|client_urgent|deal_opportunity|vendor_response|regulatory|general",
            "action_required": true/false,
            "deadline_mentioned": "date or null",
            "follow_up_needed": "description",
            "clickup_title": "concise task title",
            "clickup_description": "detailed task description with key points",
            "tags": ["relevant", "tags", "here"]
        }}
        """
        
        # Create temporary file with prompt
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            temp_file = f.name
        
        try:
            # Use Claude Code CLI to analyze
            result = subprocess.run([
                'claude', '--model', 'claude-sonnet-4-20250514', 
                '--file', temp_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Extract JSON from Claude's response
                response_text = result.stdout
                # Find JSON in response (Claude might add explanatory text)
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    return json.loads(json_str)
                else:
                    # Fallback parsing
                    return self.fallback_analysis(email_data)
            else:
                print(f"Claude Code error: {result.stderr}")
                return self.fallback_analysis(email_data)
                
        except Exception as e:
            print(f"Analysis error: {e}")
            return self.fallback_analysis(email_data)
        finally:
            os.unlink(temp_file)
    
    def fallback_analysis(self, email_data):
        """Basic rule-based analysis if Claude fails"""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        sender = email_data.get('sender', '').lower()
        
        # Determine priority based on keywords
        if any(word in subject + body for word in ['urgent', 'deadline', 'ctcac', 'application due']):
            priority = "urgent"
        elif any(word in subject + body for word in ['important', 'lihtc', 'deal', 'opportunity']):
            priority = "high" 
        else:
            priority = "medium"
        
        # Basic categorization
        if 'ctcac' in subject + body:
            category = "ctcac_deadline"
        elif any(word in sender for word in ['client', 'investor']):
            category = "client_urgent"
        else:
            category = "general"
            
        return {
            "priority": priority,
            "category": category,
            "action_required": True,
            "deadline_mentioned": None,
            "follow_up_needed": "Review email and determine action items",
            "clickup_title": f"Email: {email_data.get('subject', 'No Subject')[:50]}",
            "clickup_description": f"From: {email_data.get('sender')}\n\n{email_data.get('body', '')[:500]}...",
            "tags": ["email-followup", category]
        }
    
    def create_clickup_task(self, analysis, email_data):
        """Create ClickUp task based on analysis"""
        if not CLICKUP_API_TOKEN or not CLICKUP_LIST_ID:
            print("ClickUp credentials not configured")
            return None
            
        # Map priority to ClickUp values
        priority_map = {"urgent": 1, "high": 2, "medium": 3, "low": 4}
        
        task_data = {
            "name": analysis["clickup_title"],
            "description": analysis["clickup_description"],
            "priority": priority_map.get(analysis["priority"], 3),
            "tags": analysis["tags"],
            "custom_fields": [
                {"id": "email_sender", "value": email_data.get('sender', '')},
                {"id": "email_date", "value": email_data.get('date', '')},
                {"id": "priority_level", "value": analysis["priority"]}
            ]
        }
        
        try:
            response = requests.post(
                f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task",
                headers=self.clickup_headers,
                json=task_data
            )
            
            if response.status_code == 200:
                task = response.json()
                print(f"Created ClickUp task: {task['id']}")
                return task
            else:
                print(f"ClickUp API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"ClickUp task creation error: {e}")
            return None
    
    def log_email(self, email_data, analysis, clickup_task=None):
        """Log email processing for weekly digest"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "email": email_data,
            "analysis": analysis,
            "clickup_task_id": clickup_task.get('id') if clickup_task else None
        }
        
        log_file = EMAIL_LOG_PATH / f"email_log_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Append to daily log file
        logs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

processor = EmailProcessor()

@app.route('/webhook/email', methods=['POST'])
def receive_email():
    """Webhook endpoint for Zapier to send email data"""
    try:
        email_data = request.json
        
        # Validate required fields
        if not email_data or 'subject' not in email_data:
            return jsonify({"error": "Invalid email data"}), 400
        
        print(f"Processing email: {email_data.get('subject')}")
        
        # Analyze email with Claude Code
        analysis = processor.analyze_email_with_claude(email_data)
        
        # Create ClickUp task if action required
        clickup_task = None
        if analysis.get("action_required", False):
            clickup_task = processor.create_clickup_task(analysis, email_data)
        
        # Log for weekly digest
        processor.log_email(email_data, analysis, clickup_task)
        
        return jsonify({
            "status": "success",
            "analysis": analysis,
            "clickup_task_created": clickup_task is not None
        })
        
    except Exception as e:
        print(f"Webhook processing error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting Email Webhook Processor...")
    print(f"Webhook URL: http://localhost:5000/webhook/email")
    print(f"Health check: http://localhost:5000/health")
    
    # Check configuration
    if not CLICKUP_API_TOKEN:
        print("WARNING: CLICKUP_API_TOKEN not set")
    if not CLICKUP_LIST_ID:
        print("WARNING: CLICKUP_LIST_ID not set")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
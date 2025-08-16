#!/usr/bin/env python3
"""
Weekly Email Digest Generator
Processes accumulated email logs and creates summary reports
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class WeeklyDigestGenerator:
    def __init__(self):
        self.email_log_path = Path(__file__).parent / "email_logs"
        self.digest_path = Path(__file__).parent / "weekly_digests"
        self.digest_path.mkdir(exist_ok=True)
    
    def get_weekly_logs(self, days_back=7):
        """Collect all email logs from the past week"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        weekly_logs = []
        
        for day in range(days_back + 1):
            current_date = start_date + timedelta(days=day)
            log_file = self.email_log_path / f"email_log_{current_date.strftime('%Y%m%d')}.json"
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    daily_logs = json.load(f)
                    weekly_logs.extend(daily_logs)
        
        return weekly_logs
    
    def analyze_weekly_patterns(self, logs):
        """Analyze patterns and priorities in weekly emails"""
        stats = {
            "total_emails": len(logs),
            "priority_breakdown": defaultdict(int),
            "category_breakdown": defaultdict(int),
            "action_required": 0,
            "clickup_tasks_created": 0,
            "top_senders": defaultdict(int),
            "urgent_items": [],
            "pending_deadlines": []
        }
        
        for log in logs:
            analysis = log.get('analysis', {})
            email = log.get('email', {})
            
            # Count priorities and categories
            priority = analysis.get('priority', 'unknown')
            category = analysis.get('category', 'unknown')
            stats['priority_breakdown'][priority] += 1
            stats['category_breakdown'][category] += 1
            
            # Track actions and tasks
            if analysis.get('action_required', False):
                stats['action_required'] += 1
            
            if log.get('clickup_task_id'):
                stats['clickup_tasks_created'] += 1
            
            # Track senders
            sender = email.get('sender', 'Unknown')
            stats['top_senders'][sender] += 1
            
            # Collect urgent items
            if priority == 'urgent':
                stats['urgent_items'].append({
                    'subject': email.get('subject', 'No Subject'),
                    'sender': sender,
                    'date': email.get('date', 'Unknown'),
                    'follow_up': analysis.get('follow_up_needed', 'No details')
                })
            
            # Collect items with deadlines
            if analysis.get('deadline_mentioned'):
                stats['pending_deadlines'].append({
                    'subject': email.get('subject', 'No Subject'),
                    'sender': sender,
                    'deadline': analysis.get('deadline_mentioned'),
                    'follow_up': analysis.get('follow_up_needed', 'No details')
                })
        
        return stats
    
    def generate_digest_with_claude(self, stats, logs):
        """Use Claude Code to generate a comprehensive weekly digest"""
        
        # Prepare data for Claude analysis
        digest_prompt = f"""
        Generate a comprehensive weekly email digest for Bill Rice at Synergy CDC.

        WEEKLY EMAIL STATISTICS:
        - Total Emails Processed: {stats['total_emails']}
        - Action Required: {stats['action_required']}
        - ClickUp Tasks Created: {stats['clickup_tasks_created']}

        PRIORITY BREAKDOWN:
        {json.dumps(dict(stats['priority_breakdown']), indent=2)}

        CATEGORY BREAKDOWN:
        {json.dumps(dict(stats['category_breakdown']), indent=2)}

        TOP EMAIL SENDERS:
        {json.dumps(dict(list(stats['top_senders'].items())[:10]), indent=2)}

        URGENT ITEMS REQUIRING IMMEDIATE ATTENTION:
        {json.dumps(stats['urgent_items'], indent=2)}

        PENDING DEADLINES:
        {json.dumps(stats['pending_deadlines'], indent=2)}

        Context: This is for a LIHTC/affordable housing development business focusing on 
        CTCAC applications, Texas TDHCA deals, and real estate analysis.

        Please create a professional weekly digest with:
        1. Executive Summary (2-3 sentences)
        2. Priority Action Items (urgent tasks that need immediate attention)
        3. Upcoming Deadlines (chronologically ordered)
        4. Business Intelligence (patterns, key contacts, deal flow)
        5. Recommendations for next week's focus

        Format as markdown for easy reading.
        """
        
        # Create temporary file with prompt
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(digest_prompt)
            temp_file = f.name
        
        try:
            # Use Claude Code to generate digest
            result = subprocess.run([
                'claude', '--model', 'claude-sonnet-4-20250514', 
                '--file', temp_file
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"Claude Code error: {result.stderr}")
                return self.generate_basic_digest(stats)
                
        except Exception as e:
            print(f"Digest generation error: {e}")
            return self.generate_basic_digest(stats)
        finally:
            os.unlink(temp_file)
    
    def generate_basic_digest(self, stats):
        """Fallback basic digest if Claude fails"""
        digest = f"""
# Weekly Email Digest - {datetime.now().strftime('%B %d, %Y')}

## Summary
- **Total Emails**: {stats['total_emails']}
- **Action Required**: {stats['action_required']}
- **Tasks Created**: {stats['clickup_tasks_created']}

## Priority Breakdown
{chr(10).join([f"- {k.title()}: {v}" for k, v in stats['priority_breakdown'].items()])}

## Top Senders
{chr(10).join([f"- {k}: {v} emails" for k, v in list(stats['top_senders'].items())[:5]])}

## Urgent Items
{chr(10).join([f"- {item['subject']} (from {item['sender']})" for item in stats['urgent_items'][:5]])}

## Recommendations
- Review urgent items above
- Follow up on pending deadlines
- Consider automating responses to frequent senders
"""
        return digest
    
    def save_digest(self, digest_content):
        """Save the weekly digest to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        digest_file = self.digest_path / f"weekly_digest_{timestamp}.md"
        
        with open(digest_file, 'w') as f:
            f.write(digest_content)
        
        print(f"Weekly digest saved to: {digest_file}")
        return digest_file
    
    def run_weekly_digest(self):
        """Main method to generate and save weekly digest"""
        print("Generating weekly email digest...")
        
        # Collect logs from past week
        logs = self.get_weekly_logs()
        
        if not logs:
            print("No email logs found for the past week")
            return None
        
        print(f"Found {len(logs)} emails to analyze")
        
        # Analyze patterns
        stats = self.analyze_weekly_patterns(logs)
        
        # Generate digest with Claude
        digest_content = self.generate_digest_with_claude(stats, logs)
        
        # Save digest
        digest_file = self.save_digest(digest_content)
        
        return digest_file

def main():
    """Run weekly digest generation"""
    generator = WeeklyDigestGenerator()
    digest_file = generator.run_weekly_digest()
    
    if digest_file:
        print(f"\n✅ Weekly digest generated successfully!")
        print(f"📁 Location: {digest_file}")
        print(f"📧 Review action items and follow up on urgent emails")
    else:
        print("❌ No digest generated - check email logs")

if __name__ == '__main__':
    main()
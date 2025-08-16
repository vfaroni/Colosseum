#!/usr/bin/env python3
"""
Opus Research URL Extractor
Extracts QAP URLs from Claude Opus markdown research and populates the state tracking database
"""

import json
import re
from datetime import datetime
from pathlib import Path
from state_qap_url_tracker import StateQAPURLTracker, StateQAPProfile

class OpusURLExtractor:
    """Extract URLs from Opus research markdown and populate tracking database"""
    
    def __init__(self, base_dir: str, research_file: str):
        self.base_dir = Path(base_dir)
        self.research_file = Path(research_file)
        self.tracker = StateQAPURLTracker(base_dir)
        
    def parse_opus_research(self) -> dict:
        """Parse the Opus research markdown file"""
        with open(self.research_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by state sections
        states = {}
        current_state = None
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            # Check for state headers
            if line.startswith('### ') and line.upper() in ['### CALIFORNIA', '### HAWAII', '### NEW MEXICO', 
                                                          '### ARIZONA', '### TEXAS'] or \
               line.startswith('### ') and any(state in line.upper() for state in [
                   'ALABAMA', 'ALASKA', 'ARKANSAS', 'COLORADO', 'CONNECTICUT', 'DELAWARE',
                   'FLORIDA', 'GEORGIA', 'IDAHO', 'ILLINOIS', 'INDIANA', 'IOWA', 'KANSAS',
                   'KENTUCKY', 'LOUISIANA', 'MAINE', 'MARYLAND', 'MASSACHUSETTS', 'MICHIGAN',
                   'MINNESOTA', 'MISSISSIPPI', 'MISSOURI', 'MONTANA', 'NEBRASKA', 'NEVADA',
                   'NEW HAMPSHIRE', 'NEW JERSEY', 'NEW YORK', 'NORTH CAROLINA', 'NORTH DAKOTA',
                   'OHIO', 'OKLAHOMA', 'OREGON', 'PENNSYLVANIA', 'RHODE ISLAND', 'SOUTH CAROLINA',
                   'SOUTH DAKOTA', 'TENNESSEE', 'UTAH', 'VERMONT', 'VIRGINIA', 'WASHINGTON',
                   'WASHINGTON DC', 'WEST VIRGINIA', 'WISCONSIN', 'WYOMING']):
                
                # Save previous state
                if current_state:
                    states[current_state] = '\n'.join(current_content)
                
                # Start new state
                current_state = line.replace('### ', '').strip().upper()
                current_content = []
            else:
                current_content.append(line)
        
        # Save final state
        if current_state:
            states[current_state] = '\n'.join(current_content)
            
        return states
    
    def extract_urls_from_state(self, state_name: str, content: str) -> dict:
        """Extract URLs and metadata from a state's content"""
        # State code mapping
        state_codes = {
            'CALIFORNIA': 'CA', 'HAWAII': 'HI', 'NEW MEXICO': 'NM', 'ARIZONA': 'AZ', 'TEXAS': 'TX',
            'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARKANSAS': 'AR', 'COLORADO': 'CO', 'CONNECTICUT': 'CT',
            'DELAWARE': 'DE', 'FLORIDA': 'FL', 'GEORGIA': 'GA', 'IDAHO': 'ID', 'ILLINOIS': 'IL',
            'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS', 'KENTUCKY': 'KY', 'LOUISIANA': 'LA',
            'MAINE': 'ME', 'MARYLAND': 'MD', 'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN',
            'MISSISSIPPI': 'MS', 'MISSOURI': 'MO', 'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV',
            'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW YORK': 'NY', 'NORTH CAROLINA': 'NC',
            'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK', 'OREGON': 'OR', 'PENNSYLVANIA': 'PA',
            'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC', 'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN',
            'UTAH': 'UT', 'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WASHINGTON DC': 'DC',
            'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 'WYOMING': 'WY'
        }
        
        state_code = state_codes.get(state_name)
        if not state_code:
            return {}
        
        # Extract agency information
        agency_match = re.search(r'\*\*Agency:\*\* (.+?)(?:\n|\r)', content)
        agency_name = agency_match.group(1) if agency_match else ""
        
        website_match = re.search(r'\*\*Website:\*\* (.+?)(?:\n|\r)', content)
        website = website_match.group(1) if website_match else ""
        
        # Extract URLs
        urls = []
        
        # QAP URLs
        qap_urls = re.findall(r'https://[^\s\)]+\.pdf|https://[^\s\)]+QAP[^\s\)]*|https://[^\s\)]+qap[^\s\)]*', content, re.IGNORECASE)
        for url in qap_urls:
            urls.append({
                'url': url.rstrip('.,;'),
                'document_type': 'current',
                'title': 'QAP Document',
                'year': 2025 if '2025' in url else 2024 if '2024' in url else 2025
            })
        
        # Application URLs
        app_urls = re.findall(r'https://[^\s\)]+application[^\s\)]*|https://[^\s\)]+Application[^\s\)]*', content, re.IGNORECASE)
        for url in app_urls:
            urls.append({
                'url': url.rstrip('.,;'),
                'document_type': 'application',
                'title': 'Application Forms',
                'year': 2025
            })
        
        # Awards/results URLs
        award_urls = re.findall(r'https://[^\s\)]+award[^\s\)]*|https://[^\s\)]+Award[^\s\)]*|https://[^\s\)]+result[^\s\)]*', content, re.IGNORECASE)
        for url in award_urls:
            urls.append({
                'url': url.rstrip('.,;'),
                'document_type': 'awards',
                'title': 'Award Information',
                'year': 2025
            })
        
        # Extract all other https URLs
        all_urls = re.findall(r'https://[^\s\)]+', content)
        for url in all_urls:
            clean_url = url.rstrip('.,;')
            # Skip if already captured above
            if not any(existing['url'] == clean_url for existing in urls):
                urls.append({
                    'url': clean_url,
                    'document_type': 'general',
                    'title': 'State Website',
                    'year': 2025
                })
        
        return {
            'state_code': state_code,
            'state_name': state_name.title(),
            'agency_name': agency_name,
            'website': website,
            'urls': urls
        }
    
    def create_enhanced_state_profile(self, state_data: dict) -> StateQAPProfile:
        """Create enhanced state profile from Opus research"""
        return StateQAPProfile(
            state_code=state_data['state_code'],
            state_name=state_data['state_name'],
            agency_name=state_data['agency_name'],
            agency_acronym="",  # Extract from content if available
            qap_base_url=state_data['website'],
            last_checked=datetime.now(),
            checking_frequency_days=30
        )
    
    def populate_tracker(self) -> dict:
        """Populate the tracker with all Opus research data"""
        states_data = self.parse_opus_research()
        results = {
            'processed_states': 0,
            'total_urls': 0,
            'by_type': {},
            'states_processed': []
        }
        
        for state_name, content in states_data.items():
            state_info = self.extract_urls_from_state(state_name, content)
            
            if state_info and state_info['state_code']:
                # Create/update state profile
                profile = self.create_enhanced_state_profile(state_info)
                self.tracker.state_profiles[state_info['state_code']] = profile
                
                # Add URLs to tracker
                for url_data in state_info['urls']:
                    try:
                        self.tracker.add_qap_url(
                            state_code=state_info['state_code'],
                            year=url_data['year'],
                            url=url_data['url'],
                            document_type=url_data['document_type'],
                            title=url_data['title'],
                            notes=f"Discovered from Opus research {datetime.now().strftime('%Y-%m-%d')}"
                        )
                        
                        # Count by type
                        doc_type = url_data['document_type']
                        results['by_type'][doc_type] = results['by_type'].get(doc_type, 0) + 1
                        results['total_urls'] += 1
                        
                    except Exception as e:
                        print(f"Error adding URL for {state_info['state_code']}: {e}")
                
                results['processed_states'] += 1
                results['states_processed'].append(state_info['state_code'])
        
        # Save all data
        self.tracker.save_data()
        
        return results
    
    def generate_summary_report(self) -> str:
        """Generate summary of populated data"""
        reports = self.tracker.generate_tracking_report()
        
        summary = f"""
=== OPUS RESEARCH URL POPULATION SUMMARY ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL STATISTICS:
- States Processed: {len(self.tracker.state_profiles)}
- Total URLs: {len(self.tracker.qap_records)}
- QAP Documents: {len([r for r in self.tracker.qap_records.values() if r.document_type == 'current'])}
- Application Forms: {len([r for r in self.tracker.qap_records.values() if r.document_type == 'application'])}
- Award Information: {len([r for r in self.tracker.qap_records.values() if r.document_type == 'awards'])}
- General URLs: {len([r for r in self.tracker.qap_records.values() if r.document_type == 'general'])}

TOP 10 STATES BY URL COUNT:
"""
        
        # Count URLs by state
        state_counts = {}
        for record in self.tracker.qap_records.values():
            state_counts[record.state_code] = state_counts.get(record.state_code, 0) + 1
        
        top_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        for state, count in top_states:
            profile = self.tracker.state_profiles.get(state)
            agency = profile.agency_name if profile else "Unknown"
            summary += f"- {state}: {count} URLs ({agency})\n"
        
        summary += f"""
DATA STORAGE:
- URL Records: {self.tracker.data_dir / 'qap_url_records.json'}
- State Profiles: {self.tracker.data_dir / 'state_qap_profiles.json'}
- Excel Report: {self.tracker.data_dir / f'qap_tracking_report_{datetime.now().strftime("%Y%m%d")}.xlsx'}

NEXT STEPS:
1. Run download automation with populated URLs
2. Verify URL accuracy for priority states
3. Implement QA system for download completeness
"""
        
        return summary

def main():
    """Extract URLs from Opus research and populate tracker"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    research_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/QAP/_markdown_research/51 State DC QAP Opus Research 07_2025.md"
    
    print("🔍 Starting Opus Research URL Extraction...")
    
    extractor = OpusURLExtractor(base_dir, research_file)
    
    # Populate tracker with all Opus data
    results = extractor.populate_tracker()
    
    print(f"✅ Successfully processed {results['processed_states']} states")
    print(f"📊 Total URLs discovered: {results['total_urls']}")
    print(f"📋 By document type: {results['by_type']}")
    
    # Generate comprehensive summary
    summary = extractor.generate_summary_report()
    print(summary)
    
    # Export summary to file
    summary_file = Path(base_dir) / "QAP" / "_url_tracking" / f"opus_extraction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    print(f"💾 Summary saved to: {summary_file}")
    
    # Update our todo status
    print("🎯 TASK COMPLETED: Extract URLs from Opus research and populate state tracking database")

if __name__ == "__main__":
    main()
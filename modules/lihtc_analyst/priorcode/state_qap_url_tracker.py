#!/usr/bin/env python3
"""
State QAP URL Tracker and Discovery System
Maintains master database of QAP URLs, archives, redlines, and change notices
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
import pandas as pd
import hashlib

@dataclass
class QAPURLRecord:
    """Track QAP document URLs and metadata"""
    state_code: str
    year: int
    document_type: str  # "current", "archive", "redline", "notice"
    url: str
    discovered_date: datetime
    last_verified: datetime
    title: str = ""
    version: str = "final"  # "draft", "final", "amended"
    effective_date: Optional[datetime] = None
    replaces_url: Optional[str] = None  # For tracking document succession
    change_summary: str = ""  # For redlines/amendments
    file_hash: Optional[str] = None
    page_count: Optional[int] = None
    download_status: str = "pending"  # "pending", "downloaded", "failed"
    notes: str = ""

@dataclass 
class StateQAPProfile:
    """Profile of each state's QAP publication patterns"""
    state_code: str
    state_name: str
    agency_name: str
    agency_acronym: str
    
    # URL patterns
    qap_base_url: str = ""
    qap_url_pattern: str = ""  # e.g., "/qap/{year}/final.pdf"
    archive_url: str = ""
    
    # Publication patterns
    typical_release_month: Optional[int] = None  # 1-12
    uses_redlines: bool = False
    posts_draft_first: bool = False
    amendment_frequency: str = "rare"  # "never", "rare", "occasional", "frequent"
    
    # Document formats
    primary_format: str = "pdf"  # "pdf", "html", "docx"
    includes_excel_apps: bool = True
    separate_4pct_qap: bool = False
    
    # Special characteristics
    has_set_asides: bool = True
    rural_set_aside: bool = False
    preservation_priority: bool = False
    state_specific_funds: List[str] = field(default_factory=list)
    
    # Update tracking
    last_checked: Optional[datetime] = None
    checking_frequency_days: int = 30

class StateQAPURLTracker:
    """Master system for tracking and discovering state QAP URLs"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "QAP" / "_url_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize data
        self.load_data()
        
    def load_data(self):
        """Load existing URL tracking data"""
        # Load QAP URL records
        records_file = self.data_dir / "qap_url_records.json"
        if records_file.exists():
            with open(records_file, 'r') as f:
                records_data = json.load(f)
                self.qap_records = {}
                for k, v in records_data.items():
                    # Convert string dates back to datetime objects
                    if isinstance(v.get('discovered_date'), str):
                        v['discovered_date'] = datetime.fromisoformat(v['discovered_date'])
                    if isinstance(v.get('last_verified'), str):
                        v['last_verified'] = datetime.fromisoformat(v['last_verified'])
                    if isinstance(v.get('effective_date'), str):
                        v['effective_date'] = datetime.fromisoformat(v['effective_date'])
                    self.qap_records[k] = QAPURLRecord(**v)
        else:
            self.qap_records = {}
            
        # Load state profiles
        profiles_file = self.data_dir / "state_qap_profiles.json"
        if profiles_file.exists():
            with open(profiles_file, 'r') as f:
                profiles_data = json.load(f)
                self.state_profiles = {}
                for k, v in profiles_data.items():
                    # Convert string dates back to datetime objects
                    if isinstance(v.get('last_checked'), str):
                        v['last_checked'] = datetime.fromisoformat(v['last_checked'])
                    self.state_profiles[k] = StateQAPProfile(**v)
        else:
            self.state_profiles = self.initialize_state_profiles()
            
    def initialize_state_profiles(self) -> Dict[str, StateQAPProfile]:
        """Initialize profiles for all 50 states with known patterns"""
        profiles = {}
        
        # Known state patterns
        state_data = [
            {
                "state_code": "CA",
                "state_name": "California",
                "agency_name": "California Tax Credit Allocation Committee",
                "agency_acronym": "CTCAC",
                "qap_base_url": "https://www.treasurer.ca.gov/ctcac/",
                "archive_url": "https://www.treasurer.ca.gov/ctcac/programreg_archived.asp",
                "typical_release_month": 12,
                "uses_redlines": True,
                "posts_draft_first": True,
                "amendment_frequency": "occasional",
                "includes_excel_apps": True,
                "preservation_priority": True,
                "state_specific_funds": ["CDLAC", "AHSC", "VHHP", "NPLH"]
            },
            {
                "state_code": "TX", 
                "state_name": "Texas",
                "agency_name": "Texas Department of Housing and Community Affairs",
                "agency_acronym": "TDHCA",
                "qap_base_url": "https://www.tdhca.state.tx.us/multifamily/",
                "typical_release_month": 9,
                "uses_redlines": True,
                "posts_draft_first": True,
                "rural_set_aside": True,
                "state_specific_funds": ["HOME", "HTF", "TCAP-RF", "NSP"]
            },
            {
                "state_code": "NY",
                "state_name": "New York",
                "agency_name": "New York State Homes and Community Renewal", 
                "agency_acronym": "HCR",
                "qap_base_url": "https://hcr.ny.gov/",
                "typical_release_month": 6,
                "separate_4pct_qap": True,
                "state_specific_funds": ["SLIHC", "HOME", "HTF", "CIF"]
            },
            {
                "state_code": "FL",
                "state_name": "Florida",
                "agency_name": "Florida Housing Finance Corporation",
                "agency_acronym": "FHFC",
                "qap_base_url": "https://www.floridahousing.org/",
                "typical_release_month": 11,
                "posts_draft_first": True,
                "includes_excel_apps": True,
                "state_specific_funds": ["SAIL", "HOME", "HTF", "CWHIP"]
            },
            {
                "state_code": "NM",
                "state_name": "New Mexico",
                "agency_name": "New Mexico Mortgage Finance Authority",
                "agency_acronym": "MFA",
                "qap_base_url": "https://housingnm.org/",
                "typical_release_month": 10,
                "rural_set_aside": True,
                "state_specific_funds": ["HOME", "HTF", "LIHTF", "NSP"]
            },
            {
                "state_code": "CO",
                "state_name": "Colorado",
                "agency_name": "Colorado Housing and Finance Authority",
                "agency_acronym": "CHFA",
                "qap_base_url": "https://www.chfainfo.com/",
                "typical_release_month": 10,
                "posts_draft_first": True,
                "state_specific_funds": ["HOME", "HTF", "CDBG-DR", "HDG"]
            },
            {
                "state_code": "AZ",
                "state_name": "Arizona",
                "agency_name": "Arizona Department of Housing",
                "agency_acronym": "ADOH",
                "qap_base_url": "https://housing.az.gov/",
                "typical_release_month": 11,
                "rural_set_aside": True,
                "state_specific_funds": ["HOME", "HTF", "AHTF"]
            },
            {
                "state_code": "IL",
                "state_name": "Illinois",
                "agency_name": "Illinois Housing Development Authority",
                "agency_acronym": "IHDA",
                "qap_base_url": "https://www.ihda.org/",
                "typical_release_month": 10,
                "posts_draft_first": True,
                "preservation_priority": True,
                "state_specific_funds": ["HOME", "HTF", "IAHTC", "TCEP"]
            },
            {
                "state_code": "GA",
                "state_name": "Georgia",
                "agency_name": "Georgia Department of Community Affairs",
                "agency_acronym": "DCA",
                "qap_base_url": "https://www.dca.ga.gov/",
                "typical_release_month": 11,
                "rural_set_aside": True,
                "state_specific_funds": ["HOME", "HTF", "GHFA"]
            },
            {
                "state_code": "NC",
                "state_name": "North Carolina",
                "agency_name": "North Carolina Housing Finance Agency",
                "agency_acronym": "NCHFA",
                "qap_base_url": "https://www.nchfa.com/",
                "typical_release_month": 8,
                "posts_draft_first": True,
                "state_specific_funds": ["HOME", "HTF", "WHLP", "RPP"]
            }
            # TODO: Add remaining 40 states
        ]
        
        for state in state_data:
            profile = StateQAPProfile(**state)
            profiles[profile.state_code] = profile
            
        return profiles
        
    def add_qap_url(self, state_code: str, year: int, url: str, 
                    document_type: str = "current", **kwargs) -> str:
        """Add a new QAP URL to tracking"""
        # Generate unique key
        key = f"{state_code}_{year}_{document_type}_{hashlib.md5(url.encode()).hexdigest()[:8]}"
        
        record = QAPURLRecord(
            state_code=state_code,
            year=year,
            document_type=document_type,
            url=url,
            discovered_date=datetime.now(),
            last_verified=datetime.now(),
            **kwargs
        )
        
        self.qap_records[key] = record
        self.save_data()
        
        return key
        
    def update_url_status(self, key: str, status: str, file_hash: Optional[str] = None):
        """Update download status of a URL"""
        if key in self.qap_records:
            self.qap_records[key].download_status = status
            if file_hash:
                self.qap_records[key].file_hash = file_hash
            self.qap_records[key].last_verified = datetime.now()
            self.save_data()
            
    def get_current_qap_url(self, state_code: str) -> Optional[QAPURLRecord]:
        """Get the most recent QAP URL for a state"""
        state_records = [
            record for record in self.qap_records.values()
            if record.state_code == state_code and record.document_type == "current"
        ]
        
        if not state_records:
            return None
            
        # Sort by year descending, then by discovered date
        state_records.sort(key=lambda x: (x.year, x.discovered_date), reverse=True)
        return state_records[0]
        
    def get_state_timeline(self, state_code: str) -> pd.DataFrame:
        """Get timeline of all QAP documents for a state"""
        state_records = [
            record for record in self.qap_records.values()
            if record.state_code == state_code
        ]
        
        if not state_records:
            return pd.DataFrame()
            
        data = []
        for record in state_records:
            data.append({
                'Year': record.year,
                'Type': record.document_type,
                'Version': record.version,
                'Title': record.title,
                'URL': record.url,
                'Discovered': record.discovered_date,
                'Downloaded': record.download_status == 'downloaded',
                'Change Summary': record.change_summary
            })
            
        df = pd.DataFrame(data)
        df = df.sort_values(['Year', 'Type'], ascending=[False, True])
        
        return df
        
    def generate_tracking_report(self) -> Dict[str, pd.DataFrame]:
        """Generate comprehensive tracking report"""
        reports = {}
        
        # Overall status by state
        status_data = []
        for state_code, profile in self.state_profiles.items():
            state_records = [
                r for r in self.qap_records.values() 
                if r.state_code == state_code
            ]
            
            current_qap = self.get_current_qap_url(state_code)
            
            status_data.append({
                'State': state_code,
                'Agency': profile.agency_acronym,
                'Total URLs': len(state_records),
                'Current QAP Year': current_qap.year if current_qap else None,
                'Uses Redlines': profile.uses_redlines,
                'Downloaded': sum(1 for r in state_records if r.download_status == 'downloaded'),
                'Pending': sum(1 for r in state_records if r.download_status == 'pending'),
                'State Funds': ', '.join(profile.state_specific_funds)
            })
            
        reports['status_summary'] = pd.DataFrame(status_data)
        
        # Document type breakdown
        type_data = []
        for doc_type in ['current', 'archive', 'redline', 'notice']:
            type_records = [
                r for r in self.qap_records.values()
                if r.document_type == doc_type
            ]
            
            type_data.append({
                'Document Type': doc_type.title(),
                'Total Count': len(type_records),
                'Downloaded': sum(1 for r in type_records if r.download_status == 'downloaded'),
                'Unique States': len(set(r.state_code for r in type_records))
            })
            
        reports['document_types'] = pd.DataFrame(type_data)
        
        # Recent discoveries
        recent_records = sorted(
            self.qap_records.values(),
            key=lambda x: x.discovered_date,
            reverse=True
        )[:20]
        
        recent_data = []
        for record in recent_records:
            recent_data.append({
                'State': record.state_code,
                'Year': record.year,
                'Type': record.document_type,
                'Discovered': record.discovered_date.strftime('%Y-%m-%d'),
                'Title': record.title[:50] + '...' if len(record.title) > 50 else record.title,
                'Status': record.download_status
            })
            
        reports['recent_discoveries'] = pd.DataFrame(recent_data)
        
        return reports
        
    def save_data(self):
        """Save all tracking data"""
        # Save QAP records
        records_data = {
            k: asdict(v) for k, v in self.qap_records.items()
        }
        with open(self.data_dir / "qap_url_records.json", 'w') as f:
            json.dump(records_data, f, indent=2, default=str)
            
        # Save state profiles
        profiles_data = {
            k: asdict(v) for k, v in self.state_profiles.items()
        }
        with open(self.data_dir / "state_qap_profiles.json", 'w') as f:
            json.dump(profiles_data, f, indent=2, default=str)
            
        # Generate and save Excel report
        reports = self.generate_tracking_report()
        report_path = self.data_dir / f"qap_tracking_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            for sheet_name, df in reports.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
    def export_state_urls(self, state_code: str, output_file: Optional[str] = None) -> str:
        """Export all URLs for a specific state"""
        state_records = [
            record for record in self.qap_records.values()
            if record.state_code == state_code
        ]
        
        if not output_file:
            output_file = self.data_dir / f"{state_code}_qap_urls_{datetime.now().strftime('%Y%m%d')}.json"
        else:
            output_file = Path(output_file)
            
        # Group by year and type
        organized_data = {}
        for record in state_records:
            year = str(record.year)
            if year not in organized_data:
                organized_data[year] = {}
                
            organized_data[year][record.document_type] = {
                'url': record.url,
                'title': record.title,
                'version': record.version,
                'effective_date': record.effective_date.isoformat() if record.effective_date else None,
                'change_summary': record.change_summary,
                'discovered': record.discovered_date.isoformat(),
                'downloaded': record.download_status == 'downloaded'
            }
            
        # Add state profile info
        profile = self.state_profiles.get(state_code)
        output_data = {
            'state_code': state_code,
            'agency_info': asdict(profile) if profile else {},
            'documents_by_year': organized_data,
            'export_date': datetime.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        return str(output_file)

def main():
    """Run the QAP URL tracking system"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    tracker = StateQAPURLTracker(base_dir)
    
    # Example: Add some known URLs
    print("Adding example QAP URLs...")
    
    # California examples
    tracker.add_qap_url(
        state_code="CA",
        year=2024,
        url="https://www.treasurer.ca.gov/ctcac/2024/December_11_2024_QAP_Regulations_FINAL.pdf",
        document_type="current",
        title="2024 QAP Regulations - Final",
        effective_date=datetime(2024, 12, 11)
    )
    
    tracker.add_qap_url(
        state_code="CA",
        year=2024,
        url="https://www.treasurer.ca.gov/ctcac/2024/redline_changes.pdf",
        document_type="redline",
        title="2024 QAP Redline Changes",
        change_summary="Updates to tiebreaker criteria and opportunity area definitions"
    )
    
    # Generate reports
    print("\nGenerating tracking reports...")
    reports = tracker.generate_tracking_report()
    
    for name, df in reports.items():
        print(f"\n{name.replace('_', ' ').title()}:")
        print(df.to_string())
        
    # Export California URLs
    ca_export = tracker.export_state_urls("CA")
    print(f"\nExported California URLs to: {ca_export}")
    
    print(f"\nTracking data saved to: {tracker.data_dir}")

if __name__ == "__main__":
    main()
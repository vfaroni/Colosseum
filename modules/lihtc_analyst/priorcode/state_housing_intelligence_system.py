#!/usr/bin/env python3
"""
Comprehensive State Housing Finance Intelligence System
Collects and processes QAPs, applications, awards, and funding data from all 50 states
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import requests
from urllib.parse import urljoin, urlparse
import logging
from dataclasses import dataclass, field, asdict
from enum import Enum

class DocumentType(Enum):
    QAP_CURRENT = "qap_current"
    QAP_ARCHIVE = "qap_archive"
    QAP_REDLINE = "qap_redline"
    APP_9PCT = "app_9pct"
    APP_4PCT = "app_4pct"
    APP_INSTRUCTIONS = "app_instructions"
    NOTICE = "notice"
    AWARDS = "awards"
    SCORING = "scoring"
    SPECIAL_FUNDS = "special_funds"

class FundType(Enum):
    HOME = "HOME"
    HTF = "HTF"
    CDBG_DR = "CDBG-DR"
    STATE_SOFT_LOAN = "state_soft_loan"
    STATE_GRANT = "state_grant"
    OTHER = "other"

@dataclass
class StateAgencyInfo:
    """Core information about each state housing agency"""
    state_code: str
    state_name: str
    agency_name: str
    agency_acronym: str
    main_website: str
    qap_page_url: Optional[str] = None
    applications_page_url: Optional[str] = None
    awards_page_url: Optional[str] = None
    special_funds_page_url: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: str = ""

@dataclass
class QAPDocument:
    """QAP document tracking"""
    state_code: str
    year: int
    version: str  # "final", "draft", "amended"
    document_type: DocumentType
    url: str
    download_date: Optional[datetime] = None
    file_path: Optional[str] = None
    page_count: Optional[int] = None
    md5_hash: Optional[str] = None
    parent_qap_id: Optional[str] = None  # For redlines/amendments
    notes: str = ""

@dataclass
class ApplicationCycle:
    """Track application cycles and deadlines"""
    state_code: str
    year: int
    round_number: int  # Some states have multiple rounds
    program_type: str  # "9%", "4%", "both"
    pre_app_deadline: Optional[datetime] = None
    pre_app_required: bool = False
    full_app_deadline: Optional[datetime] = None
    award_announcement: Optional[datetime] = None
    total_allocation: Optional[float] = None
    min_score_9pct: Optional[float] = None
    total_apps_received: Optional[int] = None
    total_apps_funded: Optional[int] = None
    notes: str = ""

@dataclass
class ApplicationDocument:
    """Application forms and instructions"""
    state_code: str
    year: int
    document_type: DocumentType
    version: str
    url: str
    download_date: Optional[datetime] = None
    file_path: Optional[str] = None
    excel_tabs: List[str] = field(default_factory=list)  # For Excel apps
    page_count: Optional[int] = None
    notes: str = ""

@dataclass
class AwardRecord:
    """Individual project award tracking"""
    state_code: str
    year: int
    round_number: int
    project_name: str
    developer: str
    city: str
    county: str
    program_type: str  # "9%" or "4%"
    total_units: int
    lihtc_units: int
    credit_amount: float
    final_score: Optional[float] = None
    tiebreaker_1: Optional[str] = None
    tiebreaker_2: Optional[str] = None
    tiebreaker_3: Optional[str] = None
    special_set_aside: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: str = ""

@dataclass
class SpecialFunding:
    """Track additional funding sources"""
    state_code: str
    fund_type: FundType
    fund_name: str
    total_allocation: Optional[float] = None
    per_unit_limit: Optional[float] = None
    per_project_limit: Optional[float] = None
    eligible_with_9pct: bool = True
    eligible_with_4pct: bool = True
    application_url: Optional[str] = None
    guidelines_url: Optional[str] = None
    notes: str = ""

class StateHousingIntelligenceSystem:
    """Master system for collecting and organizing state housing finance data"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "QAP"
        self.data_dir.mkdir(exist_ok=True)
        
        # Create directory structure
        self.dirs = {
            'master': self.data_dir / '_master_data',
            'logs': self.data_dir / '_logs',
            'cache': self.data_dir / '_cache',
            'reports': self.data_dir / '_reports'
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(exist_ok=True)
            
        # Setup logging
        self.setup_logging()
        
        # Initialize state agencies data
        self.state_agencies = self.initialize_state_agencies()
        
        # Load existing data
        self.load_master_data()
        
    def setup_logging(self):
        """Configure logging system"""
        log_file = self.dirs['logs'] / f"housing_intel_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def initialize_state_agencies(self) -> Dict[str, StateAgencyInfo]:
        """Initialize all 50 state housing finance agencies"""
        agencies = {}
        
        # Start with major states - expand to all 50
        state_data = [
            {
                "state_code": "CA",
                "state_name": "California",
                "agency_name": "California Tax Credit Allocation Committee",
                "agency_acronym": "CTCAC",
                "main_website": "https://www.treasurer.ca.gov/ctcac/",
                "qap_page_url": "https://www.treasurer.ca.gov/ctcac/programreg.asp",
                "applications_page_url": "https://www.treasurer.ca.gov/ctcac/application.asp",
                "awards_page_url": "https://www.treasurer.ca.gov/ctcac/projects.asp"
            },
            {
                "state_code": "TX",
                "state_name": "Texas",
                "agency_name": "Texas Department of Housing and Community Affairs",
                "agency_acronym": "TDHCA",
                "main_website": "https://www.tdhca.state.tx.us/",
                "qap_page_url": "https://www.tdhca.state.tx.us/multifamily/htm/",
                "applications_page_url": "https://www.tdhca.state.tx.us/multifamily/apply.htm",
                "awards_page_url": "https://www.tdhca.state.tx.us/multifamily/htm/awards.htm"
            },
            {
                "state_code": "NY",
                "state_name": "New York",
                "agency_name": "New York State Homes and Community Renewal",
                "agency_acronym": "HCR",
                "main_website": "https://hcr.ny.gov/",
                "qap_page_url": "https://hcr.ny.gov/low-income-housing-tax-credit-qualified-allocation-plans",
                "applications_page_url": "https://hcr.ny.gov/multifamily-development"
            },
            {
                "state_code": "FL",
                "state_name": "Florida",
                "agency_name": "Florida Housing Finance Corporation",
                "agency_acronym": "FHFC",
                "main_website": "https://www.floridahousing.org/",
                "qap_page_url": "https://www.floridahousing.org/programs/developers-multifamily-programs/low-income-housing-tax-credit",
                "applications_page_url": "https://www.floridahousing.org/programs/developers-multifamily-programs/competitive"
            },
            {
                "state_code": "NM",
                "state_name": "New Mexico",
                "agency_name": "New Mexico Mortgage Finance Authority",
                "agency_acronym": "MFA",
                "main_website": "https://housingnm.org/",
                "qap_page_url": "https://housingnm.org/developers/low-income-housing-tax-credit-lihtc",
                "special_funds_page_url": "https://housingnm.org/developers/rental-development-funding"
            }
            # TODO: Add remaining 45 states
        ]
        
        for state in state_data:
            agency = StateAgencyInfo(**state)
            agencies[agency.state_code] = agency
            
        return agencies
        
    def create_state_directory_structure(self, state_code: str):
        """Create standardized directory structure for each state"""
        state_dir = self.data_dir / state_code
        
        subdirs = [
            "QAP/current",
            "QAP/archive",
            "QAP/redlines",
            "applications/9pct",
            "applications/4pct",
            "applications/instructions",
            "awards/results",
            "awards/scoring",
            "notices",
            "special_funds",
            "processed/sections",
            "processed/chunks",
            "processed/metadata"
        ]
        
        for subdir in subdirs:
            (state_dir / subdir).mkdir(parents=True, exist_ok=True)
            
        return state_dir
        
    def load_master_data(self):
        """Load existing master data files"""
        self.qap_documents = self.load_json_data("qap_documents.json", {})
        self.application_cycles = self.load_json_data("application_cycles.json", {})
        self.application_documents = self.load_json_data("application_documents.json", {})
        self.award_records = self.load_json_data("award_records.json", {})
        self.special_funding = self.load_json_data("special_funding.json", {})
        self.download_history = self.load_json_data("download_history.json", {})
        
    def load_json_data(self, filename: str, default=None):
        """Load JSON data file with error handling"""
        file_path = self.dirs['master'] / filename
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading {filename}: {e}")
        return default if default is not None else {}
        
    def save_master_data(self):
        """Save all master data files"""
        self.save_json_data("qap_documents.json", self.qap_documents)
        self.save_json_data("application_cycles.json", self.application_cycles)
        self.save_json_data("application_documents.json", self.application_documents)
        self.save_json_data("award_records.json", self.award_records)
        self.save_json_data("special_funding.json", self.special_funding)
        self.save_json_data("download_history.json", self.download_history)
        
        # Also save state agencies data
        agencies_data = {
            code: asdict(agency) for code, agency in self.state_agencies.items()
        }
        self.save_json_data("state_agencies.json", agencies_data)
        
    def save_json_data(self, filename: str, data):
        """Save JSON data file with error handling"""
        file_path = self.dirs['master'] / filename
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            self.logger.info(f"Saved {filename}")
        except Exception as e:
            self.logger.error(f"Error saving {filename}: {e}")
            
    def discover_state_documents(self, state_code: str) -> Dict[str, List[str]]:
        """Discover available documents for a state"""
        agency = self.state_agencies.get(state_code)
        if not agency:
            self.logger.error(f"Unknown state code: {state_code}")
            return {}
            
        discovered = {
            'qap_urls': [],
            'application_urls': [],
            'award_urls': [],
            'notice_urls': [],
            'special_fund_urls': []
        }
        
        # This would be expanded with actual web scraping logic
        # For now, return structure for manual population
        
        self.logger.info(f"Document discovery for {state_code} requires manual URL collection")
        return discovered
        
    def download_document(self, url: str, state_code: str, doc_type: DocumentType, 
                         year: int, version: str = "final") -> Optional[str]:
        """Download and save a document"""
        try:
            # Determine save path based on document type
            type_map = {
                DocumentType.QAP_CURRENT: f"QAP/current",
                DocumentType.QAP_ARCHIVE: f"QAP/archive",
                DocumentType.QAP_REDLINE: f"QAP/redlines",
                DocumentType.APP_9PCT: f"applications/9pct",
                DocumentType.APP_4PCT: f"applications/4pct",
                DocumentType.APP_INSTRUCTIONS: f"applications/instructions",
                DocumentType.NOTICE: f"notices",
                DocumentType.AWARDS: f"awards/results",
                DocumentType.SCORING: f"awards/scoring",
                DocumentType.SPECIAL_FUNDS: f"special_funds"
            }
            
            subdir = type_map.get(doc_type, "other")
            state_dir = self.create_state_directory_structure(state_code)
            save_dir = state_dir / subdir
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"{state_code}_{doc_type.value}_{year}_{version}_{timestamp}"
            
            # Add extension based on URL
            ext = self.get_file_extension(url)
            full_path = save_dir / f"{filename}{ext}"
            
            # Download file
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(full_path, 'wb') as f:
                f.write(response.content)
                
            self.logger.info(f"Downloaded {url} to {full_path}")
            
            # Update download history
            self.download_history[url] = {
                'download_date': datetime.now().isoformat(),
                'file_path': str(full_path),
                'state_code': state_code,
                'doc_type': doc_type.value,
                'year': year,
                'version': version
            }
            
            return str(full_path)
            
        except Exception as e:
            self.logger.error(f"Error downloading {url}: {e}")
            return None
            
    def get_file_extension(self, url: str) -> str:
        """Extract file extension from URL"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        if path.endswith('.pdf'):
            return '.pdf'
        elif path.endswith('.xlsx') or path.endswith('.xls'):
            return '.xlsx'
        elif path.endswith('.docx') or path.endswith('.doc'):
            return '.docx'
        elif path.endswith('.zip'):
            return '.zip'
        else:
            # Default to PDF for most QAP documents
            return '.pdf'
            
    def create_state_summary_report(self, state_code: str) -> Dict:
        """Create comprehensive summary report for a state"""
        summary = {
            'state_code': state_code,
            'agency_info': asdict(self.state_agencies.get(state_code, {})),
            'documents': {
                'qap_count': 0,
                'current_qap_year': None,
                'has_redlines': False,
                'application_forms_count': 0,
                'award_years': []
            },
            'application_cycles': [],
            'special_funds': [],
            'data_quality': {
                'qap_coverage': 0,  # Percentage of years covered
                'award_data_complete': False,
                'special_funds_tracked': False
            }
        }
        
        # Count QAP documents
        state_qaps = [doc for doc in self.qap_documents.values() 
                      if doc.get('state_code') == state_code]
        summary['documents']['qap_count'] = len(state_qaps)
        
        # Find most recent QAP year
        if state_qaps:
            years = [doc.get('year', 0) for doc in state_qaps]
            summary['documents']['current_qap_year'] = max(years)
            
        # Check for redlines
        summary['documents']['has_redlines'] = any(
            doc.get('document_type') == DocumentType.QAP_REDLINE.value 
            for doc in state_qaps
        )
        
        # Add more analysis as data is collected
        
        return summary
        
    def generate_master_status_report(self) -> pd.DataFrame:
        """Generate status report for all states"""
        status_data = []
        
        for state_code in self.state_agencies.keys():
            summary = self.create_state_summary_report(state_code)
            
            status_data.append({
                'State': state_code,
                'Agency': self.state_agencies[state_code].agency_acronym,
                'Current QAP': summary['documents']['current_qap_year'],
                'QAP Docs': summary['documents']['qap_count'],
                'Has Redlines': summary['documents']['has_redlines'],
                'App Forms': summary['documents']['application_forms_count'],
                'Award Years': len(summary['documents']['award_years']),
                'Special Funds': len(summary['special_funds']),
                'Data Quality': f"{summary['data_quality']['qap_coverage']:.0%}"
            })
            
        df = pd.DataFrame(status_data)
        
        # Save to Excel
        report_path = self.dirs['reports'] / f"master_status_{datetime.now().strftime('%Y%m%d')}.xlsx"
        df.to_excel(report_path, index=False)
        
        return df
        
    def process_qap_to_chunks(self, file_path: str, state_code: str) -> List[Dict]:
        """Process QAP PDF into chunks using enhanced extractor logic"""
        # This would integrate the enhanced_ctcac_qap_ocr_rag_extractor.py logic
        # but generalized for any state's QAP format
        
        chunks = []
        # TODO: Implement PDF processing logic
        
        return chunks
        
def main():
    """Initialize and run the state housing intelligence system"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    system = StateHousingIntelligenceSystem(base_dir)
    
    # Generate initial status report
    print("Generating master status report...")
    status_df = system.generate_master_status_report()
    print(status_df)
    
    # Save all master data
    system.save_master_data()
    
    print(f"\nSystem initialized at: {system.data_dir}")
    print("Next steps:")
    print("1. Populate state agency URLs in state_agencies.json")
    print("2. Run document discovery for each state")
    print("3. Download and process QAPs")
    print("4. Extract application cycles and award data")
    
if __name__ == "__main__":
    main()
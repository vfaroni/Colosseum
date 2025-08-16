#!/usr/bin/env python3
"""
Enhanced TDHCA LIHTC Application Data Extractor with Address and Scoring Information

This enhanced version extracts:
1. Complete property addresses (street, city, county, state, zip)
2. TDHCA scoring information that helped projects get awarded
3. All original data points from the base extractor

Based on the M4 handoff document requirements for comprehensive benchmarking.

Author: Enhanced for M4 Beast processing
Date: July 2025
"""

import os
import json
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import re
from typing import Dict, List, Any, Optional, Tuple
import PyPDF2
import pdfplumber
from dataclasses import dataclass, field

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tdhca_enhanced_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedProjectData:
    """Enhanced data structure with address and scoring information"""
    # Basic info
    application_number: str = ""
    project_name: str = ""
    
    # Complete address information
    street_address: str = ""
    city: str = ""
    county: str = ""
    state: str = "TX"
    zip_code: str = ""
    full_address: str = ""  # Combined address for geocoding
    
    # Location details
    msa: str = ""
    census_tract: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    
    # Unit information
    total_units: int = 0
    unit_mix: Dict[str, int] = field(default_factory=dict)
    unit_square_footage: Dict[str, int] = field(default_factory=dict)
    
    # AMI set-asides
    ami_matrix: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    # Financial data
    land_cost_total: float = 0.0
    land_acres: float = 0.0
    land_cost_per_acre: float = 0.0
    total_construction_cost: float = 0.0
    total_development_cost: float = 0.0
    developer_fee: float = 0.0
    architect_engineer_fee: float = 0.0
    
    # Financing structure
    lihtc_equity: float = 0.0
    first_lien_loan: float = 0.0
    second_lien_loan: float = 0.0
    other_financing: Dict[str, float] = field(default_factory=dict)
    
    # Property details
    targeted_population: str = ""
    property_type: str = ""  # Family, Senior, etc.
    
    # TDHCA Scoring Information
    opportunity_index_score: int = 0
    opportunity_index_details: str = ""
    
    qct_dda_status: str = ""  # QCT, DDA, Both, Neither
    qct_dda_boost: bool = False
    
    proximity_scores: Dict[str, float] = field(default_factory=dict)  # grocery, school, etc.
    
    competition_analysis: Dict[str, Any] = field(default_factory=dict)
    
    total_tdhca_score: int = 0
    scoring_breakdown: Dict[str, int] = field(default_factory=dict)
    award_factors: List[str] = field(default_factory=list)
    
    # Metadata
    extraction_date: str = ""
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    processing_notes: List[str] = field(default_factory=list)

class EnhancedTDHCAExtractor:
    """Enhanced extractor with address and scoring extraction capabilities"""
    
    def __init__(self, base_path: str):
        """Initialize the enhanced extractor"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create output directories
        self.output_dir = self.base_path / 'enhanced_extraction_results'
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized Enhanced TDHCA Extractor at {self.base_path}")
    
    def extract_pdf_text(self, pdf_path: Path, max_pages: int = None) -> str:
        """
        Extract text from PDF using multiple methods
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to extract (None for all)
            
        Returns:
            Extracted text
        """
        text = ""
        
        try:
            # Primary method: pdfplumber (better for tables)
            with pdfplumber.open(pdf_path) as pdf:
                pages_to_process = len(pdf.pages) if max_pages is None else min(max_pages, len(pdf.pages))
                
                for i in range(pages_to_process):
                    page = pdf.pages[i]
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {i+1} ---\n{page_text}"
                    
                    # Also extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            text += "\n[TABLE]\n"
                            for row in table:
                                if row:
                                    text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                            text += "[/TABLE]\n"
                            
            if text.strip():
                return text
                
        except Exception as e:
            logger.warning(f"pdfplumber failed for {pdf_path.name}: {e}")
        
        # Fallback to PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages_to_process = len(pdf_reader.pages) if max_pages is None else min(max_pages, len(pdf_reader.pages))
                
                for page_num in range(pages_to_process):
                    page = pdf_reader.pages[page_num]
                    text += f"\n--- Page {page_num+1} ---\n{page.extract_text()}"
                    
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path.name}: {e}")
        
        return text
    
    def extract_address(self, text: str) -> Dict[str, str]:
        """
        Extract complete address information from application text
        
        Returns dict with: street_address, city, county, state, zip_code, full_address
        """
        address_info = {
            'street_address': '',
            'city': '',
            'county': '',
            'state': 'TX',
            'zip_code': '',
            'full_address': ''
        }
        
        # Clean text for processing
        clean_text = text.replace('\n', ' ').replace('\r', ' ')
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # Pattern 1: Look for "Property Address" or "Site Address" sections
        address_patterns = [
            r'(?:Property|Site|Project|Development)\s*Address[:\s]+([^,]+),\s*([^,]+),\s*TX\s*(\d{5})',
            r'Address[:\s]+(\d+[^,]+),\s*([^,]+),\s*(?:TX|Texas)\s*(\d{5})',
            r'Location[:\s]+(\d+[^,]+),\s*([^,]+),\s*TX\s*(\d{5})',
            # Broader pattern for addresses with street numbers
            r'(\d+\s+[A-Z][^,]{5,50}),\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*TX\s*(\d{5})'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                address_info['street_address'] = match.group(1).strip()
                address_info['city'] = match.group(2).strip()
                address_info['zip_code'] = match.group(3).strip()
                break
        
        # Extract county separately
        county_patterns = [
            r'County[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Located in\s+([A-Z][a-z]+)\s+County',
            r'([A-Z][a-z]+)\s+County,?\s+(?:TX|Texas)'
        ]
        
        for pattern in county_patterns:
            match = re.search(pattern, clean_text)
            if match:
                address_info['county'] = match.group(1).strip()
                break
        
        # Build full address
        if address_info['street_address'] and address_info['city']:
            parts = [address_info['street_address'], address_info['city'], 'TX']
            if address_info['zip_code']:
                parts.append(address_info['zip_code'])
            address_info['full_address'] = ', '.join(parts)
        
        return address_info
    
    def extract_scoring_information(self, text: str) -> Dict[str, Any]:
        """
        Extract TDHCA scoring information and award factors
        """
        scoring_info = {
            'opportunity_index_score': 0,
            'opportunity_index_details': '',
            'qct_dda_status': '',
            'qct_dda_boost': False,
            'proximity_scores': {},
            'competition_analysis': {},
            'total_tdhca_score': 0,
            'scoring_breakdown': {},
            'award_factors': []
        }
        
        clean_text = text.replace('\n', ' ').replace('\r', ' ')
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # Extract Opportunity Index Score
        opp_index_patterns = [
            r'Opportunity Index[:\s]+(\d+)\s*(?:points?|pts?)',
            r'Opportunity Index Score[:\s]+(\d+)',
            r'OI Score[:\s]+(\d+)'
        ]
        
        for pattern in opp_index_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                scoring_info['opportunity_index_score'] = int(match.group(1))
                break
        
        # Extract QCT/DDA Status
        if re.search(r'(?:QCT|Qualified Census Tract)', clean_text, re.IGNORECASE):
            if re.search(r'(?:DDA|Difficult Development Area)', clean_text, re.IGNORECASE):
                scoring_info['qct_dda_status'] = 'Both'
            else:
                scoring_info['qct_dda_status'] = 'QCT'
        elif re.search(r'(?:DDA|Difficult Development Area)', clean_text, re.IGNORECASE):
            scoring_info['qct_dda_status'] = 'DDA'
        else:
            scoring_info['qct_dda_status'] = 'Neither'
        
        # Check for 130% boost eligibility
        if scoring_info['qct_dda_status'] in ['QCT', 'DDA', 'Both']:
            if re.search(r'130%\s*(?:boost|basis)', clean_text, re.IGNORECASE):
                scoring_info['qct_dda_boost'] = True
        
        # Extract proximity scores
        proximity_items = {
            'grocery_store': [r'grocery\s*store\s*(?:distance|proximity)[:\s]+([\d.]+)\s*miles?'],
            'elementary_school': [r'elementary\s*school\s*(?:distance|proximity)[:\s]+([\d.]+)\s*miles?'],
            'public_transit': [r'(?:bus|transit)\s*stop\s*(?:distance|proximity)[:\s]+([\d.]+)\s*miles?'],
            'health_facility': [r'(?:health|medical|clinic)\s*(?:distance|proximity)[:\s]+([\d.]+)\s*miles?']
        }
        
        for item, patterns in proximity_items.items():
            for pattern in patterns:
                match = re.search(pattern, clean_text, re.IGNORECASE)
                if match:
                    scoring_info['proximity_scores'][item] = float(match.group(1))
                    break
        
        # Extract total TDHCA score
        total_score_patterns = [
            r'Total\s*(?:TDHCA\s*)?Score[:\s]+(\d+)',
            r'Total\s*Points[:\s]+(\d+)',
            r'Application\s*Score[:\s]+(\d+)'
        ]
        
        for pattern in total_score_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                scoring_info['total_tdhca_score'] = int(match.group(1))
                break
        
        # Extract scoring breakdown (look for point categories)
        scoring_categories = [
            ('opportunity_index', r'Opportunity\s*Index[:\s]+(\d+)\s*(?:points?|pts?)'),
            ('site_characteristics', r'Site\s*Characteristics[:\s]+(\d+)\s*(?:points?|pts?)'),
            ('development_size', r'Development\s*Size[:\s]+(\d+)\s*(?:points?|pts?)'),
            ('tenant_services', r'Tenant\s*Services[:\s]+(\d+)\s*(?:points?|pts?)'),
            ('readiness_to_proceed', r'Readiness\s*to\s*Proceed[:\s]+(\d+)\s*(?:points?|pts?)')
        ]
        
        for category, pattern in scoring_categories:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                scoring_info['scoring_breakdown'][category] = int(match.group(1))
        
        # Extract award factors (reasons for selection)
        award_factor_keywords = [
            'high opportunity area',
            'excellent proximity to amenities',
            'strong local support',
            'experienced development team',
            'cost-effective design',
            'serves high-need population',
            'located in QCT',
            'located in DDA',
            'rural set-aside',
            'at-risk set-aside'
        ]
        
        for keyword in award_factor_keywords:
            if re.search(keyword, clean_text, re.IGNORECASE):
                scoring_info['award_factors'].append(keyword)
        
        return scoring_info
    
    def extract_ami_matrix(self, text: str, unit_mix: Dict[str, int]) -> Dict[str, Dict[str, int]]:
        """
        Extract AMI set-aside matrix by bedroom type
        """
        ami_matrix = {
            '30_ami': {},
            '50_ami': {},
            '60_ami': {},
            '80_ami': {}
        }
        
        # Look for AMI tables in the text
        ami_patterns = [
            # Pattern: "8 units at 50% AMI (1BR)"
            r'(\d+)\s*units?\s*(?:at|@)\s*(\d+)%\s*AMI\s*\((\d+BR|Studio)\)',
            # Pattern: "50% AMI: 8 1BR, 8 2BR"
            r'(\d+)%\s*AMI[:\s]+.*?(\d+)\s*(\d+BR|Studio)',
            # Pattern in tables: "TC 50%" followed by unit counts
            r'TC\s*(\d+)%.*?(\d+)\s*units?'
        ]
        
        # Clean text for processing
        clean_text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Extract from patterns
        for pattern in ami_patterns:
            matches = re.finditer(pattern, clean_text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 3:
                    units = int(match.group(1))
                    ami_level = match.group(2)
                    bedroom_type = match.group(3)
                    
                    ami_key = f'{ami_level}_ami'
                    if ami_key in ami_matrix:
                        ami_matrix[ami_key][bedroom_type] = units
        
        return ami_matrix
    
    def extract_enhanced_project_data(self, text: str, app_number: str) -> EnhancedProjectData:
        """
        Extract all project data including address and scoring information
        """
        project = EnhancedProjectData()
        project.application_number = app_number
        project.extraction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Clean text for easier parsing
        clean_text = text.replace('\n', ' ').replace('\r', ' ')
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # Extract project name
        name_patterns = [
            r'Project Name[:\s]+([^.]+?)(?:\s|$)',
            r'Development Name[:\s]+([^.]+?)(?:\s|$)',
            r'Property Name[:\s]+([^.]+?)(?:\s|$)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                project.project_name = match.group(1).strip()
                break
        
        # Extract complete address
        address_info = self.extract_address(text)
        project.street_address = address_info['street_address']
        project.city = address_info['city']
        project.county = address_info['county']
        project.state = address_info['state']
        project.zip_code = address_info['zip_code']
        project.full_address = address_info['full_address']
        
        # Extract census tract
        census_patterns = [
            r'Census Tract[:\s]+(\d+\.?\d*)',
            r'Tract[:\s]+(\d+\.?\d*)',
            r'CT[:\s]+(\d+\.?\d*)'
        ]
        
        for pattern in census_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                project.census_tract = match.group(1).strip()
                break
        
        # Extract unit information
        unit_patterns = [
            r'Total Units[:\s]+(\d+)',
            r'Number of Units[:\s]+(\d+)',
            r'Total Residential Units[:\s]+(\d+)',
            r'(\d+)\s+total units'
        ]
        
        for pattern in unit_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                try:
                    project.total_units = int(match.group(1))
                    break
                except ValueError:
                    continue
        
        # Extract unit mix
        unit_mix_patterns = [
            (r'(\d+)\s+studio', 'Studio'),
            (r'(\d+)\s+efficiency', 'Studio'),
            (r'(\d+)\s+one[-\s]bedroom', '1BR'),
            (r'(\d+)\s+1[-\s]bedroom', '1BR'),
            (r'(\d+)\s+1\s*BR', '1BR'),
            (r'(\d+)\s+two[-\s]bedroom', '2BR'),
            (r'(\d+)\s+2[-\s]bedroom', '2BR'),
            (r'(\d+)\s+2\s*BR', '2BR'),
            (r'(\d+)\s+three[-\s]bedroom', '3BR'),
            (r'(\d+)\s+3[-\s]bedroom', '3BR'),
            (r'(\d+)\s+3\s*BR', '3BR'),
            (r'(\d+)\s+four[-\s]bedroom', '4BR'),
            (r'(\d+)\s+4[-\s]bedroom', '4BR'),
            (r'(\d+)\s+4\s*BR', '4BR')
        ]
        
        for pattern, unit_type in unit_mix_patterns:
            matches = re.findall(pattern, clean_text, re.IGNORECASE)
            if matches:
                project.unit_mix[unit_type] = int(max(matches))
        
        # Extract unit square footage
        sqft_patterns = [
            r'1BR[:\s]+(\d+)\s*(?:sq\.?\s*ft\.?|square feet)',
            r'2BR[:\s]+(\d+)\s*(?:sq\.?\s*ft\.?|square feet)',
            r'(\d+)\s*(?:sq\.?\s*ft\.?|square feet)\s*\(?1BR\)?',
            r'(\d+)\s*(?:sq\.?\s*ft\.?|square feet)\s*\(?2BR\)?'
        ]
        
        # Extract AMI matrix
        project.ami_matrix = self.extract_ami_matrix(text, project.unit_mix)
        
        # Extract financial data
        # Land cost
        land_cost_patterns = [
            r'Land Cost[:\s]+\$?([\d,]+)',
            r'Site Acquisition[:\s]+\$?([\d,]+)',
            r'Land Acquisition[:\s]+\$?([\d,]+)'
        ]
        
        for pattern in land_cost_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                try:
                    cost_str = match.group(1).replace(',', '')
                    project.land_cost_total = float(cost_str)
                    break
                except ValueError:
                    continue
        
        # Total development cost
        dev_cost_patterns = [
            r'Total Development Cost[:\s]+\$?([\d,]+)',
            r'Total Project Cost[:\s]+\$?([\d,]+)',
            r'TDC[:\s]+\$?([\d,]+)'
        ]
        
        for pattern in dev_cost_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                try:
                    cost_str = match.group(1).replace(',', '')
                    project.total_development_cost = float(cost_str)
                    break
                except ValueError:
                    continue
        
        # Developer fee
        dev_fee_patterns = [
            r'Developer Fee[:\s]+\$?([\d,]+)',
            r'Development Fee[:\s]+\$?([\d,]+)'
        ]
        
        for pattern in dev_fee_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                try:
                    fee_str = match.group(1).replace(',', '')
                    project.developer_fee = float(fee_str)
                    break
                except ValueError:
                    continue
        
        # LIHTC Equity
        equity_patterns = [
            r'(?:LIHTC|Tax Credit)\s+Equity[:\s]+\$?([\d,]+)',
            r'Equity[:\s]+\$?([\d,]+)'
        ]
        
        for pattern in equity_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                try:
                    equity_str = match.group(1).replace(',', '')
                    project.lihtc_equity = float(equity_str)
                    break
                except ValueError:
                    continue
        
        # Property type
        if re.search(r'senior|elderly', clean_text, re.IGNORECASE):
            project.property_type = 'Senior'
        elif re.search(r'family', clean_text, re.IGNORECASE):
            project.property_type = 'Family'
        elif re.search(r'special needs|supportive', clean_text, re.IGNORECASE):
            project.property_type = 'Special Needs'
        
        # Extract scoring information
        scoring_info = self.extract_scoring_information(text)
        project.opportunity_index_score = scoring_info['opportunity_index_score']
        project.opportunity_index_details = scoring_info['opportunity_index_details']
        project.qct_dda_status = scoring_info['qct_dda_status']
        project.qct_dda_boost = scoring_info['qct_dda_boost']
        project.proximity_scores = scoring_info['proximity_scores']
        project.competition_analysis = scoring_info['competition_analysis']
        project.total_tdhca_score = scoring_info['total_tdhca_score']
        project.scoring_breakdown = scoring_info['scoring_breakdown']
        project.award_factors = scoring_info['award_factors']
        
        # Calculate confidence scores
        project.confidence_scores = self.calculate_confidence_scores(project)
        
        return project
    
    def calculate_confidence_scores(self, project: EnhancedProjectData) -> Dict[str, float]:
        """
        Calculate confidence scores for extracted data
        """
        scores = {}
        
        # Address confidence
        address_fields = [project.street_address, project.city, project.zip_code]
        address_filled = sum(1 for f in address_fields if f)
        scores['address'] = address_filled / len(address_fields)
        
        # Unit data confidence
        if project.total_units > 0 and project.unit_mix:
            unit_sum = sum(project.unit_mix.values())
            scores['unit_data'] = min(1.0, unit_sum / project.total_units)
        else:
            scores['unit_data'] = 0.0
        
        # Financial data confidence
        financial_fields = [
            project.land_cost_total,
            project.total_development_cost,
            project.developer_fee,
            project.lihtc_equity
        ]
        financial_filled = sum(1 for f in financial_fields if f > 0)
        scores['financial_data'] = financial_filled / len(financial_fields)
        
        # Scoring data confidence
        if project.total_tdhca_score > 0 or project.opportunity_index_score > 0:
            scores['scoring_data'] = 0.8
        elif project.award_factors:
            scores['scoring_data'] = 0.6
        else:
            scores['scoring_data'] = 0.2
        
        # Overall confidence
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def process_application(self, pdf_path: Path) -> Optional[EnhancedProjectData]:
        """
        Process a single TDHCA application PDF
        """
        logger.info(f"Processing {pdf_path.name}")
        
        # Extract application number from filename
        app_number_match = re.search(r'(\d{5})', pdf_path.name)
        if not app_number_match:
            logger.warning(f"Could not extract application number from {pdf_path.name}")
            return None
        
        app_number = app_number_match.group(1)
        
        # Extract text from PDF
        text = self.extract_pdf_text(pdf_path)
        
        if not text.strip():
            logger.warning(f"No text extracted from {pdf_path.name}")
            return None
        
        # Extract enhanced project data
        project_data = self.extract_enhanced_project_data(text, app_number)
        
        # Add processing notes
        if project_data.confidence_scores['overall'] < 0.5:
            project_data.processing_notes.append("Low confidence extraction - manual review recommended")
        
        if not project_data.full_address:
            project_data.processing_notes.append("Address extraction failed - manual lookup required")
        
        if project_data.total_tdhca_score == 0:
            project_data.processing_notes.append("No TDHCA score found - check if scoring sheet included")
        
        return project_data
    
    def process_all_applications(self, input_dir: Path) -> List[EnhancedProjectData]:
        """
        Process all PDF applications in a directory
        """
        pdf_files = list(input_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        results = []
        for pdf_file in pdf_files:
            try:
                project_data = self.process_application(pdf_file)
                if project_data:
                    results.append(project_data)
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(results)} applications")
        return results
    
    def save_results(self, projects: List[EnhancedProjectData], output_name: str = "enhanced_extraction"):
        """
        Save extraction results to multiple formats
        """
        if not projects:
            logger.warning("No projects to save")
            return
        
        # Convert to dictionaries
        projects_data = []
        for project in projects:
            data = {
                # Basic info
                'application_number': project.application_number,
                'project_name': project.project_name,
                
                # Address
                'street_address': project.street_address,
                'city': project.city,
                'county': project.county,
                'state': project.state,
                'zip_code': project.zip_code,
                'full_address': project.full_address,
                
                # Location
                'census_tract': project.census_tract,
                'msa': project.msa,
                
                # Units
                'total_units': project.total_units,
                'unit_mix': json.dumps(project.unit_mix),
                'ami_matrix': json.dumps(project.ami_matrix),
                
                # Financial
                'land_cost_total': project.land_cost_total,
                'total_development_cost': project.total_development_cost,
                'developer_fee': project.developer_fee,
                'lihtc_equity': project.lihtc_equity,
                
                # Property
                'property_type': project.property_type,
                'targeted_population': project.targeted_population,
                
                # Scoring
                'opportunity_index_score': project.opportunity_index_score,
                'qct_dda_status': project.qct_dda_status,
                'qct_dda_boost': project.qct_dda_boost,
                'total_tdhca_score': project.total_tdhca_score,
                'scoring_breakdown': json.dumps(project.scoring_breakdown),
                'award_factors': ', '.join(project.award_factors),
                
                # Metadata
                'extraction_date': project.extraction_date,
                'confidence_score': project.confidence_scores.get('overall', 0),
                'processing_notes': ', '.join(project.processing_notes)
            }
            projects_data.append(data)
        
        # Save as JSON
        json_path = self.output_dir / f"{output_name}.json"
        with open(json_path, 'w') as f:
            json.dump(projects_data, f, indent=2)
        logger.info(f"Saved JSON results to {json_path}")
        
        # Save as CSV
        df = pd.DataFrame(projects_data)
        csv_path = self.output_dir / f"{output_name}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved CSV results to {csv_path}")
        
        # Create summary report
        self.create_enhanced_summary_report(projects, output_name)
    
    def create_enhanced_summary_report(self, projects: List[EnhancedProjectData], output_name: str):
        """
        Create an enhanced summary report with address and scoring insights
        """
        report_lines = []
        report_lines.append("ENHANCED TDHCA EXTRACTION SUMMARY REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total Applications Processed: {len(projects)}")
        report_lines.append("")
        
        # Address extraction success rate
        with_address = sum(1 for p in projects if p.full_address)
        report_lines.append(f"Address Extraction Success: {with_address}/{len(projects)} ({with_address/len(projects)*100:.1f}%)")
        
        # Scoring data availability
        with_scores = sum(1 for p in projects if p.total_tdhca_score > 0)
        report_lines.append(f"Scoring Data Available: {with_scores}/{len(projects)} ({with_scores/len(projects)*100:.1f}%)")
        
        # QCT/DDA distribution
        qct_dda_counts = {}
        for p in projects:
            status = p.qct_dda_status or 'Unknown'
            qct_dda_counts[status] = qct_dda_counts.get(status, 0) + 1
        
        report_lines.append("\nQCT/DDA Status Distribution:")
        for status, count in sorted(qct_dda_counts.items()):
            report_lines.append(f"  {status}: {count} projects")
        
        # Average scores
        scored_projects = [p for p in projects if p.total_tdhca_score > 0]
        if scored_projects:
            avg_score = sum(p.total_tdhca_score for p in scored_projects) / len(scored_projects)
            report_lines.append(f"\nAverage TDHCA Score: {avg_score:.1f}")
            
            avg_opp_index = sum(p.opportunity_index_score for p in scored_projects) / len(scored_projects)
            report_lines.append(f"Average Opportunity Index: {avg_opp_index:.1f}")
        
        # Top award factors
        all_factors = []
        for p in projects:
            all_factors.extend(p.award_factors)
        
        if all_factors:
            factor_counts = {}
            for factor in all_factors:
                factor_counts[factor] = factor_counts.get(factor, 0) + 1
            
            report_lines.append("\nTop Award Factors:")
            for factor, count in sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                report_lines.append(f"  {factor}: {count} projects")
        
        # Geographic distribution
        counties = [p.county for p in projects if p.county]
        if counties:
            county_counts = {}
            for county in counties:
                county_counts[county] = county_counts.get(county, 0) + 1
            
            report_lines.append(f"\nGeographic Distribution ({len(set(counties))} counties):")
            for county, count in sorted(county_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                report_lines.append(f"  {county}: {count} projects")
        
        # Confidence score distribution
        report_lines.append("\nData Quality (Confidence Scores):")
        high_conf = sum(1 for p in projects if p.confidence_scores.get('overall', 0) >= 0.8)
        med_conf = sum(1 for p in projects if 0.5 <= p.confidence_scores.get('overall', 0) < 0.8)
        low_conf = sum(1 for p in projects if p.confidence_scores.get('overall', 0) < 0.5)
        
        report_lines.append(f"  High confidence (≥80%): {high_conf} projects")
        report_lines.append(f"  Medium confidence (50-79%): {med_conf} projects")
        report_lines.append(f"  Low confidence (<50%): {low_conf} projects")
        
        # Save report
        report_path = self.output_dir / f"{output_name}_summary.txt"
        with open(report_path, 'w') as f:
            f.write('\n'.join(report_lines))
        logger.info(f"Saved summary report to {report_path}")


def main():
    """
    Main execution function
    """
    # Set up paths
    base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites")
    
    # Initialize extractor
    extractor = EnhancedTDHCAExtractor(base_path)
    
    # Process 2023 applications
    regions = ['Dallas_Fort_Worth', 'Houston', 'San_Antonio']
    
    all_projects = []
    
    for region in regions:
        input_dir = base_path / 'Successful_2023_Applications' / region
        if input_dir.exists():
            logger.info(f"\nProcessing {region} applications...")
            projects = extractor.process_all_applications(input_dir)
            all_projects.extend(projects)
        else:
            logger.warning(f"Directory not found: {input_dir}")
    
    # Save combined results
    if all_projects:
        extractor.save_results(all_projects, "tdhca_2023_enhanced_extraction")
        logger.info(f"\nTotal applications processed: {len(all_projects)}")
    else:
        logger.error("No applications were successfully processed")


if __name__ == "__main__":
    main()
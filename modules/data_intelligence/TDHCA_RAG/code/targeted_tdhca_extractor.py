#!/usr/bin/env python3
"""
Targeted TDHCA Extractor - High-Value Financial Data
Focuses on specific sections with known locations for maximum efficiency
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

# Import salvaged components
from ultimate_tdhca_extractor import UltimateTDHCAExtractor

@dataclass
class TargetedProjectData:
    """Focused data structure for high-value extraction"""
    
    # Basic project info (keep what works)
    filename: str = ""
    project_name: str = ""
    street_address: str = ""
    city: str = ""
    county: str = ""
    zip_code: str = ""
    
    # HIGH-VALUE UNIT MIX DATA
    unit_mix: Dict[str, int] = field(default_factory=dict)  # {'1BR': 50, '2BR': 30, etc}
    unit_square_footage: Dict[str, int] = field(default_factory=dict)  # {'1BR': 650, '2BR': 850}
    unit_rents: Dict[str, float] = field(default_factory=dict)  # {'1BR': 850.0, '2BR': 1050.0}
    total_units: int = 0
    total_building_sf: int = 0
    
    # HIGH-VALUE FINANCIAL DATA
    total_development_cost: float = 0.0
    development_cost_per_unit: float = 0.0
    site_acquisition_cost: float = 0.0
    building_acquisition_cost: float = 0.0
    total_hard_costs: float = 0.0
    total_soft_costs: float = 0.0
    
    # DEVELOPMENT COSTS
    developer_fee: float = 0.0
    general_contractor_fee: float = 0.0
    architectural_fees: float = 0.0
    engineering_fees: float = 0.0
    legal_fees: float = 0.0
    
    # FINANCING SOURCES
    housing_tax_credit_equity: float = 0.0
    construction_loan: float = 0.0
    permanent_loan: float = 0.0
    government_grants: float = 0.0
    developer_cash_equity: float = 0.0
    
    # DEVELOPMENT TEAM
    developer_name: str = ""
    general_contractor: str = ""
    architect: str = ""
    management_company: str = ""
    
    # AMI TARGETING
    ami_breakdown: Dict[str, int] = field(default_factory=dict)  # {'30%': 10, '50%': 25, '60%': 30}
    
    # METADATA
    extraction_confidence: float = 0.0
    processing_notes: List[str] = field(default_factory=list)
    
class TargetedTDHCAExtractor(UltimateTDHCAExtractor):
    """Focused extractor targeting specific high-value sections"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        
        # Define target page patterns for surgical extraction
        self.target_sections = {
            'rent_schedule': {
                'patterns': [
                    r'rent\s+schedule',
                    r'unit\s+mix',
                    r'bedroom.*rent',
                    r'# of bed.*rooms'
                ],
                'priority': 1
            },
            'development_cost': {
                'patterns': [
                    r'development\s+cost\s+schedule',
                    r'total\s+development\s+cost',
                    r'acquisition\s+cost',
                    r'hard\s+costs',
                    r'soft\s+costs',
                    r'developer\s+fee'
                ],
                'priority': 1
            },
            'sources_of_funds': {
                'patterns': [
                    r'sources\s+of\s+funds',
                    r'financing\s+narrative',
                    r'tax\s+credit\s+equity',
                    r'construction\s+loan'
                ],
                'priority': 2
            },
            'development_team': {
                'patterns': [
                    r'development\s+team',
                    r'developer.*name',
                    r'general\s+contractor',
                    r'architect.*name'
                ],
                'priority': 2
            }
        }
    
    def identify_target_pages(self, pdf_path: Path) -> Dict[str, List[int]]:
        """Identify which pages contain our target sections"""
        
        # Use salvaged smart extraction to get text efficiently
        text, stats = self.smart_extract_pdf_text(pdf_path)
        
        if not text:
            return {}
        
        # Split into pages (rough approximation)
        pages = text.split('\n\n\n')  # Assume triple newlines separate pages
        
        target_pages = {}
        
        for section_name, section_info in self.target_sections.items():
            target_pages[section_name] = []
            
            for page_num, page_text in enumerate(pages):
                page_lower = page_text.lower()
                
                # Check if this page contains target patterns
                matches = 0
                for pattern in section_info['patterns']:
                    if re.search(pattern, page_lower):
                        matches += 1
                
                # If we found multiple patterns, this is likely our target page
                if matches >= 1:
                    target_pages[section_name].append(page_num)
        
        return target_pages
    
    def extract_unit_mix_data(self, text: str) -> Dict:
        """Extract unit mix data from rent schedule section"""
        
        unit_data = {
            'unit_mix': {},
            'unit_square_footage': {},
            'unit_rents': {},
            'total_units': 0
        }
        
        # Look for bedroom/unit tables
        bedroom_patterns = [
            r'(\d+)\s*(?:bedroom|br|bed)\s*.*?(\d+)\s*units?',
            r'(\d+)br\s*.*?(\d+)\s*units?',
            r'studio.*?(\d+)\s*units?',
            r'efficiency.*?(\d+)\s*units?'
        ]
        
        for pattern in bedroom_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    bedroom_count = match[0]
                    unit_count = int(match[1])
                elif len(match) == 1:  # Studio/efficiency
                    bedroom_count = '0'
                    unit_count = int(match[0])
                else:
                    continue
                
                unit_type = f"{bedroom_count}BR" if bedroom_count != '0' else 'Studio'
                unit_data['unit_mix'][unit_type] = unit_count
                unit_data['total_units'] += unit_count
        
        # Extract square footage data
        sf_patterns = [
            r'(\d+)\s*(?:bedroom|br)\s*.*?(\d{3,4})\s*(?:sq\.?\s*ft|sf)',
            r'studio.*?(\d{3,4})\s*(?:sq\.?\s*ft|sf)'
        ]
        
        for pattern in sf_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    bedroom_count, sq_ft = match[0], int(match[1])
                    unit_type = f"{bedroom_count}BR"
                elif len(match) == 1:  # Studio
                    sq_ft = int(match[0])
                    unit_type = 'Studio'
                else:
                    continue
                
                unit_data['unit_square_footage'][unit_type] = sq_ft
        
        # Extract rent data
        rent_patterns = [
            r'(\d+)\s*(?:bedroom|br)\s*.*?\$(\d{3,4})',
            r'studio.*?\$(\d{3,4})'
        ]
        
        for pattern in rent_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    bedroom_count, rent = match[0], float(match[1])
                    unit_type = f"{bedroom_count}BR"
                elif len(match) == 1:  # Studio
                    rent = float(match[0])
                    unit_type = 'Studio'
                else:
                    continue
                
                unit_data['unit_rents'][unit_type] = rent
        
        return unit_data
    
    def extract_development_costs(self, text: str) -> Dict:
        """Extract development cost data"""
        
        cost_data = {
            'total_development_cost': 0.0,
            'site_acquisition_cost': 0.0,
            'building_acquisition_cost': 0.0,
            'total_hard_costs': 0.0,
            'total_soft_costs': 0.0,
            'developer_fee': 0.0,
            'general_contractor_fee': 0.0,
            'architectural_fees': 0.0,
            'engineering_fees': 0.0,
            'legal_fees': 0.0
        }
        
        # Define cost extraction patterns
        cost_patterns = {
            'total_development_cost': [
                r'total\s+development\s+cost[:\s]+\$?([\d,]+)',
                r'total\s+project\s+cost[:\s]+\$?([\d,]+)'
            ],
            'site_acquisition_cost': [
                r'site\s+acquisition\s+cost[:\s]+\$?([\d,]+)',
                r'land\s+cost[:\s]+\$?([\d,]+)'
            ],
            'building_acquisition_cost': [
                r'building\s+acquisition\s+cost[:\s]+\$?([\d,]+)',
                r'existing\s+building.*cost[:\s]+\$?([\d,]+)'
            ],
            'total_hard_costs': [
                r'total\s+hard\s+costs[:\s]+\$?([\d,]+)',
                r'construction\s+costs[:\s]+\$?([\d,]+)'
            ],
            'total_soft_costs': [
                r'total\s+soft\s+costs[:\s]+\$?([\d,]+)',
                r'soft\s+costs[:\s]+\$?([\d,]+)'
            ],
            'developer_fee': [
                r'developer\s+fee[:\s]+\$?([\d,]+)',
                r'development\s+fee[:\s]+\$?([\d,]+)'
            ],
            'general_contractor_fee': [
                r'general\s+contractor\s+fee[:\s]+\$?([\d,]+)',
                r'contractor\s+fee[:\s]+\$?([\d,]+)'
            ],
            'architectural_fees': [
                r'architectural\s+fees?[:\s]+\$?([\d,]+)',
                r'architect.*fee[:\s]+\$?([\d,]+)'
            ],
            'engineering_fees': [
                r'engineering\s+fees?[:\s]+\$?([\d,]+)',
                r'engineer.*fee[:\s]+\$?([\d,]+)'
            ],
            'legal_fees': [
                r'legal\s+fees?[:\s]+\$?([\d,]+)',
                r'attorney.*fee[:\s]+\$?([\d,]+)'
            ]
        }
        
        for cost_type, patterns in cost_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        # Take the first match and clean it
                        amount_str = matches[0].replace(',', '')
                        amount = float(amount_str)
                        cost_data[cost_type] = amount
                        break  # Found a match, move to next cost type
                    except ValueError:
                        continue
        
        return cost_data
    
    def extract_development_team(self, text: str) -> Dict:
        """Extract development team information"""
        
        team_data = {
            'developer_name': '',
            'general_contractor': '',
            'architect': '',
            'management_company': ''
        }
        
        team_patterns = {
            'developer_name': [
                r'developer[:\s]+([A-Z][A-Za-z\s&,\.LLC]{10,60})',
                r'general\s+partner[:\s]+([A-Z][A-Za-z\s&,\.LLC]{10,60})'
            ],
            'general_contractor': [
                r'general\s+contractor[:\s]+([A-Z][A-Za-z\s&,\.LLC]{10,60})',
                r'contractor[:\s]+([A-Z][A-Za-z\s&,\.LLC]{10,60})'
            ],
            'architect': [
                r'architect[:\s]+([A-Z][A-Za-z\s&,\.LLC]{10,60})',
                r'design.*architect[:\s]+([A-Z][A-Za-z\s&,\.LLC]{10,60})'
            ],
            'management_company': [
                r'management\s+company[:\s]+([A-Z][A-Za-z\s&,\.LLC]{10,60})',
                r'property\s+management[:\s]+([A-Z][A-Za-z\s&,\.LLC]{10,60})'
            ]
        }
        
        for team_role, patterns in team_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Clean up the match
                    name = matches[0].strip()
                    if len(name) > 5 and name != name.upper():  # Avoid all caps matches
                        team_data[team_role] = name
                        break
        
        return team_data
    
    def process_targeted_application(self, pdf_path: Path) -> TargetedProjectData:
        """Process application with targeted extraction"""
        
        print(f"🎯 Processing {pdf_path.name} with targeted extraction")
        
        # Initialize result
        result = TargetedProjectData()
        result.filename = pdf_path.name
        
        try:
            # Use salvaged smart text extraction
            text, stats = self.smart_extract_pdf_text(pdf_path)
            
            if not text:
                result.processing_notes.append("Failed to extract text from PDF")
                return result
            
            result.processing_notes.append(f"Smart extraction: {stats.get('efficiency_gain', 0)*100:.1f}% pages skipped")
            
            # Extract basic project info (reuse working patterns)
            from improved_tdhca_extractor import ImprovedTDHCAExtractor
            basic_extractor = ImprovedTDHCAExtractor("")
            
            result.project_name = basic_extractor._extract_project_name_improved(text)
            street, city, zip_code = basic_extractor._extract_address_improved(text)
            result.street_address = street
            result.city = city
            result.zip_code = zip_code
            result.county = basic_extractor._extract_county_improved(text, zip_code)
            
            # HIGH-VALUE TARGETED EXTRACTIONS
            
            # 1. Unit Mix Data
            unit_data = self.extract_unit_mix_data(text)
            result.unit_mix = unit_data['unit_mix']
            result.unit_square_footage = unit_data['unit_square_footage']
            result.unit_rents = unit_data['unit_rents']
            result.total_units = unit_data['total_units']
            
            # 2. Development Costs
            cost_data = self.extract_development_costs(text)
            result.total_development_cost = cost_data['total_development_cost']
            result.site_acquisition_cost = cost_data['site_acquisition_cost']
            result.building_acquisition_cost = cost_data['building_acquisition_cost']
            result.total_hard_costs = cost_data['total_hard_costs']
            result.total_soft_costs = cost_data['total_soft_costs']
            result.developer_fee = cost_data['developer_fee']
            result.general_contractor_fee = cost_data['general_contractor_fee']
            result.architectural_fees = cost_data['architectural_fees']
            result.engineering_fees = cost_data['engineering_fees']
            result.legal_fees = cost_data['legal_fees']
            
            # Calculate per-unit costs
            if result.total_units > 0:
                result.development_cost_per_unit = result.total_development_cost / result.total_units if result.total_development_cost > 0 else 0
            
            # 3. Development Team
            team_data = self.extract_development_team(text)
            result.developer_name = team_data['developer_name']
            result.general_contractor = team_data['general_contractor']
            result.architect = team_data['architect']
            result.management_company = team_data['management_company']
            
            # Calculate extraction confidence
            fields_extracted = 0
            total_fields = 15  # Core high-value fields
            
            if result.project_name: fields_extracted += 1
            if result.total_units > 0: fields_extracted += 1
            if result.unit_mix: fields_extracted += 1
            if result.total_development_cost > 0: fields_extracted += 1
            if result.developer_fee > 0: fields_extracted += 1
            if result.developer_name: fields_extracted += 1
            # ... etc
            
            result.extraction_confidence = fields_extracted / total_fields
            result.processing_notes.append(f"Extracted {fields_extracted}/{total_fields} high-value fields")
            
        except Exception as e:
            result.processing_notes.append(f"Extraction error: {str(e)}")
            result.extraction_confidence = 0.0
        
        return result

if __name__ == "__main__":
    # Test the targeted extractor
    extractor = TargetedTDHCAExtractor("")
    
    # Test on a known file
    test_file = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_Applications_Benchmarks/Houston_Priority_1/TDHCA_25427_Bay_Terrace/25427.pdf")
    
    if test_file.exists():
        print("🧪 Testing targeted extractor on Bay Terrace Apartments")
        result = extractor.process_targeted_application(test_file)
        
        print(f"\n📊 EXTRACTION RESULTS:")
        print(f"Project: {result.project_name}")
        print(f"Units: {result.total_units}")
        print(f"Unit Mix: {result.unit_mix}")
        print(f"Development Cost: ${result.total_development_cost:,.0f}")
        print(f"Developer Fee: ${result.developer_fee:,.0f}")
        print(f"Developer: {result.developer_name}")
        print(f"Confidence: {result.extraction_confidence:.2f}")
    else:
        print("❌ Test file not found - run batch processing to test")
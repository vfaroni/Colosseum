#!/usr/bin/env python3
"""
Ollama-Optimized TDHCA Extractor for Llama 3.3 70B

Designed specifically for local LLM extraction with:
- Structured prompts optimized for Llama 3.3 70B
- JSON schema enforcement for consistent outputs
- Chunk-based processing within context limits
- Confidence scoring for hybrid routing

Author: Enhanced for M4 Beast + Ollama
Date: July 2025
"""

import json
import requests
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
import re
from ultimate_tdhca_extractor import UltimateTDHCAExtractor, UltimateProjectData

logger = logging.getLogger(__name__)

@dataclass
class LlamaExtractionResult:
    """Result from Llama extraction with confidence metrics"""
    data: Dict[str, Any]
    confidence: float
    needs_escalation: bool = False
    escalation_reasons: List[str] = field(default_factory=list)
    raw_response: str = ""


class OllamaTDHCAExtractor(UltimateTDHCAExtractor):
    """TDHCA extractor optimized for Ollama/Llama 3.3 70B"""
    
    def __init__(self, base_path: str, ollama_host: str = "http://localhost:11434"):
        super().__init__(base_path)
        self.ollama_host = ollama_host
        self.model = "llama3.3:70b"  # Adjust model name as needed
        
        # Llama-specific extraction templates
        self.extraction_prompts = {
            'basic_info': self._create_basic_info_prompt(),
            'address': self._create_address_prompt(),
            'units': self._create_units_prompt(),
            'financial': self._create_financial_prompt(),
            'team': self._create_team_prompt(),
            'dates': self._create_dates_prompt()
        }
        
        # Fields that often need Claude/Opus help
        self.complex_fields = {
            'ami_matrix', 'financial_calculations', 'complex_addresses'
        }
    
    def _create_basic_info_prompt(self) -> str:
        """Create Llama-optimized prompt for basic project info"""
        return """Extract the following information from the TDHCA application text and return ONLY a JSON object:

{{
  "application_number": "5-digit number",
  "project_name": "full project name",
  "development_type": "New Construction OR Rehabilitation",
  "property_type": "Senior OR Family OR Supportive Housing",
  "targeted_population": "specific population served"
}}

Rules:
- Application number is always 5 digits
- Property type must be one of the three listed options
- If unsure about a field, use null
- Do not include any text outside the JSON

Text to analyze:
{text}

JSON Output:"""

    def _create_address_prompt(self) -> str:
        """Create Llama-optimized prompt for address extraction"""
        return """Extract the complete property address from the text and return ONLY a JSON object:

{{
  "street_address": "number and street name",
  "city": "city name",
  "county": "county name",
  "state": "TX",
  "zip_code": "5-digit ZIP",
  "census_tract": "tract number if found",
  "region": "TDHCA region number"
}}

Rules:
- State is always "TX" for Texas
- County should not include "County" suffix
- Census tract is typically format: XX.XX
- Region is a single or double digit number
- If a field is not found, use null

Text to analyze:
{text}

JSON Output:"""

    def _create_units_prompt(self) -> str:
        """Create Llama-optimized prompt for unit information"""
        return """Extract unit information and return ONLY a JSON object:

{{
  "total_units": integer,
  "unit_mix": {{
    "Efficiency": integer or 0,
    "1BR": integer or 0,
    "2BR": integer or 0,
    "3BR": integer or 0,
    "4BR": integer or 0
  }},
  "ami_breakdown": {{
    "30_ami": integer or 0,
    "50_ami": integer or 0,
    "60_ami": integer or 0,
    "80_ami": integer or 0,
    "market_rate": integer or 0
  }}
}}

Rules:
- All values must be integers
- Unit mix values should sum to total_units
- AMI breakdown refers to income restrictions (30% AMI, 50% AMI, etc.)
- Use 0 for unit types not present

Text to analyze:
{text}

JSON Output:"""

    def _create_financial_prompt(self) -> str:
        """Create Llama-optimized prompt for financial data"""
        return """Extract financial information and return ONLY a JSON object with these amounts in dollars:

{{
  "total_development_cost": number,
  "land_cost": number,
  "construction_cost": number,
  "soft_costs": number,
  "developer_fee": number,
  "lihtc_equity": number,
  "first_lien_loan": number,
  "second_lien_loan": number,
  "other_financing": number
}}

Rules:
- All amounts should be in dollars (no cents)
- Remove any commas or $ signs from numbers
- Common abbreviations: TDC = Total Development Cost, LIHTC = Low Income Housing Tax Credit
- If a field is not found, use 0
- Land cost might be listed as "acquisition cost"

Text to analyze:
{text}

JSON Output:"""

    def _create_team_prompt(self) -> str:
        """Create Llama-optimized prompt for development team"""
        return """Extract development team information and return ONLY a JSON object:

{{
  "developer_name": "company name",
  "developer_contact": "primary contact person",
  "general_contractor": "GC company name",
  "architect": "architecture firm name",
  "management_company": "property management company",
  "consultant": "development consultant if any"
}}

Rules:
- Extract company/firm names, not individual names (except for contact)
- General Contractor may be abbreviated as "GC"
- If a field is not found, use null
- Do not guess or infer information

Text to analyze:
{text}

JSON Output:"""

    def _create_dates_prompt(self) -> str:
        """Create Llama-optimized prompt for timeline dates"""
        return """Extract project timeline dates and return ONLY a JSON object:

{{
  "application_date": "YYYY-MM-DD format",
  "construction_start": "YYYY-MM-DD format",
  "construction_end": "YYYY-MM-DD format",
  "placed_in_service": "YYYY-MM-DD format",
  "lease_up_start": "YYYY-MM-DD format"
}}

Rules:
- Convert all dates to YYYY-MM-DD format
- Common date formats: MM/DD/YYYY, Month DD, YYYY, MM-DD-YY
- "Placed in Service" may be abbreviated as "PIS"
- If only month/year given, use first day of month
- If date not found, use null

Text to analyze:
{text}

JSON Output:"""

    def call_ollama(self, prompt: str, temperature: float = 0.1) -> str:
        """Call Ollama API with error handling"""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False,
                    "format": "json"  # Helps Llama output valid JSON
                },
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "{}"
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return "{}"
    
    def extract_with_llama(self, text: str, extraction_type: str) -> LlamaExtractionResult:
        """Extract specific data using Llama with confidence scoring"""
        
        if extraction_type not in self.extraction_prompts:
            logger.error(f"Unknown extraction type: {extraction_type}")
            return LlamaExtractionResult(data={}, confidence=0.0, needs_escalation=True)
        
        # Get the appropriate prompt template
        prompt_template = self.extraction_prompts[extraction_type]
        prompt = prompt_template.format(text=text[:4000])  # Limit context to 4k tokens
        
        # Call Llama
        response = self.call_ollama(prompt)
        
        # Parse response and calculate confidence
        try:
            data = json.loads(response)
            confidence = self._calculate_extraction_confidence(data, extraction_type)
            
            # Determine if escalation needed
            needs_escalation = confidence < 0.7 or self._check_data_quality(data, extraction_type)
            escalation_reasons = []
            
            if confidence < 0.7:
                escalation_reasons.append(f"Low confidence: {confidence:.2f}")
            
            if extraction_type == 'address' and self._is_address_malformed(data):
                needs_escalation = True
                escalation_reasons.append("Malformed address detected")
            
            if extraction_type == 'financial' and not self._validate_financial_data(data):
                needs_escalation = True
                escalation_reasons.append("Financial data validation failed")
            
            return LlamaExtractionResult(
                data=data,
                confidence=confidence,
                needs_escalation=needs_escalation,
                escalation_reasons=escalation_reasons,
                raw_response=response
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Llama JSON response: {e}")
            return LlamaExtractionResult(
                data={},
                confidence=0.0,
                needs_escalation=True,
                escalation_reasons=["JSON parsing failed"],
                raw_response=response
            )
    
    def _calculate_extraction_confidence(self, data: Dict[str, Any], extraction_type: str) -> float:
        """Calculate confidence score for extracted data"""
        
        if not data:
            return 0.0
        
        # Count non-null fields
        total_fields = len(data)
        filled_fields = sum(1 for v in data.values() if v is not None and v != 0 and v != "")
        
        base_confidence = filled_fields / total_fields if total_fields > 0 else 0.0
        
        # Type-specific adjustments
        if extraction_type == 'basic_info':
            # High confidence if we have app number and project name
            if data.get('application_number') and data.get('project_name'):
                base_confidence = max(base_confidence, 0.8)
        
        elif extraction_type == 'units':
            # Check if unit mix sums to total
            total = data.get('total_units', 0)
            unit_mix = data.get('unit_mix', {})
            mix_sum = sum(unit_mix.values()) if isinstance(unit_mix, dict) else 0
            
            if total > 0 and mix_sum == total:
                base_confidence = max(base_confidence, 0.9)
            elif total > 0 and mix_sum > 0:
                # Partial credit if close
                ratio = min(mix_sum, total) / max(mix_sum, total)
                base_confidence *= ratio
        
        elif extraction_type == 'financial':
            # Check for critical fields
            critical_fields = ['total_development_cost', 'construction_cost', 'lihtc_equity']
            critical_present = sum(1 for f in critical_fields if data.get(f, 0) > 0)
            base_confidence *= (critical_present / len(critical_fields))
        
        return min(base_confidence, 1.0)
    
    def _check_data_quality(self, data: Dict[str, Any], extraction_type: str) -> bool:
        """Check if data quality issues require escalation"""
        
        if extraction_type == 'address':
            # Check for common Llama address parsing issues
            city = data.get('city', '')
            if len(city) < 3 or not city.replace(' ', '').isalpha():
                return True
            
            # Check for split addresses like "Dall, as" instead of "Dallas"
            if ',' in city or len(city.split()) > 3:
                return True
        
        elif extraction_type == 'financial':
            # Check for unrealistic values
            tdc = data.get('total_development_cost', 0)
            if tdc > 0:
                # Check if construction cost is reasonable % of TDC
                construction = data.get('construction_cost', 0)
                if construction > 0:
                    ratio = construction / tdc
                    if ratio < 0.4 or ratio > 0.8:
                        return True
        
        return False
    
    def _is_address_malformed(self, data: Dict[str, Any]) -> bool:
        """Check if address data is malformed"""
        street = data.get('street_address', '')
        city = data.get('city', '')
        
        # Common malformation patterns
        if '|' in street or '|' in city:
            return True
        if len(city) < 3:
            return True
        if ',' in city:  # City shouldn't contain commas
            return True
        if data.get('county') == 'Zip':  # Common extraction error
            return True
        
        return False
    
    def _validate_financial_data(self, data: Dict[str, Any]) -> bool:
        """Validate financial data for reasonableness"""
        tdc = data.get('total_development_cost', 0)
        
        if tdc == 0:
            return False
        
        # Sum of components shouldn't exceed TDC
        components = [
            data.get('land_cost', 0),
            data.get('construction_cost', 0),
            data.get('soft_costs', 0),
            data.get('developer_fee', 0)
        ]
        
        component_sum = sum(components)
        if component_sum > tdc * 1.1:  # Allow 10% margin
            return False
        
        # Developer fee typically 3-15% of TDC
        dev_fee = data.get('developer_fee', 0)
        if dev_fee > 0:
            fee_ratio = dev_fee / tdc
            if fee_ratio < 0.03 or fee_ratio > 0.15:
                return False
        
        return True
    
    def extract_with_ollama(self, text: str, app_number: str) -> UltimateProjectData:
        """Main extraction method using Ollama/Llama"""
        
        logger.info(f"🦙 Extracting with Llama 3.3 70B for app #{app_number}")
        
        # Initialize project data
        project = UltimateProjectData()
        project.application_number = app_number
        
        # Track what needs escalation
        escalation_needed = []
        
        # Extract each category
        extraction_types = ['basic_info', 'address', 'units', 'financial', 'team', 'dates']
        
        for ext_type in extraction_types:
            logger.info(f"  Extracting {ext_type}...")
            result = self.extract_with_llama(text, ext_type)
            
            if result.needs_escalation:
                escalation_needed.append({
                    'type': ext_type,
                    'reasons': result.escalation_reasons,
                    'confidence': result.confidence
                })
            
            # Merge extracted data into project object
            self._merge_extraction_result(project, result.data, ext_type)
        
        # Calculate overall confidence
        project = self._validate_and_score_confidence(project)
        
        # Add extraction metadata
        project.processing_notes.append(f"Extracted with Llama 3.3 70B")
        if escalation_needed:
            project.processing_notes.append(f"Needs escalation: {len(escalation_needed)} categories")
            for item in escalation_needed:
                project.validation_flags.append(f"{item['type']}: {', '.join(item['reasons'])}")
        
        return project
    
    def _merge_extraction_result(self, project: UltimateProjectData, 
                                data: Dict[str, Any], extraction_type: str) -> None:
        """Merge Llama extraction results into project data object"""
        
        if extraction_type == 'basic_info':
            project.project_name = data.get('project_name', '') or project.project_name
            project.development_type = data.get('development_type', '') or project.development_type
            project.property_type = data.get('property_type', '') or project.property_type
            project.targeted_population = data.get('targeted_population', '') or project.targeted_population
        
        elif extraction_type == 'address':
            project.street_address = data.get('street_address', '') or project.street_address
            project.city = data.get('city', '') or project.city
            project.county = data.get('county', '') or project.county
            project.state = data.get('state', 'TX')
            project.zip_code = data.get('zip_code', '') or project.zip_code
            project.census_tract = data.get('census_tract', '') or project.census_tract
            project.region = data.get('region', '') or project.region
            
            # Build full address
            if project.street_address and project.city:
                parts = [project.street_address, project.city, project.state]
                if project.zip_code:
                    parts.append(project.zip_code)
                project.full_address = ', '.join(parts)
        
        elif extraction_type == 'units':
            project.total_units = data.get('total_units', 0) or project.total_units
            project.unit_mix = data.get('unit_mix', {}) or project.unit_mix
            
            ami_breakdown = data.get('ami_breakdown', {})
            if ami_breakdown:
                project.ami_breakdown = ami_breakdown
        
        elif extraction_type == 'financial':
            project.total_development_cost = data.get('total_development_cost', 0) or project.total_development_cost
            project.land_cost_total = data.get('land_cost', 0) or project.land_cost_total
            project.total_construction_cost = data.get('construction_cost', 0) or project.total_construction_cost
            project.soft_costs_total = data.get('soft_costs', 0) or project.soft_costs_total
            project.developer_fee = data.get('developer_fee', 0) or project.developer_fee
            project.lihtc_equity = data.get('lihtc_equity', 0) or project.lihtc_equity
            project.first_lien_loan = data.get('first_lien_loan', 0) or project.first_lien_loan
            project.second_lien_loan = data.get('second_lien_loan', 0) or project.second_lien_loan
            
            # Calculate derived fields
            if project.total_units > 0:
                if project.total_development_cost > 0:
                    project.development_cost_per_unit = project.total_development_cost / project.total_units
                if project.total_construction_cost > 0:
                    project.construction_cost_per_unit = project.total_construction_cost / project.total_units
                if project.land_cost_total > 0:
                    project.land_cost_per_unit = project.land_cost_total / project.total_units
        
        elif extraction_type == 'team':
            project.developer_name = data.get('developer_name', '') or project.developer_name
            project.developer_contact = data.get('developer_contact', '') or project.developer_contact
            project.general_contractor = data.get('general_contractor', '') or project.general_contractor
            project.architect = data.get('architect', '') or project.architect
            project.management_company = data.get('management_company', '') or project.management_company
        
        elif extraction_type == 'dates':
            project.application_date = data.get('application_date', '') or project.application_date
            project.construction_start_date = data.get('construction_start', '') or project.construction_start_date
            project.placed_in_service_date = data.get('placed_in_service', '') or project.placed_in_service_date
            project.lease_up_start_date = data.get('lease_up_start', '') or project.lease_up_start_date
    
    def process_application(self, pdf_path: Path) -> Optional[UltimateProjectData]:
        """Process a single TDHCA application using Ollama/Llama"""
        
        logger.info(f"🦙 Processing {pdf_path.name} with Ollama Extractor")
        
        # Extract application number
        app_match = re.search(r'(\d{5})', pdf_path.name)
        if not app_match:
            logger.error(f"Could not extract application number from {pdf_path.name}")
            return None
        
        app_number = app_match.group(1)
        
        # Smart extract text (inherits from parent class)
        text, stats = self.smart_extract_pdf_text(pdf_path)
        if not text.strip():
            logger.error(f"No text extracted from {pdf_path.name}")
            return None
        
        # Extract with Ollama
        project_data = self.extract_with_ollama(text, app_number)
        
        # Add processing statistics
        project_data.processing_notes.extend([
            f"Smart extraction: {stats['efficiency_gain']*100:.1f}% pages skipped",
            f"Processed {stats['processed_pages']}/{stats['total_pages']} pages"
        ])
        
        logger.info(f"✅ Ollama extraction complete for {project_data.project_name or app_number} (confidence: {project_data.confidence_scores.get('overall', 0):.2f})")
        
        return project_data


def test_ollama_extractor():
    """Test the Ollama extractor on a sample file"""
    
    base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites")
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            print("❌ Ollama is not running. Please start Ollama first.")
            return
    except:
        print("❌ Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434")
        return
    
    extractor = OllamaTDHCAExtractor(base_path)
    
    # Test on Estates at Ferguson
    test_file = base_path / 'Successful_2023_Applications' / 'Dallas_Fort_Worth' / 'TDHCA_23461_Estates_at_Ferguson.pdf'
    
    if test_file.exists():
        print("🦙 Testing Ollama TDHCA Extractor")
        print("=" * 60)
        
        result = extractor.process_application(test_file)
        
        if result:
            print(f"✅ Extraction Successful!")
            print(f"Project: {result.project_name}")
            print(f"Address: {result.full_address}")
            print(f"Units: {result.total_units}")
            print(f"Confidence: {result.confidence_scores.get('overall', 0):.2f}")
            
            if result.validation_flags:
                print("\n⚠️ Validation Flags (may need Claude/Opus review):")
                for flag in result.validation_flags:
                    print(f"  - {flag}")
        else:
            print("❌ Extraction failed")
    else:
        print(f"❌ Test file not found: {test_file}")


if __name__ == "__main__":
    test_ollama_extractor()
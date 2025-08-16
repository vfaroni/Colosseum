#!/usr/bin/env python3
"""
Pipeline Manager - Offering Memorandum Extractor
Roman Engineering Standard: Built for 2000+ year reliability

Specialized extractor for offering memorandums with advanced parsing logic
for real estate investment documents and property marketing materials.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OMExtractionConfig:
    """Configuration for offering memorandum extraction"""
    enable_deep_parsing: bool = True
    extract_financial_projections: bool = True
    extract_market_analysis: bool = True
    extract_property_photos: bool = False
    confidence_threshold: float = 0.85
    
class OfferingMemorandumExtractor:
    """Specialized extractor for offering memorandum documents"""
    
    def __init__(self, config: Optional[OMExtractionConfig] = None):
        """Initialize offering memorandum extractor"""
        self.config = config or OMExtractionConfig()
        self.extraction_patterns = self._initialize_extraction_patterns()
        self.financial_keywords = self._initialize_financial_keywords()
        self.property_keywords = self._initialize_property_keywords()
        
        logger.info("OfferingMemorandumExtractor initialized with specialized parsing")
    
    def _initialize_extraction_patterns(self) -> Dict[str, Dict[str, str]]:
        """Initialize regex patterns for data extraction"""
        return {
            "property_identification": {
                "property_name": r"(?i)(?:property\s+name|name\s*:|\bname\b)\s*[:\-]?\s*([A-Za-z0-9\s\-\.,'&]+?)(?:\n|$|\s{3,})",
                "address": r"(?i)(?:address|location|situated|located)\s*[:\-]?\s*([0-9]+[^,\n]+,[^,\n]+(?:,[^,\n]+)?)",
                "unit_count": r"(?i)(?:total\s+units?|unit\s+count|\bunits?\b|number\s+of\s+units?)\s*[:\-]?\s*(\d{1,4})",
                "year_built": r"(?i)(?:built|constructed|year\s+built|construction\s+date)\s*[:\-]?\s*(\d{4})",
                "property_type": r"(?i)(?:property\s+type|type\s*:|building\s+type)\s*[:\-]?\s*([A-Za-z\s\-]+?)(?:\n|$|\s{3,})"
            },
            
            "financial_metrics": {
                "purchase_price": r"(?i)(?:purchase\s+price|asking\s+price|list\s+price|price)\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{2})?)",
                "noi": r"(?i)(?:noi|net\s+operating\s+income|annual\s+noi)\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{2})?)",
                "cap_rate": r"(?i)(?:cap\s+rate|capitalization\s+rate)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
                "gsi": r"(?i)(?:gsi|gross\s+scheduled\s+income|annual\s+income)\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{2})?)",
                "occupancy": r"(?i)(?:occupancy|occupied|occupancy\s+rate)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%",
                "grm": r"(?i)(?:grm|gross\s+rent\s+multiplier)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)"
            },
            
            "rent_information": {
                "average_rent": r"(?i)(?:average\s+rent|avg\s+rent|mean\s+rent)\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{2})?)",
                "studio_rent": r"(?i)(?:studio|0\s*br|efficiency)\s+rent\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{2})?)",
                "one_br_rent": r"(?i)(?:1\s*br|one\s+bedroom)\s+rent\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{2})?)",
                "two_br_rent": r"(?i)(?:2\s*br|two\s+bedroom)\s+rent\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{2})?)",
                "three_br_rent": r"(?i)(?:3\s*br|three\s+bedroom)\s+rent\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{2})?)"
            },
            
            "market_data": {
                "submarket": r"(?i)(?:submarket|neighborhood|area|district)\s*[:\-]?\s*([A-Za-z0-9\s\-\.,'&]+?)(?:\n|$|\s{3,})",
                "median_income": r"(?i)(?:median\s+household\s+income|median\s+income|ami)\s*[:\-]?\s*\$?([0-9,]+)",
                "population": r"(?i)(?:population|residents)\s*[:\-]?\s*([0-9,]+)",
                "employment_growth": r"(?i)(?:employment\s+growth|job\s+growth)\s*[:\-]?\s*([0-9\.]+)\s*%"
            },
            
            "transaction_details": {
                "broker_name": r"(?i)(?:broker|agent|listing\s+agent)\s*[:\-]?\s*([A-Za-z\s\-\.,'&]+?)(?:\n|$|phone|email)",
                "broker_company": r"(?i)(?:brokerage|company|firm)\s*[:\-]?\s*([A-Za-z0-9\s\-\.,'&]+?)(?:\n|$|\s{3,})",
                "broker_phone": r"(?i)(?:phone|tel|telephone)\s*[:\-]?\s*([0-9\-\.\(\)\s]+)",
                "broker_email": r"(?i)(?:email|e-mail)\s*[:\-]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                "days_on_market": r"(?i)(?:days\s+on\s+market|dom|market\s+time)\s*[:\-]?\s*(\d+)"
            }
        }
    
    def _initialize_financial_keywords(self) -> Dict[str, List[str]]:
        """Initialize financial analysis keywords"""
        return {
            "income_indicators": [
                "gross income", "rental income", "total income", "revenue",
                "gsi", "gross scheduled income", "effective gross income"
            ],
            "expense_indicators": [
                "operating expenses", "opex", "total expenses", "maintenance",
                "insurance", "taxes", "management fees", "utilities"
            ],
            "profitability_indicators": [
                "net operating income", "noi", "cash flow", "profit",
                "ebitda", "return", "yield", "cap rate"
            ],
            "financing_indicators": [
                "loan", "mortgage", "financing", "debt", "ltv", "dscr",
                "interest rate", "amortization", "principal"
            ]
        }
    
    def _initialize_property_keywords(self) -> Dict[str, List[str]]:
        """Initialize property analysis keywords"""
        return {
            "condition_indicators": [
                "excellent condition", "good condition", "fair condition",
                "renovated", "updated", "new", "recently improved"
            ],
            "amenity_indicators": [
                "pool", "fitness center", "gym", "parking", "laundry",
                "clubhouse", "playground", "balcony", "patio"
            ],
            "location_indicators": [
                "downtown", "suburban", "urban", "walkable", "transit",
                "highway access", "shopping", "schools", "employment"
            ],
            "investment_indicators": [
                "value-add", "stabilized", "core", "opportunistic",
                "appreciation potential", "upside", "renovation opportunity"
            ]
        }
    
    def extract_offering_memorandum_data(self, content: str) -> Dict[str, Any]:
        """Extract comprehensive data from offering memorandum content"""
        logger.info("Starting specialized offering memorandum extraction")
        
        extracted_data = {
            "property_details": {},
            "financial_metrics": {},
            "rent_information": {},
            "market_data": {},
            "transaction_details": {},
            "additional_info": {},
            "_extraction_metadata": {
                "extraction_method": "specialized_om_extractor",
                "extraction_timestamp": datetime.now().isoformat(),
                "content_length": len(content),
                "confidence_factors": {}
            }
        }
        
        # Extract structured data using patterns
        self._extract_property_identification(content, extracted_data)
        self._extract_financial_metrics(content, extracted_data)
        self._extract_rent_information(content, extracted_data)
        self._extract_market_data(content, extracted_data)
        self._extract_transaction_details(content, extracted_data)
        
        # Advanced extraction features
        if self.config.enable_deep_parsing:
            self._extract_unit_mix(content, extracted_data)
            self._extract_amenities(content, extracted_data)
            self._extract_investment_analysis(content, extracted_data)
        
        if self.config.extract_financial_projections:
            self._extract_financial_projections(content, extracted_data)
        
        if self.config.extract_market_analysis:
            self._extract_market_analysis(content, extracted_data)
        
        # Calculate extraction confidence
        self._calculate_extraction_confidence(extracted_data)
        
        logger.info(f"OM extraction completed with {len(self._count_extracted_fields(extracted_data))} fields")
        return extracted_data
    
    def _extract_property_identification(self, content: str, data: Dict[str, Any]):
        """Extract basic property identification information"""
        patterns = self.extraction_patterns["property_identification"]
        
        for field, pattern in patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                value = matches[0].strip()
                if field == "unit_count":
                    try:
                        value = int(value.replace(',', ''))
                    except ValueError:
                        continue
                elif field == "year_built":
                    try:
                        value = int(value)
                        if value < 1800 or value > datetime.now().year + 5:
                            continue
                    except ValueError:
                        continue
                
                data["property_details"][field] = value
                data["_extraction_metadata"]["confidence_factors"][f"property_{field}"] = len(matches)
    
    def _extract_financial_metrics(self, content: str, data: Dict[str, Any]):
        """Extract financial performance metrics"""
        patterns = self.extraction_patterns["financial_metrics"]
        
        for field, pattern in patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                value = matches[0].strip().replace(',', '').replace('$', '')
                
                try:
                    if field in ["purchase_price", "noi", "gsi"]:
                        value = float(value)
                    elif field in ["cap_rate", "occupancy"]:
                        value = float(value)
                        if field == "cap_rate" and value > 1:  # Convert percentage to decimal
                            value = value / 100
                        elif field == "occupancy" and value > 1:  # Convert percentage to decimal
                            value = value / 100
                    elif field == "grm":
                        value = float(value)
                    
                    data["financial_metrics"][field] = value
                    data["_extraction_metadata"]["confidence_factors"][f"financial_{field}"] = len(matches)
                
                except ValueError:
                    continue
    
    def _extract_rent_information(self, content: str, data: Dict[str, Any]):
        """Extract rental income information"""
        patterns = self.extraction_patterns["rent_information"]
        
        for field, pattern in patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                value = matches[0].strip().replace(',', '').replace('$', '')
                
                try:
                    value = float(value)
                    data["rent_information"][field] = value
                    data["_extraction_metadata"]["confidence_factors"][f"rent_{field}"] = len(matches)
                except ValueError:
                    continue
    
    def _extract_market_data(self, content: str, data: Dict[str, Any]):
        """Extract market and demographic information"""
        patterns = self.extraction_patterns["market_data"]
        
        for field, pattern in patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                value = matches[0].strip()
                
                if field in ["median_income", "population"]:
                    try:
                        value = int(value.replace(',', '').replace('$', ''))
                    except ValueError:
                        continue
                elif field == "employment_growth":
                    try:
                        value = float(value) / 100  # Convert to decimal
                    except ValueError:
                        continue
                
                data["market_data"][field] = value
                data["_extraction_metadata"]["confidence_factors"][f"market_{field}"] = len(matches)
    
    def _extract_transaction_details(self, content: str, data: Dict[str, Any]):
        """Extract transaction and broker information"""
        patterns = self.extraction_patterns["transaction_details"]
        
        for field, pattern in patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                value = matches[0].strip()
                
                if field == "days_on_market":
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                elif field == "broker_phone":
                    # Clean phone number
                    value = re.sub(r'[^\d\-\.\(\)\s]', '', value)
                
                data["transaction_details"][field] = value
                data["_extraction_metadata"]["confidence_factors"][f"transaction_{field}"] = len(matches)
    
    def _extract_unit_mix(self, content: str, data: Dict[str, Any]):
        """Extract unit mix information"""
        unit_mix = {}
        
        # Extract unit mix patterns
        unit_patterns = {
            "studio": r"(?i)(\d+)\s*(?:units?|#)?\s*(?:studio|efficiency|0\s*br)",
            "one_bedroom": r"(?i)(\d+)\s*(?:units?|#)?\s*(?:1\s*br|one\s*bedroom)",
            "two_bedroom": r"(?i)(\d+)\s*(?:units?|#)?\s*(?:2\s*br|two\s*bedroom)",
            "three_bedroom": r"(?i)(\d+)\s*(?:units?|#)?\s*(?:3\s*br|three\s*bedroom)",
            "four_bedroom": r"(?i)(\d+)\s*(?:units?|#)?\s*(?:4\s*br|four\s*bedroom)"
        }
        
        for unit_type, pattern in unit_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                try:
                    unit_mix[unit_type] = int(matches[0])
                except ValueError:
                    continue
        
        if unit_mix:
            data["property_details"]["unit_mix"] = unit_mix
            data["_extraction_metadata"]["confidence_factors"]["unit_mix"] = len(unit_mix)
    
    def _extract_amenities(self, content: str, data: Dict[str, Any]):
        """Extract property amenities"""
        amenities = []
        content_lower = content.lower()
        
        # Common amenity keywords
        amenity_keywords = [
            "swimming pool", "pool", "fitness center", "gym", "workout room",
            "clubhouse", "community room", "business center", "playground",
            "dog park", "pet area", "laundry room", "laundry facility",
            "parking garage", "covered parking", "carport", "storage",
            "balcony", "patio", "deck", "fireplace", "air conditioning",
            "dishwasher", "washer/dryer", "in-unit laundry"
        ]
        
        for amenity in amenity_keywords:
            if amenity in content_lower:
                amenities.append(amenity.title())
        
        if amenities:
            data["additional_info"]["amenities"] = list(set(amenities))  # Remove duplicates
            data["_extraction_metadata"]["confidence_factors"]["amenities"] = len(amenities)
    
    def _extract_investment_analysis(self, content: str, data: Dict[str, Any]):
        """Extract investment analysis and value-add opportunities"""
        analysis = {}
        content_lower = content.lower()
        
        # Investment strategy indicators
        strategy_keywords = {
            "value_add": ["value add", "value-add", "renovation", "improvement opportunity"],
            "core": ["core investment", "stabilized", "stable income"],
            "opportunistic": ["opportunistic", "distressed", "turnaround"],
            "development": ["development", "ground-up", "new construction"]
        }
        
        for strategy, keywords in strategy_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    analysis["investment_strategy"] = strategy
                    break
            if "investment_strategy" in analysis:
                break
        
        # Risk factors
        risk_keywords = ["deferred maintenance", "vacancy", "below market rents", "capital needs"]
        risks = [risk for risk in risk_keywords if risk in content_lower]
        if risks:
            analysis["identified_risks"] = risks
        
        # Upside potential
        upside_keywords = ["rent growth", "market rate", "below market", "renovation upside"]
        upside = [opportunity for opportunity in upside_keywords if opportunity in content_lower]
        if upside:
            analysis["upside_potential"] = upside
        
        if analysis:
            data["additional_info"]["investment_analysis"] = analysis
            data["_extraction_metadata"]["confidence_factors"]["investment_analysis"] = len(analysis)
    
    def _extract_financial_projections(self, content: str, data: Dict[str, Any]):
        """Extract financial projections and pro formas"""
        projections = {}
        
        # Look for year-over-year projections
        projection_patterns = {
            "year_1_noi": r"(?i)year\s+1.*noi.*\$?([0-9,]+)",
            "year_2_noi": r"(?i)year\s+2.*noi.*\$?([0-9,]+)",
            "stabilized_noi": r"(?i)stabilized.*noi.*\$?([0-9,]+)",
            "projected_value": r"(?i)projected\s+value.*\$?([0-9,]+)"
        }
        
        for field, pattern in projection_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                try:
                    value = float(matches[0].replace(',', ''))
                    projections[field] = value
                except ValueError:
                    continue
        
        if projections:
            data["financial_metrics"]["projections"] = projections
            data["_extraction_metadata"]["confidence_factors"]["projections"] = len(projections)
    
    def _extract_market_analysis(self, content: str, data: Dict[str, Any]):
        """Extract market analysis and comparable properties"""
        market_analysis = {}
        
        # Market trends
        if re.search(r"(?i)market\s+trends?", content):
            market_section = self._extract_section_content(content, "market trends", 500)
            if market_section:
                market_analysis["market_trends"] = market_section
        
        # Comparable properties
        comp_patterns = [
            r"(?i)comparable\s+(?:properties|sales)",
            r"(?i)comps?[:\s]",
            r"(?i)similar\s+properties"
        ]
        
        for pattern in comp_patterns:
            if re.search(pattern, content):
                comp_section = self._extract_section_content(content, pattern, 300)
                if comp_section:
                    market_analysis["comparable_properties"] = comp_section
                break
        
        if market_analysis:
            data["market_data"]["analysis"] = market_analysis
            data["_extraction_metadata"]["confidence_factors"]["market_analysis"] = len(market_analysis)
    
    def _extract_section_content(self, content: str, section_identifier: str, max_length: int = 500) -> Optional[str]:
        """Extract content from a specific section"""
        pattern = rf"(?i){re.escape(section_identifier)}[:\s]*(.*?)(?=\n\n|\n[A-Z][A-Z\s]*:|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            section_content = match.group(1).strip()
            return section_content[:max_length] if len(section_content) > max_length else section_content
        
        return None
    
    def _calculate_extraction_confidence(self, data: Dict[str, Any]):
        """Calculate overall extraction confidence score"""
        confidence_factors = data["_extraction_metadata"]["confidence_factors"]
        
        # Base confidence starts high for specialized extractor
        base_confidence = 0.85
        
        # Bonus for multiple matches of key fields
        key_fields = ["property_name", "purchase_price", "noi", "unit_count"]
        key_field_bonus = 0
        
        for field in key_fields:
            for category in confidence_factors:
                if field in category and confidence_factors[category] > 1:
                    key_field_bonus += 0.02  # 2% bonus per additional match
        
        # Bonus for data completeness
        total_fields = self._count_extracted_fields(data)
        completeness_bonus = min(total_fields * 0.005, 0.10)  # Up to 10% bonus
        
        # Final confidence calculation
        final_confidence = min(base_confidence + key_field_bonus + completeness_bonus, 1.0)
        data["_extraction_metadata"]["extraction_confidence"] = final_confidence
        
        logger.info(f"OM extraction confidence: {final_confidence:.3f}")
    
    def _count_extracted_fields(self, data: Dict[str, Any]) -> int:
        """Count total extracted fields"""
        count = 0
        for section_name, section_data in data.items():
            if section_name.startswith("_"):
                continue
            if isinstance(section_data, dict):
                count += len([v for v in section_data.values() if v is not None and v != ""])
        return count

# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = OfferingMemorandumExtractor()
    
    # Example content processing
    sample_content = """
    OFFERING MEMORANDUM
    
    Property Name: Sunset Apartments
    Address: 123 Main Street, Austin, TX 78701
    Total Units: 150
    Year Built: 1995
    
    Purchase Price: $18,500,000
    Net Operating Income: $1,200,000
    Cap Rate: 6.5%
    Occupancy Rate: 95%
    
    Average Rent: $1,250
    1BR Rent: $1,100
    2BR Rent: $1,400
    
    Submarket: Downtown Austin
    Median Household Income: $65,000
    
    Listing Broker: John Smith
    Broker Company: ABC Realty
    Phone: (512) 555-1234
    Email: john@abcrealty.com
    """
    
    # Extract data
    extracted_data = extractor.extract_offering_memorandum_data(sample_content)
    
    # Display results
    import json
    print(json.dumps(extracted_data, indent=2))
    
    logger.info("OfferingMemorandumExtractor ready for use")
#!/usr/bin/env python3
"""
Pipeline Manager - Rent Roll Extractor
Roman Engineering Standard: Built for 2000+ year reliability

Specialized extractor for rent rolls, tenant rosters, lease abstracts,
and unit-level rental data with advanced tenant analysis capabilities.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RentRollExtractionConfig:
    """Configuration for rent roll extraction"""
    extract_tenant_details: bool = True
    extract_lease_terms: bool = True
    extract_unit_details: bool = True
    calculate_analytics: bool = True
    confidence_threshold: float = 0.85

@dataclass
class UnitData:
    """Individual unit rental data"""
    unit_number: str
    tenant_name: Optional[str] = None
    lease_start: Optional[str] = None
    lease_end: Optional[str] = None
    monthly_rent: Optional[float] = None
    security_deposit: Optional[float] = None
    unit_type: Optional[str] = None
    square_footage: Optional[int] = None
    status: Optional[str] = None  # Occupied, Vacant, Notice, etc.

class RentRollExtractor:
    """Specialized extractor for rent roll and tenant roster documents"""
    
    def __init__(self, config: Optional[RentRollExtractionConfig] = None):
        """Initialize rent roll extractor"""
        self.config = config or RentRollExtractionConfig()
        self.unit_patterns = self._initialize_unit_patterns()
        self.tenant_patterns = self._initialize_tenant_patterns()
        self.financial_patterns = self._initialize_financial_patterns()
        self.status_keywords = self._initialize_status_keywords()
        
        logger.info("RentRollExtractor initialized with comprehensive parsing")
    
    def _initialize_unit_patterns(self) -> Dict[str, str]:
        """Initialize unit identification patterns"""
        return {
            "unit_number": r"(?i)(?:unit|apt|#)\s*([A-Z0-9\-]+)",
            "unit_type": r"(?i)([0-3])\s*(?:br|bed|bedroom)|(?:studio|efficiency)",
            "square_footage": r"(?i)(?:sq\s*ft|sqft|square\s*feet?)\s*[:\-]?\s*([0-9,]+)",
            "floor_plan": r"(?i)(?:floor\s*plan|plan\s*type)\s*[:\-]?\s*([A-Z0-9\-]+)"
        }
    
    def _initialize_tenant_patterns(self) -> Dict[str, str]:
        """Initialize tenant information patterns"""
        return {
            "tenant_name": r"(?i)(?:tenant|name)\s*[:\-]?\s*([A-Za-z\s\-\.']+?)(?:\s+\d|\n|$)",
            "phone": r"(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})",
            "email": r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            "move_in_date": r"(?i)(?:move\s*in|start|lease\s*start)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            "lease_end": r"(?i)(?:lease\s*end|expir\w+|term\s*end)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
        }
    
    def _initialize_financial_patterns(self) -> Dict[str, str]:
        """Initialize financial data patterns"""
        return {
            "monthly_rent": r"(?i)(?:rent|monthly)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "security_deposit": r"(?i)(?:security|deposit)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "pet_deposit": r"(?i)(?:pet\s*deposit|animal\s*deposit)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "application_fee": r"(?i)(?:application\s*fee|admin\s*fee)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "late_fees": r"(?i)(?:late\s*fee|penalty)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)"
        }
    
    def _initialize_status_keywords(self) -> Dict[str, List[str]]:
        """Initialize unit status keywords"""
        return {
            "occupied": ["occupied", "rented", "leased", "current"],
            "vacant": ["vacant", "empty", "available", "unoccupied"],
            "notice": ["notice", "30 day", "60 day", "moving", "vacating"],
            "maintenance": ["maintenance", "repair", "renovation", "make ready"],
            "model": ["model", "office", "leasing", "show"],
            "employee": ["employee", "manager", "staff", "maintenance"]
        }
    
    def extract_rent_roll_data(self, content: str) -> Dict[str, Any]:
        """Extract comprehensive data from rent roll content"""
        logger.info("Starting specialized rent roll extraction")
        
        extracted_data = {
            "property_summary": {},
            "unit_data": [],
            "tenant_summary": {},
            "financial_summary": {},
            "occupancy_analysis": {},
            "lease_expiration_analysis": {},
            "_extraction_metadata": {
                "extraction_method": "specialized_rent_roll_extractor",
                "extraction_timestamp": datetime.now().isoformat(),
                "content_length": len(content),
                "confidence_factors": {}
            }
        }
        
        # Extract individual unit data
        self._extract_unit_data(content, extracted_data)
        
        # Extract property-level summary
        self._extract_property_summary(content, extracted_data)
        
        # Advanced analysis features
        if self.config.calculate_analytics:
            self._calculate_rent_analytics(extracted_data)
            self._analyze_occupancy_patterns(extracted_data)
            self._analyze_lease_expirations(extracted_data)
        
        # Calculate extraction confidence
        self._calculate_extraction_confidence(extracted_data)
        
        logger.info(f"Rent roll extraction completed with {len(extracted_data['unit_data'])} units analyzed")
        return extracted_data
    
    def _extract_unit_data(self, content: str, data: Dict[str, Any]):
        """Extract individual unit rental data"""
        units = []
        
        # Split content into potential unit sections
        # Look for patterns that indicate unit boundaries
        unit_sections = self._identify_unit_sections(content)
        
        for section in unit_sections:
            unit = self._parse_unit_section(section)
            if unit and unit.unit_number:
                units.append(unit)
        
        # Convert UnitData objects to dictionaries
        data["unit_data"] = [self._unit_to_dict(unit) for unit in units]
        data["_extraction_metadata"]["confidence_factors"]["unit_count"] = len(units)
    
    def _identify_unit_sections(self, content: str) -> List[str]:
        """Identify individual unit sections in the content"""
        # Look for unit identifiers as section breaks
        unit_identifier_pattern = r"(?i)(?:^|\n)\s*(?:unit|apt|#)\s*[A-Z0-9\-]+.*?(?=(?:^|\n)\s*(?:unit|apt|#)|$)"
        
        sections = re.findall(unit_identifier_pattern, content, re.MULTILINE | re.DOTALL)
        
        # If no clear sections found, try table row approach
        if not sections:
            # Split by lines and look for rows with unit patterns
            lines = content.split('\n')
            sections = []
            current_section = []
            
            for line in lines:
                if re.search(r"(?i)(?:unit|apt|#)\s*[A-Z0-9\-]+", line):
                    if current_section:
                        sections.append('\n'.join(current_section))
                    current_section = [line]
                elif current_section and line.strip():
                    current_section.append(line)
            
            if current_section:
                sections.append('\n'.join(current_section))
        
        return sections
    
    def _parse_unit_section(self, section: str) -> Optional[UnitData]:
        """Parse individual unit section"""
        unit = UnitData(unit_number="")
        
        # Extract unit number
        unit_match = re.search(self.unit_patterns["unit_number"], section)
        if unit_match:
            unit.unit_number = unit_match.group(1)
        else:
            return None  # Must have unit number
        
        # Extract tenant information
        if self.config.extract_tenant_details:
            tenant_match = re.search(self.tenant_patterns["tenant_name"], section)
            if tenant_match:
                unit.tenant_name = tenant_match.group(1).strip()
            
            # Extract lease dates
            move_in_match = re.search(self.tenant_patterns["move_in_date"], section)
            if move_in_match:
                unit.lease_start = move_in_match.group(1)
            
            lease_end_match = re.search(self.tenant_patterns["lease_end"], section)
            if lease_end_match:
                unit.lease_end = lease_end_match.group(1)
        
        # Extract unit details
        if self.config.extract_unit_details:
            # Unit type (bedrooms)
            type_match = re.search(self.unit_patterns["unit_type"], section)
            if type_match:
                bedrooms = type_match.group(1) if type_match.group(1) else "0"
                unit.unit_type = f"{bedrooms}BR" if bedrooms.isdigit() else type_match.group(0)
            
            # Square footage
            sqft_match = re.search(self.unit_patterns["square_footage"], section)
            if sqft_match:
                try:
                    unit.square_footage = int(sqft_match.group(1).replace(',', ''))
                except ValueError:
                    pass
        
        # Extract financial information
        rent_match = re.search(self.financial_patterns["monthly_rent"], section)
        if rent_match:
            try:
                unit.monthly_rent = float(rent_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        deposit_match = re.search(self.financial_patterns["security_deposit"], section)
        if deposit_match:
            try:
                unit.security_deposit = float(deposit_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        # Determine unit status
        unit.status = self._determine_unit_status(section, unit.tenant_name)
        
        return unit
    
    def _determine_unit_status(self, section: str, tenant_name: Optional[str]) -> str:
        """Determine unit occupancy status"""
        section_lower = section.lower()
        
        # Check for explicit status keywords
        for status, keywords in self.status_keywords.items():
            for keyword in keywords:
                if keyword in section_lower:
                    return status.title()
        
        # Infer status from tenant information
        if not tenant_name or tenant_name.lower() in ["vacant", "available", ""]:
            return "Vacant"
        elif tenant_name.lower() in ["model", "office", "leasing"]:
            return "Model"
        else:
            return "Occupied"
    
    def _extract_property_summary(self, content: str, data: Dict[str, Any]):
        """Extract property-level summary information"""
        summary = {}
        
        # Extract total units
        total_units_patterns = [
            r"(?i)total\s+units?\s*[:\-]?\s*(\d+)",
            r"(?i)unit\s+count\s*[:\-]?\s*(\d+)",
            r"(?i)(\d+)\s+units?"
        ]
        
        for pattern in total_units_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    summary["total_units"] = int(match.group(1))
                    break
                except ValueError:
                    continue
        
        # Extract occupancy information
        occupancy_patterns = [
            r"(?i)occupancy\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*%",
            r"(?i)occupied\s*[:\-]?\s*(\d+)\s*(?:units?|of)",
            r"(?i)vacancy\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*%"
        ]
        
        for pattern in occupancy_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    value = float(match.group(1))
                    if "vacancy" in pattern:
                        summary["occupancy_rate"] = (100 - value) / 100
                    elif "occupied" in pattern:
                        if summary.get("total_units"):
                            summary["occupancy_rate"] = value / summary["total_units"]
                    else:
                        summary["occupancy_rate"] = value / 100
                    break
                except ValueError:
                    continue
        
        # Extract rent information
        avg_rent_patterns = [
            r"(?i)average\s+rent\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            r"(?i)avg\s+rent\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)"
        ]
        
        for pattern in avg_rent_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    summary["average_rent"] = float(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    continue
        
        if summary:
            data["property_summary"] = summary
            data["_extraction_metadata"]["confidence_factors"]["property_summary"] = len(summary)
    
    def _calculate_rent_analytics(self, data: Dict[str, Any]):
        """Calculate rent analytics from unit data"""
        units = data["unit_data"]
        occupied_units = [u for u in units if u.get("status") == "Occupied" and u.get("monthly_rent")]
        
        if not occupied_units:
            return
        
        rents = [u["monthly_rent"] for u in occupied_units]
        
        analytics = {
            "total_units": len(units),
            "occupied_units": len(occupied_units),
            "vacant_units": len([u for u in units if u.get("status") == "Vacant"]),
            "average_rent": statistics.mean(rents),
            "median_rent": statistics.median(rents),
            "min_rent": min(rents),
            "max_rent": max(rents),
            "total_monthly_income": sum(rents)
        }
        
        # Calculate occupancy rate
        if analytics["total_units"] > 0:
            analytics["occupancy_rate"] = analytics["occupied_units"] / analytics["total_units"]
            analytics["vacancy_rate"] = 1 - analytics["occupancy_rate"]
        
        # Calculate rent per square foot if available
        units_with_sqft = [u for u in occupied_units if u.get("square_footage")]
        if units_with_sqft:
            rent_per_sqft = [u["monthly_rent"] / u["square_footage"] for u in units_with_sqft]
            analytics["average_rent_per_sqft"] = statistics.mean(rent_per_sqft)
        
        # Unit type breakdown
        unit_types = {}
        for unit in units:
            unit_type = unit.get("unit_type", "Unknown")
            if unit_type not in unit_types:
                unit_types[unit_type] = {"count": 0, "occupied": 0, "avg_rent": 0}
            
            unit_types[unit_type]["count"] += 1
            if unit.get("status") == "Occupied":
                unit_types[unit_type]["occupied"] += 1
        
        # Calculate average rent by unit type
        for unit_type in unit_types:
            type_units = [u for u in occupied_units if u.get("unit_type") == unit_type]
            if type_units:
                unit_types[unit_type]["avg_rent"] = statistics.mean([u["monthly_rent"] for u in type_units])
        
        analytics["unit_type_breakdown"] = unit_types
        
        data["financial_summary"] = analytics
        data["_extraction_metadata"]["confidence_factors"]["rent_analytics"] = len(analytics)
    
    def _analyze_occupancy_patterns(self, data: Dict[str, Any]):
        """Analyze occupancy patterns and trends"""
        units = data["unit_data"]
        
        occupancy_analysis = {
            "status_distribution": {},
            "unit_type_occupancy": {},
            "rent_range_occupancy": {}
        }
        
        # Status distribution
        for unit in units:
            status = unit.get("status", "Unknown")
            occupancy_analysis["status_distribution"][status] = occupancy_analysis["status_distribution"].get(status, 0) + 1
        
        # Unit type occupancy rates
        unit_types = {}
        for unit in units:
            unit_type = unit.get("unit_type", "Unknown")
            if unit_type not in unit_types:
                unit_types[unit_type] = {"total": 0, "occupied": 0}
            
            unit_types[unit_type]["total"] += 1
            if unit.get("status") == "Occupied":
                unit_types[unit_type]["occupied"] += 1
        
        for unit_type, counts in unit_types.items():
            if counts["total"] > 0:
                occupancy_analysis["unit_type_occupancy"][unit_type] = counts["occupied"] / counts["total"]
        
        # Rent range occupancy
        occupied_units = [u for u in units if u.get("status") == "Occupied" and u.get("monthly_rent")]
        if occupied_units:
            rents = [u["monthly_rent"] for u in occupied_units]
            min_rent, max_rent = min(rents), max(rents)
            rent_range = max_rent - min_rent
            
            if rent_range > 0:
                # Create rent ranges
                ranges = {
                    "low": (min_rent, min_rent + rent_range * 0.33),
                    "medium": (min_rent + rent_range * 0.33, min_rent + rent_range * 0.67),
                    "high": (min_rent + rent_range * 0.67, max_rent)
                }
                
                for range_name, (low, high) in ranges.items():
                    range_units = [u for u in units if u.get("monthly_rent") and low <= u["monthly_rent"] <= high]
                    occupied_range_units = [u for u in range_units if u.get("status") == "Occupied"]
                    
                    if range_units:
                        occupancy_analysis["rent_range_occupancy"][range_name] = len(occupied_range_units) / len(range_units)
        
        data["occupancy_analysis"] = occupancy_analysis
        data["_extraction_metadata"]["confidence_factors"]["occupancy_analysis"] = len(occupancy_analysis)
    
    def _analyze_lease_expirations(self, data: Dict[str, Any]):
        """Analyze lease expiration patterns"""
        units = data["unit_data"]
        units_with_leases = [u for u in units if u.get("lease_end")]
        
        if not units_with_leases:
            return
        
        expiration_analysis = {
            "monthly_expirations": {},
            "quarterly_expirations": {},
            "annual_expirations": {},
            "lease_term_analysis": {}
        }
        
        # Parse lease end dates and group by periods
        for unit in units_with_leases:
            lease_end = unit.get("lease_end")
            if lease_end:
                try:
                    # Simple date parsing - would need more robust parsing in production
                    date_parts = lease_end.replace('/', '-').split('-')
                    if len(date_parts) >= 2:
                        month = int(date_parts[0]) if int(date_parts[0]) <= 12 else int(date_parts[1])
                        year = int(date_parts[2]) if len(date_parts[2]) == 4 else 2000 + int(date_parts[2])
                        
                        # Monthly analysis
                        month_key = f"{year}-{month:02d}"
                        expiration_analysis["monthly_expirations"][month_key] = expiration_analysis["monthly_expirations"].get(month_key, 0) + 1
                        
                        # Quarterly analysis
                        quarter = (month - 1) // 3 + 1
                        quarter_key = f"{year}-Q{quarter}"
                        expiration_analysis["quarterly_expirations"][quarter_key] = expiration_analysis["quarterly_expirations"].get(quarter_key, 0) + 1
                        
                        # Annual analysis
                        expiration_analysis["annual_expirations"][str(year)] = expiration_analysis["annual_expirations"].get(str(year), 0) + 1
                
                except (ValueError, IndexError):
                    continue
        
        data["lease_expiration_analysis"] = expiration_analysis
        data["_extraction_metadata"]["confidence_factors"]["lease_analysis"] = len(expiration_analysis)
    
    def _unit_to_dict(self, unit: UnitData) -> Dict[str, Any]:
        """Convert UnitData object to dictionary"""
        return {
            "unit_number": unit.unit_number,
            "tenant_name": unit.tenant_name,
            "lease_start": unit.lease_start,
            "lease_end": unit.lease_end,
            "monthly_rent": unit.monthly_rent,
            "security_deposit": unit.security_deposit,
            "unit_type": unit.unit_type,
            "square_footage": unit.square_footage,
            "status": unit.status
        }
    
    def _calculate_extraction_confidence(self, data: Dict[str, Any]):
        """Calculate overall extraction confidence score"""
        confidence_factors = data["_extraction_metadata"]["confidence_factors"]
        
        # Base confidence for rent roll extractor
        base_confidence = 0.85
        
        # Bonus for unit data quality
        units = data["unit_data"]
        if units:
            complete_units = len([u for u in units if u.get("monthly_rent") and u.get("status")])
            completeness_ratio = complete_units / len(units) if units else 0
            completeness_bonus = completeness_ratio * 0.10
        else:
            completeness_bonus = 0
        
        # Bonus for analytics
        analytics_sections = ["financial_summary", "occupancy_analysis", "lease_expiration_analysis"]
        analytics_bonus = sum(0.02 for section in analytics_sections if data.get(section)) 
        
        # Final confidence calculation
        final_confidence = min(base_confidence + completeness_bonus + analytics_bonus, 1.0)
        data["_extraction_metadata"]["extraction_confidence"] = final_confidence
        
        logger.info(f"Rent roll extraction confidence: {final_confidence:.3f}")
    
    def generate_rent_roll_summary(self, data: Dict[str, Any]) -> str:
        """Generate human-readable rent roll summary"""
        summary = []
        summary.append("=" * 50)
        summary.append("RENT ROLL SUMMARY")
        summary.append("=" * 50)
        
        # Property overview
        financial = data.get("financial_summary", {})
        if financial:
            summary.append(f"Total Units: {financial.get('total_units', 'N/A')}")
            summary.append(f"Occupied Units: {financial.get('occupied_units', 'N/A')}")
            summary.append(f"Occupancy Rate: {financial.get('occupancy_rate', 0):.1%}")
            summary.append(f"Average Rent: ${financial.get('average_rent', 0):,.2f}")
            summary.append(f"Total Monthly Income: ${financial.get('total_monthly_income', 0):,.2f}")
            summary.append("")
        
        # Unit type breakdown
        if financial.get("unit_type_breakdown"):
            summary.append("UNIT TYPE BREAKDOWN:")
            summary.append("-" * 25)
            for unit_type, data in financial["unit_type_breakdown"].items():
                occupancy = data["occupied"] / data["count"] if data["count"] > 0 else 0
                avg_rent = data.get("avg_rent", 0)
                summary.append(f"{unit_type}: {data['occupied']}/{data['count']} occupied ({occupancy:.1%}), Avg Rent: ${avg_rent:,.0f}")
            summary.append("")
        
        # Occupancy analysis
        occupancy = data.get("occupancy_analysis", {})
        if occupancy.get("status_distribution"):
            summary.append("STATUS DISTRIBUTION:")
            summary.append("-" * 20)
            for status, count in occupancy["status_distribution"].items():
                summary.append(f"{status}: {count} units")
        
        return "\n".join(summary)

# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = RentRollExtractor()
    
    # Example content processing
    sample_content = """
    RENT ROLL REPORT
    As of December 31, 2023
    
    Total Units: 150
    Occupied Units: 143
    Occupancy Rate: 95.3%
    
    Unit 101 | John Smith | 1BR | $1,200 | Occupied | Lease End: 06/30/2024
    Unit 102 | Mary Johnson | 2BR | $1,450 | Occupied | Lease End: 08/15/2024
    Unit 103 | Vacant | 1BR | $1,150 | Available | 
    Unit 104 | Bob Wilson | 2BR | $1,500 | Notice | Lease End: 03/31/2024
    """
    
    # Extract data
    extracted_data = extractor.extract_rent_roll_data(sample_content)
    
    # Generate summary
    summary = extractor.generate_rent_roll_summary(extracted_data)
    print(summary)
    
    logger.info("RentRollExtractor ready for use")
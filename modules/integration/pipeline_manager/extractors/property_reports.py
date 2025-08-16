#!/usr/bin/env python3
"""
Pipeline Manager - Property Reports Extractor
Roman Engineering Standard: Built for 2000+ year reliability

Specialized extractor for property condition reports, appraisals, inspection reports,
and physical property assessments with comprehensive analysis capabilities.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyCondition(Enum):
    """Property condition classifications"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"

@dataclass
class PropertyReportConfig:
    """Configuration for property report extraction"""
    extract_condition_details: bool = True
    extract_valuation_data: bool = True
    extract_improvement_needs: bool = True
    extract_comparable_data: bool = True
    confidence_threshold: float = 0.80

class PropertyReportsExtractor:
    """Specialized extractor for property condition and valuation reports"""
    
    def __init__(self, config: Optional[PropertyReportConfig] = None):
        """Initialize property reports extractor"""
        self.config = config or PropertyReportConfig()
        self.physical_patterns = self._initialize_physical_patterns()
        self.condition_patterns = self._initialize_condition_patterns()
        self.valuation_patterns = self._initialize_valuation_patterns()
        self.improvement_patterns = self._initialize_improvement_patterns()
        self.comparable_patterns = self._initialize_comparable_patterns()
        
        logger.info("PropertyReportsExtractor initialized with comprehensive analysis")
    
    def _initialize_physical_patterns(self) -> Dict[str, str]:
        """Initialize physical property characteristic patterns"""
        return {
            "building_area": r"(?i)(?:building\s+area|gross\s+building|total\s+area)\s*[:\-]?\s*([0-9,]+)\s*(?:sq\s*ft|square\s*feet?)",
            "lot_size": r"(?i)(?:lot\s+size|parcel\s+size|land\s+area)\s*[:\-]?\s*([0-9,\.]+)\s*(?:acres?|sq\s*ft|square\s*feet?)",
            "parking_spaces": r"(?i)(?:parking\s+spaces?|parking\s+count)\s*[:\-]?\s*(\d+)",
            "stories": r"(?i)(?:stories|floors?)\s*[:\-]?\s*(\d+)",
            "elevators": r"(?i)(?:elevators?)\s*[:\-]?\s*(\d+)",
            "balconies": r"(?i)(?:balconies|patios?)\s*[:\-]?\s*(\d+)",
            "laundry_facilities": r"(?i)(?:laundry\s+facilities?|laundry\s+rooms?)\s*[:\-]?\s*(\d+)",
            "construction_type": r"(?i)(?:construction\s+type|building\s+type)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})",
            "roof_type": r"(?i)(?:roof\s+type|roofing)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})",
            "exterior_material": r"(?i)(?:exterior|siding|facade)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})"
        }
    
    def _initialize_condition_patterns(self) -> Dict[str, str]:
        """Initialize condition assessment patterns"""
        return {
            "overall_condition": r"(?i)(?:overall\s+condition|property\s+condition|general\s+condition)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})",
            "roof_condition": r"(?i)(?:roof\s+condition|roofing\s+condition)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})",
            "hvac_condition": r"(?i)(?:hvac|heating|cooling|air\s+conditioning)\s+condition\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})",
            "plumbing_condition": r"(?i)(?:plumbing\s+condition|plumbing)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})",
            "electrical_condition": r"(?i)(?:electrical\s+condition|electrical)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})",
            "flooring_condition": r"(?i)(?:flooring\s+condition|floors?)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})",
            "exterior_condition": r"(?i)(?:exterior\s+condition|building\s+exterior)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})",
            "windows_condition": r"(?i)(?:windows?\s+condition|glazing)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})",
            "foundation_condition": r"(?i)(?:foundation\s+condition|foundation)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|\s{3,})"
        }
    
    def _initialize_valuation_patterns(self) -> Dict[str, str]:
        """Initialize valuation and appraisal patterns"""
        return {
            "appraised_value": r"(?i)(?:appraised\s+value|market\s+value|fair\s+market\s+value)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "assessed_value": r"(?i)(?:assessed\s+value|tax\s+assessed)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "replacement_cost": r"(?i)(?:replacement\s+cost|reproduction\s+cost)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "land_value": r"(?i)(?:land\s+value|site\s+value)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "improvement_value": r"(?i)(?:improvement\s+value|building\s+value)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "cost_per_unit": r"(?i)(?:cost\s+per\s+unit|price\s+per\s+unit)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "cost_per_sqft": r"(?i)(?:cost\s+per\s+sq\s*ft|price\s+per\s+square\s+foot)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "depreciation": r"(?i)(?:depreciation|accumulated\s+depreciation)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)"
        }
    
    def _initialize_improvement_patterns(self) -> Dict[str, str]:
        """Initialize capital improvement and maintenance patterns"""
        return {
            "immediate_repairs": r"(?i)(?:immediate\s+repairs?|urgent\s+repairs?|critical\s+items?)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "short_term_repairs": r"(?i)(?:short\s+term|1\s*year|12\s*months?)\s+(?:repairs?|improvements?)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "long_term_repairs": r"(?i)(?:long\s+term|5\s*year|future)\s+(?:repairs?|improvements?)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "total_repairs": r"(?i)(?:total\s+repairs?|total\s+improvements?|total\s+capital)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "roof_replacement": r"(?i)(?:roof\s+replacement|new\s+roof)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "hvac_replacement": r"(?i)(?:hvac\s+replacement|new\s+hvac)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "flooring_replacement": r"(?i)(?:flooring\s+replacement|new\s+flooring)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "exterior_improvements": r"(?i)(?:exterior\s+improvements?|facade\s+work)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)"
        }
    
    def _initialize_comparable_patterns(self) -> Dict[str, str]:
        """Initialize comparable sales patterns"""
        return {
            "comparable_sale_price": r"(?i)(?:comparable\s+sale|comp\s+sale|recent\s+sale)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "price_per_unit_comp": r"(?i)(?:comp|comparable)\s+price\s+per\s+unit\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "price_per_sqft_comp": r"(?i)(?:comp|comparable)\s+price\s+per\s+sq\s*ft\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "cap_rate_comp": r"(?i)(?:comp|comparable)\s+cap\s+rate\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
            "sale_date": r"(?i)(?:sale\s+date|sold\s+date)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
        }
    
    def extract_property_report_data(self, content: str) -> Dict[str, Any]:
        """Extract comprehensive data from property report content"""
        logger.info("Starting specialized property report extraction")
        
        extracted_data = {
            "physical_characteristics": {},
            "condition_assessment": {},
            "valuation_data": {},
            "improvement_analysis": {},
            "comparable_analysis": {},
            "property_summary": {},
            "_extraction_metadata": {
                "extraction_method": "specialized_property_report_extractor",
                "extraction_timestamp": datetime.now().isoformat(),
                "content_length": len(content),
                "confidence_factors": {}
            }
        }
        
        # Extract main components
        self._extract_physical_characteristics(content, extracted_data)
        self._extract_condition_assessment(content, extracted_data)
        
        if self.config.extract_valuation_data:
            self._extract_valuation_data(content, extracted_data)
        
        if self.config.extract_improvement_needs:
            self._extract_improvement_analysis(content, extracted_data)
        
        if self.config.extract_comparable_data:
            self._extract_comparable_analysis(content, extracted_data)
        
        # Advanced analysis
        self._analyze_investment_metrics(extracted_data)
        self._assess_overall_condition(extracted_data)
        self._calculate_value_indicators(extracted_data)
        
        # Calculate extraction confidence
        self._calculate_extraction_confidence(extracted_data)
        
        logger.info(f"Property report extraction completed with {self._count_extracted_fields(extracted_data)} fields")
        return extracted_data
    
    def _extract_physical_characteristics(self, content: str, data: Dict[str, Any]):
        """Extract physical property characteristics"""
        for field, pattern in self.physical_patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                value = matches[0].strip()
                
                # Convert numeric fields
                if field in ["building_area", "parking_spaces", "stories", "elevators", "balconies", "laundry_facilities"]:
                    try:
                        value = int(value.replace(',', ''))
                    except ValueError:
                        continue
                elif field == "lot_size":
                    try:
                        value = float(value.replace(',', ''))
                    except ValueError:
                        continue
                
                data["physical_characteristics"][field] = value
                data["_extraction_metadata"]["confidence_factors"][f"physical_{field}"] = len(matches)
    
    def _extract_condition_assessment(self, content: str, data: Dict[str, Any]):
        """Extract condition assessment information"""
        for field, pattern in self.condition_patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                condition = matches[0].strip().lower()
                
                # Normalize condition descriptions
                normalized_condition = self._normalize_condition(condition)
                
                data["condition_assessment"][field] = {
                    "raw_description": matches[0].strip(),
                    "normalized_condition": normalized_condition.value,
                    "condition_score": self._condition_to_score(normalized_condition)
                }
                data["_extraction_metadata"]["confidence_factors"][f"condition_{field}"] = len(matches)
    
    def _extract_valuation_data(self, content: str, data: Dict[str, Any]):
        """Extract valuation and appraisal data"""
        for field, pattern in self.valuation_patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                try:
                    value = float(matches[0].replace(',', '').replace('$', ''))
                    data["valuation_data"][field] = value
                    data["_extraction_metadata"]["confidence_factors"][f"valuation_{field}"] = len(matches)
                except ValueError:
                    continue
    
    def _extract_improvement_analysis(self, content: str, data: Dict[str, Any]):
        """Extract capital improvement and repair cost analysis"""
        improvements = {}
        repair_items = []
        
        for field, pattern in self.improvement_patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                try:
                    value = float(matches[0].replace(',', '').replace('$', ''))
                    improvements[field] = value
                except ValueError:
                    continue
        
        # Extract specific repair items
        repair_item_patterns = [
            r"(?i)repair\s+needed\s*[:\-]?\s*([^,\n]+)",
            r"(?i)maintenance\s+item\s*[:\-]?\s*([^,\n]+)",
            r"(?i)replacement\s+needed\s*[:\-]?\s*([^,\n]+)"
        ]
        
        for pattern in repair_item_patterns:
            matches = re.findall(pattern, content)
            repair_items.extend([item.strip() for item in matches])
        
        if improvements:
            data["improvement_analysis"]["cost_estimates"] = improvements
        
        if repair_items:
            data["improvement_analysis"]["repair_items"] = list(set(repair_items))  # Remove duplicates
        
        if improvements or repair_items:
            data["_extraction_metadata"]["confidence_factors"]["improvement_analysis"] = len(improvements) + len(repair_items)
    
    def _extract_comparable_analysis(self, content: str, data: Dict[str, Any]):
        """Extract comparable sales and market data"""
        comparables = {}
        
        for field, pattern in self.comparable_patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                value = matches[0].strip()
                
                if field in ["comparable_sale_price", "price_per_unit_comp", "price_per_sqft_comp"]:
                    try:
                        value = float(value.replace(',', '').replace('$', ''))
                    except ValueError:
                        continue
                elif field == "cap_rate_comp":
                    try:
                        value = float(value)
                        if value > 1:  # Convert percentage to decimal
                            value = value / 100
                    except ValueError:
                        continue
                
                comparables[field] = value
        
        if comparables:
            data["comparable_analysis"] = comparables
            data["_extraction_metadata"]["confidence_factors"]["comparable_analysis"] = len(comparables)
    
    def _normalize_condition(self, condition_text: str) -> PropertyCondition:
        """Normalize condition descriptions to standard categories"""
        condition_lower = condition_text.lower()
        
        excellent_keywords = ["excellent", "superior", "like new", "new", "pristine"]
        good_keywords = ["good", "well maintained", "above average", "satisfactory"]
        fair_keywords = ["fair", "average", "adequate", "typical"]
        poor_keywords = ["poor", "below average", "needs work", "deteriorated", "worn"]
        
        for keyword in excellent_keywords:
            if keyword in condition_lower:
                return PropertyCondition.EXCELLENT
        
        for keyword in good_keywords:
            if keyword in condition_lower:
                return PropertyCondition.GOOD
        
        for keyword in fair_keywords:
            if keyword in condition_lower:
                return PropertyCondition.FAIR
        
        for keyword in poor_keywords:
            if keyword in condition_lower:
                return PropertyCondition.POOR
        
        return PropertyCondition.UNKNOWN
    
    def _condition_to_score(self, condition: PropertyCondition) -> float:
        """Convert condition to numeric score (0-1)"""
        condition_scores = {
            PropertyCondition.EXCELLENT: 1.0,
            PropertyCondition.GOOD: 0.75,
            PropertyCondition.FAIR: 0.5,
            PropertyCondition.POOR: 0.25,
            PropertyCondition.UNKNOWN: 0.5
        }
        return condition_scores.get(condition, 0.5)
    
    def _analyze_investment_metrics(self, data: Dict[str, Any]):
        """Analyze investment metrics from extracted data"""
        valuation = data.get("valuation_data", {})
        physical = data.get("physical_characteristics", {})
        improvements = data.get("improvement_analysis", {}).get("cost_estimates", {})
        
        metrics = {}
        
        # Calculate improvement-adjusted value
        appraised_value = valuation.get("appraised_value")
        total_improvements = improvements.get("total_repairs", 0)
        
        if appraised_value and total_improvements:
            metrics["net_value_after_improvements"] = appraised_value - total_improvements
            metrics["improvement_to_value_ratio"] = total_improvements / appraised_value
        
        # Calculate per-unit metrics
        building_area = physical.get("building_area")
        if appraised_value and building_area:
            metrics["value_per_sqft"] = appraised_value / building_area
        
        # Calculate land-to-improvement ratio
        land_value = valuation.get("land_value")
        improvement_value = valuation.get("improvement_value")
        
        if land_value and improvement_value:
            total_value = land_value + improvement_value
            metrics["land_to_total_ratio"] = land_value / total_value
            metrics["improvement_to_total_ratio"] = improvement_value / total_value
        
        if metrics:
            data["property_summary"]["investment_metrics"] = metrics
            data["_extraction_metadata"]["confidence_factors"]["investment_metrics"] = len(metrics)
    
    def _assess_overall_condition(self, data: Dict[str, Any]):
        """Assess overall property condition from component conditions"""
        conditions = data.get("condition_assessment", {})
        
        if not conditions:
            return
        
        # Calculate average condition score
        condition_scores = []
        critical_systems = ["roof_condition", "hvac_condition", "plumbing_condition", "electrical_condition"]
        
        for system, condition_data in conditions.items():
            if isinstance(condition_data, dict) and "condition_score" in condition_data:
                score = condition_data["condition_score"]
                # Weight critical systems more heavily
                weight = 2.0 if system in critical_systems else 1.0
                condition_scores.extend([score] * int(weight))
        
        if condition_scores:
            avg_score = sum(condition_scores) / len(condition_scores)
            
            # Convert back to condition category
            if avg_score >= 0.875:
                overall_condition = PropertyCondition.EXCELLENT
            elif avg_score >= 0.625:
                overall_condition = PropertyCondition.GOOD
            elif avg_score >= 0.375:
                overall_condition = PropertyCondition.FAIR
            else:
                overall_condition = PropertyCondition.POOR
            
            data["property_summary"]["overall_condition"] = {
                "condition": overall_condition.value,
                "condition_score": avg_score,
                "systems_evaluated": len(conditions)
            }
            
            data["_extraction_metadata"]["confidence_factors"]["overall_condition"] = 1
    
    def _calculate_value_indicators(self, data: Dict[str, Any]):
        """Calculate value indicators and investment attractiveness"""
        valuation = data.get("valuation_data", {})
        comparables = data.get("comparable_analysis", {})
        improvements = data.get("improvement_analysis", {}).get("cost_estimates", {})
        
        indicators = {}
        
        # Value vs comparable analysis
        appraised_value = valuation.get("appraised_value")
        comp_price = comparables.get("comparable_sale_price")
        
        if appraised_value and comp_price:
            value_variance = (appraised_value - comp_price) / comp_price
            indicators["value_vs_comparable"] = value_variance
            
            if value_variance < -0.1:
                indicators["value_assessment"] = "Below Market"
            elif value_variance > 0.1:
                indicators["value_assessment"] = "Above Market"
            else:
                indicators["value_assessment"] = "Market Rate"
        
        # Improvement needs assessment
        total_improvements = improvements.get("total_repairs", 0)
        immediate_repairs = improvements.get("immediate_repairs", 0)
        
        if appraised_value:
            if total_improvements:
                improvement_ratio = total_improvements / appraised_value
                indicators["total_improvement_ratio"] = improvement_ratio
                
                if improvement_ratio > 0.2:
                    indicators["improvement_needs"] = "High"
                elif improvement_ratio > 0.1:
                    indicators["improvement_needs"] = "Moderate"
                else:
                    indicators["improvement_needs"] = "Low"
            
            if immediate_repairs:
                immediate_ratio = immediate_repairs / appraised_value
                indicators["immediate_repair_ratio"] = immediate_ratio
                
                if immediate_ratio > 0.05:
                    indicators["immediate_attention"] = "Required"
                else:
                    indicators["immediate_attention"] = "Not Critical"
        
        if indicators:
            data["property_summary"]["value_indicators"] = indicators
            data["_extraction_metadata"]["confidence_factors"]["value_indicators"] = len(indicators)
    
    def _calculate_extraction_confidence(self, data: Dict[str, Any]):
        """Calculate overall extraction confidence score"""
        confidence_factors = data["_extraction_metadata"]["confidence_factors"]
        
        # Base confidence for property report extractor
        base_confidence = 0.80
        
        # Bonus for comprehensive data sections
        major_sections = ["physical_characteristics", "condition_assessment", "valuation_data"]
        section_bonus = sum(0.05 for section in major_sections if data.get(section))
        
        # Bonus for analysis completeness
        analysis_sections = ["improvement_analysis", "comparable_analysis", "property_summary"]
        analysis_bonus = sum(0.02 for section in analysis_sections if data.get(section))
        
        # Final confidence calculation
        final_confidence = min(base_confidence + section_bonus + analysis_bonus, 1.0)
        data["_extraction_metadata"]["extraction_confidence"] = final_confidence
        
        logger.info(f"Property report extraction confidence: {final_confidence:.3f}")
    
    def _count_extracted_fields(self, data: Dict[str, Any]) -> int:
        """Count total extracted fields"""
        count = 0
        for section_name, section_data in data.items():
            if section_name.startswith("_"):
                continue
            if isinstance(section_data, dict):
                count += len([v for v in section_data.values() if v is not None and v != ""])
        return count
    
    def generate_property_report_summary(self, data: Dict[str, Any]) -> str:
        """Generate human-readable property report summary"""
        summary = []
        summary.append("=" * 50)
        summary.append("PROPERTY REPORT SUMMARY")
        summary.append("=" * 50)
        
        # Physical characteristics
        physical = data.get("physical_characteristics", {})
        if physical:
            summary.append("PHYSICAL CHARACTERISTICS:")
            summary.append("-" * 25)
            
            building_area = physical.get("building_area")
            if building_area:
                summary.append(f"Building Area: {building_area:,} sq ft")
            
            lot_size = physical.get("lot_size")
            if lot_size:
                summary.append(f"Lot Size: {lot_size:,.2f} acres")
            
            stories = physical.get("stories")
            if stories:
                summary.append(f"Stories: {stories}")
            
            parking = physical.get("parking_spaces")
            if parking:
                summary.append(f"Parking Spaces: {parking}")
            
            summary.append("")
        
        # Overall condition
        prop_summary = data.get("property_summary", {})
        overall_condition = prop_summary.get("overall_condition")
        if overall_condition:
            summary.append("CONDITION ASSESSMENT:")
            summary.append("-" * 20)
            summary.append(f"Overall Condition: {overall_condition['condition'].title()}")
            summary.append(f"Condition Score: {overall_condition['condition_score']:.2f}/1.00")
            summary.append(f"Systems Evaluated: {overall_condition['systems_evaluated']}")
            summary.append("")
        
        # Valuation data
        valuation = data.get("valuation_data", {})
        if valuation:
            summary.append("VALUATION DATA:")
            summary.append("-" * 15)
            
            appraised_value = valuation.get("appraised_value")
            if appraised_value:
                summary.append(f"Appraised Value: ${appraised_value:,.0f}")
            
            land_value = valuation.get("land_value")
            if land_value:
                summary.append(f"Land Value: ${land_value:,.0f}")
            
            improvement_value = valuation.get("improvement_value")
            if improvement_value:
                summary.append(f"Improvement Value: ${improvement_value:,.0f}")
            
            summary.append("")
        
        # Investment metrics
        investment_metrics = prop_summary.get("investment_metrics")
        if investment_metrics:
            summary.append("INVESTMENT ANALYSIS:")
            summary.append("-" * 20)
            
            for metric, value in investment_metrics.items():
                if isinstance(value, float):
                    if "ratio" in metric:
                        summary.append(f"{metric.replace('_', ' ').title()}: {value:.2%}")
                    else:
                        summary.append(f"{metric.replace('_', ' ').title()}: ${value:,.0f}")
        
        return "\n".join(summary)

# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = PropertyReportsExtractor()
    
    # Example content processing
    sample_content = """
    PROPERTY CONDITION REPORT
    
    PHYSICAL CHARACTERISTICS:
    Building Area: 125,000 sq ft
    Lot Size: 2.5 acres
    Stories: 3
    Parking Spaces: 150
    Construction Type: Concrete and Steel
    
    CONDITION ASSESSMENT:
    Overall Condition: Good
    Roof Condition: Fair - needs replacement in 2-3 years
    HVAC Condition: Good - recently serviced
    Plumbing Condition: Good
    Electrical Condition: Fair - panel upgrade needed
    
    VALUATION DATA:
    Appraised Value: $18,500,000
    Land Value: $3,200,000
    Improvement Value: $15,300,000
    
    IMPROVEMENT ANALYSIS:
    Immediate Repairs: $125,000
    Short Term Repairs: $350,000
    Total Repairs: $475,000
    """
    
    # Extract data
    extracted_data = extractor.extract_property_report_data(sample_content)
    
    # Generate summary
    summary = extractor.generate_property_report_summary(extracted_data)
    print(summary)
    
    logger.info("PropertyReportsExtractor ready for use")
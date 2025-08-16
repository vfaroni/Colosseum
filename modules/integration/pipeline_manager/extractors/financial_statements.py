#!/usr/bin/env python3
"""
Pipeline Manager - Financial Statements Extractor
Roman Engineering Standard: Built for 2000+ year reliability

Specialized extractor for financial statements, profit & loss statements,
operating statements, and T-12 financial reports with advanced parsing.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
import calendar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FinancialExtractionConfig:
    """Configuration for financial statement extraction"""
    extract_monthly_data: bool = True
    extract_variance_analysis: bool = True
    extract_ratios: bool = True
    normalize_periods: bool = True
    confidence_threshold: float = 0.80

class FinancialStatementsExtractor:
    """Specialized extractor for financial statements and operating reports"""
    
    def __init__(self, config: Optional[FinancialExtractionConfig] = None):
        """Initialize financial statements extractor"""
        self.config = config or FinancialExtractionConfig()
        self.income_patterns = self._initialize_income_patterns()
        self.expense_patterns = self._initialize_expense_patterns()
        self.ratio_patterns = self._initialize_ratio_patterns()
        self.month_names = self._initialize_month_names()
        
        logger.info("FinancialStatementsExtractor initialized with comprehensive parsing")
    
    def _initialize_income_patterns(self) -> Dict[str, str]:
        """Initialize income recognition patterns"""
        return {
            "rental_income": r"(?i)(?:rental\s+income|rent\s+income|gross\s+rent)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "other_income": r"(?i)(?:other\s+income|miscellaneous\s+income|additional\s+income)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "laundry_income": r"(?i)(?:laundry\s+income|vending\s+income)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "parking_income": r"(?i)(?:parking\s+income|garage\s+income)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "pet_income": r"(?i)(?:pet\s+(?:income|fees?)|animal\s+fees?)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "application_fees": r"(?i)(?:application\s+fees?|admin\s+fees?)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "late_fees": r"(?i)(?:late\s+fees?|penalty\s+fees?)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "total_income": r"(?i)(?:total\s+income|gross\s+income|total\s+revenue)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "effective_gross_income": r"(?i)(?:effective\s+gross\s+income|egi)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)"
        }
    
    def _initialize_expense_patterns(self) -> Dict[str, str]:
        """Initialize expense recognition patterns"""
        return {
            "management_fees": r"(?i)(?:management\s+fees?|property\s+management)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "maintenance": r"(?i)(?:maintenance|repairs?|maintenance\s+&\s+repairs?)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "utilities": r"(?i)(?:utilities|electric|gas|water|sewer)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "insurance": r"(?i)(?:insurance|property\s+insurance)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "taxes": r"(?i)(?:property\s+taxes?|real\s+estate\s+taxes?|taxes?)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "landscaping": r"(?i)(?:landscaping|grounds\s+maintenance|lawn\s+care)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "snow_removal": r"(?i)(?:snow\s+removal|snow\s+plowing)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "pest_control": r"(?i)(?:pest\s+control|exterminating)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "advertising": r"(?i)(?:advertising|marketing|leasing\s+costs?)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "legal_professional": r"(?i)(?:legal|professional\s+fees?|accounting)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "supplies": r"(?i)(?:supplies|office\s+supplies)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "total_expenses": r"(?i)(?:total\s+(?:operating\s+)?expenses?|total\s+opex)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "net_operating_income": r"(?i)(?:net\s+operating\s+income|noi)\s*[:\-]?\s*\$?\s*([0-9,]+(?:\.[0-9]{2})?)"
        }
    
    def _initialize_ratio_patterns(self) -> Dict[str, str]:
        """Initialize financial ratio patterns"""
        return {
            "expense_ratio": r"(?i)(?:expense\s+ratio|operating\s+ratio)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
            "vacancy_rate": r"(?i)(?:vacancy\s+rate|vacant\s+rate)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
            "collection_rate": r"(?i)(?:collection\s+rate|collected\s+rate)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
            "occupancy_rate": r"(?i)(?:occupancy\s+rate|occupied\s+rate)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
            "cap_rate": r"(?i)(?:cap\s+rate|capitalization\s+rate)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%?"
        }
    
    def _initialize_month_names(self) -> Dict[str, int]:
        """Initialize month name mappings"""
        months = {}
        for i in range(1, 13):
            month_name = calendar.month_name[i].lower()
            month_abbr = calendar.month_abbr[i].lower()
            months[month_name] = i
            months[month_abbr] = i
        return months
    
    def extract_financial_statement_data(self, content: str) -> Dict[str, Any]:
        """Extract comprehensive data from financial statement content"""
        logger.info("Starting specialized financial statement extraction")
        
        extracted_data = {
            "income_statement": {},
            "expense_statement": {},
            "financial_ratios": {},
            "period_information": {},
            "monthly_data": {},
            "variance_analysis": {},
            "_extraction_metadata": {
                "extraction_method": "specialized_financial_extractor",
                "extraction_timestamp": datetime.now().isoformat(),
                "content_length": len(content),
                "confidence_factors": {}
            }
        }
        
        # Extract main financial components
        self._extract_income_data(content, extracted_data)
        self._extract_expense_data(content, extracted_data)
        self._extract_financial_ratios(content, extracted_data)
        self._extract_period_information(content, extracted_data)
        
        # Advanced extraction features
        if self.config.extract_monthly_data:
            self._extract_monthly_breakdown(content, extracted_data)
        
        if self.config.extract_variance_analysis:
            self._extract_variance_analysis(content, extracted_data)
        
        # Calculate derived metrics
        self._calculate_derived_metrics(extracted_data)
        
        # Calculate extraction confidence
        self._calculate_extraction_confidence(extracted_data)
        
        logger.info(f"Financial extraction completed with {self._count_extracted_fields(extracted_data)} fields")
        return extracted_data
    
    def _extract_income_data(self, content: str, data: Dict[str, Any]):
        """Extract income statement data"""
        for field, pattern in self.income_patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                try:
                    # Take the highest value if multiple matches (assumes most recent/comprehensive)
                    values = [float(match.replace(',', '').replace('$', '')) for match in matches]
                    value = max(values)
                    data["income_statement"][field] = value
                    data["_extraction_metadata"]["confidence_factors"][f"income_{field}"] = len(matches)
                except ValueError:
                    continue
    
    def _extract_expense_data(self, content: str, data: Dict[str, Any]):
        """Extract expense statement data"""
        for field, pattern in self.expense_patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                try:
                    # Take the highest value if multiple matches
                    values = [float(match.replace(',', '').replace('$', '')) for match in matches]
                    value = max(values)
                    data["expense_statement"][field] = value
                    data["_extraction_metadata"]["confidence_factors"][f"expense_{field}"] = len(matches)
                except ValueError:
                    continue
    
    def _extract_financial_ratios(self, content: str, data: Dict[str, Any]):
        """Extract financial ratios and percentages"""
        for field, pattern in self.ratio_patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                try:
                    value = float(matches[0])
                    # Convert percentages to decimals if value > 1
                    if value > 1 and field.endswith('_rate'):
                        value = value / 100
                    data["financial_ratios"][field] = value
                    data["_extraction_metadata"]["confidence_factors"][f"ratio_{field}"] = len(matches)
                except ValueError:
                    continue
    
    def _extract_period_information(self, content: str, data: Dict[str, Any]):
        """Extract reporting period information"""
        period_info = {}
        
        # Extract year information
        year_pattern = r"(?i)(?:year|annual|12\s*months?)\s+(?:ended?|ending)?\s*(?:december\s+31,?\s*)?(\d{4})"
        year_matches = re.findall(year_pattern, content)
        if year_matches:
            period_info["reporting_year"] = int(year_matches[0])
        
        # Extract period type
        period_patterns = {
            "annual": r"(?i)(?:annual|yearly|12\s*months?|year\s+ended)",
            "quarterly": r"(?i)(?:quarterly|quarter|3\s*months?)",
            "monthly": r"(?i)(?:monthly|month\s+ended?)",
            "ytd": r"(?i)(?:year\s+to\s+date|ytd)",
            "t12": r"(?i)(?:trailing\s+12|t-?12|12\s*months?\s+trailing)"
        }
        
        for period_type, pattern in period_patterns.items():
            if re.search(pattern, content):
                period_info["period_type"] = period_type
                break
        
        # Extract specific dates
        date_patterns = [
            r"(?i)(?:for\s+the\s+)?(?:period|year|quarter|month)\s+ended?\s+([a-z]+\s+\d{1,2},?\s+\d{4})",
            r"(?i)as\s+of\s+([a-z]+\s+\d{1,2},?\s+\d{4})",
            r"(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{4}-\d{2}-\d{2})"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            if matches:
                period_info["reporting_date"] = matches[0]
                break
        
        if period_info:
            data["period_information"] = period_info
            data["_extraction_metadata"]["confidence_factors"]["period_info"] = len(period_info)
    
    def _extract_monthly_breakdown(self, content: str, data: Dict[str, Any]):
        """Extract monthly financial data breakdown"""
        monthly_data = {}
        
        # Look for monthly tables or breakdowns
        for month_name, month_num in self.month_names.items():
            month_patterns = {
                "income": rf"(?i){month_name}.*?(?:income|revenue).*?\$?\s*([0-9,]+(?:\.[0-9]{{2}})?)",
                "expenses": rf"(?i){month_name}.*?(?:expenses?|costs?).*?\$?\s*([0-9,]+(?:\.[0-9]{{2}})?)",
                "noi": rf"(?i){month_name}.*?(?:noi|net\s+operating).*?\$?\s*([0-9,]+(?:\.[0-9]{{2}})?)"
            }
            
            month_data = {}
            for metric, pattern in month_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    try:
                        value = float(matches[0].replace(',', ''))
                        month_data[metric] = value
                    except ValueError:
                        continue
            
            if month_data:
                monthly_data[month_name] = month_data
        
        if monthly_data:
            data["monthly_data"] = monthly_data
            data["_extraction_metadata"]["confidence_factors"]["monthly_data"] = len(monthly_data)
    
    def _extract_variance_analysis(self, content: str, data: Dict[str, Any]):
        """Extract variance analysis data"""
        variance_data = {}
        
        # Look for budget vs actual comparisons
        variance_patterns = {
            "budget_income": r"(?i)budget(?:ed)?\s+income.*?\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "actual_income": r"(?i)actual\s+income.*?\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "budget_expenses": r"(?i)budget(?:ed)?\s+expenses?.*?\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "actual_expenses": r"(?i)actual\s+expenses?.*?\$?\s*([0-9,]+(?:\.[0-9]{2})?)",
            "variance_amount": r"(?i)variance.*?\$?\s*([+-]?[0-9,]+(?:\.[0-9]{2})?)",
            "variance_percent": r"(?i)variance.*?([+-]?[0-9]+(?:\.[0-9]+)?)\s*%"
        }
        
        for field, pattern in variance_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                try:
                    value = float(matches[0].replace(',', '').replace('$', '').replace('+', ''))
                    if field == "variance_percent":
                        value = value / 100  # Convert to decimal
                    variance_data[field] = value
                except ValueError:
                    continue
        
        if variance_data:
            data["variance_analysis"] = variance_data
            data["_extraction_metadata"]["confidence_factors"]["variance_analysis"] = len(variance_data)
    
    def _calculate_derived_metrics(self, data: Dict[str, Any]):
        """Calculate derived financial metrics"""
        income = data.get("income_statement", {})
        expenses = data.get("expense_statement", {})
        ratios = data.get("financial_ratios", {})
        
        derived_metrics = {}
        
        # Calculate NOI if not directly extracted
        total_income = income.get("total_income") or income.get("effective_gross_income")
        total_expenses = expenses.get("total_expenses")
        
        if total_income and total_expenses:
            calculated_noi = total_income - total_expenses
            if "net_operating_income" not in expenses:
                derived_metrics["calculated_noi"] = calculated_noi
                expenses["net_operating_income"] = calculated_noi
        
        # Calculate expense ratio if not directly extracted
        if total_income and total_expenses and total_income > 0:
            if "expense_ratio" not in ratios:
                expense_ratio = total_expenses / total_income
                derived_metrics["calculated_expense_ratio"] = expense_ratio
                ratios["expense_ratio"] = expense_ratio
        
        # Calculate vacancy rate from occupancy rate
        if "occupancy_rate" in ratios and "vacancy_rate" not in ratios:
            vacancy_rate = 1 - ratios["occupancy_rate"]
            derived_metrics["calculated_vacancy_rate"] = vacancy_rate
            ratios["vacancy_rate"] = vacancy_rate
        
        # Calculate income per square foot if square footage available
        square_footage = self._extract_square_footage(data)
        if square_footage and total_income:
            income_per_sf = total_income / square_footage
            derived_metrics["income_per_square_foot"] = income_per_sf
        
        if derived_metrics:
            data["_derived_metrics"] = derived_metrics
            data["_extraction_metadata"]["confidence_factors"]["derived_metrics"] = len(derived_metrics)
    
    def _extract_square_footage(self, data: Dict[str, Any]) -> Optional[float]:
        """Extract square footage from content if available"""
        # This would typically come from property details in a full document
        # For now, return None as this extractor focuses on financial data
        return None
    
    def _calculate_extraction_confidence(self, data: Dict[str, Any]):
        """Calculate overall extraction confidence score"""
        confidence_factors = data["_extraction_metadata"]["confidence_factors"]
        
        # Base confidence for financial extractor
        base_confidence = 0.80
        
        # Bonus for critical financial fields
        critical_fields = ["total_income", "total_expenses", "net_operating_income"]
        critical_bonus = 0
        
        for field in critical_fields:
            if any(field in category for category in confidence_factors):
                critical_bonus += 0.05  # 5% bonus per critical field
        
        # Bonus for multiple data sources (income + expenses + ratios)
        section_count = sum(1 for section in ["income_statement", "expense_statement", "financial_ratios"] 
                           if data.get(section))
        section_bonus = section_count * 0.03  # 3% per section
        
        # Bonus for period information
        period_bonus = 0.02 if data.get("period_information") else 0
        
        # Final confidence calculation
        final_confidence = min(base_confidence + critical_bonus + section_bonus + period_bonus, 1.0)
        data["_extraction_metadata"]["extraction_confidence"] = final_confidence
        
        logger.info(f"Financial extraction confidence: {final_confidence:.3f}")
    
    def _count_extracted_fields(self, data: Dict[str, Any]) -> int:
        """Count total extracted fields"""
        count = 0
        for section_name, section_data in data.items():
            if section_name.startswith("_"):
                continue
            if isinstance(section_data, dict):
                count += len([v for v in section_data.values() if v is not None and v != ""])
        return count
    
    def generate_financial_summary(self, data: Dict[str, Any]) -> str:
        """Generate human-readable financial summary"""
        income = data.get("income_statement", {})
        expenses = data.get("expense_statement", {})
        ratios = data.get("financial_ratios", {})
        period = data.get("period_information", {})
        
        summary = []
        summary.append("=" * 50)
        summary.append("FINANCIAL STATEMENT SUMMARY")
        summary.append("=" * 50)
        
        # Period information
        if period:
            period_type = period.get("period_type", "Unknown")
            reporting_year = period.get("reporting_year", "Unknown")
            summary.append(f"Reporting Period: {period_type.title()} {reporting_year}")
            summary.append("")
        
        # Income summary
        if income:
            summary.append("INCOME STATEMENT:")
            summary.append("-" * 20)
            total_income = income.get("total_income") or income.get("effective_gross_income")
            if total_income:
                summary.append(f"Total Income: ${total_income:,.2f}")
            
            rental_income = income.get("rental_income")
            if rental_income:
                summary.append(f"Rental Income: ${rental_income:,.2f}")
            
            other_income = income.get("other_income")
            if other_income:
                summary.append(f"Other Income: ${other_income:,.2f}")
            summary.append("")
        
        # Expense summary
        if expenses:
            summary.append("EXPENSE STATEMENT:")
            summary.append("-" * 20)
            total_expenses = expenses.get("total_expenses")
            if total_expenses:
                summary.append(f"Total Expenses: ${total_expenses:,.2f}")
            
            noi = expenses.get("net_operating_income")
            if noi:
                summary.append(f"Net Operating Income: ${noi:,.2f}")
            summary.append("")
        
        # Ratios summary
        if ratios:
            summary.append("KEY RATIOS:")
            summary.append("-" * 20)
            for ratio_name, ratio_value in ratios.items():
                if ratio_name.endswith('_rate') or ratio_name.endswith('_ratio'):
                    summary.append(f"{ratio_name.replace('_', ' ').title()}: {ratio_value:.2%}")
                else:
                    summary.append(f"{ratio_name.replace('_', ' ').title()}: {ratio_value:.3f}")
        
        return "\n".join(summary)

# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = FinancialStatementsExtractor()
    
    # Example content processing
    sample_content = """
    ANNUAL OPERATING STATEMENTS
    Year Ended December 31, 2023
    
    INCOME:
    Rental Income: $1,250,000
    Other Income: $15,000
    Laundry Income: $8,500
    Total Income: $1,273,500
    
    EXPENSES:
    Management Fees: $63,675
    Maintenance: $75,000
    Utilities: $45,000
    Insurance: $25,000
    Property Taxes: $85,000
    Total Operating Expenses: $293,675
    
    Net Operating Income: $979,825
    
    RATIOS:
    Expense Ratio: 23.1%
    Occupancy Rate: 95.5%
    """
    
    # Extract data
    extracted_data = extractor.extract_financial_statement_data(sample_content)
    
    # Generate summary
    summary = extractor.generate_financial_summary(extracted_data)
    print(summary)
    
    logger.info("FinancialStatementsExtractor ready for use")
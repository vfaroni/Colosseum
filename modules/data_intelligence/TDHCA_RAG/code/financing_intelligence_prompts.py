#!/usr/bin/env python3
"""
Financing Intelligence Extraction Prompts for TDHCA Applications
Specialized prompts for Granite 3.1 8B and Llama models to extract comprehensive financing details

Based on the FINANCING_INTELLIGENCE_ENHANCEMENT_PLAN.md
Author: QAP RAG Enhanced Extraction Team
Date: July 27, 2025
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class FinancingExtractionPrompts:
    """Specialized prompts for extracting different categories of financing intelligence"""
    
    @staticmethod
    def get_construction_loan_prompt() -> str:
        """Prompt for extracting construction loan details with lender intelligence"""
        return """
Extract construction loan details from this TDHCA application text. Focus on finding:

CONSTRUCTION LOAN DETAILS:
- Loan amount
- Lender name and institution
- Interest rate (fixed/variable/prime+)
- Loan term in months
- Origination fees and points

LENDER CONTACT INFORMATION:
- Loan officer name
- Email address
- Phone number
- Lender type (Bank/Credit Union/CDFI/Private)
- Lender location (city/state)

LOAN TERMS & CONDITIONS:
- Rate type (Fixed/Variable/Prime+X)
- Interest rate floor/ceiling if variable
- Interest reserve amount
- Completion guarantee requirements
- Recourse type (Full/Limited/Non-recourse)
- Draw schedule (Monthly/Milestone-based)
- Inspection requirements
- Retainage percentage
- Special terms or conditions

Return ONLY the information found in JSON format:
{
  "construction_loan_amount": amount_or_null,
  "construction_loan_lender": "lender_name_or_empty",
  "construction_loan_rate": rate_or_null,
  "construction_loan_term_months": months_or_null,
  "construction_loan_fees": fees_or_null,
  "construction_rate_type": "type_or_empty",
  "construction_lender_contact": "contact_name_or_empty",
  "construction_lender_email": "email_or_empty",
  "construction_lender_phone": "phone_or_empty",
  "construction_lender_type": "type_or_empty",
  "construction_lender_location": "location_or_empty",
  "construction_special_terms": ["term1", "term2"] or []
}

Text to analyze:
"""

    @staticmethod
    def get_permanent_loan_prompt() -> str:
        """Prompt for extracting permanent financing details"""
        return """
Extract permanent financing details from this TDHCA application text. Focus on:

PERMANENT LOAN STRUCTURE:
- Loan amount
- Lender name and institution
- Interest rate
- Amortization period (months)
- Loan term (months)
- Loan-to-value ratio (LTV)
- Debt service coverage ratio (DSCR)

RATE STRUCTURE:
- Rate type (Fixed/Variable/Hybrid)
- Rate adjustment frequency
- Index (Prime/LIBOR/SOFR/Treasury)
- Margin over index
- Prepayment penalty terms

LENDER INTELLIGENCE:
- Loan officer/contact name
- Email and phone
- Lender specialty (LIHTC/Multifamily/Community)
- Geographic location

COMPLIANCE REQUIREMENTS:
- Required reserves
- Replacement reserves per unit
- Operating reserve months
- Special compliance terms

Return ONLY the information found in JSON format:
{
  "permanent_loan_amount": amount_or_null,
  "permanent_loan_lender": "lender_name_or_empty",
  "permanent_loan_rate": rate_or_null,
  "permanent_loan_amortization_months": months_or_null,
  "permanent_loan_term_months": months_or_null,
  "permanent_loan_ltv": ltv_or_null,
  "permanent_loan_dscr": dscr_or_null,
  "permanent_rate_type": "type_or_empty",
  "permanent_rate_index": "index_or_empty",
  "permanent_rate_margin": margin_or_null,
  "permanent_lender_contact": "contact_or_empty",
  "permanent_lender_email": "email_or_empty",
  "permanent_lender_phone": "phone_or_empty",
  "permanent_lender_specialty": "specialty_or_empty",
  "permanent_special_terms": ["term1", "term2"] or []
}

Text to analyze:
"""

    @staticmethod
    def get_subordinate_debt_prompt() -> str:
        """Prompt for extracting subordinate debt and grants"""
        return """
Extract subordinate debt and grant information from this TDHCA application text:

SUBORDINATE DEBT:
- Second lien loan amount
- Subordinate lender name
- Interest rate
- Loan term
- Payment terms (Deferred/Current/Contingent)
- Intercreditor agreement details

GRANTS & INCENTIVES:
- Municipal fee waivers (impact/permit/utility)
- Property tax abatements (value and years)
- State housing grants
- Federal grants (CDBG/HOME/HTF)
- Energy efficiency rebates
- Green building incentives

GOVERNMENT FUNDING:
- Housing Finance Agency loans
- Public-private partnerships
- Affordable housing trust funds
- Opportunity Zone benefits
- New Markets Tax Credits
- Historic Tax Credits

Return ONLY the information found in JSON format:
{
  "second_lien_amount": amount_or_null,
  "second_lien_lender": "lender_or_empty",
  "second_lien_rate": rate_or_null,
  "second_lien_payment_terms": "terms_or_empty",
  "impact_fee_waivers": amount_or_null,
  "permit_fee_waivers": amount_or_null,
  "property_tax_abatement_value": amount_or_null,
  "property_tax_abatement_years": years_or_null,
  "cdbg_funding": amount_or_null,
  "home_funds": amount_or_null,
  "housing_trust_fund": amount_or_null,
  "grants_received": [{"source": "name", "amount": amount, "terms": "terms"}],
  "government_funding_sources": [{"agency": "name", "program": "program", "amount": amount}]
}

Text to analyze:
"""

    @staticmethod
    def get_equity_structure_prompt() -> str:
        """Prompt for extracting LIHTC equity structure details"""
        return """
Extract LIHTC equity structure and investor information from this TDHCA application text:

TAX CREDIT ECONOMICS:
- Annual tax credit amount
- Tax credit factor/price per credit dollar
- Total tax credit equity raised
- Tax credit investor name
- Syndicator/packager name

EQUITY TERMS:
- Equity pay-in schedule
- Investor management fee
- Partnership flip terms
- Investor return hurdles/requirements
- Developer promote percentage

CONTACT INTELLIGENCE:
- Equity investor contact information
- Syndicator contact details
- Partnership attorney
- Tax counsel

ADDITIONAL EQUITY:
- General Partner equity contribution
- Other equity sources

Return ONLY the information found in JSON format:
{
  "annual_tax_credits": amount_or_null,
  "tax_credit_factor": factor_or_null,
  "total_tax_credit_equity": amount_or_null,
  "tax_credit_investor": "investor_name_or_empty",
  "tax_credit_syndicator": "syndicator_or_empty",
  "equity_investor_contact": "contact_or_empty",
  "syndicator_contact": "contact_or_empty",
  "partnership_attorney": "attorney_or_empty",
  "tax_counsel": "counsel_or_empty",
  "investor_management_fee": fee_or_null,
  "partnership_flip": "terms_or_empty",
  "developer_promote": percentage_or_null,
  "gp_equity": amount_or_null
}

Text to analyze:
"""

    @staticmethod
    def get_deal_analytics_prompt() -> str:
        """Prompt for extracting deal performance metrics and analytics"""
        return """
Extract deal performance metrics and analytics from this TDHCA application text:

COVERAGE RATIOS:
- Debt service coverage ratio (DSCR)
- Debt yield
- Loan-to-cost ratio
- Equity multiple

RETURN METRICS:
- Developer internal rate of return (IRR)
- Investor projected IRR
- Cash-on-cash return
- Leveraged IRR

RISK ASSESSMENT:
- Interest rate sensitivity
- Break-even occupancy
- Rent growth assumptions
- Operating expense ratio

MARKET INTELLIGENCE:
- Comparable developments
- Market capture rate
- Competitive advantages
- Risk factors

Return ONLY the information found in JSON format:
{
  "debt_service_coverage_ratio": ratio_or_null,
  "debt_yield": yield_or_null,
  "loan_to_cost_ratio": ratio_or_null,
  "developer_internal_rate_return": irr_or_null,
  "investor_projected_irr": irr_or_null,
  "cash_on_cash_return": return_or_null,
  "occupancy_break_even": percentage_or_null,
  "rent_growth_assumptions": percentage_or_null,
  "operating_expense_ratio": ratio_or_null,
  "comparable_developments": ["dev1", "dev2"] or [],
  "competitive_advantages": ["advantage1", "advantage2"] or [],
  "risk_factors": ["risk1", "risk2"] or []
}

Text to analyze:
"""

class FinancingIntelligenceExtractor:
    """Main extractor class using specialized prompts for financing intelligence"""
    
    def __init__(self, model_type: str = "granite"):
        """Initialize with model type (granite or llama)"""
        self.model_type = model_type
        self.prompts = FinancingExtractionPrompts()
        
    def extract_construction_financing(self, text: str) -> Dict[str, Any]:
        """Extract construction loan details using specialized prompt"""
        prompt = self.prompts.get_construction_loan_prompt() + text
        return self._process_with_model(prompt, "construction_financing")
    
    def extract_permanent_financing(self, text: str) -> Dict[str, Any]:
        """Extract permanent loan details using specialized prompt"""
        prompt = self.prompts.get_permanent_loan_prompt() + text
        return self._process_with_model(prompt, "permanent_financing")
    
    def extract_subordinate_debt(self, text: str) -> Dict[str, Any]:
        """Extract subordinate debt and grants using specialized prompt"""
        prompt = self.prompts.get_subordinate_debt_prompt() + text
        return self._process_with_model(prompt, "subordinate_debt")
    
    def extract_equity_structure(self, text: str) -> Dict[str, Any]:
        """Extract LIHTC equity structure using specialized prompt"""
        prompt = self.prompts.get_equity_structure_prompt() + text
        return self._process_with_model(prompt, "equity_structure")
    
    def extract_deal_analytics(self, text: str) -> Dict[str, Any]:
        """Extract deal performance metrics using specialized prompt"""
        prompt = self.prompts.get_deal_analytics_prompt() + text
        return self._process_with_model(prompt, "deal_analytics")
    
    def extract_comprehensive_financing(self, text: str) -> Dict[str, Any]:
        """Extract all financing intelligence categories"""
        results = {}
        
        # Extract each category using specialized prompts
        results.update(self.extract_construction_financing(text))
        results.update(self.extract_permanent_financing(text))
        results.update(self.extract_subordinate_debt(text))
        results.update(self.extract_equity_structure(text))
        results.update(self.extract_deal_analytics(text))
        
        return results
    
    def _process_with_model(self, prompt: str, category: str) -> Dict[str, Any]:
        """Process prompt with selected model (placeholder for actual model integration)"""
        # This will be integrated with actual Granite/Llama model calls
        # For now, return empty structure to maintain compatibility
        
        if category == "construction_financing":
            return {
                "construction_loan_amount": 0.0,
                "construction_loan_lender": "",
                "construction_loan_rate": 0.0,
                "construction_lender_contact": "",
                "construction_lender_email": "",
                "construction_special_terms": []
            }
        elif category == "permanent_financing":
            return {
                "permanent_loan_amount": 0.0,
                "permanent_loan_lender": "",
                "permanent_loan_rate": 0.0,
                "permanent_lender_contact": "",
                "permanent_special_terms": []
            }
        elif category == "subordinate_debt":
            return {
                "second_lien_amount": 0.0,
                "grants_received": [],
                "government_funding_sources": []
            }
        elif category == "equity_structure":
            return {
                "tax_credit_investor": "",
                "equity_investor_contact": "",
                "syndicator_contact": ""
            }
        elif category == "deal_analytics":
            return {
                "comparable_developments": [],
                "competitive_advantages": [],
                "risk_factors": []
            }
        
        return {}

def create_financing_extraction_examples():
    """Create example prompts for testing and validation"""
    
    examples = {
        "construction_loan_example": {
            "input_text": """
            Construction Financing:
            Bank of America Construction Loan: $15,500,000
            Interest Rate: Prime + 1.25% (Currently 8.75%)
            Loan Term: 24 months
            Loan Officer: Sarah Mitchell, smitchell@bofa.com, (214) 555-0123
            Dallas, TX Commercial Lending
            Draw Schedule: Monthly draws with third-party inspections
            Interest Reserve: $850,000
            Completion Guarantee Required
            """,
            "expected_output": {
                "construction_loan_amount": 15500000,
                "construction_loan_lender": "Bank of America",
                "construction_loan_rate": 8.75,
                "construction_loan_term_months": 24,
                "construction_rate_type": "Prime+X",
                "construction_lender_contact": "Sarah Mitchell",
                "construction_lender_email": "smitchell@bofa.com",
                "construction_lender_phone": "(214) 555-0123",
                "construction_interest_reserve": 850000,
                "construction_guarantee_required": True
            }
        },
        
        "permanent_loan_example": {
            "input_text": """
            Permanent Financing:
            Wells Fargo Permanent Loan: $12,800,000
            Interest Rate: 6.25% Fixed for 15 years
            Amortization: 30 years (360 months)
            Loan Term: 15 years (180 months)
            LTV: 75%
            DSCR: 1.25x
            Contact: Michael Johnson, LIHTC Specialist
            mjohnson@wellsfargo.com, (469) 555-0189
            Replacement Reserves: $300/unit/year
            """,
            "expected_output": {
                "permanent_loan_amount": 12800000,
                "permanent_loan_lender": "Wells Fargo",
                "permanent_loan_rate": 6.25,
                "permanent_loan_amortization_months": 360,
                "permanent_loan_term_months": 180,
                "permanent_loan_ltv": 75.0,
                "permanent_loan_dscr": 1.25,
                "permanent_rate_type": "Fixed",
                "permanent_lender_contact": "Michael Johnson",
                "permanent_lender_specialty": "LIHTC Specialist",
                "permanent_replacement_reserves": 300
            }
        }
    }
    
    return examples

if __name__ == "__main__":
    # Test the prompt system
    extractor = FinancingIntelligenceExtractor("granite")
    examples = create_financing_extraction_examples()
    
    print("🎯 Financing Intelligence Extraction Prompts")
    print("=" * 60)
    print(f"Model Type: {extractor.model_type}")
    print(f"Categories: 5 specialized prompt categories")
    print(f"Fields Targeted: 60+ financing intelligence fields")
    print("✅ Ready for Granite 3.1 8B integration")
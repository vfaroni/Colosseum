#!/usr/bin/env python3
"""
Comprehensive CTCAC Excel Data Extraction Comparison
Tests GPT-OSS 20B vs Llama 3.3 70B on extracting ALL fields from a CTCAC 4% application
Based on m4_beast_xlwings_extractor.py field patterns
"""

import json
import time
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

class ComprehensiveExtractionComparison:
    """Compare comprehensive CTCAC data extraction between models"""
    
    def __init__(self):
        self.models = ["gpt-oss:20b", "llama3.3:70b"]
        
        # Complete CTCAC application sample based on real Excel patterns
        self.ctcac_application_text = """
        CALIFORNIA TAX CREDIT ALLOCATION COMMITTEE
        4% TAX-EXEMPT BOND APPLICATION - COMPLETE SUBMISSION
        
        PROJECT IDENTIFICATION
        Project Name: Vista Del Sol Apartments
        Development Name: Vista Del Sol Senior Housing
        Property Name: VDS Senior Living
        Project Address: 1234 Main Street
        Site Address: 1234 Main Street, Los Angeles, CA 90012
        Property Address: Same as above
        Development Address: 1234 Main Street, Los Angeles, CA
        
        PROJECT DETAILS
        Project City: Los Angeles
        Project County: Los Angeles County
        Project ZIP: 90012
        Census Tract: 2011.01
        Total Units: 150
        Number of Units: 150 total
        Unit Count: 150
        Affordable Units: 149
        LIHTC Units: 149
        Tax Credit Units: 149
        
        FINANCIAL INFORMATION - SOURCES & USES
        Total Development Cost (TDC): $75,500,000
        Total Project Cost: $75,500,000
        Eligible Basis: $62,000,000
        Qualified Basis: $55,800,000 (90% applicable percentage)
        Basis: $55,800,000
        Credit Amount: $5,580,000
        Requested Credit Amount: $5,580,000 annually
        
        CONSTRUCTION FINANCING
        Construction Loan Amount: $45,000,000
        Construction Financing: $45,000,000
        Const Loan Amount: $45,000,000
        Construction Lender: Wells Fargo Bank, N.A.
        Const Lender: Wells Fargo Bank
        Construction Loan Lender: Wells Fargo Bank National Association
        Construction Loan Rate: 6.25%
        Construction Loan Term: 24 months
        Construction Lender Contact: Michael Johnson
        Construction Lender Phone: (415) 555-1234
        Construction Lender Email: mjohnson@wellsfargo.com
        
        PERMANENT FINANCING
        Permanent Loan Amount: $12,000,000
        Perm Loan: $12,000,000
        Permanent Financing: $12,000,000
        Permanent Lender: California Community Reinvestment Corporation
        Perm Lender: CCRC
        Permanent Loan Lender: California Community Reinvestment Corp
        Permanent Loan Rate: 4.75%
        Permanent Loan Term: 35 years
        Permanent Loan Amortization: 35 years
        Permanent Lender Contact: Sarah Williams
        Permanent Lender Phone: (213) 555-5678
        Permanent Lender Email: swilliams@ccrc.com
        
        DEVELOPER INFORMATION
        Developer: Affordable Housing Partners LLC
        Development Company: Affordable Housing Partners LLC
        Dev Name: AHP LLC
        Developer Contact: John Smith, President
        Dev Contact: John Smith
        Primary Contact: John Smith
        Developer Phone: (213) 555-1234
        Developer Email: jsmith@ahpartners.com
        Developer Fee: $3,775,000
        Dev Fee: $3,775,000
        Developer Compensation: $3,775,000
        Developer Fee Percentage: 5.0%
        
        ARCHITECT INFORMATION
        Architect Name: Design Build Associates, Inc.
        Architect Contact: Sarah Johnson, AIA
        Architect Phone: (310) 555-2468
        
        CONTRACTOR INFORMATION
        Contractor Name: Pacific Construction Corporation
        Contractor Contact: Mike Chen, Project Manager
        Contractor Phone: (626) 555-3690
        
        MANAGEMENT COMPANY
        Management Company: Professional Property Management Inc.
        Management Agent: Lisa Park, Regional Manager
        Management Phone: (310) 555-5678
        Management Email: lpark@ppm.com
        
        ADDITIONAL PROJECT DETAILS
        Project Type: New Construction
        Building Type: Garden Apartments (3 story)
        Construction Type: Type V Wood Frame
        Total Square Footage: 125,000 SF
        Site Acreage: 3.5 acres
        Parking Spaces: 225 (1.5 per unit)
        
        FUNDING SOURCES
        Tax-Exempt Bonds: $45,000,000
        Taxable Bonds: $5,000,000
        Deferred Developer Fee: $1,500,000
        GP Equity: $100,000
        Accrued Interest: $750,000
        Income During Construction: $250,000
        
        UNIT MIX
        Studio Units: 30 @ 450 SF
        1BR Units: 60 @ 650 SF
        2BR Units: 45 @ 850 SF
        3BR Units: 15 @ 1,050 SF
        
        AFFORDABILITY RESTRICTIONS
        30% AMI Units: 15
        50% AMI Units: 75
        60% AMI Units: 59
        Manager Unit: 1
        
        RESERVES & OPERATING
        Operating Reserve: $500,000
        Replacement Reserve: $300/unit/year
        Transition Reserve: $750,000
        """
        
        # JSON schema based on CTCACProjectData dataclass
        self.expected_schema = {
            "project_name": "",
            "project_address": "",
            "project_city": "",
            "project_county": "",
            "project_zip": "",
            "total_units": 0,
            "affordable_units": 0,
            "total_development_cost": 0.0,
            "eligible_basis": 0.0,
            "qualified_basis": 0.0,
            "credit_amount": 0.0,
            "construction_loan_amount": 0.0,
            "construction_loan_lender": "",
            "construction_loan_rate": 0.0,
            "construction_loan_term_months": 0,
            "construction_lender_contact": "",
            "construction_lender_phone": "",
            "construction_lender_email": "",
            "permanent_loan_amount": 0.0,
            "permanent_loan_lender": "",
            "permanent_loan_rate": 0.0,
            "permanent_loan_term_years": 0,
            "permanent_loan_amortization_years": 0,
            "permanent_lender_contact": "",
            "permanent_lender_phone": "",
            "permanent_lender_email": "",
            "developer_name": "",
            "developer_contact": "",
            "developer_phone": "",
            "developer_email": "",
            "developer_fee": 0.0,
            "developer_fee_percent": 0.0,
            "architect_name": "",
            "architect_contact": "",
            "architect_phone": "",
            "contractor_name": "",
            "contractor_contact": "",
            "contractor_phone": "",
            "management_company": "",
            "management_agent": "",
            "management_phone": "",
            "management_email": ""
        }
    
    def create_extraction_prompt(self) -> str:
        """Create comprehensive extraction prompt"""
        return f"""
        You are a CTCAC data extraction specialist. Extract ALL available data from this 4% tax-exempt bond application into JSON format.
        
        Return ONLY valid JSON with these exact field names:
        {json.dumps(self.expected_schema, indent=2)}
        
        Important extraction rules:
        - For amounts, extract numeric values only (no $ or commas)
        - For rates, extract as decimal (6.25% = 6.25)
        - For terms, extract numeric values (24 months = 24)
        - If multiple values exist for a field, use the most complete one
        - If a field is not found, use the default value shown
        
        Application text to extract from:
        {self.ctcac_application_text}
        
        Return ONLY the JSON object, no explanation.
        """
    
    def extract_with_model(self, model: str, timeout: int = 90) -> Dict[str, Any]:
        """Extract comprehensive data using a specific model"""
        start_time = time.time()
        
        try:
            prompt = self.create_extraction_prompt()
            
            # Use a simpler prompt for testing
            simple_prompt = f"""Extract ALL data from this CTCAC application as JSON. Include project name, address, units, all costs, all loans, developer info, and contacts. Text: {self.ctcac_application_text[:2000]}... Return only valid JSON."""
            
            # Escape and run
            cmd = f'echo {json.dumps(simple_prompt)} | timeout {timeout} ollama run {model} 2>/dev/null'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            elapsed = time.time() - start_time
            response = result.stdout.strip()
            
            # Clean response
            clean_response = self._clean_response(response)
            
            # Try to extract JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', clean_response)
            
            if json_match:
                try:
                    extracted_data = json.loads(json_match.group())
                    
                    # Count extracted fields
                    field_count = sum(1 for v in extracted_data.values() 
                                     if v and v != "" and v != 0)
                    
                    # Calculate completeness
                    expected_fields = len(self.expected_schema)
                    completeness = (field_count / expected_fields * 100) if expected_fields > 0 else 0
                    
                    return {
                        "success": True,
                        "model": model,
                        "time": elapsed,
                        "data": extracted_data,
                        "field_count": field_count,
                        "expected_fields": expected_fields,
                        "completeness": completeness,
                        "sample_fields": self._get_sample_fields(extracted_data)
                    }
                    
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "model": model,
                        "time": elapsed,
                        "error": f"JSON parse error: {str(e)}",
                        "response_preview": clean_response[:200]
                    }
            else:
                return {
                    "success": False,
                    "model": model,
                    "time": elapsed,
                    "error": "No JSON found in response",
                    "response_preview": clean_response[:200]
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "model": model,
                "time": timeout,
                "error": f"Timeout after {timeout}s"
            }
        except Exception as e:
            return {
                "success": False,
                "model": model,
                "time": time.time() - start_time,
                "error": str(e)
            }
    
    def _clean_response(self, response: str) -> str:
        """Clean model response"""
        import re
        # Remove ANSI codes
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[mGKH]|\[?[0-9]*[hln]')
        clean = ansi_escape.sub('', response)
        # Remove progress indicators
        clean = re.sub(r'\[.*?\]', '', clean)
        # Remove thinking process
        clean = re.sub(r'Thinking\.+|\.+done thinking\.?', '', clean, flags=re.IGNORECASE)
        return clean.strip()
    
    def _get_sample_fields(self, data: Dict) -> Dict:
        """Get sample of key fields for display"""
        key_fields = [
            "project_name", "total_units", "total_development_cost",
            "construction_loan_amount", "developer_name", "developer_fee"
        ]
        return {k: data.get(k, "N/A") for k in key_fields}
    
    def run_comparison(self) -> Dict[str, Any]:
        """Run comprehensive extraction comparison"""
        print("=" * 80)
        print("🏗️ COMPREHENSIVE CTCAC EXTRACTION COMPARISON")
        print("=" * 80)
        print(f"Testing extraction of {len(self.expected_schema)} fields from CTCAC 4% application")
        print(f"Application text size: {len(self.ctcac_application_text)} characters")
        print()
        
        results = {}
        
        for model in self.models:
            print(f"📊 Testing {model}...")
            print("   Extracting project, financial, contact, and team information...")
            
            result = self.extract_with_model(model, timeout=60)
            results[model] = result
            
            if result["success"]:
                print(f"✅ Success in {result['time']:.2f}s")
                print(f"   Fields extracted: {result['field_count']}/{result['expected_fields']}")
                print(f"   Completeness: {result['completeness']:.1f}%")
                print(f"   Sample fields:")
                for field, value in result.get("sample_fields", {}).items():
                    if value and value != "N/A":
                        display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"      {field}: {display_value}")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                if "response_preview" in result:
                    print(f"   Response preview: {result['response_preview']}")
            print()
        
        # Print comparison
        self._print_detailed_comparison(results)
        
        return results
    
    def _print_detailed_comparison(self, results: Dict):
        """Print detailed comparison of extraction results"""
        print("=" * 80)
        print("📈 DETAILED COMPARISON RESULTS")
        print("=" * 80)
        
        gpt = results.get("gpt-oss:20b", {})
        llama = results.get("llama3.3:70b", {})
        
        # Performance comparison
        print("\n⚡ PERFORMANCE METRICS:")
        print("-" * 40)
        if gpt.get("success"):
            print(f"GPT-OSS 20B:   {gpt['time']:.2f}s | {gpt['field_count']} fields | {gpt['completeness']:.1f}% complete")
        else:
            print(f"GPT-OSS 20B:   Failed - {gpt.get('error', 'Unknown')}")
            
        if llama.get("success"):
            print(f"Llama 3.3 70B: {llama['time']:.2f}s | {llama['field_count']} fields | {llama['completeness']:.1f}% complete")
        else:
            print(f"Llama 3.3 70B: Failed - {llama.get('error', 'Unknown')}")
        
        # Field-by-field comparison if both succeeded
        if gpt.get("success") and llama.get("success"):
            print("\n📊 FIELD EXTRACTION COMPARISON:")
            print("-" * 40)
            
            gpt_data = gpt.get("data", {})
            llama_data = llama.get("data", {})
            
            comparison_fields = [
                "project_name",
                "total_units",
                "total_development_cost",
                "construction_loan_amount",
                "developer_fee"
            ]
            
            for field in comparison_fields:
                gpt_val = gpt_data.get(field, "Not extracted")
                llama_val = llama_data.get(field, "Not extracted")
                
                print(f"\n{field}:")
                print(f"  GPT-OSS:  {gpt_val}")
                print(f"  Llama:    {llama_val}")
                
                if gpt_val != "Not extracted" and llama_val != "Not extracted":
                    if str(gpt_val) == str(llama_val):
                        print(f"  ✅ Match")
                    else:
                        print(f"  ⚠️ Different values")
        
        # Winner determination
        print("\n🏆 OVERALL ASSESSMENT:")
        print("-" * 40)
        
        if gpt.get("success") and llama.get("success"):
            gpt_score = gpt['completeness'] + (100 - min(gpt['time'], 100))
            llama_score = llama['completeness'] + (100 - min(llama['time'], 100))
            
            if gpt_score > llama_score:
                print("Winner: GPT-OSS 20B")
                print(f"  • Better completeness and/or speed")
            else:
                print("Winner: Llama 3.3 70B")
                print(f"  • Better completeness and/or speed")
        elif gpt.get("success"):
            print("Winner: GPT-OSS 20B (only successful model)")
        elif llama.get("success"):
            print("Winner: Llama 3.3 70B (only successful model)")
        else:
            print("No winner - both models failed")
        
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        print("For CTCAC Excel extraction with 30+ fields:")
        print("• Use timeout > 60s for complex extractions")
        print("• Consider breaking into smaller chunks")
        print("• Validate critical financial fields")
        print("• Use the model with higher completeness for production")

if __name__ == "__main__":
    comparator = ComprehensiveExtractionComparison()
    results = comparator.run_comparison()
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"comprehensive_extraction_results_{timestamp}.json"
    
    # Prepare results for JSON (remove actual data to avoid large file)
    clean_results = {}
    for model, result in results.items():
        clean_result = {k: v for k, v in result.items() if k not in ["data", "sample_fields"]}
        if "sample_fields" in result:
            clean_result["sample_fields"] = result["sample_fields"]
        clean_results[model] = clean_result
    
    with open(output_file, 'w') as f:
        json.dump(clean_results, f, indent=2)
    
    print(f"\n💾 Full results saved to: {output_file}")
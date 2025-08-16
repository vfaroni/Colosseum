#!/usr/bin/env python3
"""
JSON Data Extraction Comparison: GPT-OSS 20B vs Llama 3.3 70B
Tests both models for extracting structured JSON from CTCAC/CDLAC 4% bond applications
"""

import json
import time
import subprocess
from typing import Dict, Any, List
from datetime import datetime
import re

class JSONExtractionComparison:
    """Compare JSON extraction capabilities between models"""
    
    def __init__(self):
        self.models = ["gpt-oss:20b", "llama3.3:70b"]
        
        # Sample CTCAC 4% application text (typical fields)
        self.sample_text = """
        CALIFORNIA TAX CREDIT ALLOCATION COMMITTEE
        4% TAX-EXEMPT BOND APPLICATION
        
        PROJECT INFORMATION
        Project Name: Vista Del Sol Apartments
        Project Address: 1234 Main Street, Los Angeles, CA 90012
        Total Units: 150
        Affordable Units: 149
        County: Los Angeles
        Census Tract: 2011.01
        
        FINANCIAL INFORMATION
        Total Development Cost: $75,500,000
        Eligible Basis: $62,000,000
        Qualified Basis: $55,800,000
        Requested Credit Amount: $5,580,000
        Construction Loan Amount: $45,000,000
        Construction Loan Lender: Wells Fargo Bank
        Construction Loan Rate: 6.25%
        Construction Loan Term: 24 months
        Permanent Loan Amount: $12,000,000
        Permanent Loan Lender: CDLAC Bond Financing
        Permanent Loan Rate: 4.75%
        Permanent Loan Term: 35 years
        
        DEVELOPER INFORMATION
        Developer Name: Affordable Housing Partners LLC
        Developer Contact: John Smith
        Developer Phone: (213) 555-1234
        Developer Email: jsmith@ahpartners.com
        Developer Fee: $3,775,000
        Developer Fee Percentage: 5.0%
        
        ARCHITECT/CONTRACTOR
        Architect Name: Design Build Associates
        Architect Contact: Sarah Johnson
        Contractor Name: Pacific Construction Corp
        Contractor Contact: Mike Chen
        
        MANAGEMENT COMPANY
        Management Company: Professional Property Management
        Management Agent: Lisa Park
        Management Phone: (310) 555-5678
        Management Email: lpark@ppm.com
        """
        
        self.extraction_prompt = """
        Extract the following structured data from this CTCAC 4% application text into valid JSON format.
        Include all fields with proper data types (numbers for amounts, strings for text).
        
        Required JSON structure:
        {
            "project_name": "",
            "project_address": "",
            "total_units": 0,
            "affordable_units": 0,
            "county": "",
            "census_tract": "",
            "total_development_cost": 0,
            "eligible_basis": 0,
            "qualified_basis": 0,
            "requested_credit_amount": 0,
            "construction_loan": {
                "amount": 0,
                "lender": "",
                "rate": 0,
                "term_months": 0
            },
            "permanent_loan": {
                "amount": 0,
                "lender": "",
                "rate": 0,
                "term_years": 0
            },
            "developer": {
                "name": "",
                "contact": "",
                "phone": "",
                "email": "",
                "fee": 0,
                "fee_percentage": 0
            },
            "architect": {
                "name": "",
                "contact": ""
            },
            "contractor": {
                "name": "",
                "contact": ""
            },
            "management": {
                "company": "",
                "agent": "",
                "phone": "",
                "email": ""
            }
        }
        
        Text to extract from:
        """ + self.sample_text
    
    def extract_with_model(self, model: str) -> Dict[str, Any]:
        """Extract JSON using a specific model"""
        start_time = time.time()
        
        try:
            # Prepare command - escape prompt properly
            prompt_escaped = json.dumps(self.extraction_prompt)
            cmd = f'echo {prompt_escaped} | ollama run {model} 2>/dev/null'
            
            # Run extraction
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            elapsed = time.time() - start_time
            response = result.stdout.strip()
            
            # Clean response - remove progress indicators and non-JSON content
            clean_response = self._clean_response(response)
            
            # Try to parse JSON
            try:
                # Find JSON in response
                json_match = re.search(r'\{[\s\S]*\}', clean_response)
                if json_match:
                    json_str = json_match.group()
                    extracted_data = json.loads(json_str)
                    
                    return {
                        "success": True,
                        "model": model,
                        "time": elapsed,
                        "data": extracted_data,
                        "field_count": self._count_fields(extracted_data),
                        "accuracy": self._calculate_accuracy(extracted_data)
                    }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "model": model,
                    "time": elapsed,
                    "error": f"JSON parse error: {str(e)}",
                    "raw_response": clean_response[:500]
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "model": model,
                "time": 60,
                "error": "Timeout"
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
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[mGKH]|\[?[0-9]*[hln]')
        clean = ansi_escape.sub('', response)
        
        # Remove progress indicators
        clean = re.sub(r'\[.*?\]', '', clean)
        
        # Remove "Thinking..." and similar
        clean = re.sub(r'Thinking\.+|\.+done thinking\.?', '', clean, flags=re.IGNORECASE)
        
        return clean.strip()
    
    def _count_fields(self, data: Dict) -> int:
        """Count populated fields in extracted JSON"""
        count = 0
        
        def count_recursive(obj):
            nonlocal count
            if isinstance(obj, dict):
                for value in obj.values():
                    if isinstance(value, dict):
                        count_recursive(value)
                    elif value and value != 0 and value != "":
                        count += 1
            elif obj and obj != 0 and obj != "":
                count += 1
        
        count_recursive(data)
        return count
    
    def _calculate_accuracy(self, extracted: Dict) -> float:
        """Calculate extraction accuracy"""
        expected_values = {
            "project_name": "Vista Del Sol Apartments",
            "total_units": 150,
            "affordable_units": 149,
            "county": "Los Angeles",
            "total_development_cost": 75500000,
            "eligible_basis": 62000000,
            "qualified_basis": 55800000,
            "requested_credit_amount": 5580000
        }
        
        correct = 0
        total = len(expected_values)
        
        for key, expected in expected_values.items():
            if key in extracted:
                actual = extracted[key]
                if isinstance(expected, str):
                    if expected.lower() in str(actual).lower():
                        correct += 1
                elif isinstance(expected, (int, float)):
                    if abs(float(actual) - expected) < 1000:  # Allow small variance
                        correct += 1
        
        # Check nested fields
        if "construction_loan" in extracted:
            if extracted["construction_loan"].get("amount") == 45000000:
                correct += 1
                total += 1
        
        return (correct / total * 100) if total > 0 else 0
    
    def run_comparison(self) -> Dict[str, Any]:
        """Run the complete comparison"""
        print("=" * 80)
        print("🔬 JSON EXTRACTION COMPARISON: GPT-OSS 20B vs Llama 3.3 70B")
        print("=" * 80)
        print(f"Test: Extract structured JSON from CTCAC 4% application")
        print(f"Fields to extract: ~30 data points")
        print()
        
        results = {}
        
        for model in self.models:
            print(f"📊 Testing {model}...")
            result = self.extract_with_model(model)
            results[model] = result
            
            if result["success"]:
                print(f"✅ Success in {result['time']:.2f}s")
                print(f"   Fields extracted: {result['field_count']}")
                print(f"   Accuracy: {result['accuracy']:.1f}%")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            print()
        
        # Compare results
        self._print_comparison(results)
        
        return results
    
    def _print_comparison(self, results: Dict):
        """Print comparison summary"""
        print("=" * 80)
        print("📈 COMPARISON SUMMARY")
        print("=" * 80)
        
        gpt_result = results.get("gpt-oss:20b", {})
        llama_result = results.get("llama3.3:70b", {})
        
        if gpt_result.get("success") and llama_result.get("success"):
            print("\n📊 Performance Metrics:")
            print(f"GPT-OSS 20B:   {gpt_result['time']:.2f}s | {gpt_result['field_count']} fields | {gpt_result['accuracy']:.1f}% accuracy")
            print(f"Llama 3.3 70B: {llama_result['time']:.2f}s | {llama_result['field_count']} fields | {llama_result['accuracy']:.1f}% accuracy")
            
            # Determine winner
            gpt_score = (100 - gpt_result['time']) + gpt_result['accuracy'] + gpt_result['field_count']
            llama_score = (100 - llama_result['time']) + llama_result['accuracy'] + llama_result['field_count']
            
            print("\n🏆 Winner:")
            if gpt_score > llama_score:
                print("GPT-OSS 20B - Better overall JSON extraction")
            else:
                print("Llama 3.3 70B - Better overall JSON extraction")
            
            # Sample extracted data
            print("\n📝 Sample Extracted Data (GPT-OSS):")
            if "data" in gpt_result:
                sample = {
                    "project_name": gpt_result["data"].get("project_name"),
                    "total_units": gpt_result["data"].get("total_units"),
                    "total_development_cost": gpt_result["data"].get("total_development_cost")
                }
                print(json.dumps(sample, indent=2))
        else:
            print("⚠️ One or both models failed to extract JSON")
        
        print("\n💡 Recommendation:")
        print("For CTCAC/CDLAC JSON extraction, use the model with:")
        print("  • Higher accuracy on financial fields (critical for LIHTC)")
        print("  • Consistent JSON formatting")
        print("  • Better nested structure handling")

if __name__ == "__main__":
    comparator = JSONExtractionComparison()
    results = comparator.run_comparison()
    
    # Save results
    output_file = f"json_extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        # Clean results for JSON serialization
        clean_results = {}
        for model, result in results.items():
            clean_result = {k: v for k, v in result.items() if k != "data"}
            if "data" in result:
                clean_result["sample_data"] = {
                    "project_name": result["data"].get("project_name"),
                    "total_units": result["data"].get("total_units")
                }
            clean_results[model] = clean_result
        
        json.dump(clean_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
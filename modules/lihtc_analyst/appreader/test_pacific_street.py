#!/usr/bin/env python3
"""
Test the final corrected extractor on Pacific Street Apartments (24-553)
"""

from final_corrected_extractor import FinalCorrectedExtractor
from pathlib import Path
import json

def test_pacific_street():
    """Test extraction on Pacific Street Apartments"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-553.xlsx"
    
    if test_file.exists():
        extractor = FinalCorrectedExtractor()
        result = extractor.extract_file_final(test_file)
        
        print("\n" + "="*90)
        print("🏢 TESTING PACIFIC STREET APARTMENTS (24-553)")
        print("="*90)
        
        app_data = result['application_data']
        sources_data = result['sources_uses_data']
        
        print(f"\n📋 APPLICATION DATA:")
        print(f"   Project Name: {app_data.get('project_name')}")
        print(f"   CTCAC Project Number: {app_data.get('ctcac_project_number')}")
        print(f"   Year: {app_data.get('year')}")
        print(f"   City: {app_data.get('city')}")
        print(f"   County: {app_data.get('county')}")
        print(f"   General Contractor: {app_data.get('general_contractor')}")
        print(f"   New Construction: {app_data.get('new_construction')}")
        print(f"   Housing Type: {app_data.get('housing_type')}")
        print(f"   Total Units: {app_data.get('total_units'):,}")
        print(f"   Total Residential Sq Ft: {app_data.get('total_sqft_low_income'):,}")
        
        print(f"\n💰 SOURCES & USES DATA:")
        print(f"   Land Cost: ${sources_data.get('land_cost', 0):,.0f}")
        print(f"   Total New Construction: ${sources_data.get('total_new_construction'):,.0f}")
        print(f"   Total Architectural: ${sources_data.get('total_architectural', 0):,.0f}")
        print(f"   Total Survey & Engineering: ${sources_data.get('total_survey_engineering', 0):,.0f}")
        print(f"   Local Impact Fees: ${sources_data.get('local_impact_fees', 0):,.0f}")
        print(f"   Soft Cost Contingency: ${sources_data.get('soft_cost_contingency', 0):,.0f}")
        
        # Validation checks
        print(f"\n🎯 VALIDATION CHECKS:")
        
        # Check CTCAC Project Number
        expected_project_num = "24-553"
        actual_project_num = app_data.get('ctcac_project_number', "")
        project_num_correct = actual_project_num == expected_project_num
        print(f"   CTCAC Project Number: {'✅ CORRECT' if project_num_correct else '❌ INCORRECT'} (Expected: {expected_project_num}, Got: {actual_project_num})")
        
        # Check if project name contains "Pacific Street"
        project_name = app_data.get('project_name', '').lower()
        name_correct = 'pacific' in project_name and 'street' in project_name
        print(f"   Project Name Check: {'✅ CONTAINS Pacific Street' if name_correct else '❌ DOES NOT CONTAIN Pacific Street'}")
        
        # Check data completeness
        missing_fields = []
        critical_fields = {
            'project_name': app_data.get('project_name'),
            'county': app_data.get('county'), 
            'city': app_data.get('city'),
            'total_units': app_data.get('total_units'),
            'total_sqft_low_income': app_data.get('total_sqft_low_income')
        }
        
        for field, value in critical_fields.items():
            if not value or value == "Not found" or value == 0:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"   Missing/Empty Fields: {', '.join(missing_fields)}")
        else:
            print(f"   Data Completeness: ✅ ALL CRITICAL FIELDS FOUND")
        
        # Calculate project summary
        try:
            total_costs = (
                sources_data.get('land_cost', 0) +
                sources_data.get('total_new_construction', 0) +
                sources_data.get('total_architectural', 0) +
                sources_data.get('total_survey_engineering', 0) +
                sources_data.get('local_impact_fees', 0) +
                sources_data.get('soft_cost_contingency', 0)
            )
            
            units = app_data.get('total_units', 1)
            sqft = app_data.get('total_sqft_low_income', 1)
            
            print(f"\n📊 PROJECT SUMMARY:")
            print(f"   Total Tracked Costs: ${total_costs:,.0f}")
            if units > 0 and units < 10000:  # Reasonable unit count
                print(f"   Cost per Unit: ${total_costs/units:,.0f}")
            if sqft > 0 and sqft < 10000000:  # Reasonable sqft
                print(f"   Cost per Square Foot: ${total_costs/sqft:,.0f}")
            print(f"   Project Type: {app_data.get('housing_type')} Housing")
            print(f"   Construction Type: {app_data.get('new_construction')}")
            
        except Exception as e:
            print(f"   Summary calculation error: {e}")
        
        # Save results
        output_file = Path("/Users/vitorfaroni/Documents/Automation/LIHTCApp/pacific_street_results.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: {output_file}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if project_num_correct and not missing_fields:
            print(f"   ✅ EXTRACTION SUCCESSFUL - All key fields found")
        elif project_num_correct:
            print(f"   ⚠️ PARTIAL SUCCESS - Some fields missing")
        else:
            print(f"   ❌ EXTRACTION ISSUES - Need debugging")
        
    else:
        print(f"File not found: {test_file}")

if __name__ == "__main__":
    test_pacific_street()
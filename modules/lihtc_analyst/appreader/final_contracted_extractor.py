#!/usr/bin/env python3
"""
Final Contracted LIHTC 4% Application Data Extractor
Handles edge cases like legitimate $0 values
"""

import pandas as pd
import json
import re
from pathlib import Path

class FinalContractedExtractor:
    def __init__(self):
        self.debug_mode = True
        
    def log_debug(self, message):
        if self.debug_mode:
            print(f"DEBUG: {message}")
    
    def extract_with_validation(self, file_path):
        """Extract with proper validation for $0 values"""
        # Use the previous extractor logic but fix validation
        from contracted_extractor import ContractedLIHTCExtractor
        
        extractor = ContractedLIHTCExtractor()
        extractor.debug_mode = False  # Reduce debug output
        result = extractor.extract_file_contracted(file_path)
        
        # Fix validation for fields that can legitimately be $0
        sources_data = result.get('sources_uses_data', {})
        
        # Local Impact Fees can legitimately be $0 - check if field was found
        if sources_data.get('local_impact_fees') == 0:
            # Try to find the field to confirm it exists (even if $0)
            try:
                df = pd.read_excel(file_path, sheet_name="Sources and Uses Budget", header=None)
                
                # Check coordinate location
                impact_fees_value = df.iloc[84, 1] if len(df) > 84 else None
                
                if pd.notna(impact_fees_value):
                    self.log_debug(f"✅ Local Impact Fees field found with value: ${float(impact_fees_value):,.0f}")
                    # Remove from violations if it was there
                    if 'SourcesUses.local_impact_fees' in result.get('contract_violations', []):
                        result['contract_violations'].remove('SourcesUses.local_impact_fees')
                        result['contract_compliant'] = len(result['contract_violations']) == 0
            except:
                pass
        
        return result

def test_final_contracted():
    """Final test of contracted extraction"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    if test_file.exists():
        extractor = FinalContractedExtractor()
        result = extractor.extract_with_validation(test_file)
        
        print("\n" + "="*90)
        print("🏆 FINAL CONTRACTED EXTRACTION - MARINA TOWERS")
        print("="*90)
        
        app_data = result['application_data']
        sources_data = result['sources_uses_data']
        
        print(f"\n📋 APPLICATION DATA - ALL 10 MANDATORY FIELDS:")
        fields_app = [
            ('Project Name', app_data.get('project_name')),
            ('CTCAC Project Number', app_data.get('ctcac_project_number')),
            ('Year', app_data.get('year')),
            ('City', app_data.get('city')),
            ('County', app_data.get('county')),
            ('General Contractor', app_data.get('general_contractor')),
            ('New Construction', app_data.get('new_construction')),
            ('Housing Type', app_data.get('housing_type')),
            ('Total Units', f"{app_data.get('total_units'):,}"),
            ('Total Sq Ft (Low Income)', f"{app_data.get('total_sqft_low_income'):,}")
        ]
        
        for field, value in fields_app:
            status = "✅" if value and "CONTRACT_VIOLATION" not in str(value) else "❌"
            print(f"   {status} {field}: {value}")
        
        print(f"\n💰 SOURCES & USES DATA - ALL 6 MANDATORY FIELDS:")
        fields_sources = [
            ('Land Cost', f"${sources_data.get('land_cost', 0):,.0f}"),
            ('Total New Construction', f"${sources_data.get('total_new_construction'):,.0f}" if isinstance(sources_data.get('total_new_construction'), (int, float)) else str(sources_data.get('total_new_construction'))),
            ('Total Architectural', f"${sources_data.get('total_architectural', 0):,.0f}"),
            ('Total Survey & Engineering', f"${sources_data.get('total_survey_engineering', 0):,.0f}"),
            ('Local Impact Fees', f"${sources_data.get('local_impact_fees', 0):,.0f}"),
            ('Soft Cost Contingency', f"${sources_data.get('soft_cost_contingency'):,.0f}" if isinstance(sources_data.get('soft_cost_contingency'), (int, float)) else str(sources_data.get('soft_cost_contingency')))
        ]
        
        for field, value in fields_sources:
            status = "✅" if value and "CONTRACT_VIOLATION" not in str(value) else "❌"
            print(f"   {status} {field}: {value}")
        
        # Final contract compliance
        print(f"\n🎯 FINAL CONTRACT COMPLIANCE:")
        violations = result.get('contract_violations', [])
        if not violations:
            print(f"   ✅ 100% CONTRACT COMPLIANT")
            print(f"   ✅ All 16 mandatory fields successfully extracted!")
            print(f"   ✅ Ready for production use")
        else:
            print(f"   ⚠️  {len(violations)} remaining issues:")
            for violation in violations:
                print(f"     - {violation}")
        
        # Project summary
        try:
            total_costs = (
                sources_data.get('land_cost', 0) +
                (sources_data.get('total_new_construction', 0) if isinstance(sources_data.get('total_new_construction'), (int, float)) else 0) +
                sources_data.get('total_architectural', 0) +
                sources_data.get('total_survey_engineering', 0) +
                sources_data.get('local_impact_fees', 0) +
                (sources_data.get('soft_cost_contingency', 0) if isinstance(sources_data.get('soft_cost_contingency'), (int, float)) else 0)
            )
            
            units = app_data.get('total_units', 1)
            sqft = app_data.get('total_sqft_low_income', 1)
            
            print(f"\n📊 PROJECT FINANCIAL SUMMARY:")
            print(f"   Total Tracked Project Costs: ${total_costs:,.0f}")
            print(f"   Cost per Unit: ${total_costs/max(1, units):,.0f}")
            print(f"   Cost per Square Foot: ${total_costs/max(1, sqft):,.0f}")
            print(f"   Project Type: {app_data.get('housing_type')} Housing")
            print(f"   Construction Type: {app_data.get('new_construction')}")
            
        except Exception as e:
            print(f"   Summary calculation error: {e}")
        
        # Save final results
        output_file = Path("/Users/vitorfaroni/Documents/Automation/LIHTCApp/marina_towers_final_contracted.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n📄 Final results saved to: {output_file}")
        
    else:
        print(f"File not found: {test_file}")

if __name__ == "__main__":
    test_final_contracted()
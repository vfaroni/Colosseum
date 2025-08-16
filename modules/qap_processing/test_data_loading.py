#!/usr/bin/env python3
"""
Quick test to see what data is actually being loaded
"""

import json
from pathlib import Path

def test_data_loading():
    """Test what data is available"""
    
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/qap_processing")
    
    print("🔍 TESTING DATA LOADING")
    print("=" * 50)
    
    # Test Phase 2E files
    phase_2e_dir = base_dir / "phase_2e_full_54_jurisdictions"
    if phase_2e_dir.exists():
        json_files = list(phase_2e_dir.glob("*.json"))
        print(f"📁 Phase 2E directory: {len(json_files)} JSON files")
        
        total_definitions = 0
        all_jurisdictions = set()
        
        for json_file in json_files[:2]:  # Test first 2 files
            print(f"\n📄 Testing: {json_file.name}")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"   Type: {type(data)}")
                
                if isinstance(data, dict):
                    state_codes = list(data.keys())
                    print(f"   States: {state_codes}")
                    
                    for state_code, state_data in data.items():
                        if isinstance(state_data, dict) and 'definitions' in state_data:
                            defs_count = len(state_data['definitions'])
                            total_definitions += defs_count
                            all_jurisdictions.add(state_code)
                            print(f"     {state_code}: {defs_count} definitions")
                            
                            # Show sample definition
                            if state_data['definitions']:
                                sample = state_data['definitions'][0]
                                print(f"     Sample term: '{sample.get('term', 'No term')}'")
                                print(f"     Relevance: {sample.get('lihtc_relevance', 'No relevance')}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n✅ Total definitions found: {total_definitions}")
        print(f"📍 Jurisdictions: {sorted(all_jurisdictions)}")
    
    else:
        print("❌ Phase 2E directory not found")
    
    # Also check if final 5 results exist
    final_5_dir = base_dir / "phase_2e_final_5_results"
    if final_5_dir.exists():
        final_files = list(final_5_dir.glob("*.json"))
        print(f"\n📁 Final 5 directory: {len(final_files)} JSON files")
    else:
        print("\n📁 Final 5 directory not found")

if __name__ == "__main__":
    test_data_loading()
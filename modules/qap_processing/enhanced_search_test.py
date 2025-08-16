#!/usr/bin/env python3
"""
Enhanced search test to find minimum construction standards
"""

import json
from pathlib import Path

def search_ca_definitions():
    """Search California definitions for minimum construction standards"""
    
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/qap_processing")
    phase_2e_dir = base_dir / "phase_2e_full_54_jurisdictions"
    
    print("🔍 SEARCHING FOR 'MINIMUM CONSTRUCTION STANDARDS' IN CALIFORNIA")
    print("=" * 70)
    
    for json_file in phase_2e_dir.glob("*.json"):
        if "summary" in json_file.name.lower():
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'CA' in data and isinstance(data['CA'], dict) and 'definitions' in data['CA']:
                ca_definitions = data['CA']['definitions']
                print(f"📄 Found {len(ca_definitions)} CA definitions in {json_file.name}")
                
                # Search for minimum construction standards
                matches = []
                
                for i, defn in enumerate(ca_definitions):
                    term = defn.get('term', '').lower()
                    definition = defn.get('definition', '').lower()
                    
                    # Direct term matches
                    if 'minimum construction standards' in term or 'minimum construction standards' in definition:
                        matches.append(('EXACT', defn))
                    
                    # Related matches
                    elif ('minimum' in term and 'construction' in term) or ('minimum' in term and 'standard' in term):
                        matches.append(('TERM', defn))
                    
                    elif 'minimum construction' in definition or 'construction standard' in definition:
                        matches.append(('CONTENT', defn))
                    
                    # Broader matches
                    elif 'construction' in term and ('standard' in definition or 'requirement' in definition):
                        matches.append(('BROAD', defn))
                
                print(f"🎯 Found {len(matches)} potential matches:")
                
                for match_type, defn in matches:
                    print(f"\n[{match_type}] Term: '{defn.get('term', 'No term')}'")
                    print(f"Definition: {defn.get('definition', 'No definition')[:300]}...")
                    print(f"Relevance: {defn.get('lihtc_relevance', 'unknown')}")
                    print("-" * 50)
                
                break
                
        except Exception as e:
            print(f"❌ Error loading {json_file}: {e}")
            continue

def search_specific_terms():
    """Search for specific terms that should be in QAP"""
    
    search_terms = [
        "minimum construction standards",
        "construction standards", 
        "building standards",
        "rehabilitation standards",
        "energy efficiency"
    ]
    
    print(f"\n🎯 SEARCHING FOR SPECIFIC TERMS")
    print("=" * 50)
    
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/qap_processing")
    phase_2e_dir = base_dir / "phase_2e_full_54_jurisdictions"
    
    for json_file in phase_2e_dir.glob("*.json"):
        if "summary" in json_file.name.lower():
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'CA' in data and isinstance(data['CA'], dict) and 'definitions' in data['CA']:
                ca_definitions = data['CA']['definitions']
                
                for search_term in search_terms:
                    print(f"\n🔍 Searching for: '{search_term}'")
                    matches = 0
                    
                    for defn in ca_definitions:
                        term = defn.get('term', '').lower()
                        definition = defn.get('definition', '').lower()
                        
                        if search_term in term or search_term in definition:
                            matches += 1
                            print(f"  ✅ Found in: '{defn.get('term', 'No term')}'")
                    
                    print(f"  Total matches: {matches}")
                
                break
                
        except Exception as e:
            continue

if __name__ == "__main__":
    search_ca_definitions()
    search_specific_terms()
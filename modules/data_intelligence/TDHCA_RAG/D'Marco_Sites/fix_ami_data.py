#!/usr/bin/env python3
"""
Quick fix for AMI data matching
"""

import pandas as pd
import json
import math
from pathlib import Path

# Load data
base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
ami_df = pd.read_excel(base_dir / "HUD2025_AMI_Rent_Data_Static.xlsx")
sites_file = base_dir / "DMarco_Sites_With_Flood_20250730_144920.json"

# Filter AMI data for Texas only
tx_ami = ami_df[ami_df['State'] == 'TX'].copy()

with open(sites_file, 'r') as f:
    sites_data = json.load(f)

print(f"🔧 Fixing AMI data for {len(sites_data)} sites...")

updated_sites = []

for i, site in enumerate(sites_data, 1):
    county = site.get('census_county', '')
    
    # Find Texas AMI area
    ami_match = None
    if county and county not in ['County 213', 'County 257', 'County 349', 'County 91']:
        clean_county = county.replace(' County', '').strip()
        matches = tx_ami[tx_ami['County'].str.contains(clean_county, na=False, case=False)]
        
        if len(matches) > 0:
            ami_match = matches.iloc[0]
    
    updated_site = site.copy()
    
    if ami_match is not None:
        # Get the median AMI (4-person 100%)
        median_ami = ami_match.get('Median_AMI_100pct', 0)
        
        # Get rent limits directly from the data
        rent_data = {
            '50_ami_rents': {
                'Studio': ami_match.get('50pct_AMI_Studio_Rent', 0),
                '1BR': ami_match.get('50pct_AMI_1BR_Rent', 0),
                '2BR': ami_match.get('50pct_AMI_2BR_Rent', 0),
                '3BR': ami_match.get('50pct_AMI_3BR_Rent', 0),
                '4BR': ami_match.get('50pct_AMI_4BR_Rent', 0)
            },
            '60_ami_rents': {
                'Studio': ami_match.get('60pct_AMI_Studio_Rent', 0),
                '1BR': ami_match.get('60pct_AMI_1BR_Rent', 0),
                '2BR': ami_match.get('60pct_AMI_2BR_Rent', 0),
                '3BR': ami_match.get('60pct_AMI_3BR_Rent', 0),
                '4BR': ami_match.get('60pct_AMI_4BR_Rent', 0)
            }
        }
        
        updated_site.update({
            'ami_analysis_status': 'SUCCESS',
            'ami_area_name': ami_match['HUD_Area'],
            'ami_county': ami_match['County'],
            'ami_metro_status': ami_match['Metro_Status'],
            'ami_4_person_100_pct': median_ami,
            'lihtc_rent_limits': rent_data,
            'ami_method': 'HUD_2025_CORRECTED_TX_MATCH'
        })
        
        print(f"✅ Site {i}: {county} -> {ami_match['HUD_Area']} (4P AMI: ${median_ami:,})")
    else:
        updated_site.update({
            'ami_analysis_status': 'NO_MATCH',
            'ami_area_name': None,
            'ami_method': 'NO_TX_MATCH_FOUND'
        })
        print(f"❌ Site {i}: {county} -> No TX match")
    
    updated_sites.append(updated_site)

# Save corrected data
output_file = base_dir / "DMarco_Sites_Complete_With_AMI_20250730_145315.json"
with open(output_file, 'w') as f:
    json.dump(updated_sites, f, indent=2)

print(f"\n✅ Saved corrected analysis to: {output_file}")

# Summary
successful = sum(1 for site in updated_sites if site.get('ami_analysis_status') == 'SUCCESS')
ami_values = [site.get('ami_4_person_100_pct', 0) for site in updated_sites if site.get('ami_4_person_100_pct', 0) > 0]

print(f"📊 AMI Integration Results:")
print(f"   - Total sites: {len(updated_sites)}")
print(f"   - Successful matches: {successful}")
print(f"   - Success rate: {successful/len(updated_sites)*100:.1f}%")
if ami_values:
    print(f"   - Average 4P 100% AMI: ${sum(ami_values)/len(ami_values):,.0f}")
    print(f"   - Range: ${min(ami_values):,} - ${max(ami_values):,}")
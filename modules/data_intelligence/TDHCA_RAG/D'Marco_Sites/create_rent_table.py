#!/usr/bin/env python3
"""
Create clean rent table for Western Peninsula counties - 80% AMI only
"""

import pandas as pd

def main():
    # Read the HUD AMI rent data
    df = pd.read_excel('HUD2025_AMI_Rent_Data_Static.xlsx')
    
    # Filter for California
    ca_data = df[df['State'] == 'CA'].copy()
    
    # Target counties
    target_counties = [
        'Alameda County', 'Contra Costa County', 'Marin County', 'Monterey County',
        'Napa County', 'Sacramento County', 'San Benito County', 'San Francisco County',
        'San Mateo County', 'Santa Clara County', 'Santa Cruz County', 'Solano County',
        'Sonoma County'
    ]
    
    # Filter data for target counties
    target_data = ca_data[ca_data['County'].isin(target_counties)].copy()
    
    print('📊 WESTERN PENINSULA CALIFORNIA - 80% AMI MAXIMUM RENTS')
    print('=' * 80)
    print()
    
    # Column headers
    print(f'{"County":<20} {"Studio":<10} {"1BR":<10} {"2BR":<10} {"3BR":<10}')
    print('-' * 80)
    
    # Extract 80% AMI data for each county
    for county in sorted(target_counties):
        county_data = target_data[target_data['County'] == county]
        if len(county_data) > 0:
            row = county_data.iloc[0]  # Take first row if multiple areas
            
            # Get 80% AMI rents
            studio_rent = int(row['80pct_AMI_Studio_Rent']) if pd.notna(row['80pct_AMI_Studio_Rent']) else 0
            br1_rent = int(row['80pct_AMI_1BR_Rent']) if pd.notna(row['80pct_AMI_1BR_Rent']) else 0
            br2_rent = int(row['80pct_AMI_2BR_Rent']) if pd.notna(row['80pct_AMI_2BR_Rent']) else 0
            br3_rent = int(row['80pct_AMI_3BR_Rent']) if pd.notna(row['80pct_AMI_3BR_Rent']) else 0
            
            county_short = county.replace(' County', '')
            print(f'{county_short:<20} ${studio_rent:<9,} ${br1_rent:<9,} ${br2_rent:<9,} ${br3_rent:<9,}')

if __name__ == "__main__":
    main()
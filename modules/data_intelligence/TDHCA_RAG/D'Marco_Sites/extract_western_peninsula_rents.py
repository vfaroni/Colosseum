#!/usr/bin/env python3
"""
Extract max rents for Western Peninsula California counties
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
    
    print('💰 WESTERN PENINSULA CALIFORNIA - MAX RENTS BY COUNTY')
    print('=' * 100)
    print()
    
    # Display data by AMI level
    ami_levels = ['50', '60', '70', '80']
    
    for ami in ami_levels:
        print(f'📊 {ami}% AMI MAXIMUM RENTS')
        print('-' * 90)
        print(f'{"County":<25} {"Studio":<10} {"1BR":<10} {"2BR":<10} {"3BR":<10} {"4BR":<10}')
        print('-' * 90)
        
        for county in sorted(target_counties):
            county_data = target_data[target_data['County'] == county]
            if len(county_data) > 0:
                row = county_data.iloc[0]  # Take first row if multiple areas
                studio_col = f'{ami}pct_AMI_Studio_Rent'
                br1_col = f'{ami}pct_AMI_1BR_Rent'
                br2_col = f'{ami}pct_AMI_2BR_Rent'
                br3_col = f'{ami}pct_AMI_3BR_Rent'
                br4_col = f'{ami}pct_AMI_4BR_Rent'
                
                studio_rent = int(row[studio_col]) if pd.notna(row[studio_col]) else 0
                br1_rent = int(row[br1_col]) if pd.notna(row[br1_col]) else 0
                br2_rent = int(row[br2_col]) if pd.notna(row[br2_col]) else 0
                br3_rent = int(row[br3_col]) if pd.notna(row[br3_col]) else 0
                br4_rent = int(row[br4_col]) if pd.notna(row[br4_col]) else 0
                
                county_short = county.replace(' County', '')
                print(f'{county_short:<25} ${studio_rent:<9,} ${br1_rent:<9,} ${br2_rent:<9,} ${br3_rent:<9,} ${br4_rent:<9,}')
        print()
    
    # Also show HUD Area names for context
    print('📍 HUD AREA DESIGNATIONS:')
    print('-' * 70)
    for county in sorted(target_counties):
        county_data = target_data[target_data['County'] == county]
        if len(county_data) > 0:
            for _, row in county_data.iterrows():
                county_short = county.replace(' County', '')
                print(f'{county_short:<25} → {row["HUD_Area"]}')

if __name__ == "__main__":
    main()
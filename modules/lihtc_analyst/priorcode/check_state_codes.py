#!/usr/bin/env python3
"""
Check state codes in the QCT data to understand how Arizona is represented
"""

import pandas as pd
import os

def check_state_codes():
    """Check what state codes are used in the data"""
    
    base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
    
    # Check CSV file
    csv_file = os.path.join(base_path, "QCT2025.csv")
    if os.path.exists(csv_file):
        print("="*60)
        print("CSV FILE STATE CODES")
        print("="*60)
        
        df = pd.read_csv(csv_file)
        
        # Check statefp column (state FIPS codes)
        if 'statefp' in df.columns:
            unique_states = sorted(df['statefp'].unique())
            print(f"Unique state FIPS codes: {unique_states}")
            
            # Arizona FIPS code is 04
            az_fips = 4  # or 04
            az_data = df[df['statefp'] == az_fips]
            print(f"\nArizona records (FIPS 4): {len(az_data)}")
            
            if len(az_data) > 0:
                print(f"Arizona counties:")
                az_counties = sorted(az_data['cnty'].unique())
                print(az_counties)
                
                # Santa Cruz County FIPS is 023
                santa_cruz_fips = 23
                santa_cruz = az_data[az_data['cnty'] == santa_cruz_fips]
                print(f"\nSanta Cruz County (FIPS 23) records: {len(santa_cruz)}")
                if len(santa_cruz) > 0:
                    print(santa_cruz[['statefp', 'cnty', 'stcnty', 'tract', 'qct_id']])
    
    # Check Excel file
    excel_file = os.path.join(base_path, "qct_data_2025.xlsx")
    if os.path.exists(excel_file):
        print("\n" + "="*60)
        print("EXCEL FILE STATE CODES")
        print("="*60)
        
        df_excel = pd.read_excel(excel_file)
        
        # Check state column
        if 'state' in df_excel.columns:
            unique_states = sorted(df_excel['state'].unique())
            print(f"Unique state codes: {unique_states}")
            print(f"Total unique states: {len(unique_states)}")
            
            # Arizona FIPS code is 04
            az_fips = 4
            az_data = df_excel[df_excel['state'] == az_fips]
            print(f"\nArizona records (state code 4): {len(az_data)}")
            
            if len(az_data) > 0:
                print(f"Arizona counties:")
                az_counties = sorted(az_data['county'].unique())
                print(az_counties)
                
                # Look for Santa Cruz County - FIPS 023
                santa_cruz_fips = 23
                santa_cruz = az_data[az_data['county'] == santa_cruz_fips]
                print(f"\nSanta Cruz County (county code 23) records: {len(santa_cruz)}")
                if len(santa_cruz) > 0:
                    print("Santa Cruz County QCT data:")
                    print(santa_cruz[['state', 'county', 'stcnty', 'tract', 'qct']].head(10))
                else:
                    print(f"No Santa Cruz County found. Available AZ counties: {az_counties}")
                    
                # Also check for any QCT designations in Arizona
                az_qcts = az_data[az_data['qct'] == 1]
                print(f"\nArizona QCT tracts: {len(az_qcts)}")
                if len(az_qcts) > 0:
                    print("Arizona QCT tracts:")
                    print(az_qcts[['state', 'county', 'stcnty', 'tract', 'qct']].head(10))

def check_fips_codes():
    """Look up FIPS codes for reference"""
    
    print("\n" + "="*60)
    print("REFERENCE FIPS CODES")
    print("="*60)
    print("Arizona state FIPS: 04")
    print("Santa Cruz County, AZ FIPS: 023")
    print("Combined: 04023")
    print("Nogales is in Santa Cruz County, Arizona")
    print("United Church Village Apts: 31.3713391, -110.9240253")

if __name__ == "__main__":
    check_fips_codes()
    check_state_codes()
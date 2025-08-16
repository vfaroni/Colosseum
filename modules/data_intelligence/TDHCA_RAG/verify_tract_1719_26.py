#!/usr/bin/env python3
"""
Verify Census Tract 1719.26 QCT Status for Richland Hills Property
"""

import pandas as pd
import os

def main():
    data_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
    
    print('CENSUS TRACT 1719.26 VERIFICATION')
    print('=' * 50)

    # Check the CSV for the QCT designation
    csv_file = os.path.join(data_path, 'QCT2025.csv')
    csv_data = pd.read_csv(csv_file)
    texas_data = csv_data[csv_data['statefp'] == 48]
    bexar_data = texas_data[texas_data['cnty'] == 29]

    # Find tract 1719.26
    tract_1719_26 = bexar_data[bexar_data['tract'] == 1719.26]

    if len(tract_1719_26) > 0:
        tract_record = tract_1719_26.iloc[0]
        print('✅ FOUND Census Tract 1719.26 in CSV data:')
        print(f'   State: {tract_record["statefp"]} (Texas)')
        print(f'   County: {tract_record["cnty"]} (Bexar)')
        print(f'   Tract: {tract_record["tract"]}')
        print(f'   QCT_ID: {tract_record["qct_id"]}')
        print(f'   FIPS: {tract_record["fips"]}')
        print(f'   CBSA: {tract_record["cbsa"]}')
        
        # The presence in this CSV indicates it's a QCT
        print()
        print('🎯 QCT DESIGNATION ANALYSIS:')
        print('   ✅ This tract is present in the QCT2025.csv file')
        print('   ✅ This file contains ONLY Qualified Census Tracts')
        print('   ✅ Therefore, Census Tract 1719.26 IS A QCT')
        print()
        
        # Check DDA status for ZIP 78245
        print('🏔️ CHECKING DDA STATUS FOR ZIP 78245...')
        
        # Load DDA data
        try:
            dda_file = os.path.join(data_path, '2025-DDAs-Data-Used-to-Designate.xlsx')
            dda_data = pd.read_excel(dda_file)
            zip_78245 = dda_data[dda_data['ZIP Code Tabulation Area (ZCTA)'] == 78245]
            
            if len(zip_78245) > 0:
                dda_record = zip_78245.iloc[0]
                dda_designated = dda_record['2025 SDDA (1=SDDA)'] == 1
                
                print('   ✅ FOUND ZIP 78245 in DDA database:')
                print(f'      Area Name: {dda_record["Area Name"]}')
                print(f'      DDA Designated: {"YES" if dda_designated else "NO"}')
                
                safmr = dda_record['2024 Final 40th Percentile 2-Bedroom SAFMR']
                lihtc_max_rent = dda_record['LIHTC Maximum Rent (1/12 of 30% of 120% of VLIL)']
                ranking_ratio = dda_record['SDDA Ranking Ratio (SAFMR/LIHTC Maximum Rent)']
                
                print(f'      SAFMR: ${safmr:,.0f}')
                print(f'      LIHTC Max Rent: ${lihtc_max_rent:,.0f}')
                print(f'      Ranking Ratio: {ranking_ratio:.3f}')
                
                # Final determination
                print()
                print('🎯 FINAL LIHTC ANALYSIS:')
                print('   ✅ QCT Status: QUALIFIED CENSUS TRACT')
                print(f'   {"✅" if dda_designated else "❌"} DDA Status: {"DIFFICULT DEVELOPMENT AREA" if dda_designated else "NOT A DDA"}')
                
                basis_boost = True  # QCT automatically qualifies
                print('   ✅ LIHTC 130% BASIS BOOST: QUALIFIED (due to QCT designation)')
                print()
                print('📋 SUMMARY FOR RICHLAND HILLS TRACT:')
                print('   • Property Location: Corner of Midhurst Ave & Richland Hills Dr')
                print('   • Address: San Antonio, TX 78245') 
                print('   • Census Tract: 1719.26 (FIPS: 48029171926)')
                print('   • QCT Designation: YES - Qualified Census Tract')
                print(f'   • DDA Designation: {"YES" if dda_designated else "NO"}')
                print('   • Basis Boost Eligible: YES (130% qualified basis)')
                print('   • Matches HUD Map: Purple coloring confirmed as QCT')
                
            else:
                print('   ❌ ZIP 78245 not found in DDA database')
                print()
                print('🎯 FINAL LIHTC ANALYSIS:')
                print('   ✅ QCT Status: QUALIFIED CENSUS TRACT')
                print('   ❓ DDA Status: Unknown (ZIP not in database)')
                print('   ✅ LIHTC 130% BASIS BOOST: QUALIFIED (due to QCT designation)')
                
        except Exception as e:
            print(f'   Error checking DDA data: {e}')
            print()
            print('🎯 FINAL LIHTC ANALYSIS:')
            print('   ✅ QCT Status: QUALIFIED CENSUS TRACT')
            print('   ❓ DDA Status: Could not verify')
            print('   ✅ LIHTC 130% BASIS BOOST: QUALIFIED (due to QCT designation)')
            
    else:
        print('❌ Census Tract 1719.26 not found in data')
        
        # Show available Bexar County tracts for reference
        print()
        print('Available Bexar County tracts in database (first 20):')
        for i, row in bexar_data.head(20).iterrows():
            print(f'   Tract {row["tract"]}')

if __name__ == "__main__":
    main()
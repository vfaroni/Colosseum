#!/usr/bin/env python3
"""
Richland Hills QCT/DDA Analysis - Correct Census Tract 1719.26
"""

from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer
import pandas as pd

def main():
    # Initialize analyzer
    analyzer = ComprehensiveQCTDDAAnalyzer()

    # Richland Hills property coordinates (corner of Midhurst Ave & Richland Hills Dr)
    lat, lon = 29.4173, -98.6653
    print(f"Analyzing Richland Hills property at coordinates: {lat}, {lon}")
    print(f"Expected Census Tract: 1719.26 (GEOID: 48029171926)")
    print("=" * 80)

    # First get the location analysis using geocoding
    result = analyzer.lookup_qct_status(lat, lon)
    analyzer.print_detailed_analysis(result)

    print("\n" + "="*80)
    print("MANUAL VERIFICATION OF CENSUS TRACT 1719.26")
    print("="*80)

    # Manual lookup of Census Tract 1719.26 in Bexar County, Texas
    state_code = 48  # Texas
    county_code = 29  # Bexar County
    tract_number = 1719.26

    print(f"Looking up tract {tract_number} in Bexar County (029), Texas (48)")

    # Search QCT data for this specific tract
    matching_tract = analyzer.qct_data[
        (analyzer.qct_data['state'] == state_code) & 
        (analyzer.qct_data['county'] == county_code) & 
        (analyzer.qct_data['tract'] == tract_number)
    ]

    if len(matching_tract) > 0:
        record = matching_tract.iloc[0]
        qct_designated = record['qct'] == 1
        
        print(f"✅ Found Census Tract {tract_number} in HUD QCT database")
        print(f"QCT Designation: {'QCT' if qct_designated else 'Not QCT'}")
        print(f"QCT ID: {record.get('qct_id', 'Unknown')}")
        print(f"CBSA: {record.get('cbsa', 'Unknown')}")
        
        poverty_rates = {
            '2020': record.get('pov_rate_20', 0),
            '2021': record.get('pov_rate_21', 0), 
            '2022': record.get('pov_rate_22', 0)
        }
        
        print(f"Poverty Rates:")
        for year, rate in poverty_rates.items():
            if rate and rate > 0:
                print(f"  {year}: {rate:.1%}")
        
        print(f"Income Limits:")
        for year in ['20', '21', '22']:
            inc_lim = record.get(f'adj_inc_lim_{year}')
            if inc_lim and inc_lim > 0:
                print(f"  20{year}: ${inc_lim:,.0f}")
        
        # Check DDA status for ZIP 78245
        print(f"\nChecking DDA status for ZIP 78245...")
        dda_info = analyzer.lookup_dda_status('78245')
        
        if dda_info:
            print(f"✅ ZIP 78245 DDA Analysis:")
            print(f"DDA Designated: {'Yes' if dda_info['dda_designated'] else 'No'}")
            print(f"Area Name: {dda_info['area_name']}")
            print(f"SAFMR: ${dda_info['safmr']:,.0f}")
            print(f"LIHTC Max Rent: ${dda_info['lihtc_max_rent']:,.0f}")
            print(f"Ranking Ratio: {dda_info['ranking_ratio']:.3f}")
        else:
            print(f"❌ ZIP 78245 not found in DDA database")
        
        # Final determination
        basis_boost_eligible = qct_designated or (dda_info and dda_info['dda_designated'])
        
        print(f"\n🎯 FINAL DETERMINATION:")
        print(f"QCT Status: {'QCT' if qct_designated else 'Not QCT'}")
        print(f"DDA Status: {'DDA' if dda_info and dda_info['dda_designated'] else 'Not DDA'}")
        print(f"LIHTC 130% Basis Boost Eligible: {'YES' if basis_boost_eligible else 'NO'}")
        
        if qct_designated:
            print(f"✅ CONFIRMED: Census Tract 1719.26 is a QCT (matches HUD map purple coloring)")
            print(f"✅ CONFIRMED: Property qualifies for 130% qualified basis boost due to QCT designation")
        
    else:
        print(f"❌ Census Tract {tract_number} not found in QCT database")
        print(f"This may indicate a data issue or tract number mismatch")
        
        # Let's also check what tracts we do have in Bexar County
        print(f"\nAvailable tracts in Bexar County (showing first 10):")
        bexar_tracts = analyzer.qct_data[
            (analyzer.qct_data['state'] == state_code) & 
            (analyzer.qct_data['county'] == county_code)
        ]
        print(f"Total tracts in Bexar County: {len(bexar_tracts)}")
        
        if len(bexar_tracts) > 0:
            for i, row in bexar_tracts.head(10).iterrows():
                qct_status = "QCT" if row['qct'] == 1 else "Not QCT"
                print(f"  Tract {row['tract']}: {qct_status}")

if __name__ == "__main__":
    main()
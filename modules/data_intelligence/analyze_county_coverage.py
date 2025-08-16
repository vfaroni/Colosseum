#!/usr/bin/env python3
"""
Analyze County Coverage in EnviroStor Databases
Check which of our target counties have data
"""

import pandas as pd
from pathlib import Path

def analyze_county_coverage():
    """Check county coverage across all EnviroStor databases"""
    
    base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
    data_path = base_path / "data_sets" / "california" / "CA_Environmental_Data"
    
    # Our target counties from the mission
    tier1_counties = ['Los Angeles', 'San Diego', 'Orange', 'San Francisco', 'Alameda']
    
    tier2_counties = ['Riverside', 'San Bernardino', 'Sacramento', 'Contra Costa', 'Santa Clara']
    
    tier3_counties = ['Ventura', 'San Joaquin', 'Fresno', 'Kern', 'San Mateo']
    
    tier4_counties = ['Stanislaus', 'Sonoma', 'Marin', 'Monterey']
    
    all_target_counties = tier1_counties + tier2_counties + tier3_counties + tier4_counties
    
    # Datasets to check
    datasets = {
        'CleanupSites': 'EnviroStorCleanupSites/sites.txt',
        'HazardousWaste': 'EnviroStorHazardousWaste/hazardous_waste_facilities.txt',
        'ICESites': 'EnviroStorICESites/ice_sites.txt'
    }
    
    print("="*70)
    print("COUNTY COVERAGE ANALYSIS - ENVIROSTOR DATABASES")
    print("="*70)
    
    coverage_summary = {}
    
    for dataset_name, file_path in datasets.items():
        full_path = data_path / file_path
        
        if full_path.exists():
            print(f"\n{dataset_name}:")
            print("-"*50)
            
            try:
                # Read with error handling
                df = pd.read_csv(full_path, sep='\t', low_memory=False, 
                                encoding='latin-1', on_bad_lines='skip')
                
                # Find county column
                county_col = None
                for col in ['COUNTY', 'County', 'county']:
                    if col in df.columns:
                        county_col = col
                        break
                
                if county_col:
                    # Get county counts
                    county_counts = df[county_col].value_counts()
                    
                    # Check our target counties
                    for tier_name, counties in [
                        ('TIER 1 (Immediate)', tier1_counties),
                        ('TIER 2 (Major Markets)', tier2_counties),
                        ('TIER 3 (Secondary)', tier3_counties),
                        ('TIER 4 (Emerging)', tier4_counties)
                    ]:
                        print(f"\n  {tier_name}:")
                        for county in counties:
                            # Check various formats
                            count = 0
                            for idx, val in county_counts.items():
                                if county.upper() in str(idx).upper():
                                    count = val
                                    break
                            
                            status = "✅" if count > 0 else "❌"
                            print(f"    {status} {county:20} {count:6} records")
                            
                            if county not in coverage_summary:
                                coverage_summary[county] = {}
                            coverage_summary[county][dataset_name] = count
                            
            except Exception as e:
                print(f"  ERROR reading {dataset_name}: {e}")
    
    # Summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE - ALL TARGET COUNTIES")
    print("="*70)
    print(f"{'County':<20} {'Cleanup':<10} {'HazWaste':<10} {'ICE':<10} {'TOTAL':<10} {'Status'}")
    print("-"*70)
    
    for county in all_target_counties:
        if county in coverage_summary:
            cleanup = coverage_summary[county].get('CleanupSites', 0)
            hazwaste = coverage_summary[county].get('HazardousWaste', 0)
            ice = coverage_summary[county].get('ICESites', 0)
            total = cleanup + hazwaste + ice
            status = "✅ Ready" if total > 0 else "❌ No Data"
            print(f"{county:<20} {cleanup:<10} {hazwaste:<10} {ice:<10} {total:<10} {status}")
        else:
            print(f"{county:<20} {'0':<10} {'0':<10} {'0':<10} {'0':<10} ❌ No Data")
    
    # Statistics
    counties_with_data = sum(1 for c in coverage_summary.values() if sum(c.values()) > 0)
    total_records = sum(sum(c.values()) for c in coverage_summary.values())
    
    print("\n" + "="*70)
    print(f"COVERAGE STATISTICS:")
    print(f"  Counties with data: {counties_with_data}/{len(all_target_counties)}")
    print(f"  Total records available: {total_records:,}")
    print(f"  Already processed (Tier 1): 5 counties")
    print(f"  Ready to process: {counties_with_data - 5} additional counties")
    print("="*70)

if __name__ == "__main__":
    analyze_county_coverage()
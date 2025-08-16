#!/usr/bin/env python3
"""
Process ALL California Counties from EnviroStor Data
Complete statewide environmental database
WINGMAN Execution - Mission CA-ENV-2025-002
Date: 2025-08-09
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

def process_all_california_counties():
    """Process EnviroStor data for ALL California counties"""
    
    base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
    data_path = base_path / "data_sets" / "california" / "CA_Environmental_Data"
    
    # Process each dataset
    datasets = {
        'CleanupSites': 'EnviroStorCleanupSites/sites.txt',
        'HazardousWaste': 'EnviroStorHazardousWaste/hazardous_waste_facilities.txt',
        'ICESites': 'EnviroStorICESites/ice_sites.txt'
    }
    
    all_counties = set()
    results = {}
    
    print("="*70)
    print("PROCESSING ALL CALIFORNIA COUNTIES - COMPLETE STATEWIDE COVERAGE")
    print("="*70)
    
    for dataset_name, file_path in datasets.items():
        full_path = data_path / file_path
        
        if full_path.exists():
            print(f"\nProcessing {dataset_name}...")
            
            # Read with proper encoding
            try:
                df = pd.read_csv(full_path, sep='\t', low_memory=False, dtype=str, 
                                encoding='latin-1', on_bad_lines='skip')
            except Exception as e:
                print(f"  ERROR reading {dataset_name}: {e}")
                continue
                
            print(f"Total records in dataset: {len(df)}")
            
            # Find county column
            county_col = None
            for col in ['COUNTY', 'County', 'county']:
                if col in df.columns:
                    county_col = col
                    break
            
            if county_col:
                # Get unique counties
                unique_counties = df[county_col].dropna().unique()
                
                # Process each county
                for county in unique_counties:
                    # Clean county name
                    county = str(county).strip()
                    if county and county.upper() != 'COUNTY':  # Skip header rows
                        all_counties.add(county)
                        
                        # Filter for county
                        county_df = df[df[county_col] == county]
                        
                        if len(county_df) > 0:
                            # Create county directory
                            county_dir = data_path / "All_CA_Counties" / county.replace(' ', '_').replace('/', '_')
                            county_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Save to CSV
                            output_file = county_dir / f"{county.replace(' ', '_').replace('/', '_')}_{dataset_name}.csv"
                            county_df.to_csv(output_file, index=False)
                            
                            # Track results
                            if county not in results:
                                results[county] = {}
                            results[county][dataset_name] = len(county_df)
                            
                print(f"  Processed {len(unique_counties)} counties")
    
    # Sort counties alphabetically
    sorted_counties = sorted(all_counties)
    
    print("\n" + "="*70)
    print(f"COMPLETE CALIFORNIA COVERAGE: {len(sorted_counties)} COUNTIES")
    print("="*70)
    
    # Create master README
    create_master_readme(data_path / "All_CA_Counties", sorted_counties, results)
    
    # Create README for each county
    for county in sorted_counties:
        if county in results:
            create_county_readme(data_path / "All_CA_Counties", county, results[county])
    
    # Print summary table
    print(f"\n{'County':<25} {'Cleanup':<10} {'HazWaste':<10} {'ICE':<10} {'TOTAL':<10}")
    print("-"*75)
    
    total_all = 0
    for county in sorted_counties:
        if county in results:
            cleanup = results[county].get('CleanupSites', 0)
            hazwaste = results[county].get('HazardousWaste', 0)
            ice = results[county].get('ICESites', 0)
            total = cleanup + hazwaste + ice
            total_all += total
            print(f"{county:<25} {cleanup:<10} {hazwaste:<10} {ice:<10} {total:<10}")
    
    print("-"*75)
    print(f"{'STATEWIDE TOTAL':<25} {'':<10} {'':<10} {'':<10} {total_all:<10}")
    
    # Save summary JSON
    summary = {
        'processing_date': datetime.now().isoformat(),
        'total_counties': len(sorted_counties),
        'counties': sorted_counties,
        'results_by_county': results,
        'total_records': total_all,
        'datasets_processed': list(datasets.keys())
    }
    
    summary_path = data_path / "All_CA_Counties" / "california_statewide_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ STATEWIDE PROCESSING COMPLETE!")
    print(f"📁 Output: data_sets/california/CA_Environmental_Data/All_CA_Counties/")
    print(f"📊 Total Records: {total_all:,}")
    print(f"🗺️ Counties Processed: {len(sorted_counties)}")
    
    return results

def create_master_readme(base_dir, counties, results):
    """Create master README for all California counties"""
    readme_content = f"""DATASET: California Environmental Data - COMPLETE STATEWIDE COVERAGE
SOURCE: California Department of Toxic Substances Control (DTSC) EnviroStor
SOURCE URL: https://www.envirostor.dtsc.ca.gov/public/data_download
SOURCE DATE: 2025-08 (Current as of download)
DOWNLOAD DATE: {datetime.now().strftime('%Y-%m-%d')}
DESCRIPTION: Complete statewide environmental contamination database
FORMAT: CSV (converted from tab-delimited)
COVERAGE: All {len(counties)} California Counties

STATEWIDE STATISTICS:
====================
Total Counties: {len(counties)}
Total Environmental Records: {sum(sum(county.values()) for county in results.values()):,}

DATA CATEGORIES:
- Cleanup Sites: DTSC-regulated contaminated properties
- Hazardous Waste: Active and closed treatment/storage facilities
- ICE Sites: Illegal drug lab cleanup locations

COUNTIES INCLUDED:
==================
"""
    
    for county in sorted(counties):
        if county in results:
            total = sum(results[county].values())
            readme_content += f"- {county}: {total} records\n"
    
    readme_content += f"""
UPDATE FREQUENCY: Monthly

NOTES:
- Complete statewide coverage from EnviroStor public portal
- Each county has its own subdirectory with filtered data
- Includes all site addresses, contamination types, and cleanup status
- Some sites may have multiple records for different activities

PROCESSING DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}
GENERATED BY: Colosseum LIHTC Platform - WINGMAN Agent
MISSION: CA Environmental Data Acquisition - STATEWIDE
"""
    
    readme_path = base_dir / "README_STATEWIDE.txt"
    with open(readme_path, 'w') as f:
        f.write(readme_content)

def create_county_readme(base_dir, county, county_data):
    """Create README for individual county"""
    county_dir = base_dir / county.replace(' ', '_').replace('/', '_')
    readme_path = county_dir / "README.txt"
    
    readme_content = f"""DATASET: California Environmental Data - {county} County
SOURCE: California Department of Toxic Substances Control (DTSC) EnviroStor
SOURCE URL: https://www.envirostor.dtsc.ca.gov/public/data_download
SOURCE DATE: 2025-08 (Current as of download)
DOWNLOAD DATE: {datetime.now().strftime('%Y-%m-%d')}
DESCRIPTION: Environmental contamination sites for {county} County
FORMAT: CSV
COVERAGE: {county} County, California

DATA SOURCES INCLUDED:
====================
"""
    
    for dataset, count in county_data.items():
        readme_content += f"""
{dataset.upper()}:
- RECORDS: {count}
- FILE: {county.replace(' ', '_').replace('/', '_')}_{dataset}.csv
"""
    
    readme_content += f"""
TOTAL RECORDS: {sum(county_data.values())}

UPDATE FREQUENCY: Monthly

PROCESSING DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}
GENERATED BY: Colosseum LIHTC Platform - WINGMAN Agent
"""
    
    with open(readme_path, 'w') as f:
        f.write(readme_content)

if __name__ == "__main__":
    results = process_all_california_counties()
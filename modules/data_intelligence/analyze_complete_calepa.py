#!/usr/bin/env python3
"""
Analyze Complete CalEPA Dataset Suite
7 Datasets: Sites, Coordinates, Chemicals, Regulated Programs, 
           Evaluations, Violations, Enforcements
WINGMAN Analysis - Mission CA-ENV-2025-002
Date: 2025-08-09
Source: https://siteportal.calepa.ca.gov/nsite/map/export
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

def analyze_complete_calepa():
    """Analyze all 7 CalEPA datasets"""
    
    base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
    data_path = base_path / "data_sets" / "california" / "CA_Environmental_Data" / "CalEPA_Compliance"
    
    print("="*80)
    print("COMPLETE CALEPA ENVIRONMENTAL DATABASE ANALYSIS")
    print("Source: https://siteportal.calepa.ca.gov/nsite/map/export")
    print("="*80)
    
    results = {}
    
    # Core Site Data
    print("\n" + "="*80)
    print("CORE SITE INFORMATION")
    print("="*80)
    
    # 1. Site.csv - Master site list
    print("\n1. SITE MASTER LIST (Site.csv)")
    print("-"*40)
    site_file = data_path / "Site.csv"
    if site_file.exists():
        df_site = pd.read_csv(site_file, nrows=10000, low_memory=False)
        print(f"File size: {site_file.stat().st_size / (1024*1024):.1f} MB")
        print(f"Columns: {', '.join(df_site.columns[:10])}...")
        print(f"Total columns: {len(df_site.columns)}")
        
        # Check for key fields
        if 'City' in df_site.columns:
            cities = df_site['City'].value_counts().head(10)
            print(f"\nTop 10 Cities:")
            for city, count in cities.items():
                print(f"  {city}: {count}")
        
        if 'County' in df_site.columns:
            counties = df_site['County'].value_counts().head(10)
            print(f"\nTop 10 Counties:")
            for county, count in counties.items():
                print(f"  {county}: {count}")
        
        results['sites'] = {
            'file_size_mb': site_file.stat().st_size / (1024*1024),
            'columns': list(df_site.columns),
            'sample_size': len(df_site)
        }
    
    # 2. Coordinates.csv - Geospatial data
    print("\n2. GEOSPATIAL DATA (Coordinates.csv)")
    print("-"*40)
    coord_file = data_path / "Coordinates.csv"
    if coord_file.exists():
        df_coord = pd.read_csv(coord_file, nrows=10000, low_memory=False)
        print(f"File size: {coord_file.stat().st_size / (1024*1024):.1f} MB")
        print(f"Columns: {', '.join(df_coord.columns)}")
        
        # Check coordinate coverage
        if 'Latitude' in df_coord.columns and 'Longitude' in df_coord.columns:
            valid_coords = df_coord[(df_coord['Latitude'].notna()) & 
                                   (df_coord['Longitude'].notna())]
            print(f"Sites with coordinates: {len(valid_coords)} / {len(df_coord)}")
            
            # Check coordinate bounds (California approximate)
            ca_sites = valid_coords[(valid_coords['Latitude'] > 32) & 
                                   (valid_coords['Latitude'] < 42) &
                                   (valid_coords['Longitude'] < -114) & 
                                   (valid_coords['Longitude'] > -125)]
            print(f"Sites within California bounds: {len(ca_sites)}")
        
        results['coordinates'] = {
            'file_size_mb': coord_file.stat().st_size / (1024*1024),
            'columns': list(df_coord.columns),
            'sample_size': len(df_coord)
        }
    
    # Environmental Data
    print("\n" + "="*80)
    print("ENVIRONMENTAL DATA")
    print("="*80)
    
    # 3. Chemicals.csv - Chemical contamination
    print("\n3. CHEMICAL DATA (Chems.csv)")
    print("-"*40)
    chem_file = data_path / "Chems.csv"
    if chem_file.exists():
        df_chem = pd.read_csv(chem_file, nrows=10000, low_memory=False)
        print(f"File size: {chem_file.stat().st_size / (1024*1024):.1f} MB")
        print(f"Columns: {', '.join(df_chem.columns)}")
        
        # Check for chemical types
        chem_cols = [col for col in df_chem.columns if 'chem' in col.lower() or 'contam' in col.lower()]
        if chem_cols:
            print(f"Chemical-related columns: {chem_cols[:5]}")
        
        results['chemicals'] = {
            'file_size_mb': chem_file.stat().st_size / (1024*1024),
            'columns': list(df_chem.columns),
            'sample_size': len(df_chem)
        }
    
    # 4. Site Regulated Programs (SiteEI.csv)
    print("\n4. REGULATED PROGRAMS (SiteEI.csv)")
    print("-"*40)
    prog_file = data_path / "SiteEI.csv"
    if prog_file.exists():
        df_prog = pd.read_csv(prog_file, nrows=10000, low_memory=False)
        print(f"File size: {prog_file.stat().st_size / (1024*1024):.1f} MB")
        print(f"Columns: {', '.join(df_prog.columns[:10])}...")
        print(f"Total columns: {len(df_prog.columns)}")
        
        # Check for program types
        prog_cols = [col for col in df_prog.columns if 'program' in col.lower() or 'permit' in col.lower()]
        if prog_cols:
            print(f"Program-related columns found: {len(prog_cols)}")
        
        results['regulated_programs'] = {
            'file_size_mb': prog_file.stat().st_size / (1024*1024),
            'columns': list(df_prog.columns),
            'sample_size': len(df_prog)
        }
    
    # Compliance Data (already analyzed)
    print("\n" + "="*80)
    print("COMPLIANCE & ENFORCEMENT DATA")
    print("="*80)
    
    print("\n5. EVALUATIONS: 1,486,657 records (433.8 MB)")
    print("6. VIOLATIONS: 3,092,643 records (875.9 MB)")
    print("7. ENFORCEMENTS: 172,874 records (37.5 MB)")
    
    # Get actual record counts for new files
    print("\n" + "="*80)
    print("CALCULATING TOTAL RECORDS...")
    print("-"*80)
    
    import subprocess
    
    for filename, label in [("Site.csv", "Sites"), 
                            ("Coordinates.csv", "Coordinates"),
                            ("Chems.csv", "Chemicals"),
                            ("SiteEI.csv", "Regulated Programs")]:
        filepath = data_path / filename
        if filepath.exists():
            result = subprocess.run(['wc', '-l', str(filepath)], capture_output=True, text=True)
            line_count = int(result.stdout.split()[0]) - 1  # Subtract header
            print(f"{label}: {line_count:,} records")
            if label.lower().replace(' ', '_') in results:
                results[label.lower().replace(' ', '_')]['total_records'] = line_count
    
    # Create comprehensive README
    create_calepa_readme(data_path, results)
    
    # Save complete analysis
    analysis_file = data_path / "complete_calepa_analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*80)
    print("COMPLETE CALEPA DATABASE SUMMARY")
    print("="*80)
    
    print(f"""
DATABASE COMPONENTS:
1. Site Master List     - Facility information with addresses
2. Coordinates          - Latitude/Longitude for spatial analysis  
3. Chemicals            - Contamination and chemical data
4. Regulated Programs   - Permits and regulatory programs
5. Evaluations          - 1.5M inspection records
6. Violations           - 3.1M violation records
7. Enforcements         - 173K enforcement actions

TOTAL ESTIMATED RECORDS: ~5+ Million
TOTAL DATA VOLUME: ~1.4 GB

This is a COMPLETE environmental compliance database for California,
providing everything needed for comprehensive LIHTC environmental screening.
""")
    
    return results

def create_calepa_readme(data_path, results):
    """Create comprehensive README for CalEPA data"""
    
    readme_content = f"""DATASET: CalEPA Complete Environmental Database
SOURCE: California Environmental Protection Agency
SOURCE URL: https://siteportal.calepa.ca.gov/nsite/map/export
DOWNLOAD DATE: {datetime.now().strftime('%Y-%m-%d')}
DESCRIPTION: Complete California environmental compliance and contamination database
FORMAT: CSV
COVERAGE: Statewide California - All Counties

DATABASE COMPONENTS:
====================

1. SITE MASTER LIST (Site.csv)
   - Description: Master list of all regulated facilities
   - Records: Site information with addresses, cities, counties
   - Key Fields: SiteID, SiteName, Address, City, County, ZIP
   - File Size: {results.get('sites', {}).get('file_size_mb', 0):.1f} MB

2. COORDINATES (Coordinates.csv)
   - Description: Geospatial coordinates for sites
   - Records: Latitude/Longitude pairs for mapping
   - Key Fields: SiteID, Latitude, Longitude
   - File Size: {results.get('coordinates', {}).get('file_size_mb', 0):.1f} MB
   
3. CHEMICALS (Chems.csv)
   - Description: Chemical contamination data
   - Records: Hazardous substances and contaminants
   - Key Fields: SiteID, Chemical information
   - File Size: {results.get('chemicals', {}).get('file_size_mb', 0):.1f} MB

4. REGULATED PROGRAMS (SiteEI.csv)
   - Description: Environmental permits and programs
   - Records: Regulatory program participation
   - Key Fields: SiteID, Program types, Permit information
   - File Size: {results.get('regulated_programs', {}).get('file_size_mb', 0):.1f} MB

5. EVALUATIONS (Evaluations.csv)
   - Description: Site inspections and evaluations
   - Records: 1,486,657 inspection records
   - Key Fields: SiteID, EvalDate, ViolationsFound, EvalType
   - File Size: 433.8 MB

6. VIOLATIONS (Violations.csv)
   - Description: Environmental violations
   - Records: 3,092,643 violation records
   - Key Fields: SiteID, ViolationDate, Citation, ViolationDescription
   - File Size: 875.9 MB

7. ENFORCEMENTS (EA.csv)
   - Description: Enforcement actions taken
   - Records: 172,874 enforcement records
   - Key Fields: SiteID, EnfActionDate, EnfActionType, EnfActionDescription
   - File Size: 37.5 MB

TOTAL DATABASE SIZE: ~1.4 GB
TOTAL RECORDS: ~5+ Million

RELATIONSHIP STRUCTURE:
- All tables linked by SiteID
- Sites → Coordinates (1:1 geospatial)
- Sites → Chemicals (1:many contamination)
- Sites → Regulated Programs (1:many permits)
- Sites → Evaluations → Violations → Enforcements (compliance chain)

USE CASES FOR LIHTC:
- Environmental site screening
- Contamination proximity analysis
- Regulatory compliance history
- Risk assessment for due diligence
- Phase I ESA requirement identification

UPDATE FREQUENCY: Periodic (check CalEPA portal for updates)

NOTES:
- Data exported from CalEPA Site Portal
- Includes all regulated facilities in California
- Some sites may not have coordinates
- Violation/enforcement history goes back multiple years
- Critical for environmental due diligence

PROCESSING DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}
GENERATED BY: Colosseum LIHTC Platform - WINGMAN Agent
MISSION: CA Environmental Data Acquisition - CalEPA Complete
"""
    
    readme_path = data_path / "README_CALEPA_COMPLETE.txt"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"\nCreated comprehensive README: README_CALEPA_COMPLETE.txt")

if __name__ == "__main__":
    results = analyze_complete_calepa()
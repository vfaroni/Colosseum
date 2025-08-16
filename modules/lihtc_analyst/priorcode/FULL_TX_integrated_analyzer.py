"""
Test script for Integrated Texas Land Analyzer
Tests proximity analysis with TDHCA competition rules
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from texas_land_analyzer_integrated import TexasLandAnalyzerIntegrated

def test_integrated_analyzer():
    """
    Test the integrated analyzer with 5 properties
    """
    # Configuration
    API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'AIzaSyBlOVHaaTw9nbgBlIuF90xlXHbgfzvUWAM')
    CENSUS_API_KEY = os.environ.get('CENSUS_API_KEY')  # Optional
    
    # Input file
    input_file = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Costar/TX/CoStar_TX_Land_TDHCA_FLOOD_Analysis_20250606_113809.xlsx'
    
    print("Loading dataset...")
    df_full = pd.read_excel(input_file)
    print(f"Total properties in file: {len(df_full)}")
    
    # Take first 5 properties for testing
    df_sample = df_full.copy()  # Process entire dataset
    print(f"\nTesting with {len(df_sample)} properties")
    print("\nProperties being tested:")
    for idx, row in df_sample.iterrows():
        print(f"{idx+1}. {row.get('Address', 'N/A')}, {row.get('City', 'N/A')}, {row.get('County', 'N/A')} County")
    
    # Initialize integrated analyzer
    print("\nInitializing Integrated Texas Land Analyzer...")
    analyzer = TexasLandAnalyzerIntegrated(
        google_maps_api_key=API_KEY,
        census_api_key=CENSUS_API_KEY
    )
    
    print("\nRunning integrated analysis with STRICT filtering...")
    print("Features:")
    print("✅ Texas public schools dataset (no private/religious schools)")
    print("✅ Strict grocery store filtering (supermarkets only, 10+ reviews)")
    print("✅ Strict transit filtering (bus_station type only)")
    print("✅ Strict pharmacy filtering (excludes Dollar stores)")
    print("✅ Strict hospital filtering (emergency hospitals only)")
    print("✅ TDHCA competition analysis with Google ratings")
    print("✅ Hardcoded Texas city populations")
    
    # Run analysis - test both 4% and 9% rules
    results_df = analyzer.analyze_multiple_sites(df_sample, check_9pct_rules=True)
    
    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'Texas_Land_Integrated_Analysis_{timestamp}_TEST.xlsx'
    
    print(f"\nGenerating comprehensive report...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Full results
        results_df.to_excel(writer, sheet_name='Integrated Analysis', index=False)
        
        # Summary sheet
        summary_data = []
        for idx, row in results_df.iterrows():
            summary = {
                'Property': f"{row['Address']}, {row['City']}",
                'Eligibility': row['eligibility'],
                # Schools from Texas dataset
                'Elementary School': row.get('elementary_school_name', 'None'),
                'Elem Distance': row.get('elementary_school_distance_miles', ''),
                'Middle School': row.get('middle_school_name', 'None'),
                'Middle Distance': row.get('middle_school_distance_miles', ''),
                'High School': row.get('high_school_name', 'None'),
                'High Distance': row.get('high_school_distance_miles', ''),
                # Essential services with strict filtering
                'Grocery Store': row.get('grocery_store_name', 'None'),
                'Grocery Distance': row.get('grocery_store_distance_miles', ''),
                'Pharmacy': row.get('pharmacy_name', 'None'),
                'Pharmacy Distance': row.get('pharmacy_distance_miles', ''),
                'Hospital': row.get('hospital_name', 'None'),
                'Hospital Distance': row.get('hospital_distance_miles', ''),
                # Transit and parks
                'Transit Stop': row.get('transit_stop_name', 'None'),
                'Transit Distance': row.get('transit_stop_distance_miles', ''),
                # Competition
                'One Mile Rule': 'PASS' if row['one_mile_compliant'] else 'FAIL',
                'Competing Projects': row['one_mile_competing_count'],
                'Nearest LIHTC': row.get('nearest_lihtc_name', 'None'),
                'LIHTC Distance': row.get('nearest_lihtc_distance', ''),
                'LIHTC Rating': row.get('nearest_lihtc_rating', ''),
                # 9% specific
                'Same Tract Points': row.get('same_tract_points', 'N/A')
            }
            summary_data.append(summary)
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Add validation sheet
        validation_data = []
        for idx, row in results_df.iterrows():
            val = {
                'Property': f"{row['Address']}, {row['City']}",
                'Grocery Store': row.get('grocery_store_name', 'NOT FOUND'),
                'Grocery Distance': row.get('grocery_store_distance_miles', ''),
                'Grocery Rating': row.get('grocery_store_rating', ''),
                'Grocery Reviews': row.get('grocery_store_rating_count', ''),
                'Grocery Types': row.get('grocery_store_types', ''),
                'Pharmacy': row.get('pharmacy_name', 'NOT FOUND'),
                'Pharmacy Distance': row.get('pharmacy_distance_miles', ''),
                'Pharmacy Types': row.get('pharmacy_types', ''),
                'Hospital': row.get('hospital_name', 'NOT FOUND'),
                'Hospital Distance': row.get('hospital_distance_miles', ''),
                'Hospital Types': row.get('hospital_types', ''),
                'Transit': row.get('transit_stop_name', 'NOT FOUND'),
                'Transit Distance': row.get('transit_stop_distance_miles', ''),
                'Transit Types': row.get('transit_stop_types', '')
            }
            validation_data.append(val)
        
        validation_df = pd.DataFrame(validation_data)
        validation_df.to_excel(writer, sheet_name='Amenity Validation', index=False)
        
        # Statistics sheet
        stats_data = {
            'Metric': [
                'Total Properties Analyzed',
                'Properties Eligible (Pass One Mile Rule)',
                'Properties with LIHTC Competition',
                'Properties with Elementary School Found',
                'Properties with Middle School Found',
                'Properties with High School Found',
                'Properties with Grocery Store Found',
                'Properties with Pharmacy Found',
                'Properties with Hospital Found',
                'Properties with Transit Stop Found',
                'Properties with City Population Data'
            ],
            'Value': [
                len(results_df),
                sum(results_df['eligibility'] == 'ELIGIBLE'),
                sum(results_df['one_mile_competing_count'] > 0),
                sum(results_df['elementary_school_name'].notna()) if 'elementary_school_name' in results_df else 0,
                sum(results_df['middle_school_name'].notna()) if 'middle_school_name' in results_df else 0,
                sum(results_df['high_school_name'].notna()) if 'high_school_name' in results_df else 0,
                sum(results_df['grocery_store_name'].notna()) if 'grocery_store_name' in results_df else 0,
                sum(results_df['pharmacy_name'].notna()) if 'pharmacy_name' in results_df else 0,
                sum(results_df['hospital_name'].notna()) if 'hospital_name' in results_df else 0,
                sum(results_df['transit_stop_name'].notna()) if 'transit_stop_name' in results_df else 0,
                sum(results_df['city_population'].notna())
            ]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)
    
    print(f"\nIntegrated analysis complete! Results saved to: {output_file}")
    
    # Print detailed results
    print("\n" + "="*80)
    print("DETAILED TEST RESULTS:")
    print("="*80)
    
    for idx, row in results_df.iterrows():
        print(f"\n{'='*60}")
        print(f"PROPERTY {idx+1}: {row['Address']}, {row['City']}")
        print(f"{'='*60}")
        
        print(f"\nELIGIBILITY: {row['eligibility']}")
        
        print(f"\nTDHCA COMPETITION ANALYSIS:")
        print(f"  One Mile Three Year Rule: {'✅ PASS' if row['one_mile_compliant'] else '❌ FAIL'}")
        if row['one_mile_competing_count'] > 0:
            print(f"  Competing Projects Found: {row['one_mile_competing_count']}")
            print(f"  Nearest: {row.get('nearest_lihtc_name', 'Unknown')}")
            print(f"    - Distance: {row.get('nearest_lihtc_distance', 'N/A')} miles")
            print(f"    - Year: {row.get('nearest_lihtc_year', 'N/A')}")
            print(f"    - Units: {row.get('nearest_lihtc_units', 'N/A')}")
            rating = row.get('nearest_lihtc_rating')
            if rating and pd.notna(rating):
                print(f"    - Google Rating: {rating} ⭐")
        
        if pd.notna(row.get('same_tract_points')):
            print(f"  Same Census Tract Score: {row['same_tract_points']} points")
            print(f"    {row.get('same_tract_message', '')}")
        
        print(f"\nPUBLIC SCHOOLS (Texas Dataset):")
        # Schools
        for school_type in ['elementary', 'middle', 'high']:
            name = row.get(f'{school_type}_school_name')
            if name and pd.notna(name):
                dist = row.get(f'{school_type}_school_distance_miles', 'N/A')
                district = row.get(f'{school_type}_school_district', '')
                print(f"  {school_type.title()}: {name} - {dist} mi")
                if district:
                    print(f"    District: {district}")
            else:
                print(f"  {school_type.title()}: NOT FOUND")
        
        print(f"\nESSENTIAL SERVICES (Strict Filtering):")
        # Grocery
        grocery = row.get('grocery_store_name')
        if grocery and pd.notna(grocery):
            print(f"  Grocery: {grocery} - {row.get('grocery_store_distance_miles', 'N/A')} mi")
        else:
            print(f"  Grocery: NOT FOUND (no valid supermarkets)")
        
        # Pharmacy
        pharmacy = row.get('pharmacy_name')
        if pharmacy and pd.notna(pharmacy):
            print(f"  Pharmacy: {pharmacy} - {row.get('pharmacy_distance_miles', 'N/A')} mi")
        else:
            print(f"  Pharmacy: NOT FOUND")
        
        # Hospital
        hospital = row.get('hospital_name')
        if hospital and pd.notna(hospital):
            print(f"  Hospital: {hospital} - {row.get('hospital_distance_miles', 'N/A')} mi")
        else:
            print(f"  Hospital: NOT FOUND")
        
        # Transit
        transit = row.get('transit_stop_name')
        if transit and pd.notna(transit):
            print(f"  Transit: {transit} - {row.get('transit_stop_distance_miles', 'N/A')} mi")
        else:
            print(f"  Transit: NOT FOUND (no bus stations)")
        
        # City data
        if pd.notna(row.get('city_population')):
            print(f"\nCITY DATA:")
            print(f"  {row['City']} Population: {row['city_population']:,}")
    
    print("\n" + "="*80)
    print("INTEGRATED TEST COMPLETE WITH STRICT FILTERING!")
    print("This analysis uses:")
    print("- Texas public schools dataset")
    print("- Strict Google Places filtering")
    print("- TDHCA competition rules")
    print(f"Full results saved to: {output_file}")
    print("="*80)


if __name__ == "__main__":
    test_integrated_analyzer()
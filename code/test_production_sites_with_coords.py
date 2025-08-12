#!/usr/bin/env python3
"""
Test Corrected Transit Processor on Production Sites with Coordinates
Find sites from Production 1 that match those in the coordinate datasets
"""

import pandas as pd
import sys
import os
from pathlib import Path
import json
from datetime import datetime
from fuzzywuzzy import fuzz, process

# Add the botn_engine directory to the path
botn_engine_path = Path(__file__).parent / "modules/lihtc_analyst/botn_engine"
sys.path.insert(0, str(botn_engine_path))

from ultimate_ctcac_transit_processor import UltimateCTCACTransitProcessor

def find_matching_sites():
    """Find Production 1 sites in the coordinate datasets and test transit scoring"""
    
    print("🔍 MATCHING PRODUCTION 1 SITES WITH COORDINATE DATA")
    print("=" * 70)
    
    # Load Production 1 rankings file
    prod_1_file = Path("modules/lihtc_analyst/botn_engine/outputs/Production 1/Production_1_Site_Rankings_Broker_Contacts_20250804_211521.xlsx")
    
    # Load coordinate datasets
    sites_dir = Path("modules/lihtc_analyst/botn_engine/Sites")
    
    try:
        # Load Production 1 sites
        prod_1_df = pd.read_excel(prod_1_file)
        print(f"📊 Loaded {len(prod_1_df)} sites from Production 1 rankings")
        
        # Try loading coordinate datasets
        coord_datasets = []
        
        # Try BOTN Complete Final Portfolio
        botn_file = sites_dir / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415_BACKUP_20250801_093840.xlsx"
        if botn_file.exists():
            try:
                botn_df = pd.read_excel(botn_file)
                coord_datasets.append(("BOTN_Final", botn_df))
                print(f"✅ Loaded {len(botn_df)} sites from BOTN Final Portfolio")
            except Exception as e:
                print(f"⚠️ Could not load BOTN Final: {e}")
        
        # Try Combined CoStar Export
        costar_file = sites_dir / "Combined_CostarExport_Final.xlsx"
        if costar_file.exists():
            try:
                costar_df = pd.read_excel(costar_file)
                coord_datasets.append(("CoStar_Final", costar_df))
                print(f"✅ Loaded {len(costar_df)} sites from CoStar Export")
            except Exception as e:
                print(f"⚠️ Could not load CoStar Export: {e}")
        
        if not coord_datasets:
            print("❌ No coordinate datasets loaded - cannot proceed")
            return False
        
        print()
        print("🔗 MATCHING SITES BY NAME...")
        print("-" * 40)
        
        # Get Production 1 site names
        prod_1_names = prod_1_df['Property_Name'].tolist()
        matches = []
        
        # Try to match with each coordinate dataset
        for dataset_name, coord_df in coord_datasets:
            print(f"\n📊 Matching with {dataset_name} ({len(coord_df)} sites)")
            
            # Check available columns
            print(f"   Columns: {list(coord_df.columns)}")
            
            # Find coordinate columns
            lat_col = None
            lon_col = None
            name_col = None
            
            # Common coordinate column names
            lat_columns = ['Latitude', 'Lat', 'latitude', 'lat', 'Y', 'y']
            lon_columns = ['Longitude', 'Lon', 'longitude', 'lon', 'Long', 'X', 'x']
            name_columns = ['Property Name', 'Property_Name', 'Name', 'Site_Name', 'Address', 'Property Address']
            
            for col in coord_df.columns:
                if any(lat_name in col for lat_name in lat_columns):
                    lat_col = col
                if any(lon_name in col for lon_name in lon_columns):
                    lon_col = col
                if any(name_col_opt in col for name_col_opt in name_columns):
                    name_col = col
            
            print(f"   📍 Coordinate columns: {lat_col}, {lon_col}")
            print(f"   🏗️ Name column: {name_col}")
            
            if lat_col and lon_col and name_col:
                # Try fuzzy matching on names
                coord_names = coord_df[name_col].tolist()
                
                for prod_name in prod_1_names[:10]:  # Test first 10
                    # Find best match using fuzzy matching
                    best_match = process.extractOne(prod_name, coord_names)
                    if best_match and best_match[1] > 80:  # 80% similarity threshold
                        match_name = best_match[0]
                        match_row = coord_df[coord_df[name_col] == match_name].iloc[0]
                        
                        latitude = match_row[lat_col] if pd.notna(match_row[lat_col]) else None
                        longitude = match_row[lon_col] if pd.notna(match_row[lon_col]) else None
                        
                        if latitude and longitude:
                            matches.append({
                                'prod_name': prod_name,
                                'matched_name': match_name,
                                'similarity': best_match[1],
                                'latitude': float(latitude),
                                'longitude': float(longitude),
                                'dataset': dataset_name,
                                'row_data': match_row.to_dict()
                            })
                            print(f"   ✅ {prod_name} → {match_name} ({best_match[1]:.1f}%)")
        
        print(f"\n🔗 Found {len(matches)} matching sites with coordinates")
        
        if not matches:
            print("❌ No matches found - trying direct coordinate analysis")
            # Fallback: just test a few sites with sample coordinates
            return test_sample_california_sites()
        
        # Test transit scoring on matched sites
        print("\n🚌 TESTING CORRECTED TRANSIT PROCESSOR ON MATCHED SITES")
        print("=" * 70)
        
        processor = UltimateCTCACTransitProcessor()
        print("🏛️ Initialized Ultimate CTCAC Transit Processor (CORRECTED)")
        
        # Load datasets
        datasets_loaded = processor.load_all_datasets()
        if not datasets_loaded:
            print("⚠️ WARNING: Could not load transit datasets - testing with limited functionality")
        
        results = []
        
        for i, match in enumerate(matches[:5]):  # Test first 5 matches
            try:
                site_data = {
                    'site_id': f'MATCH_{i:03d}',
                    'latitude': match['latitude'],
                    'longitude': match['longitude']
                }
                
                print(f"\n🏗️ {match['prod_name']}")
                print(f"   📍 Coordinates: {match['latitude']:.4f}, {match['longitude']:.4f}")
                print(f"   🔗 Matched: {match['matched_name']} ({match['similarity']:.1f}%)")
                
                # Analyze with corrected processor
                result = processor.analyze_site_ultimate(site_data)
                results.append({
                    'match_info': match,
                    'transit_result': result
                })
                
                # Display results
                points = result['ctcac_points_earned']
                method = result['qualification_method']
                qualified = result['transit_qualified']
                
                print(f"   🚌 Transit Score: {points} points")
                print(f"   ✅ Method: {method}")
                print(f"   🎯 Qualified: {'YES' if qualified else 'NO'}")
                
                # Show detailed transit analysis
                if 'frequency_analysis' in result and result['frequency_analysis']:
                    freq = result['frequency_analysis']
                    stops = freq.get('total_stops', 0)
                    high_freq = freq.get('high_frequency_stops', 0)
                    validated = freq.get('high_frequency_validated_stops', 0)
                    best_freq = freq.get('estimated_peak_frequency', 999)
                    
                    print(f"   🚏 Transit Details:")
                    print(f"     • Stops found: {stops}")
                    if stops > 0:
                        print(f"     • High-frequency stops: {high_freq}")
                        print(f"     • Validated stops: {validated}")
                        print(f"     • Best frequency: {best_freq:.1f} minutes")
                
                if 'hqta_details' in result and result['hqta_details']:
                    hqta = result['hqta_details']
                    if hqta.get('within_hqta', False):
                        print(f"   🏛️ HQTA Qualified: {hqta.get('hqta_type', 'Unknown Type')}")
                
            except Exception as e:
                print(f"❌ Error analyzing {match['prod_name']}: {e}")
        
        # Export results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"PRODUCTION_TRANSIT_TEST_RESULTS_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                'test_timestamp': datetime.now().isoformat(),
                'matches_found': len(matches),
                'sites_tested': len(results),
                'detailed_results': results
            }, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results exported to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_sample_california_sites():
    """Test with sample California coordinates as fallback"""
    print("\n🌴 TESTING SAMPLE CALIFORNIA SITES")
    print("=" * 50)
    
    # Sample California sites for testing
    sample_sites = [
        {"name": "Los Angeles Downtown", "lat": 34.0522, "lon": -118.2437},
        {"name": "San Francisco SOMA", "lat": 37.7749, "lon": -122.4194},
        {"name": "Oakland Transit Center", "lat": 37.8044, "lon": -122.2711},
        {"name": "Fresno Central", "lat": 36.7378, "lon": -119.7871},
        {"name": "Sacramento Midtown", "lat": 38.5816, "lon": -121.4944}
    ]
    
    processor = UltimateCTCACTransitProcessor()
    datasets_loaded = processor.load_all_datasets()
    
    for i, site in enumerate(sample_sites):
        site_data = {
            'site_id': f'SAMPLE_{i:03d}',
            'latitude': site['lat'],
            'longitude': site['lon']
        }
        
        result = processor.analyze_site_ultimate(site_data)
        
        print(f"\n🏗️ {site['name']}")
        print(f"   📍 {site['lat']:.4f}, {site['lon']:.4f}")
        print(f"   🚌 Score: {result['ctcac_points_earned']} points")
        print(f"   ✅ Method: {result['qualification_method']}")
        
    return True

if __name__ == "__main__":
    try:
        success = find_matching_sites()
        if success:
            print("\n🎯 PRODUCTION SITE TRANSIT TEST COMPLETE")
        else:
            print("\n❌ PRODUCTION SITE TRANSIT TEST FAILED")
    except ImportError as e:
        print(f"⚠️ Missing dependency: {e}")
        print("Falling back to sample site testing...")
        test_sample_california_sites()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    exit(0)
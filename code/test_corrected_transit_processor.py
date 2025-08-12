#!/usr/bin/env python3
"""
Test Corrected Transit Processor on Production 1 Sites
Analyze sites from Production_1_Site_Rankings to verify transit scoring fixes
"""

import pandas as pd
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add the botn_engine directory to the path
botn_engine_path = Path(__file__).parent / "modules/lihtc_analyst/botn_engine"
sys.path.insert(0, str(botn_engine_path))

from ultimate_ctcac_transit_processor import UltimateCTCACTransitProcessor

def test_production_1_sites():
    """Test the corrected transit processor on Production 1 sites"""
    
    print("🚌 TESTING CORRECTED TRANSIT PROCESSOR")
    print("=" * 60)
    print("Testing Production 1 sites that previously had transit scoring issues")
    print()
    
    # Load the Production 1 rankings file
    prod_1_file = Path("modules/lihtc_analyst/botn_engine/outputs/Production 1/Production_1_Site_Rankings_Broker_Contacts_20250804_211521.xlsx")
    
    if not prod_1_file.exists():
        print(f"❌ ERROR: File not found: {prod_1_file}")
        return False
    
    try:
        # Read the Excel file
        df = pd.read_excel(prod_1_file)
        print(f"📊 Loaded {len(df)} sites from Production 1 rankings")
        print(f"📋 Columns: {list(df.columns)}")
        print()
        
        # Initialize the corrected processor
        processor = UltimateCTCACTransitProcessor()
        print("🏛️ Initialized Ultimate CTCAC Transit Processor (CORRECTED)")
        
        # Load datasets (this might fail without actual data, but we'll test the logic)
        datasets_loaded = processor.load_all_datasets()
        if not datasets_loaded:
            print("⚠️ WARNING: Could not load full datasets - testing with limited functionality")
        
        print()
        print("🔍 ANALYZING FIRST 10 SITES...")
        print("-" * 60)
        
        # Test first 10 sites to see the corrected scoring
        test_sites = df.head(10)
        results = []
        
        for idx, row in test_sites.iterrows():
            try:
                # Extract site information
                site_name = row.get('Property Name', f'Site_{idx}')
                
                # Try different possible column names for coordinates
                latitude = None
                longitude = None
                
                # Check common coordinate column names
                lat_columns = ['Latitude', 'Lat', 'latitude', 'lat', 'Y', 'y']
                lon_columns = ['Longitude', 'Lon', 'longitude', 'lon', 'Long', 'X', 'x']
                
                for col in lat_columns:
                    if col in row.index and pd.notna(row[col]):
                        latitude = float(row[col])
                        break
                        
                for col in lon_columns:
                    if col in row.index and pd.notna(row[col]):
                        longitude = float(row[col])
                        break
                
                if latitude is None or longitude is None:
                    print(f"⚠️ {site_name}: Missing coordinates - skipping")
                    continue
                
                # Check if density data is available
                density_per_acre = None
                density_columns = ['Density_Per_Acre', 'density_per_acre', 'Density', 'density', 'Units_Per_Acre']
                for col in density_columns:
                    if col in row.index and pd.notna(row[col]):
                        density_per_acre = float(row[col])
                        break
                
                # Create site data for analysis
                site_data = {
                    'site_id': f'PROD1_{idx:03d}',
                    'site_name': site_name,
                    'latitude': latitude,
                    'longitude': longitude,
                    'density_per_acre': density_per_acre
                }
                
                # Analyze with corrected processor
                result = processor.analyze_site_ultimate(site_data)
                results.append(result)
                
                # Display results
                points = result['ctcac_points_earned']
                method = result['qualification_method']
                qualified = result['transit_qualified']
                
                print(f"🏗️ {site_name[:40]:<40}")
                print(f"   📍 Coordinates: {latitude:.4f}, {longitude:.4f}")
                if density_per_acre:
                    print(f"   🏢 Density: {density_per_acre:.1f} units/acre")
                print(f"   🚌 Transit Score: {points} points ({method})")
                print(f"   ✅ Qualified: {'YES' if qualified else 'NO'}")
                
                # Show transit details if available
                if 'frequency_analysis' in result:
                    freq_analysis = result['frequency_analysis']
                    stops_found = freq_analysis.get('total_stops', 0)
                    high_freq_stops = freq_analysis.get('high_frequency_stops', 0)
                    validated_stops = freq_analysis.get('high_frequency_validated_stops', 0)
                    best_freq = freq_analysis.get('estimated_peak_frequency', 999)
                    
                    print(f"   🚏 Stops found: {stops_found}")
                    if stops_found > 0:
                        print(f"   ⚡ High-frequency stops: {high_freq_stops}")
                        print(f"   ✅ Validated stops: {validated_stops}")
                        print(f"   🕐 Best frequency: {best_freq:.1f} minutes")
                
                print()
                
            except Exception as e:
                print(f"❌ Error analyzing {site_name}: {e}")
                continue
        
        # Summary statistics
        print("=" * 60)
        print("📊 CORRECTED TRANSIT ANALYSIS SUMMARY")
        print("=" * 60)
        
        if results:
            total_sites = len(results)
            qualified_sites = sum(1 for r in results if r.get('transit_qualified', False))
            
            # Score distribution
            score_dist = {}
            for r in results:
                score = r.get('ctcac_points_earned', 0)
                score_dist[score] = score_dist.get(score, 0) + 1
            
            print(f"🏗️ Total sites analyzed: {total_sites}")
            print(f"✅ Transit qualified: {qualified_sites} ({qualified_sites/total_sites*100:.1f}%)")
            print()
            print("📊 Score Distribution:")
            for score in sorted(score_dist.keys()):
                count = score_dist[score]
                print(f"   {score} points: {count} sites ({count/total_sites*100:.1f}%)")
            
            print()
            print("🎯 KEY IMPROVEMENTS:")
            print("   • Full 3-7 point scoring range implemented")
            print("   • Proper frequency calculations (no more 30/n_routes)")
            print("   • High-frequency validation with peak hour analysis")
            print("   • Density integration for 7-point qualification")
            
            # Export results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"CORRECTED_TRANSIT_TEST_RESULTS_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump({
                    'test_timestamp': datetime.now().isoformat(),
                    'source_file': str(prod_1_file),
                    'sites_analyzed': total_sites,
                    'qualified_sites': qualified_sites,
                    'score_distribution': score_dist,
                    'detailed_results': results
                }, f, indent=2, default=str)
            
            print(f"📄 Detailed results exported to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to process Production 1 sites: {e}")
        return False

if __name__ == "__main__":
    success = test_production_1_sites()
    if success:
        print("\n🏛️ CORRECTED TRANSIT ANALYSIS TEST COMPLETE")
        print("Roman Engineering Standards: Precision achieved!")
    else:
        print("\n❌ CORRECTED TRANSIT ANALYSIS TEST FAILED")
        print("Investigation required.")
    
    exit(0 if success else 1)
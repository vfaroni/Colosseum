#!/usr/bin/env python3
"""
Analyze Top 10 Production 1 Sites for Transit Compliance
Process the first 10 sites from Production 1 rankings and evaluate CTCAC transit requirements
"""

import pandas as pd
import sys
import os
from pathlib import Path
import json
from datetime import datetime
import requests
import time

# Add the botn_engine directory to the path
botn_engine_path = Path(__file__).parent / "modules/lihtc_analyst/botn_engine"
sys.path.insert(0, str(botn_engine_path))

from ultimate_ctcac_transit_processor import UltimateCTCACTransitProcessor

def geocode_address(address, retries=3, delay=1):
    """Geocode address using OpenStreetMap Nominatim API with retry logic"""
    for attempt in range(retries):
        try:
            # Add city/state if not present
            if 'CA' not in address and 'California' not in address:
                address += ', CA'
            
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'us'
            }
            headers = {
                'User-Agent': 'LIHTC-Transit-Analysis/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            if results:
                result = results[0]
                lat = float(result['lat'])
                lon = float(result['lon'])
                return lat, lon, result['display_name']
            
            # If no results, try a simpler search
            if ',' in address:
                simple_address = address.split(',')[0] + ', CA'
                params['q'] = simple_address
                response = requests.get(url, params=params, headers=headers, timeout=10)
                results = response.json()
                if results:
                    result = results[0]
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    return lat, lon, result['display_name']
            
            return None, None, None
            
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            else:
                print(f"⚠️ Geocoding failed for {address}: {e}")
                return None, None, None

def analyze_production_1_top_10():
    """Analyze the first 10 sites from Production 1 rankings for transit compliance"""
    
    print("🏆 PRODUCTION 1 TOP 10 SITES - TRANSIT COMPLIANCE ANALYSIS")
    print("=" * 80)
    print("Analyzing first 10 sites from Production_1_Site_Rankings for CTCAC transit requirements")
    print("⚔️ Using STRIKE_LEADER corrected transit processor")
    print()
    
    # Load Production 1 rankings
    prod_file = Path("modules/lihtc_analyst/botn_engine/outputs/Production 1/Production_1_Site_Rankings_Broker_Contacts_20250804_211521.xlsx")
    
    if not prod_file.exists():
        print(f"❌ ERROR: File not found: {prod_file}")
        return False
    
    try:
        # Read Excel file
        df = pd.read_excel(prod_file)
        print(f"📊 Loaded {len(df)} total sites from Production 1 rankings")
        
        # Get first 10 sites
        top_10 = df.head(10)
        print(f"🎯 Analyzing top 10 ranked sites")
        print(f"📋 Available columns: {list(df.columns)}")
        print()
        
        # Initialize corrected processor
        processor = UltimateCTCACTransitProcessor()
        print("🏛️ Initialized Ultimate CTCAC Transit Processor (STRIKE_LEADER CORRECTED)")
        
        # Load datasets
        print("📊 Loading comprehensive transit datasets...")
        datasets_loaded = processor.load_all_datasets()
        print()
        
        print("🔍 ANALYZING TOP 10 SITES...")
        print("=" * 80)
        
        results = []
        compliant_sites = 0
        
        for idx, row in top_10.iterrows():
            try:
                rank = row.get('Rank', idx + 1)
                property_name = row.get('Property_Name', f'Site_{idx}')
                address = row.get('Property_Address', 'Unknown Address')
                city = row.get('City', 'Unknown City')
                market = row.get('Market', 'Unknown Market')
                units = row.get('Units', 'Unknown')
                price = row.get('Purchase_Price', 'Unknown')
                
                print(f"\n🏗️ RANK #{rank}: {property_name}")
                print(f"   📍 Address: {address}")
                print(f"   🏘️ City: {city}, Market: {market}")
                print(f"   🏢 Units: {units}, Price: ${price}")
                
                # Geocode the address
                full_address = f"{address}, {city}, CA" if address != 'Unknown Address' else f"{city}, CA"
                print(f"   🔍 Geocoding: {full_address}")
                
                lat, lon, geocoded_location = geocode_address(full_address)
                
                if lat is None or lon is None:
                    print(f"   ❌ Could not geocode address - SKIPPING")
                    results.append({
                        'rank': rank,
                        'property_name': property_name,
                        'address': address,
                        'city': city,
                        'geocoding_error': True,
                        'transit_qualified': False,
                        'ctcac_points': 0,
                        'reason': 'GEOCODING_FAILED'
                    })
                    continue
                
                print(f"   ✅ Geocoded to: {lat:.6f}, {lon:.6f}")
                
                # Estimate density if units available
                density_per_acre = None
                if units != 'Unknown' and str(units).replace(',', '').isdigit():
                    units_num = int(str(units).replace(',', ''))
                    # Estimate acres (typical LIHTC is 15-25 units/acre)
                    estimated_acres = units_num / 20  # Assume 20 units/acre
                    density_per_acre = units_num / estimated_acres if estimated_acres > 0 else None
                
                # Create site data
                site_data = {
                    'site_id': f'PROD1_RANK_{rank}',
                    'latitude': lat,
                    'longitude': lon,
                    'density_per_acre': density_per_acre
                }
                
                # Analyze transit compliance
                print(f"   🚌 Analyzing transit compliance...")
                result = processor.analyze_site_ultimate(site_data)
                
                # Extract key results
                points = result['ctcac_points_earned']
                method = result['qualification_method']
                qualified = result['transit_qualified']
                base_points = result.get('base_points', 0)
                tiebreaker = result.get('tiebreaker_points', 0)
                
                # Display results
                print(f"   🎯 TRANSIT RESULTS:")
                print(f"     🚌 CTCAC Score: {points} points (Base: {base_points} + Tiebreaker: {tiebreaker})")
                print(f"     📋 Method: {method}")
                print(f"     ✅ Compliant: {'YES' if qualified else 'NO'}")
                
                if qualified:
                    compliant_sites += 1
                
                # Show HQTA status
                hqta_details = result.get('hqta_details', {})
                if hqta_details.get('within_hqta', False):
                    print(f"     🏛️ HQTA: QUALIFIED ({hqta_details.get('hqta_type', 'Unknown')})")
                    print(f"       Agency: {hqta_details.get('agency_primary', 'Unknown')}")
                else:
                    print(f"     🏛️ HQTA: Not within boundary")
                    
                    # Show frequency analysis for non-HQTA
                    freq_analysis = result.get('frequency_analysis', {})
                    if freq_analysis and freq_analysis.get('total_stops', 0) > 0:
                        stops = freq_analysis.get('total_stops', 0)
                        high_freq = freq_analysis.get('high_frequency_stops', 0)
                        validated = freq_analysis.get('high_frequency_validated_stops', 0)
                        best_freq = freq_analysis.get('estimated_peak_frequency', 999)
                        
                        print(f"     🚏 Transit nearby: {stops} stops, {high_freq} high-freq, {validated} validated")
                        print(f"     🕐 Best frequency: {best_freq:.1f} minutes")
                
                # Store detailed results
                results.append({
                    'rank': rank,
                    'property_name': property_name,
                    'address': address,
                    'city': city,
                    'market': market,
                    'units': units,
                    'price': price,
                    'coordinates': {'lat': lat, 'lon': lon},
                    'geocoded_location': geocoded_location,
                    'density_per_acre': density_per_acre,
                    'transit_qualified': qualified,
                    'ctcac_points': points,
                    'base_points': base_points,
                    'tiebreaker_points': tiebreaker,
                    'qualification_method': method,
                    'hqta_qualified': hqta_details.get('within_hqta', False),
                    'hqta_type': hqta_details.get('hqta_type', None),
                    'transit_analysis': result
                })
                
                # Rate limiting for geocoding API
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error analyzing rank #{rank}: {e}")
                results.append({
                    'rank': rank,
                    'property_name': property_name,
                    'address': address,
                    'analysis_error': str(e),
                    'transit_qualified': False,
                    'ctcac_points': 0
                })
                continue
        
        # Summary Analysis
        print("\n" + "=" * 80)
        print("📊 TOP 10 SITES TRANSIT COMPLIANCE SUMMARY")
        print("=" * 80)
        
        total_analyzed = len([r for r in results if not r.get('geocoding_error', False) and not r.get('analysis_error')])
        
        print(f"🏗️ Total sites analyzed: {total_analyzed}/10")
        print(f"✅ Transit compliant sites: {compliant_sites}/{total_analyzed} ({compliant_sites/total_analyzed*100 if total_analyzed > 0 else 0:.1f}%)")
        print(f"❌ Non-compliant sites: {total_analyzed - compliant_sites}/{total_analyzed}")
        
        # Score distribution
        score_dist = {}
        hqta_count = 0
        
        for r in results:
            if not r.get('geocoding_error', False) and not r.get('analysis_error'):
                score = r.get('ctcac_points', 0)
                score_dist[score] = score_dist.get(score, 0) + 1
                if r.get('hqta_qualified', False):
                    hqta_count += 1
        
        print(f"\n📊 CTCAC Score Distribution:")
        for score in sorted(score_dist.keys()):
            count = score_dist[score]
            percentage = count/total_analyzed*100 if total_analyzed > 0 else 0
            print(f"   {score} points: {count} sites ({percentage:.1f}%)")
        
        print(f"\n🏛️ HQTA qualified sites: {hqta_count}/{total_analyzed}")
        
        # Identify problem sites
        problem_sites = []
        for r in results:
            if not r.get('transit_qualified', False) and not r.get('geocoding_error', False):
                problem_sites.append({
                    'rank': r.get('rank'),
                    'name': r.get('property_name'),
                    'city': r.get('city'),
                    'reason': r.get('qualification_method', 'Unknown')
                })
        
        if problem_sites:
            print(f"\n🚨 SITES NOT MEETING TRANSIT REQUIREMENTS:")
            for site in problem_sites:
                print(f"   • Rank #{site['rank']}: {site['name']} ({site['city']})")
                print(f"     Reason: {site['reason']}")
        
        # Export detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"PRODUCTION_1_TOP_10_TRANSIT_ANALYSIS_{timestamp}.json"
        
        export_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'source_file': str(prod_file),
            'analysis_summary': {
                'total_sites_analyzed': total_analyzed,
                'transit_compliant': compliant_sites,
                'compliance_rate_percent': compliant_sites/total_analyzed*100 if total_analyzed > 0 else 0,
                'hqta_qualified_sites': hqta_count,
                'score_distribution': score_dist
            },
            'problem_sites': problem_sites,
            'detailed_results': results,
            'methodology': 'STRIKE_LEADER corrected CTCAC transit processor'
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"\n📄 Detailed analysis exported to: {output_file}")
        
        # Final recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if problem_sites:
            print(f"   🚨 Review {len(problem_sites)} sites that don't meet transit requirements")
            print(f"   📊 Consider prioritizing transit-compliant alternatives")
            print(f"   🔍 Verify addresses and explore nearby transit developments")
        else:
            print(f"   ✅ All analyzed sites meet CTCAC transit requirements")
            
        print(f"   🎯 Overall compliance rate: {compliant_sites/total_analyzed*100 if total_analyzed > 0 else 0:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to process Production 1 file: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        print("🏛️ COLOSSEUM PRODUCTION 1 TRANSIT COMPLIANCE AUDIT")
        print("⚔️ Roman Engineering Standard: Every site must earn its place")
        print()
        
        success = analyze_production_1_top_10()
        
        if success:
            print("\n🏆 PRODUCTION 1 TOP 10 ANALYSIS COMPLETE")
            print("📊 Transit compliance audit finished - review recommendations above")
        else:
            print("\n❌ PRODUCTION 1 ANALYSIS FAILED")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    exit(0)
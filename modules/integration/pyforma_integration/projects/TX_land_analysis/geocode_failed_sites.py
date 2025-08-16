#!/usr/bin/env python3
"""
Geocode failed Texas sites using PositionStack API and updated QCT/DDA checker
"""

import pandas as pd
import requests
import time
import json
import os
import sys
from typing import Dict, Optional, Tuple

# Add the QCT/DDA analyzer path 
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code')

try:
    from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer
    print("✅ Successfully imported updated QCT/DDA analyzer")
except ImportError as e:
    print(f"❌ Failed to import QCT/DDA analyzer: {e}")
    print("Will skip QCT/DDA analysis")

class FailedSiteGeocoder:
    def __init__(self):
        """Initialize geocoder with PositionStack API"""
        # PositionStack API key from CLAUDE.md
        self.api_key = "41b80ed51d92978904592126d2bb8f7e"
        self.base_url = "http://api.positionstack.com/v1/forward"
        self.qct_dda_analyzer = None
        
        try:
            self.qct_dda_analyzer = ComprehensiveQCTDDAAnalyzer()
            print("✅ QCT/DDA analyzer initialized")
        except:
            print("⚠️  QCT/DDA analyzer not available")
        
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Geocode a single address using PositionStack API"""
        
        params = {
            'access_key': self.api_key,
            'query': address,
            'country': 'US',
            'limit': 1
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data') and len(data['data']) > 0:
                    result = data['data'][0]
                    return {
                        'latitude': result.get('latitude'),
                        'longitude': result.get('longitude'),
                        'formatted_address': result.get('label'),
                        'county': result.get('county'),
                        'administrative_area': result.get('administrative_area'),
                        'locality': result.get('locality'),
                        'confidence': result.get('confidence', 0)
                    }
                else:
                    print(f"  No results found for: {address}")
                    return None
            else:
                print(f"  API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"  Error geocoding {address}: {e}")
            return None
    
    def get_qct_dda_status(self, lat: float, lng: float) -> Dict:
        """Get QCT/DDA status using updated analyzer"""
        
        if not self.qct_dda_analyzer:
            return {
                'qct_status': 'Unknown',
                'dda_status': 'Unknown', 
                'basis_boost_eligible': False,
                'error': 'QCT/DDA analyzer not available'
            }
        
        try:
            result = self.qct_dda_analyzer.lookup_qct_status(lat, lng)
            return {
                'qct_status': result.get('qct_status', 'Unknown'),
                'dda_status': result.get('dda_status', 'Unknown'),
                'basis_boost_eligible': result.get('lihtc_eligible', False),
                'census_tract': result.get('census_tract', ''),
                'zip_code': result.get('zip_code', ''),
                'poverty_rate': result.get('poverty_rate', 0),
                'ami_limit': result.get('ami_limit', 0)
            }
        except Exception as e:
            return {
                'qct_status': 'Error',
                'dda_status': 'Error',
                'basis_boost_eligible': False,
                'error': str(e)
            }

    def process_tyler_site(self) -> Dict:
        """Specifically process the Tyler site"""
        
        tyler_address = "2505 Walton Rd, Tyler, TX 75701"
        
        print(f"🎯 Processing Tyler site: {tyler_address}")
        
        # Geocode
        geo_result = self.geocode_address(tyler_address)
        
        if not geo_result:
            return {
                'address': tyler_address,
                'status': 'geocoding_failed',
                'error': 'Could not geocode address'
            }
        
        print(f"  ✅ Coordinates: {geo_result['latitude']:.6f}, {geo_result['longitude']:.6f}")
        print(f"  📍 County: {geo_result.get('county', 'Unknown')}")
        
        # Get QCT/DDA status
        qct_dda = self.get_qct_dda_status(geo_result['latitude'], geo_result['longitude'])
        
        result = {
            'address': tyler_address,
            'latitude': geo_result['latitude'],
            'longitude': geo_result['longitude'],
            'county': geo_result.get('county'),
            'formatted_address': geo_result.get('formatted_address'),
            'confidence': geo_result.get('confidence'),
            'status': 'success'
        }
        
        result.update(qct_dda)
        
        print(f"  🏛️  QCT Status: {qct_dda.get('qct_status')}")
        print(f"  🏘️  DDA Status: {qct_dda.get('dda_status')}")
        print(f"  💰 Basis Boost Eligible: {qct_dda.get('basis_boost_eligible')}")
        
        return result

    def process_all_failed_sites(self, csv_file: str) -> pd.DataFrame:
        """Process all failed sites from CSV file"""
        
        print(f"📄 Loading failed sites from: {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            print(f"✅ Loaded {len(df)} sites")
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return None
        
        # Filter to just the geocoding failures (county = "NONE")
        geocoding_failures = df[df['county'] == 'NONE'].copy()
        print(f"🔍 Found {len(geocoding_failures)} sites with geocoding failures")
        
        results = []
        
        for idx, site in geocoding_failures.iterrows():
            address = site['site_address']
            original_idx = site['original_index']
            
            print(f"\n🏠 Processing site {len(results)+1}/{len(geocoding_failures)}: {address}")
            
            # Geocode
            geo_result = self.geocode_address(address)
            
            if not geo_result:
                results.append({
                    'original_index': original_idx,
                    'address': address,
                    'status': 'geocoding_failed',
                    'latitude': None,
                    'longitude': None,
                    'county': None
                })
                continue
            
            # Get QCT/DDA status
            qct_dda = self.get_qct_dda_status(geo_result['latitude'], geo_result['longitude'])
            
            result = {
                'original_index': original_idx,
                'address': address,
                'latitude': geo_result['latitude'],
                'longitude': geo_result['longitude'],
                'county': geo_result.get('county'),
                'formatted_address': geo_result.get('formatted_address'),
                'confidence': geo_result.get('confidence'),
                'status': 'success'
            }
            
            result.update(qct_dda)
            results.append(result)
            
            print(f"  ✅ {geo_result.get('county')} County | QCT: {qct_dda.get('qct_status')} | DDA: {qct_dda.get('dda_status')}")
            
            # Rate limiting
            time.sleep(1)
        
        return pd.DataFrame(results)

def main():
    """Main execution"""
    
    print("🚀 STARTING FAILED SITES GEOCODING")
    print("=" * 60)
    
    geocoder = FailedSiteGeocoder()
    
    # Test with Tyler site first
    print("\n🎯 TYLER SITE TEST")
    tyler_result = geocoder.process_tyler_site()
    
    if tyler_result['status'] == 'success':
        print(f"✅ Tyler site successfully processed!")
        
        # Save Tyler result
        tyler_df = pd.DataFrame([tyler_result])
        tyler_output = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis/outputs/tyler_geocoded_result.csv"
        tyler_df.to_csv(tyler_output, index=False)
        print(f"💾 Tyler results saved to: tyler_geocoded_result.csv")
        
    else:
        print(f"❌ Tyler site geocoding failed: {tyler_result.get('error')}")
        return
    
    # Process all failed sites
    print(f"\n📋 PROCESSING ALL FAILED SITES")
    
    csv_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis/outputs/failed_sites_for_geocoding.csv"
    
    results_df = geocoder.process_all_failed_sites(csv_file)
    
    if results_df is not None:
        # Save results
        output_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis/outputs/geocoded_sites_results.csv"
        results_df.to_csv(output_file, index=False)
        
        # Summary
        total_sites = len(results_df)
        successful = len(results_df[results_df['status'] == 'success'])
        
        print(f"\n" + "="*60)
        print(f"📊 GEOCODING SUMMARY")
        print(f"  Total sites processed: {total_sites}")
        print(f"  Successfully geocoded: {successful}")
        print(f"  Success rate: {(successful/total_sites)*100:.1f}%")
        
        # QCT/DDA summary
        if successful > 0:
            success_df = results_df[results_df['status'] == 'success']
            qct_eligible = len(success_df[success_df['qct_status'] == 'QCT'])
            dda_eligible = len(success_df[success_df['dda_status'] == 'DDA'])
            basis_boost = len(success_df[success_df['basis_boost_eligible'] == True])
            
            print(f"  QCT sites: {qct_eligible}")
            print(f"  DDA sites: {dda_eligible}") 
            print(f"  Basis boost eligible: {basis_boost}")
        
        print(f"💾 Results saved to: geocoded_sites_results.csv")
        print(f"🚀 Ready for re-scoring!")
        
    else:
        print(f"❌ Failed to process sites")

if __name__ == "__main__":
    main()
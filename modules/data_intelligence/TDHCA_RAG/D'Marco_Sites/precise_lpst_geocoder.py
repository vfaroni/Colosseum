#!/usr/bin/env python3

import pandas as pd
import numpy as np
from geopy.distance import geodesic
import json
from pathlib import Path
from datetime import datetime
import requests
import time
import csv

class PreciseLPSTGeocoder:
    """
    Precise geocoding and distance analysis for active LPST sites
    Creates database file with exact coordinates and distances to D'Marco sites
    """
    
    def __init__(self):
        self.environmental_data_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/Environmental/TX_Commission_on_Env/"
        self.lpst_file = "Texas_Commission_on_Environmental_Quality_-_Leaking_Petroleum_Storage_Tank__LPST__Sites_20250702.csv"
        self.output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/"
        
        # PositionStack API (paid account: 100k requests/month)
        self.positionstack_api_key = "b8f4a4c8b4c8e8a3d2f1b9e8a7c6d5e4"
        
        # Environmental risk distance thresholds (in miles)
        self.risk_thresholds = {
            'IMMEDIATE': 0.095,    # 500 feet
            'CRITICAL': 0.25,      # 1/4 mile - petroleum contamination
            'HIGH': 0.5,           # 1/2 mile - enforcement actions
            'MEDIUM': 1.0          # 1 mile - superfund/major sites
        }
        
        # Target cities with known high LPST exposure
        self.target_cities = ['HOUSTON', 'DALLAS', 'SAN ANTONIO', 'TYLER', 'HUTCHINS']
        
        # Geocoding cache and rate limiting
        self.geocode_cache = {}
        self.geocode_failures = []
        self.request_count = 0
        self.max_requests = 5000  # Reasonable limit for paid account
    
    def load_dmarco_sites(self):
        """Load all D'Marco priority sites with exact coordinates"""
        sites_file = "/Users/williamrice/priority_sites_data.json"
        
        with open(sites_file, 'r') as f:
            sites_data = json.load(f)
        
        processed_sites = []
        
        for i, site in enumerate(sites_data):
            # Parse corner coordinates
            corners = {}
            for corner_name in ['SW', 'SE', 'NE', 'NW']:
                lat, lon = self.parse_coordinates(site.get(corner_name))
                if lat and lon:
                    corners[f'corner_{corner_name.lower()}'] = {'lat': lat, 'lon': lon}
            
            if len(corners) == 4:
                # Extract city from address
                address = site.get('Address', '')
                city = self.extract_city_from_address(address)
                
                processed_site = {
                    'site_id': f"dmarco_site_{i+1:02d}",
                    'address': address,
                    'city': city,
                    'size_acres': site.get('Size (Acres)', 0),
                    'corners': corners,
                    'center': self.calculate_center_point(corners)
                }
                processed_sites.append(processed_site)
        
        print(f"✅ Loaded {len(processed_sites)} D'Marco sites with precise coordinates")
        return processed_sites
    
    def parse_coordinates(self, coord_string):
        """Parse coordinate string like '32.319481, -95.330743' into lat, lon"""
        try:
            if isinstance(coord_string, str) and ',' in coord_string:
                lat_str, lon_str = coord_string.split(',')
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())
                return lat, lon
            return None, None
        except:
            return None, None
    
    def extract_city_from_address(self, address):
        """Extract city name from address string"""
        try:
            address_upper = address.upper()
            known_cities = {
                'TYLER': 'TYLER',
                'SAN ANTONIO': 'SAN ANTONIO', 
                'DALLAS': 'DALLAS',
                'SAGINAW': 'SAGINAW',
                'AUBREY': 'AUBREY',
                'HUTCHINS': 'HUTCHINS',
                'HOUSTON': 'HOUSTON',
                'KERRVILLE': 'KERRVILLE'
            }
            
            for city_key, city_name in known_cities.items():
                if city_key in address_upper:
                    return city_name
            
            return 'OTHER'
        except:
            return 'OTHER'
    
    def calculate_center_point(self, corners):
        """Calculate center point from 4 corners"""
        lats = [corner['lat'] for corner in corners.values()]
        lons = [corner['lon'] for corner in corners.values()]
        return {
            'lat': sum(lats) / len(lats),
            'lon': sum(lons) / len(lons)
        }
    
    def load_active_lpst_sites_in_target_cities(self):
        """Load only active LPST sites in cities where D'Marco has properties"""
        lpst_file_path = self.environmental_data_path + self.lpst_file
        
        print(f"📊 Loading active LPST sites from target cities...")
        lpst_df = pd.read_csv(lpst_file_path)
        
        # Filter for target cities and active sites (no closure date)
        target_city_filter = False
        for city in self.target_cities:
            target_city_filter |= lpst_df['City'].str.upper().str.contains(city, na=False)
        
        active_filter = lpst_df['Closure Date'].isna()
        
        active_lpst = lpst_df[target_city_filter & active_filter].copy()
        
        print(f"   🎯 Found {len(active_lpst)} active LPST sites in target cities")
        
        # Show breakdown by city
        for city in self.target_cities:
            city_count = len(active_lpst[active_lpst['City'].str.upper().str.contains(city, na=False)])
            if city_count > 0:
                print(f"      {city}: {city_count} active sites")
        
        return active_lpst
    
    def geocode_address_positionstack(self, address, city, state='TX'):
        """Geocode address using PositionStack API with caching and rate limiting"""
        
        # Check rate limit
        if self.request_count >= self.max_requests:
            print(f"   ⚠️ Reached API rate limit ({self.max_requests} requests)")
            return None
        
        full_address = f"{address}, {city}, {state}".strip()
        
        # Check cache first
        if full_address in self.geocode_cache:
            return self.geocode_cache[full_address]
        
        # Clean up address for better geocoding
        clean_address = self.clean_address_for_geocoding(full_address)
        
        try:
            url = "http://api.positionstack.com/v1/forward"
            params = {
                'access_key': self.positionstack_api_key,
                'query': clean_address,
                'limit': 1,
                'country': 'US',
                'region': 'TX'
            }
            
            response = requests.get(url, params=params, timeout=15)
            self.request_count += 1
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    result = data['data'][0]
                    lat = float(result['latitude'])
                    lon = float(result['longitude'])
                    confidence = result.get('confidence', 0)
                    
                    geocode_result = {
                        'lat': lat, 
                        'lon': lon, 
                        'confidence': confidence,
                        'source': 'PositionStack',
                        'success': True
                    }
                    
                    # Cache successful result
                    self.geocode_cache[full_address] = geocode_result
                    time.sleep(0.2)  # Rate limiting - 5 requests per second max
                    
                    return geocode_result
                
                else:
                    print(f"      ❌ No results for: {clean_address}")
            
            else:
                print(f"      ❌ API error {response.status_code}: {response.text}")
        
        except Exception as e:
            print(f"      ❌ Geocoding failed: {e}")
        
        # Record failure
        self.geocode_failures.append(full_address)
        return None
    
    def clean_address_for_geocoding(self, address):
        """Clean address string for better geocoding accuracy"""
        # Remove common problematic elements
        clean_address = address.upper()
        
        # Remove building/suite numbers that confuse geocoding
        clean_address = clean_address.replace('BLDG ', '').replace('BUILDING ', '')
        clean_address = clean_address.replace('STE ', '').replace('SUITE ', '')
        
        # Fix common abbreviations
        clean_address = clean_address.replace(' ST,', ' STREET,')
        clean_address = clean_address.replace(' AVE,', ' AVENUE,')
        clean_address = clean_address.replace(' RD,', ' ROAD,')
        clean_address = clean_address.replace(' DR,', ' DRIVE,')
        clean_address = clean_address.replace(' LN,', ' LANE,')
        clean_address = clean_address.replace(' BLVD,', ' BOULEVARD,')
        clean_address = clean_address.replace(' HWY,', ' HIGHWAY,')
        clean_address = clean_address.replace(' FWY,', ' FREEWAY,')
        
        # Remove "NAN" addresses
        if 'NAN' in clean_address:
            # Try to extract just city, state for general area geocoding
            parts = clean_address.split(',')
            if len(parts) >= 2:
                return f"{parts[-2].strip()}, {parts[-1].strip()}"
        
        return clean_address
    
    def calculate_precise_distances(self, dmarco_sites, geocoded_lpst_sites):
        """Calculate precise distances from each LPST site to each D'Marco property"""
        
        print(f"\n📏 CALCULATING PRECISE DISTANCES")
        print("=" * 50)
        
        distance_results = []
        
        for lpst_site in geocoded_lpst_sites:
            lpst_lat = lpst_site['coordinates']['lat']
            lpst_lon = lpst_site['coordinates']['lon']
            
            lpst_distances = {
                'lpst_id': lpst_site['lpst_id'],
                'site_name': lpst_site['site_name'],
                'address': lpst_site['address'],
                'city': lpst_site['city'],
                'coordinates': lpst_site['coordinates'],
                'reported_date': lpst_site['reported_date'],
                'tceq_region': lpst_site['tceq_region'],
                'distances_to_dmarco_sites': {}
            }
            
            # Calculate distance to each D'Marco site
            for dmarco_site in dmarco_sites:
                site_id = dmarco_site['site_id']
                
                # Calculate distance from LPST to each corner (most conservative)
                corner_distances = []
                for corner_name, corner_coords in dmarco_site['corners'].items():
                    distance = geodesic(
                        (corner_coords['lat'], corner_coords['lon']),
                        (lpst_lat, lpst_lon)
                    ).miles
                    corner_distances.append(distance)
                
                # Use minimum distance (closest approach)
                min_distance = min(corner_distances) if corner_distances else float('inf')
                
                # Also calculate distance to center point
                center_distance = geodesic(
                    (dmarco_site['center']['lat'], dmarco_site['center']['lon']),
                    (lpst_lat, lpst_lon)
                ).miles
                
                lpst_distances['distances_to_dmarco_sites'][site_id] = {
                    'min_distance_miles': round(min_distance, 4),
                    'center_distance_miles': round(center_distance, 4),
                    'dmarco_address': dmarco_site['address'],
                    'within_500ft': min_distance <= self.risk_thresholds['IMMEDIATE'],
                    'within_quarter_mile': min_distance <= self.risk_thresholds['CRITICAL'],
                    'within_half_mile': min_distance <= self.risk_thresholds['HIGH'],
                    'within_one_mile': min_distance <= self.risk_thresholds['MEDIUM']
                }
            
            distance_results.append(lpst_distances)
        
        return distance_results
    
    def create_lpst_database_file(self, distance_results):
        """Create comprehensive database file with all LPST sites and distances"""
        
        output_file = self.output_dir + "D_Marco_LPST_Sites_Database.csv"
        
        print(f"\n📁 Creating comprehensive LPST database file...")
        
        # Prepare CSV data
        csv_data = []
        headers = [
            'LPST_ID', 'Site_Name', 'Address', 'City', 'Reported_Date', 'TCEQ_Region',
            'Latitude', 'Longitude', 'Geocoding_Confidence'
        ]
        
        # Add D'Marco site distance columns
        dmarco_site_ids = []
        for result in distance_results:
            if result['distances_to_dmarco_sites']:
                dmarco_site_ids = list(result['distances_to_dmarco_sites'].keys())
                break
        
        for site_id in dmarco_site_ids:
            headers.extend([
                f'{site_id}_Min_Distance_Miles',
                f'{site_id}_Center_Distance_Miles', 
                f'{site_id}_Within_500ft',
                f'{site_id}_Within_Quarter_Mile',
                f'{site_id}_Within_Half_Mile',
                f'{site_id}_Within_One_Mile'
            ])
        
        # Populate data rows
        for result in distance_results:
            row = [
                result['lpst_id'],
                result['site_name'],
                result['address'],
                result['city'],
                result['reported_date'],
                result['tceq_region'],
                result['coordinates']['lat'],
                result['coordinates']['lon'],
                result['coordinates'].get('confidence', 'N/A')
            ]
            
            # Add distance data for each D'Marco site
            for site_id in dmarco_site_ids:
                site_distances = result['distances_to_dmarco_sites'].get(site_id, {})
                row.extend([
                    site_distances.get('min_distance_miles', 'N/A'),
                    site_distances.get('center_distance_miles', 'N/A'),
                    'YES' if site_distances.get('within_500ft', False) else 'NO',
                    'YES' if site_distances.get('within_quarter_mile', False) else 'NO',
                    'YES' if site_distances.get('within_half_mile', False) else 'NO',
                    'YES' if site_distances.get('within_one_mile', False) else 'NO'
                ])
            
            csv_data.append(row)
        
        # Write CSV file
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(csv_data)
        
        print(f"   ✅ Database file created: {output_file}")
        print(f"   📊 {len(csv_data)} LPST sites with precise distances to {len(dmarco_site_ids)} D'Marco sites")
        
        return output_file
    
    def analyze_proximity_risks(self, distance_results):
        """Analyze proximity risks for each D'Marco site"""
        
        print(f"\n🎯 PROXIMITY RISK ANALYSIS")
        print("=" * 40)
        
        # Aggregate risks by D'Marco site
        site_risks = {}
        
        for lpst_result in distance_results:
            for site_id, distances in lpst_result['distances_to_dmarco_sites'].items():
                if site_id not in site_risks:
                    site_risks[site_id] = {
                        'immediate_risk_500ft': [],
                        'critical_risk_quarter_mile': [],
                        'high_risk_half_mile': [],
                        'medium_risk_one_mile': [],
                        'dmarco_address': distances['dmarco_address']
                    }
                
                # Categorize by risk level
                min_dist = distances['min_distance_miles']
                lpst_info = {
                    'name': lpst_result['site_name'],
                    'address': lpst_result['address'],
                    'distance': min_dist,
                    'reported_date': lpst_result['reported_date']
                }
                
                if distances['within_500ft']:
                    site_risks[site_id]['immediate_risk_500ft'].append(lpst_info)
                elif distances['within_quarter_mile']:
                    site_risks[site_id]['critical_risk_quarter_mile'].append(lpst_info)
                elif distances['within_half_mile']:
                    site_risks[site_id]['high_risk_half_mile'].append(lpst_info)
                elif distances['within_one_mile']:
                    site_risks[site_id]['medium_risk_one_mile'].append(lpst_info)
        
        # Display risk analysis
        for site_id, risks in site_risks.items():
            print(f"\n🏗️ {site_id.upper()}: {risks['dmarco_address']}")
            
            immediate = len(risks['immediate_risk_500ft'])
            critical = len(risks['critical_risk_quarter_mile'])
            high = len(risks['high_risk_half_mile'])
            medium = len(risks['medium_risk_one_mile'])
            
            total_within_mile = immediate + critical + high + medium
            
            if immediate > 0:
                print(f"   🚨 IMMEDIATE RISK: {immediate} LPST sites within 500 feet")
                for lpst in risks['immediate_risk_500ft'][:3]:  # Show top 3
                    print(f"      • {lpst['name']} - {lpst['distance']:.3f} miles ({lpst['distance']*5280:.0f} feet)")
            
            if critical > 0:
                print(f"   🔴 CRITICAL RISK: {critical} LPST sites within 1/4 mile")
                for lpst in risks['critical_risk_quarter_mile'][:3]:
                    print(f"      • {lpst['name']} - {lpst['distance']:.3f} miles")
            
            if high > 0:
                print(f"   🟠 HIGH RISK: {high} LPST sites within 1/2 mile")
            
            if medium > 0:
                print(f"   🟡 MEDIUM RISK: {medium} LPST sites within 1 mile")
            
            if total_within_mile == 0:
                print(f"   ✅ LOW RISK: No active LPST sites within 1 mile")
            
            # Risk level determination
            overall_risk = 'LOW'
            if immediate > 0:
                overall_risk = 'IMMEDIATE'
            elif critical >= 3:
                overall_risk = 'CRITICAL'
            elif critical >= 1 or high >= 5:
                overall_risk = 'HIGH'
            elif high >= 1 or medium >= 3:
                overall_risk = 'MEDIUM'
            
            print(f"   📊 OVERALL RISK LEVEL: {overall_risk}")
        
        return site_risks
    
    def run_precise_lpst_analysis(self):
        """Execute complete precise LPST geocoding and distance analysis"""
        
        print("🎯 PRECISE LPST GEOCODING & DISTANCE ANALYSIS")
        print("=" * 55)
        
        # API key is configured for paid account
        
        # Load D'Marco sites
        dmarco_sites = self.load_dmarco_sites()
        
        # Load active LPST sites
        active_lpst_df = self.load_active_lpst_sites_in_target_cities()
        
        if len(active_lpst_df) == 0:
            print("❌ No active LPST sites found in target cities")
            return None
        
        # Geocode LPST sites
        print(f"\n🌐 GEOCODING {len(active_lpst_df)} ACTIVE LPST SITES")
        print("=" * 50)
        
        geocoded_lpst_sites = []
        
        for idx, row in active_lpst_df.iterrows():
            try:
                lpst_id = str(row.get('LPST ID', 'Unknown'))
                site_name = str(row.get('Site Name', 'Unknown'))
                address = str(row.get('Site Address', ''))
                city = str(row.get('City', ''))
                
                print(f"   🔍 Geocoding ({len(geocoded_lpst_sites)+1}/{len(active_lpst_df)}): {site_name}")
                
                # Geocode the address
                geocode_result = self.geocode_address_positionstack(address, city)
                
                if geocode_result and geocode_result.get('success', False):
                    # Create comprehensive site record
                    geocoded_site = {
                        'lpst_id': lpst_id,
                        'site_name': site_name,
                        'address': address,
                        'city': city,
                        'county': str(row.get('County', '')),
                        'zip_code': str(row.get('Zip Code', '')),
                        'reported_date': str(row.get('Reported Date', 'N/A')),
                        'tceq_region': str(row.get('TCEQ Region', '')),
                        'coordinates': {
                            'lat': geocode_result['lat'],
                            'lon': geocode_result['lon'],
                            'confidence': geocode_result['confidence'],
                            'source': geocode_result['source']
                        }
                    }
                    
                    geocoded_lpst_sites.append(geocoded_site)
                    print(f"      ✅ Success: ({geocode_result['lat']:.4f}, {geocode_result['lon']:.4f}) confidence: {geocode_result['confidence']:.2f}")
                
                else:
                    print(f"      ❌ Failed to geocode")
                    
                # Progress update every 50 sites
                if (len(geocoded_lpst_sites) + len(self.geocode_failures)) % 50 == 0:
                    success_rate = len(geocoded_lpst_sites) / (len(geocoded_lpst_sites) + len(self.geocode_failures)) * 100
                    print(f"   📊 Progress: {len(geocoded_lpst_sites)} geocoded, {success_rate:.1f}% success rate")
                
            except Exception as e:
                print(f"      ❌ Error processing row: {e}")
                continue
        
        print(f"\n📊 GEOCODING COMPLETE:")
        print(f"   ✅ Successfully geocoded: {len(geocoded_lpst_sites)} sites")
        print(f"   ❌ Failed to geocode: {len(self.geocode_failures)} sites")  
        print(f"   📡 API requests used: {self.request_count}")
        
        if len(geocoded_lpst_sites) == 0:
            print("❌ No LPST sites successfully geocoded")
            return None
        
        # Calculate precise distances
        distance_results = self.calculate_precise_distances(dmarco_sites, geocoded_lpst_sites)
        
        # Create database file
        database_file = self.create_lpst_database_file(distance_results)
        
        # Analyze proximity risks
        site_risks = self.analyze_proximity_risks(distance_results)
        
        # Save comprehensive results
        results_file = self.output_dir + "Precise_LPST_Analysis_Results.json"
        
        final_output = {
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'Precise LPST Geocoding & Distance Analysis',
            'api_requests_used': self.request_count,
            'geocoding_success_rate': f"{len(geocoded_lpst_sites)/len(active_lpst_df)*100:.1f}%",
            'dmarco_sites_analyzed': len(dmarco_sites),
            'active_lpst_sites_found': len(active_lpst_df),
            'lpst_sites_geocoded': len(geocoded_lpst_sites),
            'database_file_created': database_file,
            'risk_thresholds_miles': self.risk_thresholds,
            'site_risk_summary': {
                site_id: {
                    'immediate_risk_count': len(risks['immediate_risk_500ft']),
                    'critical_risk_count': len(risks['critical_risk_quarter_mile']),
                    'high_risk_count': len(risks['high_risk_half_mile']),
                    'medium_risk_count': len(risks['medium_risk_one_mile'])
                }
                for site_id, risks in site_risks.items()
            },
            'geocoding_failures': self.geocode_failures[:50]  # Sample of failures
        }
        
        with open(results_file, 'w') as f:
            json.dump(final_output, f, indent=2)
        
        print(f"\n📁 ANALYSIS COMPLETE:")
        print(f"   📊 Database file: {database_file}")
        print(f"   📄 Results file: {results_file}")
        
        return final_output

def main():
    """Execute precise LPST geocoding and analysis"""
    
    print("🎯 PRECISE LPST GEOCODING FOR D'MARCO ENVIRONMENTAL ANALYSIS")
    print("=" * 65)
    
    geocoder = PreciseLPSTGeocoder()
    results = geocoder.run_precise_lpst_analysis()
    
    if results:
        print("\n🎉 PRECISE LPST ANALYSIS COMPLETE!")
        print("✅ Active LPST sites geocoded with PositionStack API")
        print("✅ Exact distances calculated (500ft, 1/4 mile, 1/2 mile, 1 mile)")
        print("✅ Comprehensive database file created")
        print("✅ Risk analysis completed for all D'Marco sites")
        print("\n💡 Next Steps:")
        print("   1. Review the database file for sites within critical distances")
        print("   2. Commission Phase I ESA for sites with IMMEDIATE or CRITICAL risk")
        print("   3. Use precise distance data for environmental insurance quotes")
    
    else:
        print("\n❌ Analysis failed - check API key and try again")

if __name__ == "__main__":
    main()
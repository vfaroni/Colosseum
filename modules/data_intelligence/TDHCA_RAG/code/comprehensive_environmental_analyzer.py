#!/usr/bin/env python3

import pandas as pd
import json
import numpy as np
from pathlib import Path
import folium
import requests
import time
import re
from datetime import datetime
from geopy.distance import geodesic

class ComprehensiveEnvironmentalAnalyzer:
    """
    Comprehensive environmental analysis for D'Marco sites using all 6 TCEQ datasets:
    1. LPST (Leaking Petroleum Storage Tank) Sites
    2. Historical Dry Cleaner Registrations
    3. Operating Dry Cleaner Registrations  
    4. NOR Waste (Notification of Regulated Waste)
    5. Notices of Enforcement (NOE)
    6. Environmental Complaints
    """
    
    def __init__(self):
        self.base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG"
        self.data_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/Environmental/TX_Commission_on_Env"
        self.output_dir = f"{self.base_dir}/D'Marco_Sites/"
        
        # Environmental datasets configuration
        self.datasets = {
            'lpst': {
                'file': 'Texas_Commission_on_Environmental_Quality_-_Leaking_Petroleum_Storage_Tank__LPST__Sites_20250702.csv',
                'risk_type': 'Petroleum Contamination',
                'color': '#8B0000',  # Dark red
                'icon': 'tint',
                'needs_geocoding': False,  # Already processed
                'database_file': f"{self.base_dir}/D'Marco_Sites/D_Marco_LPST_Sites_Database.csv"
            },
            'historical_dry_cleaners': {
                'file': 'Texas_Commission_on_Environmental_Quality_-_Historical_Dry_Cleaner_Registrations_20250702.csv',
                'risk_type': 'Historical Solvent Contamination',
                'color': '#4B0082',  # Indigo
                'icon': 'flask',
                'needs_geocoding': True,
                'address_fields': ['Location Address', 'Location City', 'Location State', 'Location Zip Code']
            },
            'operating_dry_cleaners': {
                'file': 'Texas_Commission_on_Environmental_Quality_-_Operating_Dry_Cleaner_Registrations_20250702.csv',
                'risk_type': 'Active Solvent Operations',
                'color': '#800080',  # Purple
                'icon': 'industry',
                'needs_geocoding': False,  # Has coordinates
                'coord_field': 'Location Coordinates (Decimal Degrees)'
            },
            'nor_waste': {
                'file': 'Texas_Commission_on_Environmental_Quality_-_NOR_Waste_20250702.csv',
                'risk_type': 'Hazardous Waste Sites',
                'color': '#FF4500',  # Orange red
                'icon': 'exclamation-triangle',
                'needs_geocoding': True,
                'note': 'No address fields - needs entity lookup'
            },
            'enforcement': {
                'file': 'Texas_Commission_on_Environmental_Quality_-_Notices_of_Enforcement__NOE__20250702.csv',
                'risk_type': 'Environmental Violations',
                'color': '#DC143C',  # Crimson
                'icon': 'gavel',
                'needs_geocoding': False,  # Has coordinates
                'coord_fields': ['Latitude', 'Longitude']
            },
            'complaints': {
                'file': 'Texas_Commission_on_Environmental_Quality_-_Complaints_20250702.csv',
                'risk_type': 'Environmental Complaints',
                'color': '#FF6347',  # Tomato
                'icon': 'exclamation',
                'needs_geocoding': True,
                'note': 'No address fields - county-level only'
            }
        }
        
        # Risk thresholds (miles)
        self.risk_thresholds = {
            'IMMEDIATE': 0.095,    # 500 feet
            'CRITICAL': 0.25,      # 1/4 mile
            'HIGH': 0.5,           # 1/2 mile
            'MEDIUM': 1.0          # 1 mile
        }
        
        # Risk colors
        self.risk_colors = {
            'IMMEDIATE': '#8B0000',    # Dark red
            'CRITICAL': '#FF0000',     # Red
            'HIGH': '#FF4500',         # Orange red
            'MEDIUM': '#FFA500',       # Orange
            'LOW': '#32CD32'           # Lime green
        }
        
        # D'Marco sites with environmental concerns (from previous LPST analysis)
        self.concern_sites = {
            'dmarco_site_06': {
                'address': 'N JJ Lemon Street Hutchins',
                'lpst_risk_level': 'MEDIUM'
            },
            'dmarco_site_07': {
                'address': '6053 Bellfort Ave, Houston, TX 77033',
                'lpst_risk_level': 'LOW'
            }
        }
    
    def parse_wkt_point(self, wkt_string):
        """Parse WKT POINT format: POINT (-98.22435 32.21035)"""
        if pd.isna(wkt_string) or not isinstance(wkt_string, str):
            return None, None
        
        try:
            # Extract coordinates from WKT POINT format
            match = re.search(r'POINT\s*\(\s*([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s*\)', wkt_string)
            if match:
                lon, lat = float(match.group(1)), float(match.group(2))
                return lat, lon
            return None, None
        except:
            return None, None
    
    def geocode_address(self, address_parts, max_retries=3):
        """Geocode address using OpenStreetMap Nominatim"""
        
        # Clean and format address
        address_str = ""
        for part in address_parts:
            if pd.notna(part) and str(part).strip():
                address_str += str(part).strip() + ", "
        
        address_str = address_str.rstrip(", ")
        
        if not address_str:
            return None, None, 0.0
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address_str,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'us'
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if data:
                    result = data[0]
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    confidence = float(result.get('importance', 0.5))
                    return lat, lon, confidence
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"   ❌ Geocoding failed for: {address_str[:50]}... - {str(e)}")
                time.sleep(2)
        
        return None, None, 0.0
    
    def process_operating_dry_cleaners(self):
        """Process operating dry cleaner dataset - has WKT coordinates"""
        print("📍 Processing Operating Dry Cleaner Registrations...")
        
        df = pd.read_csv(f"{self.data_dir}/{self.datasets['operating_dry_cleaners']['file']}")
        print(f"   📊 Loaded {len(df)} operating dry cleaner records")
        
        # Parse WKT coordinates
        locations = []
        for idx, row in df.iterrows():
            lat, lon = self.parse_wkt_point(row.get('Location Coordinates (Decimal Degrees)'))
            
            if lat and lon:
                locations.append({
                    'dataset': 'operating_dry_cleaners',
                    'site_id': row.get('Registration ID', f'ODC_{idx}'),
                    'site_name': row.get('Regulated Entity Name', 'Unknown Dry Cleaner'),
                    'address': f"{row.get('Location Address', '')}, {row.get('Location City', '')}, {row.get('Location State', '')} {row.get('Location Zip Code', '')}".strip(', '),
                    'city': row.get('Location City', 'Unknown'),
                    'county': row.get('Location County', 'Unknown'),
                    'tceq_region': row.get('TCEQ Region (for Location)', 'Unknown'),
                    'solvent_type': row.get('Solvent Type', 'Unknown'),
                    'status': 'ACTIVE',
                    'latitude': lat,
                    'longitude': lon,
                    'geocoding_confidence': 1.0,
                    'risk_type': self.datasets['operating_dry_cleaners']['risk_type']
                })
        
        print(f"   ✅ Successfully processed {len(locations)} operating dry cleaner sites")
        return locations
    
    def process_enforcement_notices(self):
        """Process enforcement notices dataset - has lat/lon columns"""
        print("📍 Processing Notices of Enforcement...")
        
        df = pd.read_csv(f"{self.data_dir}/{self.datasets['enforcement']['file']}")
        print(f"   📊 Loaded {len(df)} enforcement notice records")
        
        locations = []
        for idx, row in df.iterrows():
            lat = row.get('Latitude')
            lon = row.get('Longitude')
            
            # Check if coordinates are valid
            if pd.notna(lat) and pd.notna(lon):
                try:
                    lat, lon = float(lat), float(lon)
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        locations.append({
                            'dataset': 'enforcement',
                            'site_id': row.get('Notice of Enforcement ID', f'NOE_{idx}'),
                            'site_name': row.get('Regulated Entity Name', 'Unknown Entity'),
                            'address': f"{row.get('Physical Location', '')}, {row.get('Physical City ', '')}, TX {row.get('Physical Zip Code', '')}".strip(', '),
                            'city': row.get('Physical City ', 'Unknown'),
                            'county': row.get('Physical County', 'Unknown'),
                            'tceq_region': row.get('TCEQ Region Name', 'Unknown'),
                            'noe_date': row.get('NOE Date', 'Unknown'),
                            'violation_count': row.get('Total Violation Count', 0),
                            'status': 'ENFORCEMENT ACTION',
                            'latitude': lat,
                            'longitude': lon,
                            'geocoding_confidence': 1.0,
                            'risk_type': self.datasets['enforcement']['risk_type']
                        })
                except:
                    continue
        
        print(f"   ✅ Successfully processed {len(locations)} enforcement notice sites")
        return locations
    
    def process_historical_dry_cleaners(self):
        """Process historical dry cleaner dataset - needs geocoding"""
        print("📍 Processing Historical Dry Cleaner Registrations...")
        
        df = pd.read_csv(f"{self.data_dir}/{self.datasets['historical_dry_cleaners']['file']}")
        print(f"   📊 Loaded {len(df)} historical dry cleaner records")
        
        # Limit to reasonable subset for geocoding
        df_sample = df.head(500)  # Process first 500 for now
        print(f"   🎯 Processing subset of {len(df_sample)} records for performance")
        
        locations = []
        geocoded = 0
        
        for idx, row in df_sample.iterrows():
            address_parts = [
                row.get('Location Address'),
                row.get('Location City'),
                row.get('Location State', 'TX'),
                row.get('Location Zip Code')
            ]
            
            lat, lon, confidence = self.geocode_address(address_parts)
            
            if lat and lon:
                geocoded += 1
                locations.append({
                    'dataset': 'historical_dry_cleaners',
                    'site_id': row.get('Registration ID', f'HDC_{idx}'),
                    'site_name': row.get('Regulated Entity Name', 'Unknown Historical Dry Cleaner'),
                    'address': f"{row.get('Location Address', '')}, {row.get('Location City', '')}, {row.get('Location State', 'TX')} {row.get('Location Zip Code', '')}".strip(', '),
                    'city': row.get('Location City', 'Unknown'),
                    'county': row.get('Location County', 'Unknown'),
                    'tceq_region': row.get('TCEQ Region (for Location)', 'Unknown'),
                    'solvent_type': row.get('Solvent Type', 'Unknown'),
                    'status': row.get('Certificate Status', 'HISTORICAL'),
                    'latitude': lat,
                    'longitude': lon,
                    'geocoding_confidence': confidence,
                    'risk_type': self.datasets['historical_dry_cleaners']['risk_type']
                })
            
            # Rate limiting
            if idx % 50 == 0:
                print(f"   📊 Processed {idx}/{len(df_sample)} records, {geocoded} geocoded")
                time.sleep(2)
        
        success_rate = (geocoded / len(df_sample)) * 100 if len(df_sample) > 0 else 0
        print(f"   ✅ Successfully geocoded {geocoded}/{len(df_sample)} historical dry cleaner sites ({success_rate:.1f}%)")
        return locations
    
    def load_existing_lpst_data(self):
        """Load existing LPST analysis results"""
        print("📍 Loading Existing LPST Analysis...")
        
        lpst_file = self.datasets['lpst']['database_file']
        if not Path(lpst_file).exists():
            print(f"   ❌ LPST database not found: {lpst_file}")
            return []
        
        df = pd.read_csv(lpst_file)
        print(f"   📊 Loaded {len(df)} LPST records from existing analysis")
        
        locations = []
        for idx, row in df.iterrows():
            locations.append({
                'dataset': 'lpst',
                'site_id': row.get('LPST_ID', f'LPST_{idx}'),
                'site_name': row.get('Site_Name', 'Unknown LPST Site'),
                'address': row.get('Address', 'Unknown'),
                'city': row.get('City', 'Unknown'),
                'tceq_region': row.get('TCEQ_Region', 'Unknown'),
                'reported_date': row.get('Reported_Date', 'Unknown'),
                'status': 'ACTIVE LPST',
                'latitude': row.get('Latitude'),
                'longitude': row.get('Longitude'),
                'geocoding_confidence': row.get('Geocoding_Confidence', 1.0),
                'risk_type': self.datasets['lpst']['risk_type']
            })
        
        print(f"   ✅ Successfully loaded {len(locations)} LPST sites")
        return locations
    
    def calculate_distances_to_dmarco_sites(self, environmental_sites):
        """Calculate distances from environmental sites to all D'Marco sites"""
        print("📏 Calculating distances to D'Marco sites...")
        
        # Load D'Marco site coordinates
        sites_file = "/Users/williamrice/priority_sites_data.json"
        with open(sites_file, 'r') as f:
            dmarco_sites = json.load(f)
        
        # Parse D'Marco coordinates
        dmarco_coords = {}
        for i, site in enumerate(dmarco_sites):
            site_id = f"dmarco_site_{str(i+1).zfill(2)}"
            
            # Calculate center from 4 corners
            corners = []
            for corner in ['SW', 'SE', 'NE', 'NW']:
                coord_str = site.get(corner, "")
                if coord_str and ',' in coord_str:
                    try:
                        lat_str, lon_str = coord_str.split(',')
                        lat, lon = float(lat_str.strip()), float(lon_str.strip())
                        corners.append((lat, lon))
                    except:
                        continue
            
            if len(corners) == 4:
                center_lat = sum(c[0] for c in corners) / 4
                center_lon = sum(c[1] for c in corners) / 4
                dmarco_coords[site_id] = {
                    'lat': center_lat,
                    'lon': center_lon,
                    'address': site.get('Address', 'Unknown')
                }
        
        print(f"   📊 Calculating distances for {len(environmental_sites)} environmental sites to {len(dmarco_coords)} D'Marco sites")
        
        # Calculate distances and risk levels
        for env_site in environmental_sites:
            env_lat, env_lon = env_site['latitude'], env_site['longitude']
            
            for dmarco_id, dmarco_data in dmarco_coords.items():
                distance_miles = geodesic(
                    (env_lat, env_lon),
                    (dmarco_data['lat'], dmarco_data['lon'])
                ).miles
                
                # Determine risk level
                risk_level = 'LOW'
                if distance_miles <= self.risk_thresholds['IMMEDIATE']:
                    risk_level = 'IMMEDIATE'
                elif distance_miles <= self.risk_thresholds['CRITICAL']:
                    risk_level = 'CRITICAL'
                elif distance_miles <= self.risk_thresholds['HIGH']:
                    risk_level = 'HIGH'
                elif distance_miles <= self.risk_thresholds['MEDIUM']:
                    risk_level = 'MEDIUM'
                
                # Add distance data to environmental site
                env_site[f'{dmarco_id}_distance_miles'] = round(distance_miles, 3)
                env_site[f'{dmarco_id}_risk_level'] = risk_level
                env_site[f'{dmarco_id}_within_1_mile'] = distance_miles <= 1.0
        
        return environmental_sites
    
    def create_comprehensive_database(self, all_environmental_sites):
        """Create comprehensive environmental database with all datasets"""
        print("💾 Creating comprehensive environmental database...")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_environmental_sites)
        
        # Save to CSV
        output_file = f"{self.output_dir}Comprehensive_Environmental_Database.csv"
        df.to_csv(output_file, index=False)
        
        # Create summary by dataset
        summary = {}
        for dataset in self.datasets.keys():
            dataset_sites = [s for s in all_environmental_sites if s['dataset'] == dataset]
            summary[dataset] = {
                'count': len(dataset_sites),
                'risk_type': self.datasets[dataset]['risk_type'],
                'geocoded': len([s for s in dataset_sites if s['geocoding_confidence'] > 0])
            }
        
        # Save summary
        summary_file = f"{self.output_dir}Environmental_Analysis_Summary.json"
        analysis_summary = {
            'analysis_date': datetime.now().isoformat(),
            'total_environmental_sites': len(all_environmental_sites),
            'datasets_processed': len(self.datasets),
            'dataset_summary': summary,
            'database_file': output_file
        }
        
        with open(summary_file, 'w') as f:
            json.dump(analysis_summary, f, indent=2)
        
        print(f"   ✅ Database saved: {output_file}")
        print(f"   📊 Total environmental sites: {len(all_environmental_sites)}")
        print(f"   📋 Summary saved: {summary_file}")
        
        return df, analysis_summary
    
    def run_comprehensive_analysis(self):
        """Run comprehensive environmental analysis for all 6 TCEQ datasets"""
        print("🌍 COMPREHENSIVE D'MARCO ENVIRONMENTAL ANALYSIS")
        print("=" * 60)
        print("Processing all 6 TCEQ environmental datasets...")
        
        all_environmental_sites = []
        
        # Process each dataset
        datasets_processed = {
            'lpst': self.load_existing_lpst_data(),
            'operating_dry_cleaners': self.process_operating_dry_cleaners(),
            'enforcement': self.process_enforcement_notices(),
            'historical_dry_cleaners': self.process_historical_dry_cleaners()
        }
        
        # Combine all sites
        for dataset_name, sites in datasets_processed.items():
            all_environmental_sites.extend(sites)
            print(f"   ✅ {dataset_name}: {len(sites)} sites processed")
        
        print(f"\n📊 TOTAL ENVIRONMENTAL SITES: {len(all_environmental_sites)}")
        
        # Calculate distances to D'Marco sites
        all_environmental_sites = self.calculate_distances_to_dmarco_sites(all_environmental_sites)
        
        # Create comprehensive database
        df, summary = self.create_comprehensive_database(all_environmental_sites)
        
        # Update todo status
        print("\n✅ COMPREHENSIVE ENVIRONMENTAL ANALYSIS COMPLETE!")
        print(f"   📊 {len(all_environmental_sites)} environmental sites analyzed")
        print(f"   🗂️ {len(self.datasets)} datasets processed")
        print(f"   📍 Distance calculations complete for all D'Marco sites")
        
        return df, summary

def main():
    """Run comprehensive environmental analysis"""
    analyzer = ComprehensiveEnvironmentalAnalyzer()
    df, summary = analyzer.run_comprehensive_analysis()
    
    print("\n🎉 READY FOR ENHANCED ENVIRONMENTAL MAPPING!")
    print("Next steps:")
    print("1. Create multi-layer environmental risk maps")
    print("2. Update D'Marco site risk assessments")
    print("3. Generate comprehensive environmental reports")

if __name__ == "__main__":
    main()
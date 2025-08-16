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

class FastEnvironmentalAnalyzer:
    """
    Fast comprehensive environmental analysis focusing on datasets with existing coordinates
    """
    
    def __init__(self):
        self.base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG"
        self.data_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/Environmental/TX_Commission_on_Env"
        self.output_dir = f"{self.base_dir}/D'Marco_Sites/"
        
        # Environmental datasets configuration
        self.datasets = {
            'lpst': {
                'file': 'existing',  # Use existing analysis
                'risk_type': 'Petroleum Contamination',
                'color': '#8B0000',
                'icon': 'tint'
            },
            'operating_dry_cleaners': {
                'file': 'Texas_Commission_on_Environmental_Quality_-_Operating_Dry_Cleaner_Registrations_20250702.csv',
                'risk_type': 'Active Solvent Operations', 
                'color': '#800080',
                'icon': 'industry'
            },
            'enforcement': {
                'file': 'Texas_Commission_on_Environmental_Quality_-_Notices_of_Enforcement__NOE__20250702.csv',
                'risk_type': 'Environmental Violations',
                'color': '#DC143C',
                'icon': 'gavel'
            }
        }
        
        # Risk thresholds (miles)
        self.risk_thresholds = {
            'IMMEDIATE': 0.095,    # 500 feet
            'CRITICAL': 0.25,      # 1/4 mile
            'HIGH': 0.5,           # 1/2 mile
            'MEDIUM': 1.0          # 1 mile
        }
    
    def parse_wkt_point(self, wkt_string):
        """Parse WKT POINT format: POINT (-98.22435 32.21035)"""
        if pd.isna(wkt_string) or not isinstance(wkt_string, str):
            return None, None
        
        try:
            match = re.search(r'POINT\s*\(\s*([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s*\)', wkt_string)
            if match:
                lon, lat = float(match.group(1)), float(match.group(2))
                return lat, lon
            return None, None
        except:
            return None, None
    
    def load_existing_lpst_data(self):
        """Load existing LPST analysis results"""
        print("📍 Loading Existing LPST Analysis...")
        
        lpst_file = f"{self.base_dir}/D'Marco_Sites/D_Marco_LPST_Sites_Database.csv"
        if not Path(lpst_file).exists():
            print(f"   ❌ LPST database not found")
            return []
        
        df = pd.read_csv(lpst_file)
        print(f"   📊 Loaded {len(df)} LPST records")
        
        locations = []
        for idx, row in df.iterrows():
            locations.append({
                'dataset': 'lpst',
                'site_id': str(row.get('LPST_ID', f'LPST_{idx}')),
                'site_name': str(row.get('Site_Name', 'Unknown LPST Site')),
                'address': str(row.get('Address', 'Unknown')),
                'city': str(row.get('City', 'Unknown')),
                'tceq_region': str(row.get('TCEQ_Region', 'Unknown')),
                'reported_date': str(row.get('Reported_Date', 'Unknown')),
                'status': 'ACTIVE LPST',
                'latitude': float(row.get('Latitude', 0)),
                'longitude': float(row.get('Longitude', 0)),
                'geocoding_confidence': float(row.get('Geocoding_Confidence', 1.0)),
                'risk_type': self.datasets['lpst']['risk_type']
            })
        
        print(f"   ✅ Successfully loaded {len(locations)} LPST sites")
        return locations
    
    def process_operating_dry_cleaners(self):
        """Process operating dry cleaner dataset - has WKT coordinates"""
        print("📍 Processing Operating Dry Cleaner Registrations...")
        
        df = pd.read_csv(f"{self.data_dir}/{self.datasets['operating_dry_cleaners']['file']}")
        print(f"   📊 Loaded {len(df)} operating dry cleaner records")
        
        locations = []
        processed = 0
        
        for idx, row in df.iterrows():
            lat, lon = self.parse_wkt_point(row.get('Location Coordinates (Decimal Degrees)'))
            
            if lat and lon and -90 <= lat <= 90 and -180 <= lon <= 180:
                processed += 1
                locations.append({
                    'dataset': 'operating_dry_cleaners',
                    'site_id': str(row.get('Registration ID', f'ODC_{idx}')),
                    'site_name': str(row.get('Regulated Entity Name', 'Unknown Dry Cleaner')),
                    'address': f"{row.get('Location Address', '')}, {row.get('Location City', '')}, {row.get('Location State', '')} {row.get('Location Zip Code', '')}".strip(', '),
                    'city': str(row.get('Location City', 'Unknown')),
                    'county': str(row.get('Location County', 'Unknown')),
                    'tceq_region': str(row.get('TCEQ Region (for Location)', 'Unknown')),
                    'solvent_type': str(row.get('Solvent Type', 'Unknown')),
                    'status': 'ACTIVE',
                    'latitude': float(lat),
                    'longitude': float(lon),
                    'geocoding_confidence': 1.0,
                    'risk_type': self.datasets['operating_dry_cleaners']['risk_type']
                })
        
        print(f"   ✅ Successfully processed {processed} operating dry cleaner sites")
        return locations
    
    def process_enforcement_notices(self):
        """Process enforcement notices dataset - has lat/lon columns"""
        print("📍 Processing Notices of Enforcement...")
        
        df = pd.read_csv(f"{self.data_dir}/{self.datasets['enforcement']['file']}")
        print(f"   📊 Loaded {len(df)} enforcement notice records")
        
        locations = []
        processed = 0
        
        for idx, row in df.iterrows():
            lat = row.get('Latitude')
            lon = row.get('Longitude')
            
            if pd.notna(lat) and pd.notna(lon):
                try:
                    lat, lon = float(lat), float(lon)
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        processed += 1
                        locations.append({
                            'dataset': 'enforcement',
                            'site_id': str(row.get('Notice of Enforcement ID', f'NOE_{idx}')),
                            'site_name': str(row.get('Regulated Entity Name', 'Unknown Entity')),
                            'address': f"{row.get('Physical Location', '')}, {row.get('Physical City ', '')}, TX {row.get('Physical Zip Code', '')}".strip(', '),
                            'city': str(row.get('Physical City ', 'Unknown')),
                            'county': str(row.get('Physical County', 'Unknown')),
                            'tceq_region': str(row.get('TCEQ Region Name', 'Unknown')),
                            'noe_date': str(row.get('NOE Date', 'Unknown')),
                            'violation_count': int(row.get('Total Violation Count', 0)) if pd.notna(row.get('Total Violation Count')) else 0,
                            'status': 'ENFORCEMENT ACTION',
                            'latitude': float(lat),
                            'longitude': float(lon),
                            'geocoding_confidence': 1.0,
                            'risk_type': self.datasets['enforcement']['risk_type']
                        })
                except:
                    continue
        
        print(f"   ✅ Successfully processed {processed} enforcement notice sites")
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
    
    def analyze_dmarco_environmental_risks(self, all_environmental_sites):
        """Analyze environmental risks for each D'Marco site"""
        print("🎯 Analyzing D'Marco Environmental Risks...")
        
        # Group sites by D'Marco location
        dmarco_risk_analysis = {}
        
        for i in range(1, 12):  # D'Marco sites 1-11
            site_id = f"dmarco_site_{str(i).zfill(2)}"
            
            # Find all environmental risks within 1 mile
            risks_within_1_mile = []
            risks_by_type = {}
            
            for env_site in all_environmental_sites:
                if env_site.get(f'{site_id}_within_1_mile', False):
                    risk_info = {
                        'dataset': env_site['dataset'],
                        'site_name': env_site['site_name'],
                        'risk_type': env_site['risk_type'],
                        'distance_miles': env_site[f'{site_id}_distance_miles'],
                        'risk_level': env_site[f'{site_id}_risk_level']
                    }
                    risks_within_1_mile.append(risk_info)
                    
                    # Group by risk type
                    risk_type = env_site['risk_type']
                    if risk_type not in risks_by_type:
                        risks_by_type[risk_type] = []
                    risks_by_type[risk_type].append(risk_info)
            
            # Determine overall risk level for this D'Marco site
            if not risks_within_1_mile:
                overall_risk = 'NO RISK'
            else:
                risk_levels = [r['risk_level'] for r in risks_within_1_mile]
                if 'IMMEDIATE' in risk_levels:
                    overall_risk = 'IMMEDIATE'
                elif 'CRITICAL' in risk_levels:
                    overall_risk = 'CRITICAL'  
                elif 'HIGH' in risk_levels:
                    overall_risk = 'HIGH'
                elif 'MEDIUM' in risk_levels:
                    overall_risk = 'MEDIUM'
                else:
                    overall_risk = 'LOW'
            
            dmarco_risk_analysis[site_id] = {
                'overall_risk_level': overall_risk,
                'total_environmental_sites': len(risks_within_1_mile),
                'risks_by_type': risks_by_type,
                'environmental_concerns': len(risks_by_type),
                'all_risks': risks_within_1_mile
            }
        
        print(f"   ✅ Risk analysis complete for all 11 D'Marco sites")
        return dmarco_risk_analysis
    
    def create_comprehensive_database(self, all_environmental_sites, dmarco_risk_analysis):
        """Create comprehensive environmental database"""
        print("💾 Creating comprehensive environmental database...")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_environmental_sites)
        
        # Save environmental sites database
        env_output_file = f"{self.output_dir}Comprehensive_Environmental_Database.csv"
        df.to_csv(env_output_file, index=False)
        
        # Save D'Marco risk analysis
        risk_output_file = f"{self.output_dir}DMarco_Environmental_Risk_Analysis.json"
        with open(risk_output_file, 'w') as f:
            json.dump(dmarco_risk_analysis, f, indent=2)
        
        # Create summary
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'total_environmental_sites': len(all_environmental_sites),
            'datasets_processed': list(self.datasets.keys()),
            'dmarco_sites_analyzed': 11,
            'database_files': {
                'environmental_sites': env_output_file,
                'dmarco_risk_analysis': risk_output_file
            }
        }
        
        # Dataset breakdown
        for dataset in self.datasets.keys():
            dataset_sites = [s for s in all_environmental_sites if s['dataset'] == dataset]
            summary[f'{dataset}_count'] = len(dataset_sites)
        
        # D'Marco risk summary
        summary['dmarco_risk_summary'] = {}
        for site_id, analysis in dmarco_risk_analysis.items():
            summary['dmarco_risk_summary'][site_id] = {
                'overall_risk_level': analysis['overall_risk_level'],
                'total_environmental_sites': analysis['total_environmental_sites'],
                'environmental_concerns': analysis['environmental_concerns']
            }
        
        # Save summary
        summary_file = f"{self.output_dir}Multi_Dataset_Environmental_Analysis_Summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"   ✅ Environmental database: {env_output_file}")
        print(f"   🎯 D'Marco risk analysis: {risk_output_file}")
        print(f"   📊 Total environmental sites: {len(all_environmental_sites)}")
        print(f"   📋 Analysis summary: {summary_file}")
        
        return df, summary
    
    def run_fast_analysis(self):
        """Run fast comprehensive environmental analysis"""
        print("⚡ FAST COMPREHENSIVE D'MARCO ENVIRONMENTAL ANALYSIS")
        print("=" * 65)
        print("Processing 3 datasets with existing coordinates...")
        
        all_environmental_sites = []
        
        # Process each dataset
        datasets_processed = {
            'lpst': self.load_existing_lpst_data(),
            'operating_dry_cleaners': self.process_operating_dry_cleaners(),
            'enforcement': self.process_enforcement_notices()
        }
        
        # Combine all sites
        for dataset_name, sites in datasets_processed.items():
            all_environmental_sites.extend(sites)
            print(f"   ✅ {dataset_name}: {len(sites)} sites processed")
        
        print(f"\n📊 TOTAL ENVIRONMENTAL SITES: {len(all_environmental_sites)}")
        
        # Calculate distances to D'Marco sites
        all_environmental_sites = self.calculate_distances_to_dmarco_sites(all_environmental_sites)
        
        # Analyze D'Marco environmental risks
        dmarco_risk_analysis = self.analyze_dmarco_environmental_risks(all_environmental_sites)
        
        # Create comprehensive database
        df, summary = self.create_comprehensive_database(all_environmental_sites, dmarco_risk_analysis)
        
        print("\n✅ FAST COMPREHENSIVE ENVIRONMENTAL ANALYSIS COMPLETE!")
        print(f"   📊 {len(all_environmental_sites)} environmental sites analyzed")
        print(f"   🗂️ 3 datasets processed (LPST, Operating Dry Cleaners, Enforcement)")
        print(f"   📍 Distance calculations complete for all D'Marco sites")
        print(f"   🎯 Risk analysis complete for all 11 D'Marco sites")
        
        return df, summary, dmarco_risk_analysis

def main():
    """Run fast comprehensive environmental analysis"""
    analyzer = FastEnvironmentalAnalyzer()
    df, summary, risk_analysis = analyzer.run_fast_analysis()
    
    print("\n🎉 READY FOR ENHANCED ENVIRONMENTAL MAPPING!")
    print("Next: Create multi-layer environmental risk maps with all 3 datasets")

if __name__ == "__main__":
    main()
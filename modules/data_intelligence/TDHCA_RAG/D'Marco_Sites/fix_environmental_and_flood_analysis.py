#!/usr/bin/env python3
"""
🔧 Fix Environmental and Flood Analysis for D'Marco Sites
WINGMAN Agent - QA Issue Resolution

Issues to fix:
1. Environmental screening showing 0 results (likely no coordinates in TCEQ data)
2. FEMA API failures - use local flood zone data instead
3. Integrate proper flood risk ratings (X, AE, VE, etc.)
"""

import pandas as pd
import geopandas as gpd
import json
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

class EnvironmentalFloodFixer:
    """Fix environmental and flood analysis using local data"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        self.flood_data_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/priorcode/state_flood_data/TX/geographic_regions")
        
        # Input files
        self.corrected_sites_path = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        
        # Texas counties we need to cover
        self.texas_counties = {
            'Harris': '48201',    # Houston
            'Dallas': '48113',    # Dallas  
            'Bexar': '48029',     # San Antonio
            'Orange': '48361',    # East Texas
            'Henderson': '48213', # East Texas
            'Kaufman': '48257',   # Dallas area
            'Guadalupe': '48187'  # San Antonio area
        }
        
        # Flood zone risk ratings
        self.FLOOD_ZONE_RISK = {
            'X': {'risk': 'LOW', 'description': 'Minimal flood risk', 'insurance_required': False},
            'AE': {'risk': 'HIGH', 'description': '1% annual chance flood (100-year)', 'insurance_required': True},
            'A': {'risk': 'HIGH', 'description': '1% annual chance flood (no base flood elevation)', 'insurance_required': True},
            'VE': {'risk': 'VERY_HIGH', 'description': 'Coastal high hazard area', 'insurance_required': True},
            'AO': {'risk': 'MEDIUM', 'description': 'Sheet flow flooding', 'insurance_required': True},
            'AH': {'risk': 'MEDIUM', 'description': 'Ponding to 1-3 feet', 'insurance_required': True},
            'OPEN WATER': {'risk': 'VERY_HIGH', 'description': 'Open water', 'insurance_required': True}
        }
        
        # Regional coverage mapping
        self.regional_coverage = {
            'East_Texas': ['48361', '48213'],  # Orange, Henderson counties
            'San_Antonio': ['48029', '48187'],  # Bexar, Guadalupe counties  
            'Austin_Central': ['48453'],        # Travis county
            # Note: Missing Harris, Dallas, Tarrant, Collin, Kaufman
        }
        
    def load_dmarco_sites(self):
        """Load D'Marco sites"""
        print("🔧 Loading D'Marco sites...")
        
        with open(self.corrected_sites_path, 'r') as f:
            sites_data = json.load(f)
        
        print(f"✅ Loaded {len(sites_data)} sites")
        return sites_data
    
    def load_flood_data_for_region(self, region_key):
        """Load flood zone data for a specific region"""
        try:
            flood_file = self.flood_data_dir / region_key / f"{region_key}_flood_zones.geojson"
            if flood_file.exists():
                flood_gdf = gpd.read_file(flood_file)
                print(f"✅ Loaded {len(flood_gdf)} flood zones for {region_key}")
                return flood_gdf
            else:
                print(f"⚠️  No flood data found for {region_key}")
                return None
        except Exception as e:
            print(f"❌ Error loading flood data for {region_key}: {e}")
            return None
    
    def get_county_fips(self, county_name):
        """Get FIPS code for county"""
        clean_county = county_name.replace(' County', '').replace('County ', '')
        return self.texas_counties.get(clean_county)
    
    def find_region_for_county(self, county_fips):
        """Find which region contains the county"""
        for region, counties in self.regional_coverage.items():
            if county_fips in counties:
                return region
        return None
    
    def get_flood_zone_for_point(self, lat, lng, flood_gdf):
        """Get flood zone for a specific coordinate"""
        if flood_gdf is None or flood_gdf.empty:
            return None, None
        
        try:
            # Create point geometry
            from shapely.geometry import Point
            point = Point(lng, lat)
            
            # Find intersecting flood zone
            intersects = flood_gdf[flood_gdf.geometry.contains(point)]
            
            if not intersects.empty:
                # Get the first match (should only be one)
                zone_info = intersects.iloc[0]
                flood_zone = zone_info.get('FLD_ZONE', zone_info.get('ZONE', 'UNKNOWN'))
                return flood_zone, zone_info
            else:
                return 'NOT_IN_FLOODPLAIN', None
                
        except Exception as e:
            print(f"  ❌ Error checking flood zone for ({lat}, {lng}): {e}")
            return 'ERROR', None
    
    def analyze_environmental_data_quality(self, sites_data):
        """Analyze why environmental screening shows 0 results"""
        print("\n🔍 ENVIRONMENTAL DATA QUALITY ANALYSIS")
        
        # Check TCEQ LPST database
        try:
            lpst_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/Environmental/TX_Commission_on_Env/Texas_Commission_on_Environmental_Quality_-_Leaking_Petroleum_Storage_Tank__LPST__Sites_20250702.csv"
            lpst_df = pd.read_csv(lpst_path)
            
            print(f"📊 TCEQ LPST Database: {len(lpst_df)} total records")
            
            # Check for coordinate columns
            coord_cols = [col for col in lpst_df.columns if any(term in col.lower() for term in ['lat', 'lon', 'coord', 'x', 'y'])]
            print(f"🗺️  Coordinate columns found: {coord_cols}")
            
            if not coord_cols:
                print("❌ ISSUE IDENTIFIED: No coordinate columns in TCEQ LPST database")
                print("   This explains why environmental screening shows 0 results")
                print("   Cannot perform proximity analysis without coordinates")
                
                # Check Harris County records as sample
                harris_sites = lpst_df[lpst_df['County'].str.contains('Harris', na=False, case=False)]
                print(f"   Harris County LPST sites: {len(harris_sites)} (but no coordinates)")
                
                return {
                    'issue': 'NO_COORDINATES',
                    'total_records': len(lpst_df),
                    'harris_county_records': len(harris_sites),
                    'recommendation': 'Need to geocode TCEQ addresses or find geocoded version'
                }
            else:
                return {'issue': 'NONE', 'coordinates_available': True}
                
        except Exception as e:
            print(f"❌ Error analyzing environmental data: {e}")
            return {'issue': 'DATA_ACCESS_ERROR'}
    
    def fix_flood_analysis(self, sites_data):
        """Fix flood analysis using local FEMA data"""
        print("\n🌊 FIXING FLOOD ANALYSIS")
        
        # Load available flood data
        flood_data = {}
        for region in ['East_Texas', 'San_Antonio', 'Austin_Central']:
            flood_gdf = self.load_flood_data_for_region(region)
            if flood_gdf is not None:
                flood_data[region] = flood_gdf
        
        updated_sites = []
        flood_analysis_results = {
            'sites_analyzed': 0,
            'flood_zones_found': 0,
            'coverage_gaps': 0,
            'zone_distribution': {}
        }
        
        for site in sites_data:
            site_copy = site.copy()
            site_lat = site['parcel_center_lat']
            site_lng = site['parcel_center_lng']
            county_name = site.get('census_county', 'Unknown')
            
            # Get county FIPS and find region
            county_fips = self.get_county_fips(county_name)
            region = self.find_region_for_county(county_fips) if county_fips else None
            
            flood_analysis_results['sites_analyzed'] += 1
            
            if region and region in flood_data:
                # Get flood zone
                flood_zone, zone_info = self.get_flood_zone_for_point(site_lat, site_lng, flood_data[region])
                
                if flood_zone and flood_zone != 'ERROR':
                    # Update flood information
                    site_copy['fema_analysis_status'] = 'SUCCESS_LOCAL_DATA'
                    site_copy['fema_flood_zone'] = flood_zone
                    site_copy['fema_gap_flag'] = False
                    site_copy['fema_method'] = f'LOCAL_GEOSPATIAL_{region.upper()}'
                    
                    # Add risk assessment
                    risk_info = self.FLOOD_ZONE_RISK.get(flood_zone, {
                        'risk': 'UNKNOWN', 
                        'description': f'Unknown zone: {flood_zone}',
                        'insurance_required': False
                    })
                    
                    site_copy['flood_risk_level'] = risk_info['risk']
                    site_copy['flood_insurance_required'] = risk_info['insurance_required']
                    site_copy['flood_zone_description'] = risk_info['description']
                    
                    flood_analysis_results['flood_zones_found'] += 1
                    
                    # Track zone distribution
                    if flood_zone not in flood_analysis_results['zone_distribution']:
                        flood_analysis_results['zone_distribution'][flood_zone] = 0
                    flood_analysis_results['zone_distribution'][flood_zone] += 1
                    
                    print(f"  ✅ Site {site['site_index']}: {flood_zone} ({risk_info['risk']} risk)")
                else:
                    site_copy['fema_analysis_status'] = 'LOCAL_DATA_ERROR'
                    site_copy['flood_risk_level'] = 'ANALYSIS_ERROR'
                    print(f"  ❌ Site {site['site_index']}: Error analyzing flood zone")
            else:
                # No coverage available
                site_copy['fema_analysis_status'] = 'NO_LOCAL_COVERAGE'
                site_copy['fema_flood_zone'] = 'NO_COVERAGE_AVAILABLE'
                site_copy['flood_risk_level'] = 'UNKNOWN_NO_DATA'
                site_copy['fema_gap_flag'] = True
                site_copy['fema_method'] = 'NO_REGIONAL_DATA'
                
                flood_analysis_results['coverage_gaps'] += 1
                print(f"  ⚠️  Site {site['site_index']}: No flood data coverage for {county_name}")
            
            updated_sites.append(site_copy)
        
        return updated_sites, flood_analysis_results
    
    def create_fixed_analysis(self):
        """Create fixed environmental and flood analysis"""
        print("🚀 Starting Environmental & Flood Analysis Fix...")
        
        # Load data
        sites_data = self.load_dmarco_sites()
        
        # Analyze environmental data quality
        env_analysis = self.analyze_environmental_data_quality(sites_data)
        
        # Fix flood analysis
        updated_sites, flood_results = self.fix_flood_analysis(sites_data)
        
        # Create summary report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        summary_report = {
            'analysis_date': datetime.now().isoformat(),
            'total_sites': len(sites_data),
            'environmental_analysis': env_analysis,
            'flood_analysis_results': flood_results,
            'coverage_summary': {
                'flood_zones_identified': flood_results['flood_zones_found'],
                'coverage_gaps': flood_results['coverage_gaps'],
                'coverage_percentage': round((flood_results['flood_zones_found'] / len(sites_data)) * 100, 1)
            },
            'zone_distribution': flood_results['zone_distribution'],
            'recommendations': [
                'Environmental: Need geocoded TCEQ LPST database for proximity analysis',
                'Flood: Obtain additional regional flood data for Harris, Dallas, Tarrant counties',
                'Consider alternative environmental databases with coordinates'
            ]
        }
        
        # Save updated sites data
        updated_sites_file = self.base_dir / f"dmarco_sites_FIXED_env_flood_{timestamp}.json"
        with open(updated_sites_file, 'w') as f:
            json.dump(updated_sites, f, indent=2)
        
        # Save summary report
        report_file = self.base_dir / f"Environmental_Flood_QA_Report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(summary_report, f, indent=2)
        
        print(f"\n📊 ANALYSIS COMPLETE")
        print(f"✅ Sites with flood zones identified: {flood_results['flood_zones_found']}/{len(sites_data)} ({summary_report['coverage_summary']['coverage_percentage']}%)")
        print(f"⚠️  Sites with coverage gaps: {flood_results['coverage_gaps']}")
        print(f"🗂️  Flood zone distribution: {flood_results['zone_distribution']}")
        print(f"\n💾 Files created:")
        print(f"   • Updated sites: {updated_sites_file.name}")
        print(f"   • QA report: {report_file.name}")
        
        return summary_report

if __name__ == "__main__":
    fixer = EnvironmentalFloodFixer()
    results = fixer.create_fixed_analysis()
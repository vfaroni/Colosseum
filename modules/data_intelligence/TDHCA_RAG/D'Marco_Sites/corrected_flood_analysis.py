#!/usr/bin/env python3
"""
🌊 CORRECTED Flood Analysis for D'Marco Sites
WINGMAN Agent - Using ALL Available Local FEMA Data

Now using:
- Regional data (geographic_regions)
- Metro county data (metro_counties) 
- Comprehensive coverage for major Texas counties
"""

import pandas as pd
import geopandas as gpd
import json
from datetime import datetime
from pathlib import Path
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

class CorrectedFloodAnalyzer:
    """Comprehensive flood analysis using ALL available local FEMA data"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        self.flood_base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/priorcode/state_flood_data/TX")
        
        # Input files
        self.corrected_sites_path = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        
        # Texas counties and their FIPS codes
        self.texas_counties = {
            'Harris': '48201',    # Houston - METRO COUNTY
            'Dallas': '48113',    # Dallas - METRO COUNTY  
            'Bexar': '48029',     # San Antonio - REGIONAL
            'Tarrant': '48439',   # Fort Worth
            'Travis': '48453',    # Austin - METRO COUNTY (48015)
            'Collin': '48085',    # Dallas suburbs
            'Orange': '48361',    # East Texas - REGIONAL
            'Henderson': '48213', # East Texas - REGIONAL
            'Kaufman': '48257',   # Dallas area
            'Guadalupe': '48187'  # San Antonio area - REGIONAL
        }
        
        # Flood zone risk ratings
        self.FLOOD_ZONE_RISK = {
            'X': {'risk': 'LOW', 'description': 'Minimal flood risk - Outside 500-year floodplain', 'insurance_required': False},
            'AE': {'risk': 'HIGH', 'description': '1% annual chance flood (100-year floodplain)', 'insurance_required': True},
            'A': {'risk': 'HIGH', 'description': '1% annual chance flood (no base flood elevation)', 'insurance_required': True},
            'VE': {'risk': 'VERY_HIGH', 'description': 'Coastal high hazard area with wave action', 'insurance_required': True},
            'AO': {'risk': 'MEDIUM', 'description': 'Sheet flow flooding 1-3 feet deep', 'insurance_required': True},
            'AH': {'risk': 'MEDIUM', 'description': 'Ponding flooding 1-3 feet deep', 'insurance_required': True},
            'OPEN WATER': {'risk': 'VERY_HIGH', 'description': 'Open water area', 'insurance_required': True},
            'NOT_IN_FLOODPLAIN': {'risk': 'MINIMAL', 'description': 'Outside mapped flood hazard areas', 'insurance_required': False}
        }
        
        # Data source mapping - priority order
        self.data_sources = [
            {
                'type': 'metro_counties',
                'path': self.flood_base_dir / 'metro_counties',
                'counties': ['48201', '48113', '48015', '48157', '48167', '48039', '48291', '48339', '48473']
            },
            {
                'type': 'geographic_regions', 
                'path': self.flood_base_dir / 'geographic_regions',
                'regions': {
                    'East_Texas': ['48361', '48213'],  # Orange, Henderson
                    'San_Antonio': ['48029', '48187'],  # Bexar, Guadalupe
                    'Austin_Central': ['48453'],        # Travis
                    'North_Texas': ['48485', '48143', '48231', '48181'],
                    'South_Texas': [],
                    'Southeast_Texas': ['48239', '48361'],
                    'West_Texas': []
                }
            }
        ]
        
    def load_dmarco_sites(self):
        """Load D'Marco sites"""
        print("🔧 Loading D'Marco sites...")
        
        with open(self.corrected_sites_path, 'r') as f:
            sites_data = json.load(f)
        
        print(f"✅ Loaded {len(sites_data)} sites")
        return sites_data
    
    def get_county_fips(self, county_name):
        """Get FIPS code for county"""
        clean_county = county_name.replace(' County', '').replace('County ', '')
        return self.texas_counties.get(clean_county)
    
    def load_flood_data_for_county(self, county_fips):
        """Load flood data for specific county - check all sources"""
        flood_gdf = None
        data_source = None
        
        # Try metro counties first (higher priority)
        metro_file = self.data_sources[0]['path'] / f"{county_fips}_{self.get_county_name(county_fips)}" / f"{county_fips}_flood_zones.geojson"
        if metro_file.exists():
            try:
                flood_gdf = gpd.read_file(metro_file)
                data_source = f"METRO_COUNTY_{county_fips}"
                print(f"  ✅ Loaded {len(flood_gdf)} flood zones from metro_counties/{county_fips}")
                return flood_gdf, data_source
            except Exception as e:
                print(f"  ❌ Error loading metro county data for {county_fips}: {e}")
        
        # Try regional data
        for region_name, region_counties in self.data_sources[1]['regions'].items():
            if county_fips in region_counties:
                region_file = self.data_sources[1]['path'] / region_name / f"{region_name}_flood_zones.geojson"
                if region_file.exists():
                    try:
                        flood_gdf = gpd.read_file(region_file)
                        data_source = f"REGIONAL_{region_name.upper()}"
                        print(f"  ✅ Loaded {len(flood_gdf)} flood zones from {region_name}")
                        return flood_gdf, data_source
                    except Exception as e:
                        print(f"  ❌ Error loading regional data for {region_name}: {e}")
                        
        return None, None
    
    def get_county_name(self, county_fips):
        """Get county name from FIPS code"""
        county_map = {v: k for k, v in self.texas_counties.items()}
        return county_map.get(county_fips, 'Unknown')
    
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
                flood_zone = zone_info.get('FLD_ZONE', zone_info.get('ZONE', zone_info.get('FLOOD_ZONE', 'UNKNOWN')))
                return flood_zone, zone_info
            else:
                return 'NOT_IN_FLOODPLAIN', None
                
        except Exception as e:
            print(f"    ❌ Error checking flood zone for ({lat}, {lng}): {e}")
            return 'ERROR', None
    
    def analyze_all_sites(self):
        """Analyze flood zones for all D'Marco sites"""
        print("🌊 COMPREHENSIVE FLOOD ANALYSIS - Using ALL Available Data")
        
        # Load sites
        sites_data = self.load_dmarco_sites()
        
        # Track results
        results = {
            'sites_analyzed': 0,
            'sites_with_flood_data': 0,
            'coverage_gaps': 0,
            'zone_distribution': {},
            'data_source_usage': {},
            'updated_sites': []
        }
        
        print(f"\n🔍 Analyzing flood zones for {len(sites_data)} sites...")
        
        for site in sites_data:
            site_copy = site.copy()
            site_index = site['site_index']
            site_lat = site['parcel_center_lat']
            site_lng = site['parcel_center_lng']
            county_name = site.get('census_county', 'Unknown')
            
            results['sites_analyzed'] += 1
            
            # Get county FIPS
            county_fips = self.get_county_fips(county_name)
            
            if county_fips:
                print(f"Site {site_index} ({county_name}): ", end="")
                
                # Load flood data for this county
                flood_gdf, data_source = self.load_flood_data_for_county(county_fips)
                
                if flood_gdf is not None:
                    # Get flood zone for this specific point
                    flood_zone, zone_info = self.get_flood_zone_for_point(site_lat, site_lng, flood_gdf)
                    
                    if flood_zone and flood_zone != 'ERROR':
                        # Update site with flood information
                        site_copy['fema_analysis_status'] = 'SUCCESS_LOCAL_DATA'
                        site_copy['fema_flood_zone'] = flood_zone
                        site_copy['fema_gap_flag'] = False
                        site_copy['fema_method'] = data_source
                        
                        # Add risk assessment
                        risk_info = self.FLOOD_ZONE_RISK.get(flood_zone, {
                            'risk': 'UNKNOWN', 
                            'description': f'Unknown zone: {flood_zone}',
                            'insurance_required': False
                        })
                        
                        site_copy['flood_risk_level'] = risk_info['risk']
                        site_copy['flood_insurance_required'] = risk_info['insurance_required']
                        site_copy['flood_zone_description'] = risk_info['description']
                        
                        results['sites_with_flood_data'] += 1
                        
                        # Track statistics
                        if flood_zone not in results['zone_distribution']:
                            results['zone_distribution'][flood_zone] = 0
                        results['zone_distribution'][flood_zone] += 1
                        
                        if data_source not in results['data_source_usage']:
                            results['data_source_usage'][data_source] = 0
                        results['data_source_usage'][data_source] += 1
                        
                        print(f"✅ {flood_zone} ({risk_info['risk']} risk)")
                    else:
                        site_copy['fema_analysis_status'] = 'POINT_ANALYSIS_ERROR'
                        site_copy['flood_risk_level'] = 'ANALYSIS_ERROR'
                        results['coverage_gaps'] += 1
                        print(f"❌ Error analyzing point")
                else:
                    # No flood data available for this county
                    site_copy['fema_analysis_status'] = 'NO_LOCAL_COVERAGE'
                    site_copy['fema_flood_zone'] = 'NO_COVERAGE_AVAILABLE'
                    site_copy['flood_risk_level'] = 'UNKNOWN_NO_DATA'
                    site_copy['fema_gap_flag'] = True
                    site_copy['fema_method'] = 'NO_DATA_AVAILABLE'
                    
                    results['coverage_gaps'] += 1
                    print(f"⚠️  No flood data coverage")
            else:
                # Unknown county
                site_copy['fema_analysis_status'] = 'UNKNOWN_COUNTY'
                site_copy['flood_risk_level'] = 'UNKNOWN_COUNTY'
                results['coverage_gaps'] += 1
                print(f"Site {site_index}: ❌ Unknown county: {county_name}")
            
            results['updated_sites'].append(site_copy)
        
        return results
    
    def create_comprehensive_flood_analysis(self):
        """Create comprehensive flood analysis with all available data"""
        print("🚀 Starting COMPREHENSIVE Flood Analysis...")
        
        # Run analysis
        results = self.analyze_all_sites()
        
        # Create summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        coverage_percentage = round((results['sites_with_flood_data'] / results['sites_analyzed']) * 100, 1)
        
        summary_report = {
            'analysis_date': datetime.now().isoformat(),
            'total_sites': results['sites_analyzed'],
            'sites_with_flood_data': results['sites_with_flood_data'],
            'coverage_gaps': results['coverage_gaps'],
            'coverage_percentage': coverage_percentage,
            'zone_distribution': results['zone_distribution'],
            'data_source_usage': results['data_source_usage'],
            'flood_zone_breakdown': {
                'low_risk_zones': results['zone_distribution'].get('X', 0) + results['zone_distribution'].get('NOT_IN_FLOODPLAIN', 0),
                'medium_risk_zones': results['zone_distribution'].get('AO', 0) + results['zone_distribution'].get('AH', 0),
                'high_risk_zones': results['zone_distribution'].get('AE', 0) + results['zone_distribution'].get('A', 0),
                'very_high_risk_zones': results['zone_distribution'].get('VE', 0) + results['zone_distribution'].get('OPEN WATER', 0)
            }
        }
        
        # Save results
        updated_sites_file = self.base_dir / f"dmarco_sites_COMPREHENSIVE_flood_{timestamp}.json"
        with open(updated_sites_file, 'w') as f:
            json.dump(results['updated_sites'], f, indent=2)
        
        report_file = self.base_dir / f"Comprehensive_Flood_Analysis_Report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(summary_report, f, indent=2)
        
        print(f"\n📊 COMPREHENSIVE FLOOD ANALYSIS COMPLETE")
        print(f"✅ Sites with flood zones: {results['sites_with_flood_data']}/{results['sites_analyzed']} ({coverage_percentage}%)")
        print(f"⚠️  Coverage gaps: {results['coverage_gaps']}")
        print(f"🗂️  Zone distribution: {results['zone_distribution']}")
        print(f"📍 Data sources used: {results['data_source_usage']}")
        print(f"\n💾 Files created:")
        print(f"   • Updated sites: {updated_sites_file.name}")
        print(f"   • Analysis report: {report_file.name}")
        
        return summary_report

if __name__ == "__main__":
    analyzer = CorrectedFloodAnalyzer()
    results = analyzer.create_comprehensive_flood_analysis()
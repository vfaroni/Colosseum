#!/usr/bin/env python3
"""
🌊 FINAL Flood Analysis for D'Marco Sites
WINGMAN Agent - Using Correct File Paths for Metro Counties

Fixed file naming issue - now accessing actual flood data correctly
"""

import pandas as pd
import geopandas as gpd
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class FinalFloodAnalyzer:
    """Final flood analysis with correct file paths"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites")
        self.corrected_sites_path = self.base_dir / "Production_Analysis_20250730/dmarco_production_analysis_20250730_134731_COUNTY_CORRECTED.json"
        
        # Direct file paths to flood data
        self.flood_files = {
            'Harris': '/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/priorcode/state_flood_data/TX/metro_counties/48201_Harris/48201_flood_zones.geojson',
            'Dallas': '/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/priorcode/state_flood_data/TX/metro_counties/48113_Dallas/48113_flood_zones.geojson',
            'Bexar': '/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/priorcode/state_flood_data/TX/geographic_regions/San_Antonio/San_Antonio_flood_zones.geojson',
            'Orange': '/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/priorcode/state_flood_data/TX/geographic_regions/East_Texas/East_Texas_flood_zones.geojson',
            'Henderson': '/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/priorcode/state_flood_data/TX/geographic_regions/East_Texas/East_Texas_flood_zones.geojson',
            'Guadalupe': '/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/priorcode/state_flood_data/TX/geographic_regions/San_Antonio/San_Antonio_flood_zones.geojson'
        }
        
        # Flood zone risk ratings
        self.FLOOD_ZONE_RISK = {
            'X': {'risk': 'LOW', 'description': 'Minimal flood risk - Outside 500-year floodplain', 'insurance_required': False},
            'AE': {'risk': 'HIGH', 'description': '1% annual chance flood (100-year floodplain)', 'insurance_required': True},
            'A': {'risk': 'HIGH', 'description': '1% annual chance flood (no base flood elevation)', 'insurance_required': True},
            'VE': {'risk': 'VERY_HIGH', 'description': 'Coastal high hazard area with wave action', 'insurance_required': True},
            'AO': {'risk': 'MEDIUM', 'description': 'Sheet flow flooding 1-3 feet deep', 'insurance_required': True},
            'AH': {'risk': 'MEDIUM', 'description': 'Ponding flooding 1-3 feet deep', 'insurance_required': True}
        }
        
    def load_dmarco_sites(self):
        """Load D'Marco sites"""
        with open(self.corrected_sites_path, 'r') as f:
            sites_data = json.load(f)
        print(f"✅ Loaded {len(sites_data)} D'Marco sites")
        return sites_data
    
    def get_flood_zone_for_point(self, lat, lng, flood_gdf, county_name):
        """Get flood zone for specific coordinates"""
        try:
            from shapely.geometry import Point
            point = Point(lng, lat)
            
            # Find intersecting flood zone
            intersects = flood_gdf[flood_gdf.geometry.contains(point)]
            
            if not intersects.empty:
                zone_info = intersects.iloc[0]
                flood_zone = zone_info.get('FLD_ZONE', zone_info.get('ZONE', 'UNKNOWN'))
                return flood_zone, zone_info
            else:
                return 'NOT_IN_FLOODPLAIN', None
                
        except Exception as e:
            print(f"    ❌ Error for {county_name}: {e}")
            return 'ERROR', None
    
    def analyze_sites(self):
        """Analyze flood zones for all sites with efficient loading"""
        print("🌊 FINAL FLOOD ANALYSIS - Comprehensive Coverage")
        
        sites_data = self.load_dmarco_sites()
        
        # Load flood data by county (only load each dataset once)
        loaded_flood_data = {}
        
        results = {
            'sites_analyzed': 0,
            'sites_with_flood_data': 0,
            'zone_distribution': {},
            'updated_sites': []
        }
        
        for site in sites_data:
            site_copy = site.copy()
            site_index = site['site_index']
            site_lat = site['parcel_center_lat']
            site_lng = site['parcel_center_lng']
            
            # Clean county name
            raw_county = site.get('census_county', 'Unknown')
            county_name = raw_county.replace(' County', '').replace('County ', '')
            
            results['sites_analyzed'] += 1
            
            print(f"Site {site_index} ({county_name}): ", end="")
            
            # Check if we have flood data for this county
            if county_name in self.flood_files:
                flood_file = self.flood_files[county_name]
                
                # Load flood data if not already loaded
                if county_name not in loaded_flood_data:
                    try:
                        print(f"[Loading {county_name} flood data] ", end="")
                        flood_gdf = gpd.read_file(flood_file)
                        loaded_flood_data[county_name] = flood_gdf
                        print(f"[{len(flood_gdf)} zones] ", end="")
                    except Exception as e:
                        print(f"❌ Error loading {county_name}: {e}")
                        loaded_flood_data[county_name] = None
                
                # Get flood zone for this point
                if loaded_flood_data[county_name] is not None:
                    flood_zone, zone_info = self.get_flood_zone_for_point(
                        site_lat, site_lng, loaded_flood_data[county_name], county_name
                    )
                    
                    if flood_zone and flood_zone != 'ERROR':
                        # Update site with flood information
                        site_copy['fema_analysis_status'] = 'SUCCESS_LOCAL_DATA'
                        site_copy['fema_flood_zone'] = flood_zone
                        site_copy['fema_gap_flag'] = False
                        site_copy['fema_method'] = f'LOCAL_{county_name.upper()}_COUNTY'
                        
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
                        
                        # Track zone distribution
                        if flood_zone not in results['zone_distribution']:
                            results['zone_distribution'][flood_zone] = 0
                        results['zone_distribution'][flood_zone] += 1
                        
                        print(f"✅ {flood_zone} ({risk_info['risk']} risk)")
                    else:
                        site_copy['fema_analysis_status'] = 'POINT_ANALYSIS_ERROR'
                        site_copy['flood_risk_level'] = 'ANALYSIS_ERROR'
                        print(f"❌ Point analysis error")
                else:
                    site_copy['fema_analysis_status'] = 'LOAD_ERROR'
                    site_copy['flood_risk_level'] = 'LOAD_ERROR'
                    print(f"❌ Data load error")
            else:
                # No flood data available for this county
                site_copy['fema_analysis_status'] = 'NO_COVERAGE'
                site_copy['fema_flood_zone'] = 'NO_COVERAGE'
                site_copy['flood_risk_level'] = 'NO_DATA'
                site_copy['fema_gap_flag'] = True
                print(f"⚠️  No coverage available")
            
            results['updated_sites'].append(site_copy)
        
        return results
    
    def create_final_analysis(self):
        """Create final flood analysis"""
        print("🚀 Starting FINAL Flood Analysis...")
        
        # Run analysis
        results = self.analyze_sites()
        
        # Calculate statistics
        coverage_percentage = round((results['sites_with_flood_data'] / results['sites_analyzed']) * 100, 1)
        
        # Create summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        summary_report = {
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'FINAL_COMPREHENSIVE_FLOOD_ANALYSIS',
            'total_sites': results['sites_analyzed'],
            'sites_with_flood_data': results['sites_with_flood_data'],
            'coverage_percentage': coverage_percentage,
            'zone_distribution': results['zone_distribution'],
            'risk_summary': {
                'low_risk': results['zone_distribution'].get('X', 0) + results['zone_distribution'].get('NOT_IN_FLOODPLAIN', 0),
                'medium_risk': results['zone_distribution'].get('AO', 0) + results['zone_distribution'].get('AH', 0),
                'high_risk': results['zone_distribution'].get('AE', 0) + results['zone_distribution'].get('A', 0),
                'very_high_risk': results['zone_distribution'].get('VE', 0)
            }
        }
        
        # Save results
        final_sites_file = self.base_dir / f"dmarco_sites_FINAL_flood_analysis_{timestamp}.json"
        with open(final_sites_file, 'w') as f:
            json.dump(results['updated_sites'], f, indent=2)
        
        report_file = self.base_dir / f"Final_Flood_Analysis_Report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(summary_report, f, indent=2)
        
        print(f"\n📊 FINAL FLOOD ANALYSIS COMPLETE")
        print(f"✅ Sites with flood data: {results['sites_with_flood_data']}/{results['sites_analyzed']} ({coverage_percentage}%)")
        print(f"🗂️  Zone distribution: {results['zone_distribution']}")
        print(f"🛡️  Risk summary: {summary_report['risk_summary']}")
        print(f"\n💾 Files saved:")
        print(f"   • Final sites data: {final_sites_file.name}")
        print(f"   • Analysis report: {report_file.name}")
        
        return summary_report

if __name__ == "__main__":
    analyzer = FinalFloodAnalyzer()
    results = analyzer.create_final_analysis()
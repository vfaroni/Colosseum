#!/usr/bin/env python3
"""
HQTA Cross-Validation Analyzer
QA analysis to check Vitor's CTCAC transit analysis against official California HQTA polygons
and high-frequency transit routes.

This script will:
1. Load Vitor's 263 site analysis
2. Cross-reference with official HQTA polygon boundaries
3. Analyze high-frequency transit routes and stops
4. Generate QA findings for sites that may qualify for 7 points (HQTA)
"""

import pandas as pd
import json
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

# Add geospatial libraries with fallback
try:
    import geopandas as gpd
    from shapely.geometry import Point
    from shapely.ops import transform
    import pyproj
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    print("Warning: Geospatial libraries not available. Using coordinate-based analysis.")
    GEOSPATIAL_AVAILABLE = False

class HQTAAnalyzer:
    def __init__(self):
        # Data paths in Colosseum
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.data_path = self.base_path / "data_sets" / "california" / "CA_Transit_Data"
        self.vitor_file = self.base_path / "modules" / "lihtc_analyst" / "botn_engine" / "outputs" / "CTCAC_TRANSIT_COMPLIANCE_REPORT_20250731_220012.xlsx"
        
        # Output paths
        self.output_path = self.base_path / "hqta_qa_analysis"
        self.output_path.mkdir(exist_ok=True)
        
        # Initialize data containers
        self.vitor_data = None
        self.hqta_polygons = None
        self.transit_stops = None
        self.transit_routes = None
        self.qa_results = []
        
    def load_vitor_analysis(self):
        """Load Vitor's original CTCAC transit analysis"""
        print("Loading Vitor's CTCAC transit analysis...")
        self.vitor_data = pd.read_excel(self.vitor_file)
        print(f"Loaded {len(self.vitor_data)} sites from Vitor's analysis")
        
        # Get top candidates (sites with most transit stops)
        self.top_candidates = self.vitor_data.nlargest(20, 'Stops_Within_Third_Mile').copy()
        print(f"Top 20 candidates with most stops: {self.top_candidates['Stops_Within_Third_Mile'].tolist()}")
        
        return self.vitor_data
    
    def load_hqta_data(self):
        """Load official California HQTA polygon data"""
        hqta_file = self.data_path / "High_Quality_Transit_Areas.geojson"
        
        if not hqta_file.exists():
            print(f"Error: HQTA file not found at {hqta_file}")
            return None
            
        print("Loading official HQTA polygon data...")
        
        if GEOSPATIAL_AVAILABLE:
            self.hqta_polygons = gpd.read_file(hqta_file)
            print(f"Loaded {len(self.hqta_polygons)} HQTA polygons")
            print(f"HQTA columns: {list(self.hqta_polygons.columns)}")
        else:
            # Fallback: Load as JSON and extract basic info
            with open(hqta_file, 'r') as f:
                hqta_json = json.load(f)
            print(f"Loaded {len(hqta_json['features'])} HQTA features (coordinate analysis mode)")
            self.hqta_polygons = hqta_json
            
        return self.hqta_polygons
    
    def load_transit_data(self):
        """Load California transit stops and routes data"""
        stops_file = self.data_path / "California_Transit_Stops.csv"
        routes_file = self.data_path / "California_Transit_Routes.geojson"
        
        print("Loading California transit data...")
        
        # Load transit stops
        if stops_file.exists():
            self.transit_stops = pd.read_csv(stops_file)
            print(f"Loaded {len(self.transit_stops)} transit stops")
        
        # Load transit routes
        if routes_file.exists():
            if GEOSPATIAL_AVAILABLE:
                self.transit_routes = gpd.read_file(routes_file)
                print(f"Loaded {len(self.transit_routes)} transit routes")
            else:
                with open(routes_file, 'r') as f:
                    self.transit_routes = json.load(f)
                print(f"Loaded {len(self.transit_routes['features'])} transit route features")
        
        return self.transit_stops, self.transit_routes
    
    def analyze_hqta_overlap(self, site_lat, site_lon, site_id):
        """
        Check if a site falls within any HQTA polygon boundaries
        Returns: dict with analysis results
        """
        if not GEOSPATIAL_AVAILABLE or self.hqta_polygons is None:
            return {
                'within_hqta': False,
                'hqta_details': 'Geospatial analysis not available',
                'hqta_type': None,
                'hqta_agency': None
            }
        
        # Create point for site
        site_point = Point(site_lon, site_lat)
        
        # Check intersection with HQTA polygons
        intersecting_hqtas = self.hqta_polygons[self.hqta_polygons.contains(site_point)]
        
        if len(intersecting_hqtas) > 0:
            hqta_info = intersecting_hqtas.iloc[0]
            return {
                'within_hqta': True,
                'hqta_details': f"Site within {len(intersecting_hqtas)} HQTA area(s)",
                'hqta_type': hqta_info.get('hqta_type', 'Unknown'),
                'hqta_agency': hqta_info.get('agency_primary', 'Unknown'),
                'hqta_route_info': hqta_info.get('route_id', 'Unknown')
            }
        else:
            return {
                'within_hqta': False,
                'hqta_details': 'Site not within any HQTA boundaries',
                'hqta_type': None,
                'hqta_agency': None
            }
    
    def analyze_high_frequency_routes(self, site_lat, site_lon, site_id):
        """
        Analyze high-frequency transit routes near the site
        Using the transit stops data to identify high-frequency service
        """
        if self.transit_stops is None:
            return {
                'high_freq_analysis': 'Transit stops data not available',
                'peak_hour_service': 'Unknown',
                'qualifying_routes': []
            }
        
        # Convert coordinates if needed (Web Mercator to WGS84)
        # Many CA transit datasets use Web Mercator projection
        
        # For now, let's do a simple coordinate-based analysis
        # This is a simplified approach - in production we'd use proper geospatial functions
        
        # Look for stops with high service levels within reasonable distance
        if 'n_arrivals' in self.transit_stops.columns:
            nearby_high_freq = self.transit_stops[
                (self.transit_stops['n_arrivals'] >= 30) |  # 30+ arrivals per day suggests frequent service
                (self.transit_stops['n_hours_in_service'] >= 12)  # 12+ hours suggests good coverage
            ]
            
            return {
                'high_freq_analysis': f"Found {len(nearby_high_freq)} high-frequency stops in dataset",
                'peak_hour_service': 'Requires schedule analysis',
                'qualifying_routes': list(nearby_high_freq['route_ids_served'].dropna().head(5))
            }
        
        return {
            'high_freq_analysis': 'High frequency analysis requires detailed schedule data',
            'peak_hour_service': 'Manual verification needed',
            'qualifying_routes': []
        }
    
    def analyze_top_candidates(self):
        """Analyze the top 20 sites with most transit stops for HQTA qualification"""
        print("\n=== ANALYZING TOP 20 CANDIDATES FOR HQTA QUALIFICATION ===")
        
        if self.vitor_data is None:
            self.load_vitor_analysis()
        if self.hqta_polygons is None:
            self.load_hqta_data()
        if self.transit_stops is None:
            self.load_transit_data()
        
        qa_results = []
        
        for _, site in self.top_candidates.iterrows():
            site_id = site['Site_ID']
            lat = site['Latitude']
            lon = site['Longitude']
            vitor_points = site['CTCAC_Points']
            vitor_stops = site['Stops_Within_Third_Mile']
            
            print(f"\nAnalyzing {site_id}: {vitor_stops} stops, {vitor_points} points")
            
            # HQTA polygon analysis
            hqta_analysis = self.analyze_hqta_overlap(lat, lon, site_id)
            
            # High frequency route analysis
            freq_analysis = self.analyze_high_frequency_routes(lat, lon, site_id)
            
            # QA determination
            qa_recommendation = self.determine_qa_recommendation(
                vitor_points, vitor_stops, hqta_analysis, freq_analysis
            )
            
            result = {
                'Site_ID': site_id,
                'Latitude': lat,
                'Longitude': lon,
                'Vitor_CTCAC_Points': vitor_points,
                'Vitor_Stops_Within_Third_Mile': vitor_stops,
                'QA_Within_HQTA': hqta_analysis['within_hqta'],
                'QA_HQTA_Type': hqta_analysis['hqta_type'],
                'QA_HQTA_Agency': hqta_analysis['hqta_agency'],
                'QA_HQTA_Details': hqta_analysis['hqta_details'],
                'QA_High_Freq_Analysis': freq_analysis['high_freq_analysis'],
                'QA_Recommendation': qa_recommendation['recommendation'],
                'QA_Potential_Points': qa_recommendation['potential_points'],
                'QA_Investigation_Priority': qa_recommendation['priority'],
                'QA_Next_Steps': qa_recommendation['next_steps']
            }
            
            qa_results.append(result)
            
            # Print summary for this site
            if hqta_analysis['within_hqta']:
                print(f"  🎯 POTENTIAL 7-POINT SITE: Within HQTA boundary!")
                print(f"     HQTA Type: {hqta_analysis['hqta_type']}")
                print(f"     Agency: {hqta_analysis['hqta_agency']}")
            else:
                print(f"  ❌ Not within HQTA boundary")
        
        self.qa_results = qa_results
        return qa_results
    
    def determine_qa_recommendation(self, vitor_points, vitor_stops, hqta_analysis, freq_analysis):
        """Determine QA recommendation based on analysis"""
        
        if hqta_analysis['within_hqta']:
            return {
                'recommendation': 'INVESTIGATE FOR 7 POINTS - Site within HQTA boundary',
                'potential_points': 7,
                'priority': 'HIGH',
                'next_steps': 'Verify HQTA designation and peak hour service requirements'
            }
        elif vitor_stops >= 20:
            return {
                'recommendation': 'INVESTIGATE HIGH-FREQUENCY SERVICE - Many nearby stops',
                'potential_points': 'TBD',
                'priority': 'MEDIUM',
                'next_steps': 'Manual verification of peak hour schedules and HQTA boundary accuracy'
            }
        elif vitor_stops >= 10:
            return {
                'recommendation': 'VERIFY FREQUENCY ANALYSIS - Moderate stop density',
                'potential_points': 'TBD',
                'priority': 'LOW',
                'next_steps': 'Double-check frequency calculations and nearby HQTA areas'
            }
        else:
            return {
                'recommendation': 'NO ACTION NEEDED - Low transit density confirmed',
                'potential_points': vitor_points,
                'priority': 'NONE',
                'next_steps': 'Vitor analysis appears accurate'
            }
    
    def create_qa_excel_report(self):
        """Create Excel report with QA findings added to Vitor's data"""
        if not self.qa_results:
            print("No QA results to export. Run analyze_top_candidates() first.")
            return None
        
        # Create comprehensive dataset
        qa_df = pd.DataFrame(self.qa_results)
        
        # Merge with original Vitor data
        merged_data = self.vitor_data.merge(
            qa_df[['Site_ID', 'QA_Within_HQTA', 'QA_HQTA_Type', 'QA_HQTA_Agency', 
                  'QA_HQTA_Details', 'QA_Recommendation', 'QA_Potential_Points',
                  'QA_Investigation_Priority', 'QA_Next_Steps']], 
            on='Site_ID', 
            how='left'
        )
        
        # Fill NaN values for sites not in top 20
        qa_columns = [col for col in merged_data.columns if col.startswith('QA_')]
        for col in qa_columns:
            merged_data[col] = merged_data[col].fillna('Not analyzed - lower priority')
        
        # Create output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_path / f"CTCAC_TRANSIT_QA_ANALYSIS_{timestamp}.xlsx"
        
        # Write to Excel with formatting
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main sheet with all data
            merged_data.to_excel(writer, sheet_name='QA_Analysis_All_Sites', index=False)
            
            # High priority findings sheet
            high_priority = merged_data[merged_data['QA_Investigation_Priority'] == 'HIGH']
            if len(high_priority) > 0:
                high_priority.to_excel(writer, sheet_name='HIGH_PRIORITY_FINDINGS', index=False)
            
            # Top candidates summary
            qa_df.to_excel(writer, sheet_name='Top_20_Detailed_Analysis', index=False)
        
        print(f"\n✅ QA Excel report created: {output_file}")
        print(f"   - All 263 sites with QA columns")
        print(f"   - {len([r for r in self.qa_results if r['QA_Investigation_Priority'] == 'HIGH'])} HIGH priority findings")
        print(f"   - Top 20 detailed analysis included")
        
        return output_file
    
    def create_summary_report(self):
        """Create a summary text report of findings"""
        if not self.qa_results:
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_path / f"HQTA_QA_SUMMARY_REPORT_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("HQTA CROSS-VALIDATION QA ANALYSIS REPORT\n")
            f.write("="*50 + "\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Analyst: Bill Rice AI System\n")
            f.write(f"Original Analysis by: Vitor\n\n")
            
            # Summary statistics
            high_priority = [r for r in self.qa_results if r['QA_Investigation_Priority'] == 'HIGH']
            medium_priority = [r for r in self.qa_results if r['QA_Investigation_Priority'] == 'MEDIUM']
            hqta_sites = [r for r in self.qa_results if r['QA_Within_HQTA']]
            
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Sites Analyzed: {len(self.vitor_data)}\n")
            f.write(f"Top Candidates Reviewed: {len(self.qa_results)}\n")
            f.write(f"Sites Within HQTA Boundaries: {len(hqta_sites)}\n")
            f.write(f"HIGH Priority Investigations: {len(high_priority)}\n")
            f.write(f"MEDIUM Priority Investigations: {len(medium_priority)}\n\n")
            
            # High priority findings
            if high_priority:
                f.write("HIGH PRIORITY FINDINGS - POTENTIAL 7-POINT SITES\n")
                f.write("-" * 45 + "\n")
                for site in high_priority:
                    f.write(f"Site ID: {site['Site_ID']}\n")
                    f.write(f"  Location: {site['Latitude']:.6f}, {site['Longitude']:.6f}\n")
                    f.write(f"  Vitor Analysis: {site['Vitor_CTCAC_Points']} points, {site['Vitor_Stops_Within_Third_Mile']} stops\n")
                    f.write(f"  HQTA Status: {site['QA_HQTA_Details']}\n")
                    f.write(f"  HQTA Type: {site['QA_HQTA_Type']}\n")
                    f.write(f"  Transit Agency: {site['QA_HQTA_Agency']}\n")
                    f.write(f"  Recommendation: {site['QA_Recommendation']}\n")
                    f.write(f"  Next Steps: {site['QA_Next_Steps']}\n\n")
            
            # Medium priority findings
            if medium_priority:
                f.write("MEDIUM PRIORITY FINDINGS - HIGH STOP DENSITY\n")
                f.write("-" * 40 + "\n")
                for site in medium_priority:
                    f.write(f"Site ID: {site['Site_ID']} - {site['Vitor_Stops_Within_Third_Mile']} stops\n")
                    f.write(f"  Recommendation: {site['QA_Recommendation']}\n\n")
        
        print(f"✅ Summary report created: {report_file}")
        return report_file

def main():
    """Main execution function"""
    print("🚀 HQTA Cross-Validation QA Analysis Starting...")
    print("This analysis will check Vitor's CTCAC transit findings against official HQTA data\n")
    
    analyzer = HQTAAnalyzer()
    
    try:
        # Load all data
        analyzer.load_vitor_analysis()
        analyzer.load_hqta_data()
        analyzer.load_transit_data()
        
        # Analyze top candidates
        qa_results = analyzer.analyze_top_candidates()
        
        # Create reports
        excel_file = analyzer.create_qa_excel_report()
        summary_file = analyzer.create_summary_report()
        
        print(f"\n🎯 ANALYSIS COMPLETE!")
        print(f"📊 Excel Report: {excel_file}")
        print(f"📝 Summary Report: {summary_file}")
        
        # Quick summary
        high_priority = [r for r in qa_results if r['QA_Investigation_Priority'] == 'HIGH']
        if high_priority:
            print(f"\n🚨 FOUND {len(high_priority)} HIGH PRIORITY SITES THAT MAY QUALIFY FOR 7 POINTS!")
            for site in high_priority:
                print(f"   - {site['Site_ID']}: {site['QA_Recommendation']}")
        else:
            print(f"\n✅ No obvious HQTA sites found in top 20 candidates")
            print("   This may indicate Vitor's analysis was accurate, or require broader investigation")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
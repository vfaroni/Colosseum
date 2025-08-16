#!/usr/bin/env python3
"""
CTCAC/HCD Opportunity Areas Checker for Concord Property
Checks if 2451 Olivera Road, Concord, CA is in High or Highest Resource Area
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path
import sys

class CTCACOpportunityChecker:
    def __init__(self):
        self.opportunity_data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/california/CA_CTCAC_2025_Opp_MAP_shapefile")
        self.opportunity_data = None
        self.load_opportunity_data()
    
    def load_opportunity_data(self):
        """Load CTCAC/HCD Opportunity Areas data"""
        print("🗺️  Loading CTCAC/HCD Opportunity Areas data...")
        
        # Try different file options in order of preference
        file_options = [
            "final_opp_2025_public.gpkg",
            "CTCAC_Opportunity_Areas_SoCal_2025_LATEST.geojson",
            "CTCAC_Opportunity_Areas_SoCal_2025.geojson"
        ]
        
        for filename in file_options:
            filepath = self.opportunity_data_path / filename
            if filepath.exists():
                try:
                    print(f"📁 Trying to load: {filepath}")
                    self.opportunity_data = gpd.read_file(filepath)
                    
                    # Ensure proper CRS
                    if self.opportunity_data.crs != 'EPSG:4326':
                        self.opportunity_data = self.opportunity_data.to_crs('EPSG:4326')
                    
                    print(f"✅ Successfully loaded opportunity data: {len(self.opportunity_data)} areas")
                    print(f"   Columns: {list(self.opportunity_data.columns)}")
                    
                    # Show sample of resource categories
                    if 'resourcecat' in self.opportunity_data.columns:
                        resource_counts = self.opportunity_data['resourcecat'].value_counts()
                        print(f"   Resource Categories:")
                        for category, count in resource_counts.items():
                            print(f"     {category}: {count} areas")
                    elif 'Resource' in self.opportunity_data.columns:
                        resource_counts = self.opportunity_data['Resource'].value_counts()
                        print(f"   Resource Categories:")
                        for category, count in resource_counts.items():
                            print(f"     {category}: {count} areas")
                    
                    return True
                    
                except Exception as e:
                    print(f"⚠️  Error loading {filename}: {e}")
                    continue
            else:
                print(f"❌ File not found: {filepath}")
        
        print("❌ Could not load any opportunity data files")
        return False
    
    def check_opportunity_status(self, latitude, longitude):
        """Check if coordinates are in High or Highest Resource Area"""
        if self.opportunity_data is None:
            return {"error": "No opportunity data loaded"}
        
        print(f"🔍 Checking opportunity status for coordinates: {latitude}, {longitude}")
        
        point = Point(longitude, latitude)
        
        try:
            # Find intersecting opportunity areas
            intersecting = self.opportunity_data[self.opportunity_data.contains(point)]
            
            result = {
                "latitude": latitude,
                "longitude": longitude,
                "in_opportunity_area": False,
                "resource_category": None,
                "area_name": None,
                "tract_geoid": None,
                "ctcac_scoring_eligible": False,
                "scoring_details": {}
            }
            
            if not intersecting.empty:
                area_row = intersecting.iloc[0]
                result["in_opportunity_area"] = True
                
                # Try different column names for resource category
                resource_col = None
                for col in ['oppcat', 'resourcecat', 'Resource', 'resource_category', 'opp_level']:
                    if col in area_row.index:
                        resource_col = col
                        break
                
                if resource_col:
                    resource_category = area_row[resource_col]
                    result["resource_category"] = resource_category
                    
                    # Check CTCAC scoring eligibility
                    if resource_category in ['Highest Resource', 'High Resource']:
                        result["ctcac_scoring_eligible"] = True
                        
                        # CTCAC scoring details
                        if resource_category == 'Highest Resource':
                            result["scoring_details"] = {
                                "large_family_bonus": "20 percentage points",
                                "site_amenities_points": "8 points",
                                "total_possible_bonus": "Up to 28 point advantage"
                            }
                        elif resource_category == 'High Resource':
                            result["scoring_details"] = {
                                "large_family_bonus": "10 percentage points", 
                                "site_amenities_points": "8 points",
                                "total_possible_bonus": "Up to 18 point advantage"
                            }
                    
                    print(f"✅ Location is in: {resource_category}")
                    if result["ctcac_scoring_eligible"]:
                        print(f"🏆 CTCAC Scoring Eligible!")
                        for key, value in result["scoring_details"].items():
                            print(f"   {key.replace('_', ' ').title()}: {value}")
                else:
                    result["resource_category"] = "Unknown (column not found)"
                    print(f"⚠️  Could not determine resource category")
                
                # Get area name if available
                name_cols = ['name', 'area_name', 'tract_name', 'geoid']
                for col in name_cols:
                    if col in area_row.index and pd.notna(area_row[col]):
                        result["area_name"] = str(area_row[col])
                        break
                
                # Get tract GEOID if available
                geoid_cols = ['geoid', 'GEOID', 'tract_geoid', 'TRACT_ID']
                for col in geoid_cols:
                    if col in area_row.index and pd.notna(area_row[col]):
                        result["tract_geoid"] = str(area_row[col])
                        break
                
            else:
                print(f"❌ Location is NOT in any opportunity area")
                result["resource_category"] = "Not in Opportunity Area"
            
            return result
            
        except Exception as e:
            print(f"⚠️  Error checking opportunity status: {e}")
            return {"error": str(e)}
    
    def display_results(self, result):
        """Display formatted results"""
        print(f"\n📋 CTCAC/HCD OPPORTUNITY AREAS ANALYSIS")
        print("=" * 60)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print(f"📍 Location: {result['latitude']}, {result['longitude']}")
        print(f"Opportunity Area Status: {'✅ YES' if result['in_opportunity_area'] else '❌ NO'}")
        
        if result['in_opportunity_area']:
            print(f"Resource Category: {result['resource_category']}")
            
            if result['area_name']:
                print(f"Area Name: {result['area_name']}")
            
            if result['tract_geoid']:
                print(f"Tract GEOID: {result['tract_geoid']}")
            
            print(f"CTCAC Scoring Eligible: {'✅ YES' if result['ctcac_scoring_eligible'] else '❌ NO'}")
            
            if result['ctcac_scoring_eligible']:
                print(f"\n🏆 CTCAC SCORING BENEFITS:")
                for key, value in result['scoring_details'].items():
                    print(f"   {key.replace('_', ' ').title()}: {value}")
            else:
                print(f"\n⚠️  No CTCAC scoring benefits (not High/Highest Resource)")
        
        return result

def check_concord_opportunity_status():
    """Check opportunity status for Concord property"""
    print("🏠 CTCAC/HCD Opportunity Areas Analysis")
    print("2451 Olivera Road, Concord, CA 94520")
    print("=" * 70)
    
    # Concord coordinates from our earlier analysis
    latitude = 37.9779
    longitude = -122.0312
    
    checker = CTCACOpportunityChecker()
    
    if checker.opportunity_data is None:
        print("❌ Could not load opportunity data")
        return None
    
    result = checker.check_opportunity_status(latitude, longitude)
    return checker.display_results(result)

if __name__ == "__main__":
    check_concord_opportunity_status()
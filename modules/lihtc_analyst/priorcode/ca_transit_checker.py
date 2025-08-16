#!/usr/bin/env python3
"""
California Transit Proximity Checker for CTCAC Scoring
Uses HQTA (High Quality Transit Areas) data and transit stops
Based on December 2024 CTCAC QAP requirements
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path
import numpy as np

class CaliforniaTransitChecker:
    def __init__(self):
        # Paths to transit data
        self.transit_data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/CA Transit Data")
        
        # Load transit datasets
        self.hqta_data = None
        self.transit_stops = None
        self.transit_routes = None
        self.load_transit_data()
    
    def load_transit_data(self):
        """Load California transit datasets"""
        try:
            # Load High Quality Transit Areas (HQTA) shapefile
            hqta_file = self.transit_data_path / "High_Quality_Transit_Areas" / "High_Quality_Transit_Areas.shp"
            if hqta_file.exists():
                print(f"Loading HQTA data from: {hqta_file}")
                self.hqta_data = gpd.read_file(hqta_file)
                if self.hqta_data.crs != 'EPSG:4326':
                    self.hqta_data = self.hqta_data.to_crs('EPSG:4326')
                print(f"✅ Loaded HQTA data: {len(self.hqta_data)} areas")
                print(f"   Columns: {list(self.hqta_data.columns)}")
            else:
                print(f"❌ HQTA file not found: {hqta_file}")
            
            # Load transit stops
            stops_file = self.transit_data_path / "California_Transit_Stops.geojson"
            if stops_file.exists():
                print(f"Loading transit stops from: {stops_file}")
                self.transit_stops = gpd.read_file(stops_file)
                if self.transit_stops.crs != 'EPSG:4326':
                    self.transit_stops = self.transit_stops.to_crs('EPSG:4326')
                print(f"✅ Loaded transit stops: {len(self.transit_stops)} stops")
                print(f"   Columns: {list(self.transit_stops.columns)}")
            else:
                print(f"❌ Transit stops file not found: {stops_file}")
            
            # Load transit routes
            routes_file = self.transit_data_path / "California_Transit_Routes.geojson"
            if routes_file.exists():
                print(f"Loading transit routes from: {routes_file}")
                self.transit_routes = gpd.read_file(routes_file)
                if self.transit_routes.crs != 'EPSG:4326':
                    self.transit_routes = self.transit_routes.to_crs('EPSG:4326')
                print(f"✅ Loaded transit routes: {len(self.transit_routes)} routes")
                print(f"   Columns: {list(self.transit_routes.columns)}")
            else:
                print(f"❌ Transit routes file not found: {routes_file}")
                
        except Exception as e:
            print(f"⚠️ Error loading transit data: {e}")
    
    def meters_to_miles(self, meters):
        """Convert meters to miles"""
        return meters * 0.000621371
    
    def miles_to_meters(self, miles):
        """Convert miles to meters"""
        return miles * 1609.34
    
    def find_nearby_transit(self, latitude, longitude, max_distance_miles=0.5):
        """Find transit stops within specified distance"""
        point = Point(longitude, latitude)
        
        # Convert max distance to degrees (approximate)
        # 1 degree ≈ 69 miles at equator
        max_distance_deg = max_distance_miles / 69.0
        
        nearby_stops = []
        
        if self.transit_stops is not None:
            # Create a buffer around the point
            buffer = point.buffer(max_distance_deg)
            
            # Find intersecting stops
            intersecting = self.transit_stops[self.transit_stops.intersects(buffer)]
            
            for idx, stop in intersecting.iterrows():
                distance_deg = point.distance(stop.geometry)
                distance_miles = distance_deg * 69.0  # Approximate conversion
                
                if distance_miles <= max_distance_miles:
                    stop_info = {
                        'distance_miles': round(distance_miles, 3),
                        'stop_name': stop.get('stop_name', 'Unknown Stop'),
                        'route_info': stop.get('route_short_name', 'Unknown Route'),
                        'stop_type': stop.get('location_type', 'Bus Stop'),
                        'geometry': stop.geometry
                    }
                    nearby_stops.append(stop_info)
        
        # Sort by distance
        nearby_stops.sort(key=lambda x: x['distance_miles'])
        return nearby_stops
    
    def check_hqta_status(self, latitude, longitude):
        """Check if location is within High Quality Transit Area"""
        if self.hqta_data is None:
            return {"in_hqta": False, "hqta_info": None}
        
        point = Point(longitude, latitude)
        
        try:
            hqta_intersects = self.hqta_data[self.hqta_data.contains(point)]
            
            if not hqta_intersects.empty:
                hqta_row = hqta_intersects.iloc[0]
                return {
                    "in_hqta": True,
                    "hqta_info": {
                        "area_name": hqta_row.get('NAME', 'HQTA Area'),
                        "transit_type": hqta_row.get('TRANSIT_TY', 'Mixed Transit'),
                        "agency": hqta_row.get('AGENCY', 'Unknown Agency'),
                        "description": hqta_row.get('DESCRIPTIO', '')
                    }
                }
            else:
                return {"in_hqta": False, "hqta_info": None}
                
        except Exception as e:
            print(f"⚠️ Error checking HQTA status: {e}")
            return {"in_hqta": False, "hqta_info": None}
    
    def evaluate_ctcac_transit_scoring(self, latitude, longitude):
        """Evaluate CTCAC transit scoring for 9% deals based on December 2024 QAP"""
        
        # CTCAC Distance Requirements
        distances = {
            "1/3_mile": 1/3,
            "1/2_mile": 1/2
        }
        
        results = {
            "location": {"latitude": latitude, "longitude": longitude},
            "hqta_status": self.check_hqta_status(latitude, longitude),
            "transit_analysis": {},
            "ctcac_scoring": {
                "9p_eligible_categories": [],
                "4p_bond_note": "4% deals use CDLAC scoring, not CTCAC points"
            }
        }
        
        # Check transit at different distances
        for distance_name, distance_miles in distances.items():
            nearby_transit = self.find_nearby_transit(latitude, longitude, distance_miles)
            results["transit_analysis"][distance_name] = {
                "distance_miles": distance_miles,
                "transit_stops_found": len(nearby_transit),
                "nearest_stops": nearby_transit[:5]  # Top 5 nearest
            }
        
        # Evaluate 9% scoring categories
        one_third_transit = results["transit_analysis"]["1/3_mile"]["transit_stops_found"]
        one_half_transit = results["transit_analysis"]["1/2_mile"]["transit_stops_found"]
        is_hqta = results["hqta_status"]["in_hqta"]
        
        # CTCAC 9% Transit Scoring Categories
        if one_third_transit > 0:
            if is_hqta:
                results["ctcac_scoring"]["9p_eligible_categories"].append({
                    "category": "High-Quality Transit + High Density",
                    "distance": "1/3 mile",
                    "requirements": "HQTA + >25 units/acre + 30min peak service",
                    "status": "Potentially Eligible (check service frequency & density)",
                    "bonus": "Highest scoring option"
                })
                results["ctcac_scoring"]["9p_eligible_categories"].append({
                    "category": "High-Quality Transit (Standard)",
                    "distance": "1/3 mile", 
                    "requirements": "HQTA + 30min peak service",
                    "status": "Potentially Eligible (check service frequency)",
                    "bonus": "Good scoring option"
                })
            else:
                results["ctcac_scoring"]["9p_eligible_categories"].append({
                    "category": "Any Transit (Rural Set-Aside)",
                    "distance": "1/3 mile",
                    "requirements": "Any transit stop (no service frequency requirement)",
                    "status": "Eligible",
                    "bonus": "Rural projects only"
                })
        
        if one_half_transit > 0:
            if is_hqta:
                results["ctcac_scoring"]["9p_eligible_categories"].append({
                    "category": "High-Quality Transit (Extended Distance)",
                    "distance": "1/2 mile",
                    "requirements": "HQTA + 30min peak service",
                    "status": "Potentially Eligible (check service frequency)",
                    "bonus": "Lower scoring than 1/3 mile options"
                })
            else:
                results["ctcac_scoring"]["9p_eligible_categories"].append({
                    "category": "Any Transit (Extended Distance)",
                    "distance": "1/2 mile",
                    "requirements": "Any transit stop (no service frequency requirement)",
                    "status": "Eligible", 
                    "bonus": "Lowest transit scoring option"
                })
        
        if len(results["ctcac_scoring"]["9p_eligible_categories"]) == 0:
            results["ctcac_scoring"]["9p_eligible_categories"].append({
                "category": "No Transit Access",
                "distance": "N/A",
                "requirements": "N/A",
                "status": "No transit points available",
                "bonus": "Consider other site amenity categories"
            })
        
        return results

def check_transit_for_location(lat, lon):
    """Check transit scoring for a single location"""
    print(f"\n🚊 Checking CTCAC Transit Scoring for coordinates: {lat}, {lon}")
    print("=" * 80)
    
    checker = CaliforniaTransitChecker()
    results = checker.evaluate_ctcac_transit_scoring(lat, lon)
    
    # Display HQTA Status
    print(f"\n📍 HIGH QUALITY TRANSIT AREA (HQTA) STATUS:")
    if results["hqta_status"]["in_hqta"]:
        print(f"   ✅ Location IS within HQTA")
        hqta_info = results["hqta_status"]["hqta_info"]
        print(f"   📋 Area: {hqta_info['area_name']}")
        print(f"   🚌 Transit Type: {hqta_info['transit_type']}")
        print(f"   🏢 Agency: {hqta_info['agency']}")
    else:
        print(f"   ❌ Location is NOT within HQTA")
    
    # Display Transit Analysis
    print(f"\n🚇 TRANSIT PROXIMITY ANALYSIS:")
    for distance_name, analysis in results["transit_analysis"].items():
        print(f"\n   📏 Within {analysis['distance_miles']} miles ({distance_name}):")
        print(f"      Transit Stops Found: {analysis['transit_stops_found']}")
        
        if analysis['nearest_stops']:
            print(f"      Nearest Stops:")
            for i, stop in enumerate(analysis['nearest_stops'][:3], 1):
                print(f"        {i}. {stop['stop_name']} - {stop['distance_miles']} miles")
                print(f"           Route: {stop['route_info']} | Type: {stop['stop_type']}")
    
    # Display CTCAC Scoring
    print(f"\n🏆 CTCAC SCORING ANALYSIS (December 2024 QAP):")
    print(f"\n   📋 4% Tax-Exempt Bond Deals:")
    print(f"      {results['ctcac_scoring']['4p_bond_note']}")
    
    print(f"\n   🏅 9% Competitive Deal Categories:")
    for i, category in enumerate(results["ctcac_scoring"]["9p_eligible_categories"], 1):
        print(f"      {i}. {category['category']}")
        print(f"         Distance: {category['distance']}")
        print(f"         Requirements: {category['requirements']}")
        print(f"         Status: {category['status']}")
        print(f"         Note: {category['bonus']}")
        print()
    
    return results

if __name__ == "__main__":
    # Test with the provided coordinates
    # 38°47'47.1"N 121°13'57.6"W = 38.796417, -121.232667
    lat = 38.796417
    lon = -121.232667
    
    results = check_transit_for_location(lat, lon)
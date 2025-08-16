#!/usr/bin/env python3
"""
CTCAC Comprehensive Site Amenities Analyzer
San Jacinto Vista II - 202 E. Jarvis St., Perris, CA 92571

Analyzes ALL CTCAC site amenity categories for maximum scoring:
- Transit (7-3 points)
- Public Park (3-2 points) 
- Public Library (3-2 points)
- Grocery Store/Market (5-1 points)
- Public Schools (3-2 points)
- Medical Clinic/Hospital (3-2 points)
- Pharmacy (2-1 points)
- Highest/High Resource Area (8 points)
- In-unit Internet Service (2-3 points)

Project Details:
- 64 units on 5.26 acres = 12.17 units per acre
- General occupancy (not senior/special needs)
- Target: Maximum 15 points
"""

import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path
import json
import time

class CTCACComprehensiveSiteAnalyzer:
    def __init__(self, address, units, acres):
        self.address = address
        self.units = units
        self.acres = acres
        self.density = units / acres
        self.lat = None
        self.lon = None
        
        # Results storage
        self.analysis_results = {
            'project_info': {
                'address': address,
                'units': units,
                'acres': acres,
                'density': round(self.density, 2),
                'coordinates': None
            },
            'amenity_scores': {
                'transit': {'points': 0, 'category': None, 'details': []},
                'public_park': {'points': 0, 'category': None, 'details': []},
                'public_library': {'points': 0, 'category': None, 'details': []},
                'grocery_store': {'points': 0, 'category': None, 'details': []},
                'public_schools': {'points': 0, 'category': None, 'details': []},
                'medical_clinic': {'points': 0, 'category': None, 'details': []},
                'pharmacy': {'points': 0, 'category': None, 'details': []},
                'high_resource_area': {'points': 0, 'category': None, 'details': []},
                'internet_service': {'points': 0, 'category': None, 'details': []}
            },
            'scoring_strategy': []
        }
        
        # Load data paths
        self.data_paths = {
            'transit_data': Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/CA Transit Data"),
            'opportunity_areas': Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/CTCAC_2025_Opp_MAP_shapefile"),
            'ca_schools': Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/CA Public Schools")
        }

    def geocode_address(self):
        """Geocode the project address"""
        print(f"📍 GEOCODING: {self.address}")
        
        base_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        params = {
            'address': self.address,
            'benchmark': 'Public_AR_Current',
            'format': 'json'
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['result']['addressMatches']:
                match = data['result']['addressMatches'][0]
                coords = match['coordinates']
                self.lat = float(coords['y'])
                self.lon = float(coords['x'])
                self.analysis_results['project_info']['coordinates'] = {
                    'latitude': self.lat,
                    'longitude': self.lon
                }
                print(f"   ✅ Success: {self.lat:.6f}, {self.lon:.6f}")
                return True
            else:
                print(f"   ❌ No geocoding matches found")
                return False
        except Exception as e:
            print(f"   ⚠️ Geocoding error: {e}")
            return False

    def analyze_density_for_transit(self):
        """Check if project qualifies for 7-point high-density transit scoring"""
        print(f"\n🏘️ DENSITY ANALYSIS FOR TRANSIT SCORING:")
        print(f"   Units: {self.units}")
        print(f"   Acres: {self.acres}")
        print(f"   Density: {self.density:.2f} units per acre")
        
        if self.density > 25:
            print(f"   ✅ QUALIFIES for 7-point high-density transit scoring")
            return True
        else:
            print(f"   ❌ Does NOT qualify for 7-point scoring (needs >25 units/acre)")
            print(f"   📋 Still eligible for 6-point, 5-point, 4-point, and 3-point categories")
            return False

    def find_google_maps_measurement_locations(self):
        """Identify key locations for Google Maps walking distance measurement"""
        measurement_plan = {
            'origin': self.address,
            'destinations': {
                'transit_stops': [],
                'public_parks': [],
                'libraries': [],
                'grocery_stores': [],
                'schools': [],
                'medical_facilities': [],
                'pharmacies': []
            }
        }
        
        # For now, provide framework for manual Google Maps research
        print(f"\n📱 GOOGLE MAPS MEASUREMENT PLAN:")
        print(f"   🏠 FROM: {self.address}")
        print(f"   📍 Coordinates: {self.lat:.6f}, {self.lon:.6f}")
        print(f"\n   🎯 RESEARCH NEEDED: Use Google Maps to find and measure walking distances to:")
        
        categories = [
            ("🚌 Transit Stops", "Bus stops, rail stations within 0.5 miles"),
            ("🏞️ Public Parks", "City/county parks within 0.75 miles"), 
            ("📚 Public Libraries", "Public libraries within 1 mile"),
            ("🛒 Grocery Stores", "Supermarkets 25,000+ sq ft within 1.5 miles, Markets 5,000+ sq ft within 0.5 miles"),
            ("🏫 Public Schools", "Elementary (1 mile), Middle (1 mile), High (1.5 miles), Adult Ed/Community College (1 mile)"),
            ("🏥 Medical Facilities", "Clinics with 40+ hrs/week, Hospitals within 1 mile"),
            ("💊 Pharmacies", "Pharmacies within 1 mile")
        ]
        
        for category, description in categories:
            print(f"      {category}: {description}")
        
        return measurement_plan

    def check_opportunity_areas(self):
        """Check if site is in CTCAC/HCD Highest or High Resource Area"""
        print(f"\n🗺️ OPPORTUNITY AREA ANALYSIS:")
        
        try:
            # Look for opportunity area files
            opp_files = list(self.data_paths['opportunity_areas'].glob("*.geojson"))
            if not opp_files:
                opp_files = list(self.data_paths['opportunity_areas'].glob("*.gpkg"))
            
            if opp_files:
                print(f"   📂 Found opportunity area files: {len(opp_files)}")
                for file in opp_files:
                    print(f"      • {file.name}")
                
                # Try to load and analyze the most relevant file
                socal_files = [f for f in opp_files if 'SoCal' in f.name or 'socal' in f.name.lower()]
                if socal_files:
                    opp_file = socal_files[0]
                    print(f"   🎯 Using: {opp_file.name}")
                    
                    try:
                        opp_data = gpd.read_file(opp_file)
                        if opp_data.crs != 'EPSG:4326':
                            opp_data = opp_data.to_crs('EPSG:4326')
                        
                        project_point = Point(self.lon, self.lat)
                        intersects = opp_data[opp_data.contains(project_point)]
                        
                        if not intersects.empty:
                            resource_level = intersects.iloc[0].get('resource_level', 'Unknown')
                            print(f"   ✅ SITE IS IN OPPORTUNITY AREA: {resource_level}")
                            
                            if resource_level.lower() in ['highest', 'high']:
                                self.analysis_results['amenity_scores']['high_resource_area'] = {
                                    'points': 8,
                                    'category': 'Highest or High Resource Area',
                                    'details': [f"Located in {resource_level} Resource Area"]
                                }
                                return True
                        else:
                            print(f"   ❌ Site is NOT in a Highest or High Resource Area")
                            
                    except Exception as e:
                        print(f"   ⚠️ Error analyzing opportunity data: {e}")
                        
            else:
                print(f"   ❌ No opportunity area files found in {self.data_paths['opportunity_areas']}")
                
        except Exception as e:
            print(f"   ⚠️ Error checking opportunity areas: {e}")
        
        return False

    def generate_scoring_strategy(self):
        """Generate optimal scoring strategy to reach 15 points"""
        print(f"\n🏆 CTCAC SCORING STRATEGY ANALYSIS:")
        
        total_available_points = sum(score['points'] for score in self.analysis_results['amenity_scores'].values())
        
        print(f"   🎯 Target: 15 points (maximum)")
        print(f"   📊 Currently Identified: {total_available_points} points")
        
        # Priority scoring categories (highest points first)
        priority_categories = [
            ("high_resource_area", 8, "Highest/High Resource Area - VERIFY CTCAC/HCD Map"),
            ("transit", 7, "Transit within 1/3 mile + >25 units/acre + 30min service"),
            ("transit", 6, "Transit within 1/3 mile + 30min service"),
            ("transit", 5, "Transit within 1/2 mile + 30min service"),
            ("grocery_store", 5, "Supermarket 25,000+ sq ft within 1/2 mile"),
            ("transit", 4, "Transit within 1/3 mile (any frequency)"),
            ("grocery_store", 4, "Supermarket 25,000+ sq ft within 1 mile OR Market 5,000+ sq ft within 1/4 mile"),
            ("public_park", 3, "Public park within 1/2 mile"),
            ("public_library", 3, "Public library within 1/2 mile"),
            ("public_schools", 3, "Schools within distance + attendance area"),
            ("medical_clinic", 3, "Medical clinic/hospital within 1/2 mile"),
            ("grocery_store", 3, "Supermarket 25,000+ sq ft within 1.5 miles OR Market 5,000+ sq ft within 1/2 mile"),
            ("transit", 3, "Transit within 1/2 mile (any frequency)"),
            ("internet_service", 3, "High-speed internet (Rural set-aside only)"),
            ("pharmacy", 2, "Pharmacy within 1/2 mile"),
            ("internet_service", 2, "High-speed internet in each unit"),
            ("public_park", 2, "Public park within 3/4 mile"),
            ("public_library", 2, "Public library within 1 mile"),
            ("public_schools", 2, "Schools within extended distance + attendance area"),
            ("medical_clinic", 2, "Medical clinic/hospital within 1 mile"),
            ("grocery_store", 2, "Farmers market within 1/2 mile"),
            ("pharmacy", 1, "Pharmacy within 1 mile"),
            ("grocery_store", 1, "Farmers market within 1 mile")
        ]
        
        print(f"\n   📋 RECOMMENDED RESEARCH PRIORITIES:")
        print(f"   (Focus on highest-point categories first)")
        
        points_needed = 15
        for category, points, description in priority_categories:
            if points_needed > 0:
                print(f"   • {points} pts: {description}")
                points_needed -= points
                if points_needed <= 0:
                    break
        
        print(f"\n   🎯 KEY MEASUREMENTS NEEDED:")
        print(f"   1. Google Maps walking distances to ALL amenities")
        print(f"   2. Transit service frequency verification (30min peak hours)")
        print(f"   3. Grocery store square footage verification")
        print(f"   4. School district attendance area verification")
        print(f"   5. Medical facility staffing verification (40+ hrs/week)")
        
        return priority_categories

    def export_measurement_checklist(self):
        """Export a detailed measurement checklist for field work"""
        checklist = {
            'project_info': self.analysis_results['project_info'],
            'measurement_requirements': {
                'transit': {
                    'distances': ['1/3 mile = 1,760 feet', '1/2 mile = 2,640 feet'],
                    'service_requirements': '30 minutes during 7-9am, 4-6pm Monday-Friday',
                    'types': 'Bus rapid transit, light rail, commuter rail, ferry, bus station, bus stop'
                },
                'public_park': {
                    'distances': ['1/2 mile = 2,640 feet', '3/4 mile = 3,960 feet'],
                    'requirements': 'Accessible to general public, not school grounds unless joint-use agreement'
                },
                'public_library': {
                    'distances': ['1/2 mile = 2,640 feet', '1 mile = 5,280 feet'],
                    'requirements': 'Book-lending, inter-branch lending capability'
                },
                'grocery_store': {
                    'distances': ['1/4 mile = 1,320 feet', '1/2 mile = 2,640 feet', '1 mile = 5,280 feet', '1.5 miles = 7,920 feet'],
                    'requirements': 'Supermarket: 25,000+ sq ft, Neighborhood Market: 5,000+ sq ft, Fresh meat & produce'
                },
                'public_schools': {
                    'distances': ['Elementary: 1/4 mile', 'Middle: 1/2 mile', 'High: 1 mile', 'Adult Ed/Community College: 1 mile'],
                    'requirements': 'Must be within school attendance area, need 25%+ 3-bedroom units for points'
                },
                'medical_clinic': {
                    'distances': ['1/2 mile = 2,640 feet', '1 mile = 5,280 feet'],
                    'requirements': 'Physician/PA/NP on-site minimum 40 hours/week, or hospital'
                },
                'pharmacy': {
                    'distances': ['1/2 mile = 2,640 feet', '1 mile = 5,280 feet'],
                    'requirements': 'Can be combined with other amenities'
                }
            }
        }
        
        return checklist

    def run_comprehensive_analysis(self):
        """Run the complete CTCAC site amenities analysis"""
        print("🏠 CTCAC COMPREHENSIVE SITE AMENITIES ANALYSIS")
        print("=" * 70)
        print(f"Project: San Jacinto Vista II")
        print(f"Address: {self.address}")
        print(f"Units: {self.units} | Acres: {self.acres} | Density: {self.density:.2f} units/acre")
        
        # Step 1: Geocode address
        if not self.geocode_address():
            print("❌ Cannot proceed without geocoded coordinates")
            return None
        
        return self.run_comprehensive_analysis_with_coordinates()
    
    def run_comprehensive_analysis_with_coordinates(self):
        """Run analysis assuming coordinates are already set"""
        
        # Step 2: Analyze density for transit scoring
        high_density_eligible = self.analyze_density_for_transit()
        
        # Step 3: Check opportunity areas
        self.check_opportunity_areas()
        
        # Step 4: Generate measurement plan
        measurement_plan = self.find_google_maps_measurement_locations()
        
        # Step 5: Generate scoring strategy
        self.generate_scoring_strategy()
        
        # Step 6: Export checklist
        checklist = self.export_measurement_checklist()
        
        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Use Google Maps to measure walking distances to nearby amenities")
        print(f"   2. Verify service frequencies and facility requirements")
        print(f"   3. Check CTCAC/HCD Opportunity Area Map status")
        print(f"   4. Document findings with photos and contact information")
        print(f"   5. Select optimal combination of amenities for 15 points")
        
        return {
            'analysis_results': self.analysis_results,
            'measurement_plan': measurement_plan,
            'checklist': checklist
        }

def main():
    # San Jacinto Vista II project details
    address = "202 E. Jarvis St., Perris, CA 92571"
    units = 64
    acres = 5.26
    
    analyzer = CTCACComprehensiveSiteAnalyzer(address, units, acres)
    
    # Manual coordinates for Perris, CA area (approximate)
    # User should verify exact coordinates using Google Maps
    analyzer.lat = 33.7825  # Approximate latitude for Perris
    analyzer.lon = -117.2286  # Approximate longitude for Perris
    analyzer.analysis_results['project_info']['coordinates'] = {
        'latitude': analyzer.lat,
        'longitude': analyzer.lon,
        'note': 'Approximate coordinates - verify exact location using Google Maps'
    }
    
    print(f"📍 Using approximate coordinates for Perris area: {analyzer.lat:.6f}, {analyzer.lon:.6f}")
    print(f"   ⚠️ IMPORTANT: Verify exact project coordinates using Google Maps")
    
    # Run analysis with manual coordinates
    results = analyzer.run_comprehensive_analysis_with_coordinates()
    
    if results:
        print(f"\n✅ Analysis complete! Use the measurement plan to gather field data.")
        return results
    else:
        print(f"\n❌ Analysis failed. Check data files.")
        return None

if __name__ == "__main__":
    results = main()
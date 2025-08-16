#!/usr/bin/env python3
"""
Apply fixes to Enhanced Texas Analyzer and test with problematic addresses
"""

import sys
import pandas as pd
from shapely.geometry import Point
import types

sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code')

from enhanced_texas_analyzer_st import EnhancedTexasAnalyzer

def fixed_get_nearby_lihtc_projects(self, target_point: Point, radius_miles: float):
    """FIXED competition analysis method"""
    
    if self.tdhca_data is None:
        print(f"    ⚠️ No TDHCA data available")
        return []
    
    nearby_projects = []
    target_coords = (target_point.y, target_point.x)  # (lat, lon)
    
    print(f"    🔍 Searching {len(self.tdhca_data)} projects within {radius_miles} miles...")
    
    valid_coords = 0
    projects_found = 0
    
    for idx, project in self.tdhca_data.iterrows():
        try:
            lat = project.get('Latitude11')
            lon = project.get('Longitude11')
            
            # Skip if no coordinates
            if pd.isna(lat) or pd.isna(lon):
                continue
            
            # Convert to float
            try:
                lat_val = float(lat)
                lon_val = float(lon)
            except:
                continue
            
            # Basic Texas bounds check
            if not (25.0 <= lat_val <= 37.0 and -107.0 <= lon_val <= -93.0):
                continue
            
            valid_coords += 1
            project_coords = (lat_val, lon_val)
            
            # Calculate distance using geopy if available, else simple calculation
            try:
                from geopy.distance import geodesic
                distance_miles = geodesic(target_coords, project_coords).miles
            except ImportError:
                # Simple distance calculation if geopy not available
                import math
                lat1, lon1 = target_coords
                lat2, lon2 = project_coords
                lat_diff = lat2 - lat1
                lon_diff = lon2 - lon1
                distance_km = ((lat_diff * 111.32) ** 2 + (lon_diff * 111.32 * math.cos(math.radians(lat1))) ** 2) ** 0.5
                distance_miles = distance_km * 0.621371
            
            if distance_miles <= radius_miles:
                projects_found += 1
                
                # Extract project data
                project_name = str(project.get('Development Name', 'Unknown')).strip()
                if project_name in ['Unknown', 'nan', 'None', '']:
                    project_name = 'Unknown'
                
                total_units = 0
                if pd.notna(project.get('Total Units')):
                    try:
                        total_units = int(float(project.get('Total Units', 0)))
                    except:
                        total_units = 0
                
                year_placed = 0
                year_display = "N/A"
                if pd.notna(project.get('Year')):
                    try:
                        full_year = int(float(project.get('Year', 0)))
                        if 1950 <= full_year <= 2030:
                            year_placed = full_year
                            year_display = f"'{str(full_year)[-2:]}"
                    except:
                        pass
                
                project_info = {
                    'distance': round(distance_miles, 2),
                    'project_name': project_name,
                    'total_units': total_units,
                    'year_placed': year_placed,
                    'year_display': year_display,
                    'city': str(project.get('Project City', 'Unknown')).strip(),
                    'coordinates': project_coords
                }
                nearby_projects.append(project_info)
        
        except Exception as e:
            continue
    
    print(f"    📊 Results: {valid_coords} valid coordinates, {projects_found} within radius")
    
    # Sort by distance
    nearby_projects.sort(key=lambda x: x['distance'])
    return nearby_projects

def enhanced_geocode_address_fixed(self, address: str):
    """Enhanced geocoding with better address variations"""
    
    print(f"🔍 Enhanced geocoding: {address}")
    
    # Create comprehensive variations
    variations = [address]
    
    # Add Texas if missing
    if ', TX' not in address.upper():
        variations.append(f"{address}, TX")
        variations.append(f"{address}, Texas")
    
    # Specific fixes for known failing addresses
    if "Old Lytton Springs" in address:
        base = address.split("Old Lytton Springs")[0].strip()
        city_part = "Lockhart, TX" if "Lockhart" not in address else ""
        variations.extend([
            f"{base} Old Lytton Springs Road, {city_part}".strip(),
            f"{base} Lytton Springs Road, {city_part}".strip(),
            f"{base} Lytton Springs Rd, {city_part}".strip(),
            f"{base} Old Lytton Rd, {city_part}".strip()
        ])
    
    if "Hagerson" in address and "Sugar Land" in address:
        number = address.split()[0]
        variations.extend([
            f"{number} Hagerson St, Sugar Land, TX",
            f"{number} Hagerson Street, Sugar Land, TX",
            f"{number} Hagerson Ave, Sugar Land, TX",
            f"{number} Hagerson Avenue, Sugar Land, TX",
            f"{number} Hagerson Dr, Sugar Land, TX",
            f"{number} Hagerson Drive, Sugar Land, TX"
        ])
    
    # Remove empty strings and duplicates
    clean_variations = []
    for var in variations:
        var = var.strip().replace("  ", " ")
        if var and var not in clean_variations:
            clean_variations.append(var)
    
    # Try each variation
    for i, variation in enumerate(clean_variations[:8]):  # Limit attempts
        print(f"   Attempt {i+1}: {variation}")
        
        try:
            import requests
            import time
            
            url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
            params = {
                'address': variation,
                'benchmark': 'Public_AR_Current',
                'vintage': 'Current_Current',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('result', {}).get('addressMatches'):
                match = data['result']['addressMatches'][0]
                coords = match['coordinates']
                matched_address = match.get('matchedAddress', variation)
                
                census_tract = None
                if 'geographies' in match:
                    tracts = match['geographies'].get('Census Tracts', [])
                    if tracts:
                        census_tract = tracts[0].get('GEOID')
                
                # Validate coordinates are in Texas
                lat, lon = coords['y'], coords['x']
                if not (25 <= lat <= 37 and -107 <= lon <= -93):
                    print(f"   ⚠️ Coordinates outside Texas")
                    continue
                
                print(f"   ✅ SUCCESS!")
                return {
                    "address": address,
                    "matched_address": matched_address,
                    "longitude": lon,
                    "latitude": lat,
                    "census_tract": census_tract,
                    "geocoding_success": True
                }
            
            time.sleep(0.5)  # Be nice to the API
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue
    
    print(f"   ❌ All attempts failed")
    return None

def test_fixes():
    """Test the fixes on your problematic addresses"""
    
    print("🔧 APPLYING FIXES TO ENHANCED TEXAS ANALYZER")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = EnhancedTexasAnalyzer(
        census_api_key="06ece0121263282cd9ffd753215b007b8f9a3dfc",
        hud_ami_file_path="/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx",
        tdhca_project_file_path="/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
    )
    
    # Apply fixes by replacing methods
    analyzer.get_nearby_lihtc_projects = types.MethodType(fixed_get_nearby_lihtc_projects, analyzer)
    analyzer.enhanced_geocode_address = types.MethodType(enhanced_geocode_address_fixed, analyzer)
    
    print("✅ Fixes applied to analyzer methods")
    
    # Test problematic addresses
    test_addresses = [
        "13921 Nutty Brown Rd, Austin, TX 78737",    # Should now find competition
        "1000 Old Lytton Springs Rd, Lockhart",     # Should now geocode
        "2140 Hagerson, Sugar Land",                 # Should now geocode
        "925 County Road 070, Jasper, TX 75951"     # Should still work but with better competition data
    ]
    
    print(f"\n🧪 TESTING FIXES ON PROBLEMATIC ADDRESSES")
    print("=" * 70)
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n🔍 TEST {i}: {address}")
        print("-" * 50)
        
        try:
            result = analyzer.comprehensive_analyze_address(address, "4% Bond")
            
            if "error" not in result:
                scoring = result.get('scoring', {})
                competition = result.get('competition_analysis', {})
                
                print(f"✅ Analysis successful!")
                print(f"   📊 Category: {scoring.get('category', 'Unknown')}")
                print(f"   🎯 Total points: {scoring.get('total_points', 'N/A')}/5")
                print(f"   🏘️ Competing projects: {competition.get('projects_within_radius', 'N/A')}")
                print(f"   📈 Market saturation: {competition.get('saturation_analysis', {}).get('saturation_level', 'N/A')}")
                
                if competition.get('nearest_project'):
                    nearest = competition['nearest_project']
                    print(f"   📍 Nearest project: {nearest.get('project_name', 'Unknown')} ({nearest.get('distance', 'N/A')} mi)")
                
            else:
                print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception during analysis: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print("If the tests above show competing projects being found, the fixes are working!")
    print("You can now re-run your 10-address analysis with corrected results.")

if __name__ == "__main__":
    test_fixes()
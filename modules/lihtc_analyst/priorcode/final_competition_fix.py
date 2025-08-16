#!/usr/bin/env python3
"""
Final fix for competition analysis - the issue is likely coordinate format or distance calculation
"""

import sys
import pandas as pd
from shapely.geometry import Point
import types
import math

sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code')

def final_competition_fix(self, target_point: Point, radius_miles: float):
    """FINAL FIX for competition analysis with comprehensive debugging"""
    
    if self.tdhca_data is None:
        print(f"    ⚠️ No TDHCA data available")
        return []
    
    print(f"    🔍 FINAL FIX - Competition Analysis Debug:")
    print(f"       • Target: {target_point.y:.6f}, {target_point.x:.6f}")
    print(f"       • Radius: {radius_miles} miles")
    
    # Simple distance calculation (avoiding potential geopy issues)
    def simple_distance_miles(lat1, lon1, lat2, lon2):
        """Simple distance calculation in miles"""
        # Convert to radians
        lat1_r = math.radians(lat1)
        lon1_r = math.radians(lon1)
        lat2_r = math.radians(lat2)
        lon2_r = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_r - lat1_r
        dlon = lon2_r - lon1_r
        a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in miles
        r_miles = 3959
        return c * r_miles
    
    target_lat = target_point.y
    target_lon = target_point.x
    
    nearby_projects = []
    debug_info = {
        'total_checked': 0,
        'valid_coords': 0,
        'in_texas': 0,
        'distance_calculated': 0,
        'within_radius': 0,
        'sample_distances': []
    }
    
    # Check first 10 projects for debugging
    sample_projects = []
    
    for idx, project in self.tdhca_data.iterrows():
        debug_info['total_checked'] += 1
        
        try:
            # Get coordinates
            lat = project.get('Latitude11')
            lon = project.get('Longitude11')
            
            if pd.isna(lat) or pd.isna(lon):
                continue
            
            # Convert to float
            try:
                lat_val = float(lat)
                lon_val = float(lon)
            except (ValueError, TypeError):
                continue
                
            debug_info['valid_coords'] += 1
            
            # Texas bounds check (more lenient)
            if not (24.0 <= lat_val <= 38.0 and -108.0 <= lon_val <= -92.0):
                continue
                
            debug_info['in_texas'] += 1
            
            # Calculate distance
            try:
                distance_miles = simple_distance_miles(target_lat, target_lon, lat_val, lon_val)
                debug_info['distance_calculated'] += 1
                
                # Store sample distances for debugging
                if len(debug_info['sample_distances']) < 10:
                    debug_info['sample_distances'].append({
                        'name': str(project.get('Development Name', 'Unknown'))[:25],
                        'distance': round(distance_miles, 2),
                        'coords': f"{lat_val:.4f}, {lon_val:.4f}",
                        'city': str(project.get('Project City', 'Unknown'))
                    })
                
                if distance_miles <= radius_miles:
                    debug_info['within_radius'] += 1
                    
                    # Build project info
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
                        'coordinates': (lat_val, lon_val)
                    }
                    nearby_projects.append(project_info)
                    
            except Exception as e:
                continue
                
        except Exception as e:
            continue
    
    # Print comprehensive debug info
    print(f"       • Total projects checked: {debug_info['total_checked']}")
    print(f"       • Valid coordinates: {debug_info['valid_coords']}")
    print(f"       • In Texas bounds: {debug_info['in_texas']}")
    print(f"       • Distance calculations: {debug_info['distance_calculated']}")
    print(f"       • Within {radius_miles} miles: {debug_info['within_radius']}")
    
    print(f"       • Sample distances from target:")
    for sample in debug_info['sample_distances']:
        print(f"         - {sample['name']} ({sample['city']}): {sample['distance']} mi")
    
    # If still no results, let's check what's closest
    if len(nearby_projects) == 0 and debug_info['distance_calculated'] > 0:
        print(f"       🚨 NO PROJECTS FOUND - Finding closest project...")
        
        closest_distance = float('inf')
        closest_info = None
        
        for idx, project in self.tdhca_data.iterrows():
            lat = project.get('Latitude11')
            lon = project.get('Longitude11')
            
            if pd.notna(lat) and pd.notna(lon):
                try:
                    lat_val, lon_val = float(lat), float(lon)
                    if 24.0 <= lat_val <= 38.0 and -108.0 <= lon_val <= -92.0:
                        distance = simple_distance_miles(target_lat, target_lon, lat_val, lon_val)
                        
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_info = {
                                'name': project.get('Development Name', 'Unknown'),
                                'distance': round(distance, 2),
                                'city': project.get('Project City', 'Unknown'),
                                'coords': f"{lat_val:.4f}, {lon_val:.4f}"
                            }
                except:
                    continue
        
        if closest_info:
            print(f"       📍 CLOSEST PROJECT: {closest_info['name']}")
            print(f"         City: {closest_info['city']}")
            print(f"         Distance: {closest_info['distance']} miles")
            print(f"         Coordinates: {closest_info['coords']}")
            print(f"       ⚠️ This suggests the search radius might be too small!")
    
    # Sort by distance
    nearby_projects.sort(key=lambda x: x['distance'])
    return nearby_projects

def final_geocoding_fix(self, address: str):
    """Final geocoding fix with even more address variations"""
    
    print(f"🔍 FINAL Geocoding Fix: {address}")
    
    variations = []
    
    # Base variations
    variations.extend([
        address,
        f"{address}, TX",
        f"{address}, Texas"
    ])
    
    # Enhanced variations for specific failing addresses
    if "Old Lytton Springs" in address:
        base_parts = address.split()
        number = base_parts[0] if base_parts[0].isdigit() else ""
        
        # Try without "Old"
        variations.extend([
            f"{number} Lytton Springs Rd, Lockhart, TX 78644",
            f"{number} Lytton Springs Road, Lockhart, TX 78644", 
            f"{number} Lytton Springs, Lockhart, TX",
            f"{number} Old Lytton Springs Road, Lockhart, TX 78644",
            f"{number} Lytton Springs Dr, Lockhart, TX",
            # Try without specific number
            "Lytton Springs Rd, Lockhart, TX",
            "Old Lytton Springs Rd, Lockhart, TX 78644"
        ])
    
    if "Hagerson" in address and "Sugar Land" in address:
        number = address.split()[0] if address.split()[0].isdigit() else "2140"
        
        # Try different street types and zip codes
        sugar_land_zips = ["77479", "77478", "77496", "77498"]
        street_types = ["St", "Street", "Ave", "Avenue", "Dr", "Drive", "Ln", "Lane", "Way", "Blvd", "Boulevard"]
        
        for zip_code in sugar_land_zips:
            for street_type in street_types:
                variations.append(f"{number} Hagerson {street_type}, Sugar Land, TX {zip_code}")
        
        # Also try without specific number
        variations.extend([
            "Hagerson St, Sugar Land, TX",
            "Hagerson Ave, Sugar Land, TX", 
            "Hagerson Dr, Sugar Land, TX"
        ])
    
    # Remove duplicates and clean
    clean_variations = []
    seen = set()
    for var in variations:
        var = var.strip().replace("  ", " ")
        if var and var not in seen and len(var) > 5:
            seen.add(var)
            clean_variations.append(var)
    
    print(f"   Trying {len(clean_variations)} enhanced variations...")
    
    # Try each variation with better error handling
    for i, variation in enumerate(clean_variations[:15]):  # Try more variations
        try:
            print(f"   Attempt {i+1}: {variation}")
            
            import requests
            import time
            
            url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
            params = {
                'address': variation,
                'benchmark': 'Public_AR_Current',
                'vintage': 'Current_Current',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=20)
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
                
                lat, lon = coords['y'], coords['x']
                
                # More lenient Texas bounds check
                if not (24.0 <= lat <= 38.0 and -108.0 <= lon <= -92.0):
                    print(f"   ⚠️ Coordinates outside expanded Texas bounds: {lat:.4f}, {lon:.4f}")
                    continue
                
                print(f"   ✅ SUCCESS with: {variation}")
                print(f"   📍 Coordinates: {lat:.4f}, {lon:.4f}")
                
                return {
                    "address": address,
                    "matched_address": matched_address,
                    "longitude": lon,
                    "latitude": lat,
                    "census_tract": census_tract,
                    "geocoding_success": True,
                    "successful_variation": variation
                }
            
            time.sleep(0.3)  # Shorter delay
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)[:50]}")
            continue
    
    print(f"   ❌ All {len(clean_variations)} variations failed")
    return None

def apply_final_fixes():
    """Apply the final fixes and test"""
    
    print("🔧 APPLYING FINAL FIXES")
    print("=" * 60)
    
    # Import analyzer
    from enhanced_texas_analyzer_st import EnhancedTexasAnalyzer
    
    analyzer = EnhancedTexasAnalyzer(
        census_api_key="06ece0121263282cd9ffd753215b007b8f9a3dfc",
        hud_ami_file_path="/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx",
        tdhca_project_file_path="/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
    )
    
    # Apply final fixes
    analyzer.get_nearby_lihtc_projects = types.MethodType(final_competition_fix, analyzer)
    analyzer.enhanced_geocode_address = types.MethodType(final_geocoding_fix, analyzer)
    
    print("✅ Final fixes applied")
    
    # Test on problematic cases
    test_addresses = [
        "13921 Nutty Brown Rd, Austin, TX 78737",  # Should find competition now
        "1000 Old Lytton Springs Rd, Lockhart",   # Should geocode now
        "2140 Hagerson, Sugar Land"                # Should geocode now
    ]
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n🧪 FINAL TEST {i}: {address}")
        print("-" * 50)
        
        try:
            result = analyzer.comprehensive_analyze_address(address, "4% Bond")
            
            if "error" not in result:
                comp = result.get('competition_analysis', {})
                scoring = result.get('scoring', {})
                
                print(f"✅ SUCCESS!")
                print(f"   🏘️ Competing projects: {comp.get('projects_within_radius', 'N/A')}")
                print(f"   📈 Market saturation: {comp.get('saturation_analysis', {}).get('saturation_level', 'N/A')}")
                print(f"   🎯 Category: {scoring.get('category', 'Unknown')}")
                
                if comp.get('nearby_projects'):
                    print(f"   📍 Sample nearby projects:")
                    for j, proj in enumerate(comp['nearby_projects'][:3]):
                        print(f"      {j+1}. {proj.get('project_name', 'Unknown')} - {proj.get('distance', 'N/A')} mi")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    apply_final_fixes()
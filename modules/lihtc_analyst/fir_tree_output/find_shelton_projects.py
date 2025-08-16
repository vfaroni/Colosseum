#!/usr/bin/env python3
"""
Find all LIHTC projects in Shelton, WA and calculate exact distances
Add geocoding to get lat/long for all projects
"""

import pandas as pd
import requests
import time
from geopy.distance import geodesic

def geocode_address(address, city, state="WA"):
    """Geocode an address using Census Geocoder"""
    try:
        full_address = f"{address}, {city}, {state}"
        
        url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        params = {
            'address': full_address,
            'benchmark': 'Public_AR_Current',
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'result' in data and 'addressMatches' in data['result']:
            if data['result']['addressMatches']:
                coords = data['result']['addressMatches'][0]['coordinates']
                return float(coords['y']), float(coords['x'])  # lat, lon
        
        # Fallback to Nominatim if Census fails
        nom_url = "https://nominatim.openstreetmap.org/search"
        nom_params = {
            'q': full_address,
            'format': 'json',
            'limit': 1
        }
        
        time.sleep(1)  # Rate limiting
        nom_response = requests.get(nom_url, params=nom_params, timeout=10)
        nom_data = nom_response.json()
        
        if nom_data:
            return float(nom_data[0]['lat']), float(nom_data[0]['lon'])
            
    except Exception as e:
        print(f"Geocoding error for {address}: {e}")
        return None, None
    
    return None, None

def find_shelton_projects():
    """Find all projects in Shelton and calculate distances"""
    
    print("🏛️ SHELTON, WA LIHTC PROJECT VERIFICATION")
    print("=" * 50)
    
    # Fir Tree coordinates
    fir_tree_lat = 47.2172038
    fir_tree_lon = -123.1027976
    fir_tree_coords = (fir_tree_lat, fir_tree_lon)
    
    wa_lihtc_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/Data_Sets/washington/lihtc_projects/Big TC List for website_2-6-25.xlsx"
    
    try:
        df = pd.read_excel(wa_lihtc_path)
        
        # Find all Shelton projects
        shelton_projects = df[df['Property City'].str.upper() == 'SHELTON'].copy()
        
        print(f"🏘️ FOUND {len(shelton_projects)} LIHTC PROJECTS IN SHELTON, WA:")
        print("=" * 60)
        
        for idx, project in shelton_projects.iterrows():
            print(f"\n📍 PROJECT {idx + 1}:")
            print(f"   Name: {project['Property Name']}")
            print(f"   Address: {project['Property Address']}")
            print(f"   Units: {project['TOTAL Units']}")
            print(f"   Elderly Setaside: {project['Elderly Setaside']}")
            print(f"   First Credit Year: {project['First Credit Year']}")
            
            # Geocode the project
            print(f"   🗺️ Geocoding...")
            lat, lon = geocode_address(project['Property Address'], 'Shelton', 'WA')
            
            if lat and lon:
                print(f"   Coordinates: {lat}, {lon}")
                
                # Calculate distance to Fir Tree
                project_coords = (lat, lon)
                distance = geodesic(fir_tree_coords, project_coords).miles
                
                print(f"   📏 Distance to Fir Tree: {distance:.2f} miles")
                
                if distance <= 2.0:
                    print(f"   🚨 WITHIN 2 MILES - COMPETING PROJECT!")
                else:
                    print(f"   ✅ Outside 2-mile radius")
                
                # Add to dataframe
                shelton_projects.at[idx, 'Latitude'] = lat
                shelton_projects.at[idx, 'Longitude'] = lon
                shelton_projects.at[idx, 'Distance_to_Fir_Tree_Miles'] = distance
                
            else:
                print(f"   ❌ Could not geocode address")
                shelton_projects.at[idx, 'Latitude'] = None
                shelton_projects.at[idx, 'Longitude'] = None
                shelton_projects.at[idx, 'Distance_to_Fir_Tree_Miles'] = None
        
        print(f"\n📊 SHELTON PROJECT SUMMARY:")
        print("=" * 30)
        
        # Check for competing projects
        if 'Distance_to_Fir_Tree_Miles' in shelton_projects.columns:
            competing = shelton_projects[shelton_projects['Distance_to_Fir_Tree_Miles'] <= 2.0]
            
            print(f"Total Shelton Projects: {len(shelton_projects)}")
            print(f"Successfully Geocoded: {shelton_projects['Latitude'].notna().sum()}")
            print(f"Within 2 Miles of Fir Tree: {len(competing)}")
            
            if len(competing) > 0:
                print(f"\n🚨 COMPETING PROJECTS FOUND:")
                for _, comp in competing.iterrows():
                    print(f"   • {comp['Property Name']} - {comp['Distance_to_Fir_Tree_Miles']:.2f} miles")
            else:
                print(f"✅ NO COMPETING PROJECTS within 2 miles")
        
        # Save enhanced dataset with coordinates
        output_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/Data_Sets/washington/lihtc_projects/WA_LIHTC_with_Coordinates.xlsx"
        
        print(f"\n💾 Now adding coordinates to full dataset...")
        
        # For now, just save Shelton projects with coordinates
        shelton_projects.to_excel('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/fir_tree_output/Shelton_LIHTC_Projects.xlsx', index=False)
        print(f"📄 Shelton projects with coordinates saved to: Shelton_LIHTC_Projects.xlsx")
        
        return shelton_projects
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

if __name__ == "__main__":
    projects = find_shelton_projects()
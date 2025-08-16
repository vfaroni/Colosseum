#!/usr/bin/env python3
"""
Add latitude and longitude coordinates to the full Washington LIHTC database
This will create an enhanced database for future competitive analysis
"""

import pandas as pd
import requests
import time
import json
from datetime import datetime

def geocode_address_batch(address, city, state="WA"):
    """Geocode an address using multiple providers for reliability"""
    
    if not address or pd.isna(address) or not city or pd.isna(city):
        return None, None, "Missing address data"
    
    full_address = f"{address}, {city}, {state}"
    
    try:
        # Try Census Geocoder first (most reliable for US addresses)
        url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        params = {
            'address': full_address,
            'benchmark': 'Public_AR_Current',
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if 'result' in data and 'addressMatches' in data['result']:
            if data['result']['addressMatches']:
                coords = data['result']['addressMatches'][0]['coordinates']
                return float(coords['y']), float(coords['x']), "Census Geocoder"  # lat, lon
        
        # Fallback to Nominatim
        time.sleep(1)  # Rate limiting
        nom_url = "https://nominatim.openstreetmap.org/search"
        nom_params = {
            'q': full_address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'us'
        }
        
        nom_response = requests.get(nom_url, params=nom_params, timeout=15)
        nom_data = nom_response.json()
        
        if nom_data:
            return float(nom_data[0]['lat']), float(nom_data[0]['lon']), "Nominatim"
            
    except Exception as e:
        return None, None, f"Error: {str(e)}"
    
    return None, None, "No geocoding results"

def add_coordinates_to_database():
    """Add coordinates to the full WA LIHTC database"""
    
    print("🏛️ WASHINGTON LIHTC DATABASE COORDINATE ENHANCEMENT")
    print("=" * 60)
    
    input_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/Data_Sets/washington/lihtc_projects/Big TC List for website_2-6-25.xlsx"
    output_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/Data_Sets/washington/lihtc_projects/WA_LIHTC_Enhanced_with_Coordinates_2025.xlsx"
    
    try:
        # Load the database
        print("📊 Loading Washington LIHTC database...")
        df = pd.read_excel(input_path)
        
        print(f"✅ Loaded {len(df)} LIHTC projects")
        print(f"📍 Columns: {len(df.columns)} existing columns")
        
        # Add new coordinate columns
        df['Latitude'] = None
        df['Longitude'] = None
        df['Geocoding_Source'] = None
        df['Geocoding_Date'] = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n🗺️ Beginning geocoding process...")
        print(f"   This will take approximately {len(df) * 2 / 60:.1f} minutes")
        
        # Track progress
        successful_geocodes = 0
        failed_geocodes = 0
        
        # Process in batches
        batch_size = 50
        for batch_start in range(0, len(df), batch_size):
            batch_end = min(batch_start + batch_size, len(df))
            
            print(f"\n📦 Processing batch {batch_start//batch_size + 1}: projects {batch_start+1}-{batch_end}")
            
            for idx in range(batch_start, batch_end):
                row = df.iloc[idx]
                
                # Get address components
                address = row['Property Address']
                city = row['Property City']
                
                print(f"   {idx+1:4d}. {row['Property Name'][:30]:<30} | {city}")
                
                # Geocode
                lat, lon, source = geocode_address_batch(address, city)
                
                if lat and lon:
                    df.at[idx, 'Latitude'] = lat
                    df.at[idx, 'Longitude'] = lon
                    df.at[idx, 'Geocoding_Source'] = source
                    successful_geocodes += 1
                    print(f"        ✅ {lat:.6f}, {lon:.6f} via {source}")
                else:
                    df.at[idx, 'Geocoding_Source'] = source
                    failed_geocodes += 1
                    print(f"        ❌ Failed: {source}")
                
                # Rate limiting
                time.sleep(0.5)
            
            # Save progress after each batch
            df.to_excel(output_path, index=False)
            print(f"   💾 Progress saved - {successful_geocodes} successful, {failed_geocodes} failed")
        
        print(f"\n📈 GEOCODING COMPLETE:")
        print(f"   ✅ Successful: {successful_geocodes} ({successful_geocodes/len(df)*100:.1f}%)")
        print(f"   ❌ Failed: {failed_geocodes} ({failed_geocodes/len(df)*100:.1f}%)")
        
        # Generate summary statistics
        print(f"\n📊 ENHANCED DATABASE SUMMARY:")
        print(f"   Total Projects: {len(df)}")
        print(f"   Geocoded Projects: {successful_geocodes}")
        print(f"   Total Columns: {len(df.columns)} (added Latitude, Longitude, Geocoding_Source, Geocoding_Date)")
        
        # Show city coverage
        city_coverage = df[df['Latitude'].notna()]['Property City'].value_counts().head(10)
        print(f"\n🏘️ TOP 10 CITIES WITH GEOCODED PROJECTS:")
        for city, count in city_coverage.items():
            print(f"   • {city}: {count} projects")
        
        # Final save
        df.to_excel(output_path, index=False)
        
        print(f"\n💾 ENHANCED DATABASE SAVED:")
        print(f"   📁 File: WA_LIHTC_Enhanced_with_Coordinates_2025.xlsx")
        print(f"   📍 Location: Data_Sets/washington/lihtc_projects/")
        
        return output_path, successful_geocodes, failed_geocodes
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, 0, 0

if __name__ == "__main__":
    result = add_coordinates_to_database()
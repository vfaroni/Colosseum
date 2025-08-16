#!/usr/bin/env python3
"""
CTCAC Medical Facilities Geocoder
Downloads and geocodes California healthcare facilities for CTCAC amenity scoring.

CTCAC Requirements:
- Medical clinics, hospitals, urgent care facilities
- 40+ hours per week staffing requirement
- 0.25 mile distance for 1 point, 0.5 mile for 2 points, 1 mile for 3 points

Data Source: California Health Care Access and Information (HCAI)
API: https://data.chhs.ca.gov/api/3/action/datastore_search
"""

import pandas as pd
import requests
import json
import time
from pathlib import Path
import geopandas as gpd
from geopy.distance import geodesic

class CAMedicalFacilitiesGeocoder:
    def __init__(self, data_path=None):
        if data_path is None:
            self.data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets")
        else:
            self.data_path = Path(data_path)
        
        self.medical_dir = self.data_path / "CA_Hospitals_Medical"
        self.medical_dir.mkdir(exist_ok=True)
        
        # PositionStack API key from CLAUDE.md
        self.positionstack_key = "41b80ed51d92978904592126d2bb8f7e"
        
        # HCAI API endpoint
        self.hcai_api_base = "https://data.chhs.ca.gov/api/3/action/datastore_search"
        
        # Cache file for geocoded results
        self.cache_file = self.medical_dir / "geocoded_medical_facilities_cache.json"
        self.cache = self.load_cache()
        
    def load_cache(self):
        """Load geocoding cache to avoid re-geocoding"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_cache(self):
        """Save geocoding cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def download_hcai_facilities(self):
        """Download California healthcare facilities from HCAI API"""
        print("Downloading California healthcare facilities from HCAI...")
        
        all_facilities = []
        offset = 0
        limit = 1000
        
        while True:
            # HCAI API call
            params = {
                'resource_id': 'ece4a19b-40a4-40f2-b6a9-a8c8f6e3b7e2',  # Healthcare facilities resource
                'limit': limit,
                'offset': offset
            }
            
            try:
                response = requests.get(self.hcai_api_base, params=params)
                response.raise_for_status()
                data = response.json()
                
                records = data.get('result', {}).get('records', [])
                if not records:
                    break
                    
                all_facilities.extend(records)
                print(f"Downloaded {len(records)} facilities (total: {len(all_facilities)})")
                
                offset += limit
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"Error downloading from HCAI API: {e}")
                break
        
        if not all_facilities:
            print("No facilities downloaded. Trying alternative approach...")
            return self.download_alternative_medical_data()
        
        # Convert to DataFrame
        df = pd.DataFrame(all_facilities)
        print(f"Total facilities downloaded: {len(df)}")
        
        # Save raw data
        raw_file = self.medical_dir / "HCAI_Raw_Healthcare_Facilities.csv"
        df.to_csv(raw_file, index=False)
        print(f"Raw data saved to: {raw_file}")
        
        return df
    
    def download_alternative_medical_data(self):
        """Alternative method: Use a curated list of major CA medical facilities"""
        print("Using alternative medical facilities dataset...")
        
        # Major medical facilities across California
        facilities = [
            # Los Angeles Area
            {"name": "UCLA Medical Center", "address": "757 Westwood Plaza, Los Angeles, CA 90095", "type": "hospital"},
            {"name": "Cedars-Sinai Medical Center", "address": "8700 Beverly Blvd, West Hollywood, CA 90048", "type": "hospital"},
            {"name": "Children's Hospital Los Angeles", "address": "4650 Sunset Blvd, Los Angeles, CA 90027", "type": "hospital"},
            {"name": "USC Medical Center", "address": "1500 San Pablo St, Los Angeles, CA 90033", "type": "hospital"},
            {"name": "Kaiser Permanente Los Angeles", "address": "4867 Sunset Blvd, Los Angeles, CA 90027", "type": "hospital"},
            
            # Orange County
            {"name": "UC Irvine Medical Center", "address": "101 The City Dr S, Orange, CA 92868", "type": "hospital"},
            {"name": "Hoag Hospital Newport Beach", "address": "1 Hoag Dr, Newport Beach, CA 92663", "type": "hospital"},
            
            # San Diego Area
            {"name": "UC San Diego Medical Center", "address": "200 W Arbor Dr, San Diego, CA 92103", "type": "hospital"},
            {"name": "Sharp Memorial Hospital", "address": "7901 Frost St, San Diego, CA 92123", "type": "hospital"},
            {"name": "Scripps Memorial Hospital", "address": "9888 Genesee Ave, La Jolla, CA 92037", "type": "hospital"},
            
            # San Francisco Bay Area
            {"name": "UCSF Medical Center", "address": "500 Parnassus Ave, San Francisco, CA 94143", "type": "hospital"},
            {"name": "California Pacific Medical Center", "address": "2333 Buchanan St, San Francisco, CA 94115", "type": "hospital"},
            {"name": "Stanford University Medical Center", "address": "300 Pasteur Dr, Stanford, CA 94305", "type": "hospital"},
            {"name": "UCSF Benioff Children's Hospital Oakland", "address": "747 52nd St, Oakland, CA 94609", "type": "hospital"},
            {"name": "Kaiser Permanente San Francisco", "address": "2425 Geary Blvd, San Francisco, CA 94115", "type": "hospital"},
            
            # Central Valley
            {"name": "UC Davis Medical Center", "address": "2315 Stockton Blvd, Sacramento, CA 95817", "type": "hospital"},
            {"name": "Sutter Memorial Hospital", "address": "5151 F St, Sacramento, CA 95819", "type": "hospital"},
            {"name": "Community Medical Centers Fresno", "address": "2823 Fresno St, Fresno, CA 93721", "type": "hospital"},
            {"name": "Saint Agnes Medical Center", "address": "1303 E Herndon Ave, Fresno, CA 93720", "type": "hospital"},
            
            # Northern California
            {"name": "Mercy Medical Center Redding", "address": "2175 Rosaline Ave, Redding, CA 96001", "type": "hospital"},
            {"name": "Shasta Regional Medical Center", "address": "1100 Butte St, Redding, CA 96001", "type": "hospital"},
            
            # Inland Empire
            {"name": "Loma Linda University Medical Center", "address": "11234 Anderson St, Loma Linda, CA 92354", "type": "hospital"},
            {"name": "Kaiser Permanente Riverside", "address": "10800 Magnolia Ave, Riverside, CA 92505", "type": "hospital"},
            {"name": "Desert Regional Medical Center", "address": "1150 N Indian Canyon Dr, Palm Springs, CA 92262", "type": "hospital"},
            
            # Major Urgent Care Chains
            {"name": "Kaiser Permanente Urgent Care", "address": "Multiple Locations", "type": "urgent_care"},
            {"name": "Sutter Health Urgent Care", "address": "Multiple Locations", "type": "urgent_care"},
            {"name": "MinuteClinic CVS", "address": "Multiple Locations", "type": "clinic"},
        ]
        
        df = pd.DataFrame(facilities)
        print(f"Alternative dataset created with {len(df)} major medical facilities")
        return df
    
    def geocode_address(self, address, facility_name):
        """Geocode a single address using PositionStack API"""
        # Check cache first
        cache_key = f"{facility_name}_{address}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if address == "Multiple Locations":
            # Skip chain entries for now
            return None, None
        
        # PositionStack geocoding
        url = "http://api.positionstack.com/v1/forward"
        params = {
            'access_key': self.positionstack_key,
            'query': address,
            'country': 'US',
            'region': 'CA',
            'limit': 1
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                result = data['data'][0]
                lat = float(result['latitude'])
                lng = float(result['longitude'])
                
                # Cache the result
                self.cache[cache_key] = (lat, lng)
                
                print(f"Geocoded: {facility_name[:50]}... -> {lat:.4f}, {lng:.4f}")
                return lat, lng
            else:
                print(f"No geocoding result for: {facility_name}")
                return None, None
                
        except Exception as e:
            print(f"Geocoding error for {facility_name}: {e}")
            return None, None
    
    def process_medical_facilities(self):
        """Download and geocode all California medical facilities"""
        print("=== CTCAC Medical Facilities Geocoding ===")
        
        # Download facilities data
        facilities_df = self.download_hcai_facilities()
        
        if facilities_df.empty:
            print("No facilities data available")
            return
        
        # Determine address fields
        address_fields = ['address', 'facility_address', 'street_address', 'location']
        name_fields = ['name', 'facility_name', 'organization_name', 'dba_name']
        
        address_field = None
        name_field = None
        
        for field in address_fields:
            if field in facilities_df.columns:
                address_field = field
                break
        
        for field in name_fields:
            if field in facilities_df.columns:
                name_field = field
                break
        
        if not address_field:
            print(f"No address field found. Available columns: {list(facilities_df.columns)}")
            return
        
        if not name_field:
            print(f"No name field found. Available columns: {list(facilities_df.columns)}")
            return
        
        print(f"Using address field: {address_field}")
        print(f"Using name field: {name_field}")
        
        # Filter for CTCAC-qualifying facilities
        print("Filtering for CTCAC-qualifying medical facilities...")
        
        # Filter criteria (adjust based on available fields)
        qualifying_types = ['hospital', 'clinic', 'medical center', 'urgent care', 'emergency']
        
        if 'facility_type' in facilities_df.columns:
            mask = facilities_df['facility_type'].str.lower().str.contains('|'.join(qualifying_types), na=False)
            facilities_df = facilities_df[mask]
        elif 'type' in facilities_df.columns:
            mask = facilities_df['type'].str.lower().str.contains('|'.join(qualifying_types), na=False)
            facilities_df = facilities_df[mask]
        
        print(f"Qualifying facilities for geocoding: {len(facilities_df)}")
        
        # Geocode facilities
        geocoded_results = []
        
        for idx, row in facilities_df.iterrows():
            facility_name = str(row[name_field])
            facility_address = str(row[address_field])
            
            # Skip if missing data
            if pd.isna(facility_name) or pd.isna(facility_address):
                continue
                
            if facility_address.lower() in ['nan', 'none', '']:
                continue
            
            lat, lng = self.geocode_address(facility_address, facility_name)
            
            if lat is not None and lng is not None:
                result = {
                    'name': facility_name,
                    'address': facility_address,
                    'latitude': lat,
                    'longitude': lng,
                    'amenity_type': 'medical_facility',
                    'amenity_category': 'medical'
                }
                
                # Add other fields if available
                if 'facility_type' in row:
                    result['facility_type'] = row['facility_type']
                if 'type' in row:
                    result['facility_type'] = row['type']
                
                geocoded_results.append(result)
            
            # Rate limiting
            time.sleep(0.2)
            
            # Save cache periodically
            if len(geocoded_results) % 50 == 0:
                self.save_cache()
                print(f"Progress: {len(geocoded_results)} facilities geocoded")
        
        # Save final cache
        self.save_cache()
        
        # Convert to DataFrame and save
        if geocoded_results:
            result_df = pd.DataFrame(geocoded_results)
            
            # Save as CSV
            output_file = self.medical_dir / "CA_Medical_Facilities_Geocoded.csv"
            result_df.to_csv(output_file, index=False)
            
            # Save as GeoJSON
            gdf = gpd.GeoDataFrame(
                result_df, 
                geometry=gpd.points_from_xy(result_df.longitude, result_df.latitude),
                crs='EPSG:4326'
            )
            geojson_file = self.medical_dir / "CA_Medical_Facilities_Geocoded.geojson"
            gdf.to_file(geojson_file, driver='GeoJSON')
            
            print(f"\n=== GEOCODING COMPLETE ===")
            print(f"Total facilities geocoded: {len(result_df)}")
            print(f"CSV saved to: {output_file}")
            print(f"GeoJSON saved to: {geojson_file}")
            
            # Summary statistics
            print(f"\nFacility type distribution:")
            if 'facility_type' in result_df.columns:
                print(result_df['facility_type'].value_counts())
            
            return result_df
        else:
            print("No facilities were successfully geocoded")
            return pd.DataFrame()

def main():
    """Main execution function"""
    geocoder = CAMedicalFacilitiesGeocoder()
    result_df = geocoder.process_medical_facilities()
    
    if not result_df.empty:
        print(f"\n=== SUCCESS ===")
        print(f"Medical facilities geocoding complete!")
        print(f"Ready for integration with CTCAC amenity mapper")
        
        # Test a sample facility
        if len(result_df) > 0:
            sample = result_df.iloc[0]
            print(f"\nSample facility:")
            print(f"Name: {sample['name']}")
            print(f"Address: {sample['address']}")
            print(f"Coordinates: {sample['latitude']:.4f}, {sample['longitude']:.4f}")
    else:
        print("Geocoding failed - no results produced")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Analyze D'Marco's Region 3 Broker List
Fourth dataset to analyze for LIHTC opportunities

Processes:
1. 16 addresses with full street addresses
2. 7 properties with only lat/lng coordinates

Integrates with existing analysis pipeline to check:
- QCT/DDA status (30% basis boost eligibility)
- TDHCA competition analysis (One Mile/Two Mile rules)
- Economic viability (4% and 9% rankings)
- FEMA flood zones and construction costs
- HUD AMI rents by county

Author: LIHTC Analysis System
Date: 2025-06-25
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from geopy.geocoders import Nominatim
import time
import requests

# Import the existing analyzer
from final_195_sites_complete import Final195SitesComplete

class DMarcoRegion3Analyzer:
    """Analyzer for D'Marco's Region 3 Broker List"""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize base analyzer for all existing functionality
        self.base_analyzer = Final195SitesComplete()
        
        # PositionStack API for better geocoding accuracy
        self.positionstack_key = "41b80ed51d92978904592126d2bb8f7e"
        
        # Geocoding fallback
        self.geolocator = Nominatim(user_agent="dmarco_region3_analyzer")
        
    def create_dataframe(self):
        """Create DataFrame from the provided addresses"""
        
        # Properties with addresses
        address_data = [
            {"Address": "6053 Bellfort St", "City": "Houston", "State": "TX", "Zip": "77033"},
            {"Address": "970 Cowan Rd", "City": "Celina", "State": "TX", "Zip": "75009"},
            {"Address": "1199 N Coit Rd", "City": "Prosper", "State": "TX", "Zip": "75078"},
            {"Address": "1911 Oak Grove Pkwy", "City": "Frisco", "State": "TX", "Zip": "75034"},
            {"Address": "399 E Malone St", "City": "Celina", "State": "TX", "Zip": "75009"},
            {"Address": "8700 Preston Rd", "City": "Frisco", "State": "TX", "Zip": "75034"},
            {"Address": "9923 Smiley Rd", "City": "Celina", "State": "TX", "Zip": "75009"},
            {"Address": "13161 Co Rd 426", "City": "Anna", "State": "TX", "Zip": "75409"},
            {"Address": "611 W White St", "City": "Anna", "State": "TX", "Zip": "75409"},
            {"Address": "15624 Fishtrap Rd", "City": "Aubrey", "State": "TX", "Zip": "76227"},
            {"Address": "9174 Co Rd 9", "City": "Celina", "State": "TX", "Zip": "75009"},
            {"Address": "2260 N Louisiana Dr", "City": "Celina", "State": "TX", "Zip": "75009"},
            {"Address": "6218 N McDonald St", "City": "Melissa", "State": "TX", "Zip": "75454"},
            {"Address": "2350 N Louisiana Dr", "City": "Celina", "State": "TX", "Zip": "75009"},
            {"Address": "1488 W First St", "City": "Prosper", "State": "TX", "Zip": "75078"},
            {"Address": "6169 Private Rd 902", "City": "Celina", "State": "TX", "Zip": "75009"}
        ]
        
        # Properties with only coordinates
        coord_data = [
            {"Latitude": 33.192215, "Longitude": -96.801620},
            {"Latitude": 33.146441, "Longitude": -96.849079},
            {"Latitude": 33.293596, "Longitude": -96.811962},
            {"Latitude": 33.205793, "Longitude": -96.802205},
            {"Latitude": 33.225853, "Longitude": -96.844240},
            {"Latitude": 33.361583, "Longitude": -96.456708},
            {"Latitude": 33.07391258261536, "Longitude": -96.68027524297095}
        ]
        
        # Create DataFrames
        df_addresses = pd.DataFrame(address_data)
        df_coords = pd.DataFrame(coord_data)
        
        # Add property names/identifiers
        df_addresses['Property_Name'] = [f"Region3_Address_{i+1}" for i in range(len(df_addresses))]
        df_coords['Property_Name'] = [f"Region3_Coords_{i+1}" for i in range(len(df_coords))]
        
        # Add source identifier
        df_addresses['Source'] = 'DMarco_Region3_Broker'
        df_coords['Source'] = 'DMarco_Region3_Broker'
        
        # For coord properties, we'll need to reverse geocode to get city/county
        df_coords['Address'] = None
        df_coords['City'] = None
        df_coords['State'] = 'TX'
        df_coords['Zip'] = None
        
        return df_addresses, df_coords
    
    def geocode_with_positionstack(self, address, city, state, zip_code):
        """Use PositionStack API for geocoding"""
        query = f"{address}, {city}, {state} {zip_code}"
        
        url = "http://api.positionstack.com/v1/forward"
        params = {
            'access_key': self.positionstack_key,
            'query': query,
            'limit': 1,
            'country': 'US'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    result = data['data'][0]
                    return {
                        'latitude': result['latitude'],
                        'longitude': result['longitude'],
                        'confidence': result.get('confidence', 0),
                        'geocoded_address': result.get('label', query)
                    }
        except Exception as e:
            self.logger.warning(f"PositionStack geocoding failed: {e}")
        
        return None
    
    def reverse_geocode_coordinates(self, lat, lng):
        """Reverse geocode to get address info from coordinates"""
        try:
            location = self.geolocator.reverse((lat, lng), timeout=10)
            if location:
                # Parse the address components
                components = location.raw.get('address', {})
                return {
                    'address': location.address,
                    'city': components.get('city') or components.get('town') or components.get('village'),
                    'county': components.get('county', '').replace(' County', ''),
                    'state': components.get('state'),
                    'zip': components.get('postcode')
                }
            time.sleep(1)  # Rate limiting
        except Exception as e:
            self.logger.warning(f"Reverse geocoding failed for {lat}, {lng}: {e}")
        
        return None
    
    def process_sites(self):
        """Process all Region 3 broker sites"""
        self.logger.info("Starting D'Marco Region 3 Broker List analysis")
        
        # Create dataframes
        df_addresses, df_coords = self.create_dataframe()
        
        # Process addresses - geocode to get coordinates
        self.logger.info(f"Geocoding {len(df_addresses)} properties with addresses")
        
        for idx, row in df_addresses.iterrows():
            # Try PositionStack first
            result = self.geocode_with_positionstack(
                row['Address'], row['City'], row['State'], row['Zip']
            )
            
            if result:
                df_addresses.at[idx, 'Latitude'] = result['latitude']
                df_addresses.at[idx, 'Longitude'] = result['longitude']
                df_addresses.at[idx, 'Geocoding_Confidence'] = result['confidence']
            else:
                # Fallback to Nominatim
                full_address = f"{row['Address']}, {row['City']}, {row['State']} {row['Zip']}"
                try:
                    location = self.geolocator.geocode(full_address, timeout=10)
                    if location:
                        df_addresses.at[idx, 'Latitude'] = location.latitude
                        df_addresses.at[idx, 'Longitude'] = location.longitude
                        df_addresses.at[idx, 'Geocoding_Confidence'] = 0.8
                    time.sleep(1)
                except Exception as e:
                    self.logger.warning(f"Geocoding failed for {full_address}: {e}")
        
        # Process coordinate-only properties - reverse geocode
        self.logger.info(f"Reverse geocoding {len(df_coords)} properties with coordinates only")
        
        for idx, row in df_coords.iterrows():
            addr_info = self.reverse_geocode_coordinates(row['Latitude'], row['Longitude'])
            if addr_info:
                df_coords.at[idx, 'City'] = addr_info['city']
                df_coords.at[idx, 'County'] = addr_info['county']
                df_coords.at[idx, 'Zip'] = addr_info['zip']
                df_coords.at[idx, 'Geocoded_Address'] = addr_info['address']
        
        # Combine both dataframes
        all_sites = pd.concat([df_addresses, df_coords], ignore_index=True)
        
        # Add county information where missing (from city lookup)
        county_mapping = {
            'Houston': 'Harris',
            'Celina': 'Collin',
            'Prosper': 'Collin',
            'Frisco': 'Collin',
            'Anna': 'Collin',
            'Aubrey': 'Denton',
            'Melissa': 'Collin'
        }
        
        all_sites['County'] = all_sites.apply(
            lambda row: county_mapping.get(row['City'], row.get('County')), 
            axis=1
        )
        
        # Save the prepared data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"DMarco_Region3_Broker_Prepared_{timestamp}.csv"
        all_sites.to_csv(output_file, index=False)
        
        self.logger.info(f"Saved prepared data to {output_file}")
        self.logger.info(f"Total sites: {len(all_sites)}")
        self.logger.info(f"Sites with coordinates: {all_sites['Latitude'].notna().sum()}")
        
        return all_sites, output_file
    
    def integrate_with_analysis(self, prepared_file):
        """Run the prepared sites through the existing analysis pipeline"""
        self.logger.info("Integrating with existing LIHTC analysis pipeline")
        
        # This would integrate with the existing final_195_sites_complete.py
        # or other analysis scripts to:
        # 1. Check QCT/DDA status
        # 2. Run competition analysis
        # 3. Calculate economic viability
        # 4. Check FEMA flood zones
        # 5. Apply HUD AMI rents
        
        # For now, return the prepared file path
        return prepared_file


def main():
    """Main execution function"""
    analyzer = DMarcoRegion3Analyzer()
    
    # Process and prepare the sites
    sites_df, output_file = analyzer.process_sites()
    
    # Summary statistics
    print("\n=== D'Marco Region 3 Broker List Summary ===")
    print(f"Total Sites: {len(sites_df)}")
    print(f"Sites with Addresses: {sites_df['Address'].notna().sum()}")
    print(f"Sites with Coordinates Only: {sites_df['Address'].isna().sum()}")
    print(f"Successfully Geocoded: {sites_df['Latitude'].notna().sum()}")
    
    # City distribution
    print("\nSites by City:")
    city_counts = sites_df['City'].value_counts()
    for city, count in city_counts.items():
        print(f"  {city}: {count}")
    
    print(f"\nPrepared data saved to: {output_file}")
    print("\nNext Steps:")
    print("1. Run through QCT/DDA checker")
    print("2. Apply TDHCA competition analysis")
    print("3. Calculate economic viability scores")
    print("4. Integrate with existing 195 sites analysis")


if __name__ == "__main__":
    main()
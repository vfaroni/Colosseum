#!/usr/bin/env python3
"""
CTCAC Amenity Mapper - COMPLETE VERSION
Comprehensive Site Amenity Analysis for LIHTC Projects with ALL CTCAC Categories

This script maps all CTCAC-eligible amenities around a development site and calculates
scoring points based on CTCAC QAP 2025 complete amenity list.

Author: LIHTC Analysis Team
Date: June 30, 2025
"""

import pandas as pd
import geopandas as gpd
import json
import folium
import requests
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class CTCACAmenityMapperComplete:
    def __init__(self, data_path=None):
        """Initialize the CTCAC Amenity Mapper with complete amenity categories"""
        if data_path is None:
            self.data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets")
        else:
            self.data_path = Path(data_path)
        
        # Complete CTCAC distance requirements (in miles) from application
        self.distance_rules = {
            # a) Transit
            'transit': {
                'brt_rail_ferry_high_density': {'standard': [0.33], 'points': [7], 'requires_density': True},  # >25 units/acre + 30min service
                'brt_rail_ferry_regular': {'standard': [0.33], 'points': [6]},  # 30min service 7-9am, 4-6pm
                'brt_rail_ferry_half_mile': {'standard': [0.5], 'points': [5]},  # 30min service 7-9am, 4-6pm
                'basic_transit_third': {'standard': [0.33], 'rural': [0.33], 'points': [4]},  # Any transit
                'basic_transit_half': {'standard': [0.5], 'rural': [0.5], 'points': [3]}  # Any transit
            },
            
            # b) Public Park
            'public_park': {
                'park_community_center': {'standard': [0.5, 0.75], 'rural': [1.0, 1.5], 'points': [3, 2]}
            },
            
            # c) Book-Lending Public Library
            'library': {
                'public_library': {'standard': [0.5, 1.0], 'rural': [1.0, 2.0], 'points': [3, 2]}
            },
            
            # d) Grocery Stores/Markets
            'grocery': {
                'full_scale': {'standard': [0.5, 1.0, 1.5], 'rural': [1.0, 2.0, 3.0], 'points': [5, 4, 3]},  # 25,000+ sq ft
                'neighborhood': {'standard': [0.25, 0.5], 'rural': [0.5, 1.0], 'points': [4, 3]},  # 5,000+ sq ft
                'farmers_market': {'standard': [0.5, 1.0], 'points': [2, 1]}  # Weekly, 5+ months
            },
            
            # e) Schools
            'schools': {
                'adult_ed_community_college': {'standard': [1.0], 'rural': [1.5], 'points': [3]},
                'elementary': {'standard': [0.25, 0.75], 'rural': [0.75, 1.25], 'points': [3, 2]},  # Qualifying development only
                'middle': {'standard': [0.5, 1.0], 'rural': [1.0, 1.5], 'points': [3, 2]},  # Qualifying development only
                'high': {'standard': [1.0, 1.5], 'rural': [1.5, 2.5], 'points': [3, 2]}  # Qualifying development only
            },
            
            # f) Senior Centers (Senior developments only)
            'senior_center': {
                'daily_operated': {'standard': [0.5, 0.75], 'rural': [1.0, 1.5], 'points': [3, 2]}
            },
            
            # g) Special Needs Facilities (Special needs developments only)
            'special_needs': {
                'population_specific': {'standard': [0.5, 1.0], 'points': [3, 2]}
            },
            
            # h) Medical Clinic or Hospital
            'medical': {
                'clinic_hospital': {'standard': [0.5, 1.0], 'rural': [1.0, 1.5], 'points': [3, 2]}
            },
            
            # i) Pharmacy
            'pharmacy': {
                'pharmacy': {'standard': [0.5, 1.0], 'rural': [1.0, 2.0], 'points': [2, 1]}
            },
            
            # j) High Speed Internet (not location-based - project amenity)
            'internet': {
                'high_speed': {'standard': [], 'rural': [], 'points': [2, 3]}  # 2 pts standard, 3 pts rural
            },
            
            # k) Highest/High Resource Area (not distance-based - census tract designation)
            'opportunity_area': {
                'highest_high_resource': {'points': [8]}  # New construction Large Family only
            }
        }
        
        self.amenity_colors = {
            'transit': 'green',
            'public_park': 'darkgreen',
            'library': 'purple',
            'grocery': 'red',
            'schools': 'blue',
            'senior_center': 'orange',
            'special_needs': 'brown',
            'medical': 'pink',
            'pharmacy': 'lightred',
            'opportunity_area': 'gold'
        }
        
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate the great circle distance between two points in miles"""
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 3959  # Radius of earth in miles
        return c * r
    
    def geocode_address(self, address):
        """Geocode an address to lat/lng using PositionStack API with Census fallback"""
        # First try PositionStack API (more reliable for complex addresses)
        positionstack_url = "http://api.positionstack.com/v1/forward"
        positionstack_params = {
            'access_key': '41b80ed51d92978904592126d2bb8f7e',
            'query': address,
            'country': 'US',
            'limit': 1
        }
        
        try:
            print(f"Geocoding with PositionStack: {address}")
            response = requests.get(positionstack_url, params=positionstack_params)
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                coords = data['data'][0]
                lat = coords['latitude']
                lng = coords['longitude']
                print(f"PositionStack geocoded to: {lat:.6f}, {lng:.6f}")
                return lat, lng
            else:
                print(f"PositionStack could not geocode: {address}")
        except Exception as e:
            print(f"PositionStack error: {e}")
        
        # Fallback to Census Geocoding API
        print(f"Trying Census geocoding as fallback...")
        census_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        census_params = {
            'address': address,
            'benchmark': 'Public_AR_Current',
            'format': 'json'
        }
        
        try:
            response = requests.get(census_url, params=census_params)
            data = response.json()
            
            if data['result']['addressMatches']:
                coords = data['result']['addressMatches'][0]['coordinates']
                lat, lng = coords['y'], coords['x']
                print(f"Census geocoded to: {lat:.6f}, {lng:.6f}")
                return lat, lng
            else:
                print(f"Census could not geocode address: {address}")
                return None, None
        except Exception as e:
            print(f"Census geocoding error: {e}")
            return None, None
    
    def load_schools_data(self):
        """Load California public schools data"""
        schools_file = self.data_path / "california" / "CA_Public Schools" / "SchoolSites2324_4153587227043982744.csv"
        
        if not schools_file.exists():
            print(f"Schools file not found: {schools_file}")
            return pd.DataFrame()
        
        schools = pd.read_csv(schools_file)
        
        # Filter for active CTCAC-eligible schools
        eligible_schools = schools[
            (schools['Status'] == 'Active') &
            (schools['School Type'].isin(['Elementary', 'Middle', 'High'])) |
            (schools['School Level'] == 'Adult Education')
        ].copy()
        
        # Standardize school types for mapping
        eligible_schools['amenity_type'] = eligible_schools['School Type'].str.lower()
        eligible_schools['amenity_category'] = 'schools'
        
        # Standardize column names
        result = eligible_schools[['School Name', 'School Type', 'Street', 'City', 'Latitude', 'Longitude', 
                               'amenity_type', 'amenity_category']].dropna()
        result = result.rename(columns={'School Name': 'name', 'Latitude': 'latitude', 'Longitude': 'longitude'})
        return result
    
    def load_libraries_data(self):
        """Load California libraries data from OpenStreetMap"""
        libraries_file = self.data_path / "california" / "CA_Libraries" / "CA_Libraries_OSM.geojson"
        
        if not libraries_file.exists():
            print(f"Libraries file not found: {libraries_file}")
            return pd.DataFrame()
        
        gdf = gpd.read_file(libraries_file)
        gdf['centroid'] = gdf.geometry.centroid
        
        libraries = pd.DataFrame()
        libraries['name'] = gdf['name'].fillna('Public Library')
        libraries['amenity_type'] = 'public_library'
        libraries['amenity_category'] = 'library'
        libraries['latitude'] = gdf['centroid'].y
        libraries['longitude'] = gdf['centroid'].x
        
        return libraries.dropna()
    
    def load_pharmacies_data(self):
        """Load California pharmacies data from OpenStreetMap"""
        pharmacies_file = self.data_path / "california" / "CA_Pharmacies" / "CA_Pharmacies_OSM.geojson"
        
        if not pharmacies_file.exists():
            print(f"Pharmacies file not found: {pharmacies_file}")
            return pd.DataFrame()
        
        gdf = gpd.read_file(pharmacies_file)
        gdf['centroid'] = gdf.geometry.centroid
        
        pharmacies = pd.DataFrame()
        pharmacies['name'] = gdf['name'].fillna('Pharmacy')
        pharmacies['amenity_type'] = 'pharmacy'
        pharmacies['amenity_category'] = 'pharmacy'
        pharmacies['latitude'] = gdf['centroid'].y
        pharmacies['longitude'] = gdf['centroid'].x
        
        return pharmacies.dropna()
    
    def load_senior_centers_data(self):
        """Load California senior centers data from OpenStreetMap"""
        senior_file = self.data_path / "california" / "CA_Senior_Centers" / "CA_Senior_Centers_OSM.geojson"
        
        if not senior_file.exists():
            print(f"Senior centers file not found: {senior_file}")
            return pd.DataFrame()
        
        gdf = gpd.read_file(senior_file)
        gdf['centroid'] = gdf.geometry.centroid
        
        senior_centers = pd.DataFrame()
        senior_centers['name'] = gdf['name'].fillna('Senior Center')
        senior_centers['amenity_type'] = 'daily_operated'
        senior_centers['amenity_category'] = 'senior_center'
        senior_centers['latitude'] = gdf['centroid'].y
        senior_centers['longitude'] = gdf['centroid'].x
        
        return senior_centers.dropna()
    
    def load_medical_data(self):
        """Load California licensed healthcare facilities data"""
        # Use the comprehensive licensed healthcare facilities dataset
        medical_file = self.data_path / "california" / "CA_Hospitals_Medical" / "Licensed_and_Certified_Healthcare_Facilities.csv"
        
        if not medical_file.exists():
            print(f"Licensed healthcare facilities file not found: {medical_file}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(medical_file)
            
            # Filter for CTCAC-qualifying medical facilities:
            # GACH = General Acute Care Hospitals
            # RHC = Rural Health Clinics  
            # FQHC = Federally Qualified Health Centers
            # COMTYC = Community Clinics
            qualifying_types = ['GACH', 'RHC', 'RHC/OP', 'RHC/MD', 'RHC/COMTYC', 'FQHC', 'COMTYC']
            medical_df = df[df['FAC_TYPE_CODE'].isin(qualifying_types)].copy()
            
            # Filter for active facilities only
            medical_df = medical_df[medical_df['FAC_STATUS_TYPE_CODE'] == 'OPEN']
            
            # Filter out facilities with missing coordinates
            medical_df = medical_df.dropna(subset=['LATITUDE', 'LONGITUDE'])
            
            # Standardize for CTCAC scoring
            medical_facilities = pd.DataFrame()
            medical_facilities['name'] = medical_df['FACNAME']
            medical_facilities['amenity_type'] = medical_df['FAC_TYPE_CODE'].map({
                'GACH': 'hospital',
                'RHC': 'rural_health_clinic', 
                'RHC/OP': 'rural_health_clinic',
                'RHC/MD': 'rural_health_clinic',
                'RHC/COMTYC': 'rural_health_clinic',
                'FQHC': 'federally_qualified_health_center',
                'COMTYC': 'community_clinic'
            })
            medical_facilities['amenity_category'] = 'medical'
            medical_facilities['latitude'] = medical_df['LATITUDE']
            medical_facilities['longitude'] = medical_df['LONGITUDE']
            medical_facilities['address'] = medical_df['ADDRESS']
            medical_facilities['city'] = medical_df['CITY']
            medical_facilities['county'] = medical_df['COUNTY_NAME']
            medical_facilities['facility_type'] = medical_df['FAC_TYPE_CODE']
            medical_facilities['license_status'] = medical_df['LICENSE_STATUS_DESCRIPTION']
            medical_facilities['capacity'] = medical_df['CAPACITY']
            
            print(f"Loaded {len(medical_facilities)} licensed medical facilities")
            print(f"  - Hospitals (GACH): {len(medical_facilities[medical_facilities['facility_type'] == 'GACH'])}")
            print(f"  - Rural Health Clinics: {len(medical_facilities[medical_facilities['facility_type'].str.contains('RHC')])}")
            print(f"  - FQHCs: {len(medical_facilities[medical_facilities['facility_type'] == 'FQHC'])}")
            print(f"  - Community Clinics: {len(medical_facilities[medical_facilities['facility_type'] == 'COMTYC'])}")
            
            return medical_facilities.dropna(subset=['latitude', 'longitude'])
            
        except Exception as e:
            print(f"Error loading licensed healthcare facilities: {e}")
            return pd.DataFrame()
    
    def load_transit_data(self):
        """Load California transit stops data from the comprehensive CA transit dataset"""
        # Use the comprehensive CA transit stops dataset
        transit_file = self.data_path / "california" / "CA_Transit_Data" / "California_Transit_Stops.csv"
        
        if not transit_file.exists():
            print(f"Transit stops file not found: {transit_file}")
            return pd.DataFrame()
        
        try:
            # Load the full transit stops dataset
            df = pd.read_csv(transit_file)
            
            # The GeoJSON shows this structure: agency, stop_id, stop_name, n_routes, n_arrivals, n_hours_in_service
            # Extract coordinates from geometry if needed, or use lat/lng columns if available
            
            # Check if we need to load from GeoJSON instead for coordinates
            geojson_file = self.data_path / "california" / "CA_Transit_Data" / "California_Transit_Stops.geojson"
            if geojson_file.exists():
                print("Loading transit stops from GeoJSON for coordinates...")
                import geopandas as gpd
                gdf = gpd.read_file(str(geojson_file))
                
                # Extract coordinates from geometry
                gdf['latitude'] = gdf.geometry.y
                gdf['longitude'] = gdf.geometry.x
                
                # Standardize column names for CTCAC scoring
                transit_stops = pd.DataFrame()
                transit_stops['name'] = gdf['stop_name'].fillna('Transit Stop')
                transit_stops['amenity_type'] = 'transit_stop'  # Basic transit stops
                transit_stops['amenity_category'] = 'transit'
                transit_stops['latitude'] = gdf['latitude']
                transit_stops['longitude'] = gdf['longitude']
                transit_stops['agency'] = gdf['agency'].fillna('Unknown')
                transit_stops['stop_id'] = gdf['stop_id'].fillna('')
                
                # Add service frequency info if available
                if 'n_arrivals' in gdf.columns:
                    transit_stops['n_arrivals'] = gdf['n_arrivals']
                if 'n_hours_in_service' in gdf.columns:
                    transit_stops['n_hours_in_service'] = gdf['n_hours_in_service']
                if 'n_routes' in gdf.columns:
                    transit_stops['n_routes'] = gdf['n_routes']
                
                # Remove duplicate stops based on location (lat/lng) but keep different routes at same location
                # This preserves multiple bus routes serving the same stop while removing true duplicates
                if len(transit_stops) > 0:
                    # Round coordinates to avoid minor GPS differences
                    transit_stops['lat_rounded'] = transit_stops['latitude'].round(6)
                    transit_stops['lng_rounded'] = transit_stops['longitude'].round(6)
                    # Keep first occurrence of each unique location
                    transit_stops = transit_stops.drop_duplicates(subset=['lat_rounded', 'lng_rounded'])
                    transit_stops = transit_stops.drop(['lat_rounded', 'lng_rounded'], axis=1)
                
                # Load additional Metrolink stations
                metrolink_file = self.data_path / "california" / "CA_Transit_Data" / "Perris_Metrolink_Station.csv"
                if metrolink_file.exists():
                    metrolink_df = pd.read_csv(metrolink_file)
                    print(f"Loading Metrolink station: {metrolink_df['name'].iloc[0]} at {metrolink_df['latitude'].iloc[0]}, {metrolink_df['longitude'].iloc[0]}")
                    transit_stops = pd.concat([transit_stops, metrolink_df], ignore_index=True)
                    print(f"Added {len(metrolink_df)} Metrolink stations")
                
                print(f"Loaded {len(transit_stops)} comprehensive CA transit stops")
                return transit_stops.dropna(subset=['latitude', 'longitude'])
            else:
                print("GeoJSON file not found, trying CSV approach")
                return pd.DataFrame()
            
        except Exception as e:
            print(f"Error loading transit stops: {e}")
            return pd.DataFrame()
    
    def load_hqta_data(self):
        """Load High Quality Transit Areas data for maximum 7-point CTCAC scoring"""
        hqta_file = self.data_path / "california" / "CA_Transit_Data" / "High_Quality_Transit_Areas.csv"
        
        if not hqta_file.exists():
            print(f"HQTA file not found: {hqta_file}")
            return pd.DataFrame()
        
        try:
            # Load HQTA data
            df = pd.read_csv(hqta_file)
            
            # For HQTA, we need to work with the GeoJSON to get area boundaries
            geojson_file = self.data_path / "california" / "CA_Transit_Data" / "High_Quality_Transit_Areas.geojson"
            if geojson_file.exists():
                print("Loading High Quality Transit Areas from GeoJSON...")
                import geopandas as gpd
                gdf = gpd.read_file(str(geojson_file))
                
                # Calculate centroids for distance calculations
                gdf['centroid'] = gdf.geometry.centroid
                gdf['latitude'] = gdf['centroid'].y
                gdf['longitude'] = gdf['centroid'].x
                
                # Standardize for CTCAC scoring
                hqta_areas = pd.DataFrame()
                hqta_areas['name'] = 'High Quality Transit Area'
                hqta_areas['amenity_type'] = 'hqta'  # High Quality Transit Area
                hqta_areas['amenity_category'] = 'transit'
                hqta_areas['latitude'] = gdf['latitude']
                hqta_areas['longitude'] = gdf['longitude']
                hqta_areas['hqta_type'] = gdf.get('hqta_type', 'hq_corridor')
                hqta_areas['agency_primary'] = gdf.get('agency_primary', 'Unknown')
                
                # Mark these as high-quality for scoring
                hqta_areas['is_hqta'] = True
                hqta_areas['max_points'] = 7  # HQTA can provide maximum 7 points
                
                print(f"Loaded {len(hqta_areas)} High Quality Transit Areas")
                return hqta_areas.dropna(subset=['latitude', 'longitude'])
            else:
                print("HQTA GeoJSON file not found")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error loading HQTA data: {e}")
            return pd.DataFrame()
    
    def load_parks_data(self):
        """Load California public parks data"""
        parks_file = self.data_path / "california" / "CA_Public_Parks" / "CA_Public_Parks.csv"
        
        if not parks_file.exists():
            print(f"Parks file not found: {parks_file}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(parks_file)
            
            # Standardize column names
            parks = pd.DataFrame()
            parks['name'] = df['name']
            parks['amenity_type'] = df['park_type']  # public_park, community_center
            parks['amenity_category'] = 'public_park'
            parks['latitude'] = df['latitude']
            parks['longitude'] = df['longitude']
            
            # Add additional info if available
            if 'city' in df.columns:
                parks['city'] = df['city']
            if 'county' in df.columns:
                parks['county'] = df['county']
            if 'size_acres' in df.columns:
                parks['size_acres'] = df['size_acres']
            
            print(f"Loaded {len(parks)} public parks and community centers")
            return parks.dropna()
            
        except Exception as e:
            print(f"Error loading parks: {e}")
            return pd.DataFrame()
    
    def load_grocery_data(self):
        """Load California grocery stores data"""
        grocery_file = self.data_path / "california" / "CA_Grocery_Stores" / "CA_Grocery_Stores.csv"
        
        if not grocery_file.exists():
            print(f"Grocery stores file not found: {grocery_file}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(grocery_file)
            
            # Standardize column names
            grocery_stores = pd.DataFrame()
            grocery_stores['name'] = df['name']
            grocery_stores['amenity_type'] = df['store_type']  # full_scale, neighborhood, farmers_market
            grocery_stores['amenity_category'] = 'grocery'
            grocery_stores['latitude'] = df['latitude']
            grocery_stores['longitude'] = df['longitude']
            
            # Add additional info if available
            if 'chain' in df.columns:
                grocery_stores['chain'] = df['chain']
            if 'city' in df.columns:
                grocery_stores['city'] = df['city']
            if 'county' in df.columns:
                grocery_stores['county'] = df['county']
            if 'est_sqft' in df.columns:
                grocery_stores['est_sqft'] = df['est_sqft']
            if 'has_fresh_produce' in df.columns:
                grocery_stores['has_fresh_produce'] = df['has_fresh_produce']
            if 'has_fresh_meat' in df.columns:
                grocery_stores['has_fresh_meat'] = df['has_fresh_meat']
            
            print(f"Loaded {len(grocery_stores)} grocery stores and markets")
            return grocery_stores.dropna()
            
        except Exception as e:
            print(f"Error loading grocery stores: {e}")
            return pd.DataFrame()
    
    def calculate_complete_amenity_scores(self, site_lat, site_lng, is_rural=False, 
                                        project_type='family', density_per_acre=None,
                                        qualifying_development=False, new_construction=False,
                                        large_family=False, opportunity_area_status=None):
        """Calculate complete CTCAC amenity scores for a site"""
        
        results = {
            'site_coordinates': (site_lat, site_lng),
            'is_rural': is_rural,
            'project_type': project_type,
            'qualifying_development': qualifying_development,
            'amenities_found': {},
            'scoring_summary': {},
            'total_points': 0,
            'max_possible_points': 15  # CTCAC maximum
        }
        
        # Load all amenity datasets
        schools = self.load_schools_data()
        libraries = self.load_libraries_data()
        pharmacies = self.load_pharmacies_data()
        senior_centers = self.load_senior_centers_data()
        medical_facilities = self.load_medical_data()
        transit_stops = self.load_transit_data()
        hqta_areas = self.load_hqta_data()
        public_parks = self.load_parks_data()
        grocery_stores = self.load_grocery_data()
        
        # Combine transit stops and HQTA areas into one transit category
        if not transit_stops.empty and not hqta_areas.empty:
            combined_transit = pd.concat([transit_stops, hqta_areas], ignore_index=True)
        elif not transit_stops.empty:
            combined_transit = transit_stops
        elif not hqta_areas.empty:
            combined_transit = hqta_areas
        else:
            combined_transit = pd.DataFrame()
        
        # Combine all amenities and calculate distances
        all_amenities = []
        
        for df, category in [(schools, 'schools'), (libraries, 'library'), 
                           (pharmacies, 'pharmacy'), (senior_centers, 'senior_center'),
                           (medical_facilities, 'medical'), (combined_transit, 'transit'),
                           (public_parks, 'public_park'), (grocery_stores, 'grocery')]:
            if not df.empty:
                df_copy = df.copy()
                df_copy['distance_miles'] = df_copy.apply(
                    lambda row: self.haversine_distance(site_lat, site_lng, row['latitude'], row['longitude']),
                    axis=1
                )
                all_amenities.append(df_copy)
        
        if not all_amenities:
            print("No amenity data loaded")
            return results
        
        all_amenities_df = pd.concat(all_amenities, ignore_index=True)
        
        # Calculate scores for each category
        total_points = 0
        
        # a) Transit stops - filter to CTCAC scoring distances
        transit_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'transit']
        # Filter to maximum CTCAC scoring distance (0.5 miles for transit)
        transit_scorable = transit_nearby[transit_nearby['distance_miles'] <= 0.5]
        # Include non-scoring transit (0.5-1.0 miles) for display with 0 points
        transit_extended = transit_nearby[
            (transit_nearby['distance_miles'] > 0.5) & 
            (transit_nearby['distance_miles'] <= 1.0)
        ]
        # Mark extended transit as non-scoring
        transit_extended_dict = transit_extended.to_dict('records')
        for stop in transit_extended_dict:
            stop['ctcac_points'] = 0
            stop['beyond_scoring_distance'] = True
        
        # Mark scoring transit with points
        transit_scoring_dict = transit_scorable.to_dict('records')
        for stop in transit_scoring_dict:
            stop['ctcac_points'] = 'varies'  # Will be calculated by scoring function
            stop['beyond_scoring_distance'] = False
        
        # Combine both for display
        all_transit_for_display = transit_scoring_dict + transit_extended_dict
        
        transit_points = self._score_transit_complete(transit_nearby, is_rural, density_per_acre)
        results['amenities_found']['transit'] = all_transit_for_display
        results['scoring_summary']['transit'] = transit_points
        total_points += transit_points.get('points', 0)
        
        # b) Public Parks and Community Centers - filter to CTCAC scoring distances
        parks_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'public_park']
        # Maximum CTCAC distance: 0.75 miles standard, 1.5 miles rural
        max_park_dist = 1.5 if is_rural else 0.75
        parks_scorable = parks_nearby[parks_nearby['distance_miles'] <= max_park_dist]
        parks_points = self._score_parks_complete(parks_nearby, is_rural)
        results['amenities_found']['public_parks'] = parks_scorable.to_dict('records')
        results['scoring_summary']['public_park'] = parks_points
        total_points += parks_points.get('points', 0)
        
        # c) Libraries - filter to CTCAC scoring distances
        libraries_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'library']
        # Maximum CTCAC distance: 1.0 mile standard, 2.0 miles rural
        max_lib_dist = 2.0 if is_rural else 1.0
        libraries_scorable = libraries_nearby[libraries_nearby['distance_miles'] <= max_lib_dist]
        library_points = self._score_libraries_complete(libraries_nearby, is_rural)
        results['amenities_found']['libraries'] = libraries_scorable.to_dict('records')
        results['scoring_summary']['library'] = library_points
        total_points += library_points.get('points', 0)
        
        # d) Grocery stores, supermarkets, and farmers markets - filter to CTCAC scoring distances
        grocery_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'grocery']
        # Maximum CTCAC distance: 1.5 miles standard, 3.0 miles rural
        max_grocery_dist = 3.0 if is_rural else 1.5
        grocery_scorable = grocery_nearby[grocery_nearby['distance_miles'] <= max_grocery_dist]
        grocery_points = self._score_grocery_complete(grocery_nearby, is_rural)
        results['amenities_found']['grocery'] = grocery_scorable.to_dict('records')
        results['scoring_summary']['grocery'] = grocery_points
        total_points += grocery_points.get('points', 0)
        
        # e) Schools - filter by school type distances
        schools_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'schools']
        # Different maximum distances for different school types
        schools_scorable = pd.DataFrame()
        if not schools_nearby.empty:
            # Elementary: 0.75 mi standard, 1.25 mi rural
            elem_max = 1.25 if is_rural else 0.75
            elem_schools = schools_nearby[schools_nearby['amenity_type'] == 'elementary']
            elem_scorable = elem_schools[elem_schools['distance_miles'] <= elem_max]
            # Middle: 1.0 mi standard, 1.5 mi rural
            mid_max = 1.5 if is_rural else 1.0
            mid_schools = schools_nearby[schools_nearby['amenity_type'] == 'middle']
            mid_scorable = mid_schools[mid_schools['distance_miles'] <= mid_max]
            # High: 1.5 mi standard, 2.5 mi rural
            high_max = 2.5 if is_rural else 1.5
            high_schools = schools_nearby[schools_nearby['amenity_type'] == 'high']
            high_scorable = high_schools[high_schools['distance_miles'] <= high_max]
            # Adult Ed: 1.0 mi standard, 1.5 mi rural
            adult_max = 1.5 if is_rural else 1.0
            adult_schools = schools_nearby[schools_nearby['amenity_type'] == 'adult_ed_community_college']
            adult_scorable = adult_schools[adult_schools['distance_miles'] <= adult_max]
            # Combine all scorable schools
            schools_scorable = pd.concat([elem_scorable, mid_scorable, high_scorable, adult_scorable])
        school_points = self._score_schools_complete(schools_nearby, is_rural, qualifying_development)
        results['amenities_found']['schools'] = schools_scorable.to_dict('records')
        results['scoring_summary']['schools'] = school_points
        total_points += sum([v for v in school_points.values() if isinstance(v, (int, float))])
        
        # f) Senior Centers (senior developments only)
        if project_type == 'senior':
            senior_centers_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'senior_center']
            # Maximum CTCAC distance: 0.75 miles standard, 1.5 miles rural
            max_senior_dist = 1.5 if is_rural else 0.75
            senior_scorable = senior_centers_nearby[senior_centers_nearby['distance_miles'] <= max_senior_dist]
            senior_points = self._score_senior_centers_complete(senior_centers_nearby, is_rural)
            results['amenities_found']['senior_centers'] = senior_scorable.to_dict('records')
            results['scoring_summary']['senior_center'] = senior_points
            total_points += senior_points.get('points', 0)
        
        # g) Special Needs - placeholder (would need special needs facility data)
        if project_type == 'special_needs':
            special_points = self._score_special_needs_placeholder(is_rural)
            results['scoring_summary']['special_needs'] = special_points
        
        # h) Medical facilities - filter to CTCAC scoring distances
        medical_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'medical']
        # Maximum CTCAC distance: 1.0 mile standard, 1.5 miles rural
        max_medical_dist = 1.5 if is_rural else 1.0
        medical_scorable = medical_nearby[medical_nearby['distance_miles'] <= max_medical_dist]
        medical_points = self._score_medical_complete(medical_nearby, is_rural)
        results['amenities_found']['medical'] = medical_scorable.to_dict('records')
        results['scoring_summary']['medical'] = medical_points
        total_points += medical_points.get('points', 0)
        
        # i) Pharmacies - filter to CTCAC scoring distances
        pharmacies_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'pharmacy']
        # Maximum CTCAC distance: 1.0 mile standard, 2.0 miles rural
        max_pharmacy_dist = 2.0 if is_rural else 1.0
        pharmacy_scorable = pharmacies_nearby[pharmacies_nearby['distance_miles'] <= max_pharmacy_dist]
        pharmacy_points = self._score_pharmacies_complete(pharmacies_nearby, is_rural)
        results['amenities_found']['pharmacies'] = pharmacy_scorable.to_dict('records')
        results['scoring_summary']['pharmacy'] = pharmacy_points
        total_points += pharmacy_points.get('points', 0)
        
        # j) Internet - not location-based, project amenity
        results['scoring_summary']['internet'] = {'note': 'Project amenity - not location based', 'points': 0}
        
        # k) Opportunity Area
        if opportunity_area_status in ['highest', 'high'] and new_construction and large_family:
            results['scoring_summary']['opportunity_area'] = {'points': 8, 'status': opportunity_area_status}
            total_points += 8
        else:
            results['scoring_summary']['opportunity_area'] = {'points': 0, 'status': 'not_applicable'}
        
        # Cap at 15 points maximum
        results['total_points'] = min(total_points, 15)
        return results
    
    def _score_libraries_complete(self, libraries_df, is_rural):
        """Score libraries based on complete CTCAC criteria"""
        if libraries_df.empty:
            return {'points': 0, 'closest_distance': None}
        
        min_distance = libraries_df['distance_miles'].min()
        distance_set = 'rural' if is_rural else 'standard'
        distances = self.distance_rules['library']['public_library'][distance_set]
        point_values = self.distance_rules['library']['public_library']['points']
        
        points = 0
        for i, max_dist in enumerate(distances):
            if min_distance <= max_dist:
                points = point_values[i]
                break
        
        return {'points': points, 'closest_distance': min_distance}
    
    def _score_schools_complete(self, schools_df, is_rural, qualifying_development):
        """Score schools based on complete CTCAC criteria"""
        if schools_df.empty:
            return {'elementary': 0, 'middle': 0, 'high': 0, 'adult_ed': 0}
        
        points = {'elementary': 0, 'middle': 0, 'high': 0, 'adult_ed': 0}
        distance_set = 'rural' if is_rural else 'standard'
        
        # Adult education/community college (no qualifying development requirement)
        adult_ed_schools = schools_df[schools_df['amenity_type'].str.contains('adult', case=False, na=False)]
        if not adult_ed_schools.empty:
            min_distance = adult_ed_schools['distance_miles'].min()
            distances = self.distance_rules['schools']['adult_ed_community_college'][distance_set]
            if min_distance <= distances[0]:
                points['adult_ed'] = self.distance_rules['schools']['adult_ed_community_college']['points'][0]
        
        # K-12 schools (only for qualifying developments)
        if qualifying_development:
            for school_type in ['elementary', 'middle', 'high']:
                schools_of_type = schools_df[schools_df['amenity_type'] == school_type]
                if not schools_of_type.empty:
                    min_distance = schools_of_type['distance_miles'].min()
                    distances = self.distance_rules['schools'][school_type][distance_set]
                    point_values = self.distance_rules['schools'][school_type]['points']
                    
                    for i, max_dist in enumerate(distances):
                        if min_distance <= max_dist:
                            points[school_type] = point_values[i]
                            break
        
        return points
    
    def _score_pharmacies_complete(self, pharmacies_df, is_rural):
        """Score pharmacies based on complete CTCAC criteria"""
        if pharmacies_df.empty:
            return {'points': 0, 'closest_distance': None}
        
        min_distance = pharmacies_df['distance_miles'].min()
        distance_set = 'rural' if is_rural else 'standard'
        distances = self.distance_rules['pharmacy']['pharmacy'][distance_set]
        point_values = self.distance_rules['pharmacy']['pharmacy']['points']
        
        points = 0
        for i, max_dist in enumerate(distances):
            if min_distance <= max_dist:
                points = point_values[i]
                break
        
        return {'points': points, 'closest_distance': min_distance}
    
    def _score_senior_centers_complete(self, senior_centers_df, is_rural):
        """Score senior centers based on complete CTCAC criteria"""
        if senior_centers_df.empty:
            return {'points': 0, 'closest_distance': None}
        
        min_distance = senior_centers_df['distance_miles'].min()
        distance_set = 'rural' if is_rural else 'standard'
        distances = self.distance_rules['senior_center']['daily_operated'][distance_set]
        point_values = self.distance_rules['senior_center']['daily_operated']['points']
        
        points = 0
        for i, max_dist in enumerate(distances):
            if min_distance <= max_dist:
                points = point_values[i]
                break
        
        return {'points': points, 'closest_distance': min_distance}
    
    # Placeholder scoring methods for missing data categories
    def _score_transit_complete(self, transit_df, is_rural, density_per_acre):
        """Score transit access according to CTCAC 2025 regulations with proper frequency and HQTA analysis"""
        if transit_df.empty:
            return {'points': 0, 'note': 'No transit stops found within scoring range'}
        
        # Separate HQTA areas from regular transit stops
        hqta_areas = transit_df[transit_df.get('amenity_type') == 'hqta'] if 'amenity_type' in transit_df.columns else pd.DataFrame()
        regular_stops = transit_df[transit_df.get('amenity_type') != 'hqta'] if 'amenity_type' in transit_df.columns else transit_df
        
        points = 0
        scoring_category = None
        scoring_method = None
        
        # Check if high density (>25 units/acre) for maximum 7 points
        is_high_density = density_per_acre is not None and density_per_acre > 25
        
        # Method 1: Check HQTA areas (can provide 7 points directly)
        if not hqta_areas.empty:
            closest_hqta_distance = hqta_areas['distance_miles'].min()
            
            if closest_hqta_distance <= 0.33:  # 1/3 mile
                if is_high_density:
                    points = 7
                    scoring_category = 'HQTA - High Density (7 pts)'
                    scoring_method = 'hqta_high_density'
                else:
                    points = 6
                    scoring_category = 'HQTA - Regular Service (6 pts)'
                    scoring_method = 'hqta_regular'
            elif closest_hqta_distance <= 0.5:  # 1/2 mile
                points = 5
                scoring_category = 'HQTA - Half Mile (5 pts)'
                scoring_method = 'hqta_half_mile'
        
        # Method 2: Check regular transit stops with frequency analysis
        if not regular_stops.empty and points < 7:  # Only check if we haven't achieved max points
            # Analyze stops within 1/3 mile for high-frequency service
            third_mile_stops = regular_stops[regular_stops['distance_miles'] <= 0.33]
            half_mile_stops = regular_stops[regular_stops['distance_miles'] <= 0.5]
            
            # Check for high-frequency service within 1/3 mile
            high_freq_points = self._analyze_transit_frequency(third_mile_stops, is_high_density)
            if high_freq_points > points:
                points = high_freq_points
                if high_freq_points == 7:
                    scoring_category = 'High-Frequency Transit - High Density (7 pts)'
                    scoring_method = 'frequency_high_density'
                elif high_freq_points == 6:
                    scoring_category = 'High-Frequency Transit - Regular (6 pts)'
                    scoring_method = 'frequency_regular'
            
            # Check for high-frequency service within 1/2 mile
            if points < 5:
                half_mile_freq_points = self._analyze_transit_frequency(half_mile_stops, False, max_points=5)
                if half_mile_freq_points > points:
                    points = half_mile_freq_points
                    scoring_category = 'High-Frequency Transit - Half Mile (5 pts)'
                    scoring_method = 'frequency_half_mile'
            
            # Fall back to basic transit scoring if no high-frequency service
            if points == 0:
                if not third_mile_stops.empty:
                    points = 4
                    scoring_category = 'Basic Transit - Third Mile (4 pts)'
                    scoring_method = 'basic_third_mile'
                elif not half_mile_stops.empty:
                    points = 3
                    scoring_category = 'Basic Transit - Half Mile (3 pts)'
                    scoring_method = 'basic_half_mile'
        
        # Overall statistics
        closest_distance = transit_df['distance_miles'].min()
        closest_stop = transit_df.iloc[0] if not transit_df.empty else None
        
        # Detailed stop analysis by distance
        stops_by_tier = {}
        for distance_threshold, tier_name in [(0.33, 'third_mile'), (0.5, 'half_mile')]:
            tier_stops = transit_df[transit_df['distance_miles'] <= distance_threshold]
            if not tier_stops.empty:
                stops_by_tier[tier_name] = {
                    'count': len(tier_stops),
                    'hqta_count': len(tier_stops[tier_stops.get('amenity_type') == 'hqta']) if 'amenity_type' in tier_stops.columns else 0,
                    'regular_count': len(tier_stops[tier_stops.get('amenity_type') != 'hqta']) if 'amenity_type' in tier_stops.columns else len(tier_stops),
                    'stops': tier_stops.head(3).to_dict('records')  # Top 3 closest
                }
        
        return {
            'points': points,
            'scoring_category': scoring_category,
            'scoring_method': scoring_method,
            'closest_distance': closest_distance,
            'closest_stop': closest_stop.to_dict() if closest_stop is not None else None,
            'stops_by_tier': stops_by_tier,
            'total_found': len(transit_df),
            'hqta_areas_found': len(hqta_areas) if not hqta_areas.empty else 0,
            'regular_stops_found': len(regular_stops) if not regular_stops.empty else 0,
            'high_density_bonus': is_high_density,
            'density_per_acre': density_per_acre
        }
    
    def _analyze_transit_frequency(self, stops_df, is_high_density, max_points=7):
        """Analyze transit stops for high-frequency service requirements (every 30 minutes, 7-9 AM and 4-6 PM)"""
        if stops_df.empty:
            return 0
        
        # Check for stops with sufficient service frequency
        # Look for: n_arrivals and n_hours_in_service data
        high_frequency_stops = []
        
        for idx, stop in stops_df.iterrows():
            # Check if stop has frequency data
            n_arrivals = stop.get('n_arrivals', 0)
            n_hours_in_service = stop.get('n_hours_in_service', 0)
            
            # CTCAC requirement: at least every 30 minutes during peak hours
            # Approximate: if 30+ arrivals per day and 8+ hours of service, likely meets frequency requirements
            if n_arrivals >= 30 and n_hours_in_service >= 8:
                high_frequency_stops.append(stop)
        
        # If we have high-frequency stops, award points based on density
        if high_frequency_stops:
            if is_high_density and max_points >= 7:
                return 7  # High density + high frequency = maximum points
            elif max_points >= 6:
                return 6  # High frequency without high density
            elif max_points >= 5:
                return 5  # High frequency at extended distance
        
        return 0  # No high-frequency service found
    
    def _score_parks_complete(self, parks_df, is_rural):
        """Score public parks and community centers according to CTCAC 2025 regulations"""
        if parks_df.empty:
            return {'points': 0, 'note': 'No public parks found within scoring range'}
        
        # CTCAC parks scoring distances (miles)
        distance_set = 'rural' if is_rural else 'standard'
        distances = self.distance_rules['public_park']['park_community_center'][distance_set]
        points_available = self.distance_rules['public_park']['park_community_center']['points']
        
        # Find closest park
        closest_distance = parks_df['distance_miles'].min()
        
        # Award points based on distance
        points = 0
        for i, max_distance in enumerate(distances):
            if closest_distance <= max_distance:
                points = points_available[i]
                break
        
        # Find parks within each scoring tier
        parks_by_tier = {}
        for i, max_distance in enumerate(distances):
            tier_parks = parks_df[parks_df['distance_miles'] <= max_distance]
            if not tier_parks.empty:
                parks_by_tier[f'{max_distance}_mile'] = {
                    'count': len(tier_parks),
                    'closest': tier_parks.iloc[0] if len(tier_parks) > 0 else None,
                    'points': points_available[i] if closest_distance <= max_distance else 0
                }
        
        return {
            'points': points,
            'closest_distance': closest_distance,
            'closest_park': parks_df.iloc[0] if not parks_df.empty else None,
            'parks_by_tier': parks_by_tier,
            'total_found': len(parks_df),
            'distance_set': distance_set
        }
    
    def _score_grocery_complete(self, grocery_df, is_rural):
        """Score grocery stores, supermarkets, and farmers markets according to CTCAC 2025 regulations"""
        if grocery_df.empty:
            return {'points': 0, 'note': 'No grocery stores found within scoring range'}
        
        # CTCAC grocery scoring has different rules for different store types
        points = 0
        scoring_details = {}
        
        # Separate stores by type
        full_scale = grocery_df[grocery_df['amenity_type'] == 'full_scale']
        neighborhood = grocery_df[grocery_df['amenity_type'] == 'neighborhood']
        farmers_markets = grocery_df[grocery_df['amenity_type'] == 'farmers_market']
        
        # Score full-scale supermarkets (25,000+ sq ft) - highest points
        if not full_scale.empty:
            closest_full_scale = full_scale['distance_miles'].min()
            distance_set = 'rural' if is_rural else 'standard'
            distances = self.distance_rules['grocery']['full_scale'][distance_set]
            points_available = self.distance_rules['grocery']['full_scale']['points']
            
            for i, max_distance in enumerate(distances):
                if closest_full_scale <= max_distance:
                    points = max(points, points_available[i])
                    scoring_details['full_scale'] = {
                        'points': points_available[i],
                        'distance': closest_full_scale,
                        'closest_store': full_scale.iloc[0].to_dict() if len(full_scale) > 0 else None
                    }
                    break
        
        # Score neighborhood stores (5,000+ sq ft) - medium points
        if not neighborhood.empty:
            closest_neighborhood = neighborhood['distance_miles'].min()
            distance_set = 'rural' if is_rural else 'standard'
            distances = self.distance_rules['grocery']['neighborhood'][distance_set]
            points_available = self.distance_rules['grocery']['neighborhood']['points']
            
            for i, max_distance in enumerate(distances):
                if closest_neighborhood <= max_distance:
                    neighborhood_points = points_available[i]
                    points = max(points, neighborhood_points)
                    scoring_details['neighborhood'] = {
                        'points': neighborhood_points,
                        'distance': closest_neighborhood,
                        'closest_store': neighborhood.iloc[0].to_dict() if len(neighborhood) > 0 else None
                    }
                    break
        
        # Score farmers markets (weekly, 5+ months) - lower points
        if not farmers_markets.empty:
            closest_farmers_market = farmers_markets['distance_miles'].min()
            distances = self.distance_rules['grocery']['farmers_market']['standard']
            points_available = self.distance_rules['grocery']['farmers_market']['points']
            
            for i, max_distance in enumerate(distances):
                if closest_farmers_market <= max_distance:
                    farmers_points = points_available[i]
                    points = max(points, farmers_points)
                    scoring_details['farmers_market'] = {
                        'points': farmers_points,
                        'distance': closest_farmers_market,
                        'closest_market': farmers_markets.iloc[0].to_dict() if len(farmers_markets) > 0 else None
                    }
                    break
        
        # Overall closest store
        closest_distance = grocery_df['distance_miles'].min()
        closest_store = grocery_df.iloc[0] if not grocery_df.empty else None
        
        return {
            'points': points,
            'closest_distance': closest_distance,
            'closest_store': closest_store.to_dict() if closest_store is not None else None,
            'scoring_details': scoring_details,
            'stores_by_type': {
                'full_scale': len(full_scale),
                'neighborhood': len(neighborhood),
                'farmers_markets': len(farmers_markets)
            },
            'total_found': len(grocery_df),
            'distance_set': 'rural' if is_rural else 'standard'
        }
    
    def _score_medical_complete(self, medical_df, is_rural):
        """Score medical facilities according to CTCAC 2025 regulations"""
        if medical_df.empty:
            return {'points': 0, 'note': 'No medical facilities found within scoring range'}
        
        # CTCAC medical facility scoring distances (miles)
        distance_set = 'rural' if is_rural else 'standard'
        distances = self.distance_rules['medical']['clinic_hospital'][distance_set]
        points_available = self.distance_rules['medical']['clinic_hospital']['points']
        
        # Find closest medical facility
        closest_distance = medical_df['distance_miles'].min()
        
        # Award points based on distance
        points = 0
        for i, max_distance in enumerate(distances):
            if closest_distance <= max_distance:
                points = points_available[i]
                break
        
        # Find facilities within each scoring tier
        facilities_by_tier = {}
        for i, max_distance in enumerate(distances):
            tier_facilities = medical_df[medical_df['distance_miles'] <= max_distance]
            if not tier_facilities.empty:
                facilities_by_tier[f'{max_distance}_mile'] = {
                    'count': len(tier_facilities),
                    'closest': tier_facilities.iloc[0] if len(tier_facilities) > 0 else None,
                    'points': points_available[i] if closest_distance <= max_distance else 0
                }
        
        return {
            'points': points,
            'closest_distance': closest_distance,
            'closest_facility': medical_df.iloc[0] if not medical_df.empty else None,
            'facilities_by_tier': facilities_by_tier,
            'total_found': len(medical_df),
            'distance_set': distance_set
        }
    
    def _score_special_needs_placeholder(self, is_rural):
        return {'points': 0, 'note': 'Special needs facility data not available - placeholder scoring'}
    
    def create_complete_amenity_map(self, site_lat, site_lng, site_name="Development Site", 
                                  is_rural=False, project_type='family', qualifying_development=False,
                                  new_construction=False, large_family=False, opportunity_area_status=None,
                                  density_per_acre=None, zoom_level=14, project_address=None):
        """Create complete interactive map with all CTCAC amenity categories"""
        
        # Calculate complete scores
        results = self.calculate_complete_amenity_scores(
            site_lat, site_lng, is_rural, project_type, density_per_acre,
            qualifying_development, new_construction, large_family, opportunity_area_status
        )
        
        # Create base map with scale
        m = folium.Map(location=[site_lat, site_lng], zoom_start=zoom_level)
        
        # Add scale bar (distance scale)
        from folium import plugins
        
        # Add measurement control
        plugins.MeasureControl(position='topright', active_color='blue', completed_color='red').add_to(m)
        
        # Add scale control for distance reference
        folium.plugins.MiniMap(toggle_display=True).add_to(m)
        
        # Add development site marker
        folium.Marker(
            [site_lat, site_lng],
            popup=f"""<b>{site_name}</b><br>
                     {project_address if project_address else 'Development Site'}<br>
                     Coordinates: {site_lat:.6f}, {site_lng:.6f}<br>
                     Total CTCAC Points: {results['total_points']}/15<br>
                     Project Type: {project_type.replace('_', ' ').title()}<br>
                     Use Rural Dist?: {'Yes' if is_rural else 'No'}""",
            icon=folium.Icon(color='red', icon='home')
        ).add_to(m)
        
        # Add scoring circles for different amenity types
        self._add_scoring_circles(m, site_lat, site_lng, is_rural, project_type, qualifying_development)
        
        # Add amenity markers with numbered symbols and detailed legend
        legend_data = self._add_enhanced_amenity_markers(m, results)
        
        # Add comprehensive legend with amenity details
        legend_html = self._create_enhanced_legend(results, legend_data)
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m, results
    
    def _add_scoring_circles(self, map_obj, site_lat, site_lng, is_rural, project_type, qualifying_development):
        """Add all relevant scoring circles to the map"""
        distance_set = 'rural' if is_rural else 'standard'
        
        # Libraries
        lib_distances = self.distance_rules['library']['public_library'][distance_set]
        for i, dist_miles in enumerate(lib_distances):
            circle = folium.Circle(
                [site_lat, site_lng],
                radius=dist_miles * 1609.34,
                popup=f"Library: {dist_miles} mi ({self.distance_rules['library']['public_library']['points'][i]} pts)",
                color='darkblue',  # Changed from purple to darker blue for visibility
                fillColor='darkblue',
                fillOpacity=0.0,  # Remove fill
                weight=2,
                dashArray='10,5'
            ).add_to(map_obj)
            
            # Add distance label
            folium.Marker(
                [site_lat + (dist_miles * 0.014), site_lng],  # Offset north
                icon=folium.DivIcon(html=f'<div style="font-size: 10pt; color: darkblue; font-weight: bold; background: white; padding: 1px 3px; border-radius: 3px;">{dist_miles} mi Library</div>')
            ).add_to(map_obj)
        
        # Pharmacies
        pharm_distances = self.distance_rules['pharmacy']['pharmacy'][distance_set]
        for i, dist_miles in enumerate(pharm_distances):
            folium.Circle(
                [site_lat, site_lng],
                radius=dist_miles * 1609.34,
                popup=f"Pharmacy: {dist_miles} mi ({self.distance_rules['pharmacy']['pharmacy']['points'][i]} pts)",
                color='hotpink',
                fillColor='hotpink',
                fillOpacity=0.0,  # Remove fill
                weight=2,
                dashArray='15,5'
            ).add_to(map_obj)
            
            # Add distance label
            folium.Marker(
                [site_lat + (dist_miles * 0.014), site_lng + (dist_miles * 0.01)],  # Offset northeast
                icon=folium.DivIcon(html=f'<div style="font-size: 10pt; color: hotpink; font-weight: bold; background: white; padding: 1px 3px; border-radius: 3px;">{dist_miles} mi Pharmacy</div>')
            ).add_to(map_obj)
        
        # Schools (if qualifying development)
        if qualifying_development:
            school_colors = [('elementary', 'green'), ('middle', 'orange'), ('high', 'red')]
            for j, (school_type, color) in enumerate(school_colors):
                distances = self.distance_rules['schools'][school_type][distance_set]
                for i, dist_miles in enumerate(distances):
                    folium.Circle(
                        [site_lat, site_lng],
                        radius=dist_miles * 1609.34,
                        popup=f"{school_type.title()} School: {dist_miles} mi ({self.distance_rules['schools'][school_type]['points'][i]} pts)",
                        color=color,
                        fillColor=color,
                        fillOpacity=0.0,  # Remove fill
                        weight=2,
                        dashArray='5,5'
                    ).add_to(map_obj)
                    
                    # Add distance label with different offset for each school type
                    offset_lat = dist_miles * 0.014
                    offset_lng = dist_miles * 0.01 * (j - 1)  # Spread labels horizontally
                    folium.Marker(
                        [site_lat + offset_lat, site_lng + offset_lng],
                        icon=folium.DivIcon(html=f'<div style="font-size: 10pt; color: {color}; font-weight: bold; background: white; padding: 1px 3px; border-radius: 3px;">{dist_miles} mi {school_type.title()}</div>')
                    ).add_to(map_obj)
        
        # Senior centers (if senior project)
        if project_type == 'senior':
            senior_distances = self.distance_rules['senior_center']['daily_operated'][distance_set]
            for i, dist_miles in enumerate(senior_distances):
                folium.Circle(
                    [site_lat, site_lng],
                    radius=dist_miles * 1609.34,
                    popup=f"Senior Center: {dist_miles} mi ({self.distance_rules['senior_center']['daily_operated']['points'][i]} pts)",
                    color='darkorange',
                    fillColor='darkorange',
                    fillOpacity=0.0,  # Remove fill
                    weight=2,
                    dashArray='20,5'
                ).add_to(map_obj)
                
                # Add distance label
                folium.Marker(
                    [site_lat + (dist_miles * 0.014), site_lng - (dist_miles * 0.01)],  # Offset northwest
                    icon=folium.DivIcon(html=f'<div style="font-size: 10pt; color: darkorange; font-weight: bold; background: white; padding: 1px 3px; border-radius: 3px;">{dist_miles} mi Senior</div>')
                ).add_to(map_obj)
    
    def _add_enhanced_amenity_markers(self, map_obj, results):
        """Add enhanced amenity markers with numbered symbols and category colors"""
        legend_data = {}
        
        # Define enhanced symbols and colors for each amenity category
        amenity_symbols = {
            'schools': {'icon': 'graduation-cap', 'color': 'blue', 'symbol': '🏫'},
            'library': {'icon': 'book', 'color': 'purple', 'symbol': '📚'},
            'pharmacy': {'icon': 'plus', 'color': 'pink', 'symbol': '💊'},
            'senior_center': {'icon': 'user', 'color': 'orange', 'symbol': '👥'},
            'medical': {'icon': 'plus-square', 'color': 'red', 'symbol': '🏥'},
            'transit': {'icon': 'bus', 'color': 'green', 'symbol': '🚌'},
            'public_park': {'icon': 'tree', 'color': 'darkgreen', 'symbol': '🌳'},
            'grocery': {'icon': 'shopping-cart', 'color': 'cadetblue', 'symbol': '🛒'},
            'special_needs': {'icon': 'heart', 'color': 'lightred', 'symbol': '❤️'}
        }
        
        marker_counter = 1
        
        for category, amenities in results['amenities_found'].items():
            if not amenities:
                continue
                
            # Map plural category names to singular for symbol lookup
            category_key = category.rstrip('s') if category.endswith('s') and category != 'special_needs' else category
            category_key = 'schools' if category_key == 'school' else category_key
            category_key = 'libraries' if category == 'libraries' else category_key
            category_key = 'pharmacies' if category == 'pharmacies' else category_key
            category_key = 'senior_centers' if category == 'senior_centers' else category_key
            category_key = 'public_parks' if category == 'public_parks' else category_key
            
            symbol_info = amenity_symbols.get(category_key, {'icon': 'info-sign', 'color': 'gray', 'symbol': '📍'})
            category_markers = []
            
            # Sort amenities by distance and limit based on category
            # Show more transit stops to include Metrolink stations  
            limit = 30 if category_key == 'transit' else 10
            sorted_amenities = sorted(amenities, key=lambda x: x.get('distance_miles', 999))
            
            # Debug: Check if Metrolink station is in the list
            if category_key == 'transit':
                metrolink_stations = [a for a in sorted_amenities if 'metrolink' in a.get('name', '').lower()]
                if metrolink_stations:
                    metrolink_dist = metrolink_stations[0].get('distance_miles', 999)
                    metrolink_rank = next(i for i, a in enumerate(sorted_amenities) if 'metrolink' in a.get('name', '').lower()) + 1
                    print(f"DEBUG: Metrolink station found at rank #{metrolink_rank}, distance {metrolink_dist:.3f} miles")
                else:
                    print("DEBUG: No Metrolink stations found in transit list")
            
            sorted_amenities = sorted_amenities[:limit]
            
            for i, amenity in enumerate(sorted_amenities):
                if 'latitude' in amenity and 'longitude' in amenity:
                    name = amenity.get('name', 'Unknown')
                    distance = amenity.get('distance_miles', 0)
                    amenity_type = amenity.get('amenity_type', category)
                    
                    # Create numbered marker
                    marker_number = marker_counter
                    marker_counter += 1
                    
                    # Add marker to map
                    popup_html = f"""
                    <b>#{marker_number}: {name}</b><br>
                    <b>Type:</b> {amenity_type.replace('_', ' ').title()}<br>
                    <b>Category:</b> {category.replace('_', ' ').title()}<br>
                    <b>Distance:</b> {distance:.1f} miles
                    """
                    
                    # Check if this amenity is beyond CTCAC scoring distance
                    marker_color = symbol_info['color']
                    beyond_scoring = False
                    
                    if category_key == 'transit' and distance > 0.5:
                        marker_color = '#dc3545'  # Red for non-scoring
                        beyond_scoring = True
                    elif category_key == 'public_parks' and distance > 0.75:  # Standard area
                        marker_color = '#dc3545'
                        beyond_scoring = True
                    elif category_key == 'libraries' and distance > 1.0:  # Standard area
                        marker_color = '#dc3545'
                        beyond_scoring = True
                    elif category_key == 'grocery' and distance > 1.5:  # Standard area
                        marker_color = '#dc3545'
                        beyond_scoring = True
                    elif category_key == 'medical' and distance > 1.0:  # Standard area
                        marker_color = '#dc3545'
                        beyond_scoring = True
                    elif category_key == 'pharmacies' and distance > 1.0:  # Standard area
                        marker_color = '#dc3545'
                        beyond_scoring = True
                    
                    # Create custom HTML icon with number
                    html_icon = f'''
                    <div style="text-align: center;">
                        <div style="background-color: {marker_color}; 
                                    color: white; 
                                    width: 24px; 
                                    height: 24px; 
                                    border-radius: 50%; 
                                    text-align: center; 
                                    font-weight: bold;
                                    line-height: 24px;
                                    font-size: 12px;
                                    border: 2px solid white;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                            {marker_number}
                        </div>
                    </div>
                    '''
                    
                    folium.Marker(
                        [amenity['latitude'], amenity['longitude']],
                        popup=popup_html,
                        tooltip=f"#{marker_number}: {name} ({distance:.1f} mi)",
                        icon=folium.DivIcon(html=html_icon)
                    ).add_to(map_obj)
                    
                    # Store legend data
                    category_markers.append({
                        'number': marker_number,
                        'name': name,
                        'distance': distance,
                        'type': amenity_type
                    })
            
            if category_markers:
                legend_data[category] = {
                    'symbol': symbol_info['symbol'],
                    'color': symbol_info['color'],
                    'markers': category_markers
                }
        
        return legend_data
    
    def _create_enhanced_legend(self, results, legend_data):
        """Create enhanced HTML legend with detailed amenity listings and distance requirements"""
        
        # CTCAC distance requirements for legend
        distance_requirements = {
            'transit': {
                'standard': {'max_distance': '0.5 mi', 'scoring_tiers': '1/3 mi (7 pts), 1/2 mi (6-3 pts)'},
                'rural': {'max_distance': '0.5 mi', 'scoring_tiers': '1/3 mi (7 pts), 1/2 mi (6-3 pts)'}
            },
            'public_parks': {
                'standard': {'max_distance': '0.75 mi', 'scoring_tiers': '1/2 mi (3 pts), 3/4 mi (2 pts)'},
                'rural': {'max_distance': '1.5 mi', 'scoring_tiers': '1.0 mi (3 pts), 1.5 mi (2 pts)'}
            },
            'library': {
                'standard': {'max_distance': '1.0 mi', 'scoring_tiers': '1/2 mi (3 pts), 1.0 mi (2 pts)'},
                'rural': {'max_distance': '2.0 mi', 'scoring_tiers': '1.0 mi (3 pts), 2.0 mi (2 pts)'}
            },
            'grocery': {
                'standard': {'max_distance': '1.5 mi', 'scoring_tiers': '1/4 mi (4 pts), 1/2 mi (3-5 pts), 1.0-1.5 mi (1-3 pts)'},
                'rural': {'max_distance': '3.0 mi', 'scoring_tiers': '1/2 mi (4 pts), 1.0 mi (3-5 pts), 2.0-3.0 mi (1-3 pts)'}
            },
            'schools': {
                'standard': {'max_distance': '1.5 mi', 'scoring_tiers': 'Elementary 3/4 mi (3 pts), High 1.5 mi (3 pts)'},
                'rural': {'max_distance': '2.5 mi', 'scoring_tiers': 'Elementary 1.25 mi (3 pts), High 2.5 mi (3 pts)'}
            },
            'medical': {
                'standard': {'max_distance': '1.0 mi', 'scoring_tiers': '1/2 mi (3 pts), 1.0 mi (2 pts)'},
                'rural': {'max_distance': '1.5 mi', 'scoring_tiers': '1.0 mi (3 pts), 1.5 mi (2 pts)'}
            },
            'pharmacy': {
                'standard': {'max_distance': '1.0 mi', 'scoring_tiers': '1/2 mi (2 pts), 1.0 mi (1 pt)'},
                'rural': {'max_distance': '2.0 mi', 'scoring_tiers': '1.0 mi (2 pts), 2.0 mi (1 pt)'}
            },
            'senior_center': {
                'standard': {'max_distance': '0.75 mi', 'scoring_tiers': '1/2 mi (3 pts), 3/4 mi (2 pts)'},
                'rural': {'max_distance': '1.5 mi', 'scoring_tiers': '1.0 mi (3 pts), 1.5 mi (2 pts)'}
            }
        }
        
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 420px; height: auto; max-height: 85vh; overflow-y: auto;
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:11px; padding: 12px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.3);">
        
        <h4 style="margin-top:0; color: #2E7D32;">CTCAC Amenity Analysis</h4>
        <div style="background-color: #E8F5E8; padding: 8px; border-radius: 3px; margin-bottom: 10px;">
            <p style="margin:2px;"><b>Total Score: {results['total_points']}/15 Points</b></p>
            <p style="margin:2px;"><b>Project Type:</b> {results['project_type'].replace('_', ' ').title()}</p>
            <p style="margin:2px;"><b>Use Rural Dist?:</b> {'Yes' if results['is_rural'] else 'No'}</p>
        </div>
        
        <h5 style="margin-bottom:8px;">📊 Scoring Summary:</h5>
        <div style="background-color: #F5F5F5; padding: 6px; border-radius: 3px; margin-bottom: 10px;">
        '''
        
        # Add scoring summary (skip Internet since it's not mapped)
        for category, score_data in results['scoring_summary'].items():
            if category == 'internet':  # Skip internet service
                continue
            if isinstance(score_data, dict):
                if 'points' in score_data:
                    points = score_data['points']
                    note = score_data.get('note', '')
                    legend_html += f"<p style='margin:2px;'><b>{category.replace('_', ' ').title()}:</b> {points} pts"
                    if note and "placeholder" not in note.lower() and "not location based" not in note.lower():
                        legend_html += f"<br><small style='color:#666;'>{note}</small>"
                    legend_html += "</p>"
                elif category == 'schools':
                    # Special handling for schools subcategories
                    total_pts = sum([v for v in score_data.values() if isinstance(v, (int, float))])
                    legend_html += f"<p style='margin:2px;'><b>Schools:</b> {total_pts} pts total</p>"
                    for subcat, pts in score_data.items():
                        if isinstance(pts, (int, float)) and pts > 0:
                            legend_html += f"<p style='margin:2px 2px 2px 15px;'>• {subcat.replace('_', ' ').title()}: {pts} pts</p>"
        
        legend_html += "</div>"
        
        # Add detailed amenity legend
        if legend_data:
            legend_html += "<h5 style='margin-bottom:8px;'>🗺️ Map Legend:</h5>"
            
            for category, data in legend_data.items():
                symbol = data['symbol']
                markers = data['markers']
                
                if markers:
                    # Get distance requirements for this category
                    dist_set = 'rural' if results['is_rural'] else 'standard'
                    
                    # Map plural category names to singular for distance requirements lookup
                    lookup_category = category
                    if category == 'libraries':
                        lookup_category = 'library'
                    elif category == 'pharmacies':
                        lookup_category = 'pharmacy'
                    elif category == 'public_parks':
                        lookup_category = 'public_parks'
                    
                    category_reqs = distance_requirements.get(lookup_category, {}).get(dist_set, {})
                    max_dist = category_reqs.get('max_distance', '')
                    scoring_tiers = category_reqs.get('scoring_tiers', '')
                    
                    legend_html += f"""
                    <div style="margin-bottom:8px; border-left: 3px solid {data['color']}; padding-left:8px;">
                        <h6 style="margin:2px 0; color:{data['color']};">{symbol} {category.replace('_', ' ').title()}</h6>
                        <div style="background-color: #f8f9fa; padding: 3px 6px; margin: 2px 0; border-radius: 3px; font-size: 9px; color: #495057;">
                            <b>Max Distance:</b> {max_dist}<br>
                            <b>Scoring:</b> {scoring_tiers}
                        </div>
                    """
                    
                    for marker in markers:
                        # Check if this marker has scoring information
                        points_display = ""
                        color_style = data['color']
                        
                        # Look up the original amenity data to see if it's beyond scoring distance
                        marker_name = marker['name']
                        marker_distance = marker['distance']
                        
                        # Calculate exact points for this amenity based on CTCAC thresholds (no rounding up)
                        points_display = ""
                        color_style = data['color']
                        
                        # Get the amenity points based on exact distance thresholds
                        is_rural = results['is_rural']
                        amenity_points = 0
                        
                        if category == 'transit':
                            if marker_distance <= 0.33:
                                amenity_points = 7 if results.get('high_density', False) else 6
                            elif marker_distance <= 0.5:
                                amenity_points = 5 if results.get('high_density', False) else 3
                            
                        elif category == 'public_parks':
                            distances = [1.0, 1.5] if is_rural else [0.5, 0.75]
                            points = [3, 2]
                            for i, dist in enumerate(distances):
                                if marker_distance <= dist:
                                    amenity_points = points[i]
                                    break
                                    
                        elif category == 'libraries':
                            distances = [1.0, 2.0] if is_rural else [0.5, 1.0]
                            points = [3, 2]
                            for i, dist in enumerate(distances):
                                if marker_distance <= dist:
                                    amenity_points = points[i]
                                    break
                                    
                        elif category == 'pharmacies':
                            distances = [1.0, 2.0] if is_rural else [0.5, 1.0]
                            points = [2, 1]
                            for i, dist in enumerate(distances):
                                if marker_distance <= dist:
                                    amenity_points = points[i]
                                    break
                                    
                        elif category == 'medical':
                            distances = [1.0, 1.5] if is_rural else [0.5, 1.0]
                            points = [3, 2]
                            for i, dist in enumerate(distances):
                                if marker_distance <= dist:
                                    amenity_points = points[i]
                                    break
                                    
                        elif category == 'schools':
                            # Schools scoring depends on school type and qualifying development
                            if results.get('qualifying_development', False):
                                # Determine school type from name
                                school_name = marker_name.lower()
                                if 'elementary' in school_name or 'elem' in school_name:
                                    distances = [0.75, 1.25] if is_rural else [0.25, 0.75]
                                    points = [3, 2]
                                    for i, dist in enumerate(distances):
                                        if marker_distance <= dist:
                                            amenity_points = points[i]
                                            break
                                elif 'middle' in school_name:
                                    distances = [1.0, 1.5] if is_rural else [0.5, 1.0]
                                    points = [3, 2]
                                    for i, dist in enumerate(distances):
                                        if marker_distance <= dist:
                                            amenity_points = points[i]
                                            break
                                elif 'high' in school_name:
                                    distances = [1.5, 2.5] if is_rural else [1.0, 1.5]
                                    points = [3, 2]
                                    for i, dist in enumerate(distances):
                                        if marker_distance <= dist:
                                            amenity_points = points[i]
                                            break
                                            
                        elif category == 'grocery':
                            # Grocery scoring is complex with different store types
                            # For legend display, show if it would score any points
                            max_distances = [3.0] if is_rural else [1.5]
                            if marker_distance <= max_distances[0]:
                                amenity_points = 1  # Minimum grocery points
                        
                        # Set display based on points
                        if amenity_points > 0:
                            points_display = f" • {amenity_points} pts"
                            color_style = data['color']  # Keep original color
                        else:
                            points_display = " • 0 pts"
                            color_style = '#dc3545'  # Red for non-scoring
                        
                        legend_html += f"""
                        <p style="margin:3px 0; font-size:10px; line-height:1.4;">
                            <span style="background-color:{color_style}; color:white; padding:1px 4px; border-radius:2px; font-weight:bold; margin-right:6px;">
                                #{marker['number']}
                            </span>
                            {marker['name']} ({marker['distance']:.2f} mi){points_display}
                        </p>
                        """
                    
                    legend_html += "</div>"
        
        legend_html += '''
        <hr style="margin:8px 0;">
        <div style="font-size:9px; color:#666;">
            <p style="margin:2px 0;"><b>🎯 Enhanced Features:</b></p>
            <p style="margin:1px 0;">✅ CTCAC distance requirements shown for each category</p>
            <p style="margin:1px 0;">🔴 Red markers/text = beyond CTCAC scoring distance (0 points)</p>
            <p style="margin:1px 0;">🚆 Metrolink stations included even if non-scoring</p>
            <p style="margin:4px 0 0 0;"><b>Legend:</b> Circles = scoring distances, Numbers = amenity markers</p>
        </div>
        </div>
        '''
        
        return legend_html
    
    def _create_complete_legend(self, results):
        """Create comprehensive HTML legend for the map"""
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 350px; height: auto; max-height: 80vh; overflow-y: auto;
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px;">
        <h4>CTCAC Complete Amenity Scoring</h4>
        <p><b>Total Points: {results['total_points']}/15</b></p>
        <p><b>Project Type:</b> {results['project_type'].title()}</p>
        <p><b>Rural Status:</b> {'Yes' if results['is_rural'] else 'No'}</p>
        <p><b>Qualifying Dev:</b> {'Yes' if results.get('qualifying_development', False) else 'No'}</p>
        <hr>
        <h5>Detailed Scoring:</h5>
        '''
        
        for category, score_data in results['scoring_summary'].items():
            if isinstance(score_data, dict):
                if 'points' in score_data:
                    points = score_data['points']
                    note = score_data.get('note', '')
                    legend_html += f"<p><b>{category.replace('_', ' ').title()}:</b> {points} pts"
                    if note:
                        legend_html += f"<br><small><i>{note}</i></small>"
                    legend_html += "</p>"
                elif category == 'schools':
                    # Special handling for schools subcategories
                    total_pts = sum([v for v in score_data.values() if isinstance(v, (int, float))])
                    legend_html += f"<p><b>Schools:</b> {total_pts} pts total</p>"
                    for subcat, pts in score_data.items():
                        if isinstance(pts, (int, float)) and pts > 0:
                            legend_html += f"<p style='margin-left:10px;'>• {subcat.replace('_', ' ').title()}: {pts} pts</p>"
        
        legend_html += '''
        <hr>
        <h5>Data Coverage:</h5>
        <p style="font-size:10px;">
        ✅ Schools, Libraries, Pharmacies, Senior Centers<br>
        🚧 Transit, Parks, Grocery, Medical (placeholders)<br>
        📋 Internet, Opportunity Area (project-specific)
        </p>
        <p><small>Circles show CTCAC scoring distances<br>
        Markers show actual amenity locations</small></p>
        </div>
        '''
        
        return legend_html

# Example usage functions for complete system
def analyze_complete_site_by_address(address, is_rural=False, project_type='family', 
                                   qualifying_development=False, new_construction=False, 
                                   large_family=False, opportunity_area_status=None,
                                   site_name=None, project_address=None):
    """Analyze a site by address with complete CTCAC amenity scoring"""
    mapper = CTCACAmenityMapperComplete()
    
    lat, lng = mapper.geocode_address(address)
    if lat is None:
        print(f"Could not geocode address: {address}")
        return None, None
    
    print(f"Analyzing site at: {lat:.6f}, {lng:.6f}")
    
    # Use provided site name or default to address
    if not site_name:
        site_name = address
    
    map_obj, results = mapper.create_complete_amenity_map(
        lat, lng, site_name, is_rural, project_type, qualifying_development,
        new_construction, large_family, opportunity_area_status,
        project_address=project_address if project_address else address
    )
    
    return map_obj, results

def analyze_complete_site_by_coordinates(lat, lng, site_name="Development Site", 
                                       is_rural=False, project_type='family',
                                       qualifying_development=False, new_construction=False,
                                       large_family=False, opportunity_area_status=None):
    """Analyze a site by coordinates with complete CTCAC amenity scoring"""
    mapper = CTCACAmenityMapperComplete()
    
    map_obj, results = mapper.create_complete_amenity_map(
        lat, lng, site_name, is_rural, project_type, qualifying_development,
        new_construction, large_family, opportunity_area_status
    )
    
    return map_obj, results

if __name__ == "__main__":
    # Example usage with complete system
    print("CTCAC Complete Amenity Mapper")
    print("============================")
    
    # Test with Sacramento coordinates - qualifying family development
    test_lat, test_lng = 38.7584, -121.2942
    
    print(f"Testing complete system with coordinates: {test_lat}, {test_lng}")
    
    mapper = CTCACAmenityMapperComplete()
    map_obj, results = mapper.create_complete_amenity_map(
        test_lat, test_lng, 
        "Test Development Site - Complete",
        is_rural=False,
        project_type='family',
        qualifying_development=True,  # Has 25%+ 3BR units
        new_construction=True,
        large_family=True,
        opportunity_area_status='high'  # Assume high resource area
    )
    
    # Save map
    output_file = "ctcac_complete_amenity_analysis.html"
    map_obj.save(output_file)
    print(f"Complete analysis map saved to: {output_file}")
    
    # Print comprehensive scoring summary
    print(f"\nComplete CTCAC Amenity Scoring Summary:")
    print(f"======================================")
    print(f"Total Points: {results['total_points']}/15")
    print(f"Project Type: {results['project_type'].title()}")
    print(f"Rural Status: {'Yes' if results['is_rural'] else 'No'}")
    print(f"Qualifying Development: {'Yes' if results.get('qualifying_development', False) else 'No'}")
    
    print(f"\nDetailed Category Scoring:")
    for category, scores in results['scoring_summary'].items():
        print(f"{category.replace('_', ' ').title()}: {scores}")
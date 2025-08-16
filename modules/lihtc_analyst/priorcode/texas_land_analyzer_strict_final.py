"""
Strict Final Texas Land Analyzer
Uses strict filtering to avoid gas stations, convenience stores, and incorrect amenities
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from geopy.distance import geodesic
import time
import json
from texas_proximity_analyzer_strict import TexasProximityAnalyzerStrict
import googlemaps

class TexasLandAnalyzerStrictFinal:
    """
    Final analyzer with strict amenity validation
    """
    
    # Top Texas cities by population
    TEXAS_CITY_POPULATIONS = {
        'Houston': 2304580,
        'San Antonio': 1434625,
        'Dallas': 1304379,
        'Austin': 961855,
        'Fort Worth': 918915,
        'El Paso': 678815,
        'Arlington': 394266,
        'Corpus Christi': 317863,
        'Plano': 285494,
        'Laredo': 255205,
        'Lubbock': 257141,
        'Garland': 246018,
        'Irving': 256684,
        'Amarillo': 200393,
        'Grand Prairie': 196100,
        'Brownsville': 186738,
        'Pasadena': 151950,
        'McKinney': 195308,
        'Mesquite': 150108,
        'Killeen': 153095,
        'McAllen': 142210,
        'Waco': 138486,
        'Carrollton': 133434,
        'Denton': 139869,
        'Midland': 132524
    }
    
    # Large counties for Two Mile Rule
    LARGE_COUNTIES = {
        'Harris': 4731145,
        'Dallas': 2613539,
        'Tarrant': 2110640,
        'Bexar': 2009324,
        'Travis': 1290188
    }
    
    def __init__(self, google_maps_api_key: str, 
                 schools_file: str = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/TX_Public_Schools/Schools_2024_to_2025.csv",
                 tdhca_project_file: str = None):
        """Initialize with strict proximity analyzer"""
        # Use strict proximity analyzer
        self.proximity_analyzer = TexasProximityAnalyzerStrict(
            google_maps_api_key=google_maps_api_key,
            schools_file=schools_file,
            cache_dir="./proximity_cache"
        )
        self.gmaps = googlemaps.Client(key=google_maps_api_key)
        
        # Load TDHCA data
        if tdhca_project_file and Path(tdhca_project_file).exists():
            self.tdhca_data = self.load_tdhca_data(tdhca_project_file)
        else:
            search_paths = [
                "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx",
                "./TX_TDHCA_Project_List_05252025.xlsx"
            ]
            for path in search_paths:
                if Path(path).exists():
                    self.tdhca_data = self.load_tdhca_data(path)
                    break
            else:
                print("⚠️ Warning: TDHCA project list not found")
                self.tdhca_data = None
        
        print(f"Strict Texas Land Analyzer initialized")
        print(f"✅ Using strict amenity filtering")
        print(f"✅ Texas public schools loaded")
        print(f"{'✅' if self.tdhca_data is not None else '❌'} TDHCA projects loaded")
    
    def load_tdhca_data(self, file_path: str) -> pd.DataFrame:
        """Load TDHCA project data"""
        print(f"Loading TDHCA data...")
        df = pd.read_excel(file_path)
        
        column_mapping = {
            'Development Name': 'Development Name',
            'Year': 'Year',
            'Latitude11': 'Latitude',
            'Longitude11': 'Longitude',
            'Total Units': 'Total Units',
            'Population Served': 'Population Served',
            'CT 2020': 'Census Tract',
            'Project City': 'City',
            'County': 'County'
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        if 'Year' in df.columns:
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        if 'Latitude' in df.columns:
            df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        if 'Longitude' in df.columns:
            df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        df = df.dropna(subset=['Latitude', 'Longitude'])
        print(f"Loaded {len(df)} TDHCA projects")
        return df
    
    def check_one_mile_three_year_rule(self, lat: float, lng: float, 
                                       current_year: int = 2025) -> Dict:
        """Check One Mile Three Year Rule"""
        if self.tdhca_data is None:
            return {
                'compliant': None,
                'competing_projects': [],
                'message': 'TDHCA data not available'
            }
        
        target_coords = (lat, lng)
        competing_projects = []
        
        recent_years = [current_year - 1, current_year - 2, current_year - 3]
        recent_projects = self.tdhca_data[self.tdhca_data['Year'].isin(recent_years)]
        
        for _, project in recent_projects.iterrows():
            project_coords = (project['Latitude'], project['Longitude'])
            
            try:
                distance = geodesic(target_coords, project_coords).miles
                if distance <= 1.0:
                    competing_projects.append({
                        'name': project.get('Development Name', 'Unknown'),
                        'year': int(project.get('Year', 0)),
                        'distance_miles': round(distance, 2),
                        'units': int(project.get('Total Units', 0)),
                        'population_served': project.get('Population Served', 'Unknown'),
                        'city': project.get('City', 'Unknown')
                    })
            except:
                continue
        
        competing_projects.sort(key=lambda x: x['distance_miles'])
        compliant = len(competing_projects) == 0
        
        return {
            'compliant': compliant,
            'competing_projects': competing_projects,
            'message': f"{'PASS' if compliant else 'FAIL'}: {len(competing_projects)} projects within 1 mile from last 3 years"
        }
    
    def get_google_ratings_for_projects(self, projects: List[Dict], max_projects: int = 3) -> List[Dict]:
        """Get Google ratings for TDHCA projects"""
        for i, project in enumerate(projects[:max_projects]):
            try:
                search_query = f"{project['name']} {project.get('city', '')} Texas apartment"
                places_result = self.gmaps.places(query=search_query)
                
                if places_result['results']:
                    place = places_result['results'][0]
                    place_details = self.gmaps.place(
                        place_id=place['place_id'],
                        fields=['rating', 'user_ratings_total']
                    )['result']
                    
                    project['google_rating'] = place_details.get('rating')
                    project['google_rating_count'] = place_details.get('user_ratings_total', 0)
                else:
                    project['google_rating'] = None
                    project['google_rating_count'] = 0
                
                time.sleep(0.1)
                
            except:
                project['google_rating'] = None
                project['google_rating_count'] = 0
        
        return projects
    
    def analyze_site(self, lat: float, lng: float, address: str, 
                    city: str, county: str) -> Dict:
        """Analyze a single site with strict filtering"""
        print(f"\nAnalyzing: {address}, {city}")
        print("  Using strict amenity filtering...")
        
        results = {
            'address': address,
            'city': city,
            'county': county,
            'latitude': lat,
            'longitude': lng,
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. Strict proximity analysis
        proximity_results = self.proximity_analyzer.analyze_site_proximity(lat, lng, address)
        results['proximity'] = proximity_results['distances']
        
        # 2. TDHCA competition
        print("  Checking TDHCA competition...")
        one_mile_check = self.check_one_mile_three_year_rule(lat, lng)
        results['one_mile_three_year_rule'] = one_mile_check
        
        if one_mile_check['competing_projects']:
            print("  Getting Google ratings for competing projects...")
            one_mile_check['competing_projects'] = self.get_google_ratings_for_projects(
                one_mile_check['competing_projects']
            )
        
        # 3. City population
        results['city_population'] = self.TEXAS_CITY_POPULATIONS.get(city)
        
        return results
    
    def analyze_multiple_sites(self, sites_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze multiple sites with strict filtering"""
        results = []
        
        for idx, row in sites_df.iterrows():
            try:
                print(f"\nProcessing site {idx + 1} of {len(sites_df)}")
                
                lat = row.get('Latitude')
                lng = row.get('Longitude')
                address = row.get('Address', '')
                city = row.get('City', '')
                county = row.get('County', '')
                
                if pd.isna(lat) or pd.isna(lng):
                    continue
                
                site_results = self.analyze_site(lat, lng, address, city, county)
                
                # Flatten for DataFrame
                flat_results = {
                    'original_index': idx,
                    'Address': address,
                    'City': city,
                    'County': county,
                    'Latitude': lat,
                    'Longitude': lng
                }
                
                # Add proximity results
                for key, value in site_results['proximity'].items():
                    flat_results[key] = value
                
                # Add competition results
                one_mile = site_results['one_mile_three_year_rule']
                flat_results['one_mile_compliant'] = one_mile['compliant']
                flat_results['one_mile_projects_count'] = len(one_mile['competing_projects'])
                
                if one_mile['competing_projects']:
                    nearest = one_mile['competing_projects'][0]
                    flat_results['nearest_lihtc_name'] = nearest['name']
                    flat_results['nearest_lihtc_distance'] = nearest['distance_miles']
                    flat_results['nearest_lihtc_year'] = nearest['year']
                    flat_results['nearest_lihtc_units'] = nearest['units']
                    flat_results['nearest_lihtc_rating'] = nearest.get('google_rating')
                
                flat_results['city_population'] = site_results.get('city_population')
                
                results.append(flat_results)
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing site {idx}: {e}")
                continue
        
        return pd.DataFrame(results)
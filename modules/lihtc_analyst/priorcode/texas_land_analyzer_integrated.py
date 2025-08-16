"""
Enhanced Texas Land Analyzer with Integrated TDHCA Competition Analysis
Combines Google Maps proximity scoring with TDHCA project list competition analysis
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
from texas_proximity_analyzer_improved import TexasProximityAnalyzerImproved as TexasProximityAnalyzerStrict
import googlemaps

from texas_city_populations_extended import TEXAS_CITY_POPULATIONS_EXTENDED
from get_city_population_census import CityPopulationFetcher

class TexasLandAnalyzerIntegrated:
    """
    Integrates proximity analysis with TDHCA competition rules
    """
    
    # Extended Texas cities by population - includes 100+ cities
    TEXAS_CITY_POPULATIONS = TEXAS_CITY_POPULATIONS_EXTENDED
    
    # Original top 25 for reference
    _TOP_25_CITIES = {
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
    
    # Counties with population > 1 million (for Two Mile Same Year Rule)
    LARGE_COUNTIES = {
        'Harris': 4731145,
        'Dallas': 2613539,
        'Tarrant': 2110640,
        'Bexar': 2009324,
        'Travis': 1290188
    }
    
    def __init__(self, google_maps_api_key: str, census_api_key: str = None, 
                 tdhca_project_file: str = None):
        """
        Initialize the integrated analyzer
        
        Args:
            google_maps_api_key: Google Maps API key for proximity analysis
            census_api_key: Census API key (optional, for non-hardcoded locations)
            tdhca_project_file: Path to TX_TDHCA_Project_List Excel file
        """
        # Initialize strict proximity analyzer with Texas schools
        self.proximity_analyzer = TexasProximityAnalyzerStrict(
            google_maps_api_key=google_maps_api_key,
            schools_file="/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/TX_Public_Schools/Schools_2024_to_2025.csv",
            cache_dir="./proximity_cache"
        )
        self.gmaps = googlemaps.Client(key=google_maps_api_key)
        
        self.census_api_key = census_api_key
        
        # Initialize population fetcher if census key available
        if census_api_key and census_api_key != "None":
            self.population_fetcher = CityPopulationFetcher(census_api_key)
        else:
            self.population_fetcher = None
        
        # Load TDHCA project data
        if tdhca_project_file and Path(tdhca_project_file).exists():
            self.tdhca_data = self.load_tdhca_data(tdhca_project_file)
        else:
            # Try to find the file in common locations
            search_paths = [
                "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx",
                "./TX_TDHCA_Project_List_05252025.xlsx",
                "../TX_TDHCA_Project_List_05252025.xlsx"
            ]
            for path in search_paths:
                if Path(path).exists():
                    self.tdhca_data = self.load_tdhca_data(path)
                    break
            else:
                print("⚠️ Warning: TDHCA project list not found. Competition analysis will be limited.")
                self.tdhca_data = None
        
        print(f"Texas Land Analyzer Integrated initialized with STRICT filtering")
        print(f"✅ Using Texas public schools dataset")
        print(f"✅ Strict amenity filtering enabled")
        print(f"TDHCA projects loaded: {'✅' if self.tdhca_data is not None else '❌'}")
        if self.tdhca_data is not None:
            print(f"Total TDHCA projects: {len(self.tdhca_data)}")
    
    def load_tdhca_data(self, file_path: str) -> pd.DataFrame:
        """Load and prepare TDHCA project data"""
        print(f"Loading TDHCA data from: {file_path}")
        df = pd.read_excel(file_path)
        
        # Clean and standardize columns
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
        
        # Rename columns if they exist
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Convert year to numeric
        if 'Year' in df.columns:
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        
        # Convert coordinates to numeric
        if 'Latitude' in df.columns:
            df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        if 'Longitude' in df.columns:
            df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        # Remove rows without valid coordinates
        df = df.dropna(subset=['Latitude', 'Longitude'])
        
        print(f"Loaded {len(df)} TDHCA projects with valid coordinates")
        return df
    
    def check_one_mile_three_year_rule(self, lat: float, lng: float, 
                                       current_year: int = 2025) -> Dict:
        """
        Check One Mile Three Year Rule for both 4% and 9% deals
        """
        if self.tdhca_data is None:
            return {
                'compliant': None,
                'competing_projects': [],
                'message': 'TDHCA data not available'
            }
        
        target_coords = (lat, lng)
        competing_projects = []
        
        # Filter for projects from the last 3 years
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
                        'distance_miles': round(distance, 3),
                        'units': int(project.get('Total Units', 0)),
                        'population_served': project.get('Population Served', 'Unknown'),
                        'city': project.get('City', 'Unknown'),
                        'address': f"{project.get('Development Name', 'Unknown')}, {project.get('City', 'Unknown')}"
                    })
            except Exception as e:
                print(f"Error calculating distance: {e}")
                continue
        
        # Sort by distance
        competing_projects.sort(key=lambda x: x['distance_miles'])
        
        compliant = len(competing_projects) == 0
        
        return {
            'compliant': compliant,
            'competing_projects': competing_projects,
            'message': f"{'PASS' if compliant else 'FAIL'}: {len(competing_projects)} competing projects within 1 mile from last 3 years"
        }
    
    def check_two_mile_same_year_rule(self, lat: float, lng: float, 
                                      county: str, current_year: int = 2025) -> Dict:
        """
        Check Two Mile Same Year Rule (9% only, large counties)
        """
        # Check if county is large enough
        if county not in self.LARGE_COUNTIES:
            return {
                'applicable': False,
                'compliant': True,
                'competing_projects': [],
                'message': f"Not applicable - {county} County population < 1 million"
            }
        
        if self.tdhca_data is None:
            return {
                'applicable': True,
                'compliant': None,
                'competing_projects': [],
                'message': 'TDHCA data not available'
            }
        
        target_coords = (lat, lng)
        same_year_projects = []
        
        # Filter for projects from current year
        current_year_projects = self.tdhca_data[self.tdhca_data['Year'] == current_year]
        
        for _, project in current_year_projects.iterrows():
            project_coords = (project['Latitude'], project['Longitude'])
            
            try:
                distance = geodesic(target_coords, project_coords).miles
                if distance <= 2.0:
                    same_year_projects.append({
                        'name': project.get('Development Name', 'Unknown'),
                        'distance_miles': round(distance, 3),
                        'units': int(project.get('Total Units', 0)),
                        'city': project.get('City', 'Unknown')
                    })
            except Exception as e:
                print(f"Error calculating distance: {e}")
                continue
        
        compliant = len(same_year_projects) == 0
        
        return {
            'applicable': True,
            'compliant': compliant,
            'competing_projects': same_year_projects,
            'message': f"Large county ({county}) - {'PASS' if compliant else 'FAIL'}: {len(same_year_projects)} projects within 2 miles same year"
        }
    
    def calculate_tdhca_same_tract_score(self, census_tract: str, 
                                         current_year: int = 2025) -> Dict:
        """
        Calculate TDHCA same census tract scoring (9% only)
        """
        if self.tdhca_data is None or not census_tract:
            return {
                'score': None,
                'most_recent_project': None,
                'message': 'Unable to calculate - missing data'
            }
        
        # Find projects in same census tract
        same_tract = self.tdhca_data[self.tdhca_data['Census Tract'] == census_tract]
        
        if len(same_tract) == 0:
            return {
                'score': 5,
                'most_recent_project': None,
                'message': '5 points - No competing projects in census tract'
            }
        
        # Find most recent project
        most_recent_year = same_tract['Year'].max()
        years_ago = current_year - most_recent_year
        
        # Calculate score based on years
        if years_ago >= 20:
            score = 5
            message = f"5 points - Most recent project {years_ago} years ago"
        elif years_ago >= 15:
            score = 4
            message = f"4 points - Most recent project {years_ago} years ago"
        elif years_ago >= 10:
            score = 3
            message = f"3 points - Most recent project {years_ago} years ago"
        else:
            score = 0
            message = f"0 points - Most recent project only {years_ago} years ago"
            
            # Add borderline notifications
            if years_ago == 9:
                message += " (will be 3pts in 2026)"
            elif years_ago == 14:
                message += " (will be 4pts in 2026)"
            elif years_ago == 19:
                message += " (will be 5pts in 2026)"
        
        most_recent = same_tract[same_tract['Year'] == most_recent_year].iloc[0]
        
        return {
            'score': score,
            'most_recent_project': {
                'name': most_recent.get('Development Name', 'Unknown'),
                'year': int(most_recent_year),
                'units': int(most_recent.get('Total Units', 0))
            },
            'message': message
        }
    
    def get_google_ratings_for_projects(self, projects: List[Dict]) -> List[Dict]:
        """
        Get Google review ratings for TDHCA projects
        """
        for project in projects:
            try:
                # Search for the project by name and city
                search_query = f"{project['name']} {project.get('city', '')} Texas apartment"
                places_result = self.gmaps.places(query=search_query)
                
                if places_result['results']:
                    place = places_result['results'][0]
                    place_details = self.gmaps.place(
                        place_id=place['place_id'],
                        fields=['rating', 'user_ratings_total', 'reviews']
                    )['result']
                    
                    project['google_rating'] = place_details.get('rating')
                    project['google_rating_count'] = place_details.get('user_ratings_total', 0)
                else:
                    project['google_rating'] = None
                    project['google_rating_count'] = 0
                
                # Respect API rate limits
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error getting Google rating for {project['name']}: {e}")
                project['google_rating'] = None
                project['google_rating_count'] = 0
        
        return projects
    
    def analyze_land_site_comprehensive(self, lat: float, lng: float, 
                                       address: str, city: str, 
                                       county: str, census_tract: str = None,
                                       check_9pct_rules: bool = True) -> Dict:
        """
        Comprehensive analysis combining proximity and TDHCA competition rules
        """
        print(f"\nAnalyzing site: {address}, {city}")
        
        results = {
            'address': address,
            'city': city,
            'county': county,
            'census_tract': census_tract,
            'latitude': lat,
            'longitude': lng,
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. Run strict proximity analysis
        print("Running proximity analysis with strict filtering...")
        proximity_results = self.proximity_analyzer.analyze_site_proximity(lat, lng, address)
        results['proximity_analysis'] = proximity_results
        
        # 2. Check TDHCA competition rules
        print("Checking TDHCA competition rules...")
        
        # One Mile Three Year Rule (both 4% and 9%)
        one_mile_check = self.check_one_mile_three_year_rule(lat, lng)
        results['one_mile_three_year_rule'] = one_mile_check
        
        # Get Google ratings for competing projects if any found
        if one_mile_check['competing_projects']:
            print("Getting Google ratings for competing projects...")
            one_mile_check['competing_projects'] = self.get_google_ratings_for_projects(
                one_mile_check['competing_projects'][:5]  # Limit to top 5 closest
            )
        
        # 9% specific rules
        if check_9pct_rules:
            # Two Mile Same Year Rule
            two_mile_check = self.check_two_mile_same_year_rule(lat, lng, county)
            results['two_mile_same_year_rule'] = two_mile_check
            
            # Same Census Tract Scoring
            if census_tract:
                tract_score = self.calculate_tdhca_same_tract_score(census_tract)
                results['same_tract_score'] = tract_score
        
        # 3. Get city population
        city_population = self.TEXAS_CITY_POPULATIONS.get(city)
        if city_population:
            results['city_population'] = city_population
            results['city_population_source'] = 'hardcoded'
        elif self.population_fetcher:
            # Try Census API if not in hardcoded list
            city_population = self.population_fetcher.get_population(city, "TX")
            if city_population:
                results['city_population'] = city_population
                results['city_population_source'] = 'census_api'
                # Update our hardcoded list for future use
                self.TEXAS_CITY_POPULATIONS[city] = city_population
            else:
                results['city_population'] = None
                results['city_population_source'] = 'not_found'
        else:
            results['city_population'] = None
            results['city_population_source'] = 'no_census_api_key'
        
        return results
    
    def analyze_multiple_sites(self, sites_df: pd.DataFrame, 
                              check_9pct_rules: bool = True) -> pd.DataFrame:
        """
        Analyze multiple sites with comprehensive scoring
        """
        results = []
        
        for idx, row in sites_df.iterrows():
            try:
                print(f"\nProcessing site {idx + 1} of {len(sites_df)}")
                
                # Get required fields
                lat = row.get('Latitude')
                lng = row.get('Longitude')
                address = row.get('Address', '')
                city = row.get('City', '')
                county = row.get('County', '')
                census_tract = row.get('Census_Tract', row.get('CT_2020', ''))
                
                if pd.isna(lat) or pd.isna(lng):
                    print(f"Skipping site {idx + 1} - missing coordinates")
                    continue
                
                # Run comprehensive analysis
                site_results = self.analyze_land_site_comprehensive(
                    lat, lng, address, city, county, census_tract, check_9pct_rules
                )
                
                # Flatten results for DataFrame
                flat_results = {
                    'original_index': idx,
                    'Address': address,
                    'City': city,
                    'County': county,
                    'Census_Tract': census_tract,
                    'Latitude': lat,
                    'Longitude': lng
                }
                
                # Add proximity distances (no scores in strict mode)
                distances = site_results['proximity_analysis']['distances']
                for key, value in distances.items():
                    flat_results[key] = value
                
                # Add competition results
                one_mile = site_results['one_mile_three_year_rule']
                flat_results['one_mile_compliant'] = one_mile['compliant']
                flat_results['one_mile_competing_count'] = len(one_mile['competing_projects'])
                if one_mile['competing_projects']:
                    nearest = one_mile['competing_projects'][0]
                    flat_results['nearest_lihtc_name'] = nearest['name']
                    flat_results['nearest_lihtc_distance'] = nearest['distance_miles']
                    flat_results['nearest_lihtc_year'] = nearest['year']
                    flat_results['nearest_lihtc_units'] = nearest['units']
                    flat_results['nearest_lihtc_rating'] = nearest.get('google_rating')
                
                # Add 9% specific results
                if check_9pct_rules:
                    if 'two_mile_same_year_rule' in site_results:
                        two_mile = site_results['two_mile_same_year_rule']
                        flat_results['two_mile_applicable'] = two_mile['applicable']
                        flat_results['two_mile_compliant'] = two_mile.get('compliant')
                    
                    if 'same_tract_score' in site_results:
                        tract = site_results['same_tract_score']
                        flat_results['same_tract_points'] = tract['score']
                        flat_results['same_tract_message'] = tract['message']
                
                # Determine eligibility based on One Mile Rule
                if not site_results['one_mile_three_year_rule']['compliant']:
                    flat_results['eligibility'] = 'INELIGIBLE - One Mile Rule Violation'
                else:
                    flat_results['eligibility'] = 'ELIGIBLE'
                
                # Add city population if available
                flat_results['city_population'] = site_results.get('city_population')
                
                results.append(flat_results)
                
                # Respect API rate limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing site {idx}: {e}")
                continue
        
        return pd.DataFrame(results)


def main():
    """
    Example usage of the integrated analyzer
    """
    # Configuration
    GOOGLE_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'AIzaSyBlOVHaaTw9nbgBlIuF90xlXHbgfzvUWAM')
    CENSUS_API_KEY = os.environ.get('CENSUS_API_KEY')  # Optional
    
    # Initialize analyzer
    analyzer = TexasLandAnalyzerIntegrated(
        google_maps_api_key=GOOGLE_API_KEY,
        census_api_key=CENSUS_API_KEY
    )
    
    # Example: Analyze a single site
    sample_analysis = analyzer.analyze_land_site_comprehensive(
        lat=29.7604,
        lng=-95.3698,
        address="1000 Main St",
        city="Houston",
        county="Harris",
        census_tract="48201100000"
    )
    
    print(json.dumps(sample_analysis, indent=2, default=str))


if __name__ == "__main__":
    main()
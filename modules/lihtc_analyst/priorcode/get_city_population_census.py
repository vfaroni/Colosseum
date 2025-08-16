"""
Get city population using Census API for cities not in hardcoded list
"""

import requests
import json
from pathlib import Path
from typing import Optional

class CityPopulationFetcher:
    def __init__(self, census_api_key: str, cache_dir: str = "./population_cache"):
        self.census_api_key = census_api_key
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Import hardcoded populations
        from texas_city_populations_extended import TEXAS_CITY_POPULATIONS_EXTENDED
        self.hardcoded_pops = TEXAS_CITY_POPULATIONS_EXTENDED
        
        # Load cache
        self.cache_file = self.cache_dir / "texas_city_populations.json"
        self.cache = self.load_cache()
    
    def load_cache(self) -> dict:
        """Load cached populations"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def get_population(self, city: str, state: str = "TX") -> Optional[int]:
        """
        Get population for a city, checking in order:
        1. Hardcoded list
        2. Cache
        3. Census API
        """
        # Check hardcoded first
        if city in self.hardcoded_pops:
            return self.hardcoded_pops[city]
        
        # Check cache
        cache_key = f"{city}, {state}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try Census API if we have a key
        if self.census_api_key and self.census_api_key != "None":
            pop = self.fetch_from_census(city, state)
            if pop:
                self.cache[cache_key] = pop
                self.save_cache()
                return pop
        
        return None
    
    def fetch_from_census(self, city: str, state: str) -> Optional[int]:
        """Fetch population from Census API"""
        try:
            # Census API endpoint for places
            url = f"https://api.census.gov/data/2020/dec/pl"
            
            # Parameters for the API call
            params = {
                'get': 'P1_001N,NAME',  # Total population and name
                'for': f'place:*',       # All places
                'in': f'state:48',       # Texas FIPS code
                'key': self.census_api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Search for the city in results
                for row in data[1:]:  # Skip header
                    place_name = row[1]
                    # Census format is "City city, Texas"
                    if place_name and city.lower() in place_name.lower():
                        population = int(row[0])
                        print(f"Found {city} in Census data: {population:,}")
                        return population
                        
        except Exception as e:
            print(f"Census API error for {city}: {e}")
        
        return None
    
    def update_all_cities(self, cities_list: list):
        """Update cache with a list of cities"""
        print(f"Updating population data for {len(cities_list)} cities...")
        
        updated = 0
        for city in cities_list:
            if city and city not in self.hardcoded_pops and f"{city}, TX" not in self.cache:
                pop = self.get_population(city, "TX")
                if pop:
                    updated += 1
                    
        print(f"Updated {updated} cities in cache")
        return updated
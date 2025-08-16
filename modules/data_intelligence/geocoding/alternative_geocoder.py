#!/usr/bin/env python3
"""
Alternative Geocoding System for Colosseum Platform
Replaces Position Stack due to their ongoing technical issues
Supports multiple geocoding providers with fallback options

Author: Strike Leader
Date: 2025-08-09
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime
import hashlib

class AlternativeGeocoder:
    """Multi-provider geocoding system with fallback support"""
    
    def __init__(self, cache_dir: str = None):
        """Initialize geocoder with caching support"""
        self.cache_dir = Path(cache_dir or "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/cache/geocoding")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Provider configurations
        self.providers = {
            'nominatim': {
                'name': 'OpenStreetMap Nominatim',
                'enabled': True,
                'rate_limit': 1.0,  # 1 request per second
                'priority': 1
            },
            'census': {
                'name': 'US Census Geocoder',
                'enabled': True,
                'rate_limit': 0.1,  # 10 requests per second
                'priority': 2
            },
            'mapbox': {
                'name': 'Mapbox',
                'enabled': False,  # Requires API key
                'api_key': None,
                'rate_limit': 0.01,  # 100 requests per second
                'priority': 3
            },
            'google': {
                'name': 'Google Maps',
                'enabled': False,  # Requires API key
                'api_key': None,
                'rate_limit': 0.02,  # 50 requests per second
                'priority': 4
            }
        }
        
        self.last_request_time = {}
        
    def geocode(self, address: str, city: str = None, state: str = None, 
                zip_code: str = None, provider: str = None) -> Optional[Dict]:
        """
        Geocode an address using available providers
        
        Args:
            address: Street address
            city: City name
            state: State code (e.g., 'CA')
            zip_code: ZIP code
            provider: Specific provider to use (optional)
            
        Returns:
            Dict with latitude, longitude, and metadata
        """
        # Build full address string
        full_address = self._build_address(address, city, state, zip_code)
        
        # Check cache first
        cached = self._check_cache(full_address)
        if cached:
            self.logger.info(f"Cache hit for: {full_address}")
            return cached
        
        # Try specified provider or iterate through available providers
        if provider and provider in self.providers:
            providers_to_try = [provider]
        else:
            providers_to_try = sorted(
                [p for p, config in self.providers.items() if config['enabled']],
                key=lambda x: self.providers[x]['priority']
            )
        
        for provider_name in providers_to_try:
            try:
                result = self._geocode_with_provider(provider_name, full_address)
                if result:
                    # Cache successful result
                    self._save_to_cache(full_address, result)
                    return result
            except Exception as e:
                self.logger.warning(f"Provider {provider_name} failed: {str(e)}")
                continue
        
        self.logger.error(f"All providers failed for address: {full_address}")
        return None
    
    def _build_address(self, address: str, city: str = None, 
                       state: str = None, zip_code: str = None) -> str:
        """Build full address string from components"""
        parts = [address]
        if city:
            parts.append(city)
        if state:
            parts.append(state)
        if zip_code:
            parts.append(zip_code)
        return ', '.join(filter(None, parts))
    
    def _geocode_with_provider(self, provider: str, address: str) -> Optional[Dict]:
        """Geocode using specific provider"""
        
        # Rate limiting
        self._enforce_rate_limit(provider)
        
        if provider == 'nominatim':
            return self._geocode_nominatim(address)
        elif provider == 'census':
            return self._geocode_census(address)
        elif provider == 'mapbox':
            return self._geocode_mapbox(address)
        elif provider == 'google':
            return self._geocode_google(address)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _geocode_nominatim(self, address: str) -> Optional[Dict]:
        """Geocode using OpenStreetMap Nominatim (FREE)"""
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'us'
        }
        headers = {
            'User-Agent': 'Colosseum LIHTC Platform/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                result = data[0]
                return {
                    'latitude': float(result['lat']),
                    'longitude': float(result['lon']),
                    'formatted_address': result.get('display_name', ''),
                    'provider': 'nominatim',
                    'confidence': float(result.get('importance', 0)),
                    'timestamp': datetime.now().isoformat()
                }
        return None
    
    def _geocode_census(self, address: str) -> Optional[Dict]:
        """Geocode using US Census Geocoder (FREE, US only)"""
        url = 'https://geocoding.geo.census.gov/geocoder/locations/onelineaddress'
        params = {
            'address': address,
            'benchmark': 'Public_AR_Current',
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('result', {}).get('addressMatches'):
                match = data['result']['addressMatches'][0]
                coords = match['coordinates']
                return {
                    'latitude': coords['y'],
                    'longitude': coords['x'],
                    'formatted_address': match.get('matchedAddress', ''),
                    'provider': 'census',
                    'confidence': 1.0,  # Census doesn't provide confidence
                    'timestamp': datetime.now().isoformat()
                }
        return None
    
    def _geocode_mapbox(self, address: str) -> Optional[Dict]:
        """Geocode using Mapbox (requires API key)"""
        api_key = self.providers['mapbox'].get('api_key')
        if not api_key:
            raise ValueError("Mapbox API key not configured")
        
        url = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json'
        params = {
            'access_token': api_key,
            'country': 'US',
            'limit': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('features'):
                feature = data['features'][0]
                return {
                    'latitude': feature['center'][1],
                    'longitude': feature['center'][0],
                    'formatted_address': feature.get('place_name', ''),
                    'provider': 'mapbox',
                    'confidence': feature.get('relevance', 0),
                    'timestamp': datetime.now().isoformat()
                }
        return None
    
    def _geocode_google(self, address: str) -> Optional[Dict]:
        """Geocode using Google Maps (requires API key)"""
        api_key = self.providers['google'].get('api_key')
        if not api_key:
            raise ValueError("Google Maps API key not configured")
        
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {
            'address': address,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                result = data['results'][0]
                location = result['geometry']['location']
                return {
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'formatted_address': result.get('formatted_address', ''),
                    'provider': 'google',
                    'confidence': 1.0 if result['geometry'].get('location_type') == 'ROOFTOP' else 0.8,
                    'timestamp': datetime.now().isoformat()
                }
        return None
    
    def _enforce_rate_limit(self, provider: str):
        """Enforce rate limiting for provider"""
        rate_limit = self.providers[provider]['rate_limit']
        
        if provider in self.last_request_time:
            elapsed = time.time() - self.last_request_time[provider]
            if elapsed < rate_limit:
                time.sleep(rate_limit - elapsed)
        
        self.last_request_time[provider] = time.time()
    
    def _check_cache(self, address: str) -> Optional[Dict]:
        """Check if address is in cache"""
        cache_key = hashlib.md5(address.lower().encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Cache read error: {str(e)}")
        
        return None
    
    def _save_to_cache(self, address: str, result: Dict):
        """Save geocoding result to cache"""
        cache_key = hashlib.md5(address.lower().encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            result['cached_address'] = address
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Cache write error: {str(e)}")
    
    def batch_geocode(self, addresses: List[Dict], provider: str = None) -> List[Dict]:
        """
        Geocode multiple addresses
        
        Args:
            addresses: List of dicts with address components
            provider: Specific provider to use (optional)
            
        Returns:
            List of geocoding results
        """
        results = []
        total = len(addresses)
        
        for i, addr_dict in enumerate(addresses, 1):
            self.logger.info(f"Geocoding {i}/{total}: {addr_dict.get('address', '')}")
            
            result = self.geocode(
                address=addr_dict.get('address', ''),
                city=addr_dict.get('city'),
                state=addr_dict.get('state'),
                zip_code=addr_dict.get('zip_code'),
                provider=provider
            )
            
            if result:
                result['original'] = addr_dict
                results.append(result)
            else:
                results.append({
                    'error': 'Geocoding failed',
                    'original': addr_dict
                })
        
        return results
    
    def configure_api_key(self, provider: str, api_key: str):
        """Configure API key for paid providers"""
        if provider in ['mapbox', 'google']:
            self.providers[provider]['api_key'] = api_key
            self.providers[provider]['enabled'] = True
            self.logger.info(f"API key configured for {provider}")
        else:
            raise ValueError(f"Provider {provider} doesn't use API keys")
    
    def get_provider_status(self) -> Dict:
        """Get status of all providers"""
        status = {}
        for name, config in self.providers.items():
            status[name] = {
                'name': config['name'],
                'enabled': config['enabled'],
                'has_api_key': bool(config.get('api_key')) if name in ['mapbox', 'google'] else 'N/A',
                'priority': config['priority']
            }
        return status


def main():
    """Test the alternative geocoding system"""
    print("Alternative Geocoding System for Colosseum Platform")
    print("=" * 60)
    
    # Initialize geocoder
    geocoder = AlternativeGeocoder()
    
    # Show provider status
    print("\nProvider Status:")
    for provider, status in geocoder.get_provider_status().items():
        print(f"  {status['name']}: {'✅ Enabled' if status['enabled'] else '❌ Disabled'}")
    
    # Test addresses
    test_addresses = [
        {
            'address': '1600 Pennsylvania Avenue NW',
            'city': 'Washington',
            'state': 'DC',
            'zip_code': '20500'
        },
        {
            'address': '350 Fifth Avenue',
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10118'
        },
        {
            'address': '1 Apple Park Way',
            'city': 'Cupertino',
            'state': 'CA',
            'zip_code': '95014'
        }
    ]
    
    print("\nTesting geocoding with free providers:")
    print("-" * 40)
    
    for addr in test_addresses:
        full_addr = f"{addr['address']}, {addr['city']}, {addr['state']} {addr['zip_code']}"
        print(f"\nAddress: {full_addr}")
        
        result = geocoder.geocode(**addr)
        
        if result:
            print(f"  Provider: {result['provider']}")
            print(f"  Latitude: {result['latitude']}")
            print(f"  Longitude: {result['longitude']}")
            print(f"  Confidence: {result.get('confidence', 'N/A')}")
        else:
            print("  ❌ Geocoding failed")
    
    print("\n" + "=" * 60)
    print("Alternative geocoding system ready for production use!")
    print("FREE providers (Nominatim, Census) are enabled by default.")
    print("Add API keys for Mapbox or Google if higher volume needed.")


if __name__ == "__main__":
    main()
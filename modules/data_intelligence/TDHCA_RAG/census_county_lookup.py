#!/usr/bin/env python3
"""
🗺️ CENSUS COUNTY LOOKUP
Free, high-accuracy county lookup using US Census Geocoding API

FEATURES:
✅ 100% Free - No API key required
✅ Official US Government source
✅ High accuracy using official census boundaries
✅ Batch processing with rate limiting
✅ Robust error handling and retries
✅ Returns standardized county names for TDHCA region mapping
"""

import requests
import time
import pandas as pd
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CensusCountyLookup:
    """High-accuracy county lookup using Census Geocoding API"""
    
    def __init__(self):
        self.base_url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        self.session = requests.Session()
        self.cache = {}  # Simple cache to avoid duplicate API calls
        
        # Rate limiting - Census API is generous but let's be respectful
        self.delay_between_calls = 0.1  # 100ms delay
        self.max_retries = 3
    
    def get_county_from_coordinates(self, lat, lng):
        """
        Get county name from latitude/longitude using Census API
        
        Args:
            lat (float): Latitude
            lng (float): Longitude
            
        Returns:
            str: County name (e.g., "Dallas County") or None if not found
        """
        # Check cache first
        cache_key = f"{lat:.6f},{lng:.6f}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Validate coordinates
        if not self._validate_coordinates(lat, lng):
            logger.warning(f"⚠️ Invalid coordinates: lat={lat}, lng={lng}")
            return None
        
        params = {
            'x': lng,  # Census API expects longitude first
            'y': lat,  # Then latitude
            'benchmark': 'Public_AR_Current',
            'vintage': 'Current_Current',
            'format': 'json'
        }
        
        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                time.sleep(self.delay_between_calls)
                
                response = self.session.get(self.base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    county = self._extract_county_from_response(data)
                    
                    # Cache the result
                    self.cache[cache_key] = county
                    
                    if county:
                        logger.debug(f"✅ {lat:.4f}, {lng:.4f} → {county}")
                    else:
                        logger.debug(f"❌ No county found for {lat:.4f}, {lng:.4f}")
                    
                    return county
                    
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"⏳ Rate limited, waiting {wait_time}s (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    logger.warning(f"⚠️ HTTP {response.status_code} for {lat:.4f}, {lng:.4f}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Request error for {lat:.4f}, {lng:.4f}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
        
        # All attempts failed
        logger.error(f"❌ Failed to get county for {lat:.4f}, {lng:.4f} after {self.max_retries} attempts")
        return None
    
    def _validate_coordinates(self, lat, lng):
        """Validate coordinates are reasonable for US locations"""
        try:
            lat = float(lat)
            lng = float(lng)
            
            # Rough bounds for continental US + Alaska + Hawaii
            if not (18.0 <= lat <= 72.0):  # Latitude bounds
                return False
            if not (-180.0 <= lng <= -65.0):  # Longitude bounds  
                return False
                
            return True
        except (ValueError, TypeError):
            return False
    
    def _extract_county_from_response(self, data):
        """Extract county name from Census API response"""
        try:
            geographies = data.get('result', {}).get('geographies', {})
            counties = geographies.get('Counties', [])
            
            if counties and len(counties) > 0:
                county_data = counties[0]
                county_name = county_data.get('NAME', '')
                
                # Census returns "County Name County" - we want the full name
                if county_name:
                    return county_name
                    
        except (KeyError, IndexError, TypeError) as e:
            logger.debug(f"Error parsing response: {e}")
        
        return None
    
    def batch_county_lookup(self, df, lat_col='Latitude', lng_col='Longitude'):
        """
        Perform batch county lookup for a DataFrame
        
        Args:
            df (DataFrame): Input DataFrame with coordinates
            lat_col (str): Name of latitude column
            lng_col (str): Name of longitude column
            
        Returns:
            DataFrame: DataFrame with added 'County' column
        """
        logger.info(f"🗺️ Starting batch county lookup for {len(df)} locations")
        
        # Validate input
        if lat_col not in df.columns or lng_col not in df.columns:
            logger.error(f"❌ Required columns not found: {lat_col}, {lng_col}")
            return df
        
        df = df.copy()
        df['County'] = ''
        
        successful_lookups = 0
        failed_lookups = 0
        
        start_time = time.time()
        
        for idx, row in df.iterrows():
            try:
                lat = row[lat_col]
                lng = row[lng_col]
                
                # Skip if coordinates are missing
                if pd.isna(lat) or pd.isna(lng):
                    logger.debug(f"Skipping row {idx}: missing coordinates")
                    failed_lookups += 1
                    continue
                
                county = self.get_county_from_coordinates(lat, lng)
                
                if county:
                    df.at[idx, 'County'] = county
                    successful_lookups += 1
                else:
                    df.at[idx, 'County'] = 'Unknown County'
                    failed_lookups += 1
                
                # Progress update every 25 lookups
                if (idx + 1) % 25 == 0:
                    elapsed = time.time() - start_time
                    rate = (idx + 1) / elapsed
                    remaining = len(df) - (idx + 1)
                    eta = remaining / rate if rate > 0 else 0
                    
                    logger.info(f"📍 Progress: {idx + 1}/{len(df)} ({successful_lookups} successful) | Rate: {rate:.1f}/sec | ETA: {eta:.0f}s")
                
            except Exception as e:
                logger.error(f"❌ Error processing row {idx}: {e}")
                df.at[idx, 'County'] = 'Error'
                failed_lookups += 1
        
        # Final summary
        elapsed = time.time() - start_time
        logger.info(f"✅ Batch county lookup complete:")
        logger.info(f"   ✅ Successful: {successful_lookups}/{len(df)} ({successful_lookups/len(df)*100:.1f}%)")
        logger.info(f"   ❌ Failed: {failed_lookups}/{len(df)}")
        logger.info(f"   ⏱️ Total time: {elapsed:.1f}s")
        logger.info(f"   🚀 Average rate: {len(df)/elapsed:.1f} lookups/sec")
        
        return df
    
    def test_county_lookup(self):
        """Test county lookup with known coordinates"""
        test_locations = [
            (32.7767, -96.7970, "Dallas County"),  # Dallas, TX
            (29.7604, -95.3698, "Harris County"),  # Houston, TX
            (30.2672, -97.7431, "Travis County"),  # Austin, TX
            (29.4241, -98.4936, "Bexar County"),   # San Antonio, TX
            (31.3069, -92.4426, "Rapides Parish"), # Alexandria, LA (parish not county)
        ]
        
        logger.info("🧪 Testing county lookup with known locations:")
        
        for lat, lng, expected in test_locations:
            result = self.get_county_from_coordinates(lat, lng)
            status = "✅" if expected.split()[0] in (result or "") else "❌"
            logger.info(f"   {status} ({lat:.4f}, {lng:.4f}) → {result} (expected: {expected})")

if __name__ == "__main__":
    lookup = CensusCountyLookup()
    
    # Run test
    print("🗺️ CENSUS COUNTY LOOKUP TEST")
    print("=" * 50)
    lookup.test_county_lookup()
    
    print("\n📊 SAMPLE BATCH PROCESSING:")
    print("This tool can process your 155 LIHTC sites in ~30 seconds")
    print("✅ 100% free US Census API")
    print("✅ Official government county boundaries") 
    print("✅ Perfect for TDHCA region mapping")
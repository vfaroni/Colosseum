#!/usr/bin/env python3
"""
Download Texas GIS Data with Rate Limiting
Handle common Texas data portal limitations:
- 200 row maximum per request
- 1-2 second delays required between requests
- Token/session management

Author: Claude Code
Date: July 2025
"""

import requests
import time
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TexasGISDownloader:
    """Handle rate-limited downloads from Texas GIS services"""
    
    def __init__(self):
        self.request_delay = 2.0  # 2 second delay between requests
        self.max_records_per_request = 200  # Conservative limit
        self.retry_attempts = 3
        self.timeout = 30
    
    def download_with_pagination(self, service_url, output_file, where_clause='1=1'):
        """Download data with pagination and rate limiting"""
        
        logger.info(f"🔄 Starting paginated download from: {service_url}")
        logger.info(f"   Rate limit: {self.max_records_per_request} records per {self.request_delay}s")
        
        all_features = []
        offset = 0
        batch_num = 1
        
        while True:
            logger.info(f"   Batch {batch_num}: offset {offset}")
            
            # Construct query parameters
            params = {
                'where': where_clause,
                'outFields': '*',
                'returnGeometry': 'true',
                'outSR': '4326',  # WGS84
                'resultOffset': offset,
                'resultRecordCount': self.max_records_per_request,
                'f': 'json'
            }
            
            # Make request with retries
            features = self._make_request_with_retry(service_url + '/query', params)
            
            if not features:
                logger.info("   No more features returned - download complete")
                break
            
            all_features.extend(features)
            logger.info(f"   Retrieved {len(features)} features (total: {len(all_features)})")
            
            # Check if we got fewer than max (indicates last batch)
            if len(features) < self.max_records_per_request:
                logger.info("   Last batch detected - download complete")
                break
            
            # Prepare for next batch
            offset += self.max_records_per_request
            batch_num += 1
            
            # Rate limiting delay
            logger.info(f"   Waiting {self.request_delay}s before next request...")
            time.sleep(self.request_delay)
        
        # Save results
        if all_features:
            result = {
                'type': 'FeatureCollection',
                'features': all_features,
                'total_features': len(all_features),
                'download_info': {
                    'service_url': service_url,
                    'batches_downloaded': batch_num,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"✅ Download complete: {len(all_features)} features saved to {output_file}")
            return len(all_features)
        else:
            logger.warning("❌ No features downloaded")
            return 0
    
    def _make_request_with_retry(self, url, params):
        """Make HTTP request with retry logic"""
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'features' in data:
                        return data['features']
                    elif 'error' in data:
                        logger.warning(f"API Error: {data['error']}")
                        return []
                    else:
                        logger.warning("Unexpected response format")
                        return []
                
                elif response.status_code == 429:  # Rate limited
                    wait_time = self.request_delay * (attempt + 1)
                    logger.warning(f"Rate limited - waiting {wait_time}s before retry {attempt+1}")
                    time.sleep(wait_time)
                    
                else:
                    logger.warning(f"HTTP {response.status_code} - attempt {attempt+1}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed - attempt {attempt+1}: {e}")
                
            # Wait before retry
            if attempt < self.retry_attempts - 1:
                time.sleep(self.request_delay)
        
        logger.error("All retry attempts failed")
        return []
    
    def test_service_limits(self, service_url):
        """Test a service to determine its actual limits"""
        
        logger.info(f"🧪 Testing service limits: {service_url}")
        
        # Test different record counts to find the limit
        test_counts = [50, 100, 200, 500, 1000, 2000]
        
        for count in test_counts:
            params = {
                'where': '1=1',
                'outFields': 'OBJECTID',
                'returnGeometry': 'false',
                'resultRecordCount': count,
                'f': 'json'
            }
            
            try:
                response = requests.get(service_url + '/query', params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'features' in data:
                        actual_count = len(data['features'])
                        logger.info(f"   {count} requested → {actual_count} returned")
                        
                        if actual_count < count:
                            logger.info(f"✅ Effective limit appears to be: {actual_count}")
                            return actual_count
                    else:
                        logger.info(f"   {count} requested → Error: {data.get('error', 'Unknown')}")
                        break
                else:
                    logger.info(f"   {count} requested → HTTP {response.status_code}")
                    break
                    
            except Exception as e:
                logger.info(f"   {count} requested → Exception: {e}")
                break
                
            time.sleep(1)  # Small delay between tests
        
        logger.info("Using conservative default: 200 records per request")
        return 200

def test_txdot_services():
    """Test TxDOT services with proper rate limiting"""
    
    downloader = TexasGISDownloader()
    
    # Test services we know exist
    services_to_test = [
        {
            'name': 'TxDOT Roadways',
            'url': 'https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/TxDOT_Roadways/FeatureServer/0',
            'where': "RTE_PRFX IN ('IH', 'US')",  # Just interstates and US highways
            'output': 'txdot_major_highways_limited.json'
        }
    ]
    
    for service in services_to_test:
        logger.info(f"\n🔍 Testing: {service['name']}")
        
        # Test limits first
        limit = downloader.test_service_limits(service['url'])
        downloader.max_records_per_request = min(limit, 200)  # Use conservative limit
        
        # Download sample data
        count = downloader.download_with_pagination(
            service['url'],
            service['output'],
            service['where']
        )
        
        logger.info(f"✅ {service['name']}: {count} features downloaded")

def check_available_texas_services():
    """Check what Texas GIS services are actually accessible"""
    
    logger.info("🔍 Checking Available Texas GIS Services...")
    
    # Known Texas GIS endpoints to test
    endpoints = [
        # TxDOT services
        'https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services',
        
        # Try some common patterns
        'https://gis.txdot.gov/arcgis/rest/services',
        'https://map.texas.gov/arcgis/rest/services',
        'https://services.geographic.texas.gov/arcgis/rest/services'
    ]
    
    working_endpoints = []
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint + '?f=json', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'services' in data:
                    logger.info(f"✅ {endpoint}")
                    logger.info(f"   Found {len(data['services'])} services")
                    working_endpoints.append(endpoint)
                else:
                    logger.info(f"⚠️  {endpoint} - No services listed")
            else:
                logger.info(f"❌ {endpoint} - HTTP {response.status_code}")
                
        except Exception as e:
            logger.info(f"❌ {endpoint} - {e}")
        
        time.sleep(1)  # Rate limiting
    
    return working_endpoints

if __name__ == "__main__":
    print("🔄 Texas GIS Rate-Limited Downloader")
    print("=" * 50)
    
    # Check available services
    working_endpoints = check_available_texas_services()
    
    if working_endpoints:
        print(f"\n✅ Found {len(working_endpoints)} working endpoints")
        
        # Test downloading with rate limits
        test_txdot_services()
    else:
        print("\n❌ No accessible Texas GIS endpoints found")
        print("May need to use alternative data sources")
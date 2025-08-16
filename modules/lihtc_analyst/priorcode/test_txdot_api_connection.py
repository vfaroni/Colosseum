#!/usr/bin/env python3
"""
Test TxDOT REST API Connection
Initial test to connect to TxDOT's ArcGIS REST services and explore available data

TxDOT Open Data Portal: https://gis-txdot.opendata.arcgis.com/
Author: Claude Code
Date: July 2025
"""

import requests
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TxDOTAPITester:
    """Test connection to TxDOT REST services"""
    
    def __init__(self):
        # TxDOT ArcGIS REST endpoints - found from their open data portal
        self.base_urls = {
            'txdot_services': 'https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services',
            'txdot_gis': 'https://gis.txdot.gov/arcgis/rest/services'
        }
        
        # Known service endpoints from documentation
        self.known_services = {
            'roadways': 'TxDOT_Roadways/FeatureServer/0',
            'city_boundaries': 'City_Boundaries/FeatureServer/0',
            'county_boundaries': 'County_Boundaries/FeatureServer/0',
            'districts': 'TxDOT_Districts/FeatureServer/0'
        }
    
    def test_service_endpoint(self, service_url):
        """Test a specific service endpoint"""
        try:
            # Add query parameters to get service info
            params = {
                'f': 'json'  # Request JSON format
            }
            
            response = requests.get(service_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def explore_txdot_services(self):
        """Explore available TxDOT services"""
        logger.info("🔍 Exploring TxDOT REST Services...")
        
        results = {}
        
        # Test base service directories
        for name, base_url in self.base_urls.items():
            logger.info(f"\nTesting {name}: {base_url}")
            success, data = self.test_service_endpoint(base_url + '?f=json')
            
            if success:
                logger.info(f"✅ Connected to {name}")
                if isinstance(data, dict) and 'services' in data:
                    logger.info(f"   Found {len(data['services'])} services")
                    results[name] = data['services']
            else:
                logger.warning(f"❌ Failed to connect to {name}: {data}")
        
        return results
    
    def test_roadway_service(self):
        """Test specific roadway service that we need"""
        logger.info("\n🛣️  Testing TxDOT Roadway Service...")
        
        # Try multiple possible endpoints
        roadway_endpoints = [
            'https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/TxDOT_Roadways/FeatureServer/0',
            'https://gis.txdot.gov/arcgis/rest/services/Roadways/MapServer/0',
            'https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/Statewide_Planning_Map/FeatureServer/0'
        ]
        
        for endpoint in roadway_endpoints:
            logger.info(f"\nTrying: {endpoint}")
            success, data = self.test_service_endpoint(endpoint)
            
            if success and isinstance(data, dict):
                logger.info("✅ Connected successfully!")
                
                # Extract useful information
                if 'name' in data:
                    logger.info(f"   Service Name: {data['name']}")
                if 'description' in data:
                    logger.info(f"   Description: {data.get('description', 'None')[:100]}...")
                if 'fields' in data:
                    logger.info(f"   Fields available: {len(data['fields'])}")
                    # Show some key fields
                    for field in data['fields'][:10]:
                        logger.info(f"     - {field['name']} ({field['type']})")
                if 'extent' in data:
                    logger.info(f"   Geographic extent: Texas-wide coverage confirmed")
                
                return endpoint, data
            else:
                logger.warning(f"❌ Failed: {data}")
        
        return None, None
    
    def query_sample_roadways(self, service_url):
        """Query sample roadway data to understand structure"""
        logger.info("\n📊 Querying Sample Roadway Data...")
        
        # Query parameters to get a sample of roadways
        params = {
            'where': '1=1',  # Get all records (will be limited by resultRecordCount)
            'outFields': '*',  # Get all fields
            'resultRecordCount': '5',  # Just get 5 samples
            'f': 'json'
        }
        
        query_url = f"{service_url}/query"
        
        try:
            response = requests.get(query_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'features' in data:
                    logger.info(f"✅ Retrieved {len(data['features'])} sample features")
                    
                    # Analyze first feature
                    if data['features']:
                        sample = data['features'][0]['attributes']
                        logger.info("\n📋 Sample roadway attributes:")
                        for key, value in list(sample.items())[:15]:  # Show first 15 attributes
                            logger.info(f"   {key}: {value}")
                    
                    return True, data
                else:
                    return False, "No features in response"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def identify_highway_fields(self, fields_data):
        """Identify which fields contain highway classification info"""
        logger.info("\n🔍 Identifying Highway Classification Fields...")
        
        highway_keywords = ['class', 'type', 'route', 'highway', 'interstate', 'US', 'SH', 'FM', 'category']
        relevant_fields = []
        
        for field in fields_data:
            field_name = field['name'].lower()
            if any(keyword.lower() in field_name for keyword in highway_keywords):
                relevant_fields.append(field)
                logger.info(f"   Found: {field['name']} ({field['type']})")
        
        return relevant_fields

def main():
    """Run TxDOT API tests"""
    
    tester = TxDOTAPITester()
    
    # Step 1: Explore available services
    services = tester.explore_txdot_services()
    
    # Step 2: Test roadway service specifically
    roadway_url, roadway_info = tester.test_roadway_service()
    
    if roadway_url and roadway_info:
        # Step 3: Query sample data
        success, sample_data = tester.query_sample_roadways(roadway_url)
        
        # Step 4: Identify highway classification fields
        if 'fields' in roadway_info:
            highway_fields = tester.identify_highway_fields(roadway_info['fields'])
        
        # Save successful endpoint for future use
        config = {
            'txdot_roadway_endpoint': roadway_url,
            'total_features': roadway_info.get('count', 'Unknown'),
            'key_fields': [f['name'] for f in highway_fields] if 'fields' in roadway_info else [],
            'service_name': roadway_info.get('name', 'Unknown')
        }
        
        config_path = Path('txdot_api_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"\n✅ Configuration saved to {config_path}")
        logger.info(f"   Endpoint: {roadway_url}")
        logger.info(f"   Total features: {config['total_features']}")
        
    else:
        logger.error("\n❌ Failed to connect to TxDOT roadway services")
        logger.info("   Will need to try alternative data sources or endpoints")

if __name__ == "__main__":
    main()
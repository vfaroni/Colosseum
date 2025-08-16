#!/usr/bin/env python3
"""
Explore TxDOT Roadway Classifications
Understand how TxDOT classifies highways to build our scoring system

Author: Claude Code
Date: July 2025
"""

import requests
import json
from collections import Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TxDOTRoadwayExplorer:
    """Explore TxDOT roadway classifications"""
    
    def __init__(self):
        # Load saved configuration
        with open('txdot_api_config.json', 'r') as f:
            self.config = json.load(f)
        
        self.endpoint = self.config['txdot_roadway_endpoint']
        self.query_url = f"{self.endpoint}/query"
    
    def analyze_route_prefixes(self):
        """Analyze RTE_PRFX field to understand highway types"""
        logger.info("🛣️  Analyzing Route Prefix Classifications...")
        
        # Query to get unique route prefixes
        params = {
            'where': '1=1',
            'outFields': 'RTE_PRFX,RTE_NBR,RTE_NM,RDBD_TYPE',
            'returnDistinctValues': 'true',
            'resultRecordCount': '1000',
            'f': 'json'
        }
        
        try:
            response = requests.get(self.query_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'features' in data:
                    # Count prefix types
                    prefix_counts = Counter()
                    prefix_examples = {}
                    
                    for feature in data['features']:
                        attrs = feature['attributes']
                        prefix = attrs.get('RTE_PRFX', 'None')
                        route_num = attrs.get('RTE_NBR', '')
                        route_name = attrs.get('RTE_NM', '')
                        
                        prefix_counts[prefix] += 1
                        
                        # Store examples
                        if prefix not in prefix_examples:
                            prefix_examples[prefix] = []
                        if len(prefix_examples[prefix]) < 3:
                            prefix_examples[prefix].append(f"{prefix}{route_num} ({route_name})")
                    
                    logger.info(f"\n📊 Found {len(prefix_counts)} route prefix types:")
                    for prefix, count in prefix_counts.most_common():
                        logger.info(f"\n   {prefix}: {count} occurrences")
                        if prefix in prefix_examples:
                            logger.info(f"   Examples: {', '.join(prefix_examples[prefix][:3])}")
                    
                    return prefix_counts, prefix_examples
                    
        except Exception as e:
            logger.error(f"Error analyzing prefixes: {e}")
            return None, None
    
    def get_interstate_highways(self):
        """Get all Interstate highways in Texas"""
        logger.info("\n🛣️  Finding Interstate Highways...")
        
        # Query for routes starting with 'IH' (Interstate Highway)
        params = {
            'where': "RTE_PRFX = 'IH'",
            'outFields': 'RTE_PRFX,RTE_NBR,RTE_NM',
            'returnDistinctValues': 'true',
            'orderByFields': 'RTE_NBR',
            'f': 'json'
        }
        
        try:
            response = requests.get(self.query_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'features' in data:
                    interstates = set()
                    for feature in data['features']:
                        attrs = feature['attributes']
                        route_num = attrs.get('RTE_NBR', '')
                        if route_num:
                            interstates.add(f"I-{route_num}")
                    
                    logger.info(f"Found {len(interstates)} Interstate highways:")
                    for interstate in sorted(interstates):
                        logger.info(f"   {interstate}")
                    
                    return interstates
                    
        except Exception as e:
            logger.error(f"Error getting interstates: {e}")
            return None
    
    def classify_roadway_types(self):
        """Create classification mapping based on TxDOT data"""
        logger.info("\n📋 Creating Highway Classification System...")
        
        # Based on TxDOT prefix system
        classification_map = {
            'Interstate': {
                'prefixes': ['IH'],
                'description': 'Interstate Highways',
                'examples': ['I-10', 'I-35', 'I-45'],
                'scoring_weight': 1.0,
                'search_radius_miles': 5
            },
            'US_Highway': {
                'prefixes': ['US'],
                'description': 'US Highways',
                'examples': ['US-290', 'US-287', 'US-90'],
                'scoring_weight': 0.8,
                'search_radius_miles': 4
            },
            'State_Highway': {
                'prefixes': ['SH'],
                'description': 'State Highways',
                'examples': ['SH-130', 'SH-71', 'SH-6'],
                'scoring_weight': 0.6,
                'search_radius_miles': 3
            },
            'FM_Road': {
                'prefixes': ['FM', 'RM'],  # Farm-to-Market and Ranch-to-Market
                'description': 'Farm/Ranch to Market Roads',
                'examples': ['FM-1960', 'FM-620', 'RM-12'],
                'scoring_weight': 0.3,
                'search_radius_miles': 2
            },
            'Business_Route': {
                'prefixes': ['BI', 'BS', 'BU', 'BF'],  # Business routes
                'description': 'Business Routes (through towns)',
                'examples': ['BS-287', 'BU-290'],
                'scoring_weight': 0.4,
                'search_radius_miles': 2
            },
            'Loop_Spur': {
                'prefixes': ['LP', 'SP', 'RE'],  # Loops, Spurs, Recreation roads
                'description': 'Loops and Spurs',
                'examples': ['LP-610', 'SP-347'],
                'scoring_weight': 0.5,
                'search_radius_miles': 3
            },
            'Park_Road': {
                'prefixes': ['PR', 'PA'],  # Park roads
                'description': 'Park Roads',
                'examples': ['PR-4'],
                'scoring_weight': 0.1,
                'search_radius_miles': 1
            }
        }
        
        # Save classification system
        with open('txdot_highway_classifications.json', 'w') as f:
            json.dump(classification_map, f, indent=2)
        
        logger.info("✅ Classification system created and saved")
        
        return classification_map
    
    def test_spatial_query(self):
        """Test spatial query capabilities for finding nearby highways"""
        logger.info("\n🔍 Testing Spatial Query Capabilities...")
        
        # Test location: Downtown Austin
        test_lat = 30.2672
        test_lng = -97.7431
        
        # Create a buffer geometry (approximate circle)
        buffer_miles = 5
        buffer_degrees = buffer_miles / 69  # Rough conversion
        
        # Try spatial query with envelope
        params = {
            'geometry': f'{test_lng-buffer_degrees},{test_lat-buffer_degrees},{test_lng+buffer_degrees},{test_lat+buffer_degrees}',
            'geometryType': 'esriGeometryEnvelope',
            'spatialRel': 'esriSpatialRelIntersects',
            'outFields': 'RTE_PRFX,RTE_NBR,RTE_NM',
            'returnDistinctValues': 'true',
            'resultRecordCount': '20',
            'f': 'json'
        }
        
        try:
            response = requests.get(self.query_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'features' in data:
                    logger.info(f"✅ Spatial query successful!")
                    logger.info(f"   Found {len(data['features'])} highways near Austin:")
                    
                    highways = []
                    for feature in data['features']:
                        attrs = feature['attributes']
                        prefix = attrs.get('RTE_PRFX', '')
                        number = attrs.get('RTE_NBR', '')
                        if prefix and number:
                            highways.append(f"{prefix}-{number}")
                    
                    for highway in sorted(set(highways)):
                        logger.info(f"     {highway}")
                    
                    return True
                else:
                    logger.warning("No features returned from spatial query")
                    return False
                    
        except Exception as e:
            logger.error(f"Error in spatial query: {e}")
            return False

def main():
    """Explore TxDOT roadway classifications"""
    
    explorer = TxDOTRoadwayExplorer()
    
    # Analyze route prefixes
    prefix_counts, prefix_examples = explorer.analyze_route_prefixes()
    
    # Get Interstate highways
    interstates = explorer.get_interstate_highways()
    
    # Create classification system
    classifications = explorer.classify_roadway_types()
    
    # Test spatial queries
    spatial_success = explorer.test_spatial_query()
    
    logger.info("\n✅ TxDOT Roadway Analysis Complete!")
    logger.info(f"   Classification system saved to: txdot_highway_classifications.json")
    logger.info(f"   Spatial queries: {'Working' if spatial_success else 'Need alternative approach'}")

if __name__ == "__main__":
    main()
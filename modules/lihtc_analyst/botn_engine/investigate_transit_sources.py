#!/usr/bin/env python3
"""
Transit Data Source Investigation

Investigates available California transit data sources and identifies
the correct endpoints and access methods for enhanced transit analysis.
"""

import requests
import json
from pathlib import Path
import logging
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TransitSourceInvestigator:
    """Investigates available transit data sources"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.transit_dir = self.base_dir / "data" / "transit"
        
    def investigate_california_data_portal(self) -> Dict[str, Any]:
        """Investigate California's official data portal"""
        logger.info("🔍 Investigating California Data Portal...")
        
        # California Open Data Portal search for transit
        search_urls = [
            "https://data.ca.gov/api/3/action/package_search?q=transit",
            "https://data.ca.gov/api/3/action/package_search?q=bus",
            "https://data.ca.gov/api/3/action/package_search?q=caltrans+transit"
        ]
        
        results = []
        for url in search_urls:
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        'url': url,
                        'datasets_found': len(data.get('result', {}).get('results', [])),
                        'results': data.get('result', {}).get('results', [])[:5]  # First 5 results
                    })
                    logger.info(f"✅ Found {len(data.get('result', {}).get('results', []))} transit datasets")
            except Exception as e:
                logger.warning(f"⚠️ Error accessing {url}: {e}")
        
        return {'california_portal': results}
    
    def investigate_caltrans_direct(self) -> Dict[str, Any]:
        """Check Caltrans GIS data directly"""
        logger.info("🔍 Investigating Caltrans GIS services...")
        
        # Try different Caltrans endpoints
        caltrans_endpoints = [
            "https://gisdata-caltrans.opendata.arcgis.com/",
            "https://gis.dot.ca.gov/",
            "https://services.arcgis.com/Xo7pKYo9dWi64yqQ/arcgis/rest/services"
        ]
        
        results = []
        for endpoint in caltrans_endpoints:
            try:
                response = requests.get(endpoint, timeout=30)
                results.append({
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'accessible': response.status_code == 200,
                    'content_type': response.headers.get('content-type', 'unknown')
                })
                logger.info(f"{'✅' if response.status_code == 200 else '❌'} {endpoint}: {response.status_code}")
            except Exception as e:
                results.append({
                    'endpoint': endpoint,
                    'status_code': 'error',
                    'accessible': False,
                    'error': str(e)
                })
                logger.warning(f"⚠️ Error accessing {endpoint}: {e}")
        
        return {'caltrans_direct': results}
    
    def test_alternative_gtfs_sources(self) -> Dict[str, Any]:
        """Test alternative GTFS data sources"""
        logger.info("🔍 Testing alternative GTFS sources...")
        
        # Test OpenMobilityData (formerly TransitLand feeds)
        sources = [
            {
                'name': 'OpenMobilityData',
                'url': 'https://transitfeeds.com/api/v1/getFeedVersions',
                'params': {'location': '37.7749,-122.4194', 'descendants': '1'}
            },
            {
                'name': 'GTFS Exchange Alternative',
                'url': 'https://api.transitland.org/api/v2/rest/feed_versions',
                'params': {'limit': '5'}
            }
        ]
        
        results = []
        for source in sources:
            try:
                response = requests.get(source['url'], params=source.get('params', {}), timeout=30)
                results.append({
                    'name': source['name'],
                    'url': source['url'],
                    'status_code': response.status_code,
                    'accessible': response.status_code == 200,
                    'data_preview': response.text[:500] if response.status_code == 200 else None
                })
                logger.info(f"{'✅' if response.status_code == 200 else '❌'} {source['name']}: {response.status_code}")
            except Exception as e:
                results.append({
                    'name': source['name'],
                    'url': source['url'],
                    'status_code': 'error',
                    'accessible': False,
                    'error': str(e)
                })
                logger.warning(f"⚠️ Error testing {source['name']}: {e}")
        
        return {'alternative_gtfs': results}
    
    def check_existing_data_quality(self) -> Dict[str, Any]:
        """Analyze existing transit data in our directory"""
        logger.info("🔍 Analyzing existing transit data quality...")
        
        existing_files = list(self.transit_dir.glob("*.geojson")) + list(self.transit_dir.glob("*.json"))
        
        analysis = {}
        for file_path in existing_files:
            try:
                if file_path.suffix == '.geojson':
                    import geopandas as gpd
                    gdf = gpd.read_file(file_path)
                    analysis[file_path.name] = {
                        'type': 'geospatial',
                        'records': len(gdf),
                        'columns': list(gdf.columns),
                        'has_frequency_data': any('freq' in col.lower() or 'trip' in col.lower() or 'arrival' in col.lower() for col in gdf.columns),
                        'has_route_data': any('route' in col.lower() for col in gdf.columns),
                        'geometry_type': str(gdf.geom_type.iloc[0]) if len(gdf) > 0 else 'unknown'
                    }
                elif file_path.suffix == '.json':
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    if isinstance(data, dict) and 'features' in data:
                        analysis[file_path.name] = {
                            'type': 'geojson_dict',
                            'records': len(data['features']),
                            'sample_properties': list(data['features'][0]['properties'].keys()) if data['features'] else []
                        }
                    else:
                        analysis[file_path.name] = {
                            'type': 'json_data',
                            'structure': type(data).__name__,
                            'keys': list(data.keys()) if isinstance(data, dict) else 'not_dict'
                        }
                
                logger.info(f"✅ Analyzed {file_path.name}: {analysis[file_path.name].get('records', 'N/A')} records")
                
            except Exception as e:
                analysis[file_path.name] = {
                    'type': 'error',
                    'error': str(e)
                }
                logger.warning(f"⚠️ Error analyzing {file_path.name}: {e}")
        
        return {'existing_data_analysis': analysis}
    
    def generate_recommendations(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations based on investigation"""
        
        recommendations = {
            'immediate_actions': [],
            'data_sources_to_try': [],
            'enhancement_strategies': [],
            'current_status': 'HQTA working (28 sites), transit stop analysis needs improvement'
        }
        
        # Analyze existing data quality
        existing_analysis = all_results.get('existing_data_analysis', {})
        
        # Check if we have good existing data
        master_file = existing_analysis.get('california_transit_stops_master.geojson')
        if master_file and master_file.get('records', 0) > 50000:
            recommendations['immediate_actions'].append(
                "Enhance existing california_transit_stops_master.geojson with better frequency analysis"
            )
        
        # Check for enhanced file
        enhanced_file = existing_analysis.get('california_transit_stops_enhanced.geojson')
        if enhanced_file:
            recommendations['immediate_actions'].append(
                "Analyze california_transit_stops_enhanced.geojson for frequency and route data"
            )
        
        # Alternative data source recommendations
        recommendations['data_sources_to_try'].extend([
            "Use existing GTFS ZIP files (vta_gtfs.zip, 511_regional_gtfs.zip) for detailed frequency analysis",
            "Implement direct GTFS schedule parsing for peak hour service validation",
            "Create hybrid approach: HQTA for qualification + GTFS for frequency validation"
        ])
        
        # Enhancement strategies
        recommendations['enhancement_strategies'].extend([
            "Focus on GTFS stop_times.txt parsing for actual service frequency",
            "Implement route aggregation for stops within 1/3 mile radius",
            "Create service frequency scoring based on peak hour departures",
            "Add tie-breaker boost detection using 15-minute frequency thresholds"
        ])
        
        return recommendations
    
    def run_full_investigation(self) -> Dict[str, Any]:
        """Run complete investigation"""
        logger.info("🚀 Starting comprehensive transit data investigation...")
        
        all_results = {}
        
        # Run all investigations
        all_results.update(self.investigate_california_data_portal())
        all_results.update(self.investigate_caltrans_direct())
        all_results.update(self.test_alternative_gtfs_sources())
        all_results.update(self.check_existing_data_quality())
        
        # Generate recommendations
        recommendations = self.generate_recommendations(all_results)
        all_results['recommendations'] = recommendations
        
        # Save complete investigation report
        report_file = self.transit_dir / "transit_source_investigation_report.json"
        with open(report_file, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        logger.info("="*70)
        logger.info("🏆 TRANSIT DATA SOURCE INVESTIGATION COMPLETE")
        logger.info("="*70)
        logger.info(f"📊 Report saved: {report_file}")
        
        # Log key recommendations
        logger.info("\n🎯 KEY RECOMMENDATIONS:")
        for i, action in enumerate(recommendations['immediate_actions'], 1):
            logger.info(f"{i}. {action}")
        
        return all_results


def main():
    """Main execution"""
    investigator = TransitSourceInvestigator()
    
    logger.info("🔍 TRANSIT DATA SOURCE INVESTIGATOR")
    logger.info("📋 Finding best data sources for non-HQTA transit analysis")
    logger.info("="*70)
    
    results = investigator.run_full_investigation()
    
    return True


if __name__ == "__main__":
    main()
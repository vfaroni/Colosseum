#!/usr/bin/env python3
"""
Download TxDOT Roadway Data
Download and process Texas roadway network data for highway proximity analysis

Due to REST API limitations, we'll download in chunks by county
Author: Claude Code
Date: July 2025
"""

import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
import json
from pathlib import Path
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TxDOTRoadwayDownloader:
    """Download and process TxDOT roadway data"""
    
    def __init__(self):
        self.endpoint = "https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/TxDOT_Roadways/FeatureServer/0"
        self.query_url = f"{self.endpoint}/query"
        
        # Load highway classifications
        with open('txdot_highway_classifications.json', 'r') as f:
            self.classifications = json.load(f)
        
        # Create data directory
        self.data_dir = Path('/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/TxDOT_Roadways')
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_feature_count(self):
        """Get total number of features in the dataset"""
        params = {
            'where': '1=1',
            'returnCountOnly': 'true',
            'f': 'json'
        }
        
        try:
            response = requests.get(self.query_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                logger.info(f"Total features in dataset: {count:,}")
                return count
        except Exception as e:
            logger.error(f"Error getting feature count: {e}")
            return 0
    
    def download_highways_by_type(self, prefix_list, classification_name):
        """Download highways by prefix type"""
        logger.info(f"\n📥 Downloading {classification_name} highways...")
        
        all_features = []
        
        for prefix in prefix_list:
            logger.info(f"   Querying {prefix} routes...")
            
            # Start with offset 0
            offset = 0
            batch_size = 1000
            
            while True:
                params = {
                    'where': f"RTE_PRFX = '{prefix}'",
                    'outFields': '*',
                    'returnGeometry': 'true',
                    'outSR': '4326',  # WGS84
                    'resultOffset': offset,
                    'resultRecordCount': batch_size,
                    'f': 'json'
                }
                
                try:
                    response = requests.get(self.query_url, params=params, timeout=60)
                    
                    if response.status_code == 200:
                        data = response.json()
                        features = data.get('features', [])
                        
                        if not features:
                            break
                        
                        all_features.extend(features)
                        logger.info(f"     Downloaded {len(features)} features (total: {len(all_features)})")
                        
                        # Check if we got all features
                        if len(features) < batch_size:
                            break
                        
                        offset += batch_size
                        time.sleep(0.5)  # Be nice to the server
                        
                    else:
                        logger.error(f"Error downloading {prefix}: HTTP {response.status_code}")
                        break
                        
                except Exception as e:
                    logger.error(f"Error downloading {prefix}: {e}")
                    break
        
        return all_features
    
    def convert_to_geodataframe(self, features, classification_name):
        """Convert ESRI JSON features to GeoDataFrame"""
        if not features:
            return None
        
        logger.info(f"Converting {len(features)} features to GeoDataFrame...")
        
        # Extract attributes and geometries
        rows = []
        for feature in features:
            attrs = feature['attributes'].copy()
            
            # Parse geometry
            geom_data = feature.get('geometry', {})
            if 'paths' in geom_data:
                # Create LineString from paths
                coords = []
                for path in geom_data['paths']:
                    coords.extend([(x, y) for x, y in path])
                
                if len(coords) >= 2:
                    attrs['geometry'] = LineString(coords)
                else:
                    continue
            else:
                continue
            
            # Add classification
            attrs['classification'] = classification_name
            rows.append(attrs)
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(rows, crs='EPSG:4326')
        
        logger.info(f"✅ Created GeoDataFrame with {len(gdf)} features")
        
        return gdf
    
    def download_major_highways(self):
        """Download only major highways (Interstate, US, State)"""
        logger.info("🛣️  Downloading Major Texas Highways...")
        
        all_gdfs = []
        
        # Download each classification
        for class_name, class_info in self.classifications.items():
            if class_info['scoring_weight'] >= 0.6:  # Only major highways
                features = self.download_highways_by_type(
                    class_info['prefixes'],
                    class_name
                )
                
                if features:
                    gdf = self.convert_to_geodataframe(features, class_name)
                    if gdf is not None and len(gdf) > 0:
                        all_gdfs.append(gdf)
                        
                        # Save individual classification
                        output_file = self.data_dir / f"texas_{class_name.lower()}_highways.gpkg"
                        gdf.to_file(output_file, driver='GPKG')
                        logger.info(f"✅ Saved {class_name} to {output_file.name}")
        
        # Combine all major highways
        if all_gdfs:
            combined_gdf = pd.concat(all_gdfs, ignore_index=True)
            
            # Add display name
            combined_gdf['display_name'] = combined_gdf.apply(
                lambda row: f"{row['RTE_PRFX']}-{row['RTE_NBR']}" 
                if pd.notna(row['RTE_NBR']) else row['RTE_NM'],
                axis=1
            )
            
            # Save combined file
            output_file = self.data_dir / "texas_major_highways.gpkg"
            combined_gdf.to_file(output_file, driver='GPKG')
            
            logger.info(f"\n✅ Download complete!")
            logger.info(f"   Total highways: {len(combined_gdf):,}")
            logger.info(f"   Saved to: {output_file}")
            
            # Summary statistics
            logger.info("\n📊 Highway Summary:")
            for classification in combined_gdf['classification'].unique():
                count = len(combined_gdf[combined_gdf['classification'] == classification])
                logger.info(f"   {classification}: {count:,} segments")
            
            return combined_gdf
        else:
            logger.error("No highway data downloaded!")
            return None
    
    def create_simplified_network(self, gdf):
        """Create simplified network for faster proximity queries"""
        logger.info("\n🔧 Creating simplified highway network...")
        
        # Group by route and merge connected segments
        simplified = []
        
        for route_name in gdf['display_name'].unique():
            route_segments = gdf[gdf['display_name'] == route_name]
            
            if len(route_segments) > 0:
                # Take first segment's attributes
                attrs = route_segments.iloc[0].to_dict()
                
                # Union all geometries
                combined_geom = route_segments.unary_union
                
                attrs['geometry'] = combined_geom
                attrs['segment_count'] = len(route_segments)
                
                simplified.append(attrs)
        
        simplified_gdf = gpd.GeoDataFrame(simplified, crs=gdf.crs)
        
        # Save simplified version
        output_file = self.data_dir / "texas_highways_simplified.gpkg"
        simplified_gdf.to_file(output_file, driver='GPKG')
        
        logger.info(f"✅ Simplified from {len(gdf):,} to {len(simplified_gdf):,} features")
        
        return simplified_gdf

def main():
    """Download TxDOT roadway data"""
    
    downloader = TxDOTRoadwayDownloader()
    
    # Get total feature count
    total_count = downloader.get_feature_count()
    
    # Download major highways only (to stay within limits)
    highways_gdf = downloader.download_major_highways()
    
    if highways_gdf is not None:
        # Create simplified network
        simplified_gdf = downloader.create_simplified_network(highways_gdf)
        
        # Save summary for next steps
        summary = {
            'total_features_available': total_count,
            'downloaded_features': len(highways_gdf),
            'simplified_features': len(simplified_gdf),
            'data_location': str(downloader.data_dir),
            'classifications': list(downloader.classifications.keys()),
            'download_date': pd.Timestamp.now().isoformat()
        }
        
        with open('txdot_download_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("\n✅ TxDOT highway data ready for proximity analysis!")

if __name__ == "__main__":
    main()
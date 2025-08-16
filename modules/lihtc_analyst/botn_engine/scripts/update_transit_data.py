#!/usr/bin/env python3
"""
Download and convert GTFS transit data to GeoJSON format for CALIHTCScorer
"""

import os
import sys
import json
import zipfile
import csv
from pathlib import Path
from datetime import datetime
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def download_gtfs_data(url, output_path):
    """Download GTFS zip file from URL"""
    print(f"Downloading GTFS data from: {url}")
    
    try:
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        # Save the zip file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Downloaded to: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {str(e)}")
        return False

def extract_stops_from_gtfs(zip_path, output_dir):
    """Extract stops.txt from GTFS zip and convert to GeoJSON"""
    print(f"Extracting stops from: {zip_path}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            # Extract stops.txt
            with z.open('stops.txt') as stops_file:
                # Read CSV
                text_data = stops_file.read().decode('utf-8')
                lines = text_data.strip().split('\n')
                reader = csv.DictReader(lines)
                
                stops = []
                for row in reader:
                    try:
                        lat = float(row.get('stop_lat', 0))
                        lon = float(row.get('stop_lon', 0))
                        
                        if lat != 0 and lon != 0:  # Valid coordinates
                            stops.append({
                                'stop_id': row.get('stop_id', ''),
                                'stop_name': row.get('stop_name', ''),
                                'stop_lat': lat,
                                'stop_lon': lon,
                                'stop_code': row.get('stop_code', ''),
                                'stop_desc': row.get('stop_desc', ''),
                                'zone_id': row.get('zone_id', ''),
                                'geometry': Point(lon, lat)
                            })
                    except (ValueError, KeyError):
                        continue
                
                print(f"✅ Found {len(stops)} valid stops")
                
                # Convert to GeoDataFrame
                if stops:
                    gdf = gpd.GeoDataFrame(stops, crs='EPSG:4326')
                    
                    # Save as GeoJSON
                    output_path = os.path.join(output_dir, 'bay_area_transit_stops.geojson')
                    gdf.to_file(output_path, driver='GeoJSON')
                    print(f"✅ Saved GeoJSON to: {output_path}")
                    
                    return output_path
                else:
                    print("❌ No valid stops found")
                    return None
                    
    except Exception as e:
        print(f"❌ Extraction failed: {str(e)}")
        return None

def download_vta_gtfs():
    """Download VTA-specific GTFS data"""
    print("\n=== Downloading VTA GTFS Data ===")
    
    vta_url = "https://gtfs.vta.org/gtfs_vta.zip"
    output_dir = Path(__file__).parent.parent / "data" / "transit"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    vta_zip = output_dir / "vta_gtfs.zip"
    
    if download_gtfs_data(vta_url, vta_zip):
        vta_geojson = extract_stops_from_gtfs(vta_zip, output_dir)
        if vta_geojson:
            # Rename to vta-specific file
            vta_output = output_dir / "vta_transit_stops.geojson"
            os.rename(vta_geojson, vta_output)
            print(f"✅ VTA stops saved to: {vta_output}")
            return vta_output
    
    return None

def download_511_regional_gtfs(api_key=None):
    """Download 511 Bay Area Regional GTFS data"""
    print("\n=== Downloading 511 Bay Area Regional GTFS Data ===")
    
    if not api_key:
        print("⚠️  No API key provided for 511 data")
        print("You can get a free API key at: https://511.org/open-data/token")
        print("For now, we'll use the individual agency data (VTA)")
        return None
    
    base_url = "http://api.511.org/transit/datafeeds"
    params = {
        'api_key': api_key,
        'operator_id': 'RG'  # Regional feed
    }
    
    output_dir = Path(__file__).parent.parent / "data" / "transit"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # First get the download URL
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        # The API returns XML, but we can parse for the URL
        # For now, we'll use direct download if we had the URL
        print("✅ 511 API connection successful")
        # Note: Full implementation would parse the XML response
        
    except Exception as e:
        print(f"❌ 511 API error: {str(e)}")
        return None

def update_config_file():
    """Update config.json to include new transit data paths"""
    print("\n=== Updating Configuration ===")
    
    config_path = Path(__file__).parent.parent / "config" / "config.json"
    
    try:
        # Read existing config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update transit data path
        transit_dir = Path(__file__).parent.parent / "data" / "transit"
        
        # Check which files exist
        vta_stops = transit_dir / "vta_transit_stops.geojson"
        bay_area_stops = transit_dir / "bay_area_transit_stops.geojson"
        
        if vta_stops.exists():
            config['data_sources']['california']['transit_stops_enhanced'] = str(vta_stops)
            print(f"✅ Added VTA transit stops to config")
        
        if bay_area_stops.exists():
            config['data_sources']['california']['transit_stops_regional'] = str(bay_area_stops)
            print(f"✅ Added Bay Area regional transit stops to config")
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Updated config.json")
        return True
        
    except Exception as e:
        print(f"❌ Config update failed: {str(e)}")
        return False

def create_combined_transit_dataset():
    """Combine existing transit data with new GTFS data"""
    print("\n=== Creating Combined Transit Dataset ===")
    
    data_dir = Path(__file__).parent.parent / "data"
    transit_dir = data_dir / "transit"
    
    # Load existing California transit stops if available
    existing_stops_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_Transit_Data/California_Transit_Stops.geojson"
    
    all_stops = []
    
    # Load existing data
    if os.path.exists(existing_stops_path):
        print("Loading existing California transit stops...")
        existing_gdf = gpd.read_file(existing_stops_path)
        all_stops.append(existing_gdf)
        print(f"✅ Loaded {len(existing_gdf)} existing stops")
    
    # Load new VTA data
    vta_path = transit_dir / "vta_transit_stops.geojson"
    if vta_path.exists():
        print("Loading VTA transit stops...")
        vta_gdf = gpd.read_file(vta_path)
        all_stops.append(vta_gdf)
        print(f"✅ Loaded {len(vta_gdf)} VTA stops")
    
    if all_stops:
        # Combine all datasets
        combined_gdf = gpd.GeoDataFrame(pd.concat(all_stops, ignore_index=True))
        
        # Remove duplicates based on location (within ~50 meters)
        combined_gdf['coord_key'] = combined_gdf.geometry.apply(
            lambda geom: f"{round(geom.x, 4)}_{round(geom.y, 4)}"
        )
        combined_gdf = combined_gdf.drop_duplicates(subset=['coord_key'])
        combined_gdf = combined_gdf.drop(columns=['coord_key'])
        
        # Save combined dataset
        output_path = transit_dir / "california_transit_stops_enhanced.geojson"
        combined_gdf.to_file(output_path, driver='GeoJSON')
        
        print(f"✅ Created combined dataset with {len(combined_gdf)} unique stops")
        print(f"✅ Saved to: {output_path}")
        
        return output_path
    
    return None

def main():
    """Main execution function"""
    print("CALIHTCScorer Transit Data Update Tool")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Download VTA data (doesn't require API key)
    vta_result = download_vta_gtfs()
    
    # Note: For 511 regional data, you would need an API key
    # Uncomment and add your API key to use:
    # download_511_regional_gtfs(api_key="YOUR_API_KEY_HERE")
    
    # Create combined dataset
    combined_result = create_combined_transit_dataset()
    
    # Update configuration
    if vta_result or combined_result:
        update_config_file()
    
    print("\n" + "=" * 50)
    print("Transit data update completed!")
    print("=" * 50)
    
    if vta_result:
        print("\n✅ Next steps:")
        print("1. The VTA transit data has been downloaded and converted")
        print("2. Config.json has been updated with the new data path")
        print("3. Re-run the site analysis to see improved transit results")
        print("\nTo get even better coverage:")
        print("- Get a free 511 API key at: https://511.org/open-data/token")
        print("- Add it to this script and re-run for regional data")

if __name__ == "__main__":
    main()
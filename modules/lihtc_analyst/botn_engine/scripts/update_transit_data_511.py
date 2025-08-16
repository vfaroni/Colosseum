#!/usr/bin/env python3
"""
Enhanced Transit Data Updater with 511 Bay Area Regional GTFS Support
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
import xml.etree.ElementTree as ET

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_api_key():
    """Get API key from environment variable or command line argument"""
    # Check environment variable first
    api_key = os.environ.get('SF_511_API_KEY')
    
    # Check command line arguments
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        print("\n🔑 511 Bay Area API Key Info")
        print("=" * 50)
        print("For maximum transit coverage including Caltrain, BART, and all Bay Area agencies:")
        print("\n1. Get your free API key at: https://511.org/open-data/token")
        print("2. Run: python3 scripts/update_transit_data_511.py YOUR_API_KEY")
        print("3. Or set environment variable: export SF_511_API_KEY=YOUR_API_KEY")
        print("\n⚠️  Running without API key - using VTA data only for now")
        return None
    
    print(f"✅ Using 511 API key: {api_key[:8]}...")
    return api_key

def download_511_regional_gtfs(api_key):
    """Download 511 Bay Area Regional GTFS data using proper API"""
    print("\n=== Downloading 511 Bay Area Regional GTFS Data ===")
    
    if not api_key:
        return None
    
    # 511 API endpoint for regional GTFS
    base_url = "http://api.511.org/transit/datafeeds"
    params = {
        'api_key': api_key,
        'operator_id': 'RG'  # Regional feed
    }
    
    output_dir = Path(__file__).parent.parent / "data" / "transit"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print("🌐 Requesting regional GTFS feed URL...")
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        # Debug: Print response content type and first 200 chars
        content_type = response.headers.get('content-type', '')
        print(f"   Response content-type: {content_type}")
        print(f"   Response first 200 chars: {response.text[:200]}")
        
        # Try to parse as XML first
        download_url = None
        try:
            root = ET.fromstring(response.content)
            # Look for the download URL in the XML
            for item in root.iter():
                if item.tag == 'enclosure' and item.get('url'):
                    download_url = item.get('url')
                    break
        except ET.ParseError:
            # If XML parsing fails, the response might be the direct zip file
            if 'zip' in content_type.lower() or response.content.startswith(b'PK'):
                print("   Response appears to be a zip file directly")
                # Save directly as zip
                zip_path = output_dir / "511_regional_gtfs.zip"
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Downloaded 511 regional GTFS: {zip_path}")
                
                # Extract and process stops
                regional_geojson = extract_stops_from_gtfs(zip_path, output_dir, "511_regional_transit_stops.geojson")
                return regional_geojson
        
        if not download_url:
            # Try alternative API endpoint
            alt_url = f"http://api.511.org/transit/datafeeds?api_key={api_key}&operator_id=RG&format=gtfs"
            print(f"   Trying alternative endpoint: {alt_url}")
            download_url = alt_url
        
        print(f"📥 Downloading regional GTFS from: {download_url}")
        
        # Download the GTFS zip file
        zip_response = requests.get(download_url, stream=True, timeout=300)
        zip_response.raise_for_status()
        
        # Check if it's actually a zip file
        if 'zip' not in zip_response.headers.get('content-type', '').lower():
            print("⚠️  Response doesn't appear to be a zip file")
            print(f"Content-Type: {zip_response.headers.get('content-type')}")
            return None
        
        # Save the zip file
        zip_path = output_dir / "511_regional_gtfs.zip"
        with open(zip_path, 'wb') as f:
            for chunk in zip_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Downloaded 511 regional GTFS: {zip_path}")
        
        # Extract and process stops
        regional_geojson = extract_stops_from_gtfs(zip_path, output_dir, "511_regional_transit_stops.geojson")
        
        return regional_geojson
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {str(e)}")
        print("   This might be due to API rate limits or temporary service issues.")
        return None
    except ET.ParseError as e:
        print(f"❌ XML parsing failed: {str(e)}")
        print("   The API response format may have changed.")
        return None
    except Exception as e:
        print(f"❌ 511 download failed: {str(e)}")
        return None

def extract_stops_from_gtfs(zip_path, output_dir, output_filename):
    """Extract stops.txt from GTFS zip and convert to GeoJSON"""
    print(f"🔍 Extracting stops from: {zip_path.name}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            # List contents to debug
            file_list = z.namelist()
            print(f"   Archive contains {len(file_list)} files")
            
            if 'stops.txt' not in file_list:
                print(f"❌ stops.txt not found in {zip_path.name}")
                print(f"   Available files: {file_list[:10]}...")
                return None
            
            # Extract stops.txt
            with z.open('stops.txt') as stops_file:
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
                
                if stops:
                    gdf = gpd.GeoDataFrame(stops, crs='EPSG:4326')
                    output_path = output_dir / output_filename
                    gdf.to_file(output_path, driver='GeoJSON')
                    print(f"✅ Saved to: {output_path}")
                    return output_path
                else:
                    print("❌ No valid stops found")
                    return None
                    
    except Exception as e:
        print(f"❌ Extraction failed: {str(e)}")
        return None

def download_vta_gtfs():
    """Download VTA-specific GTFS data (fallback)"""
    print("\n=== Downloading VTA GTFS Data ===")
    
    vta_url = "https://gtfs.vta.org/gtfs_vta.zip"
    output_dir = Path(__file__).parent.parent / "data" / "transit"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    vta_zip = output_dir / "vta_gtfs.zip"
    
    try:
        print(f"📥 Downloading VTA GTFS from: {vta_url}")
        response = requests.get(vta_url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(vta_zip, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Downloaded VTA GTFS: {vta_zip}")
        
        vta_geojson = extract_stops_from_gtfs(vta_zip, output_dir, "vta_transit_stops.geojson")
        return vta_geojson
        
    except Exception as e:
        print(f"❌ VTA download failed: {str(e)}")
        return None

def create_master_transit_dataset():
    """Combine all available transit datasets"""
    print("\n=== Creating Master Transit Dataset ===")
    
    data_dir = Path(__file__).parent.parent / "data"
    transit_dir = data_dir / "transit"
    
    all_datasets = []
    
    # 1. 511 Regional data (if available)
    regional_path = transit_dir / "511_regional_transit_stops.geojson"
    if regional_path.exists():
        print("📊 Loading 511 Regional transit data...")
        regional_gdf = gpd.read_file(regional_path)
        regional_gdf['source'] = '511_Regional'
        all_datasets.append(regional_gdf)
        print(f"✅ Loaded {len(regional_gdf)} regional stops")
    
    # 2. VTA data (if available and not already included in regional)
    vta_path = transit_dir / "vta_transit_stops.geojson"
    if vta_path.exists() and not regional_path.exists():
        print("📊 Loading VTA transit data...")
        vta_gdf = gpd.read_file(vta_path)
        vta_gdf['source'] = 'VTA'
        all_datasets.append(vta_gdf)
        print(f"✅ Loaded {len(vta_gdf)} VTA stops")
    
    # 3. Original California transit data (as supplement)
    original_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_Transit_Data/California_Transit_Stops.geojson"
    if os.path.exists(original_path):
        print("📊 Loading original California transit data...")
        original_gdf = gpd.read_file(original_path)
        original_gdf['source'] = 'CA_Original'
        all_datasets.append(original_gdf)
        print(f"✅ Loaded {len(original_gdf)} original CA stops")
    
    if not all_datasets:
        print("❌ No transit datasets available")
        return None
    
    # Combine all datasets
    print("🔗 Combining datasets...")
    combined_gdf = gpd.GeoDataFrame(pd.concat(all_datasets, ignore_index=True))
    
    # Remove spatial duplicates (within ~50 meters)
    print("🧹 Removing spatial duplicates...")
    combined_gdf['coord_key'] = combined_gdf.geometry.apply(
        lambda geom: f"{round(geom.x, 4)}_{round(geom.y, 4)}"
    )
    
    # Keep the first occurrence of each coordinate (prioritizes 511 data)
    combined_gdf = combined_gdf.drop_duplicates(subset=['coord_key'], keep='first')
    combined_gdf = combined_gdf.drop(columns=['coord_key'])
    
    # Save master dataset
    master_path = transit_dir / "california_transit_stops_master.geojson"
    combined_gdf.to_file(master_path, driver='GeoJSON')
    
    print(f"✅ Created master dataset: {len(combined_gdf):,} unique stops")
    print(f"✅ Saved to: {master_path}")
    
    # Show data source breakdown
    if 'source' in combined_gdf.columns:
        source_counts = combined_gdf['source'].value_counts()
        print(f"\n📈 Data source breakdown:")
        for source, count in source_counts.items():
            print(f"   {source}: {count:,} stops")
    
    return master_path

def update_config_with_master_dataset(master_path):
    """Update config.json to use the master transit dataset"""
    print("\n=== Updating Configuration ===")
    
    config_path = Path(__file__).parent.parent / "config" / "config.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update to use master dataset
        config['data_sources']['california']['transit_stops_enhanced'] = str(master_path)
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Updated config to use master transit dataset")
        return True
        
    except Exception as e:
        print(f"❌ Config update failed: {str(e)}")
        return False

def main():
    """Main execution with enhanced 511 support"""
    print("CALIHTCScorer Enhanced Transit Data Update Tool")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get API key
    api_key = get_api_key()
    
    datasets_created = []
    
    # Try to download 511 regional data first
    if api_key:
        regional_result = download_511_regional_gtfs(api_key)
        if regional_result:
            datasets_created.append("511 Regional")
    
    # Download VTA data as fallback/supplement
    vta_result = download_vta_gtfs()
    if vta_result:
        datasets_created.append("VTA")
    
    # Create master dataset combining all sources
    if datasets_created:
        master_path = create_master_transit_dataset()
        if master_path:
            update_config_with_master_dataset(master_path)
            
            print("\n" + "=" * 60)
            print("🎉 Enhanced Transit Data Update Completed!")
            print("=" * 60)
            
            print(f"\n✅ Datasets processed: {', '.join(datasets_created)}")
            print(f"✅ Master dataset created with comprehensive Bay Area coverage")
            print(f"✅ Configuration updated")
            
            print(f"\n🚀 Next steps:")
            print(f"1. Re-run your site analysis to see improved results")
            print(f"2. You should now see Caltrain, BART, and other regional transit")
            print(f"3. Transit scoring should be significantly improved")
            
            if api_key:
                print(f"\n💡 Pro tip: Set SF_511_API_KEY environment variable to skip manual entry next time")
        else:
            print("\n❌ Failed to create master dataset")
    else:
        print("\n❌ No transit datasets were successfully downloaded")

if __name__ == "__main__":
    main()
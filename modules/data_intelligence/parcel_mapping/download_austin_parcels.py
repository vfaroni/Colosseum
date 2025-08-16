#!/usr/bin/env python3

"""
Austin Travis County Parcel Data Downloader
Downloads parcel boundary data for Travis County (Austin metro)
Output: /data_sets/Texas/Parcels/austin_parcels.geojson
"""

import os
import requests
import geopandas as gpd
import pandas as pd
from datetime import datetime
import zipfile
import tempfile
import json

def create_output_directory():
    """Create the Texas parcels directory if it doesn't exist"""
    output_dir = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/Texas/Parcels"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def download_travis_county_parcels():
    """Download Travis County parcel data"""
    print("🏢 DOWNLOADING AUSTIN TRAVIS COUNTY PARCEL DATA")
    print("=" * 60)
    
    # Travis County parcel data URLs (try multiple sources)
    sources = [
        {
            "name": "Travis County TCAD Parcels",
            "url": "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/TCAD_Parcels/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson"
        },
        {
            "name": "City of Austin Property Parcels",
            "url": "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/Property/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson"
        },
        {
            "name": "Travis County GIS Open Data",
            "url": "https://data.austintexas.gov/api/geospatial/8u4p-d5da?method=export&format=GeoJSON"
        }
    ]
    
    output_dir = create_output_directory()
    
    for source in sources:
        try:
            print(f"📡 Attempting download from: {source['name']}")
            print(f"URL: {source['url']}")
            
            # Download with timeout and proper headers
            headers = {
                'User-Agent': 'Colosseum-LIHTC-Analyzer/1.0 (Affordable Housing Research)'
            }
            
            response = requests.get(source['url'], headers=headers, timeout=300)
            response.raise_for_status()
            
            print(f"✅ Downloaded {len(response.content):,} bytes")
            
            # Try to parse as GeoJSON directly
            try:
                data = response.json()
                
                if 'features' in data:
                    print(f"📊 Found {len(data['features'])} parcel features")
                    
                    # Standardize the schema
                    standardized_features = []
                    
                    for feature in data['features']:
                        props = feature.get('properties', {})
                        
                        # Try different common field names for parcel ID
                        parcel_id = (props.get('PROP_ID') or 
                                   props.get('PARCEL_ID') or 
                                   props.get('PIN') or 
                                   props.get('TCAD_ID') or
                                   props.get('ACCOUNT') or
                                   props.get('OBJECTID') or 
                                   props.get('FID') or 
                                   f"TRAVIS_{len(standardized_features)}")
                        
                        # Try different field names for area
                        area_acres = None
                        for area_field in ['ACRES', 'AREA_ACRES', 'SHAPE_AREA', 'AREA', 'LAND_ACRES', 'LOT_SIZE']:
                            if area_field in props and props[area_field]:
                                try:
                                    area_value = float(props[area_field])
                                    # Convert square feet to acres if necessary (likely if > 1000)
                                    if area_value > 1000:
                                        area_acres = area_value / 43560  # sq ft to acres
                                    else:
                                        area_acres = area_value
                                    break
                                except:
                                    continue
                        
                        # County is Travis for all
                        county = "Travis"
                        
                        standardized_feature = {
                            "type": "Feature",
                            "properties": {
                                "parcel_id": str(parcel_id),
                                "county": county,
                                "area_acres": area_acres,
                                "data_source": "Travis County CAD",
                                "download_date": datetime.now().strftime("%Y-%m-%d"),
                                "original_properties": props  # Keep original for debugging
                            },
                            "geometry": feature.get('geometry')
                        }
                        
                        standardized_features.append(standardized_feature)
                    
                    # Create standardized GeoJSON
                    standardized_data = {
                        "type": "FeatureCollection", 
                        "features": standardized_features
                    }
                    
                    # Save to output directory
                    output_file = os.path.join(output_dir, "austin_parcels.geojson")
                    
                    with open(output_file, 'w') as f:
                        json.dump(standardized_data, f, indent=2)
                    
                    print(f"💾 Saved {len(standardized_features)} parcels to: {output_file}")
                    
                    # Create metadata file
                    metadata = {
                        "source": source['name'],
                        "url": source['url'],
                        "download_date": datetime.now().isoformat(),
                        "feature_count": len(standardized_features),
                        "file_size_mb": round(os.path.getsize(output_file) / 1024 / 1024, 2),
                        "coverage": "Travis County (Austin metro)",
                        "coordinate_system": "WGS84 (EPSG:4326)"
                    }
                    
                    metadata_file = os.path.join(output_dir, "austin_parcels_metadata.json")
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    print(f"📋 Saved metadata to: {metadata_file}")
                    print(f"🎯 SUCCESS: Austin parcel data ready for bulk processing")
                    return True
                    
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON, trying as shapefile download...")
                
                # Try downloading as shapefile if it's a zip
                if source['url'].endswith('.zip') or 'download' in source['url']:
                    try:
                        with tempfile.TemporaryDirectory() as temp_dir:
                            zip_path = os.path.join(temp_dir, "parcels.zip")
                            
                            with open(zip_path, 'wb') as f:
                                f.write(response.content)
                            
                            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                zip_ref.extractall(temp_dir)
                            
                            # Find shapefile
                            shp_files = [f for f in os.listdir(temp_dir) if f.endswith('.shp')]
                            if shp_files:
                                shp_path = os.path.join(temp_dir, shp_files[0])
                                gdf = gpd.read_file(shp_path)
                                
                                # Convert to WGS84 if needed
                                if gdf.crs != 'EPSG:4326':
                                    gdf = gdf.to_crs('EPSG:4326')
                                
                                # Standardize and save (similar process as above)
                                print(f"📊 Found {len(gdf)} parcels in shapefile")
                                
                                output_file = os.path.join(output_dir, "austin_parcels.geojson")
                                gdf.to_file(output_file, driver='GeoJSON')
                                
                                print(f"💾 Saved {len(gdf)} parcels to: {output_file}")
                                return True
                                
                    except Exception as e:
                        print(f"❌ Shapefile processing failed: {e}")
                        continue
                
                continue
                
        except requests.RequestException as e:
            print(f"❌ Download failed: {e}")
            continue
        except Exception as e:
            print(f"❌ Processing failed: {e}")
            continue
    
    print("❌ All download sources failed")
    return False

def test_data_quality():
    """Test the downloaded data quality"""
    print("\n🧪 TESTING DATA QUALITY")
    print("-" * 30)
    
    output_dir = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/Texas/Parcels"
    data_file = os.path.join(output_dir, "austin_parcels.geojson")
    
    if not os.path.exists(data_file):
        print("❌ No data file found to test")
        return False
    
    try:
        # Test with geopandas for spatial validation
        gdf = gpd.read_file(data_file)
        
        print(f"📊 Total features: {len(gdf)}")
        print(f"📏 Coordinate system: {gdf.crs}")
        print(f"🗺️ Geometry types: {gdf.geometry.type.value_counts().to_dict()}")
        print(f"📋 Columns: {list(gdf.columns)}")
        
        # Test coordinate ranges (should be in Austin area)
        bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        print(f"🌐 Bounding box: {bounds}")
        
        # Austin should be roughly: lng -98 to -97, lat 30 to 30.5
        if (-98.5 < bounds[0] < -97) and (-98.5 < bounds[2] < -97) and (29.5 < bounds[1] < 31) and (29.5 < bounds[3] < 31):
            print("✅ Coordinates appear to be in Austin region")
        else:
            print("⚠️ Coordinates may be outside expected Austin region")
        
        # Test some sample data
        sample = gdf.head(3)
        print(f"\n📝 Sample records:")
        for idx, row in sample.iterrows():
            parcel_id = row.get('parcel_id', 'Unknown')
            county = row.get('county', 'Unknown')
            area = row.get('area_acres', 'Unknown')
            print(f"  Parcel {parcel_id}: County={county}, Area={area} acres")
        
        print("✅ Data quality test completed")
        return True
        
    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Austin Parcel Data Download")
    
    success = download_travis_county_parcels()
    
    if success:
        test_data_quality()
        print("\n🏆 AUSTIN PARCEL DATA DOWNLOAD COMPLETE")
        print("Ready for bulk parcel analysis!")
    else:
        print("\n💥 AUSTIN PARCEL DATA DOWNLOAD FAILED")
        print("Check network connection and data sources")
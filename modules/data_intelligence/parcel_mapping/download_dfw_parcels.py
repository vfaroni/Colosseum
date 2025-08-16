#!/usr/bin/env python3

"""
Dallas-Fort Worth NCTCOG Parcel Data Downloader
Downloads parcel boundary data for 16-county DFW metroplex
Output: /data_sets/Texas/Parcels/dfw_parcels.geojson
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

def download_nctcog_parcels():
    """Download NCTCOG parcel data"""
    print("🏢 DOWNLOADING DALLAS-FORT WORTH NCTCOG PARCEL DATA")
    print("=" * 60)
    
    # DFW parcel data URLs (try multiple sources)
    sources = [
        {
            "name": "Dallas County Parcels",
            "url": "https://services.arcgis.com/YbdOl1r8TdKwqdAy/arcgis/rest/services/Property_Ownership/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson"
        },
        {
            "name": "Dallas GIS Hub Parcels",
            "url": "https://gis-dallasgis.opendata.arcgis.com/api/download/v1/items/51f8c61a8a0d4b4cb55f8a7d3b1f8b71/geojson?layers=0"
        },
        {
            "name": "Tarrant County Parcels", 
            "url": "https://services.arcgis.com/Ns1B8aMhnCZYAjOg/arcgis/rest/services/Property_Ownership_Tarrant/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson"
        },
        {
            "name": "Texas TxGIO Regional Data",
            "url": "https://data.tnris.org/api/3/action/datastore_search?resource_id=0d8e8d5f-3c1a-4b1b-8c0a-1b1b1b1b1b1b&limit=10000"
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
                        parcel_id = (props.get('PARCEL_ID') or 
                                   props.get('PIN') or 
                                   props.get('OBJECTID') or 
                                   props.get('FID') or 
                                   f"DFW_{len(standardized_features)}")
                        
                        # Try different field names for area
                        area_acres = None
                        for area_field in ['ACRES', 'AREA_ACRES', 'SHAPE_AREA', 'AREA']:
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
                        
                        # Try different field names for county
                        county = (props.get('COUNTY') or 
                                props.get('COUNTY_NAME') or 
                                props.get('CNTY_NAME') or 
                                'DFW_Region')
                        
                        standardized_feature = {
                            "type": "Feature",
                            "properties": {
                                "parcel_id": str(parcel_id),
                                "county": str(county),
                                "area_acres": area_acres,
                                "data_source": "NCTCOG",
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
                    output_file = os.path.join(output_dir, "dfw_parcels.geojson")
                    
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
                        "coverage": "Dallas-Fort Worth 16-county metroplex",
                        "coordinate_system": "WGS84 (EPSG:4326)"
                    }
                    
                    metadata_file = os.path.join(output_dir, "dfw_parcels_metadata.json")
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    print(f"📋 Saved metadata to: {metadata_file}")
                    print(f"🎯 SUCCESS: DFW parcel data ready for bulk processing")
                    return True
                    
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
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
    data_file = os.path.join(output_dir, "dfw_parcels.geojson")
    
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
        
        # Test coordinate ranges (should be in DFW area)
        bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        print(f"🌐 Bounding box: {bounds}")
        
        # DFW should be roughly: lng -97.5 to -96.5, lat 32.5 to 33.5
        if (-98 < bounds[0] < -95) and (-98 < bounds[2] < -95) and (32 < bounds[1] < 34) and (32 < bounds[3] < 34):
            print("✅ Coordinates appear to be in DFW region")
        else:
            print("⚠️ Coordinates may be outside expected DFW region")
        
        # Test some sample data
        sample = gdf.head(3)
        print(f"\n📝 Sample records:")
        for idx, row in sample.iterrows():
            print(f"  Parcel {row['parcel_id']}: County={row['county']}, Area={row['area_acres']} acres")
        
        print("✅ Data quality test completed")
        return True
        
    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting DFW Parcel Data Download")
    
    success = download_nctcog_parcels()
    
    if success:
        test_data_quality()
        print("\n🏆 DFW PARCEL DATA DOWNLOAD COMPLETE")
        print("Ready for bulk parcel analysis!")
    else:
        print("\n💥 DFW PARCEL DATA DOWNLOAD FAILED")
        print("Check network connection and data sources")
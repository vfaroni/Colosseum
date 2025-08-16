#!/usr/bin/env python3
"""
Download California libraries data from OpenStreetMap using Overpass API
"""

import requests
import json
import time
from pathlib import Path

def download_ca_libraries():
    """Download California libraries from OpenStreetMap"""
    
    # Overpass API query for California libraries
    # California bounding box: [32.534, -124.482, 42.009, -114.131]
    overpass_query = """
    [out:json][timeout:60];
    (
      node["amenity"="library"](32.534,-124.482,42.009,-114.131);
      way["amenity"="library"](32.534,-124.482,42.009,-114.131);
      relation["amenity"="library"](32.534,-124.482,42.009,-114.131);
    );
    out geom;
    """
    
    # Overpass API endpoint
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Output directory
    output_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/CA_Libraries")
    output_dir.mkdir(exist_ok=True)
    
    print("Downloading California libraries from OpenStreetMap...")
    print(f"Output directory: {output_dir}")
    
    try:
        # Make the request
        response = requests.post(overpass_url, data=overpass_query, timeout=120)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        print(f"Downloaded {len(data.get('elements', []))} library records")
        
        # Save raw JSON
        json_file = output_dir / "CA_Libraries_OSM.json"
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved raw data to: {json_file}")
        
        # Convert to GeoJSON format
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        for element in data.get('elements', []):
            if element['type'] == 'node':
                feature = {
                    "type": "Feature",
                    "properties": element.get('tags', {}),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [element['lon'], element['lat']]
                    }
                }
                geojson['features'].append(feature)
            elif element['type'] == 'way' and 'geometry' in element:
                # For ways with geometry
                coordinates = [[point['lon'], point['lat']] for point in element['geometry']]
                feature = {
                    "type": "Feature",
                    "properties": element.get('tags', {}),
                    "geometry": {
                        "type": "LineString" if coordinates[0] != coordinates[-1] else "Polygon",
                        "coordinates": [coordinates] if coordinates[0] == coordinates[-1] else coordinates
                    }
                }
                geojson['features'].append(feature)
        
        # Save GeoJSON
        geojson_file = output_dir / "CA_Libraries_OSM.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(geojson, f, indent=2)
        print(f"Saved GeoJSON to: {geojson_file}")
        
        # Create summary
        summary = {
            "source": "OpenStreetMap via Overpass API",
            "query_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_features": len(geojson['features']),
            "bounding_box": "California (32.534,-124.482,42.009,-114.131)",
            "feature_types": {
                "nodes": sum(1 for f in geojson['features'] if f['geometry']['type'] == 'Point'),
                "ways": sum(1 for f in geojson['features'] if f['geometry']['type'] in ['LineString', 'Polygon'])
            }
        }
        
        summary_file = output_dir / "CA_Libraries_OSM_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Saved summary to: {summary_file}")
        
        print(f"✅ Successfully downloaded {summary['total_features']} California libraries")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading data: {e}")
        return False
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return False

if __name__ == "__main__":
    download_ca_libraries()
#!/usr/bin/env python3
"""Test GeoJSON loading"""

import json
from pathlib import Path

# Define the path
transit_path = Path(__file__).parent.parent / "priorcode/!VFupload/CALIHTCScorer/data/transit/california_transit_stops_master.geojson"

print(f"Loading: {transit_path}")
print(f"Exists: {transit_path.exists()}")
print(f"Size: {transit_path.stat().st_size / (1024*1024):.1f} MB")

try:
    print("Attempting to load GeoJSON...")
    with open(transit_path, 'r') as f:
        # Load just the first few lines to test
        first_lines = []
        for i, line in enumerate(f):
            first_lines.append(line)
            if i >= 5:  # Read first 6 lines
                break
    
    print("First few lines:")
    for i, line in enumerate(first_lines):
        print(f"{i}: {line.strip()[:100]}...")
    
    # Try to load as JSON with size limit
    print("\nAttempting full JSON load (this may take time for 50MB file)...")
    with open(transit_path, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Successfully loaded GeoJSON")
    print(f"Type: {type(data)}")
    print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
    
    if 'features' in data:
        print(f"Number of features: {len(data['features'])}")
        if data['features']:
            first_feature = data['features'][0]
            print(f"First feature keys: {list(first_feature.keys())}")
            if 'geometry' in first_feature:
                geom = first_feature['geometry']
                print(f"Geometry type: {geom.get('type')}")
                print(f"Coordinates sample: {geom.get('coordinates')}")

except Exception as e:
    print(f"❌ Error loading GeoJSON: {e}")
    import traceback
    traceback.print_exc()
#!/usr/bin/env python3

"""
Demonstration of Parcel Edge Distance Analysis
Shows concept without loading full 6.7GB files
"""

import pandas as pd
import json
from datetime import datetime
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import nearest_points
import numpy as np

def calculate_edge_distance_demo(parcel_corners, amenity_point):
    """
    Calculate minimum distance from amenity to parcel edge
    Returns distance in miles
    """
    # Create polygon from corners
    polygon = Polygon([(lng, lat) for lat, lng in parcel_corners])
    
    # Create point for amenity
    point = Point(amenity_point[1], amenity_point[0])  # (lng, lat)
    
    # Get nearest point on boundary
    nearest_edge_point, _ = nearest_points(polygon.boundary, point)
    
    # Calculate distance (degrees to miles approximation)
    distance_degrees = point.distance(nearest_edge_point)
    distance_miles = distance_degrees * 69
    
    return distance_miles, (nearest_edge_point.y, nearest_edge_point.x)

def apply_ctcac_scoring(distances):
    """Apply CTCAC scoring based on distances"""
    scores = {}
    total = 0
    
    # Transit scoring
    if distances['transit'] <= 0.33:
        scores['transit'] = {'points': 7, 'type': 'HQTA'}
        total += 7
    elif distances['transit'] <= 0.5:
        scores['transit'] = {'points': 5, 'type': 'Frequent Service'}
        total += 5
    else:
        scores['transit'] = {'points': 0, 'type': 'No Transit Points'}
    
    # Park scoring
    if distances['park'] <= 0.5:
        scores['park'] = {'points': 3, 'type': 'Within 0.5 mi'}
        total += 3
    elif distances['park'] <= 0.75:
        scores['park'] = {'points': 2, 'type': 'Within 0.75 mi'}
        total += 2
    else:
        scores['park'] = {'points': 0, 'type': 'No Park Points'}
    
    # Grocery scoring
    if distances['grocery'] <= 0.5:
        scores['grocery'] = {'points': 5, 'type': 'Full Scale < 0.5 mi'}
        total += 5
    elif distances['grocery'] <= 1.0:
        scores['grocery'] = {'points': 4, 'type': 'Full Scale < 1.0 mi'}
        total += 4
    elif distances['grocery'] <= 1.5:
        scores['grocery'] = {'points': 3, 'type': 'Full Scale < 1.5 mi'}
        total += 3
    else:
        scores['grocery'] = {'points': 0, 'type': 'No Grocery Points'}
    
    # School scoring
    if distances['school'] <= 0.25:
        scores['school'] = {'points': 3, 'type': 'Elementary < 0.25 mi'}
        total += 3
    elif distances['school'] <= 0.75:
        scores['school'] = {'points': 2, 'type': 'Elementary < 0.75 mi'}
        total += 2
    else:
        scores['school'] = {'points': 0, 'type': 'No School Points'}
    
    # Medical scoring
    if distances['medical'] <= 0.5:
        scores['medical'] = {'points': 3, 'type': 'Within 0.5 mi'}
        total += 3
    elif distances['medical'] <= 1.0:
        scores['medical'] = {'points': 2, 'type': 'Within 1.0 mi'}
        total += 2
    else:
        scores['medical'] = {'points': 0, 'type': 'No Medical Points'}
        
    scores['total'] = total
    return scores

def main():
    print("🏛️ PARCEL EDGE DISTANCE DEMONSTRATION")
    print("=" * 60)
    print(f"Demonstration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load one site from CostarExport-11.xlsx
    costar_file = 'Sites/CostarExport-11.xlsx'
    df = pd.read_excel(costar_file)
    
    # Get first LA site with coordinates
    la_sites = df[(df['County Name'] == 'Los Angeles') & 
                  (df['Latitude'].notna()) & 
                  (df['Longitude'].notna())]
    
    if la_sites.empty:
        print("No LA sites found with coordinates")
        return
        
    site = la_sites.iloc[0]
    
    print(f"📍 Demo Site: {site['Property Address']}")
    print(f"   Location: ({site['Latitude']:.6f}, {site['Longitude']:.6f})")
    print(f"   County: {site['County Name']}")
    print()
    
    # Mock parcel corners (rectangle around the site)
    # In reality, these would come from the parcel GeoJSON
    lat, lng = site['Latitude'], site['Longitude']
    offset = 0.001  # About 360 feet
    
    parcel_corners = [
        (lat + offset, lng - offset),  # NW corner
        (lat + offset, lng + offset),  # NE corner  
        (lat - offset, lng + offset),  # SE corner
        (lat - offset, lng - offset),  # SW corner
    ]
    
    print("📐 Parcel Information:")
    print(f"   Mock APN: 1234-567-890")
    print(f"   Corners: {len(parcel_corners)}")
    for i, (plat, plng) in enumerate(parcel_corners):
        print(f"      Corner {i+1}: ({plat:.6f}, {plng:.6f})")
    
    # Calculate approximate area
    width_miles = offset * 2 * 69
    area_acres = (width_miles ** 2) * 640
    print(f"   Area: {area_acres:.2f} acres")
    print()
    
    # Mock amenity locations
    amenities = {
        'transit': (lat + 0.003, lng + 0.002),  # ~0.25 miles away
        'park': (lat - 0.004, lng + 0.003),     # ~0.35 miles
        'grocery': (lat + 0.008, lng - 0.006),  # ~0.65 miles
        'school': (lat - 0.002, lng - 0.003),   # ~0.22 miles
        'medical': (lat + 0.011, lng + 0.009),  # ~0.95 miles
    }
    
    print("📏 Distance Calculations (to nearest parcel edge):")
    distances = {}
    
    for amenity_type, amenity_loc in amenities.items():
        dist, nearest_point = calculate_edge_distance_demo(parcel_corners, amenity_loc)
        distances[amenity_type] = dist
        print(f"   {amenity_type.capitalize()}: {dist:.3f} miles")
        print(f"      Nearest edge point: ({nearest_point[0]:.6f}, {nearest_point[1]:.6f})")
    
    print()
    
    # Apply CTCAC scoring
    scores = apply_ctcac_scoring(distances)
    
    print("🎯 CTCAC Scoring Results:")
    print(f"   Total Score: {scores['total']} points")
    print()
    print("   Breakdown:")
    for category in ['transit', 'park', 'grocery', 'school', 'medical']:
        if category in scores:
            score_info = scores[category]
            print(f"   - {category.capitalize()}: {score_info['points']} pts ({score_info['type']})")
    
    print()
    
    # Create output summary
    output_file = costar_file.replace('.xlsx', '_EDGE_DEMO_RESULTS.xlsx')
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Original data
        df.head(10).to_excel(writer, sheet_name='Sample_CoStar_Data', index=False)
        
        # Demo results
        demo_results = pd.DataFrame([{
            'Site': site['Property Address'],
            'County': site['County Name'],
            'Latitude': site['Latitude'],
            'Longitude': site['Longitude'],
            'Mock_APN': '1234-567-890',
            'Parcel_Corners': len(parcel_corners),
            'Parcel_Area_Acres': round(area_acres, 2),
            'Transit_Distance_Miles': round(distances['transit'], 3),
            'Park_Distance_Miles': round(distances['park'], 3),
            'Grocery_Distance_Miles': round(distances['grocery'], 3),
            'School_Distance_Miles': round(distances['school'], 3),
            'Medical_Distance_Miles': round(distances['medical'], 3),
            'CTCAC_Total_Score': scores['total'],
            'Transit_Score': scores['transit']['points'],
            'Park_Score': scores['park']['points'],
            'Grocery_Score': scores['grocery']['points'],
            'School_Score': scores['school']['points'],
            'Medical_Score': scores['medical']['points']
        }])
        demo_results.to_excel(writer, sheet_name='Edge_Distance_Analysis', index=False)
        
        # CTCAC scoring rules
        scoring_rules = pd.DataFrame([
            {'Category': 'Transit (HQTA)', 'Max Distance': '0.33 mi', 'Points': 7},
            {'Category': 'Transit (Frequent)', 'Max Distance': '0.50 mi', 'Points': 5},
            {'Category': 'Park', 'Max Distance': '0.50 mi', 'Points': 3},
            {'Category': 'Park', 'Max Distance': '0.75 mi', 'Points': 2},
            {'Category': 'Grocery (Full)', 'Max Distance': '0.50 mi', 'Points': 5},
            {'Category': 'Grocery (Full)', 'Max Distance': '1.00 mi', 'Points': 4},
            {'Category': 'Grocery (Full)', 'Max Distance': '1.50 mi', 'Points': 3},
            {'Category': 'Elementary School', 'Max Distance': '0.25 mi', 'Points': 3},
            {'Category': 'Elementary School', 'Max Distance': '0.75 mi', 'Points': 2},
            {'Category': 'Medical', 'Max Distance': '0.50 mi', 'Points': 3},
            {'Category': 'Medical', 'Max Distance': '1.00 mi', 'Points': 2}
        ])
        scoring_rules.to_excel(writer, sheet_name='CTCAC_Scoring_Rules', index=False)
    
    print(f"💾 Results saved to: {output_file}")
    print()
    print("✅ Demonstration Complete!")
    print("   This shows the exact methodology for:")
    print("   - Finding parcel boundaries and corners")
    print("   - Calculating distances to nearest parcel edge")
    print("   - Applying CTCAC scoring from Perris model")
    print()
    print("📝 Note: For production use with real parcel data:")
    print("   - Use spatial indexing for 6.7GB files")
    print("   - Query actual amenity locations from datasets")
    print("   - Process in batches to manage memory")


if __name__ == "__main__":
    main()
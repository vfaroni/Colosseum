#!/usr/bin/env python3
"""
Extract amenity coordinates and details from the San Jacinto Vista II developer map HTML file.
"""

import re
import json
from pathlib import Path

def extract_amenities_from_html(html_file_path):
    """
    Extract all amenity markers with their coordinates, types, and other details from the HTML file.
    """
    
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    amenities = []
    
    # Pattern to match marker definitions with coordinates
    marker_pattern = r'var\s+marker_(\w+)\s*=\s*L\.marker\(\s*\[([0-9.]+),\s*(-[0-9.]+)\]'
    
    # Pattern to match popup content for amenities
    popup_pattern = r'<b>#(\d+):\s*([^<]+)</b><br>\s*<b>Type:</b>\s*([^<]+)<br>\s*<b>Category:</b>\s*([^<]+)<br>\s*<b>Distance:</b>\s*([^<]+)'
    
    # Find all marker definitions
    marker_matches = re.findall(marker_pattern, html_content)
    
    # Create a dictionary mapping marker IDs to coordinates
    marker_coords = {}
    for marker_id, lat, lon in marker_matches:
        marker_coords[marker_id] = (float(lat), float(lon))
    
    # Find all popup content for amenities
    popup_matches = re.findall(popup_pattern, html_content)
    
    # Extract the correspondence between markers and popups
    marker_popup_pattern = r'marker_(\w+)\.bindPopup\(popup_(\w+)\)'
    marker_popup_matches = re.findall(marker_popup_pattern, html_content)
    
    # Create mapping from marker to popup
    marker_to_popup = {}
    for marker_id, popup_id in marker_popup_matches:
        marker_to_popup[marker_id] = popup_id
    
    # Extract popup content with IDs
    popup_content_pattern = r'var\s+html_(\w+)\s*=\s*\$\(`<div[^>]*>(.*?)</div>`\)\[0\]'
    popup_content_matches = re.findall(popup_content_pattern, html_content, re.DOTALL)
    
    # Create mapping from popup HTML ID to content
    popup_content = {}
    for html_id, content in popup_content_matches:
        popup_content[html_id] = content
    
    # Extract popup ID to HTML ID mapping
    popup_html_pattern = r'popup_(\w+)\.setContent\(html_(\w+)\)'
    popup_html_matches = re.findall(popup_html_pattern, html_content)
    
    # Create mapping from popup ID to HTML ID
    popup_to_html = {}
    for popup_id, html_id in popup_html_matches:
        popup_to_html[popup_id] = html_id
    
    # Process each marker that has coordinates
    for marker_id, coords in marker_coords.items():
        if marker_id in marker_to_popup:
            popup_id = marker_to_popup[marker_id]
            if popup_id in popup_to_html:
                html_id = popup_to_html[popup_id]
                if html_id in popup_content:
                    content = popup_content[html_id]
                    
                    # Parse the popup content for amenity information
                    amenity_match = re.search(popup_pattern, content)
                    if amenity_match:
                        number, name, type_info, category, distance = amenity_match.groups()
                        
                        amenity = {
                            'id': int(number),
                            'name': name.strip(),
                            'type': type_info.strip(),
                            'category': category.strip(),
                            'distance': distance.strip(),
                            'latitude': coords[0],
                            'longitude': coords[1]
                        }
                        amenities.append(amenity)
    
    # Sort amenities by ID number
    amenities.sort(key=lambda x: x['id'])
    
    return amenities

def main():
    html_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/san_jacinto_vista_ii_developer_scaled_map.html")
    
    print("Extracting amenities from San Jacinto Vista II developer map...")
    
    amenities = extract_amenities_from_html(html_file)
    
    print(f"\nFound {len(amenities)} amenities:\n")
    
    # Group by category
    categories = {}
    for amenity in amenities:
        category = amenity['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(amenity)
    
    # Print summary by category
    for category, items in categories.items():
        print(f"\n{category.upper()} ({len(items)} items):")
        print("-" * 50)
        for item in items:
            print(f"  #{item['id']}: {item['name']}")
            print(f"    Type: {item['type']}")
            print(f"    Distance: {item['distance']}")
            print(f"    Coordinates: {item['latitude']}, {item['longitude']}")
            print()
    
    # Save to JSON file
    output_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/san_jacinto_vista_ii_amenities.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(amenities, f, indent=2, ensure_ascii=False)
    
    print(f"\nAmenity data saved to: {output_file}")

if __name__ == "__main__":
    main()
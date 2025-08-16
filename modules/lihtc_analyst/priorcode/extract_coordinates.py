#!/usr/bin/env python3

import re

# Read the HTML file
with open('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/san_jacinto_vista_ii_developer_scaled_map.html', 'r') as f:
    content = f.read()

# Extract polygon coordinates (property parcel)
polygon_match = re.search(r'L\.polygon\(\s*\[([^\]]+)\]', content, re.DOTALL)
if polygon_match:
    polygon_coords = polygon_match.group(1)
    print("=== PROPERTY PARCEL COORDINATES ===")
    print("From L.polygon line:")
    print(polygon_coords.strip())
    
    # Extract individual coordinates
    coords = re.findall(r'\[([0-9.]+), (-[0-9.]+)\]', polygon_coords)
    print("\nIndividual corner coordinates:")
    for i, (lat, lon) in enumerate(coords, 1):
        print(f"Corner {i}: {lat}, {lon}")

print("\n=== AMENITY MARKERS ===")

# Find all marker definitions with their coordinates
marker_pattern = r'var (marker_[a-f0-9]+) = L\.marker\(\s*\[([0-9.]+), (-[0-9.]+)\]'
markers = re.findall(marker_pattern, content)

# Find all HTML content with amenity information
html_pattern = r'var (html_[a-f0-9]+) = \$\(`<div[^>]*>([^`]+)</div>`\)\[0\];'
html_contents = re.findall(html_pattern, content)

# Create a mapping from popup to HTML content
popup_to_html = {}
for html_id, html_content in html_contents:
    # Find which popup uses this HTML
    popup_match = re.search(rf'popup_([a-f0-9]+)\.setContent\({html_id}\);', content)
    if popup_match:
        popup_id = popup_match.group(1)
        popup_to_html[popup_id] = html_content

# Find marker to popup bindings
marker_to_popup = {}
binding_pattern = r'(marker_[a-f0-9]+)\.bindPopup\(popup_([a-f0-9]+)\)'
bindings = re.findall(binding_pattern, content)
for marker_id, popup_id in bindings:
    marker_to_popup[marker_id] = popup_id

# Now combine everything
results = []
for marker_id, lat, lon in markers:
    popup_id = marker_to_popup.get(marker_id)
    if popup_id:
        html_content = popup_to_html.get(popup_id, "")
        
        # Extract amenity information
        if "<b>#" in html_content:
            # This is a numbered amenity
            name_match = re.search(r'<b>(#[0-9]+: [^<]+)</b>', html_content)
            distance_match = re.search(r'<b>Distance:</b> ([0-9.]+) miles', html_content)
            
            if name_match and distance_match:
                name = name_match.group(1)
                distance = float(distance_match.group(1))
                # Truncate to 2 decimal places (don't round)
                distance_truncated = int(distance * 100) / 100
                results.append((lat, lon, name, distance_truncated))
                
# Sort by the order they appear in the file (already in order from regex)
print("Coordinates and amenity information (in order of appearance):")
for i, (lat, lon, name, distance) in enumerate(results, 1):
    print(f"{i}. Coordinates: {lat}, {lon} - {name} - {distance:.2f} mi")
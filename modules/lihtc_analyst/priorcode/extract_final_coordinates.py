import re
import math

def truncate_to_2_decimal(value):
    """Truncate to exactly 2 decimal places"""
    num = float(value)
    return math.floor(num * 100) / 100

# Read the HTML file
with open('san_jacinto_vista_ii_developer_scaled_map.html', 'r') as f:
    content = f.read()

print("PROPERTY PARCEL COORDINATES (4 corners):")
print("From line 609 - L.polygon:")
# Extract the specific coordinates from the polygon
coords = [
    [33.79377, -117.22184],
    [33.79376, -117.2205],
    [33.79211, -117.22048],
    [33.79213, -117.22173]
]

for i, (lat, lon) in enumerate(coords):
    lat_truncated = truncate_to_2_decimal(lat)
    lon_truncated = truncate_to_2_decimal(lon)
    print(f"  {i+1}: [{lat_truncated}, {lon_truncated}]")

print("\nALL MARKERS IN ORDER WITH AMENITY NAMES:")
print("=" * 60)

# Extract all marker variables and their coordinates
marker_pattern = r'var (marker_[a-f0-9]+) = L\.marker\(\s*\[([\d.-]+),\s*([\d.-]+)\]'
marker_matches = re.findall(marker_pattern, content)

# Create a mapping of marker IDs to coordinates
marker_coords = {}
for marker_id, lat, lon in marker_matches:
    marker_coords[marker_id] = (lat, lon)

# Find all numbered amenities and their popup binding
numbered_amenities = []
numbered_pattern = r'<b>(#\d+:.*?)</b>'
numbered_matches = re.findall(numbered_pattern, content)

# For each numbered amenity, find which marker it's bound to
for amenity in numbered_matches:
    # Find the popup that contains this amenity
    popup_pattern = re.escape(amenity)
    popup_match = re.search(popup_pattern, content)
    if popup_match:
        # Find the marker binding for this popup
        start_pos = popup_match.start()
        # Look for the marker binding after this popup
        binding_pattern = r'(marker_[a-f0-9]+)\.bindPopup'
        binding_matches = re.finditer(binding_pattern, content)
        
        for binding_match in binding_matches:
            if binding_match.start() > start_pos:
                marker_id = binding_match.group(1)
                if marker_id in marker_coords:
                    lat, lon = marker_coords[marker_id]
                    lat_truncated = truncate_to_2_decimal(lat)
                    lon_truncated = truncate_to_2_decimal(lon)
                    numbered_amenities.append({
                        'name': amenity,
                        'coords': [lat_truncated, lon_truncated],
                        'marker_id': marker_id
                    })
                    break

print(f"Found {len(numbered_amenities)} numbered amenities with coordinates:")
for i, amenity in enumerate(numbered_amenities, 1):
    print(f"  {i}: [{amenity['coords'][0]}, {amenity['coords'][1]}] - {amenity['name']}")

print("\n" + "=" * 60)
print("SUMMARY:")
print(f"Property corners: 4")
print(f"Numbered amenities: {len(numbered_amenities)}")
print(f"Total markers in file: {len(marker_matches)}")
import re
import math

def truncate_to_2_decimal(value):
    """Truncate to exactly 2 decimal places"""
    num = float(value)
    return math.floor(num * 100) / 100

# Read the HTML file
with open('san_jacinto_vista_ii_developer_scaled_map.html', 'r') as f:
    content = f.read()

# Extract property parcel coordinates from line 609
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
print("=" * 50)

# Extract markers and their corresponding popup content
# We need to find the marker coordinates and match them with their popup content
marker_pattern = r'var marker_[a-f0-9]+ = L\.marker\(\s*\[([\d.-]+),\s*([\d.-]+)\]'
marker_matches = re.findall(marker_pattern, content)

# Find all popup content in order
popup_content = []
popup_pattern = r'<b>(.*?)</b>'
popup_matches = re.findall(popup_pattern, content)

# Extract specific numbered amenities with full context
numbered_pattern = r'<b>(#\d+:.*?)</b>'
numbered_matches = re.findall(numbered_pattern, content)

print(f"Found {len(marker_matches)} markers total")
print(f"Found {len(numbered_matches)} numbered amenities")

# Print all markers with their coordinates
for i, (lat, lon) in enumerate(marker_matches):
    lat_truncated = truncate_to_2_decimal(lat)
    lon_truncated = truncate_to_2_decimal(lon)
    
    # Try to find the corresponding popup name
    popup_name = "Unknown"
    if i < len(popup_matches):
        popup_name = popup_matches[i]
    
    print(f"  {i+1}: [{lat_truncated}, {lon_truncated}] - {popup_name}")

print("\n" + "=" * 50)
print("NUMBERED AMENITIES FOUND:")
for i, amenity in enumerate(numbered_matches):
    print(f"  {i+1}: {amenity}")
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
# Extract the specific coordinates from the polygon (from line 609)
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

# Let's manually find and extract the numbered amenities with their exact coordinates
# Since I know the first one is at [33.79178000100006, -117.217515], let me find them systematically

amenity_coords = []

# Find each numbered amenity and its coordinates
for i in range(1, 50):  # Looking for #1 through #49
    pattern = rf'<b>(#{i}:.*?)</b>'
    match = re.search(pattern, content)
    if match:
        amenity_name = match.group(1)
        
        # Find the popup that contains this amenity
        popup_start = match.start()
        
        # Find the marker binding for this popup (search backwards and forwards)
        # Look for the marker variable that binds to this popup
        before_popup = content[:popup_start]
        after_popup = content[popup_start:]
        
        # Find the marker binding after this popup
        binding_match = re.search(r'(marker_[a-f0-9]+)\.bindPopup', after_popup)
        if binding_match:
            marker_id = binding_match.group(1)
            
            # Find the coordinates for this marker
            coord_pattern = rf'var {marker_id} = L\.marker\(\s*\[([\d.-]+),\s*([\d.-]+)\]'
            coord_match = re.search(coord_pattern, content)
            if coord_match:
                lat = float(coord_match.group(1))
                lon = float(coord_match.group(2))
                lat_truncated = truncate_to_2_decimal(lat)
                lon_truncated = truncate_to_2_decimal(lon)
                amenity_coords.append({
                    'num': i,
                    'name': amenity_name,
                    'coords': [lat_truncated, lon_truncated],
                    'original_coords': [lat, lon]
                })

print(f"Found {len(amenity_coords)} numbered amenities with coordinates:")
for amenity in amenity_coords:
    print(f"  {amenity['num']}: [{amenity['coords'][0]}, {amenity['coords'][1]}] - {amenity['name']}")

print("\n" + "=" * 60)
print("FIRST 10 WITH ORIGINAL COORDINATES (for verification):")
for amenity in amenity_coords[:10]:
    print(f"  {amenity['num']}: [{amenity['original_coords'][0]}, {amenity['original_coords'][1]}] -> [{amenity['coords'][0]}, {amenity['coords'][1]}] - {amenity['name']}")

print("\n" + "=" * 60)
print("SUMMARY:")
print(f"Property corners: 4")
print(f"Numbered amenities: {len(amenity_coords)}")
import re
import math

def truncate_to_2_decimal(value):
    """Truncate to exactly 2 decimal places"""
    num = float(value)
    return math.floor(num * 100) / 100

# Read the HTML file
with open('san_jacinto_vista_ii_developer_scaled_map.html', 'r') as f:
    content = f.read()

# Extract property parcel coordinates from the first polygon
polygon_match = re.search(r'L\.polygon\(\s*\[\[(.*?)\]\]', content)
if polygon_match:
    coords_str = polygon_match.group(1)
    coords_list = re.findall(r'\[([\d.-]+),\s*([\d.-]+)\]', coords_str)
    print("Property Parcel Coordinates (4 corners):")
    for i, (lat, lon) in enumerate(coords_list[:4]):  # First 4 are the corners
        lat_truncated = truncate_to_2_decimal(lat)
        lon_truncated = truncate_to_2_decimal(lon)
        print(f"  {i+1}: [{lat_truncated}, {lon_truncated}]")

# Extract all markers with their coordinates
marker_matches = re.findall(r'var marker_[a-f0-9]+ = L\.marker\(\s*\[([\d.-]+),\s*([\d.-]+)\]', content)

# Extract popup content - this is more complex, need to match them in order
# Look for popup content patterns
popup_matches = re.findall(r'<b>(.*?)</b>', content)

print(f"\nAll Markers (in order) - Found {len(marker_matches)} markers:")
for i, (lat, lon) in enumerate(marker_matches):
    lat_truncated = truncate_to_2_decimal(lat)
    lon_truncated = truncate_to_2_decimal(lon)
    
    # Find the corresponding popup name
    popup_name = "Unknown"
    if i < len(popup_matches):
        popup_name = popup_matches[i]
    
    print(f"  {i+1}: [{lat_truncated}, {lon_truncated}] - {popup_name}")

# Let's also extract the numbered amenities specifically
print("\n--- Numbered Amenities ---")
numbered_amenities = re.findall(r'<b>(#\d+:.*?)</b>', content)
numbered_coords = []

# Find coordinates for numbered amenities
for amenity in numbered_amenities:
    print(f"Found amenity: {amenity}")
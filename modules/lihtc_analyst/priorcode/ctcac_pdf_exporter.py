#!/usr/bin/env python3
"""
CTCAC PDF Exporter
Export clean, printable PDF maps for LIHTC applications
"""

import folium
import webbrowser
import tempfile
import os
from pathlib import Path
import time

def create_printable_map(parcel_corners, project_name, project_address, 
                        amenities_data, site_name="Development Site"):
    """
    Create a clean, printable map for PDF export without legend
    
    Args:
        parcel_corners: Dict with 'nw', 'ne', 'sw', 'se' corners as (lat, lng) tuples
        project_name: Name of the project (e.g., "San Jacinto Vista II")
        project_address: Full address (e.g., "202 E. Jarvis St., Perris, CA")
        amenities_data: Results from CTCAC analysis containing amenities
        site_name: Name for the development site marker
    
    Returns:
        Folium map object ready for PDF export
    """
    
    # Calculate center point of parcel
    center_lat = (parcel_corners['nw'][0] + parcel_corners['ne'][0] + 
                 parcel_corners['sw'][0] + parcel_corners['se'][0]) / 4
    center_lng = (parcel_corners['nw'][1] + parcel_corners['ne'][1] + 
                 parcel_corners['sw'][1] + parcel_corners['se'][1]) / 4
    
    # Create map with title and optimal size for US Letter portrait
    m = folium.Map(
        location=[center_lat, center_lng], 
        zoom_start=15,
        width='8.5in',  # US Letter width
        height='9in'    # Leave space for title
    )
    
    # Add project title at the top
    title_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 50%; transform: translateX(-50%);
                background-color: white; 
                border: 2px solid #2E7D32; 
                border-radius: 5px;
                padding: 8px 16px;
                z-index: 9999; 
                font-family: Arial, sans-serif;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);">
        <h3 style="margin: 0; color: #2E7D32; text-align: center; font-size: 16px;">
            {project_name}
        </h3>
        <p style="margin: 2px 0 0 0; color: #333; text-align: center; font-size: 12px;">
            {project_address}
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add parcel boundary
    parcel_folium_coords = [
        [parcel_corners['nw'][0], parcel_corners['nw'][1]],
        [parcel_corners['ne'][0], parcel_corners['ne'][1]],
        [parcel_corners['se'][0], parcel_corners['se'][1]],
        [parcel_corners['sw'][0], parcel_corners['sw'][1]],
        [parcel_corners['nw'][0], parcel_corners['nw'][1]]  # Close polygon
    ]
    
    folium.Polygon(
        locations=parcel_folium_coords,
        color='darkred',
        weight=3,
        fill=True,
        fillColor='red',
        fillOpacity=0.1,
        popup=f'{site_name} Parcel (5.26 acres)'
    ).add_to(m)
    
    # Add corner markers
    corner_labels = {'nw': 'NW', 'ne': 'NE', 'sw': 'SW', 'se': 'SE'}
    for corner, label in corner_labels.items():
        lat, lng = parcel_corners[corner]
        folium.Marker(
            [lat, lng],
            icon=folium.DivIcon(
                html=f'<div style="font-size: 10pt; color: darkred; font-weight: bold; '
                     f'background: white; padding: 2px 4px; border: 1px solid darkred; '
                     f'border-radius: 3px;">{label}</div>'
            )
        ).add_to(m)
    
    # Add center marker
    folium.Marker(
        [center_lat, center_lng],
        popup=f'{site_name}<br>{project_address}',
        icon=folium.Icon(color='red', icon='home', prefix='fa')
    ).add_to(m)
    
    # Add distance circles (0.25, 1/3, 0.5, 1.0 mile)
    distance_circles = [
        (0.25, 'black', '1/4 Mile', '5,3'),
        (0.333, 'gray', '1/3 Mile', '8,4'), 
        (0.5, 'darkgray', '1/2 Mile', '12,6'),
        (1.0, 'lightgray', '1 Mile', '15,8')
    ]
    
    for dist_miles, color, label, dash_pattern in distance_circles:
        # Convert miles to meters for radius
        radius_meters = dist_miles * 1609.34
        
        folium.Circle(
            [center_lat, center_lng],
            radius=radius_meters,
            color=color,
            weight=2,
            fill=False,
            dashArray=dash_pattern,
            popup=f'{label} from site center'
        ).add_to(m)
        
        # Add distance label
        label_lat = center_lat + (dist_miles * 0.012)  # Offset north
        folium.Marker(
            [label_lat, center_lng],
            icon=folium.DivIcon(
                html=f'<div style="font-size: 10pt; color: {color}; font-weight: bold; '
                     f'background: white; padding: 1px 3px; border-radius: 3px; '
                     f'border: 1px solid {color};">{label}</div>'
            )
        ).add_to(m)
    
    # Add ALL numbered amenity markers (matching original legend exactly)
    if amenities_data and 'amenities_found' in amenities_data:
        marker_counter = 1
        
        # Use exact same colors as original CTCAC mapper
        category_colors = {
            'transit': 'green',
            'public_parks': 'darkgreen', 
            'libraries': 'purple',
            'grocery': 'cadetblue',
            'schools': 'blue',
            'medical': 'red',
            'pharmacies': 'pink'
        }
        
        for category, amenities in amenities_data['amenities_found'].items():
            if not amenities:
                continue
                
            color = category_colors.get(category, 'gray')
            
            # Show ALL amenities, not just closest 5 - sort by distance
            sorted_amenities = sorted(amenities, key=lambda x: x.get('distance_miles', 999))
            
            for amenity in sorted_amenities:
                if 'latitude' in amenity and 'longitude' in amenity:
                    name = amenity.get('name', 'Unknown')
                    distance = amenity.get('distance_miles', 0)
                    
                    folium.Marker(
                        [amenity['latitude'], amenity['longitude']],
                        popup=f'<b>#{marker_counter}: {name}</b><br>'
                              f'Category: {category.replace("_", " ").title()}<br>'
                              f'Distance: {distance:.2f} miles',
                        icon=folium.DivIcon(
                            html=f'<div style="background-color: {color}; color: white; '
                                 f'width: 20px; height: 20px; border-radius: 50%; '
                                 f'text-align: center; line-height: 20px; font-size: 10px; '
                                 f'font-weight: bold; border: 2px solid white;">{marker_counter}</div>'
                        )
                    ).add_to(m)
                    
                    marker_counter += 1
    
    return m


def export_to_pdf(map_obj, output_filename, open_browser=True):
    """
    Export map to HTML and optionally open in browser for PDF printing
    
    Args:
        map_obj: Folium map object
        output_filename: Name for the output HTML file
        open_browser: Whether to automatically open in browser for printing
    
    Returns:
        Path to the exported HTML file
    """
    
    # Save map to HTML
    output_path = Path(output_filename)
    map_obj.save(str(output_path))
    
    print(f"✅ Printable map exported to: {output_path}")
    print(f"📄 To create PDF: Open in browser → Print → Save as PDF")
    print(f"📐 Recommended: Portrait orientation, US Letter size")
    
    if open_browser:
        # Open in default browser for printing
        file_url = f"file://{output_path.absolute()}"
        webbrowser.open(file_url)
        print(f"🌐 Opened in browser: {file_url}")
    
    return output_path


def create_san_jacinto_printable_pdf():
    """Create printable PDF version for San Jacinto Vista II"""
    
    # Import the analysis results
    from ctcac_san_jacinto_custom_mapper import analyze_san_jacinto_with_custom_data
    
    # Project details
    project_name = "San Jacinto Vista II"
    project_address = "202 E. Jarvis St., Perris, CA"
    
    # Parcel corner coordinates
    parcel_corners = {
        'nw': (33.79377, -117.22184),
        'ne': (33.79376, -117.22050),
        'sw': (33.79213, -117.22173),
        'se': (33.79211, -117.22048)
    }
    
    print("Generating CTCAC analysis data...")
    map_obj, results = analyze_san_jacinto_with_custom_data(
        parcel_corners=parcel_corners,
        address=project_address,
        is_rural=False,
        project_type='at_risk',
        qualifying_development=True,
        new_construction=False,
        large_family=True,
        site_name=project_name
    )
    
    print("Creating printable map...")
    printable_map = create_printable_map(
        parcel_corners=parcel_corners,
        project_name=project_name,
        project_address=project_address,
        amenities_data=results,
        site_name=project_name
    )
    
    # Export to HTML for PDF printing
    output_file = 'san_jacinto_vista_ii_printable.html'
    export_path = export_to_pdf(printable_map, output_file, open_browser=True)
    
    return export_path


if __name__ == "__main__":
    create_san_jacinto_printable_pdf()
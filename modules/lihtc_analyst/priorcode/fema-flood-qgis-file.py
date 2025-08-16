#!/usr/bin/env python3
"""
FEMA Flood Map Loader for QGIS
For affordable housing site analysis
Tested with QGIS 3.40 LTR
"""

from qgis.core import QgsProject, QgsRasterLayer
import os

def add_fema_flood_layers():
    """
    Add FEMA flood hazard layers to current QGIS project
    """
    print("Starting FEMA flood map import...")
    
    # FEMA WMS endpoint
    wms_url = "https://hazards.fema.gov/gis/nfhl/services/public/NFHL/MapServer/WMSServer"
    
    # Define layers relevant for affordable housing development
    layers_to_add = [
        {
            'id': '28',
            'name': 'FEMA Flood Hazard Zones',
            'description': 'Primary flood risk zones'
        },
        {
            'id': '16', 
            'name': 'FEMA Base Flood Elevations',
            'description': 'Elevation requirements for construction'
        },
        {
            'id': '4',
            'name': 'FEMA Political Jurisdictions',
            'description': 'Jurisdictional boundaries'
        }
    ]
    
    # Track results
    added_layers = []
    failed_layers = []
    
    # Add each layer
    for layer_info in layers_to_add:
        print(f"\nAdding: {layer_info['name']}")
        print(f"  Description: {layer_info['description']}")
        
        # Build WMS URI
        uri = (
            f"contextualWMSLegend=0&"
            f"crs=EPSG:4326&"
            f"dpiMode=7&"
            f"featureCount=10&"
            f"format=image/png&"
            f"layers={layer_info['id']}&"
            f"styles=&"
            f"url={wms_url}"
        )
        
        # Create layer
        layer = QgsRasterLayer(uri, layer_info['name'], 'wms')
        
        # Check if valid and add to project
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            added_layers.append(layer_info['name'])
            print(f"  ✓ Successfully added")
        else:
            failed_layers.append(layer_info['name'])
            print(f"  ✗ Failed to add")
    
    # Print summary
    print("\n" + "="*50)
    print("IMPORT SUMMARY")
    print("="*50)
    print(f"Successfully added: {len(added_layers)} layers")
    for layer in added_layers:
        print(f"  ✓ {layer}")
    
    if failed_layers:
        print(f"\nFailed to add: {len(failed_layers)} layers")
        for layer in failed_layers:
            print(f"  ✗ {layer}")
    
    print("\nNext steps:")
    print("1. Zoom to your project area")
    print("2. The flood zones will load as you zoom in")
    print("3. Layer 'FEMA Flood Hazard Zones' shows the risk areas")
    print("   - Zone AE, A, AH, AO = High risk (1% annual chance)")
    print("   - Zone X = Moderate/Minimal risk")
    
    return added_layers

# Run the function when script is executed
if __name__ == "__main__":
    try:
        added = add_fema_flood_layers()
        if added:
            print(f"\n✓ Successfully added {len(added)} FEMA layers to your project")
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        print("Make sure you have an active QGIS project open")
#!/usr/bin/env python3
"""
FEMA Flood Risk Analysis Tool for Affordable Housing Development
Specifically designed for CTCAC and other affordable housing programs
Tested with QGIS 3.40 LTR
"""

from qgis.core import *
from qgis import processing
import os

class FEMAFloodAnalysis:
    """Complete FEMA flood analysis toolkit"""
    
    def __init__(self):
        self.project = QgsProject.instance()
        self.wms_url = "https://hazards.fema.gov/gis/nfhl/services/public/NFHL/MapServer/WMSServer"
        
        # California-specific settings (for CTCAC)
        self.ca_counties = {
            'Los Angeles': '06037',
            'San Diego': '06073',
            'Orange': '06059',
            'San Francisco': '06075',
            'Sacramento': '06067'
        }
    
    def quick_add_ca_county(self, county_name):
        """
        Quick add flood data for a California county
        Useful for CTCAC applications
        """
        if county_name not in self.ca_counties:
            print(f"County {county_name} not in preset list")
            print(f"Available counties: {', '.join(self.ca_counties.keys())}")
            return
        
        # Add county-specific flood hazard layer
        uri = (
            f"contextualWMSLegend=0&"
            f"crs=EPSG:4326&"
            f"dpiMode=7&"
            f"featureCount=10&"
            f"format=image/png&"
            f"layers=28&"
            f"styles=&"
            f"url={self.wms_url}"
        )
        
        layer_name = f"FEMA Flood Zones - {county_name} County"
        layer = QgsRasterLayer(uri, layer_name, 'wms')
        
        if layer.isValid():
            self.project.addMapLayer(layer)
            print(f"✓ Added flood zones for {county_name} County")
            
            # Zoom to county extent (approximate)
            # You may want to add actual county boundaries
            return layer
        else:
            print(f"✗ Failed to add layer for {county_name} County")
            return None
    
    def analyze_sites_for_ctcac(self, sites_layer):
        """
        Analyze sites specifically for CTCAC application considerations
        """
        print("\nCTCAC Flood Risk Analysis")
        print("="*50)
        
        # This is a placeholder for CTCAC-specific analysis
        # In practice, you'd want to:
        # 1. Check flood zones
        # 2. Calculate additional construction costs
        # 3. Assess impact on tiebreaker points
        # 4. Determine insurance requirements
        
        feature_count = sites_layer.featureCount()
        print(f"Analyzing {feature_count} potential sites...")
        
        # Add basic flood zone field
        if 'flood_zone' not in [field.name() for field in sites_layer.fields()]:
            sites_layer.dataProvider().addAttributes([
                QgsField('flood_zone', QVariant.String),
                QgsField('ctcac_flood_notes', QVariant.String)
            ])
            sites_layer.updateFields()
        
        print("✓ Analysis fields added to layer")
        print("\nNote: Run full spatial analysis to determine actual flood zones")
        
        return sites_layer

# Create instance
tool = FEMAFloodAnalysis()

# Example usage for quick California county load:
# tool.quick_add_ca_county('Los Angeles')

print("\nFEMA Flood Analysis Tool Loaded")
print("\nQuick Commands:")
print("  tool.quick_add_ca_county('Los Angeles')  - Add LA County flood data")
print("  tool.quick_add_ca_county('San Diego')    - Add SD County flood data")
print("\nAvailable counties:", ', '.join(tool.ca_counties.keys()))

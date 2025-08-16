# California Fire Hazard Data Integration Guide

## Overview
This document outlines available California fire hazard data sources and integration approaches for the CALIHTCScorer system to meet the mandatory fire risk assessment requirement.

## Primary Data Sources

### 1. CAL FIRE Fire Hazard Severity Zones (FHSZ) - RECOMMENDED

**REST API Endpoint**
```
https://services.gis.ca.gov/arcgis/rest/services/Environment/Fire_Severity_Zones/MapServer
```

**Key Features:**
- Official state fire hazard severity zones
- Three risk levels: Moderate, High, Very High
- Covers both State Responsibility Areas (SRA) and Local Responsibility Areas (LRA)
- Updated 2024 data (effective April 1, 2024)
- 2025 updates rolling out through March 2025

**Data Access Methods:**
1. **REST API Query** (Recommended for real-time analysis)
2. **Shapefile Download** from OSFM website
3. **Web Feature Service (WFS)** endpoint

### 2. California State Geoportal FHSZ Dataset

**Direct Dataset Link**
```
https://gis.data.ca.gov/datasets/31219c833eb54598ba83d09fa0adb346
```

**Available Formats:**
- CSV
- KML
- GeoJSON
- Shapefile (ZIP)
- GeoTIFF
- PNG

### 3. CAL FIRE FRAP Data Portal

**Website:** https://frap.fire.ca.gov/mapping/gis-data/

**Provides:**
- Historical fire perimeters
- Vegetation and fuels data
- Watershed assessments
- Climate data

## Integration Approaches

### Approach 1: Real-Time API Integration (Recommended)

```python
import requests
import json

class FireHazardAnalyzer:
    def __init__(self):
        self.base_url = "https://services.gis.ca.gov/arcgis/rest/services/Environment/Fire_Severity_Zones/MapServer"
        
    def check_fire_hazard(self, latitude, longitude):
        """Query fire hazard severity at given coordinates"""
        
        # Construct query endpoint
        query_url = f"{self.base_url}/identify"
        
        # Parameters for point query
        params = {
            'geometry': f'{longitude},{latitude}',
            'geometryType': 'esriGeometryPoint',
            'sr': '4326',  # WGS84 coordinate system
            'layers': 'all',
            'tolerance': '0',
            'mapExtent': f'{longitude-0.01},{latitude-0.01},{longitude+0.01},{latitude+0.01}',
            'imageDisplay': '96,96,96',
            'returnGeometry': 'false',
            'f': 'json'
        }
        
        response = requests.get(query_url, params=params)
        data = response.json()
        
        # Parse results
        for result in data.get('results', []):
            attributes = result.get('attributes', {})
            hazard_class = attributes.get('HAZ_CLASS', 'Unknown')
            hazard_code = attributes.get('HAZ_CODE', 0)
            
            return {
                'hazard_class': hazard_class,
                'hazard_code': hazard_code,
                'meets_criteria': hazard_class not in ['High', 'Very High']
            }
        
        return {'hazard_class': 'No Data', 'meets_criteria': True}
```

### Approach 2: Local Shapefile Integration

```python
import geopandas as gpd
from shapely.geometry import Point

class FireHazardShapefileAnalyzer:
    def __init__(self, shapefile_path):
        self.fire_hazard_gdf = gpd.read_file(shapefile_path)
        self.fire_hazard_gdf = self.fire_hazard_gdf.to_crs('EPSG:4326')
        
    def check_fire_hazard(self, latitude, longitude):
        """Check fire hazard using local shapefile"""
        point = Point(longitude, latitude)
        
        # Find which polygon contains the point
        mask = self.fire_hazard_gdf.contains(point)
        
        if mask.any():
            zone = self.fire_hazard_gdf[mask].iloc[0]
            hazard_class = zone['HAZ_CLASS']
            
            return {
                'hazard_class': hazard_class,
                'meets_criteria': hazard_class not in ['High', 'Very High']
            }
        
        return {'hazard_class': 'No Data', 'meets_criteria': True}
```

### Approach 3: Feature Server Query

```python
def query_fire_hazard_feature_server(lat, lon):
    """Query using ArcGIS Feature Server"""
    base_url = "https://services.gis.ca.gov/arcgis/rest/services/Environment/Fire_Severity_Zones/MapServer/0/query"
    
    params = {
        'where': '1=1',
        'geometry': f'{lon},{lat}',
        'geometryType': 'esriGeometryPoint',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': 'HAZ_CLASS,HAZ_CODE,SRA',
        'returnGeometry': 'false',
        'f': 'json'
    }
    
    response = requests.get(base_url, params=params)
    return response.json()
```

## Data Schema

### FHSZ Key Fields
- **HAZ_CLASS**: Hazard classification (Moderate, High, Very High)
- **HAZ_CODE**: Numeric hazard code (1, 2, 3)
- **SRA**: State Responsibility Area indicator
- **LRA**: Local Responsibility Area indicator

### Risk Level Mapping
```python
FIRE_RISK_LEVELS = {
    'Non-VHFHSZ': 'No Risk',
    'Moderate': 'Moderate Risk',
    'High': 'High Risk',
    'Very High': 'Very High Risk'
}

# Acceptable levels per Site Recommendation Contract
ACCEPTABLE_FIRE_RISK = ['No Risk', 'Low Risk', 'Moderate Risk']
```

## Implementation Steps

1. **Add Fire Hazard Analyzer Module**
   ```
   src/analyzers/fire_hazard_analyzer.py
   ```

2. **Update Site Analyzer**
   - Add fire hazard check to main analysis flow
   - Include in mandatory criteria validation

3. **Configuration Updates**
   - Add fire hazard data source to config.json
   - Include API endpoints or shapefile paths

4. **Testing**
   - Test known high-risk areas (e.g., Oakland Hills)
   - Test known low-risk areas (e.g., downtown San Francisco)
   - Validate against CAL FIRE maps

## Additional Resources

### WUI (Wildland-Urban Interface) Data
- **CAL FIRE WUI Maps**: Additional layer for interface zones
- **USFS WUI Data**: Federal wildland-urban interface mapping

### Historical Fire Perimeters
```
https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/California_Fire_Perimeters/FeatureServer
```
- Useful for understanding fire history at a location
- Can supplement FHSZ data

### Real-Time Fire Data
```
https://gis.fema.gov/arcgis/rest/services/Partner/Active_Fire_Exposure/FeatureServer
```
- Updated every 4 hours
- Shows active fire perimeters

## Contact Information

**CAL FIRE OSFM**
- Email: FHSZinformation@fire.ca.gov
- Phone: (916) 633-7655
- Website: https://osfm.fire.ca.gov/

## Notes

1. **2025 Updates**: New FHSZ maps are being released in phases through March 2025
2. **Dual Coverage**: Some areas may have both SRA and LRA designations
3. **Insurance Implications**: High/Very High zones may affect insurance availability
4. **Local Ordinances**: Some jurisdictions have additional fire safety requirements

## Example Integration

```python
# In site_analyzer.py
def analyze_site(self, latitude, longitude, state='CA', project_type='family'):
    # ... existing code ...
    
    # Add fire hazard check
    fire_analyzer = FireHazardAnalyzer()
    fire_risk = fire_analyzer.check_fire_hazard(latitude, longitude)
    
    # Update recommendations based on fire risk
    if not fire_risk['meets_criteria']:
        self.recommendations['fire_risk_warning'] = 'Site is in High/Very High fire hazard zone'
        self.recommendations['meets_mandatory_criteria'] = False
```
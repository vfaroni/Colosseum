# OVERNIGHT BUILD: Texas Regional Parcel Data Acquisition

**Target**: Open LLM implementation (local/free) - TRUCK not Ferrari  
**Timeline**: 6-8 hours overnight development  
**Purpose**: Bulk download and standardize Texas regional parcel data

---

## SIMPLE ARCHITECTURE: 4 SCRIPTS APPROACH

### Script 1: `download_dfw_parcels.py`
**Purpose**: Download Dallas-Fort Worth NCTCOG 16-county dataset  
**Source**: https://data-nctcoggis.opendata.arcgis.com/  
**Output**: `data/dfw_parcels.geojson`

```python
# Pseudocode - Open LLM should implement:
import requests, geopandas
# 1. Find NCTCOG parcel data download URL
# 2. Download shapefile/geodatabase 
# 3. Convert to standardized GeoJSON
# 4. Save with consistent schema: [parcel_id, geometry, county, acres]
```

### Script 2: `download_san_antonio_parcels.py`  
**Purpose**: Download Bexar County parcel data
**Source**: https://www.bcad.org/ or https://gis-bcad.opendata.arcgis.com/
**Output**: `data/san_antonio_parcels.geojson`

### Script 3: `download_austin_parcels.py`
**Purpose**: Download Travis County parcel data  
**Source**: https://data.austintexas.gov/ or Travis CAD
**Output**: `data/austin_parcels.geojson`

### Script 4: `download_houston_parcels.py`
**Purpose**: Download Harris County parcel data
**Source**: https://hcad.org/ or Harris County GIS
**Output**: `data/houston_parcels.geojson`

---

## STANDARDIZED OUTPUT SCHEMA

Each script should produce GeoJSON with this exact schema:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature", 
      "properties": {
        "parcel_id": "unique_identifier",
        "county": "county_name",
        "area_acres": 0.0,
        "data_source": "source_name",
        "download_date": "2025-08-03"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lng, lat], [lng, lat], ...]]
      }
    }
  ]
}
```

---

## INTEGRATION SCRIPT: `bulk_parcel_loader.py`

**Purpose**: Load regional data into existing parcel mapper  
**Requirements**: 
- Read GeoJSON files from `data/` directory
- Create spatial index for fast lookups
- Integrate with existing `universal_parcel_mapper.py`

```python
# Pseudocode for integration:
class RegionalParcelLoader:
    def __init__(self):
        self.dfw_data = load_geojson('data/dfw_parcels.geojson')
        self.san_antonio_data = load_geojson('data/san_antonio_parcels.geojson') 
        self.austin_data = load_geojson('data/austin_parcels.geojson')
        self.houston_data = load_geojson('data/houston_parcels.geojson')
        
    def get_parcel_by_coordinates(self, lat, lng):
        # Check which region the coordinates fall in
        # Return parcel data from appropriate dataset
        # Use spatial index for fast lookup
```

---

## SUCCESS CRITERIA (OVERNIGHT)

### Minimum Viable Product:
1. **4 working download scripts** - each metro downloads successfully
2. **Standardized GeoJSON output** - consistent schema across all regions  
3. **Basic integration** - can lookup parcels by lat/lng coordinates
4. **Documentation** - simple README explaining how to run each script

### Stretch Goals:
- **Error handling** for failed downloads
- **Data validation** routines 
- **Coordinate transformation** (if needed)
- **File size optimization** (remove unnecessary attributes)

---

## OPEN LLM PROMPT TEMPLATE

```
You are tasked with building a simple, robust parcel data acquisition system for Texas regions. 

GOAL: Create 4 Python scripts that download parcel boundary data for:
1. Dallas-Fort Worth (NCTCOG 16 counties)
2. San Antonio (Bexar County)  
3. Austin (Travis County)
4. Houston (Harris County)

REQUIREMENTS:
- Use only standard Python libraries (requests, json, etc.) and geopandas
- Output standardized GeoJSON files with schema: parcel_id, county, area_acres, geometry
- Handle download failures gracefully
- Include simple usage instructions
- Focus on functionality over optimization

APPROACH:
- Research each county/region's open data portal
- Find parcel/property boundary datasets
- Download as shapefile or GeoJSON
- Standardize the output format
- Create simple integration with coordinate-based lookup

This is a "truck not Ferrari" - prioritize working code over elegant architecture.
```

---

## FILE STRUCTURE FOR OVERNIGHT BUILD

```
modules/data_intelligence/parcel_mapping/
├── regional_data/
│   ├── download_dfw_parcels.py
│   ├── download_san_antonio_parcels.py  
│   ├── download_austin_parcels.py
│   ├── download_houston_parcels.py
│   ├── bulk_parcel_loader.py
│   └── README.md
├── data/
│   ├── dfw_parcels.geojson
│   ├── san_antonio_parcels.geojson
│   ├── austin_parcels.geojson
│   └── houston_parcels.geojson
└── test_regional_lookup.py
```

---

## VALIDATION TEST

Create simple test that:
1. Loads all 4 regional datasets
2. Tests coordinate lookup for known addresses in each metro
3. Verifies boundary extraction works
4. Compares results to current API-based approach

**Test coordinates**:
- **DFW**: 32.7767, -96.7970 (Downtown Dallas)
- **San Antonio**: 29.4241, -98.4936 (Downtown SA) 
- **Austin**: 30.2672, -97.7431 (Downtown Austin)
- **Houston**: 29.7604, -95.3698 (Downtown Houston)

---

This overnight build gives you the foundation for batch processing 155 sites without API dependencies, using free regional data sources identified in the Opus research. Simple, robust, and ready for morning testing.
# CTCAC Amenity Mapper System

## Overview
Comprehensive system for analyzing CTCAC site amenity scoring for LIHTC 9% competitive tax credit applications. Maps amenities around development sites and calculates CTCAC points based on QAP 2025 radius distance requirements.

## Features

### ✅ **Implemented Amenities**
- **Public Schools**: Elementary, Middle, High School proximity scoring
- **Public Libraries**: Library proximity scoring with rural adjustments
- **Pharmacies**: Pharmacy proximity scoring with rural adjustments
- **Adult Education**: Basic framework (requires separate community college data)

### 🚧 **Partially Implemented**
- **Medical Facilities**: Data loaded but requires geocoding
- **Public Parks**: Framework exists, needs park data
- **Public Transit**: Framework exists, needs transit data
- **Grocery Stores**: Framework exists, needs grocery data

### 📍 **Distance Measurement**
- **Method**: Straight-line radius distance (per CTCAC regulations)
- **Accuracy**: Haversine formula for precise distance calculations
- **Compliance**: All measurements follow CTCAC QAP 2025 specifications

## Installation

### Required Dependencies
```bash
pip3 install -r amenity_mapper_requirements.txt
```

### Data Dependencies
- CA_Public Schools dataset (included)
- CA_Libraries dataset (from OpenStreetMap)
- CA_Pharmacies dataset (from OpenStreetMap)

## Usage

### 1. Python API

```python
from ctcac_amenity_mapper import CTCACAmenityMapper, analyze_site_by_address, analyze_site_by_coordinates

# Analyze by address
map_obj, results = analyze_site_by_address(
    "123 Main St, Sacramento, CA",
    is_rural=False,
    project_type='family'
)

# Analyze by coordinates
map_obj, results = analyze_site_by_coordinates(
    38.7584, -121.2942,
    site_name="My Development",
    is_rural=False,
    project_type='family'
)

# Save interactive map
map_obj.save("amenity_analysis.html")

# Access scoring results
print(f"Total CTCAC Points: {results['total_points']}")
```

### 2. Command Line Interface

```bash
# Analyze by address
python3 quick_amenity_analysis.py "123 Main St, Sacramento, CA"

# Analyze by coordinates
python3 quick_amenity_analysis.py 38.7584 -121.2942

# With project type and rural options
python3 quick_amenity_analysis.py 38.7584 -121.2942 --rural --senior
```

### 3. Project Types
- **family**: Family housing (default) - includes school scoring
- **senior**: Senior housing - different amenity requirements
- **special_needs**: Special needs housing - specialized scoring

### 4. Rural Classification
- **Standard**: Uses standard CTCAC distance requirements
- **Rural**: Uses extended distances per CTCAC rural set-aside rules

## CTCAC Scoring Implementation

### Distance Requirements (Miles)

#### **Public Schools** (Family Projects Only)
| School Type | Standard Distance | Rural Distance | Points |
|-------------|------------------|----------------|---------|
| Elementary | 0.25, 0.75 | 0.75, 1.25 | 3, 2 |
| Middle | 0.5, 1.0 | 1.0, 1.5 | 3, 2 |
| High | 1.0, 1.5 | 1.5, 2.0 | 3, 2 |

#### **Public Libraries**
| Standard Distance | Rural Distance | Points |
|------------------|----------------|---------|
| 0.5, 1.0 | 1.0, 2.0 | 3, 2 |

#### **Pharmacies**
| Standard Distance | Rural Distance | Points |
|------------------|----------------|---------|
| 0.5, 1.0 | 1.0, 2.0 | 2, 1 |

#### **Adult Education/Community Colleges**
| Standard Distance | Rural Distance | Points |
|------------------|----------------|---------|
| 1.0 | 1.5 | 3 |

## Output Formats

### 1. Interactive Map
- **Folium-based** HTML map with markers and scoring circles
- **Development Site**: Red home icon marker
- **Amenity Markers**: Color-coded by category
- **Scoring Circles**: Dashed circles showing CTCAC distance requirements
- **Legend**: Displays total points and scoring breakdown

### 2. Scoring Results Dictionary
```python
{
    'site_coordinates': (lat, lng),
    'is_rural': bool,
    'project_type': str,
    'total_points': int,
    'scoring_summary': {
        'schools': {'elementary': pts, 'middle': pts, 'high': pts},
        'libraries': {'points': pts, 'closest_distance': miles},
        'pharmacies': {'points': pts, 'closest_distance': miles}
    },
    'amenities_found': {
        'schools': [list of nearby schools with distances],
        'libraries': [list of nearby libraries with distances],
        'pharmacies': [list of nearby pharmacies with distances]
    }
}
```

### 3. Command Line Summary
- Total CTCAC points
- Detailed scoring by category
- List of closest amenities with distances
- Interactive map file path

## Technical Architecture

### Core Classes
- **CTCACAmenityMapper**: Main analysis engine
- Data loading methods for each amenity type
- Distance calculation using Haversine formula
- CTCAC scoring logic implementation

### Data Processing
- **Schools**: CSV processing with filtering for active, eligible schools
- **Libraries/Pharmacies**: GeoJSON processing with centroid calculation
- **Geocoding**: Census Geocoding API for address conversion

### Mapping Engine
- **Folium**: Interactive web maps with markers and circles
- **Scoring Visualization**: Color-coded circles for different distance thresholds
- **Legend**: Dynamic HTML legend with scoring breakdown

## Expansion Roadmap

### High Priority Missing Amenities
1. **Grocery Stores**: Requires commercial database or OSM data
2. **Public Parks**: Requires park boundary data
3. **Public Transit**: Requires GTFS or transit agency data
4. **Medical Facilities**: Requires geocoding of HCAI data

### Data Sources for Expansion
- **Grocery**: USDA Food Access Research Atlas, commercial databases
- **Parks**: National Recreation and Park Association, local GIS
- **Transit**: California transit agencies, GTFS feeds
- **Medical**: Geocode existing HCAI CSV data

### Advanced Features
- **Parcel-based Analysis**: Use assessor parcel data for precise boundaries
- **Barrier Detection**: Implement physical barrier analysis (highways, rivers)
- **Batch Processing**: Analyze multiple sites simultaneously
- **Report Generation**: Automated PDF reports for loan applications

## Integration with LIHTC Workflow

### Current Integration Points
- **Site Selection**: Evaluate multiple potential sites
- **Due Diligence**: Confirm amenity scoring assumptions
- **Application Preparation**: Generate maps and scoring documentation
- **Underwriting**: Validate site amenity claims

### CLAUDE.md Integration
This system integrates with the broader LIHTC analysis framework documented in the project's CLAUDE.md file. Use in conjunction with:
- QCT/DDA analysis tools
- Competition analysis systems
- Financial feasibility modeling

## Limitations and Disclaimers

### Current Limitations
1. **Incomplete Amenity Coverage**: Missing grocery, parks, transit, medical
2. **Point Geometry**: Uses centroids for non-point features
3. **No Barrier Analysis**: Doesn't account for physical barriers
4. **Data Currency**: OSM data may not be completely current

### CTCAC Compliance Notes
- **Distance Method**: Implements radius distance per regulations
- **Measurement Points**: Uses nearest corners as specified
- **Rural Adjustments**: Correctly applies extended distances
- **Project Type Requirements**: Enforces family housing school requirements

### Recommendations
- **Verify Results**: Always cross-check critical amenities manually
- **Update Data**: Refresh OSM data periodically
- **Professional Review**: Have qualified professionals validate scoring
- **Application Use**: Treat as analysis tool, not definitive scoring

## Maintenance

### Data Updates
- **Schools**: Annual updates from CDE (fall release)
- **OSM Data**: Periodic re-downloads (quarterly recommended)
- **Regulations**: Monitor CTCAC QAP updates for scoring changes

### Code Maintenance
- **Dependencies**: Keep pandas, geopandas, folium updated
- **Testing**: Test with known sites before important analyses
- **Backup**: Maintain copies of working data versions

---

**Version**: 1.0  
**Last Updated**: June 30, 2025  
**Maintained By**: LIHTC Analysis Team  
**Status**: Production Ready (with noted limitations)
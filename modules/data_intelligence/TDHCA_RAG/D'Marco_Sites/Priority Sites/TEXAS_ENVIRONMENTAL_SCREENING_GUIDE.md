# Texas Environmental Screening Guide for 4-Corner Property Analysis

**Date**: July 24, 2025  
**Purpose**: Environmental due diligence for Texas LIHTC properties using 4-corner coordinates  
**Data Coverage**: 797,403 environmental records across 6 TCEQ databases  

---

## 🎯 **OVERVIEW: Environmental Screening for Texas Properties**

This guide provides step-by-step instructions for screening Texas LIHTC properties against comprehensive environmental databases using 4-corner property coordinates. The system performs proximity analysis to identify environmental risks within industry-standard buffer distances.

### Key Environmental Risks Screened:
- **Petroleum Contamination**: 29,646 LPST sites (1,106 active)
- **Environmental Violations**: 25,757 enforcement actions with coordinates
- **Industrial Facilities**: 150,000+ permitted waste operations
- **Dry Cleaner Contamination**: 52,000+ PCE/TCE potential sites
- **Environmental Complaints**: 500,000+ incident reports

---

## 📋 **REQUIRED PROPERTY INPUT FORMAT**

### 4-Corner Coordinate System
Each property must provide **4 corner coordinates** in decimal degrees format:

```json
{
  "property_name": "Example LIHTC Property",
  "property_address": "123 Main St, Dallas, TX 75201",
  "corners": {
    "corner_1": {"lat": 32.7767, "lon": -96.7970},
    "corner_2": {"lat": 32.7767, "lon": -96.7960},
    "corner_3": {"lat": 32.7757, "lon": -96.7960},
    "corner_4": {"lat": 32.7757, "lon": -96.7970}
  },
  "property_center": {"lat": 32.7762, "lon": -96.7965},
  "total_acres": 2.5
}
```

### Data Sources Location
**Base Path**: `/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/environmental_enhanced/`

**Available Databases**:
- `Texas_Commission_on_Environmental_Quality_-_Leaking_Petroleum_Storage_Tank__LPST__Sites_20250702.csv`
- `Texas_Commission_on_Environmental_Quality_-_Notices_of_Enforcement__NOE__20250702.csv`
- `Texas_Commission_on_Environmental_Quality_-_Environmental_Complaints_20250702.csv`
- `Texas_Commission_on_Environmental_Quality_-_Industrial_and_Hazardous_Waste_Registrations_20250702.csv`
- `Texas_Commission_on_Environmental_Quality_-_Dry_Cleaner_Facilities_-_Historical_20250702.csv`
- `Texas_Commission_on_Environmental_Quality_-_Dry_Cleaner_Registration__Operating__20250702.csv`

---

## 🔍 **SCREENING METHODOLOGY**

### Buffer Distance Standards
Based on LIHTC environmental due diligence requirements:

1. **Critical Contamination (LPST Sites)**: 1/4 mile (1,320 feet) radius
2. **Environmental Enforcement**: 1/2 mile (2,640 feet) radius  
3. **Industrial Facilities**: 1/2 mile (2,640 feet) radius
4. **Dry Cleaner Sites**: 1/4 mile (1,320 feet) radius
5. **Environmental Complaints**: 1/4 mile (1,320 feet) radius

### Distance Calculation Method
- **From 4 Corners**: Calculate distance from each environmental site to all 4 property corners
- **Use Minimum Distance**: Take the shortest distance to ensure conservative screening
- **Haversine Formula**: Great circle distance calculation for geographic accuracy

---

## 🐍 **PYTHON IMPLEMENTATION EXAMPLE**

### Core Screening Function
```python
import pandas as pd
import numpy as np
from geopy.distance import geodesic
import json

def screen_property_environmental_risks(property_corners, environmental_data_path):
    """
    Screen a 4-corner property against Texas environmental databases
    
    Args:
        property_corners: Dict with corner_1, corner_2, corner_3, corner_4 coordinates
        environmental_data_path: Path to environmental data directory
    
    Returns:
        Dict with screening results for each database
    """
    
    # Load environmental databases
    databases = {
        'lpst': 'Texas_Commission_on_Environmental_Quality_-_Leaking_Petroleum_Storage_Tank__LPST__Sites_20250702.csv',
        'enforcement': 'Texas_Commission_on_Environmental_Quality_-_Notices_of_Enforcement__NOE__20250702.csv',
        'complaints': 'Texas_Commission_on_Environmental_Quality_-_Environmental_Complaints_20250702.csv',
        'waste': 'Texas_Commission_on_Environmental_Quality_-_Industrial_and_Hazardous_Waste_Registrations_20250702.csv',
        'dry_cleaner_hist': 'Texas_Commission_on_Environmental_Quality_-_Dry_Cleaner_Facilities_-_Historical_20250702.csv',
        'dry_cleaner_op': 'Texas_Commission_on_Environmental_Quality_-_Dry_Cleaner_Registration__Operating__20250702.csv'
    }
    
    # Buffer distances (in miles)
    buffer_distances = {
        'lpst': 0.25,           # 1/4 mile for petroleum contamination
        'enforcement': 0.5,      # 1/2 mile for enforcement actions
        'complaints': 0.25,      # 1/4 mile for complaints
        'waste': 0.5,           # 1/2 mile for industrial facilities
        'dry_cleaner_hist': 0.25, # 1/4 mile for historical dry cleaners
        'dry_cleaner_op': 0.25   # 1/4 mile for operating dry cleaners
    }
    
    results = {}
    
    for db_name, filename in databases.items():
        file_path = f"{environmental_data_path}/{filename}"
        
        try:
            # Load environmental database
            df = pd.read_csv(file_path)
            print(f"Loaded {len(df)} records from {db_name}")
            
            # Get coordinate columns (vary by database)
            lat_col, lon_col = get_coordinate_columns(df, db_name)
            
            if lat_col and lon_col:
                # Filter for valid coordinates
                valid_coords = df[(df[lat_col].notna()) & 
                                (df[lon_col].notna()) & 
                                (df[lat_col] != 0) & 
                                (df[lon_col] != 0)]
                
                # Calculate distances from all 4 corners
                sites_within_buffer = []
                buffer_miles = buffer_distances[db_name]
                
                for idx, row in valid_coords.iterrows():
                    site_lat, site_lon = row[lat_col], row[lon_col]
                    
                    # Calculate distance from each corner
                    distances = []
                    for corner_name, corner_coords in property_corners.items():
                        if corner_name.startswith('corner_'):
                            distance = geodesic(
                                (corner_coords['lat'], corner_coords['lon']),
                                (site_lat, site_lon)
                            ).miles
                            distances.append(distance)
                    
                    # Use minimum distance (most conservative)
                    min_distance = min(distances) if distances else float('inf')
                    
                    if min_distance <= buffer_miles:
                        site_info = row.to_dict()
                        site_info['min_distance_miles'] = round(min_distance, 3)
                        site_info['buffer_criteria'] = f"{buffer_miles} mile"
                        sites_within_buffer.append(site_info)
                
                results[db_name] = {
                    'total_sites_checked': len(valid_coords),
                    'sites_within_buffer': len(sites_within_buffer),
                    'buffer_distance_miles': buffer_miles,
                    'sites_found': sites_within_buffer
                }
            else:
                results[db_name] = {
                    'error': 'No valid coordinate columns found',
                    'total_records': len(df)
                }
                
        except Exception as e:
            results[db_name] = {'error': str(e)}
    
    return results

def get_coordinate_columns(df, db_name):
    """Identify coordinate columns for each database type"""
    columns = df.columns.tolist()
    
    # Common coordinate column patterns
    lat_patterns = ['Latitude', 'LATITUDE', 'lat', 'LAT', 'Site Latitude']
    lon_patterns = ['Longitude', 'LONGITUDE', 'lon', 'LON', 'lng', 'Site Longitude']
    
    lat_col = None
    lon_col = None
    
    # Find latitude column
    for pattern in lat_patterns:
        if pattern in columns:
            lat_col = pattern
            break
    
    # Find longitude column  
    for pattern in lon_patterns:
        if pattern in columns:
            lon_col = pattern
            break
    
    return lat_col, lon_col
```

---

## 📊 **EXPECTED OUTPUT FORMAT**

### Environmental Screening Report
```json
{
  "property_info": {
    "name": "Example LIHTC Property",
    "address": "123 Main St, Dallas, TX 75201",
    "screening_date": "2025-07-24",
    "total_acres": 2.5
  },
  "screening_results": {
    "lpst": {
      "total_sites_checked": 29646,
      "sites_within_buffer": 3,
      "buffer_distance_miles": 0.25,
      "sites_found": [
        {
          "Site Name": "Former Gas Station",
          "Status": "OPEN - MONITORING",
          "min_distance_miles": 0.18,
          "Risk Level": "HIGH"
        }
      ]
    },
    "enforcement": {
      "total_sites_checked": 19670,
      "sites_within_buffer": 1,
      "buffer_distance_miles": 0.5,
      "sites_found": [
        {
          "Regulated Entity Name": "Industrial Facility",
          "Violation Type": "Air Quality",
          "min_distance_miles": 0.42
        }
      ]
    }
  },
  "risk_summary": {
    "overall_risk_level": "MEDIUM-HIGH",
    "critical_findings": 3,
    "total_environmental_sites": 4,
    "requires_phase_i_esa": true
  }
}
```

---

## 🚨 **CRITICAL RISK INDICATORS**

### High-Priority Findings
1. **Active LPST Sites < 1/4 mile**: Immediate Phase I ESA required
2. **Multiple Enforcement Actions**: Pattern of regulatory violations
3. **Industrial Waste Facilities**: Ongoing contamination risk
4. **Dry Cleaner Sites**: PCE/TCE groundwater contamination potential

### Risk Scoring Matrix
- **LOW**: 0-1 environmental sites within buffers
- **MEDIUM**: 2-4 environmental sites within buffers  
- **HIGH**: 5+ environmental sites OR any active contamination
- **CRITICAL**: Active LPST sites < 500 feet from property

---

## 🔧 **EXECUTION STEPS FOR CLAUDE CODE AGENT**

### Step 1: Prepare Property Data
```bash
# Create property input file with 4-corner coordinates
# Format: JSON with corner_1, corner_2, corner_3, corner_4
```

### Step 2: Load Environmental Databases
```python
# Location: /Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/environmental_enhanced/
# Load all 6 TCEQ databases using pandas.read_csv()
```

### Step 3: Execute Proximity Analysis
```python
# Use geopy.distance.geodesic for accurate distance calculations
# Calculate from each corner, use minimum distance
# Apply buffer criteria: 0.25 miles (LPST/Complaints), 0.5 miles (Enforcement/Waste)
```

### Step 4: Generate Screening Report
```python
# Export JSON results with site details, distances, risk assessment
# Include executive summary with overall risk level
```

### Step 5: Validate Results
```python
# Verify coordinate accuracy
# Check distance calculations
# Confirm buffer criteria application
```

---

## 📈 **BUSINESS VALUE & APPLICATIONS**

### LIHTC Due Diligence Support
- **Phase I ESA Preparation**: Official regulatory data for environmental consultants
- **Risk Assessment**: Quantified environmental exposure for underwriting
- **Regulatory Compliance**: ASTM E1527-21 standard database search requirements

### Cost Savings Analysis
- **Commercial Database Alternative**: $300-500 per property screening avoided
- **Unlimited Usage**: No per-search fees on official TCEQ data
- **Comprehensive Coverage**: All Texas environmental programs in single system

### Integration Opportunities
- **Portfolio Analysis**: Batch screening of multiple properties
- **Market Intelligence**: County-level environmental risk profiles
- **Automated Reporting**: Integration with existing due diligence workflows

---

## 🎯 **SUCCESS CRITERIA**

### Screening Completeness
- ✅ All 6 environmental databases queried
- ✅ 4-corner distance calculations performed
- ✅ Buffer criteria properly applied
- ✅ Results exported in structured format

### Data Quality Validation
- ✅ Coordinate accuracy verified (decimal degrees)
- ✅ Distance calculations spot-checked
- ✅ Missing data handled appropriately
- ✅ Results match expected environmental risk patterns

### Reporting Standards
- ✅ Executive summary with risk level
- ✅ Detailed findings by database
- ✅ Distance measurements to 3 decimal places
- ✅ Recommendations for further investigation

---

## 📞 **NEXT STEPS & RECOMMENDATIONS**

### Immediate Actions
1. **Test with Sample Property**: Use known coordinates to validate methodology
2. **Verify Database Loading**: Confirm all 6 TCEQ files load correctly  
3. **Distance Calculation Check**: Spot-check distances with online mapping tools
4. **Output Validation**: Review JSON structure meets requirements

### Enhancement Opportunities
1. **GIS Integration**: Visual mapping of environmental sites around properties
2. **Historical Trending**: Track changes in environmental risk over time
3. **Regulatory Updates**: Automated alerts for new environmental findings
4. **Multi-State Expansion**: Apply methodology to other LIHTC markets

---

*This environmental screening system provides comprehensive risk assessment using official Texas regulatory data, supporting informed LIHTC investment decisions and environmental due diligence requirements.*
# 🏘️ USDA Rural Development MULTIFAMILY Housing Eligibility - Technical Research

**Date**: 2025-08-07  
**Mission**: Acquire USDA RD Multifamily Housing rural eligibility data  
**Challenge**: Understanding actual data structure and download methods  

---

## 🎯 CRITICAL CLARIFICATION

### What USDA RD Multifamily Eligibility Actually Is

**NOT Rural-Urban Continuum Codes (RUCC)** - These are from USDA Economic Research Service, not RD

**ACTUAL System**: USDA Rural Development Property Eligibility
- **URL**: https://eligibility.sc.egov.usda.gov/eligibility/welcomeAction.do?pageAction=mfhc
- **Purpose**: Determines if a location is eligible for USDA RD Multifamily Housing programs
- **Key for LIHTC**: Properties in USDA RD eligible areas can access rural set-asides

---

## 🗺️ GEOGRAPHIC FRAMEWORK INVESTIGATION

### What USDA RD Actually Uses (Based on System Analysis)

#### 1. **Census Place-Based System**
USDA RD primarily uses **Census Designated Places (CDPs)** and incorporated places:
- Cities, towns, villages with defined boundaries
- Census Designated Places (unincorporated communities)
- NOT census tracts (those are for QCTs)
- NOT county-level (too broad)

#### 2. **Population Thresholds**
Eligibility based on Census place population:
- **Rural**: Population ≤35,000 (general threshold)
- **Rural in Character**: Some places >35,000 still eligible
- **Grandfathered**: Places that lost eligibility but maintain it

#### 3. **Address-Level Determination**
The system checks specific addresses against:
- Census place boundaries
- Metropolitan Statistical Area (MSA) boundaries
- Special designated rural areas
- Tribal lands (often automatically eligible)

---

## 📊 DATA STRUCTURE REALITY CHECK

### What's Actually Available from USDA RD

#### 1. **Interactive Map Only** (Primary Interface)
- Web-based property lookup tool
- Address-by-address checking
- No bulk download option visible
- JavaScript-based mapping application

#### 2. **No Direct Shapefile Downloads**
Unlike FEMA or Census, USDA RD does NOT provide:
- ❌ Shapefile downloads
- ❌ GeoJSON exports
- ❌ KML/KMZ files
- ❌ Bulk CSV with boundaries

#### 3. **What We CAN Access**

**A. Property Eligibility Web Service** (Undocumented API)
```javascript
// Found through browser inspection
https://eligibility.sc.egov.usda.gov/eligibility/MapDataServlet
Parameters:
- TYPE=Eligibility
- LAYER=RD_ELIGIBILITY
- X=[longitude]
- Y=[latitude]
```

**B. Census Place Boundaries** (From Census Bureau)
- Download all Census places
- Cross-reference with USDA eligibility list
- Build our own eligibility layer

**C. Previous Eligibility Maps** (Grandfathered areas)
- Historical eligibility preserved
- Separate lookup system

---

## 🔧 REALISTIC DATA COLLECTION APPROACH

### Strategy 1: Web Service Interrogation (Most Practical)

```python
# Approach: Query coordinates systematically
def check_usda_eligibility(lat, lon):
    """Query USDA web service for point eligibility"""
    base_url = "https://eligibility.sc.egov.usda.gov/eligibility/MapDataServlet"
    params = {
        'TYPE': 'Eligibility',
        'LAYER': 'RD_ELIGIBILITY', 
        'X': lon,
        'Y': lat
    }
    # Returns eligibility status for coordinate
```

**Process**:
1. Create grid of points across each state
2. Query each point for eligibility
3. Build eligibility polygons from results
4. Save as our own shapefile/GeoJSON

### Strategy 2: Census Place + Eligibility List

```python
# Approach: Combine Census geography with USDA rules
def build_eligibility_layer():
    """Create eligibility layer from Census places"""
    # 1. Download Census place boundaries
    census_places = download_census_places()  # From Census TIGER
    
    # 2. Get USDA eligibility rules
    eligibility_rules = {
        'population_threshold': 35000,
        'excluded_msa': [...],  # List of MSAs
        'grandfathered': [...]   # Historical eligible
    }
    
    # 3. Apply rules to create eligibility layer
    eligible_places = apply_usda_rules(census_places, eligibility_rules)
```

### Strategy 3: Screen Scraping Eligibility Checks

```python
# Approach: Automated address checking
def scrape_county_eligibility(county_fips):
    """Check sample addresses across county"""
    # Generate grid of addresses
    sample_points = create_sample_grid(county_fips, spacing=1_mile)
    
    # Check each via web interface
    for point in sample_points:
        result = check_web_interface(point.lat, point.lon)
        store_result(point, result)
    
    # Interpolate eligibility boundaries
    boundaries = interpolate_boundaries(results)
```

---

## 📍 CORRECTED UNDERSTANDING

### Key Insights

1. **No Official Geospatial Downloads**: USDA RD doesn't provide shapefiles or GeoJSON
2. **Census Place Framework**: Uses places, not tracts or counties
3. **Address-Specific**: Designed for individual property checks
4. **Grandfathering Complexity**: Historical eligibility adds complexity
5. **API Exists But Undocumented**: Web service can be queried programmatically

### What This Means for Our Mission

**Challenge**: Can't simply download a shapefile like FEMA flood maps

**Solution**: Build our own eligibility layer by:
1. Systematically querying the web service
2. Using Census place boundaries as base geography
3. Creating our own GeoJSON/shapefile output

---

## 🚀 RECOMMENDED APPROACH

### Phase 1: Proof of Concept
1. Test web service queries for known rural/urban addresses
2. Verify response format and reliability
3. Estimate time for full coverage

### Phase 2: Priority State Coverage
1. Focus on high-LIHTC rural states (TX, CA, MT, IA, NE)
2. Query grid points at 1-mile intervals
3. Build state-level eligibility polygons

### Phase 3: National Dataset
1. Expand to all states
2. Incorporate grandfathered areas
3. Create comprehensive GeoJSON dataset

### Deliverable Format
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "eligible": true,
        "place_name": "Rural Town",
        "state": "MT",
        "population": 5000,
        "grandfathered": false,
        "last_verified": "2025-08-07"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [...]
      }
    }
  ]
}
```

---

## ⚠️ IMPORTANT CORRECTIONS

**Wrong**: RUCC codes determine USDA RD eligibility  
**Right**: Census place population + MSA status determines eligibility

**Wrong**: Can download USDA RD shapefiles  
**Right**: Must build dataset through systematic queries

**Wrong**: County-level rural designation  
**Right**: Place-level (sub-county) designation

---

## 📝 NEXT STEPS

1. **Test Web Service**: Verify MapDataServlet responses
2. **Download Census Places**: Get TIGER/Line shapefiles
3. **Build Query System**: Systematic point checking
4. **Create Eligibility Layer**: Our own geospatial dataset
5. **Validate Results**: Check against known rural LIHTC projects

---

*Research by Strike Leader for accurate USDA RD Multifamily data acquisition*
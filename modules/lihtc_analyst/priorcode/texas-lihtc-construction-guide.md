# Texas LIHTC Construction Cost & Flood Risk Integration Guide

## Overview

This guide provides a comprehensive framework for integrating construction cost modifiers with FEMA flood zone risk factors into your Texas LIHTC scoring system. It's designed to be implemented by Claude Code and integrated with your existing CoStar data and HUD AMI/Rent data.

## 1. Construction Cost Base Modifiers by Location

### A. Major Metro Areas

| Metro Area | Base Modifier | Cost/SF | Counties/Cities Included |
|------------|--------------|---------|-------------------------|
| **Austin-Round Rock-Georgetown MSA** | 1.20 | $180 | Travis, Williamson, Hays, Bastrop, Caldwell |
| **Houston-The Woodlands-Sugar Land MSA** | 1.18 | $177 | Harris, Fort Bend, Montgomery, Brazoria, Galveston, Liberty, Waller, Chambers, Austin |
| **Dallas-Plano-Irving MD** | 1.17 | $176 | Dallas, Collin, Denton (partial), Ellis, Hunt, Kaufman, Rockwall |
| **Fort Worth-Arlington-Grapevine MD** | 1.15 | $173 | Tarrant, Johnson, Parker, Hood, Somervell, Wise |
| **San Antonio-New Braunfels MSA** | 1.10 | $165 | Bexar, Guadalupe, Comal, Wilson, Atascosa, Bandera, Kendall, Medina |

### B. Mid-Size Cities

| City/Area | Base Modifier | Cost/SF | Counties Included |
|-----------|--------------|---------|-------------------|
| **El Paso MSA** | 1.05 | $158 | El Paso, Hudspeth |
| **Corpus Christi MSA** | 1.08 | $162 | Nueces, Aransas, San Patricio |
| **McAllen-Edinburg-Mission MSA** | 1.03 | $155 | Hidalgo |
| **Killeen-Temple MSA** | 1.05 | $158 | Bell, Coryell, Lampasas |
| **Beaumont-Port Arthur MSA** | 1.06 | $159 | Jefferson, Orange, Hardin |
| **Lubbock MSA** | 1.04 | $156 | Lubbock, Crosby, Lynn |
| **Amarillo MSA** | 1.04 | $156 | Armstrong, Carson, Potter, Randall |
| **Waco MSA** | 1.05 | $158 | McLennan, Falls |
| **Laredo MSA** | 1.03 | $155 | Webb |
| **College Station-Bryan MSA** | 1.05 | $158 | Brazos, Burleson, Robertson |

### C. Suburban Areas
- **Default Suburban Modifier**: 1.00 (Base $150/sf)
- Applies to counties adjacent to major metros not listed above
- Examples: Denton (partial), Rockwall, Kaufman, Guadalupe

### D. Rural Areas
- **Default Rural Modifier**: 0.95 ($143/sf)
- Applies to all counties not classified as Metro, Mid-Size, or Suburban
- Additional transport cost factor: +0.03 for counties >100 miles from major metro

## 2. FEMA Flood Zone Modifiers

### Flood Zone Construction Cost Impacts

| FEMA Zone | Description | Cost Modifier | Notes |
|-----------|-------------|---------------|-------|
| **VE/V Zones** | Coastal high-velocity wave action | +0.25 to +0.35 | Requires pile/column foundation, breakaway walls |
| **AE/A Zones** | 100-year floodplain with BFE | +0.15 to +0.25 | Elevation requirements, flood venting |
| **AO/AH Zones** | Shallow flooding (1-3 feet) | +0.10 to +0.15 | Minor elevation, flood-resistant materials |
| **X (shaded)** | 500-year floodplain | +0.05 to +0.08 | Recommended elevation, lower insurance |
| **X (unshaded)** | Minimal flood risk | 0.00 | No additional requirements |

### Elevation Cost Factors

Cost to elevate: $10-$18 per square foot of house footprint

Additional costs by elevation height:
- 0-3 feet: Base elevation cost
- 3-6 feet: Base × 1.2
- 6-10 feet: Base × 1.5
- >10 feet: Base × 2.0

## 3. Combined Cost Adjustment Formula

```python
def calculate_adjusted_construction_cost(base_cost, location_modifier, flood_modifier, elevation_feet):
    """
    Calculate total construction cost per square foot with all modifiers
    
    Args:
        base_cost: Base construction cost per SF ($150 default)
        location_modifier: From location tables above
        flood_modifier: From FEMA zone table
        elevation_feet: Required elevation above grade
    
    Returns:
        Adjusted construction cost per square foot
    """
    # Base adjustment
    adjusted_cost = base_cost * location_modifier * (1 + flood_modifier)
    
    # Add elevation costs if needed
    if elevation_feet > 0:
        elevation_cost_psf = calculate_elevation_cost(elevation_feet)
        adjusted_cost += elevation_cost_psf
    
    return adjusted_cost

def calculate_elevation_cost(elevation_feet):
    """Calculate elevation cost per square foot of living area"""
    base_elevation_cost = 14  # $14/sf average
    
    if elevation_feet <= 3:
        return base_elevation_cost * 0.9
    elif elevation_feet <= 6:
        return base_elevation_cost * 1.2
    elif elevation_feet <= 10:
        return base_elevation_cost * 1.5
    else:
        return base_elevation_cost * 2.0
```

## 4. Affordable Housing Density Assumptions

| Location Type | Units/Acre | Typical Configuration |
|--------------|------------|----------------------|
| **Urban** | 30 | 3-4 story buildings, structured parking |
| **Suburban** | 20 | 2-3 story buildings, surface parking |
| **Rural** | 15 | 1-2 story buildings, ample parking |

## 5. Integration with HUD AMI/Rent Data

### Data Linking Process

1. **County Matching**:
   ```python
   # Match FIPS codes from HUD data to construction cost zones
   # Texas FIPS codes start with '48'
   hud_data['construction_zone'] = map_county_to_zone(hud_data['fips'])
   ```

2. **Rent Extraction**:
   - Use 2BR 60% AMI rent as baseline
   - Calculate weighted average rent for mixed-income properties
   - Account for utility allowances (typically $75-150/month)

3. **Key Fields from HUD Data**:
   - `fips`: County identifier
   - `hud_area_name`: MSA or county name
   - `median2025`: 4-person household AMI
   - `2BR 50%`, `2BR 60%`, `2BR 80%`: Rent limits by AMI level

## 6. Comprehensive Scoring Metric

### Adjusted Rent/Acre Calculation

```python
def calculate_adjusted_rent_per_acre(county_data, flood_zone, elevation_req):
    """
    Calculate construction cost-adjusted rent per acre
    
    Args:
        county_data: Row from HUD rent data
        flood_zone: FEMA flood zone designation
        elevation_req: Required elevation in feet
    
    Returns:
        Dictionary with scoring metrics
    """
    # Get base parameters
    location_type = determine_location_type(county_data['fips'])
    density = DENSITY_MAP[location_type]
    monthly_rent = county_data['2BR 60%']
    
    # Calculate revenue
    annual_rent_per_unit = monthly_rent * 12
    gross_rent_per_acre = annual_rent_per_unit * density
    
    # Get cost modifiers
    location_mod = get_location_modifier(county_data['fips'])
    flood_mod = get_flood_modifier(flood_zone)
    
    # Calculate adjusted construction cost
    construction_cost_psf = calculate_adjusted_construction_cost(
        150, location_mod, flood_mod, elevation_req
    )
    
    # Calculate metric
    construction_factor = construction_cost_psf / 150  # Normalize to base
    adjusted_rent_per_acre = gross_rent_per_acre / construction_factor
    
    return {
        'county': county_data['County_Name'],
        'gross_rent_per_acre': gross_rent_per_acre,
        'construction_factor': construction_factor,
        'adjusted_rent_per_acre': adjusted_rent_per_acre,
        'flood_zone': flood_zone,
        'density': density
    }
```

## 7. Additional Cost Drivers

### Labor Cost Factors
- **Major Metros**: +15-20% due to competition for skilled trades
- **Border Counties**: -5-10% due to available workforce
- **Oil/Gas Counties**: +10-15% during boom cycles

### Material Transport Costs
- **<50 miles from distribution center**: No adjustment
- **50-100 miles**: +3% to materials cost
- **100-200 miles**: +5% to materials cost
- **>200 miles**: +8% to materials cost

### Regulatory Costs
- **Houston**: +5% for enhanced wind/flood requirements
- **Austin**: +3% for green building requirements
- **Rural**: -2% for simplified permitting

## 8. Implementation Steps for Claude Code

1. **Load Data Sources**:
   ```python
   # Load HUD rent data
   hud_data = pd.read_excel('HUD2025_AMI_Rent_Data_Static.xlsx')
   texas_data = hud_data[hud_data['fips'].str.startswith('48')]
   
   # Load your CoStar property data
   costar_data = load_costar_data()
   
   # Load FEMA flood maps (if available)
   flood_zones = load_flood_zone_data()
   ```

2. **Apply Modifiers**:
   ```python
   # For each property in CoStar data
   for idx, property in costar_data.iterrows():
       # Get county rent data
       county_rents = texas_data[texas_data['fips'] == property['fips']]
       
       # Determine flood zone (from address or parcel data)
       flood_zone = get_flood_zone(property['address'])
       
       # Calculate adjusted metrics
       metrics = calculate_adjusted_rent_per_acre(
           county_rents.iloc[0], 
           flood_zone,
           get_elevation_requirement(flood_zone)
       )
       
       # Add to scoring
       costar_data.loc[idx, 'adjusted_rent_per_acre'] = metrics['adjusted_rent_per_acre']
       costar_data.loc[idx, 'construction_factor'] = metrics['construction_factor']
   ```

3. **Scoring Integration**:
   ```python
   # Add to your existing LIHTC scoring system
   def calculate_lihtc_score(property_data):
       base_score = existing_scoring_function(property_data)
       
       # Add construction-adjusted rent score (0-20 points)
       if property_data['adjusted_rent_per_acre'] > 300000:
           rent_score = 20
       elif property_data['adjusted_rent_per_acre'] > 250000:
           rent_score = 15
       elif property_data['adjusted_rent_per_acre'] > 200000:
           rent_score = 10
       elif property_data['adjusted_rent_per_acre'] > 150000:
           rent_score = 5
       else:
           rent_score = 0
       
       # Penalty for high flood risk
       if property_data['flood_zone'] in ['VE', 'V']:
           flood_penalty = -10
       elif property_data['flood_zone'] in ['AE', 'A']:
           flood_penalty = -5
       else:
           flood_penalty = 0
       
       return base_score + rent_score + flood_penalty
   ```

## 9. Data Quality Checks

Implement these validations:

```python
def validate_calculations(results):
    # Check for reasonable construction costs
    assert 100 <= results['construction_cost_psf'] <= 300
    
    # Check density assumptions
    assert 10 <= results['density'] <= 35
    
    # Check rent reasonableness
    assert 500 <= results['monthly_rent'] <= 3000
    
    # Flag outliers for manual review
    if results['adjusted_rent_per_acre'] > 500000:
        flag_for_review("Unusually high adjusted rent")
    if results['construction_factor'] > 1.8:
        flag_for_review("Very high construction costs")
```

## 10. Example Output Format

```json
{
  "property_id": "CS123456",
  "address": "123 Main St, Austin, TX",
  "county": "Travis",
  "fips": "48453",
  "location_type": "major_metro",
  "base_construction_psf": 150,
  "location_modifier": 1.20,
  "flood_zone": "X",
  "flood_modifier": 0.00,
  "elevation_required": 0,
  "total_construction_psf": 180,
  "density_units_acre": 30,
  "ami_2025": 133800,
  "rent_2br_60pct": 1807,
  "annual_rent_per_unit": 21684,
  "gross_rent_per_acre": 650520,
  "construction_factor": 1.20,
  "adjusted_rent_per_acre": 542100,
  "lihtc_score_components": {
    "base_score": 75,
    "rent_adjustment_score": 20,
    "flood_penalty": 0,
    "total_score": 95
  }
}
```

This comprehensive guide provides all the components needed to integrate construction cost variations and flood risk into your LIHTC scoring system while maintaining direct ties to the HUD AMI/Rent data.
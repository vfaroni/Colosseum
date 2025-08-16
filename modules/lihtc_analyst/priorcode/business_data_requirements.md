# Business-Focused Data Requirements for Deal Sourcing Dashboard

## Core Required Fields (Already Present)
✅ **Location Data**
- Address, City, County, State
- Latitude, Longitude

✅ **Analysis Results**
- eligibility, one_mile_competing_count
- Distance fields (*_distance_miles)
- city_population

## ✅ HUD AMI Rent Data Integration - IMPLEMENTED

**Source: HUD2025_AMI_Rent_Data_Static.xlsx**
```
Studio_50AMI_rent      # Studio apartment rent at 50% AMI
BR1_50AMI_rent         # 1BR apartment rent at 50% AMI  
BR2_50AMI_rent         # 2BR apartment rent at 50% AMI
BR3_50AMI_rent         # 3BR apartment rent at 50% AMI
BR4_50AMI_rent         # 4BR apartment rent at 50% AMI
Studio_60AMI_rent      # Studio apartment rent at 60% AMI
BR1_60AMI_rent         # 1BR apartment rent at 60% AMI
BR2_60AMI_rent         # 2BR apartment rent at 60% AMI
BR3_60AMI_rent         # 3BR apartment rent at 60% AMI
BR4_60AMI_rent         # 4BR apartment rent at 60% AMI

# Calculated fields:
weighted_avg_rent_50AMI      # Weighted average rent 50% AMI
weighted_avg_rent_60AMI      # Weighted average rent 60% AMI
annual_income_per_unit_50AMI # Annual income per unit 50% AMI
annual_income_per_unit_60AMI # Annual income per unit 60% AMI
```

**Features Available:**
- ✅ County-based rent lookup from HUD data
- ✅ Revenue projection calculator
- ✅ Rent comparison charts
- ✅ Top revenue opportunity identification
- ✅ Unit mix scenarios (Studio/1BR/2BR/3BR/4BR)

## Additional Business Fields to Add

### 📞 Contact Information
**Source: CoStar broker/listing data**
```
broker_name          # Primary contact name
broker_phone         # Phone number for outreach
broker_email         # Email for initial contact
listing_agent        # Secondary contact if different
brokerage_company    # Company name
```

### 💰 Financial Data
**Source: CoStar property listings**
```
asking_price         # Listed sale price
price_per_acre       # Price per acre calculation
total_acres          # Parcel size
property_tax_annual  # Annual property taxes
assessed_value       # County assessed value
days_on_market       # How long listed
```

### 📊 Development Metrics
**Source: Various sources**
```
zoning_current       # Current zoning designation
zoning_proposed      # Planned zoning if different
max_density_units    # Maximum units allowed
parking_required     # Parking spaces per unit required
height_restriction   # Maximum building height
setback_requirements # Building setback requirements
```

### 🏘️ Market Data
**Source: Census/HUD data**
```
poverty_rate         # Area poverty percentage
median_income_ami    # Area Median Income
unemployment_rate    # Local unemployment rate
population_growth    # Recent population growth %
school_district      # School district name
school_rating        # District rating/ranking
```

### 🏗️ Site Conditions
**Source: Environmental/engineering**
```
environmental_clear  # Environmental clearance status
flood_zone          # FEMA flood zone designation
soil_conditions     # Basic soil assessment
utilities_available # What utilities are on-site
road_access         # Road access quality
topography         # Flat, sloped, etc.
```

## Enhanced Scoring Calculations

### 4% Credit Scoring (60 points max)
```python
# Proximity Scoring (40 points)
grocery_score = 10 if distance <= 1 else 7 if distance <= 2 else 3 if distance <= 5 else 0
school_score = 10 if distance <= 0.5 else 7 if distance <= 1 else 3 if distance <= 2 else 0
transit_score = 10 if distance <= 0.25 else 7 if distance <= 0.5 else 3 if distance <= 1 else 0
hospital_score = 10 if distance <= 2 else 5 if distance <= 5 else 0

# Market Factors (20 points)
population_score = 20 if pop >= 100k else 15 if pop >= 50k else 10 if pop >= 25k else 5
```

### 9% Credit Scoring (Additional tie-breaker points)
```python
# Same Census Tract (0-5 points)
tract_score = 5 if no_recent_projects else years_based_score

# Competition Penalty
competition_penalty = competing_projects * -5

# Large County Bonus
large_county_bonus = 10 if county in ['Harris', 'Dallas', 'Tarrant', 'Bexar', 'Travis'] else 0
```

## Data Integration Sources

### 1. CoStar Enhancement
**Add these fields to your CoStar export:**
- Broker contact information
- Financial details (price, size, taxes)
- Days on market
- Zoning information

### 2. Census API Integration
**Already implemented for:**
- City population ✅
**Can add:**
- Poverty rates
- Median income
- Demographics

### 3. School District API
**Texas Education Agency data:**
- District ratings
- School performance
- Enrollment data

### 4. HUD AMI Data
**Area Median Income by county:**
- 30%, 50%, 80% AMI thresholds
- Income limits by household size

## Sample Enhanced Excel Structure

```
Core Columns (Existing):
- Address, City, County, Latitude, Longitude
- eligibility, *_distance_miles, city_population

Business Columns (Add):
- broker_name, broker_phone, broker_email
- asking_price, price_per_acre, total_acres
- poverty_rate, median_income_ami
- zoning_current, max_density_units
- days_on_market, environmental_clear

Calculated Columns (Dashboard creates):
- 4pct_score, 9pct_score
- 4pct_category, 9pct_category  
- deal_quality, contact_priority
```

## Implementation Steps

### Phase 1: Contact Enhancement
1. Export additional CoStar fields for broker contacts
2. Add columns to your merged Excel file
3. Re-run dashboard with contact features

### Phase 2: Financial Integration
1. Add pricing and size data from CoStar
2. Calculate price per acre metrics
3. Add financial filters to dashboard

### Phase 3: Market Data Integration
1. Integrate Census poverty rate API
2. Add HUD AMI data lookup
3. Create market attractiveness scoring

### Phase 4: Development Metrics
1. Add zoning and density data
2. Create development feasibility scoring
3. Add site condition assessments

## Quick Start: Contact Information

To immediately improve the dashboard, add these columns to your Excel file:

```python
# Minimum viable contact enhancement
required_columns = [
    'broker_name',       # From CoStar listing agent
    'broker_phone',      # From CoStar contact info  
    'broker_email',      # From CoStar contact info
    'asking_price',      # From CoStar price field
    'total_acres'        # From CoStar size field
]
```

This will enable the contact management and outreach features in the enhanced dashboard.